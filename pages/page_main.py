import time, os,nanoid,string
from functools import partial

from pywebio import config, session
from pywebio.output import *
from pywebio.pin import *
from pywebio_battery.web import *
from pywebio.input import file_upload,actions,input_group
from utils.custom_exception import *
from data import RClient

from utils.constants import *
from utils import (task_post_enhance_prompt, task_post_image_gen,
                           task_post_upscale, task_publish_to_gallery)
from utils import gpt_image_describe
from utils import  get_username,put_column_autosize,upload_to_storage,put_row_autosize


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
        if 'extra_model_name' in text2image_data:
            pin.extra_model = text2image_data['extra_model_name']

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
                put_column([
                    put_html(f'<a href="{img_url}" content-type="image/webp" download>下载图像</a>'),
                    put_button("复刻这张图", color="info", onclick=partial(close_popup_and_set_params, generation_id=generation_id)),
                    put_button("发布到画廊",color="info",onclick=partial(task_publish_to_gallery, scope="popup_image_disp", genid= genid)),
                    # put_button("获取高清图",color="info", onclick=partial(task_post_upscale, scope="popup_image_disp", img_url=img_url)),
                    put_button("删除这张图",color="danger",onclick=partial(del_from_history,genid=genid))
                ]).style("margin: 3%; text-align: center")
                


            with use_scope("popup_image_info"):
                put_text("✅ "+ (text2image_data["prompt"] or "(无提示词)" ) )
                
                put_text("❌ "+ (text2image_data["negative_prompt"] or "(无反向提示词)" ) )
                put_row([ 
                    put_column(put_select("width_info",label="宽度",options=[text2image_data["width"]],value=text2image_data["width"])),
                    put_column(put_select("height_info",label="高度",options=[text2image_data["height"]],value=text2image_data["height"])),
                ])
                put_slider('guidance_scale_info',label="引导程度",min_value=0.0,max_value=30.0,value=text2image_data["guidance_scale"])
                put_row([ 
                    put_column(put_select("num_inference_steps_info",label="推理步骤",options=[text2image_data["num_inference_steps"]],value=text2image_data["num_inference_steps"])),
                    put_column(put_select("scheduler_name_info",label="采样器",options=[text2image_data["scheduler_name"]],value=text2image_data["scheduler_name"])),
                ]),
                put_select("model_name_info",label="模型",options=[MODEL_NAME_MAPPING_REVERSE[text2image_data['model_name']]],value=MODEL_NAME_MAPPING_REVERSE[text2image_data['model_name']]),
                if 'extra_model_name' not in text2image_data:
                    text2image_data['extra_model_name'] = "无"
                # put_select("extra_model_info",label="附加模型",options=[text2image_data['extra_model_name']],value=text2image_data['extra_model_name']),
                img_guide_opt = "启用" if text2image_data['type']=="image2image" else "未使用"
                put_row([
                    put_column(put_input("seed_info",label="随机种子",value=text2image_data["seed"])),
                    put_column(put_select("imgguide_info",label="图像引导",options=["启用","未使用"],value=img_guide_opt))
                ])
                if "hiresfix" in text2image_data:
                    hiresfix = text2image_data['hiresfix']
                else:
                    hiresfix = "Off" 
                put_select("hiresfix_info",label="高清修复",value=hiresfix,options=[hiresfix])

  



def fill_prompt_template(template_key):
    if template_key=="请选择模版...":
        return 
    else:
        fill_prompt, fill_neg_prompt = prompt_template[template_key]
        if fill_prompt is not None:
            pin['prompt'] = fill_prompt
        if fill_neg_prompt is not None:
            pin['negative_prompt'] = fill_neg_prompt

def del_from_history(genid):
    session.local.rclient.del_history(session.local.client_id,genid)
    load_history()
    close_popup()

@use_scope('history_images',clear=True)
def load_history():
    session.local.history_image_cnt = 0
    for img,genid in session.local.rclient.get_history(session.local.client_id, limit=session.local.max_history_bonus):
        if "storage." in img:
            img_preview = img 
            img_full = img 
        else:
            img_preview = img + "/med" if len(img)>10 else img 
            img_full = img 
        put_image(img_preview).onclick(partial(show_image_information_window,img_url=img_full, genid=genid)) 
        session.local.history_image_cnt += 1

def change_prompt_word_sheet(val):
    model_select = pin['model_name']
    extra_model_select = pin['extra_model']
    pin['prompt'] = EXTRA_MODEL_STRING[extra_model_select] +" "+pin['prompt']
    with use_scope("word_sheet",clear=True):
        content = []
        if model_select in SPECIAL_WORD:
            for text in SPECIAL_WORD[model_select]:
                content.append(put_markdown(text))
        content.append(put_markdown("----"))
        if extra_model_select in SPECIAL_WORD:
            for text in SPECIAL_WORD[extra_model_select]:
                content.append(put_markdown(text))
        put_collapse("特殊提示词表",content,open=True)
    pin['extra_model'] = "使用附加模型"



def popup_img_upload():
    info = input_group('添加引导图', [
        file_upload("",name="file",accept=[".jpg",".jpeg",".png",".webp"],placeholder="请选择图像文件",max_size="2M"),
        actions('', [
                {'label': '上传', 'type':'submit','value':'submit'},
                {'label': '重选', 'type': 'reset', 'color': 'warning'},
                {'label': '取消', 'type': 'cancel', 'color': 'danger'},
                ], name='actions'),
            ]
    )
    
    if info is not None:
        f = info["file"]
        filename_ext = os.path.splitext(f['filename'])[1]
        toast(upload_img_submit,duration=1)
        temp_path = "tempfile-{}.{}".format(nanoid.generate(string.ascii_lowercase,4),filename_ext)
        temp_file = open(temp_path,"wb")
        temp_file.write(f['content'])
        temp_file.close()
        # upload_data = f['content']
        upload_url = upload_to_storage(temp_path)
        os.remove(temp_path)
        if upload_url=="":
            toast(upload_img_fail,color="error",duration=3)
            return
        session.run_js(f"$('#img2img-img').attr('src','{upload_url}')")
        pin["img2img-url"] = upload_url

def show_img2img_options(val):
    # print(val,pin["enable_img2img"])
    if len(val)>0:
        # show 
        with use_scope("img2img-options",clear=True):
            put_row([
                put_column_autosize([
                    put_html(
                        f'<img style="height:200px;align-self: center;" id="img2img-img" src="{upload_img_placeholder}" />'
                    ).onclick(popup_img_upload),
                    put_input("img2img-url",placeholder="输入图像链接或上传图像")
                    
                    ]
                ),
                None,
                put_column([
                    put_select("i2i-preprocess",
                        label="预处理方式",
                        options=
                            ["原图",
                             "边缘提取(Canny)",
                             "边缘提取(HED)",
                             "线段提取",
                             "草图提取",
                             "人体姿态估计",
                             "语义分割",
                             "深度估计",
                             "法线贴图估计"
                             
                             ]),
                    put_select("i2i-model",label="引导模型",
                        options=
                            ["原模型",
                             "ControlNet-Canny",
                             "ControlNet-HED",
                             "ControlNet-线段",
                             "ControlNet-草图",
                             "ControlNet-人体姿态",
                             "ControlNet-语义分割",
                             "ControlNet-深度图",
                             "ControlNet-法线贴图"
                             ]),
                    put_input("i2i-strength",label="图像引导力度",value="0.5",help_text="范围0-1,越大越像引导图")
               ])
            ],size="1fr 10px 1fr")

    else:
        clear("img2img-options")

def set_prompt_pin_and_closepopup(val):
    pin["prompt"]=val
    close_popup()

def set_gpt_output():
    with use_scope("gpt_output",clear=True):
        session.run_js('$(".modal-dialog .btn").prop("disabled",true);')
        with put_loading():
            eng,cn,content = gpt_image_describe(pin['gpt_input'])
        session.run_js('$(".modal-dialog .btn").prop("disabled",false);')
        if eng=="Error":
            put_markdown(content)
        else:
            put_markdown(eng)
            put_markdown(cn)
            put_row(
                [
                    put_button("填入提示词(英文)",color="info",onclick=partial(set_prompt_pin_and_closepopup,val=eng)),
                    put_button("填入提示词(中文)",color="info",onclick=partial(set_prompt_pin_and_closepopup,val=cn))
                ]
            ).style("text-align:center")

def show_chatgpt_window():        
    with popup("帮我写(ChatGPT版)"):
        put_column([
            put_input("gpt_input",placeholder="例如：月亮上的树",help_text="简单描述您想生成的图像中的内容"),
            None,
            put_button("生成图像描述",color="info",onclick=set_gpt_output)
        ]).style("text-align:center")
        put_scope("gpt_output").style("text-align:center")


@config(theme="minty", css_style=css, title='云景AI绘图平台',description="AI画图工具，输入文本生成图像，二次元、写实、人物、风景、设计素材，支持中文，图像库分享")
def page_main():
    session.set_env(title='云景 · 绘图', output_max_width='90%')
    session.local.rclient: RClient = RClient()

    # 检查有没有登陆
    username = get_username()
    if username:
        session.local.username = username
        session.local.client_id = session.local.rclient.get_userid(username)
    else:
    # 检查本地有没有cookie client id，如果没有，让服务器赋予一个。
        if get_cookie("client_id") is None or not get_cookie("client_id").startswith("@"):
            new_client_id = session.local.rclient.get_new_client_id()
            set_cookie("client_id", new_client_id)
        session.local.client_id = get_cookie("client_id")
        toast("请先登录，正在跳转到“账户”页面 ...")
        time.sleep(1.5)
        session.run_js(f'window.open("/account");')
        
    # 设置footer
    sharerate,num_gen,num_pub = session.local.rclient.get_sharerate(session.local.client_id)
    footer_html = "您好，{}！<br>当前分享值{:.2f}%，生成数{}，分享数{}。".format(username,sharerate,num_gen,num_pub)
    session.run_js(f'$("footer").html("{footer_html}")')

    session.local.last_task_time = time.time() - 3
    
    if not session.local.client_id.startswith("@"):
        config = session.local.rclient.get_user_config(session.local.client_id)
        if "hisnum" in config:
            session.local.max_history_bonus = config['hisnum']
        else:
            session.local.max_history_bonus = 200
    else:
        session.local.max_history_bonus = 0
    put_html(header_html_main)

    put_column_autosize(
        [
            put_scope('input'), 
            put_markdown("----"),
            put_scope('history'), 
            put_markdown("----"),
            put_scope('images').style("text-align: center"),
        ]
    )
    

    with use_scope('input'):
        put_select("model_name",label="模型",options=MODELS,value=MODELS[0])
        pin_on_change("model_name",onchange=change_prompt_word_sheet)
        put_select("extra_model",label="附加模型",options=EXTRA_MODEL_LIST,value="使用附加模型")
        pin_on_change("extra_model",onchange=change_prompt_word_sheet)

        prompt_templates = list(prompt_template.keys())
        put_scope("word_sheet")


        put_select("prompt_template",label="提示词模板",options=prompt_templates,value="请选择模版..."),
        pin_on_change("prompt_template",onchange=fill_prompt_template)
 
        
        put_textarea('prompt',label="提示词",
                placeholder='例如：A car on the road, masterpiece, 8k wallpaper',
                rows=2,
            )
        put_row_autosize([
            put_button("帮我写",color="info",onclick=task_post_enhance_prompt),
            put_button("帮我写(ChatGPT版)",color="info",onclick=show_chatgpt_window),
        ])
        
        put_textarea('negative_prompt',label="反向提示词", placeholder="例如：NSFW, bad quality", rows=2)
        
        put_checkbox("enable_img2img",options=["开启图片引导模式"])
        pin_on_change("enable_img2img",onchange=show_img2img_options)
        put_scope("img2img-options")

        put_row([ 
            put_column(put_select("width",label="宽度",options=[str(64*i) for i in range(4,21,2)],value=str(512))),
            put_column(put_select("height",label="高度",options=[str(64*i) for i in range(4,21,2)],value=str(512))),

        ])
        put_row([            
            put_column(put_select("num_inference_steps",label="推理步骤",options=["20","25","30","35","40"],value="20")),
            put_column(put_select("scheduler_name",label="采样器",options=SCHEDULERS,value="Euler_A")),
        ])
        put_row([ 
            put_input("guidance_scale",label="引导程度",value="7.0"),
            put_input("seed",label="随机种子",value="-1"),
            put_select("hiresfix",label="高清修复",value="Off",options=["Off","On"])
        ])

        put_scope("generate_button",put_button(' - 开始绘制 -  ',onclick=partial(task_post_image_gen,callback=show_image_information_window))).style("text-align: center")
    

        

        #.style("position: relative;top: 50%;transform: translateY(-30%);")s
    with use_scope('history'):
        put_collapse(f"历史记录(保留{session.local.max_history_bonus}张)", [

            put_scrollable(put_scope('history_images'), height=0, keep_bottom=True, border=False)],
        open=True)
    
    load_history()
        
    param_gen_id = get_query("gen")
    if param_gen_id is not None:
        set_generation_params(param_gen_id)

