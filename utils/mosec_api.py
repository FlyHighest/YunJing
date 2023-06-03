from secret import MODEL_URL
import json 
import httpx 
from .decorators import *
from .custom_exception import *
import requests 

@api_checker
@cd_checker
def generate_image(image_generation_data:dict):
    post_data = json.dumps(image_generation_data)
    prediction = requests.post(
                    MODEL_URL,
                    data=post_data,
                    timeout=180000
                )
    if prediction.status_code == 200:
        output = json.loads(prediction.content)
        output_img_url = output['img_url'] # url or Error
        nsfw = output['nsfw'] # bool
        score = output['score'] # float
        face = output['face'] # bool
        if output_img_url == "Error":
            raise ServerError
        return output_img_url, nsfw, score, face
    else:
        raise ServerError
    

@api_checker
def upscale_image(upscale_data:dict):
    post_data = json.dumps(upscale_data)
    prediction = httpx.post(
        MODEL_URL,
        data=post_data,
        timeout=180000
    )
    if prediction.status_code == 200:
        output_img_url = json.loads(prediction.content)['img_url']
        if output_img_url =="Error":
            raise ServerError
    else:
        raise ServerError
    return output_img_url