from pywebio import session, config
from pywebio.output import put_html,put_markdown,use_scope,put_scope,put_button


from data import RClient

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

@config(theme="minty", css_style=css, title='云景AI绘图平台',description="AI画图工具，输入文本生成图像，二次元、写实、人物、风景、设计素材，支持中文，图像库分享")
def page_index():
    session.set_env(title='云景 · 首页', output_max_width='80%')
    session.local.rclient: RClient = RClient()

    put_html(header_html_index)
    put_markdown("""

------
[云景 · 绘图](/main)：在这里创作您的作品，用一组文本描述绘制画面。

------ 

[云景 · 画廊](/gallery)：在这里分享您的创作参数，并参考别人的作品，也许其他人的经验能为您提供良好的开端。

您可以将您认为优秀的、或者对他人有帮助的创作成果分享到云景画廊，这完全是自愿的，您未发布的创作参数将被严格保密。

**请勿公开发布不适合工作场合观看的内容**。

------

**服务器状态**

    """)
    put_button("刷新",onclick=show_server_status)
    put_scope("current_server_status")
    show_server_status()
    put_markdown("""
------

**更新日志**

v1.14 (2023-05-04)
 - 修复了内容审核模型过于严格的问题

<details>
<summary>历史更新记录 展开查看</summary>

v1.13 (2023-04-08)
 - 添加了新的模型、新的附加模型、新的反向提示词（帮助界面查看详情）
 - 现在LORA模型的使用方式更改为写在提示词里，可以同时使用多个附加模型
 - 可选高清修复功能，提升高分辨率图像的效果
 - 最大可选分辨率从1024提高到1280

v1.12 (2023-04-02)
 - 现在用户可以取消分享到画廊的图像
 - 修复了复用参数生成的图像未被记录到历史记录表的Bug
 - 更换了网站Logo

v1.11 (2023-03-14)
 - 添加6个新模型
 
v1.10 (2023-03-04)
 - 添加新的“帮我写”功能，给定一些关键词，让ChatGPT帮忙拓展成完整、细致的图像描述。

v1.9 (2023-02-26)
 - 模型变化：去掉了融合模型国风2+3；新增模型国风2、云景Anime-v1；anythingv3升级到3.2
 - 功能更新：添加图生图功能，可使用**原版img2img**或**controlnet**的附加能力
 - 账户页面可以调整一些用户配置

v1.8 (2023-02-19)
 - 画廊里可以搜索图片了，支持按提示词、模型和用户名进行搜索

v1.7 (2023-02-18)
 - 中文支持更新：支持中英文混用，后台会自动翻译中文，保留原有英文
 - 帮我写功能更新：支持输入中文后续写（会全部转变为英文）
 - 新增模型ChilloutMix和AsiaFacemix
 - 新增附加模型功能
 - 新增模型特有关键词表，选择模型后会展示特有的关键词

v1.6 (2023-02-15)
 - 绘图页面更新：对移动端更加友好；历史记录可折叠。
 - 新添加了模型“国风2+3”，融合了国风2和国风3
 - 新添加了模型Myne Factory Base

v1.5 (2023-02-11):
 - 历史记录：现在可以将图像移出历史记录
 - 添加了新模型GuoFeng3和对应的提示词模板

v1.4 (2023-02-05):
 - 账户系统：计算用户分享值，以此决定用户的生成速度
 - 提示词模板功能

v1.3 (2023-01-25):
 - 画廊更新：登录用户可以给图像点赞
 - 更完善的注册系统

v1.2 (2023-01-23): 
 - 现在可以创建账户，登录后发布在画廊中的作品会展示用户名。
 - 在帮助界面，可以提交图像人工审核。

v1.1 (2023-01-22): 
 - 提示词支持中文。
 - 增加帮助界面，有模型介绍、使用建议等，推荐阅读。


</details>

------
如果您有疑问或者建议，欢迎加入交流群(QQ): 557228477

您也可以在[爱发电](https://afdian.net/a/terryzhang)赞助我，帮助云景扩充GPU资源。

    """)
