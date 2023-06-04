import json
import random
import time
import traceback
from functools import partial
import os 
import hashlib,httpx
from pywebio import session
from pywebio.output import *
from pywebio.pin import *
from pywebio_battery.web import *

from .custom_exception import *
from secret import MODEL_URL
from .storage_tool import get_presigned_url_tencent
from .constants import *
from .mosec_api import generate_image,upscale_image,prompt_enhance

def before_post():
    if session.local.client_id.startswith("@"):
        raise NotLoginError
    if time.time() - session.local.last_task_time < 3:
        raise TooFrequent
    else:
        session.local.last_task_time = time.time()
    if session.local.rclient.get_queue_size() > MAX_QUEUE:
        raise QueueTooLong


def task_publish_to_gallery(scope, genid):
    # check if has published 
    if session.local.rclient.check_published(genid):
        toast(has_published_text,color="warn")
        return
    
    ret = session.local.rclient.record_publish(genid)
        
    if ret:
        toast(publish_success_text, color="success")
    else:
        toast(publish_fail_text, color="warn")
 
              

def task_post_upscale(scope, img_url, genid, factor=2):
    with use_scope(scope):
        try:
            with put_loading():
                output_img_url = session.local.rclient.get_upscale_url(genid,factor)
                if output_img_url is None:
                    upscale_data = {
                            "type":"upscale",
                            "img_url": img_url,
                            "up_factor":factor,
                            "up_type":"anime"
                        }

                    output_img_url=upscale_image(upscale_data=upscale_data)
                    
                output_img_url_presigned = get_presigned_url_tencent(output_img_url)
                put_html(f'<a href="{output_img_url_presigned}" content-type="image/webp" download>点击下载高清图像(x{factor})</a>'),

                # put_link('高清图片链接',url=output_img_url_presigned,new_window=True)
                session.local.rclient.record_upscale_task(genid,output_img_url,factor)
        except ServerError as _:
            toast(server_error_text,   duration=4,color="warn")
        except QueueTooLong as _:
            toast(queue_too_long_text, duration=4,color="warn")
        except TooFrequent as _:
            toast(too_frequent_error_text, duration=4,color="warn")
        except NotLoginError as _:
            toast(not_login_error_text, duration=4,color="warn")
        except Exception as _:
            traceback.print_exc()
            toast(unknown_error_text , duration=4,color="warn")
        
