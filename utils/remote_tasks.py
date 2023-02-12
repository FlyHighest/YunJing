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

from .constants import *

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
        toast("图像已发布在画廊，请勿重复发布")
        return
    with use_scope(scope):
        try:
            before_post()
            with put_loading():
                data = {
                    "type":"safety_check",
                    "img_url": session.local.rclient.get_imgurl_by_id(genid)
                }
                post_data = json.dumps(data)
                prediction = httpx.post(
                    MODEL_URL,
                    data=post_data,
                    timeout=180000
                )
                if prediction.status_code == 200:
                    output_img_url = json.loads(prediction.content)['result']
                    if output_img_url =="NSFW":
                        raise NSFWDetected
                else:
                    raise ServerError
                

                ret = session.local.rclient.record_publish(genid)
                
                if ret:
                    toast(publish_success_text, color="success")
                else:
                    toast(publish_fail_text, color="warn")
        except NSFWDetected as _:
            session.local.rclient.add_check_image(genid)
            toast(nsfw_warn_text_publish,duration=4,color="warn")
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
            toast(unknown_error_text , duration=4,color="warn")

def convert_int(s):
    try:
        return int(s)
    except:
        return -1

@use_scope('images', clear=False)
def task_post_image_gen(callback):
    clear()
    session.run_js('''$("#pywebio-scope-generate_button button").prop("disabled",true)''')
    try:
        before_post()
        toast(image_gen_text)
        with put_loading(shape="border",color="primary"):
            sharerate,num_gen,num_pub = session.local.rclient.get_sharerate(session.local.client_id)
            if sharerate < 10:
                if time.time() - session.local.rclient.get_lastgentime(session.local.client_id) < 8*(num_gen//50):
                    time.sleep(10)
                    raise ShareTooLow
            else:
                if time.time() - session.local.rclient.get_lastgentime(session.local.client_id) < 10:
                    time.sleep(3)
                    raise TooFrequent
            session.local.rclient.set_lastgentime(session.local.client_id)

            seed = convert_int(pin['seed'])
            
            seed = random.randint(-2**31,2**31-1) if seed==-1 else seed
        
            text2image_data = {
                "type":"text2image",
                "model_name":          MODEL_NAME_MAPPING[pin['model_name']],
                "scheduler_name":      pin['scheduler_name'],
                "prompt":              pin['prompt'],
                "negative_prompt":     pin['negative_prompt'],
                "height":              int(pin['height']),
                "width":               int(pin['width']),
                "num_inference_steps": int(pin['num_inference_steps']),
                "guidance_scale":      int(pin['guidance_scale']),
                "seed":                seed
            }
            image_gen_id = hashlib.sha1(json.dumps(text2image_data).encode('utf-8')).hexdigest()
            output_img_url = session.local.rclient.check_genid_in_imagetable(image_gen_id)

            if output_img_url is None:
                text2image_data['gen_id'] = image_gen_id
                post_data = json.dumps(text2image_data)
                prediction = httpx.post(
                    MODEL_URL,
                    data=post_data,
                    timeout=180000
                )
                if prediction.status_code == 200:
                    output = json.loads(prediction.content)
                    output_img_url = output['img_url']
                    nsfw = output['nsfw']
                    score = output['score']
                    session.local.current_img = output_img_url
                    if output_img_url =="Error":
                        raise ServerError
                    
                else:
                    raise ServerError
                output_img_url = output_img_url
            else:
                nsfw = False 
        put_image(output_img_url) # 大图output


        # 这里是正常处理
        if not nsfw:
            put_row([
                put_button("获取高清图",color="info", onclick=partial(task_post_upscale, scope="images",img_url=output_img_url)),
                put_button("发布到画廊",color="info",onclick=partial(task_publish_to_gallery,scope="images", genid=image_gen_id))
            ]).style("margin: 5%")
        
            # 历史记录相关
            with use_scope('history_images'):
                session.local.history_image_cnt += 1
                session.local.rclient.record_new_generated_image(session.local.client_id, output_img_url,image_gen_id,text2image_data,nsfw,score)

                if  session.local.history_image_cnt > MAX_HISTORY + session.local.max_history_bonus:
                    session.local.history_image_cnt -= 1
                    session.run_js('''$("#pywebio-scope-history_images img:first-child").remove()''')
                put_image(output_img_url).onclick(partial(callback, img_url=output_img_url,genid=image_gen_id))
        else:
            put_text("该图像可能含有不适宜工作场所观看的内容，本网站将不会留存该图像")
            toast(nsfw_warn_text_gen,color="warn",duration=3)
            session.local.rclient.record_new_generated_image(session.local.client_id, output_img_url,image_gen_id,text2image_data,nsfw,score)

    except NSFWDetected as _:
        toast(nsfw_warn_text_gen,duration=4,color="warn")
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
    except ShareTooLow as _:
        toast(share_too_low, duration=4, color="warn")
    except Exception as _:
        traceback.print_exc()
        toast(unknown_error_text,duration=4,color="warn")
    finally:
        session.run_js('''$("#pywebio-scope-generate_button button").prop("disabled",false)''')

def task_post_enhance_prompt():
    session.run_js('''$("#pywebio-scope-input textarea:first").prop("disabled",true)''')
    try:
        before_post()
        data ={
            "type": "enhanceprompt",
            "starting_text":  pin['prompt']
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
            raise ServerError
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
        
