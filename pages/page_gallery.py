
from functools import partial

from pywebio import config, session
from pywebio.io_ctrl import output_register_callback
from pywebio.output import *
from pywebio.pin import *
from pywebio_battery.web import *

from data import RClient
import time ,random
from utils.constants import *
from utils import task_post_upscale
from utils import get_username

from search import query_recent_images,query_by_input
import numpy as np 
@use_scope("popup_likes",clear=True)
def popup_cancel_like(userid, genid):
    session.local.rclient.cancel_likes(userid,genid)
    like_num = session.local.rclient.get_likenum(genid)
    put_html(thumbup_false).onclick(partial(popup_create_like,userid=userid,genid=genid)),
    put_text(like_num)

@use_scope("popup_likes",clear=True)
def popup_create_like(userid,genid):
    session.local.rclient.set_likes(userid,genid)
    like_num = session.local.rclient.get_likenum(genid)
    put_html(thumbup_true).onclick(partial(popup_cancel_like,userid=userid,genid=genid)),
    put_text(like_num)

def show_image_information_window(img_url,genid, fuke_func=None):
    generation_id = genid
    with popup("图像信息",size="large"):
        text2image_data = session.local.rclient.get_image_information(generation_id=genid)
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
                    put_scope("popup_user"),
                    put_scope("popup_likes")
                ]).style("margin:2%")
                if not session.local.client_id.startswith("@"): 
                    put_column([
                        put_button("复刻这张图", color="info", onclick=fuke_func),
                        put_button("获取高清图",color="info", onclick=partial(task_post_upscale, scope="popup_image_disp", img_url=img_url)),
                    ]).style("margin: 3%; text-align: center")

            with use_scope("popup_user"):
                put_text("作者: @"+text2image_data["user"])
                put_text("日期: "+text2image_data["gentime"].split(" ")[0])


            with use_scope("popup_likes"):
                # 登录否？
                like_num = session.local.rclient.get_likenum(generation_id)

                if session.local.client_id.startswith("@"):
                    
                    put_html(thumbup_false).onclick(lambda: toast("请先登录",duration=1)),
                    put_text(like_num)
                
                else:
                    userid = session.local.client_id
                    if session.local.rclient.check_likes(userid,generation_id):
                        put_html(thumbup_true).onclick(partial(popup_cancel_like,userid=userid,genid=generation_id)),
                        put_text(like_num)
                        
                    else:
                        put_html(thumbup_false).onclick(partial(popup_create_like,userid=userid,genid=generation_id)),
                        put_text(like_num)
                        

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
                put_select("model_name_info",label="模型",options=[MODEL_NAME_MAPPING_REVERSE[text2image_data['model_name']]],value=MODEL_NAME_MAPPING_REVERSE[text2image_data['model_name']]),
                if 'extra_model_name' not in text2image_data:
                    text2image_data['extra_model_name'] = "无"
                put_select("extra_model_info",label="附加模型",options=[text2image_data['extra_model_name']],value=text2image_data['extra_model_name']),

                put_input("seed_info",label="随机种子",value=text2image_data["seed"])
                

def open_main_page_with_generate_params(generate_url):
    session.run_js(f'window.open("{generate_url}", "_blank");')


def load_more_images_on_gallery(val=None):
    images = []
    for i in range(24):
        if len(session.local.image_list)>0:
            images.append(session.local.image_list.pop(0))
    # add images to the shortest col
    if len(images) > 0:
        for img_info in images:

            img_url = img_info["image"]
            height=img_info["height"]
            width = img_info['width']
            username=img_info['username']  
            genid = img_info["genid"]
            # find col
            short_ind = np.argmin(session.local.col_height)
            session.local.col_height[short_ind] += height * (256 / width)
            with use_scope("img-col"+str(short_ind)):
                img_url_md = img_url.replace(".jpeg",".md.jpeg")
                put_image(img_url_md).onclick(
                    partial(
                        show_image_information_window, 
                        img_url=img_url, genid=genid,
                        fuke_func=partial(open_main_page_with_generate_params, generate_url="/main?gen="+genid)
                    )
                )
            
@use_scope("image_flow",clear=True)
def get_search_images_on_gallery():
    session.local.col_height = [0,0,0,0,0,0]
    session.local.image_list = query_by_input(pin['search_prompt'],pin['search_model'],pin['search_user'])
    toast(f"搜索到{len(session.local.image_list)}张图像",duration=2)
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
    load_more_images_on_gallery(0)
    

@config(theme="minty", css_style=css, title='云景AI绘图平台',description="AI画图工具，输入文本生成图像，二次元、写实、人物、风景、设计素材，支持中文，图像库分享")
def page_gallery():
    session.set_env(title='云景 · 画廊', output_max_width='100%')
    session.local.rclient: RClient = RClient()
    session.local.last_task_time = time.time() - 3
    # 检查登录情况
    username = get_username()
    if username:
        session.local.client_id = session.local.rclient.get_userid(username)
        print(session.local.client_id)
    else:
    # 检查本地有没有cookie client id，如果没有，让服务器赋予一个。
        if get_cookie("client_id") is None or not get_cookie("client_id").startswith("@"):
            new_client_id = session.local.rclient.get_new_client_id()
            set_cookie("client_id", new_client_id)
        session.local.client_id = get_cookie("client_id")


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
    put_scope("search_scope")
    with use_scope("search_scope"):
        put_row([
            None,
            put_column([
                put_textarea("search_prompt",label="",placeholder="请输入关键词",rows=1),
                put_row([
                    put_select("search_model",label="",options=["模型: 任意"]+MODELS,value="模型: 任意"),
                    None,
                    put_textarea("search_user",label="",placeholder="（可选）请输入作者名",rows=1),
                    None,
                    put_button(label="搜索",onclick=get_search_images_on_gallery)
                ])
            ]),
            None
        ],size="5% 90% 5%")

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
    # random.shuffle(session.local.image_list) 
    load_more_images_on_gallery(0)
