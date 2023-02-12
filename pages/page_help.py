from pywebio import config, session
from pywebio.output import put_html,put_markdown,put_button,put_row,toast
from pywebio.pin import put_input,pin

from utils.constants import header_html_help,css
from data import RClient
def submit_img_to_check():
    try:
        session.local.rclient.add_check_image(pin['img_url'])
        toast("提交成功")
        pin['img_url'] = ""
    except:
        toast("未知错误，请联系管理员")

@config(theme="minty", css_style=css, title='云景AI绘图平台',description="AI画图工具，输入文本生成图像，二次元、写实、人物、风景、设计素材，支持中文，图像库分享")
def page_help():
    session.set_env(title='云景 · 帮助', output_max_width='80%')
    session.local.rclient: RClient = RClient()

    put_html(header_html_help)
    put_markdown("""
## 一、云景·绘图

当前支持以下功能：
- 文本生成图像
- 图像超分辨率
- 提示词自动扩写
- 提示词模板

### 1. 文本生成图像

#### (1) 参数说明

在绘图页面，左侧是文本生成图像的参数输入区，中间部分是图像预览区，右侧是最近生成的图像。

文本生成图像的参数说明：

| 输入参数   | 说明                                                                                                                                                            |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 提示词     | 对图像内容或特性的描述文本                                                                                                                                    |
| 反向提示词 | 对不希望在图像中出现的内容或特性的描述文本                                                                                                                   |
| 宽度、高度 | 生成图像的尺寸                                                                                                                                                  |
| 引导程度   | 生成图像时对提示词的重视度，更大的值会更严格绘制提示词的内容，但会限制模型发挥                                                                                  |
| 推理步骤   | 一般越大图像质量越高，但生成速度更慢                                                                                                                            |
| 采样器     | [这里](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features#sampling-method-selection)有一些不同采样器效果对比，如果生成效果不好可尝试换采样器 |
| 模型       | 详见下面的"模型介绍"章节                                                                                                                                        |
| 随机种子   | 可以手动指定，为空或-1时将由系统随机生成，保证生成结果可以复现                                                                                                  |

#### (2) 提示词说明

**a. 支持webui特性（仅英语）**
支持webui的多种语法特性，包括Attention/emphasis、Prompt editing等。

Attention/emphasis:

使用`()` 或`{}`加大括号内提示词的权重，使用`[]`减少权重。一层`()`或`{}`增加10%，可嵌套多层。一层`[]`减少10%。

Prompt Editing:

在图像生成步骤中间更换关键词。

第一种语法是 `[关键词1:关键词2:更换关键词的步骤数]`。

最开始按关键词1进行生成，在指定步骤数之后按关键词2进行生成。可以创作出一些风格融合的效果。比如`a [fantasy:cyberpunk:15] landscape`，推理步骤设为30，能呈现出奇幻和赛博风融合。

第二种语法是 `[关键词1|关键词2]`。

两个关键词交替使用，每个采样步骤都更换一次。比如`a picture of [cat|bird]`，可画出类似猫头鹰的猫、鸟融合兽。

**b. 支持中文提示词和反向提示词**

云景后台接入了[机器翻译模型](https://huggingface.co/Helsinki-NLP/opus-mt-zh-en)，输入汉语文本会自动翻译为英文后再进行图像生成。
翻译后会去掉括号、改变标点符号等，因此使用汉语时无法使用webui的特性。


#### (3) 模型介绍

当前后台集成了7个模型，可在“模型”选项自由切换。

- [Stable-Diffusion-v1.5](https://huggingface.co/runwayml/stable-diffusion-v1-5): 原版的stable diffusion 1.5，许多微调模型的基础，比较全能，写实、动漫，人物、风景，包括背景图、头像风格都都能生成，但非常依赖提示词。
- [Protogen-x5.8](https://huggingface.co/darkstorm2150/Protogen_x5.8_Official_Release): AI模型分享网站civitai上最火的模型之一，比较擅长画人物，有时候提示词没有人物相关的也会画个人出来。
- [OpenJourney](https://huggingface.co/prompthero/openjourney): prompthero基于著名的midjourney生成的图像训练stable diffusion获得的模型。系统会自动在提示词最前面加上'mdjrny-v4 style'。
- [ACertainThing](https://huggingface.co/JosephusCheung/ACertainThing): Joseph Cheung训练的二次元风格的图像生成模型，同NovelAI一样，支持danbooru标签。
- [Anything-v3](https://huggingface.co/cag/anything-v3-1): 另一个大家喜闻乐见的二次元风格图像生成模型，同NovelAI一样，支持danbooru标签。
- [RealisticVision-v1.3](https://civitai.com/models/4201/realistic-vision-v13): civitai上备受欢迎的模型，擅长绘制写实照片类图像。RealisticVision的模板是模型作者推荐的，建议配合模板使用。
- [国风GuoFeng-v3](https://huggingface.co/xiaolxl/GuoFeng3): B站up[@小李xiaolxl](https://space.bilibili.com/34590220)发布的中国华丽古风风格模型，也可以说是一个古风游戏角色模型，具有2.5D的质感。

### 2. 图像超分辨率

在点击“开始生成”按钮后，稍等片刻，图像预览区会显示图像，同时下方出现“获取高清图”按钮，点击按钮即可获得高清图下载链接。

此外，在历史图像记录区或者画廊中，点击缩略图会弹出详细参数框，详细参数预览框中也有获取高清图按钮。

服务器使用[RealESRGAN](https://github.com/xinntao/Real-ESRGAN)模型进行图像超分。

### 3. 提示词自动扩写

在提示词输入框右侧有“帮我写”按钮，点击后将对当前输入的内容自动扩写。扩写模型使用[MagicPrompt](https://huggingface.co/Gustavosta/MagicPrompt-Stable-Diffusion)，主要是为stable diffusion准备的，protogen和openjourney也可以参考。

当前**仅支持英文**提示词扩写。虽然会拓展出来一些提高质量、风格或者艺术家的词汇，但仍无法百分之百保证生成图像的质量，还需手动调整，仅供参考。

### 4. 提示词模板

这个功能给用户提供了更加简便的提示词书写流程。这些模板能够提高出图良品率，提升图像质量，增加图像细节。

当前所使用模板来源：
- 网站[NovelAI tag生成器](https://wolfchen.top/tag/)
- github项目[stable-diffusion-prompt-templates](https://github.com/Dalabad/stable-diffusion-prompt-templates)

## 二、云景·画廊

生成图像后，点击发布按钮，即可将图像分享到画廊，与其他用户分享您的成果和创作参数。您也可以在画廊中点击您喜欢的图像，打开参数详情预览框，点击复刻按钮，快速填写该图的生成参数，在此基础上根据您的需要进行调整。

目前画廊随机展示图像，按关键词搜索图像的功能正在开发中，敬请期待。

欢迎大家多贡献好图~

## 三、常见问题

### 1. 常见错误提示和说明

- "**未知错误**"/"**模型服务错误，请稍后再试**": GPU服务器异常，如果一直出现请联系我解决(QQ 369945942, email tyz.xyz@qq.com)
- "**检测到不适宜内容，请尝试更换提示词或随机种子**": 不适宜工作场所观看的内容禁止发布在画廊
- "**当前排队过长，请稍后再试**": 在排队的任务过多，可以在首页查看当前排队任务数
- "**生成参数已过期**": 未发布在画廊中的图像，生成参数仅保留7天
- "**操作频率过于频繁，请三秒后再试**": 提示词扩展、超分、图像生成都会使用GPU资源，公益项目预算有限，因此对频率进行了限制
- "**与服务器连接已断开，请刷新页面重新操作**"/"**Disconnected from the server,...**": 长时间不操作自动断开，刷新网页即可重新连接

### 2. 我的图像中不含🔞内容，为何提示“检测到不适宜内容”？

为了平台的健康发展，内容安全检测器有时会表现的过于严格。内容安全检测器判断为不适宜工作场所观看的图像将不被网站保存、不能发布至画廊。

### 3. 其他

如有其他问题或者建议，可以联系我或加入我们的交流群(QQ群: 557228477)。
""")

