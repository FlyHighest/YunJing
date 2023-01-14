import logging
from pywebio import session, config, start_server
from pywebio.output import *
from pywebio.pin import *
from pywebio_battery.web import *
import traceback
import time 
import httpx
from aiohttp import web
from pywebio.platform.aiohttp import webio_handler
from secret import MODEL_URL
import json
from db_utils import RClient
from custom_exception import *
import random 
import os 
from functools import partial
from utils import get_generation_id

MAX_HISTORY = 10
MAX_QUEUE = 10

image_gen_text = "正在生成，请稍后"
server_error_text = "模型服务错误，请稍后再试"
nsfw_warn_text = "检测到不适宜内容，请尝试更换提示词或随机种子"
queue_too_long_text = "当前排队过长，请稍后再试"
unknown_error_text = "未知错误"

css = """
#pywebio-scope-history_images img {
    max-width: 45%;
    margin: 2%;
    border-radius: 6% ;
}
#pywebio-scope-history_images img:hover {
    transform: scale(1.05);
}
#pywebio-scope-images {
    height: calc(100vh - 150px);
    overflow-y: scroll;
}
#pywebio-scope-history {
    height: calc(100vh - 150px);
    overflow-y: scroll;
}
#pywebio-scope-history:hover {
    overflow-y: scroll;
}
#pywebio-scope-images:hover {
    overflow-y: scroll;
}
#pywebio-scope-input {
    height: calc(100vh - 150px);
    overflow-y: scroll;
}
#pywebio-scope-input:hover {
    overflow-y: scroll;
}
/* Works on Firefox */
* {
  scrollbar-width: thin;
}
/* Works on Chrome, Edge, and Safari */
*::-webkit-scrollbar {
  width: 7px;
}
*::-webkit-scrollbar-track {
  background: transparent;
}
*::-webkit-scrollbar-thumb {
  background-color: gray;
  border-radius: 20px;
  border: 2px
}
"""

# @popup("title")
def show_image_information_window(img_url):
    text2image_data = session.local.rclient.get_history_image_information(img_url)
    put_row([ 
        put_image(img_url),
        put_scope("popup_image_info")
    ])
    with use_scope("popup_image_info"):
        put_text("提示词: "+text2image_data["prompt"])
        put_text("反向提示词: "+text2image_data["negative_prompt"])
        put_row([ 
            put_column(put_select("width",label="宽度",value=text2image_data["width"])),
            put_column(put_select("height",label="高度",value=text2image_data["height"])),
        ])
        put_slider('guidance_scale',label="引导程度",min_value=0,max_value=30,value=text2image_data["guidance_scale"])
        put_row([ 
            put_column(put_select("num_inference_steps",label="推理步骤",options=[20,25,30,35,40],value=text2image_data["num_inference_steps"])),
            put_column(put_select("scheduler",label="采样器",value=text2image_data["scheduler"])),
        ]),
        put_select("model_name",label="模型",value=text2image_data["model_name"]),
        put_input("seed",label="随机种子",value=text2image_data["seed"])
        

@use_scope('images', clear=False)
def put_upscale_url():
    session.local.rclient.enter_queue()
    try:
        if session.local.rclient.get_queue_size() > MAX_QUEUE:
            raise QueueTooLong
        with put_loading():
            upscale_data = {
                    "type":"upscale",
                    "img_url":session.local.current_img
                }

            post_data = json.dumps(upscale_data)
            prediction = httpx.post(
                MODEL_URL,
                data=post_data,
            )
            if prediction.status_code == 200:
                output_img_url = json.loads(prediction.content)['img_url']
                session.local.current_img = output_img_url
                if output_img_url =="Error":
                    raise ServerError

            else:
                raise ServerError
            
            put_link('高清图片链接',url=output_img_url,new_window=True)

    except ServerError as _:
        toast(server_error_text,   duration=4,color="warn")
    except QueueTooLong as _:
        toast(queue_too_long_text, duration=4,color="warn")
    except Exception as _:
        toast(unknown_error_text , duration=4,color="warn")

    session.local.rclient.enter_queue()




@use_scope('images', clear=False)
def preview_image_gen():
    toast(image_gen_text)
    clear()
    session.run_js('''$("#pywebio-scope-generate_button button").prop("disabled",true)''')
    session.local.rclient.enter_queue()
    try:
        if session.local.rclient.get_queue_size() > MAX_QUEUE:
            raise QueueTooLong

        with put_loading(shape="border",color="primary"):
            if int(pin['seed'])==-1:
                # 可复现的生成。
                seed = random.randint(-2**31,2**31-1)
                
            text2image_data = {
                "type":"text2image",
                "model_name":          pin['model_name'],
                "scheduler_name":      pin['scheduler'],
                "prompt":              pin['prompt'],
                "negative_prompt":     pin['negative_prompt'],
                "height":              pin['height'],
                "width":               pin['width'],
                "num_inference_steps": pin['num_inference_steps'],
                "guidance_scale":      pin['guidance_scale'],
                "seed":                seed
            }

            post_data = json.dumps(text2image_data)
            prediction = httpx.post(
                MODEL_URL,
                data=post_data,
                timeout=40000
            )

        # 检查结果，异常抛出
        if prediction.status_code == 200:
            output_img_url = json.loads(prediction.content)['img_url']
            session.local.current_img = output_img_url
            if output_img_url =="Error":
                raise ServerError
            elif output_img_url =="NSFW":
                raise NSFWDetected
            put_image(output_img_url)
        else:
            raise ServerError

        # 这里是正常处理
        put_row([
            put_button("获取高清图(x4)",color="info", onclick=put_upscale_url),
            put_button("发布到画廊",color="info",onclick=lambda: toast("暂未开放"))
        ]).style("margin: 5%")

        # 历史记录相关
        with use_scope('history_images'):
            session.local.history_image_cnt += 1
            session.local.rclient.append_history(session.local.client_id, output_img_url)

            if  session.local.history_image_cnt > MAX_HISTORY:
                session.local.history_image_cnt -= 1
                session.local.rclient.pop_history(session.local.client_id)
                session.run_js('''$("#pywebio-scope-history_images img:first-child").remove()''')
            put_image(output_img_url)
        
    except NSFWDetected as _:
        toast(nsfw_warn_text,duration=4,color="warn")
    except (ServerError, ConnectionRefusedError, httpx.ConnectError) as _:
        traceback.print_exc()
        toast(server_error_text,duration=4,color="warn")
    except QueueTooLong as _:
        traceback.print_exc()
        toast(queue_too_long_text, duration=4,color="warn" )
    except Exception as _:
        traceback.print_exc()
        toast(unknown_error_text,duration=4,color="warn")

    session.run_js('''$("#pywebio-scope-generate_button button").prop("disabled",false)''')
    session.local.rclient.quit_queue()


@config(theme="minty", css_style=css)
def main():
    session.set_env(title='云景 · AI绘图', output_max_width='100%')

    session.local.rclient: RClient = RClient()
    # 检查本地有没有cookie client id，如果没有，让服务器赋予一个。
    if get_cookie("client_id") is None:
        new_client_id = session.local.rclient.get_new_client_id()
        set_cookie("client_id", new_client_id)
    session.local.client_id = get_cookie("client_id")

    session.local.history_image_cnt = session.local.rclient.get_history_length(session.local.client_id)


    # put_row([ 
    #         put_column(put_markdown('# 云景 · AI绘图')),
    #     ])
    
    put_row(
        [
            put_scope('input'),   
            put_scope('images').style("text-align: center"),
            put_scope('history'), 
        ],
        size="3fr 4fr 3fr",
    )

    with use_scope('input'):
        put_textarea('prompt',label="提示词",
            placeholder='例如：A car on the road, masterpiece, 8k wallpaper',
            rows=5,
        )
        put_textarea('negative_prompt',label="反向提示词", placeholder="例如：NSFW, bad quality", rows=2)
        put_row([ 
            put_column(put_select("width",label="宽度",options=[256,384,512,640,768],value=512)),
            put_column(put_select("height",label="高度",options=[256,384,512,640,768],value=512)),
        ])
        put_slider('guidance_scale',label="引导程度",min_value=0,max_value=30,value=7,step=0.5)
        put_row([ 
            put_column(put_select("num_inference_steps",label="推理步骤",options=[20,25,30,35,40],value=30)),
            put_column(put_select("scheduler",label="采样器",options=["DPM","EULER","EULER_A","DDIM","K_LMS","PNDM"],value="DPM")),
        ]),
        put_select("model_name",label="模型",options=["OpenJourney","Anything-v3","Taiyi-Chinese-v0.1","Stable-Diffusion-2.1","AltDiffusion"],value="OpenJourney"),
        put_input("seed",label="随机种子",value="-1")
        put_scope("generate_button",put_button('开始绘制',onclick=preview_image_gen)).style("text-align: center")
    
    with use_scope('history'):
        put_text(f"历史记录 (保留{MAX_HISTORY}张，详细信息保留7天)")
        put_scrollable(put_scope('history_images'), height=0, keep_bottom=True, border=False)
    
    with use_scope('history_images'):
        for img in session.local.rclient.get_history(session.local.client_id):
            put_image(img).onclick(partial(show_image_information_window, img_url=img))

if __name__ == '__main__':
    # app = web.Application()
    # app.add_routes([web.get('/', webio_handler(main, cdn=True))])

    # web.run_app(app, host='localhost', port=5001)
    start_server(main, port=5001)