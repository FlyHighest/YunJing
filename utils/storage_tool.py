import json,httpx
import requests

import httpx
from secret import tencentcloud_secret_id, tencentcloud_secret_key
import nanoid
import json 
import os 
import time
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

import os , json
import datetime
import base64
import hmac
import json
from hashlib import sha256 as sha256
from urllib.request import Request, urlopen
from PIL import Image 
from io import BytesIO
from secret import ilivedata_pid,ilivedata_secret

endpoint_host = 'isafe.ilivedata.com'
endpoint_path = '/api/v1/image/check'
endpoint_url = 'https://isafe.ilivedata.com/api/v1/image/check'

def img2base64(img):
    if type(img)==str:
        image = Image.open(img)
    else:
        image = img
    byte_data = BytesIO()# 创建一个字节流管道
    image.save(byte_data, format="webp")# 将图片数据存入字节流管道
    byte_data = byte_data.getvalue()# 从字节流管道中获取二进制
    base64_str = base64.b64encode(byte_data).decode("ascii")# 二进制转base64
    return base64_str


def check(image, type, user_id):
    now_date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    params = {
        "type": type,
        "strategyId":"001",
        "userId": str(user_id),
        "image": image
    }
    query_body = json.dumps(params)

    parameter = "POST\n"
    parameter += endpoint_host + "\n"
    parameter += endpoint_path + '\n'
    parameter += sha256(query_body.encode('utf-8')).hexdigest() + "\n"
    parameter += "X-AppId:" + ilivedata_pid + "\n"
    parameter += "X-TimeStamp:" + now_date

    signature = base64.b64encode(
        hmac.new(ilivedata_secret, parameter.encode('utf-8'), digestmod=sha256).digest())
    return send(query_body, signature, now_date)


def send(querystring, signature, time_stamp):
    headers = {
        "X-AppId": ilivedata_pid,
        "X-TimeStamp": time_stamp,
        "Content-type": "application/json",
        "Authorization": signature,
        "Host": endpoint_host,
        "Connection": "keep-alive"
    }

    # querystring = parse.urlencode(params)
    req = Request(endpoint_url, querystring.encode(
        'utf-8'), headers=headers, method='POST')
    response= urlopen(req).read().decode()
    res = json.loads(response)
    return int(res["result"])



class StorageTool:
    def __init__(self) -> None:
        
        region = None              # 通过自定义域名初始化不需要配置 region
        token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
        scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

        domain = 'images.dong-liu.com' # 用户自定义域名，需要先开启桶的自定义域名，具体请参见 https://cloud.tencent.com/document/product/436/36638
        config = CosConfig(Region=region, SecretId=tencentcloud_secret_id, SecretKey=tencentcloud_secret_key, Token=token, Domain=domain, Scheme=scheme)
        self.client = CosS3Client(config)
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
        self.tencent_url = "https://images.dong-liu.com/"
        
  
    def upload(self, img_path,userid="tmp"):
        return self.upload_tencent(img_path,userid)
        
    def upload_tencent(self,img_path,userid):
        response = None
        if os.path.exists(img_path.replace(".jpeg",".webp")):
            img_path = img_path.replace(".jpeg",".webp")
            
        key = f'{userid}/{nanoid.generate(self.alphabet,8)}.webp'
        for i in range(0, 5):
            try:
                response = self.client.upload_file(
                    Bucket='yunjing-images-1256692038',
                    Key=key,
                    LocalFilePath=img_path
                )
                response["image_url"] = self.tencent_url+key
                break
            except:
                continue
        if response is None:
            return ""
        else:
            return response["image_url"]
    
    def tencent_copy(self,image_url_temp,userid):
        source_key = image_url_temp[len(self.tencent_url):]
        key = f'{userid}/{nanoid.generate(self.alphabet,8)}.webp'
        self.client.copy(
            Bucket='yunjing-images-1256692038',
            Key=key,
            CopySource={
                'Bucket': 'yunjing-images-1256692038', 
                'Key': source_key, 
                'Region': 'ap-shanghai'
            }
        )

    def tencent_check_nsfw(self,image_url):
        key = image_url[len(self.tencent_url):]
        response = self.client.get_object_sensitive_content_recognition(
            Bucket='yunjing-images-1256692038',
            Key=key,
            BizType="7ae30966d9f89aa719fa2b5ed21074d7"
        )
        res = int(response["Result"])
        if res==0:
            return False
        else:
            self.client.delete_object(
                Bucket='yunjing-images-1256692038',
                Key=key
            )
            return True 

ST = StorageTool()
def is_url_image(image_url):
   r = httpx.head(image_url)
   if  r.headers["content-type"].startswith("image"):
      return True
   return False

def upload_to_storage(path):
    try:
        image_base64 = img2base64(path) 
        result = check(image_base64, 2, "tmp")
        if result==0:
            ret = ST.upload_tencent(path,"tmp")
        elif result==1:
            ret = ST.upload_tencent(path,"tmp")
            if ST.tencent_check_nsfw(ret):
                ret = ""
        else: # ret == 2, bad content
            ret = ""

        return ret 
    except:
        return ""

if __name__=="__main__":
    storage_tools = StorageTool()
    x = storage_tools.upload("nahida.jpg","PT5M")
    