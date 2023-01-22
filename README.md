# YunJing
云景. A simple web ui (frontend) for AI image generating. 

# 使用手册

## 一、云景·绘图

当前支持以下功能：
- 文本生成图像
- 图像超分辨率
- 提示词自动扩写

### 1. 文本生成图像

#### (1) 参数说明

在绘图页面，左侧是文本生成图像的参数输入区，中间部分是图像预览区，右侧是最近生成的图像。

文本生成图像的参数说明：

| 输入参数   | 说明                                                                                                                                                            |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 提示词     | 对图像内容或特性的描述文本                                                                                                                                      |
| 反向提示词 | 对不希望在图像中出现的内容或特性的描述文本                                                                                                                      |
| 宽度、高度 | 生成图像的尺寸                                                                                                                                                  |
| 引导程度   | 生成图像时对提示词的重视度，更大的值会更严格绘制提示词的内容，但会限制模型发挥                                                                                  |
| 推理步骤   | 一般越大图像质量越高，但生成速度更慢                                                                                                                            |
| 采样器     | [这里](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features#sampling-method-selection)有一些不同采样器效果对比，如果生成效果不好可尝试换采样器 |
| 模型       | 详见下面的"模型介绍"章节                                                                                                                                        |
| 随机种子   | 可以手动指定，为空或-1时将由系统随机生成，保证生成结果可以复现                                                                                                  |

#### (2) 模型介绍

当前后台集成了5个模型，可在“模型”选项自由切换：

- [Stable-Diffusion-v1.5](https://huggingface.co/runwayml/stable-diffusion-v1-5): 原版的stable diffusion 1.5，许多微调模型的基础，比较全能，写实、动漫，人物、风景，包括背景图、头像风格都都能生成，但非常依赖提示词。
- [Protogen-x5.8](https://huggingface.co/darkstorm2150/Protogen_x5.8_Official_Release): AI模型分享网站civiai上最火的模型之一，比较擅长画人物，有时候提示词没有人物相关的也会画个人出来。
- [OpenJourney](https://huggingface.co/prompthero/openjourney): prompthero基于著名的midjourney生成的图像训练stable diffusion获得的模型。使用该模型请在提示词最前面加上'mdjrny-v4 style'。
- [ACertainThing](https://huggingface.co/JosephusCheung/ACertainThing): Joseph Cheung训练的二次元风格的图像生成模型，同NovelAI一样，支持danbooru标签。
- [Anything-v3](https://huggingface.co/Linaqruf/anything-v3.0): 另一个大家喜闻乐见的二次元风格图像生成模型，同NovelAI一样，支持danbooru标签。

### 2. 图像超分辨率

在点击“开始生成”按钮后，稍等片刻，图像预览区会显示图像，同时下方出现“获取高清图”按钮，点击按钮即可获得高清图下载链接。

此外，在历史图像记录区或者画廊中，点击缩略图会弹出详细参数框，详细参数预览框中也有获取高清图按钮。

服务器使用[RealESRGAN](https://github.com/xinntao/Real-ESRGAN)模型进行图像超分。

### 3. 提示词自动扩写

在提示词输入框右侧有“帮我写”按钮，点击后将对当前输入的内容自动扩写。扩写模型使用[MagicPrompt](https://huggingface.co/Gustavosta/MagicPrompt-Stable-Diffusion)，主要是为stable diffusion准备的，protogen和openjourney也可以参考。

虽然会拓展出来一些提高质量、风格或者艺术家的词汇，但仍无法百分之百保证生成图像的质量，还需手动调整，仅供参考。

## 二、云景·画廊

生成图像后，点击发布按钮，即可将图像分享到画廊，与其他用户分享您的成果和创作参数。您也可以在画廊中点击您喜欢的图像，打开参数详情预览框，点击复刻按钮，快速填写该图的生成参数，在此基础上根据您的需要进行调整。

目前画廊随机展示图像，按关键词搜索图像的功能正在开发中，敬请期待。

欢迎大家多贡献好图~





