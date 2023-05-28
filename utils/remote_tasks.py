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
from .mosec_api import generate_image

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
 
def task_post_enhance_prompt():
    session.run_js('''$("#pywebio-scope-input textarea:first").prop("disabled",true)''')
    try:
        before_post()
        data ={
            "type": "enhanceprompt",
            "starting_text":  pin['prompt'],
            "model_type": "universal"
        }
        post_data = json.dumps(data)
        prediction = httpx.post(
            MODEL_URL,
            data=post_data,
            timeout=180000
        )
        if prediction.status_code == 200:
            enhanced_text = json.loads(prediction.content)['enhanced_text']
            pin['prompt'] = enhanced_text
        else:
            ret = prediction.content.decode()
            if ret.startswith("request validation error: "):
                pin['prompt'] = ret.replace("request validation error: ","")
    except (ServerError, ConnectionRefusedError, httpx.ConnectError) as _:
        traceback.print_exc()
        toast(server_error_text,duration=4,color="warn")
    except QueueTooLong as _:
        traceback.print_exc()
        toast(queue_too_long_text, duration=4,color="warn" )
    except TooFrequent as _:
        toast(too_frequent_error_text, duration=4,color="warn")
    except NotLoginError as _:
        toast(not_login_error_text, duration=4,color="warn")
    except Exception as _:
        traceback.print_exc()
        toast(unknown_error_text,duration=4,color="warn")

    finally:
        session.run_js('''$("#pywebio-scope-input textarea:first").prop("disabled",false)''')

    
              

def task_post_upscale(scope, img_url):
    with use_scope(scope):
        try:
            before_post()
            with put_loading():
                upscale_data = {
                        "type":"upscale",
                        "img_url": img_url
                    }

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
                output_img_url = output_img_url

                put_link('高清图片链接',url=output_img_url,new_window=True)
                session.local.rclient.record_upscale_task()
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
        
