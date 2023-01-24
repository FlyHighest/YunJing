
from functools import partial

from pywebio import config, session
from pywebio.io_ctrl import output_register_callback
from pywebio.output import *
from pywebio.pin import *
from pywebio_battery.web import *

from data import RClient

from utils.constants import *
from utils import task_post_upscale
from utils import get_generation_id

from search import query_recent_images
import numpy as np 

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
                put_row([
                    put_text("@"+text2image_data["user"]+"  |  "+text2image_data["gentime"].split(" ")[0])
                    #put_html(thumbup_false), #TODO 这里获取点赞状态和点赞数
                    #put_text("0")
                ])
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
                

def open_main_page_with_generate_params(generate_url):
    session.run_js(f'window.open("{generate_url}", "_blank");')


def load_more_images_on_gallery(val=None):
    images = []
    for i in range(10):
        if len(session.local.image_list)>0:
            images.append(session.local.image_list.pop(0))
    # add images to the shortest col
    if len(images) > 0:
        arr = []
        for img_info in images:

            img_url = img_info["image"]
            height=img_info["height"]
            width = img_info['width']
            username=img_info['username']  
            # find col
            short_ind = np.argmin(session.local.col_height)
            session.local.col_height[short_ind] += height * (256 / width)
            with use_scope("img-col"+str(short_ind)):
                put_image(img_url+"-w256").onclick(
                    partial(
                        show_image_information_window, 
                        img_url=img_url, 
                        fuke_func=partial(open_main_page_with_generate_params, generate_url="/main?gen="+get_generation_id(img_url))
                    )
                )
            
    

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
    with use_scope("image_flow"):
        put_row([
            put_scope("img-col0"),
            None,
            put_scope("img-col1"),
            None,
            put_scope("img-col2"),
            None,
            put_scope("img-col3"),
            None,
            put_scope("img-col4"),
            None,
            put_scope("img-col5"),
        ])
    session.local.col_height = [0,0,0,0,0,0]
    session.local.image_list = query_recent_images()
    load_more_images_on_gallery(0)
