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
from datetime import datetime
from .gallery_data import GalleryDataManager
from collections import deque , defaultdict
CLIENT_ID_ALPHABET = "1234567890abcdefghjkmnpqrstuvwxyz"

# a custom deque class. When append elements, check the left element within time range 10 minitues
class CustomDeque:
    def __init__(self, expire_time_seconds=3600) -> None:
        self.expire_time_seconds = expire_time_seconds
        self.queue = deque()
        self.unique_set = defaultdict(int)
    
    def append(self,element):
        self.queue.append((time.time(),element))
        self.unique_set[element] += 1 

    
    def remove_expired_element(self):
        while len(self.queue)>0 and self.queue[0][0] < time.time()-self.expire_time_seconds:
            poped_element = self.queue.popleft()[1]
            self.unique_set[poped_element] -= 1 
            if self.unique_set[poped_element]<=0:
                del self.unique_set[poped_element]

    def get_unique_element_count(self):
        self.remove_expired_element()
        return len(self.unique_set)
    
    def get_queue_length(self):
        self.remove_expired_element()
        return len(self.queue)

        


class RClient:

    def __init__(self) -> None:
        self.r = redis.Redis("localhost", 6379, decode_responses=True)

        if not self.r.exists("max_userid"):
            self.r.set("max_userid",10000)
        
        self.generation_task_queue = CustomDeque()
        self.gallery_data_manager =  GalleryDataManager()
    
    def genid_to_gallery_return_list(self,genids):
        results = []
        for genid in genids:
            image_url,height,width,username=self.r.hmget(f"image:{genid}",["imgurl","height","width","userid"])
            if "storage.yunjing.gallery" in image_url:
                
                continue 
            results.append({
                "image_url": image_url,
                "height": int(height),
                "width": int(width),
                "username": username,
                "genid": genid
            })
        return results  
               
    # 画廊query相关 
    def query_best_images(self):
        genids = list(self.r.smembers("gallery-hq"))
        random.shuffle(genids)
        genids = genids[:400]
        return self.genid_to_gallery_return_list(genids)

    def query_all_images(self,date_str):
        genids = list(self.r.smembers("gallery-all"))
        random.shuffle(genids)

        
        if isinstance(date_str,str):
            genids = [g for g in genids
                       if g.startswith(date_str) and self.r.sismember("gallery-hq",g)==False
                         ]
        else:
            genids = genids[:400]
            genids = [g for g in genids if self.r.sismember("gallery-hq",g)==False]
        return self.genid_to_gallery_return_list(genids)

    def query_personal_history(self,userid):
        img_url_and_genid = [json.loads(i) for i in self.r.lrange(f"history:{userid}",0,-1)]
        genids = []
        for url,genid in img_url_and_genid:
            genids.append(genid)
        return self.genid_to_gallery_return_list(genids)   

    def query_by_input(self,author,modelname,text):
        genids = self.gallery_data_manager.search(author,modelname,text)
        random.shuffle(genids)
        genids = genids[:400]
        return self.genid_to_gallery_return_list(genids)


    # cd 功能相关
    def set_generation_lock(self,userid, cd=10):
        self.r.set(f"lock:gen:{userid}",1,ex=cd)
    
    def exists_generation_lock(self,userid):
        return self.r.get(f"lock:gen:{userid}") is not None

    def unset_generation_lock(self,userid):
        self.r.delete(f"lock:gen:{userid}")


    def get_generation_server_status(self):
        unique_user_count = self.generation_task_queue.get_unique_element_count()
        task_count = self.generation_task_queue.get_queue_length()
        if unique_user_count <= 1:
            return "🟢空闲",0
        elif unique_user_count <= 3:
            return "🟡繁忙",1
        elif unique_user_count <= 5:
            return "🟠拥挤",2
        else:
            return "🔴爆满",3

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


    def status_get_gallery_num(self):
        try:
            return int(self.r.scard("gallery-all"))
        except:
            
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
        if  ret!=1:
            print("del histroy error",userid,genid)
            img_url_and_genid = [json.loads(i) for i in self.r.lrange(f"history:{userid}",0,-1)]
            genids = []
            for url,genid_ in img_url_and_genid:
                if genid_==genid:
                    ret = self.r.lrem(f"history:{userid}",0,json.dumps((url,genid)))
                    if ret==1:
                        print("del history ok")
                        break

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
            ret = json.loads(self.r.hget(f"user:{userid}","config"))
            if "annotation" not in ret:
                ret["annotation"] = False
            return ret
        except:
            return {
                "colnum":6,
                "hisnum": 200,
                "annotation": False
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
        self.status_add_generated_num()
        self.generation_task_queue.append(userid)
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
        self.cancel_publish(genid)


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
            
            userid = self.r.hget(f"image:{genid}","userid")
            num_published = int(self.r.hget(f"user:{userid}","num_published"))  
            self.r.hset(f"user:{userid}","num_published",num_published+1)

            model_name = self.r.hget(f"image:{genid}","modelname")
            prompt = self.r.hget(f"image:{genid}","prompt")

            username = self.r.hget(f"user:{userid}","username")
            self.r.sadd("gallery-all",genid)

            self.gallery_data_manager.add_item(username,prompt,model_name,genid)
           
            return True
        except Exception as _:
            traceback.print_exc()
            return False

    def is_in_gallery_hq(self,genid):
        return self.r.sismember("gallery-hq",genid)

    def record_highquality_gallery(self,genid):
        try:
            self.r.sadd("gallery-hq",genid)
            return True
        except Exception as _:
            traceback.print_exc()
            return False

    def cancel_publish(self,genid):
        self.gallery_data_manager.del_item(genid)
        self.r.hset(f"image:{genid}","published",0)
        self.r.srem("gallery-all",genid)
        self.r.srem("gallery-hq",genid) 
        
  


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
            self.add_pro_time(userid,86400)
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
            if self.r.sismember("gallery-all",genid):
                return True 
            else:
                return False
        except:
            return False 

    def record_chatgpt(self,input,output):
        # self.r.rpush("chatgptrecord",input+"|"+output)
        pass

    def record_anno_nsfw(self,genid,anno,userid):
        self.r.set(f"anno_nsfw:{genid}:{userid}",anno)
    
    def record_anno_score(self,genid,anno,userid):
        self.r.set(f"anno_score:{genid}:{userid}",anno)

    def is_user_pro(self,userid):
        protime = self.r.get(f"protime:{userid}") or 0
        protime= int(protime)
        if protime > time.time():
            return True 
        else:
            return False 
    
    def check_pro_key(self,key):
        if self.r.get("prokey:"+key) == "0" :
            self.r.set("prokey:"+key,"1")
            return True 
        else:
            return False 

    def get_bonus_pro_time(self,userid):
        # hour
        b_time = self.r.get(f"bonusprotime:{userid}") or 0 
        return float(b_time)
    
    def set_bonus_pro_time(self,userid,b_time):
        self.r.set(f"bonusprotime:{userid}",b_time)

    def add_bonus_pro_time(self,userid,b_time):
        current_b_time = self.get_bonus_pro_time(userid)
        self.set_bonus_pro_time(userid,float(b_time)+float(current_b_time))

    def add_pro_time(self, userid, timevalue=2678400):
        current = self.r.get(f"protime:{userid}")
        if current is None:
            protime =  time.time()
        else:
            protime = max(int(current), time.time())

        protime= int(protime)
        endtime = int( protime + timevalue )
        self.r.set(f"protime:{userid}",str(endtime))

    def get_pro_time_show(self,userid):
        time_str= self.r.get(f"protime:{userid}") 
        if time_str is None:
            showtime = "（未激活专业版功能）"
        else:
            dt_object = datetime.fromtimestamp(int(time_str))
            showtime = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        return showtime 
    


if __name__=="__main__":
    r=RClient()
    r.move_redis_gallery_to_mysql()
