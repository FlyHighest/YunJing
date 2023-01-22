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
      </nav>
    </div>
  </header>
<hr />
"""