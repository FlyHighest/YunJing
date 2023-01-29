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

网站维护中，预计将在1月30日10:00开放。

加入交流群，获得最新消息(QQ群 557228477)。

-----

**简介**

☁️云景☁️是一个公益项目，目的是给更多人提供AI绘图的免费工具。

您可以将您认为优秀的、或者对他人有帮助的创作成果分享到云景画廊，这完全是自愿的，您未发布的创作参数将被严格保密。

1. 免费的在线生成服务，无需付费、无广告烦扰。
2. 多种最新模型一键切换。
3. 在画廊，与其他人分享你的创意或者复刻他人的创意(请勿公开发布不适合工作场合观看的内容)。

------

**更新日志**

v1.3 (2023-01-25):
 - 画廊更新：登录用户可以给图像点赞
 - 更完善的注册系统

v1.2 (2023-01-23): 
 - 现在可以创建账户，登录后发布在画廊中的作品会展示用户名。
 - 在帮助界面，可以提交图像人工审核。

v1.1 (2023-01-22): 
 - 提示词支持中文。
 - 增加帮助界面，有模型介绍、使用建议等，推荐阅读。

------
如果您有疑问或者建议，欢迎加入交流群(QQ): 557228477

您也可以在[爱发电](https://afdian.net/a/terryzhang)赞助我，帮助云景扩充GPU资源。

    """)
