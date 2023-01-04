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
image_gen_text = ""
server_error_text = "服务器错误"


@use_scope('images', clear=True)
def preview_image_gen():
    global server_url
    
    session.run_js('''$("#pywebio-scope-input button").prop("disabled",true)''')

    try:
        with put_loading(shape="grow",color="primary"):
            text2image_data = {
                "type":"text2image",
                "model_name": "openjourney",
                "scheduler_name": pin['scheduler'],
                "prompt": pin['prompt'],
                "negative_prompt":pin['negative_prompt'],
                "height":pin['height'],
                "width": pin['width'],
                "num_inference_steps": pin['num_steps'],
                "guidance_scale": pin['guidance_scale']
            }
            print(text2image_data)
            prediction = httpx.post(
                MODEL_URL,
                data=json.dumps(text2image_data),
            )

            if prediction.status_code == 200:
                output_img_url = json.loads(prediction.content)['img_url']
                put_image(output_img_url)
            else:
                print(prediction.status_code, prediction.content)

    except Exception as e:
        logging.exception(e)
        clear()
        popup(server_error_text)

    session.run_js('''$("#pywebio-scope-input button").prop("disabled",false)''')



css = """
#pywebio-scope-images {
    height: calc(100vh - 150px);
    overflow-y: hidden;
}
#pywebio-scope-images:hover {
    overflow-y: scroll;
}
#pywebio-scope-input {
    height: calc(100vh - 150px);
    overflow-y: hidden;
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

@config(theme="minty", css_style=css)
def main():
    session.set_env(title='云景 · AI绘图', output_max_width='100%')
    
    # 设置背景图像
    #  session.run_js('''
    #     $("body").attr("style","background-image: url('http://storage.dong-liu.com/rabit-newyear.jpg');background-repeat: no-repeat;background-attachment: fixed;background-size: cover;")
    #     ''')

    put_row([ 
            put_column(put_markdown('# 云景 · AI绘图'))
        ])
    

    put_row(
        [
            put_scope('input'),
            None, 
            put_scope('images'),
            None,
            put_scrollable(put_scope('history'), height=100, keep_bottom=True)
        ],
        size="2fr 30px 6fr 30px 2fr",
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
            put_column(put_select("num_steps",label="推理步骤",options=[20,25,30,35,40],value=20)),
            put_column(put_select("scheduler",label="采样器",options=["DPM","K_Euler","K_EULER_ANCESTRAL","DDIM","K_LMS","PNDM"],value="DPM")),
        ])
        put_button('开始绘制',onclick=preview_image_gen)
    
    session.run_js('$("div.webio-scrollable.scrollable-border").css("max-height","calc(100vh - 150px)")')

    # with use_scope('history'):
        # put_image("http://storage.dong-liu.com/rabit-newyear.jpg")
        # put_markdown("---")
        # put_image("http://storage.dong-liu.com/rabit-newyear.jpg")
        # put_markdown("---")
        # put_image("http://storage.dong-liu.com/rabit-newyear.jpg")
        # put_markdown("---")
        # put_image("http://storage.dong-liu.com/rabit-newyear.jpg")
        # put_markdown("---")
        # put_image("http://storage.dong-liu.com/rabit-newyear.jpg")
        # put_markdown("---")
        # put_image("http://storage.dong-liu.com/rabit-newyear.jpg")
        # put_markdown("---")



if __name__ == '__main__':
    # app = web.Application()
    # app.add_routes([web.get('/', webio_handler(main, cdn=True))])

    # web.run_app(app, host='localhost', port=8800)
    start_server(main)
