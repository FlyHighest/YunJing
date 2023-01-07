import logging
from pywebio import session, config, start_server
from pywebio.output import *
from pywebio.pin import *

import time 
import httpx
from aiohttp import web
from pywebio.platform.aiohttp import webio_handler
from secret import MODEL_URL
import json

from custom_exception import *
image_gen_text = "正在生成，请稍后"
server_error_text = "服务器错误，请稍后再试"
nsfw_warn_text = "检测到不适宜内容，请尝试更换提示词或随机种子"
css = """
#pywebio-scope-history_images img {
    max-width: 45%;
    margin: 2%;
    border-radius: 6% ;
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


@use_scope('images', clear=True)
def preview_image_gen():
    toast(image_gen_text)
    session.run_js('''$("#pywebio-scope-generate_button button").prop("disabled",true)''')

    try:
        with put_loading(shape="border",color="primary"):
            text2image_data = {
                "type":"text2image",
                "model_name": pin['model_name'],
                "scheduler_name": pin['scheduler'],
                "prompt": pin['prompt'],
                "negative_prompt":pin['negative_prompt'],
                "height":pin['height'],
                "width": pin['width'],
                "num_inference_steps": pin['num_inference_steps'],
                "guidance_scale": pin['guidance_scale'],
                "seed": pin['seed']
            }

            post_data = json.dumps(text2image_data)
            prediction = httpx.post(
                MODEL_URL,
                data=post_data,
            )

        # 检查结果，异常抛出
        if prediction.status_code == 200:
            output_img_url = json.loads(prediction.content)['img_url']
            if output_img_url =="Error":
                raise ServerError
            elif output_img_url =="NSFW":
                raise NSFWDetected
            put_image(output_img_url)
        else:
            raise ServerError

        # 这里是正常处理
        put_row([
            put_button("下载", onclick=None),
            put_button("发布",onclick=lambda: toast("暂未开放"))
        ]).style("margin: 5%")
        with use_scope('history_images'):
            session.local.history_image_cnt += 1
            if  session.local.history_image_cnt == 21:
                session.local.history_image_cnt -= 1
                session.run_js('''$("#pywebio-scope-history_images img:first-child").remove()''')
            put_image(output_img_url)
        
    except NSFWDetected as _:
        toast(nsfw_warn_text,duration=4,color="warn")
    except ServerError as _:
        toast(server_error_text,duration=4,color="warn")
    except Exception as _:
        clear()
        popup(server_error_text)

    session.run_js('''$("#pywebio-scope-generate_button button").prop("disabled",false)''')


@config(theme="minty", css_style=css)
def main():
    session.set_env(title='云景 · AI绘图', output_max_width='100%')

    session.local.history_image_cnt = 0

    put_row([ 
            put_column(put_markdown('# 云景 · AI绘图')),
        ])
    
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
            put_column(put_select("num_inference_steps",label="推理步骤",options=[20,25,30,35,40],value=20)),
            put_column(put_select("scheduler",label="采样器",options=["DPM","EULER","EULER_A","DDIM","K_LMS","PNDM"],value="DPM")),
        ]),
        put_select("model_name",label="模型",options=["Stable-Diffusion-2.1","AltDiffusion","OpenJourney","Anything-v3","Taiyi-Chinese-v0.1"],value="AltDiffusion"),
        put_input("seed",label="随机种子",value="-1")
        put_scope("generate_button",put_button('开始绘制',onclick=preview_image_gen)).style("text-align: center")
    
    with use_scope('history'):
        put_text("历史记录 (仅保留20张)")
        put_scrollable(put_scope('history_images'), height=0, keep_bottom=True, border=False)


if __name__ == '__main__':
    # app = web.Application()
    # app.add_routes([web.get('/', webio_handler(main, cdn=True))])

    # web.run_app(app, host='localhost', port=8800)
    start_server(main,port=8888)
