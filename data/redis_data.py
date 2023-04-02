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
from peewee import fn, IntegrityError
CLIENT_ID_ALPHABET = "1234567890abcdefghjkmnpqrstuvwxyz"

EXP_7DAYS = 7*24*60*60

from .data_models import mysql_db, User,Image,Likes,Histories



class RClient:

    def __init__(self) -> None:
        self.r = redis.Redis("localhost", 6379, decode_responses=True)
        self.mysql_db = mysql_db 
        self.mysql_db.connect()

    # 整体统计
    def get_server_status(self):
        # 排队任务数
        queue_size = self.get_queue_size()
        # 已生成图像数
        generated_num = self.get_generated_number()
        # 高清图生成数量
        upscale_num = self.get_upscale_number()
        # 画廊图像数
        gallery_num = self.get_gallery_number()
        return queue_size, generated_num, upscale_num, gallery_num

    def add_generated_number(self):
        self.r.incr("status_generated_num")
    
    def get_generated_number(self):
        try:
            return int(self.r.get("status_generated_num"))
        except:
            return 0 

    def add_upscale_number(self):
        self.r.incr("status_upscale_num")

    def get_upscale_number(self):
        try:
            return int(self.r.get("status_upscale_num"))
        except:
            return 0

    def record_upscale_task(self):
        self.add_upscale_number()

    def add_gallery_number(self):
        self.r.incr("status_gallery_num")
    
    def get_gallery_number(self):
        try:
            return Image.select().where(Image.published==True).count()
            
        except:
            return 0

    # mosec服务器队列情况

    def get_queue_size(self):
        try:
            metrics = httpx.get(MODEL_URL.replace("inference","metrics")).content.decode()
            remain = re.findall(r"mosec_service_remaining_task \d+", metrics)[0]
            return int(remain.split(" ")[-1])
        except:
            return 0 

    # 用户历史记录相关
    def get_new_client_id(self):
        new_client_id = "@"+nanoid.generate(CLIENT_ID_ALPHABET, size=10)
        return new_client_id

    def get_user_config(self,userid):
        try:
            return json.loads(User.get_by_id(userid).config)
        except:
            return {
                "autopub":False,
                "colnum":6,
                "hisnum": 200
            }

    def update_user_config(self,userid,config):
        try:
            user = User.get_by_id(userid)
            user.config = json.dumps(config)
            user.save()
            return True
        except:
            return False 


    def get_user_level(self,userid):
        try:
            return User.get_by_id(userid).level
        except:
            return 0

    def get_lastgentime(self,userid):
        try:
            return int(self.r.get(f"gentime:{userid}"))
        except:
            return -1

    def set_lastgentime(self,userid):
        self.r.set(f"gentime:{userid}",int(time.time()))

    def get_sharerate(self, userid):
        '''
        return rate, num gen, num share
        '''
        num_generated = Image.select().where(Image.userid==userid).count()
        num_published = Image.select().where((Image.published==1) & (Image.userid==userid)).count()
        if num_generated <= 100:
            return 100,num_generated,num_published
        return 100*num_published/(num_generated-100),num_generated,num_published

    def record_new_but_history_only(self, client_id, img_url, gen_id,nsfw):
        try:
            with self.mysql_db.atomic():
                if not nsfw:
                    Histories.create(
                        userid=client_id,
                        imgurl=img_url,
                        genid=gen_id
                    )
        except:
            pass 

    def record_new_generated_image(self, client_id, img_url,gen_id,text2image_data,nsfw,score,face): 
        # client id 也有可能是一个userid，如果已经登陆，session的client id使用username
        self.add_generated_number()
        try:
            with self.mysql_db.atomic():
                if not nsfw:
                    Histories.create(
                        userid=client_id,
                        imgurl=img_url,
                        genid=gen_id
                    )
                Image.create(
                    genid=gen_id,
                    imgurl=img_url,
                    height=text2image_data['height'],
                    width=text2image_data['width'],
                    params=json.dumps(text2image_data),
                    modelname=text2image_data['model_name'],
                    prompt=text2image_data['prompt'],
                    published=False,
                    userid=client_id,
                    nsfw=nsfw,
                    score=score,
                    face=face
                )
        except IntegrityError:
            pass
        
    def mark_as_nsfw(self,genid):
        Histories.delete().where(Histories.genid==genid).execute()
        img = Image.get_by_id(genid)
        img.nsfw=True
        img.published=False
        img.save()

    def del_history(self,userid,genid):
        Histories.delete().where((Histories.userid==userid)&(Histories.genid==genid)).execute()

    def get_history(self, client_id, limit=200):
        if client_id.startswith("@"): return []
        images = Histories.select().where(Histories.userid==client_id).order_by(Histories.gentime.desc()).limit(limit)
        img_url_and_genid = [(image.imgurl,image.genid) for image in images]
        return img_url_and_genid[::-1]

    def check_genid_in_imagetable(self,genid):
        try:
            return Image.get_by_id(genid).imgurl
        except:
            return None


    def get_image_information(self, generation_id=None):
        try:
            image_record = Image.get_by_id(generation_id)
            ret = json.loads(image_record.params)
            ret["gentime"] = str(image_record.gentime)
            ret["user"] = User.get_by_id(image_record.userid).username
            return ret 
        except:
            traceback.print_exc()
            return None

    def record_publish(self,genid):
        try:
            self.store_gallery_image_information(genid)
            self.add_gallery_number()
            return True
        except Exception as _:
            traceback.print_exc()
            return False

    def update_lifecycle(self,img_url):
        pass 

    def store_gallery_image_information(self, genid):
        generation_id = genid
        image = Image.get_by_id(generation_id)
        image.published = True
        image.save()

    def get_random_samples_from_gallery(self, num):
        images = Image.select().where(Image.published==True).order_by(fn.Rand()).limit(num)
        ret = []
        for img in images:
            ret.append(img.imgurl)
        return ret 

    def add_check_image(self, genid):
        self.r.rpush("Check",genid)
        return True 
    def get_check_image(self):
        if self.r.llen("Check")>0:
            img = self.r.lpop("Check")
            return img 
        else:
            return None

    def reset_pass_and_email(self,username,password,email):
        try:
            user = User.get(User.username==username)
            user.password = hashlib.sha1((username+password).encode("utf-8")).hexdigest()
            user.email = email 
            user.save()
            return True
        except:
            return False

    def register_user(self,username,password,email):
        try:
            pw_hash = hashlib.sha1((username+password).encode("utf-8")).hexdigest()
            with self.mysql_db.atomic():
                User.create(
                    username=username,
                    password=pw_hash,
                    email=email,
                    level=1
                )
            return True
        except:
            return False

    def check_user_email(self,username,email):
        try:
            user=User.get(User.username==username)
            print(username,email,user.email)
            if user.email==email:
                return True
            else:
                return False 
        except:
            return False

    def verif_user(self,username,password):
        try:
            pw_hash = hashlib.sha1((username+password).encode("utf-8")).hexdigest()
            user = User.get((User.username==username) & (User.password==pw_hash))
            return user is not None
        except:
            return False

    def get_userid(self, username):
        try:
            return str(User.get(User.username==username).userid)
        except:
            return None

    def check_likes(self,userid,genid):
        if Likes.select().where((Likes.userid==userid) & (Likes.genid==genid)).count()>0:
            return True 
        else:
            return False

    def set_likes(self,userid,genid):
        with self.mysql_db.atomic():
            if not self.check_likes(userid,genid):
                Likes.create(
                    userid=userid,
                    genid=genid
                )

    def get_likenum(self,genid):
        return Likes.select().where(Likes.genid==genid).count()
        
    def cancel_likes(self,userid,genid):
        Likes.delete().where((Likes.userid==userid) & (Likes.genid==genid)).execute()

    def check_email_exists(self,email):
        if User.select().where(User.email==email).count()>0:
            return True
        else:
            return False

    def get_imgurl_by_id(self,genid):
        try:
            return Image.get_by_id(genid).imgurl
        except:
            return ""

    def check_published(self,genid):
        try:
            if Image.get_by_id(genid).published==True:
                return True 
            else:
                return False
        except:
            return False 

    def record_chatgpt(self,input,output):
        self.r.rpush("chatgptrecord",input+"|"+output)

    # 点赞相关的功能
    

if __name__=="__main__":
    r=RClient()
    r.move_redis_gallery_to_mysql()
