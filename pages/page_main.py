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
from utils import  get_username


def set_generation_params(generation_id):
    text2image_data = session.local.rclient.get_image_information(generation_id=generation_id)
    if text2image_data is None:
        toast(generation_outdated_error_text,color="warn",duration=4)
    else:
        pin.model_name = MODEL_NAME_MAPPING_REVERSE[text2image_data['model_name']]
        pin.scheduler_name = text2image_data["scheduler_name"]
        pin.prompt= text2image_data["prompt"] 
        pin.negative_prompt = text2image_data["negative_prompt"]
        pin.height = str(text2image_data["height"])
        pin.width = str(text2image_data["width"])
        pin.num_inference_steps = str(text2image_data["num_inference_steps"])
        pin.guidance_scale = text2image_data["guidance_scale"]
        pin.seed = text2image_data["seed"]

def close_popup_and_set_params(generation_id):
    close_popup()
    set_generation_params(generation_id)

def show_image_information_window(img_url,genid, fuke_func=None):
    generation_id = genid
    with popup("图像信息",size="large"):
        text2image_data = session.local.rclient.get_image_information(genid)
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
                        put_button("发布到画廊",color="info",onclick=partial(task_publish_to_gallery, scope="popup_image_disp", genid= genid)),
                        put_button("获取高清图",color="info", onclick=partial(task_post_upscale, scope="popup_image_disp", img_url=img_url)),
                        put_button("删除这张图",color="danger",onclick=partial(del_from_history,genid=genid))
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
  



def fill_prompt_template(template_key):
    fill_prompt, fill_neg_prompt = prompt_template[template_key]
    pin['prompt'] = fill_prompt
    pin['negative_prompt'] = fill_neg_prompt

def del_from_history(genid):
    session.local.rclient.del_history(session.local.client_id,genid)
    load_history()
    close_popup()

@use_scope('history_images',clear=True)
def load_history():
    session.local.history_image_cnt = 0
    for img,genid in session.local.rclient.get_history(session.local.client_id):
        put_image(img).onclick(partial(show_image_information_window,img_url=img, genid=genid))
        session.local.history_image_cnt += 1
    

@config(theme="minty", css_style=css, title='云景AI绘图平台',description="AI画图工具，输入文本生成图像，二次元、写实、人物、风景、设计素材，支持中文，图像库分享")
def page_main():
    session.set_env(title='云景 · 绘图', output_max_width='100%')
    session.local.rclient: RClient = RClient()
    # 检查有没有登陆
    username = get_username()
    if username:
        session.local.client_id = session.local.rclient.get_userid(username)
    else:
    # 检查本地有没有cookie client id，如果没有，让服务器赋予一个。
        if get_cookie("client_id") is None or not get_cookie("client_id").startswith("@"):
            new_client_id = session.local.rclient.get_new_client_id()
            set_cookie("client_id", new_client_id)
        session.local.client_id = get_cookie("client_id")
        toast("请先登录，正在跳转到“账户”页面 ...")
        time.sleep(1.5)
        session.run_js(f'window.open("/account", "_blank");')
        

    session.local.last_task_time = time.time() - 3
    
    if not session.local.client_id.startswith("@"):
        session.local.max_history_bonus = 190
    else:
        session.local.max_history_bonus = 0
    put_html(header_html_main)

    put_row(
        [
            put_scope('input'),  
            None, 
            put_scope('history'), 
        ],
        size="67% 3% 30%",
    )
    put_html("<hr />")
    put_scope('images').style("text-align: center")

    with use_scope('input'):
        put_select("model_name",label="模型",options=MODELS,value=MODELS[0]),

        prompt_templates = list(prompt_template.keys())
        put_scope("prompt_template")
 
        put_row([
            put_textarea('prompt',label="提示词",
                placeholder='例如：A car on the road, masterpiece, 8k wallpaper',
                rows=5,
            ),
            put_scope("prompt_operator")
            ],size="75% 25%")
        put_textarea('negative_prompt',label="反向提示词", placeholder="例如：NSFW, bad quality", rows=2)
        
        put_row([ 
            put_column(put_select("width",label="宽度",options=[str(64*i) for i in range(4,17,2)],value=str(512))),
            put_column(put_select("height",label="高度",options=[str(64*i) for i in range(4,17,2)],value=str(512))),
            put_column(put_select("num_inference_steps",label="推理步骤",options=["20","25","30","35","40"],value="30")),

        ])
        
        put_row([ 
            put_column(put_select("scheduler_name",label="采样器",options=SCHEDULERS,value="Euler_A")),
            put_slider('guidance_scale',label="引导程度",min_value=0,max_value=30,value=7,step=1),
            put_input("seed",label="随机种子",value="-1")
        ])

        put_scope("generate_button",put_button('   开始绘制   ',onclick=partial(task_post_image_gen,callback=show_image_information_window))).style("text-align: center")
    
    with use_scope("prompt_template"):
        put_select("prompt_template",label="提示词模板",options=prompt_templates,value="清空(提示词+反向提示词)"),
        pin_on_change("prompt_template",onchange=fill_prompt_template)

    with use_scope('prompt_operator'):
        put_column([
            None,
            put_button("帮我写!",color="info",onclick=task_post_enhance_prompt),

            None
        ],size="3fr 4fr 3fr")
        

        #.style("position: relative;top: 50%;transform: translateY(-30%);")s
    with use_scope('history'):
        put_text(f"历史记录 (保留{MAX_HISTORY+session.local.max_history_bonus}张，详细信息保留7天)")
        put_scrollable(put_scope('history_images'), height=0, keep_bottom=True, border=False)
    
    load_history()
        
    param_gen_id = get_query("gen")
    if param_gen_id is not None:
        set_generation_params(param_gen_id)

