MODELS = [
    "Taiyi-Chinese-v0.1",
    "Taiyi-Chinese-Anime-v0.1",
    "Stable-Diffusion-2.1",
    "Protogen-x5.8",
    "Anything-v4.5"
]

SCHEDULERS = [
    "PNDM", 
    "LMS",
    "DDIM",
    "Euler",
    "Euler_A",
    "DPMSolver",
    "Heun",
    "KDPM2_A"
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
publish_success_text = "发布成功"
publish_fail_text = "发布失败，请稍后再试"

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
"""
