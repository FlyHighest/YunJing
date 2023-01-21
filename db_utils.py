import random 
import nanoid , os, traceback
import redis
import httpx,re
from utils import get_generation_id
from secret import qiniu_access_key_id,qiniu_access_key_secret,qiniu_public_url, MODEL_URL
from qiniu import Auth as QiniuAuth
from qiniu import BucketManager as QiniuBucketManager
CLIENT_ID_ALPHABET = "1234567890abcdefghjkmnpqrstuvwxyz"
GENERATION_ID_ALPHABET = "1234567890abcdefghjkmnpqrstuvwxyz"

EXP_7DAYS = 7*24*60*60


class RClient:

    def __init__(self) -> None:
        self.r = redis.Redis("localhost", 6379, decode_responses=True)
        self.r.set("mosec_queue", 0)

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
            return int(self.r.get("status_gallery_num"))
        except:
            return 0

    # mosec服务器队列情况
    def enter_queue(self):
        self.r.incr("status_mosec_queue")

    def quit_queue(self):
        self.r.decr("status_mosec_queue")

    def get_queue_size(self):
        try:
            metrics = httpx.get(MODEL_URL.replace("inference","metrics")).content.decode()
            remain = re.findall(r"mosec_service_remaining_task \d+", metrics)[0]
            return int(remain.split(" ")[-1])
        except:
            return 0 

    # 用户历史记录相关
    def get_new_client_id(self):
        new_client_id = nanoid.generate(CLIENT_ID_ALPHABET, size=10)
        return new_client_id

    def record_new_generated_image(self, client_id, img_url, text2image_data):
        self.r.rpush("His:"+client_id, img_url)
        self.r.expire("His:"+client_id, EXP_7DAYS)
        self.store_history_image_information(text2image_data, img_url)
        self.add_generated_number()

    def pop_history(self, client_id):
        img_url = self.r.lpop("His:"+client_id)
        self.r.delete("InfoHis:"+get_generation_id(img_url))

    def get_history(self, client_id):
        return self.r.lrange("His:"+client_id, 0, -1)

    def get_history_length(self, client_id):
        try:
            return self.r.llen("His:"+client_id)
        except:
            return 0

    # 图像信息存储
    # HisInfo:generation_id : image information dict
    # 用户历史图像的信息存储，pop history时删除，设置exp为7天。
    # 上传到画廊的，信息永久存储，且同步到mysql数据库。
    # GalleryInfo:generation_id : image information dict
    def store_history_image_information(self, text2image_data, img_url):
        generation_id = get_generation_id(img_url)
        text2image_data["img_url"] = img_url
        self.r.hmset("InfoHis:"+generation_id, text2image_data)
        self.r.expire("InfoHis:"+generation_id, EXP_7DAYS)

    def get_image_information(self, img_url=None, generation_id=None):
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
        if text2image_data['type'] is not None:
            return text2image_data
        else :
            return None 

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
        print(key)
        ret, info = bucket.delete_after_days(bucket_name, key, days)
        assert info.status_code==200


    def store_gallery_image_information(self, img_url):
        generation_id = get_generation_id(img_url)
        text2image_data = self.get_image_information(img_url)
        self.r.hmset("InfoGal:"+generation_id, text2image_data)
        self.r.rpush("Gal", img_url)

    def get_random_samples_from_gallery(self, num):
        size = self.r.llen("Gal")
        ret = []
        for _ in range(num):
            ind = random.randint(0,size-1)
            ret.append(self.r.lindex("Gal", ind))
        return ret 