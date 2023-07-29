from pywebio import config, session
from pywebio.output import put_html,put_markdown,put_button,put_row,toast
from pywebio.pin import put_input,pin

from utils.constants import header_html_help,css
from data import RClient


@config(theme="minty", css_style=css, title='云景AI绘图平台',description="AI画图工具，输入文本生成图像，二次元、写实、人物、风景、设计素材，支持中文，图像库分享")
def page_help():
    session.set_env(title='云景 · 帮助', output_max_width='80%')
    session.local.rclient: RClient = RClient()

    put_html(header_html_help)
    put_markdown("""
## 一、云景·绘图

当前支持以下功能：
- 文本生成图像
- 图像引导生成
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
| 附加模型   | 选择后在提示词中自动添加对应的附加模型调用命令     |
| 高清修复   | 在生成高分辨率(超过768)时开启高清修复，对一些不擅长生成高分辨率的模型来说提升效果显著 | 
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

云景后台接入了腾讯机器翻译API，输入汉语文本会自动翻译为英文后再进行图像生成。


在反向提示词中，除了一些常见的描述，还可以使用以下几种由低质量图像训练得到的负面词向量：

_easy_negative_, _bad_prompt_, _bad_prompt_version2_, _bad_hand_, _bad_artist_, _bad_artist_anime_, _ng_deepnegative_



#### (3) 模型介绍

当前后台集成多个模型，可在“模型”选项自由切换，选中模型后在模型信息页面可以查看信息。

附加模型：

- [LoRA-KoreanDollLikeness](https://civitai.com/models/7448/korean-doll-likeness): 擅长绘制韩国明星风格的人像。
- [LoRA-国风汉服少女](https://www.bilibili.com/read/cv21493779): B站up[@K43](https://space.bilibili.com/51049)制作的汉服少女模型。
- [LoRA-国风汉服少女仿明风格](https://www.bilibili.com/read/cv21681512): B站up[@K43](https://space.bilibili.com/51049)制作的汉服少女仿明风格模型。
- [LoRA-国风汉服少女仿宋风格](https://www.bilibili.com/read/cv21926093): B站up[@K43](https://space.bilibili.com/51049)制作的汉服少女仿宋风格模型。
- [LoRA-墨心 & 疏可走马](https://civitai.com/models/12597/moxin): simhuang制作的水墨风lora。
- [LoRA-线稿风格](https://civitai.com/models/16014/anime-lineart-manga-like-style): 配合提示词lineart, monochrome，绘制线稿、漫画风图像。
- [LoRA-立绘风格](https://civitai.com/models/13090/gacha-splash-lora): 立绘风格Lora，效果很酷。 
- [LoRA-细节调整](https://civitai.com/models/58390?modelVersionId=62833)
- [LoRA-CLAMP风格](https://civitai.com/models/76069/clamp-style-lora)
- [LoRA-Hamao风格](https://civitai.com/models/76790/hamao-style-lora)
- [LoRA-LAM风格](https://civitai.com/models/69673/lam-ramdayo-style-lora)
- [LoRA-《无职转生》风格](https://civitai.com/models/62950/mushoku-tensei-jobless-reincarnation-anime-style-lora)
- [LoRA-《龙珠超》风格](https://civitai.com/models/59619/dragon-ball-super-style-lora)
- [LoRA-《鬼灭之刃》风格](https://civitai.com/models/21272/demon-slayer-kimetsu-no-yaiba-anime-style-lora)
- [LoRA-新海诚风格](https://civitai.com/models/10626/makoto-shinkai-your-name-substyles-style-lora)
- [LoRA-派蒙的画作风格](https://civitai.com/models/26291/paimons-paintings-style-genshin-impact-stickers)
- [LoRA-沁彩](https://civitai.com/models/16055/colorwater)
- [LoRA-小人书风格](https://civitai.com/models/18323?modelVersionId=25661)


### 2. 图像引导生成

以图像引导图像生成，可使用[ControlNet](https://github.com/lllyasviel/ControlNet)的所有功能。图片引导仅提供了额外的规范，仍需要填写适当的提示词。

**(1) 引导图**

首先，上传一张图或者直接填入图像的url。这张图的宽高比最好和下面参数中填写的宽度高度一致，因为引导图首先会被缩放到到指定宽高。
引导图可以是手机拍摄的照片，也可以是网络上的图片。

**(2) 预处理方式**

指定使用引导图的哪个方面的特性来引导图像生成。如果使用原图则不进行预处理。如果选择了一种预处理方式，则会将引导图处理成指定形式后，以该形式引导图像生成。

**(3) 引导模型**

指定加载哪个模型来进行图像引导生成。使用“原模型”则不额外加载，可实现原版的图生图功能。

建议引导模型和预处理方式对应，获得最佳效果。

**(4) 图像引导力度**

范围0-1，越大则引导力度越大。在使用原模型时，推荐0.5；使用ControlNet系列模型时，可调至1.0。


### 3. 图像超分辨率 (该服务已下线)

在点击“开始生成”按钮后，稍等片刻，图像预览区会显示图像，同时下方出现“获取高清图”按钮，点击按钮即可获得高清图下载链接。

此外，在历史图像记录区或者画廊中，点击缩略图会弹出详细参数框，详细参数预览框中也有获取高清图按钮。

服务器使用[RealESRGAN](https://github.com/xinntao/Real-ESRGAN)模型进行图像超分。

### 4. 提示词增强

#### 帮我写
在提示词输入框右侧有“帮我写”按钮，点击后将对当前输入的内容自动扩写。扩写模型使用微软公司发布的模型[Promptist](https://huggingface.co/spaces/microsoft/Promptist)。

虽然会拓展出来一些提高质量、风格或者艺术家的词汇，但仍无法百分之百保证生成图像的质量，还需手动调整，仅供参考。

输入中文后点击帮我写，原本输入的文字会被翻译成英文后扩写，返回结果将覆盖原有中文文本。

#### 帮我写(ChatGPT版)

ChatGPT是一个十分强大的语言大模型，云景后台调用了OpenAI的官方API，给模型输入一个设定，让它扮演一个生成式艺术提示词助手，将用户输入的关键词扩展成详细的图像描述。

图像描述会使用英文和中文两种语言呈现。点击“填入提示词”后，会将提示词输入框的内容替换为ChatGPT提供的图像描述。

下面是给语言模型输入的设定内容：

> You are a generative art prompt generator. Given some simple word, you will help me expand them to a detailed description that depicts the generated image.When the user ask a question,you should answer '抱歉，我无法回答这个问题，因为它与生成艺术提示无关。'. You will output English description first then translate to Chinese. You will describe the picture directly and don't start with 'in this artwork,...' or 'the artwork/picture/image depicts ...'. Output format: (Eng)... \\n(中文)...


#### 提示词模板

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

### 3. “分享值“是什么？如何增加分享值？

当生成图像数量超过100张时，开始计算分享值。分享值的计算公式：用户发布到画廊的图像数/(用户生成图像的总数-100)。

分享值设立的目的是鼓励用户分享自己的画作，让其他用户了解如何书写提示词和其他参数以达到相同的效果。当然，任何用户都可以访问画廊，获取其他用户分享的画作和参数。画廊对我们的网站是有益的，对用户也是有益的。

分享值小于10%时，用户提交的任务在队列中的优先级会降低，可能会多等待一段时间才能成功提交图像生成任务。对一般用户来说，每产出10张图像分享一张看起来最好的，这并不是一个负担—（只要不是一直生成不适宜分享的内容）。

### 4. 其他

如有其他问题或者建议，可以联系我或加入我们的交流群(QQ群: 557228477)。

""")

