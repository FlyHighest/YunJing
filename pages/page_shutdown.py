from pywebio import session, config
from pywebio.output import put_html,put_markdown,use_scope,put_scope,put_button


from data import RClient

from utils.constants import css,header_html_index


@config(theme="minty", css_style=css, title='云景AI绘图平台',description="AI画图工具，输入文本生成图像，二次元、写实、人物、风景、设计素材，支持中文，图像库分享")
def page_shutdown():
    session.set_env(title='云景 · 首页', output_max_width='80%')
    session.local.rclient: RClient = RClient()
    put_markdown("""

------

## 公告

网站数据备份中，预计将在3月5日16:00开放。

------
如果您有疑问或者建议，欢迎加入交流群(QQ): 557228477

您也可以在[爱发电](https://afdian.net/a/terryzhang)赞助我，帮助云景扩充GPU资源。

    """)
