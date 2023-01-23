from pywebio import session, config
from pywebio.output import put_html,put_markdown,use_scope,put_scope,put_button


from utils import RClient

from utils.constants import css,header_html_index

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
    put_markdown("""

------
[云景 · 绘图](/main)：在这里创作您的作品，用一组文本描述绘制画面。

[云景 · 画廊](/gallery)：在这里分享您的创作参数，并参考别人的作品，也许其他人的经验能为您提供良好的开端。

-----

**简介**

☁️云景☁️是一个公益项目，目的是给更多人提供AI绘图的免费工具。

您可以将您认为优秀的、或者对他人有帮助的创作成果分享到云景画廊，这完全是自愿的，您未发布的创作参数将被严格保密。

1. 免费的在线生成服务，无需付费、无广告烦扰。
2. 多种最新模型一键切换。
3. 在画廊，与其他人分享你的创意或者复刻他人的创意(请勿公开发布不适合工作场合观看的内容)。

------

**服务器状态**

    """)
    put_button("刷新",onclick=show_server_status)
    put_scope("current_server_status")
    show_server_status()
    put_markdown("""
------

如果您有疑问或者建议，欢迎加入交流群(QQ): 557228477

您也可以在[爱发电](https://afdian.net/a/terryzhang)赞助我，帮助云景扩充GPU资源。

    """)
