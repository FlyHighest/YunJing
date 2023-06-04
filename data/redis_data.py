import sys
sys.path.append(".")
sys.path.append("..")
import random ,hashlib
import nanoid, traceback
import redis
import httpx,re,json
from secret import *
import os 
import time
CLIENT_ID_ALPHABET = "1234567890abcdefghjkmnpqrstuvwxyz"


# from .data_models import mysql_db, User,Image,Likes,Histories



class RClient:

    def __init__(self) -> None:
        self.r = redis.Redis("localhost", 6379, decode_responses=True)

        if not self.r.exists("max_userid"):
            self.r.set("max_userid",10000)

    # 画廊query相关 
    def query_best_images(self):
        genids = self.r.zrange("gallery",-200,-1)
        random.shuffle(genids)
        results = []
        for genid in genids:
            image_url,height,width,username=self.r.hmget(f"image:{genid}",["imgurl","height","width","username"])
            results.append({
                "image_url": image_url,
                "height": int(height),
                "width": int(width),
                "username": username,
                "genid": genid
            })
        return results

    def query_user_images(self,username):
        userid = self.r.get(f"userid:{username}")
        genids = self.r.zrange(f"gallery:userid:{userid}",-1000,1000)
        results = []
        for genid in genids:
            image_url,height,width,username=self.r.hmget(f"image:{genid}",["imgurl","height","width","username"])
            results.append({
                "image_url": image_url,
                "height": int(height),
                "width": int(width),
                "username": username,
                "genid": genid
            })
        return results

    # cd 功能相关
    def set_generation_lock(self,userid, cd=10):
        self.r.set(f"lock:gen:{userid}",1,ex=cd)
    
    def exists_generation_lock(self,userid):
        return self.r.get(f"lock:gen:{userid}") is not None

    def unset_generation_lock(self,userid):
        self.r.delete(f"lock:gen:{userid}")


    # status 相关
    def status_get_all(self):
        # 排队任务数
        # queue_size = self.get_queue_size()
        # 已生成图像数
        generated_num = self.status_get_generated_num()
        # 高清图生成数量
        upscale_num = self.status_get_upscale_num()
        # 画廊图像数
        gallery_num = self.status_get_gallery_num()
        return  generated_num, upscale_num, gallery_num

    def status_add_generated_num(self):
        self.r.incr("status_generated_num")
    
    def status_get_generated_num(self):
        try:
            return int(self.r.get("status_generated_num"))
        except:
            return 0 

    def status_add_upscale_num(self):
        self.r.incr("status_upscale_num")

    def status_get_upscale_num(self):
        try:
            return int(self.r.get("status_upscale_num"))
        except:
            self.r.set("status_upscale_num",0)
            return 0

    def status_add_gallery_num(self):
        self.r.incr("status_gallery_num")
    
    def status_get_gallery_num(self):
        try:
            return int(self.r.get("status_gallery_num"))
        except:
            self.r.set("status_gallery_num",0)
            return 0

    def record_history(self, userid, img_url,genid):
        try:
            self.r.rpush(f"history:{userid}",json.dumps((img_url,genid)))
            current_length = self.r.llen(f"history:{userid}")
            if current_length >510:
                self.r.lpop(f"history:{userid}",current_length-510)
        except:
            traceback.print_exc() 

    def del_history(self,userid,genid):
        # Histories.delete().where((Histories.userid==userid)&(Histories.genid==genid)).execute()
        url = self.r.hget(f"image:{genid}","imgurl")
        ret =self.r.lrem(f"history:{userid}",0,json.dumps((url,genid)))
        assert ret==1

    def get_history(self, userid, limit=200):
        if userid.startswith("@"): return []
        length = self.r.llen(f"history:{userid}")

        img_url_and_genid = [json.loads(i) for i in self.r.lrange(f"history:{userid}",length-limit,length-1)]
        return img_url_and_genid


    def record_upscale_task(self,genid,img_url,factor):
        self.status_add_upscale_num()
        if factor==2:
            self.r.hset(f"image:{genid}","upx2",img_url)
        elif factor==4:
            self.r.hset(f"image:{genid}","upx4",img_url)
        
    def get_upscale_url(self,genid,factor=2):
        if factor==2:
            return self.r.hget(f"image:{genid}","upx2")
        elif factor==4:
            return self.r.hget(f"image:{genid}","upx4")


    # mosec服务器队列情况
    def get_queue_size(self):
        try:
            metrics = httpx.get(MODEL_URL.replace("inference","metrics")).content.decode()
            remain = re.findall(r"mosec_service_remaining_task \d+", metrics)[0]
            return int(remain.split(" ")[-1])
        except:
            return 0 


    def get_new_client_id(self):
        # 仍在使用的函数
        new_client_id = "@"+nanoid.generate(CLIENT_ID_ALPHABET, size=10)
        return new_client_id

    def get_user_config(self,userid):
        try:
            return json.loads(self.r.hget(f"user:{userid}","config"))
        except:
            return {
                "colnum":6,
                "hisnum": 200
            }

    def update_user_config(self,userid,config):
        try:
            
            config = json.dumps(config)
            self.r.hset(f"user:{userid}","config",config)
            return True
        except:
            return False 


    def get_user_level(self,userid):
        try:
            return int(self.r.hget(f"user:{userid}","level"))
        except:
            return 0

    def get_sharerate(self, userid):
        '''
        return rate, num gen, num share
        '''
        num_generated = int(self.r.hget(f"user:{userid}","num_generated") or 0)
        num_published = int(self.r.hget(f"user:{userid}","num_published") or 0)
        if num_generated <= 100:
            return 100,num_generated,num_published
        return 100*num_published/(num_generated-100),num_generated,num_published



    def record_new_generated_image(self, userid, img_url,gen_id,text2image_data,nsfw,score,face): 
        # client id 也有可能是一个userid，如果已经登陆，session的client id使用username
        self.status_add_gallery_num()
        try:
            data_mapping = dict(
                    genid=gen_id,
                    imgurl=img_url,
                    height=text2image_data['height'],
                    width=text2image_data['width'],
                    params=json.dumps(text2image_data),
                    modelname=text2image_data['model_name'],
                    prompt=text2image_data['prompt'],
                    published=int(False),
                    userid=userid,
                    nsfw=int(nsfw),
                    score=float(score),
                    face=int(face),
                    gentime=time.strftime("%Y-%m-%d %H:%M:%S")
                )
            self.r.hset(f"image:{gen_id}",mapping=data_mapping)
            num_generated = int(self.r.hget(f"user:{userid}","num_generated"))  
            self.r.hset(f"user:{userid}","num_generated",num_generated+1)
        except:
            pass
        
    def mark_as_nsfw(self,genid):
        # Histories.delete().where(Histories.genid==genid).execute()
        # img = Image.get_by_id(genid)
        # img.nsfw=True
        # img.published=False
        # img.save()
        pass 


    def check_genid_in_imagetable(self,genid):
        try:
            if self.r.exists(f"image:{genid}"):
                imgurl,nsfw= self.r.hmget(f"image:{genid}",["imgurl","nsfw"])
                nsfw = True if nsfw=="1" else False 
                return imgurl, nsfw
            else:
                return None, None
        except:
            return None, None


    def get_image_information(self, generation_id=None):
        try:
            image_record = self.r.hgetall(f"image:{generation_id}")
            ret = json.loads(image_record["params"])
            ret["gentime"] = str(image_record["gentime"])
            userid = image_record["userid"]
            ret["user"] = self.r.hget(f"user:{userid}","username")
            ret["userid"] = userid 
            ret['published'] = image_record["published"] # TODO: possibly unused
            return ret 
        except:
            traceback.print_exc()
            return None

    def record_publish(self,genid):
        try:
            self.r.hset(f"image:{genid}","published",1)
            self.status_add_gallery_num()
            userid = self.r.hget(f"image:{genid}","userid")
            num_published = int(self.r.hget(f"user:{userid}","num_published"))  
            self.r.hset(f"user:{userid}","num_published",num_published+1)

            score = float(self.r.hget(f"image:{genid}","score"))
            model_name = self.r.hget(f"image:{genid}","modelname")
            self.r.zadd("gallery",{genid:score})
            self.r.zadd(f"gallery:userid:{userid}",{genid:score})
            self.r.zadd(f"gallery:model:{model_name}",{genid:score})
            
            return True
        except Exception as _:
            traceback.print_exc()
            return False
        

    def cancel_publish(self,genid):
        self.r.hset(f"image:{genid}","published",0)
        self.r.zrem("gallery",genid)
        userid = self.r.hget(f"image:{genid}","userid")
        model_name = self.r.hget(f"image:{genid}","modelname")
        self.r.zrem(f"gallery:userid:{userid}",genid)
        self.r.zrem(f"gallery:model:{model_name}",genid)


    def reset_pass_and_email(self,username,password,email):
        try:

            userid = self.r.get(f"userid:{username}")
            password = hashlib.sha1((username+password).encode("utf-8")).hexdigest()
            email = email 
            self.r.hset(f"user:{userid}","password",password)
            self.r.hset(f"user:{userid}","email",email)
            return True
        except:
            return False

    def register_user(self,username,password,email):
        try:
            pw_hash = hashlib.sha1((username+password).encode("utf-8")).hexdigest()
            mapping = \
                dict(
                    username=username,
                    password=pw_hash,
                    email=email,
                    level=1,
                    jointime=time.strftime("%Y-%m-%d %H:%M:%S"),
                    num_generated=0,
                    num_published=0
                )
            userid = int(self.r.get("max_userid")) + 1
            self.r.set("max_userid",userid)
            self.r.hset(f"user:{userid}",mapping=mapping)
            self.r.set(f"userid:{username}",userid)
            self.r.sadd("user-emails",email)
            return True
        except:
            return False

    def check_user_email(self,username,email):
        try:
            userid = self.r.get(f"userid:{username}")
            user_email = self.r.hget(f"user:{userid}","email")
            if user_email==email:
                return True
            else:
                return False 
        except:
            return False

    def verif_user(self,username,password):
        try:
            pw_hash = hashlib.sha1((username+password).encode("utf-8")).hexdigest()
           
            userid = self.r.get(f"userid:{username}")
            user_password = self.r.hget(f"user:{userid}","password")
            return pw_hash == user_password
        except:
            return False

    def get_userid(self, username):
        try:
            return self.r.get(f"userid:{username}")
        except:
            return None

    def check_likes(self,userid,genid):
        return False

    def set_likes(self,userid,genid):
        pass 
        # with self.mysql_db.atomic():
        #     if not self.check_likes(userid,genid):
        #         Likes.create(
        #             userid=userid,
        #             genid=genid
        #         )

    def get_likenum(self,genid):
        return 0
        # return Likes.select().where(Likes.genid==genid).count()
        
    def cancel_likes(self,userid,genid):
        pass 
        #Likes.delete().where((Likes.userid==userid) & (Likes.genid==genid)).execute()

    def check_email_exists(self,email):
        if self.r.sismember("user-emails",email):
            return True
        else:
            return False

    def get_imgurl_by_id(self,genid):
        try:
            return self.r.hget(f"image:{genid}","imgurl")
        except:
            return ""

    def check_published(self,genid):
        try:
            if self.r.zrank("gallery",genid) is not None:
                return True 
            else:
                return False
        except:
            return False 

    def record_chatgpt(self,input,output):
        self.r.rpush("chatgptrecord",input+"|"+output)

    

if __name__=="__main__":
    r=RClient()
    r.move_redis_gallery_to_mysql()
