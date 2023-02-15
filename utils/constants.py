MODELS = [
    "Stable-Diffusion-v1.5",
    "Protogen-x5.8",
    "OpenJourney",
    "RealisticVision-V1.3",
    "ACertainThing",
    "Anything-v3",
    "国风GuoFeng-v3",
    "国风GuoFeng-v2+v3",
    "Counterfeit-V2.5",
    "MyneFactoryBase-v1.0"
]

MODEL_NAME_MAPPING = {
    "Stable-Diffusion-v1.5":"Stable-Diffusion-v1.5",
    "Protogen-x5.8":"Protogen-x5.8",
    "OpenJourney":"OpenJourney",
    "RealisticVision-V1.3":"RealisticVision-V1.3",
    "ACertainThing":"ACertainThing",
    "Anything-v3":"Anything-v3.2",
    "国风GuoFeng-v3":"GuoFeng3_Fix",
    "国风GuoFeng-v2+v3":"GF2+3",
    "Counterfeit-V2.5":"Counterfeit-V2.5",
    "MyneFactoryBase-v1.0":"MyneFactoryBase v1.0"
}

MODEL_NAME_MAPPING_REVERSE = {v:k for k,v in MODEL_NAME_MAPPING.items()}
SCHEDULERS = [
    "Euler a",
    "Euler",
    "LMS",
    "Heun",
    "DPM2",
    "DPM2 a",
    "DPM++ 2S a",
    "DPM++ 2M",
    "DPM++ SDE",
    "DPM fast",
    "DPM adaptive",
    "LMS Karras",
    "DPM2 Karras",
    "DPM2 a Karras",
    "DPM++ 2S a Karras",
    "DPM++ 2M Karras",
    "DPM++ SDE Karras",
    "DDIM",
    "PLMS"
]

MAX_HISTORY = 10
MAX_QUEUE = 10
IMAGE_NUM_PER_LOAD = 20
IMAGE_NUM_PER_ROW = 5
image_gen_text = "正在生成，请稍后"
server_error_text = "模型服务错误，请稍后再试"
nsfw_warn_text_publish = "检测到不适宜内容，人工审核后发布"
nsfw_warn_text_gen = "图像可能含有不适宜工作场所观看的内容，请更换提示词或随机种子"
queue_too_long_text = "当前排队过长，请稍后再试"
unknown_error_text = "未知错误"
generation_outdated_error_text = "生成参数已过期"
publish_success_text = "发布成功，稍后将显示在画廊"
publish_fail_text = "发布失败，请稍后再试"
too_frequent_error_text = "操作频率过于频繁，请稍后再试"
not_login_error_text = "请先在“账户”页面登录或注册"
share_too_low="您的分享值过低，生成频率被限制，本次任务提交失败"

css = """
#pywebio-scope-image_flow{
    text-align:center;
}
#pywebio-scope-image_flow img{
    margin: 2%;
    border-radius: 0.6vw ;
    transition: all 0.2s;
}
#pywebio-scope-image_flow img:hover {
    transform: scale(1.05);
}

.thumbupicon {
      transition: all 0.2s;
      height:25px;
      width:25px;
      margin-bottom:10px;
}

.thumbupicon:hover {
    transform: scale(1.1);
}


#pywebio-scope-history_images img {
    max-height: 44%;
    margin: 1%;
    border-radius: 0.6vw ;
    transition: all 0.2s;
}


#pywebio-scope-history_images img:hover {

    transform: scale(1.05);
}
#pywebio-scope-history_images {
  height:200px;
    overflow-x: scroll;
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
/*
 * Header
 */
.masthead {
  margin-bottom: 2rem;
}

.masthead-brand {
  margin-bottom: 0;
}

.nav-masthead .nav-link {
  padding: .25rem 0;
  font-weight: 700;
  color: rgba(0, 0, 0, .5);
  background-color: transparent;
  border-bottom: .25rem solid transparent;
}

.nav-masthead .nav-link:hover,
.nav-masthead .nav-link:focus {
  border-bottom-color: rgba(0, 0, 0, .25);
  text-decoration: none
}

.nav-masthead .nav-link + .nav-link {
  margin-left: 1rem;
}

.nav-masthead .active {
  color: #000;
  border-bottom-color: #000;
}
"""

header_html_index = """
<header class="masthead mb-auto">
    <div class="inner">
      <nav class="nav nav-masthead justify-content-center">
        <a class="nav-link active" href="/">首页</a>
        <a class="nav-link" href="/main">绘图</a>
        <a class="nav-link" href="/gallery">画廊</a>
        <a class="nav-link" href="/help">帮助</a>
        <a class="nav-link" href="/account">账户</a>

      </nav>
    </div>
  </header>

"""

header_html_main = """
<header class="masthead mb-auto">
    <div class="inner">
      <nav class="nav nav-masthead justify-content-center">
        <a class="nav-link" href="/">首页</a>
        <a class="nav-link active" href="/main">绘图</a>
        <a class="nav-link" href="/gallery">画廊</a>
        <a class="nav-link" href="/help">帮助</a>
        <a class="nav-link" href="/account">账户</a>

      </nav>
    </div>
  </header>
    <hr />
"""

header_html_gallery = """
<header class="masthead mb-auto">
    <div class="inner">
      <nav class="nav nav-masthead justify-content-center">
        <a class="nav-link" href="/">首页</a>
        <a class="nav-link" href="/main">绘图</a>
        <a class="nav-link active" href="/gallery">画廊</a>
         <a class="nav-link" href="/help">帮助</a>
        <a class="nav-link" href="/account">账户</a>

      </nav>
    </div>
  </header>
<hr />
"""

header_html_help = """
<header class="masthead mb-auto">
    <div class="inner">
      <nav class="nav nav-masthead justify-content-center">
        <a class="nav-link" href="/">首页</a>
        <a class="nav-link" href="/main">绘图</a>
        <a class="nav-link" href="/gallery">画廊</a>
        <a class="nav-link active" href="/help">帮助</a>
        <a class="nav-link" href="/account">账户</a>

      </nav>
    </div>
  </header>
<hr />
"""

header_html_account = """
<header class="masthead mb-auto">
    <div class="inner">
      <nav class="nav nav-masthead justify-content-center">
        <a class="nav-link" href="/">首页</a>
        <a class="nav-link" href="/main">绘图</a>
        <a class="nav-link" href="/gallery">画廊</a>
        <a class="nav-link" href="/help">帮助</a>
        <a class="nav-link active" href="/account">账户</a>
      </nav>
    </div>
  </header>
<hr />
"""

thumbup_false="""<svg t="1674519918190" class="thumbupicon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7654" width="200" height="200"><path d="M896.537737 872.991991c-90.117275 98.293062-222.585219 150.43597-383.111736 150.941794l-2.329113 0c-309.520102 0-510.060666-200.378099-510.957633-510.41563C-0.703785 202.514712 199.65247 0.986392 510.570586 0.066215l2.285425 0c309.550138 0 510.158281 200.38356 511.004734 510.434743C1024.268271 656.398162 980.213091 781.749752 896.537737 872.991991zM369.797157 440.889704l-23.977164 0c-33.877258 0-61.3399 27.296081-61.3399 61.404067l0 161.215284c0 34.118907 27.462642 61.776097 61.3399 61.776097l23.977164-0.046418L369.797157 440.889704zM753.732819 475.095987c0-34.598109-26.060532-62.643712-58.203243-62.643712l-126.654036 0 0-60.307773c0-37.594145-10.930174-67.671919-49.392617-67.671919-42.874241 0-60.399927 43.223745-64.367337 71.095961 0 0-1.063528 47.667626-30.155593 72.928806 0 0-4.857552-3.074538-12.503622 5.888314l0 290.769106 7.311584-0.014335c10.033206 8.843392 22.689053 14.365137 36.669873 14.365137l239.091748 0c32.142028 0 58.203243-28.045602 58.203243-62.651903L753.732819 475.095987 753.732819 475.095987z" p-id="7655" fill="#515151"></path></svg>"""
thumbup_true="""<svg t="1674519918190" class="thumbupicon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7654" width="200" height="200"><path d="M896.537737 872.991991c-90.117275 98.293062-222.585219 150.43597-383.111736 150.941794l-2.329113 0c-309.520102 0-510.060666-200.378099-510.957633-510.41563C-0.703785 202.514712 199.65247 0.986392 510.570586 0.066215l2.285425 0c309.550138 0 510.158281 200.38356 511.004734 510.434743C1024.268271 656.398162 980.213091 781.749752 896.537737 872.991991zM369.797157 440.889704l-23.977164 0c-33.877258 0-61.3399 27.296081-61.3399 61.404067l0 161.215284c0 34.118907 27.462642 61.776097 61.3399 61.776097l23.977164-0.046418L369.797157 440.889704zM753.732819 475.095987c0-34.598109-26.060532-62.643712-58.203243-62.643712l-126.654036 0 0-60.307773c0-37.594145-10.930174-67.671919-49.392617-67.671919-42.874241 0-60.399927 43.223745-64.367337 71.095961 0 0-1.063528 47.667626-30.155593 72.928806 0 0-4.857552-3.074538-12.503622 5.888314l0 290.769106 7.311584-0.014335c10.033206 8.843392 22.689053 14.365137 36.669873 14.365137l239.091748 0c32.142028 0 58.203243-28.045602 58.203243-62.651903L753.732819 475.095987 753.732819 475.095987z" p-id="7655" fill="#d81e06"></path></svg>"""

prompt_template = {
  "请选择模版...":None,
  "清空(提示词+反向提示词)":("",""),
  "GuoFeng3模板":(
    "best quality, masterpiece, highres, 1girl,china dress,Beautiful face",
    "(((simple background))),monochrome ,lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, lowres, bad anatomy, bad hands, text, error, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, ugly,pregnant,vore,duplicate,morbid,mut ilated,tran nsexual, hermaphrodite,long neck,mutated hands,poorly drawn hands,poorly drawn face,mutation,deformed,blurry,bad anatomy,bad proportions,malformed limbs,extra limbs,cloned face,disfigured,gross proportions, (((missing arms))),(((missing legs))), (((extra arms))),(((extra legs))),pubic hair, plump,bad legs,error legs,username,blurry,bad feet"),
  "RealisticVision模板":
    ("RAW photo, ?, (high detailed skin:1.2), 8k uhd, dslr, soft lighting, high quality, film grain, Fujifilm XT3",
     "(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck")
     ,
  "二次元模型通用模板":
    ("masterpiece, best quality, ",
     "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry")
    ,
  "二次元模型更高质量":
    ("masterpiece,best quality,official art,extremely detailed CG unity 8k wallpaper, ",
     "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry")
    ,
  "SD动物模板":
    ("?, wildlife photography, photograph, high quality, wildlife, f 1.8, soft focus, 8k, national geographic, award - winning photograph by nick nichols",
     ""),
  "SD建筑(室内)":
    ("?, by James McDonald and Joarc Architects, home, interior, octane render, deviantart, cinematic, key art, hyperrealism, sun light, sunrays, canon eos c 300, ƒ 1.8, 35 mm, 8k, medium - format print	",
    ""),
  "SD建筑(室外)":
    ("? , shot 35 mm, realism, octane render, 8k, trending on artstation, 35 mm camera, unreal engine, hyper detailed, photo - realistic maximum detail, volumetric light, realistic matte painting, hyper photorealistic, trending on artstation, ultra - detailed, realistic	",
    ""),
  "SD卡通角色":
    ("? , anthro, very cute kid's film character, disney pixar zootopia character concept artwork, 3d concept, detailed fur, high detail iconic character for upcoming film, trending on artstation, character design, 3d artistic render, highly detailed, octane, blender, cartoon, shadows, lighting",
    ""),
  "SD概念艺术、设计":
    ("? , character sheet, concept design, contrast, style by kim jung gi, zabrocki, karlkka, jayison devadas, trending on artstation, 8k, ultra wide angle, pincushion lens effect",
    ""),
  "SD赛博朋克":
    ("? , cyberpunk, in heavy raining futuristic tokyo rooftop cyberpunk night, sci-fi, fantasy, intricate, very very beautiful, elegant, neon light, highly detailed, digital painting, artstation, concept art, soft light, hdri, smooth, sharp focus, illustration, art by tian zi and craig mullins and wlop and alphonse much	",
    ""),
  "SD数字艺术":
    ("? , ultra realistic, concept art, intricate details, highly detailed, photorealistic, octane render, 8k, unreal engine, sharp focus, volumetric lighting unreal engine. art by artgerm and alphonse mucha",
    ""),
  "SD数字艺术(场景)":
    ("?, epic concept art by barlowe wayne, ruan jia, light effect, volumetric light, 3d, ultra clear detailed, octane render, 8k, [颜色] colour scheme	",
        ""),
  "SD绘画":
    ("?, cute, funny, centered, award winning watercolor pen illustration, detailed, disney, isometric illustration, drawing, by Stephen Hillenburg, Matt Groening, Albert Uderzo",
          ""),
  "SD时尚模特":
    ("photograph of a Fashion model, ?, full body, highly detailed and intricate, golden ratio, vibrant colors, hyper maximalist, futuristic, city background, luxury, elite, cinematic, fashion, depth of field, colorful, glow, trending on artstation, ultra high detail, ultra realistic, cinematic lighting, focused, 8k,	",
    ""),
  "SD风景":
    ("? , realism, octane render, 8 k, exploration, cinematic, trending on artstation, 35 mm camera, unreal engine, hyper detailed, photo - realistic maximum detail, volumetric light, moody cinematic epic concept art, realistic matte painting, hyper photorealistic, epic, trending on artstation, movie concept art, cinematic composition, ultra - detailed, realistic	",
    ""),
  "SD特写":
    ("?, depth of field. bokeh. soft light. by Yasmin Albatoul, Harry Fayt. centered. extremely detailed. Nikon D850, (35mm|50mm|85mm). award winning photography.	",
    ""),
  "SD肖像":
    ("portrait photo of ?, photograph, highly detailed face, depth of field, moody light, golden hour, style by Dan Winters, Russell James, Steve McCurry, centered, extremely detailed, Nikon D850, award winning photography	",
    ""),
  "SD后末日艺术":
    ("? , fog, animals, birds, deer, bunny, postapocalyptic, overgrown with plant life and ivy, artgerm, yoshitaka amano, gothic interior, 8k, octane render, unreal engine	",
    ""), 
  "SD结构图/原理图":
    ("23rd century scientific schematics for ?, blueprint, hyperdetailed vector technical documents, callouts, legend, patent registry	",
    ""),
  "SD素描":
    ("?, sketch, drawing, detailed, pencil, black and white by Adonna Khare, Paul Cadden, Pierre-Yves Riveau	",
    ""),
  "SD太空":
    ("?, by Andrew McCarthy, Navaneeth Unnikrishnan, Manuel Dietrich, photo realistic, 8 k, cinematic lighting, hd, atmospheric, hyperdetailed, trending on artstation, deviantart, photography, glow effect	",
    ""), 
  "SD游戏图标素材":
    ("sprite of video games, ?, icons, 2d icons, rpg skills icons, world of warcraft, league of legends, ability icon, fantasy, potions, spells, objects, flowers, gems, swords, axe, hammer, fire, ice, arcane, shiny object, graphic design, high contrast, artstation",
    ""),
  "SD蒸汽朋克":
    ("? , steampunk cybernetic biomechanical, 3d model, very coherent symmetrical artwork, unreal engine realistic render, 8k, micro detail, intricate, elegant, highly detailed, centered, digital painting, artstation, smooth, sharp focus, illustration, artgerm, Caio Fantini, wlop",
    ""), 
  "SD车辆":
    ("photograph of ?, photorealistic, vivid, sharp focus, reflection, refraction, sunrays, very detailed, intricate, intense cinematic composition",
    ""),
}
