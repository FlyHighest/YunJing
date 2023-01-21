import logging
from pywebio import session, config, start_server
from pywebio.output import *
from pywebio.pin import *
from pywebio_battery.web import *
import traceback
import httpx
from secret import MODEL_URL
import json
from db_utils import RClient
from custom_exception import *
import random 
import os 
from functools import partial
from utils import get_generation_id
from pywebio.io_ctrl import output_register_callback
import time 
import tornado.ioloop
import tornado.web
from pywebio.platform.tornado import webio_handler

from constants import *

def publish_to_gallery(img_url):
    ret = session.local.rclient.record_publish(img_url)
    if ret:
        toast(publish_success_text, color="success")
    else:
        toast(publish_fail_text, color="warn")

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

# @popup("title")
def show_image_information_window(img_url, fuke_func=None):
    generation_id = get_generation_id(img_url)
    with popup("图像信息"):
        text2image_data = session.local.rclient.get_image_information(img_url)
        if text2image_data is None:
            put_warning(generation_outdated_error_text)
        else:
            put_row([ 
                put_scope("popup_image_disp").style("text-align: center"),
                None,
                put_scope("popup_image_info")
            ],size="48% 4% 48%")
            with use_scope("popup_image_disp"):
                put_image(img_url)
                if fuke_func is None:
                    put_column([
                        put_button("复刻这张图", color="info", onclick=partial(close_popup_and_set_params, generation_id=generation_id)),
                        put_button("发布到画廊",color="info",onclick=partial(publish_to_gallery, img_url= img_url)),
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
                

def task_post_upscale(scope, img_url):
    with use_scope(scope):
        try:
            
            if session.local.rclient.get_queue_size() > MAX_QUEUE:
                raise QueueTooLong
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
                
                put_link('高清图片链接',url=output_img_url,new_window=True)
                session.local.rclient.record_upscale_task()
        except ServerError as _:
            toast(server_error_text,   duration=4,color="warn")
        except QueueTooLong as _:
            toast(queue_too_long_text, duration=4,color="warn")
        except TooFrequent as _:
            toast(too_frequent_error_text, duration=4,color="warn")
        except Exception as _:
            traceback.print_exc()
            toast(unknown_error_text , duration=4,color="warn")
        

def convert_int(s):
    try:
        return int(s)
    except:
        return -1

def before_post():
    if time.time() - session.local.last_task_time < 3:
        raise TooFrequent
    else:
        session.local.last_task_time = time.time()
    if session.local.rclient.get_queue_size() > MAX_QUEUE:
        raise QueueTooLong



@use_scope('images', clear=False)
def task_post_image_gen():


    clear()
    session.run_js('''$("#pywebio-scope-generate_button button").prop("disabled",true)''')
    try:
        before_post()
        toast(image_gen_text)
        with put_loading(shape="border",color="primary"):
            seed = convert_int(pin['seed'])
            
            seed = random.randint(-2**31,2**31-1) if seed==-1 else seed
        
            text2image_data = {
                "type":"text2image",
                "model_name":          pin['model_name'],
                "scheduler_name":      pin['scheduler_name'],
                "prompt":              pin['prompt'],
                "negative_prompt":     pin['negative_prompt'],
                "height":              int(pin['height']),
                "width":               int(pin['width']),
                "num_inference_steps": int(pin['num_inference_steps']),
                "guidance_scale":      int(pin['guidance_scale']),
                "seed":                seed
            }

            post_data = json.dumps(text2image_data)
            prediction = httpx.post(
                MODEL_URL,
                data=post_data,
                timeout=180000
            )

        # 检查结果，异常抛出
        if prediction.status_code == 200:
            output_img_url = json.loads(prediction.content)['img_url']
            session.local.current_img = output_img_url
            if output_img_url =="Error":
                raise ServerError
            elif output_img_url =="NSFW":
                raise NSFWDetected
            put_image(output_img_url) # 大图output
        else:
            raise ServerError

        # 这里是正常处理
        put_row([
            put_button("获取高清图(x4)",color="info", onclick=partial(task_post_upscale, scope="images",img_url=output_img_url)),
            put_button("发布到画廊",color="info",onclick=partial(publish_to_gallery,img_url=output_img_url))
        ]).style("margin: 5%")

        # 历史记录相关
        with use_scope('history_images'):
            session.local.history_image_cnt += 1
            session.local.rclient.record_new_generated_image(session.local.client_id, output_img_url,text2image_data)

            if  session.local.history_image_cnt > MAX_HISTORY:
                session.local.history_image_cnt -= 1
                session.local.rclient.pop_history(session.local.client_id)
                session.run_js('''$("#pywebio-scope-history_images img:first-child").remove()''')
            put_image(output_img_url).onclick(partial(show_image_information_window, img_url=output_img_url))
        
    except NSFWDetected as _:
        toast(nsfw_warn_text,duration=4,color="warn")
    except (ServerError, ConnectionRefusedError, httpx.ConnectError) as _:
        traceback.print_exc()
        toast(server_error_text,duration=4,color="warn")
    except QueueTooLong as _:
        traceback.print_exc()
        toast(queue_too_long_text, duration=4,color="warn" )
    except TooFrequent as _:
        toast(too_frequent_error_text, duration=4,color="warn")
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
    except Exception as _:
        traceback.print_exc()
        toast(unknown_error_text,duration=4,color="warn")

    finally:
        session.run_js('''$("#pywebio-scope-input textarea:first").prop("disabled",false)''')

    

@config(theme="minty", css_style=css)
def page_main():
    session.set_env(title='云景 · 绘图', output_max_width='100%')
    session.local.rclient: RClient = RClient()
    # 检查本地有没有cookie client id，如果没有，让服务器赋予一个。
    if get_cookie("client_id") is None:
        new_client_id = session.local.rclient.get_new_client_id()
        set_cookie("client_id", new_client_id)
    session.local.client_id = get_cookie("client_id")
    session.local.last_task_time = time.time()
    session.local.history_image_cnt = session.local.rclient.get_history_length(session.local.client_id)
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
        put_scope("generate_button",put_button('开始绘制',onclick=task_post_image_gen)).style("text-align: center")
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
    
    param_gen_id = get_query("gen")
    if param_gen_id is not None:
        set_generation_params(param_gen_id)


def open_main_page_with_generate_params(generate_url):
    session.run_js(f'window.open("{generate_url}", "_blank");')


@use_scope("image_flow")
def load_more_images_on_gallery(val):
    img_url_list = session.local.rclient.get_random_samples_from_gallery(IMAGE_NUM_PER_LOAD)
    # for i in range(0,IMAGE_NUM_PER_LOAD,IMAGE_NUM_PER_ROW):
    #     put_row([
    #         put_image(img_url+"-w220").onclick(
    #             partial(
    #                 show_image_information_window, 
    #                 img_url=img_url, 
    #                 fuke_func=partial(open_main_page_with_generate_params, generate_url="/main?gen="+get_generation_id(img_url))
    #             )
    #         )
    #         for img_url in img_url_list[i : i + IMAGE_NUM_PER_ROW]
    #     ]) 
    
    for img_url in img_url_list:
        put_image(img_url+"-w256").onclick(
                partial(
                    show_image_information_window, 
                    img_url=img_url, 
                    fuke_func=partial(open_main_page_with_generate_params, generate_url="/main?gen="+get_generation_id(img_url))
                )
            )
            
    session.run_js("""
        requirejs(["//unpkg.com/masonry-layout@4/dist/masonry.pkgd"], function( Masonry ) {
            new Masonry( '#pywebio-scope-image_flow',{ 
                percentPosition: true,horizontalOrder: true
            });
        });
    """)

@config(theme="minty", css_style=css)
def page_gallery():
    session.set_env(title='云景 · 画廊', output_max_width='100%')
    session.local.rclient: RClient = RClient()
    callback_loadimages_id = output_register_callback(load_more_images_on_gallery)
    put_html(header_html_gallery)

    put_html("""
    <script>
           var index = 0;
        function lowEnough(){
            var pageHeight = Math.max(document.body.scrollHeight,document.body.offsetHeight);
            var viewportHeight = window.innerHeight || 
                document.documentElement.clientHeight ||
                document.body.clientHeight || 0;
            var scrollHeight = window.pageYOffset ||
                document.documentElement.scrollTop ||
                document.body.scrollTop || 0;

            return pageHeight - viewportHeight - scrollHeight < 20;
        }

        function doSomething(){
            WebIO.pushData("1",%r)
            pollScroll();//继续循环
        }

        function checkScroll(){
            if(!lowEnough()) return pollScroll();

            setTimeout(doSomething,900);

        }
        function pollScroll(){
            setTimeout(checkScroll,1000);
        }
        checkScroll();
    </script>
    """%callback_loadimages_id)
    # put_row([ 
    #         put_column(put_markdown('## 云景 · 画廊')),
    #     ])
    put_scope("image_flow")

    load_more_images_on_gallery(0)

@use_scope("current_server_status",clear=True)
def show_server_status():
    queue_size, generated_num, upscale_num, gallery_num = session.local.rclient.get_server_status()
    put_markdown(f" \
- 当前排队任务数：{queue_size} \n\
- 已生成图像数：{generated_num} \n\
- 超分辨率次数：{upscale_num} \n\
- 画廊图像数：{gallery_num}  \
    ") 

@config(theme="minty", css_style=css)
def page_index():
    session.set_env(title='云景 · 首页', output_max_width='80%')
    session.local.rclient: RClient = RClient()
    put_html(header_html_index)

    put_markdown("# 云景 · 首页")
    put_markdown("""

[云景 · 绘图](/main)：在这里创作您的作品，用一组文本描述绘制画面。

[云景 · 画廊](/gallery)：在这里分享您的创作参数，并参考别人的作品，也许其他人的经验能为您提供良好的开端。

------
    
1. 免费的在线生成服务，无需付费、无广告烦扰。
2. 多种最新模型一键切换。
3. 在画廊，与其他人分享你的创意或者复刻他人的创意(请勿公开发布不适合工作场合观看的内容)。
    """)
    put_markdown("## 服务器状态")
    put_button("刷新",onclick=show_server_status)
    put_scope("current_server_status")
    show_server_status()
    put_markdown("""
------
如果您有疑问或者建议，欢迎加入交流群(QQ): 557228477
    """)


if __name__ == '__main__':
    application = tornado.web.Application([
        ('/', webio_handler(page_index, cdn=True)),
        ('/main', webio_handler(page_main, cdn=True)),
        ('/gallery', webio_handler(page_gallery, cdn=True))
    ])
    application.listen(port=5001, address='localhost')
    tornado.ioloop.IOLoop.current().start()

    # start_server(gallery, port=5001)