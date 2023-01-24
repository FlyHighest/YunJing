import sys
sys.path.append(".")
sys.path.append("..")
import random ,hashlib
import nanoid, traceback
import redis
import httpx,re,json
from utils import get_generation_id
from secret import *
from qiniu import Auth as QiniuAuth
from qiniu import BucketManager as QiniuBucketManager
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

    def record_new_generated_image(self, client_id, img_url, text2image_data): 
        # client id 也有可能是一个userid，如果已经登陆，session的client id使用username
        self.add_generated_number()
        gen_id = get_generation_id(img_url)
        try:
            if client_id.startswith("@"):
                self.r.rpush("His:"+client_id, img_url)
                self.r.expire("His:"+client_id, EXP_7DAYS)
                text2image_data["img_url"] = img_url
                
                with self.mysql_db.atomic():
                    Image.create(
                        genid=gen_id,
                        imgurl=img_url,
                        params=json.dumps(text2image_data),
                        modelname=text2image_data['model_name'],
                        prompt=text2image_data['prompt'],
                        published=False,
                        userid=1 # 匿名用户
                    )
            else:
                
                with self.mysql_db.atomic():
                    Histories.create(
                        userid=client_id,
                        imgurl=img_url
                    )
                    Image.create(
                        genid=gen_id,
                        imgurl=img_url,
                        params=json.dumps(text2image_data),
                        modelname=text2image_data['model_name'],
                        prompt=text2image_data['prompt'],
                        published=False,
                        userid=client_id
                    )
        except IntegrityError:
            pass


    def get_history(self, client_id):
        if client_id.startswith("@"):
            return self.r.lrange("His:"+client_id, 0, -1)
        else:
            images = Histories.select().where(Histories.userid==client_id).order_by(Histories.gentime.desc).limit(100)
            img_urls = [image.imgurl for image in images]
            return img_urls

    def check_genid_in_imagetable(self,genid):
        try:
            return Image.get_by_id(genid).imgurl
        except:
            return None

    def get_image_information_old(self, img_url=None, generation_id=None):
        generation_id = generation_id or get_generation_id(img_url)
        keys=[
            "type",
            "img_url",
            "model_name",
            "scheduler_name",
            "prompt",
            "negative_prompt",
            "height",
            "width",
            "num_inference_steps",
            "guidance_scale",
            "seed"]
        if self.r.exists("InfoHis:"+generation_id)>0:
            text2image_data_values = self.r.hmget("InfoHis:"+generation_id, keys)
        else:
            text2image_data_values = self.r.hmget("InfoGal:"+generation_id, keys)
        text2image_data = {k:v for k,v in zip(keys,text2image_data_values)}
        text2image_data["user"]="匿名用户"
        text2image_data["gentime"] ="2023-01-24 00:00:00"
        if text2image_data['type'] is not None:
            return text2image_data
        else :
            return None 

    def get_image_information(self, img_url=None, generation_id=None):
        generation_id = generation_id or get_generation_id(img_url)
        try:
            image_record = Image.get_by_id(generation_id)
            ret = json.loads(image_record.params)
            ret["gentime"] = str(image_record.gentime)
            ret["user"] = User.get_by_id(image_record.userid).username
            return ret 
        except:
            traceback.print_exc()
            return self.get_image_information_old(img_url,generation_id) 

    def record_publish(self,img_url):
        try:
            self.update_lifecycle(img_url)
            self.store_gallery_image_information(img_url)
            self.add_gallery_number()
            return True
        except Exception as _:
            traceback.print_exc()
            return False

    def update_lifecycle(self,img_url):
        #初始化Auth状态
        q = QiniuAuth(qiniu_access_key_id, qiniu_access_key_secret)
        #初始化BucketManager
        bucket = QiniuBucketManager(q)
        #你要测试的空间， 并且这个key在你空间中存在
        bucket_name = 'imagedraw'
        # img_url example: http://storage.dong-liu.com/2023-01-14/SFX2P6KALDRVI142ZOMFXCVS3.webp
        key = "/".join(img_url.split("/")[-2:])
        #您要更新的生命周期
        days = '-1'
        ret, info = bucket.delete_after_days(bucket_name, key, days)
        assert info.status_code==200


    def store_gallery_image_information(self, img_url):
        generation_id = get_generation_id(img_url)
        image = Image.get_by_id(generation_id)
        image.published = True
        image.save()

    def get_random_samples_from_gallery(self, num):
        images = Image.select().where(Image.published==True).order_by(fn.Rand()).limit(num)
        ret = []
        for img in images:
            ret.append(img.imgurl)
        return ret 

    def add_check_image(self, img_url):
        self.r.rpush("Check",img_url)
        return True 

    def register_user(self,username,password):
        try:
            sub_str = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])","",username)
            if username!=sub_str:
                return False
            if len(username)>20:
                return False

            pw_hash = hashlib.sha1((username+password).encode("utf-8")).hexdigest()
            User.create(
                username=username,
                password=pw_hash,
                level=1
            )
            return True
        except:
            return False

    def verif_user(self,username,password):
        try:
            pw_hash = hashlib.sha1((username+password).encode("utf-8")).hexdigest()
            user = User.get(User.username==username and User.password==pw_hash)
            return True
        except:
            return False

    def get_userid(self, username):
        try:
            return str(User.get(User.username==username).userid)
        except:
            traceback.print_exc()
            return None

    def move_redis_gallery_to_mysql(self):
        for i in range(1,1+self.r.llen("Gal")):
            img_url = self.r.lindex("Gal",i)
            print(img_url)

            genid = get_generation_id(img_url)
            text2image_data = self.get_image_information(img_url)
            try:
                Image.get_by_id(genid)
            except:
                with self.mysql_db.atomic():
                    Image.create(
                        genid=genid,
                        imgurl=img_url,
                        params=json.dumps(text2image_data),
                        modelname=text2image_data['model_name'],
                        prompt=text2image_data['prompt'],
                        published=True,
                        userid=1 # 匿名用户
                    )

if __name__=="__main__":
    r=RClient()
    r.move_redis_gallery_to_mysql()
