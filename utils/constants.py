MODELS = [
    "Stable-Diffusion-v1.5",
    "Protogen-x5.8",
    "OpenJourney",
    "ACertainThing",
    "Anything-v3"
]

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
nsfw_warn_text = "检测到不适宜内容，请尝试更换提示词或随机种子"
queue_too_long_text = "当前排队过长，请稍后再试"
unknown_error_text = "未知错误"
generation_outdated_error_text = "生成参数已过期"
publish_success_text = "发布成功，通过安全检测后将显示在画廊"
publish_fail_text = "发布失败，请稍后再试"
too_frequent_error_text = "操作频率过于频繁，请三秒后再试"
css = """
#pywebio-scope-image_flow{
    text-align:center;
}
#pywebio-scope-image_flow img{
    width: 19%;
    margin:0.5%;
    float:left;
    border-radius: 5% ;
    transition: all 0.2s;
}
#pywebio-scope-image_flow img:hover {
    transform: scale(1.05);
}

#pywebio-scope-history_images img {
    max-width: 45%;
    margin: 2%;
    border-radius: 6% ;
    transition: all 0.2s;
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

thumbup_false="""<svg t="1674519918190" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7654" width="200" height="200"><path d="M896.537737 872.991991c-90.117275 98.293062-222.585219 150.43597-383.111736 150.941794l-2.329113 0c-309.520102 0-510.060666-200.378099-510.957633-510.41563C-0.703785 202.514712 199.65247 0.986392 510.570586 0.066215l2.285425 0c309.550138 0 510.158281 200.38356 511.004734 510.434743C1024.268271 656.398162 980.213091 781.749752 896.537737 872.991991zM369.797157 440.889704l-23.977164 0c-33.877258 0-61.3399 27.296081-61.3399 61.404067l0 161.215284c0 34.118907 27.462642 61.776097 61.3399 61.776097l23.977164-0.046418L369.797157 440.889704zM753.732819 475.095987c0-34.598109-26.060532-62.643712-58.203243-62.643712l-126.654036 0 0-60.307773c0-37.594145-10.930174-67.671919-49.392617-67.671919-42.874241 0-60.399927 43.223745-64.367337 71.095961 0 0-1.063528 47.667626-30.155593 72.928806 0 0-4.857552-3.074538-12.503622 5.888314l0 290.769106 7.311584-0.014335c10.033206 8.843392 22.689053 14.365137 36.669873 14.365137l239.091748 0c32.142028 0 58.203243-28.045602 58.203243-62.651903L753.732819 475.095987 753.732819 475.095987z" p-id="7655" fill="#515151"></path></svg>"""
thumbup_true="""<svg t="1674519918190" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7654" width="200" height="200"><path d="M896.537737 872.991991c-90.117275 98.293062-222.585219 150.43597-383.111736 150.941794l-2.329113 0c-309.520102 0-510.060666-200.378099-510.957633-510.41563C-0.703785 202.514712 199.65247 0.986392 510.570586 0.066215l2.285425 0c309.550138 0 510.158281 200.38356 511.004734 510.434743C1024.268271 656.398162 980.213091 781.749752 896.537737 872.991991zM369.797157 440.889704l-23.977164 0c-33.877258 0-61.3399 27.296081-61.3399 61.404067l0 161.215284c0 34.118907 27.462642 61.776097 61.3399 61.776097l23.977164-0.046418L369.797157 440.889704zM753.732819 475.095987c0-34.598109-26.060532-62.643712-58.203243-62.643712l-126.654036 0 0-60.307773c0-37.594145-10.930174-67.671919-49.392617-67.671919-42.874241 0-60.399927 43.223745-64.367337 71.095961 0 0-1.063528 47.667626-30.155593 72.928806 0 0-4.857552-3.074538-12.503622 5.888314l0 290.769106 7.311584-0.014335c10.033206 8.843392 22.689053 14.365137 36.669873 14.365137l239.091748 0c32.142028 0 58.203243-28.045602 58.203243-62.651903L753.732819 475.095987 753.732819 475.095987z" p-id="7655" fill="#d81e06"></path></svg>"""
