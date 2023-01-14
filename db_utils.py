'''
需要记录的信息
1. 用户信息，是否要做登陆，个人信息页面？
2. text2image图像信息库: 当用户点击上传到画廊时，将图像移到另一个桶，获得新的url，并保存图像信息
    - model_name          
    - scheduler_name      
    - prompt              
    - negative_prompt     
    - height              
    - width               
    - num_inference_steps 
    - guidance_scale      
    - seed
    - img_url
    - datetime : 提交时间
    - checked : 是否确认过是高质量图像
    - likes : 获赞数

'''
import nanoid
import redis
from utils import get_generation_id
CLIENT_ID_ALPHABET = "1234567890abcdefghjkmnpqrstuvwxyz"
GENERATION_ID_ALPHABET = "1234567890abcdefghjkmnpqrstuvwxyz"

EXP_7DAYS = 7*24*60*60


class RClient:

    def __init__(self) -> None:
        self.r = redis.Redis("localhost", 6379, decode_responses=True)
        self.r.set("mosec_queue", 0)

    # mosec服务器队列情况
    def enter_queue(self):
        self.r.incr("mosec_queue")

    def quit_queue(self):
        self.r.decr("mosec_queue")

    def get_queue_size(self):
        return int(self.r.get("mosec_queue"))

    # 用户历史记录相关
    def get_new_client_id(self):
        new_client_id = nanoid.generate(CLIENT_ID_ALPHABET, size=10)
        return new_client_id

    def append_history(self, client_id, img_url, text2image_data):
        self.r.rpush("His:"+client_id, img_url)
        self.store_history_image_information(text2image_data, img_url)

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
        self.r.hmset("InfoHis:"+generation_id, text2image_data)
        self.r.expire("InfoHis:"+generation_id, EXP_7DAYS)

    def store_gallery_image_information(self, img_url):
        generation_id = get_generation_id(img_url)
        text2image_data = self.r.hmget("InfoHis:"+generation_id, keys=[
            "type",
            "model_name",
            "scheduler_name",
            "prompt",
            "negative_prompt",
            "height",
            "width",
            "num_inference_steps",
            "guidance_scale",
            "seed"])
        self.r.hmset("InfoGal:"+generation_id, text2image_data)
