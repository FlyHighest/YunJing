import time
from functools import partial

from pywebio import config, session
from pywebio.output import *
from pywebio.pin import *
from pywebio_battery.web import *

from utils.custom_exception import *
from data import RClient

from utils.constants import *
from utils import (task_post_enhance_prompt, task_post_image_gen,
                           task_post_upscale, task_publish_to_gallery)
from utils import get_generation_id, get_username


def set_generation_params(generation_id):
    text2image_data = session.local.rclient.get_image_information(generation_id=generation_id)
    if text2image_data is None:
        toast(generation_outdated_error_text,color="warn",duration=4)
    else:
        pin.model_name = text2image_data['model_name']
        pin.scheduler_name = text2image_data["scheduler_name"]
        pin.prompt= text2image_data["prompt"] 
        pin.negative_prompt = text2image_data["negative_prompt"]
        pin.height = text2image_data["height"]
        pin.width = text2image_data["width"]
        pin.num_inference_steps = text2image_data["num_inference_steps"]
        pin.guidance_scale = text2image_data["guidance_scale"]
        pin.seed = text2image_data["seed"]

def close_popup_and_set_params(generation_id):
    close_popup()
    set_generation_params(generation_id)

def show_image_information_window(img_url, fuke_func=None):
    generation_id = get_generation_id(img_url)
    with popup("图像信息",size="large"):
        text2image_data = session.local.rclient.get_image_information(img_url)
        if text2image_data is None:
            put_warning(generation_outdated_error_text)
        else:
            put_row([ 
                put_scope("popup_image_disp").style("text-align: center"),
                None,
                put_scope("popup_image_info")
            ],size="66% 2% 32%")
            with use_scope("popup_image_disp"):
                put_image(img_url)
                if fuke_func is None:
                    put_column([
                        put_button("复刻这张图", color="info", onclick=partial(close_popup_and_set_params, generation_id=generation_id)),
                        put_button("发布到画廊",color="info",onclick=partial(task_publish_to_gallery, scope="popup_image_disp", img_url= img_url)),
                        put_button("获取高清图",color="info", onclick=partial(task_post_upscale, scope="popup_image_disp", img_url=img_url)),
                    ]).style("margin: 3%; text-align: center")
                else:
                    put_column([
                        put_button("复刻这张图", color="info", onclick=fuke_func),
                        put_button("获取高清图",color="info", onclick=partial(task_post_upscale, scope="popup_image_disp", img_url=img_url)),
                    ]).style("margin: 3%; text-align: center")


            with use_scope("popup_image_info"):
                put_text("✅ "+ (text2image_data["prompt"] or "(无提示词)" ) )
                
                put_text("❌ "+ (text2image_data["negative_prompt"] or "(无反向提示词)" ) )
                put_row([ 
                    put_column(put_select("width_info",label="宽度",options=[text2image_data["width"]],value=text2image_data["width"])),
                    put_column(put_select("height_info",label="高度",options=[text2image_data["height"]],value=text2image_data["height"])),
                ])
                put_slider('guidance_scale_info',label="引导程度",min_value=0,max_value=30,value=text2image_data["guidance_scale"])
                put_row([ 
                    put_column(put_select("num_inference_steps_info",label="推理步骤",options=[text2image_data["num_inference_steps"]],value=text2image_data["num_inference_steps"])),
                    put_column(put_select("scheduler_name_info",label="采样器",options=[text2image_data["scheduler_name"]],value=text2image_data["scheduler_name"])),
                ]),
                put_select("model_name_info",label="模型",options=[text2image_data["model_name"]],value=text2image_data["model_name"]),
                put_input("seed_info",label="随机种子",value=text2image_data["seed"])
  





@config(theme="minty", css_style=css)
def page_main():
    session.set_env(title='云景 · 绘图', output_max_width='100%')
    session.local.rclient: RClient = RClient()
    # 检查有没有登陆
    username = get_username()
    if username:
        session.local.client_id = session.local.rclient.get_userid(username)
        print(session.local.client_id)
    else:
    # 检查本地有没有cookie client id，如果没有，让服务器赋予一个。
        if get_cookie("client_id") is None:
            new_client_id = session.local.rclient.get_new_client_id()
            set_cookie("client_id", new_client_id)
        session.local.client_id = get_cookie("client_id")

    session.local.last_task_time = time.time() - 3
    session.local.history_image_cnt = 0
    if not session.local.client_id.startswith("@"):
        session.local.max_history_bonus = 90
    else:
        session.local.max_history_bonus = 0
    put_html(header_html_main)
    # put_row([ 
    #         put_column(put_markdown('## 云景 · 绘图')),
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
        put_row([
            put_textarea('prompt',label="提示词",
                placeholder='例如：A car on the road, masterpiece, 8k wallpaper',
                rows=5,
            ),
            None,
            put_scope("prompt_operator")
        ],size="77% 3% 20%")
        put_textarea('negative_prompt',label="反向提示词", placeholder="例如：NSFW, bad quality", rows=2)
        put_row([ 
            put_column(put_select("width",label="宽度",options=[str(64*i) for i in range(4,17,2)],value=str(512))),
            put_column(put_select("height",label="高度",options=[str(64*i) for i in range(4,17,2)],value=str(512))),
        ])
        put_slider('guidance_scale',label="引导程度",min_value=0,max_value=30,value=7,step=0.5)
        put_row([ 
            put_column(put_select("num_inference_steps",label="推理步骤",options=["20","25","30","35","40"],value="30")),
            put_column(put_select("scheduler_name",label="采样器",options=SCHEDULERS,value="Euler_A")),
        ]),
        put_select("model_name",label="模型",options=MODELS,value=MODELS[0]),
        put_input("seed",label="随机种子",value="-1")
        put_scope("generate_button",put_button('开始绘制',onclick=partial(task_post_image_gen,callback=show_image_information_window))).style("text-align: center")
    with use_scope('prompt_operator'):
        def clear_prompt():
            pin['prompt']=""
        put_column([
            None,
            put_button("帮我写!",color="info",onclick=task_post_enhance_prompt), 
            None,
            put_button("清空",color="info",onclick=clear_prompt )
        ], size="25% 25% 25% 25%").style("text-align:center")

        #.style("position: relative;top: 50%;transform: translateY(-30%);")s
    with use_scope('history'):
        put_text(f"历史记录 (保留{MAX_HISTORY}张，详细信息保留7天)")
        put_scrollable(put_scope('history_images'), height=0, keep_bottom=True, border=False)
    
    with use_scope('history_images'):
        for img in session.local.rclient.get_history(session.local.client_id):
            put_image(img).onclick(partial(show_image_information_window, img_url=img))
            session.local.history_image_cnt += 1
    
    param_gen_id = get_query("gen")
    if param_gen_id is not None:
        set_generation_params(param_gen_id)

