class ModelInformationCard:
    def __init__(self, name, short_intro=None, 
                 link=None,
                 example_prompt=None,
                 example_neg_prompt=None,
                 recommended_settings=None) -> None:
        self.name = name
        self.short_intro = short_intro
        self.link = link 
        self.example_prompt = example_prompt
        self.example_neg_prompt = example_neg_prompt
        if type(recommended_settings)==str:
            self.recommended_settings = [recommended_settings]
        else:
            self.recommended_settings = recommended_settings

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self):
        markdown_strs = []
        markdown_strs.append(f"### {self.name}")
        if self.short_intro is not None:
            markdown_strs.append(f"{self.short_intro}")
        if self.link is not None:
            markdown_strs.append(f"* 模型主页：{self.link}")
        if self.example_prompt is not None:
            markdown_strs.append(f"* 示例-提示词：`{self.example_prompt}`")
        if self.example_prompt is not None:
            markdown_strs.append(f"* 示例-反向词：`{self.example_neg_prompt}`")
        if self.recommended_settings is not None:
            markdown_strs.append(f"* 推荐设置：{';'.join(self.recommended_settings)}")

        return "\n".join(markdown_strs)
        
class LoRAInformationCard:
    def __init__(self, name, command,
                 link=None, 
                 default_weight=1.0, 
                 best_fit_model=None, 
                 short_intro=None, 
                 trigger_words=[], 
                 additional_words=[]) -> None:
        self.name = name
        self.command = command 
        self.default_weight = default_weight
        self.best_fit_model = best_fit_model
        self.short_intro = short_intro
        self.trigger_words = trigger_words
        self.link = link
        if type(additional_words)==str:
            self.additional_words = [additional_words]
        else:
            self.additional_words = additional_words
      
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self):
        markdown_strs = []
        markdown_strs.append(f"### {self.name}")
        if self.short_intro is not None:
            markdown_strs.append(f"{self.short_intro}")
        if self.link is not None:
            markdown_strs.append(f"* 模型主页：{self.link}")
        markdown_strs.append(f"* 提示词指令：`<lora:{self.command}:{self.default_weight}>`")
        if self.best_fit_model is not None:
            markdown_strs.append(f"* 推荐模型：{self.best_fit_model}")
        if len(self.trigger_words)>0:
            trigger_words = ";".join( [f'`{i}`' for i in self.trigger_words] )
            markdown_strs.append(f"* 触发词：{trigger_words}")
        if len(self.additional_words)>0:
            additional_words = ";".join( [f'`{i}`' for i in self.additional_words] )
            markdown_strs.append(f"* 可附加提示词：{additional_words}")
        return "\n".join(markdown_strs)
        
LoRA_list = []

LoRA_list.append(
    LoRAInformationCard("LoRA-KoreanDollLikeness","koreandollv10",
                        short_intro=None,
                        default_weight=0.66,best_fit_model="ChilloutMixNi",
                        trigger_words=["girl","woman"],additional_words=["Kpop idol","aegyo sal"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-国风汉服少女","hanfugirlv15",
                        short_intro=None,
                        link="https://www.bilibili.com/read/cv21493779",
                        default_weight=0.66,best_fit_model="AsiaFacemix",
                        trigger_words=["hanfugirl,hanfu"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-国风汉服少女仿明风格","hanfu2ming",
                        short_intro=None,
                        link="https://www.bilibili.com/read/cv21681512",
                        default_weight=0.66,best_fit_model="AsiaFacemix",
                        trigger_words=["duijin","ouqun","yunjian"],additional_words=["girlface"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-国风汉服少女仿宋风格","hanfu2song",
                        short_intro=None,
                        link="https://www.bilibili.com/read/cv21926093",
                        default_weight=0.66,best_fit_model="AsiaFacemix",
                        trigger_words=["songmo"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-墨心","moxin",
                        short_intro="水墨画风，中国画风格",
                        link="https://civitai.com/models/12597/moxin",
                        default_weight=0.7,best_fit_model=None,
                        trigger_words=["shuimobysim"],additional_words=["wuchangshuo","bonian","zhengbanqiao","badashanren"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-疏可走马","shukezouma",
                        short_intro="增加图像留白面积，配合墨心使用",
                        link="https://civitai.com/models/12597/moxin",
                        default_weight=0.7,best_fit_model=None,
                        trigger_words=["shukezouma"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-线稿风格","anime_lineart",
                        link="https://civitai.com/models/16014/anime-lineart-manga-like-style",
                        default_weight=1.0,best_fit_model=None,
                        trigger_words=["lineart, monochrome"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-立绘风格","gacha_splash",
                        short_intro="立绘风格，效果很酷，建议调高分辨率，开启高清修复",
                        link="https://civitai.com/models/13090/gacha-splash-lora",
                        default_weight=0.5,best_fit_model=None,
                        trigger_words=["[(white background:1.5), ::5],isometric"])
)

LoRA_INFO = dict()

for card in LoRA_list:
    LoRA_INFO[card.name] = card


MODEL_NAMES = \
['A-ZovyaRPGArtistTools-v3',
 'ACertainThing',
 'AnyLora',
 'Anything-v3.2',
 'AsiaFaceMix',
 'ChilloutMixNi',
 'Counterfeit-v2.5',
 'Counterfeit-v3',
 'Deliberate-v2',
 'DreamShaper-v4',
 'DreamShaper-v6',
 'Dreamlike-Anime-v1',
 'Dreamlike-Diffusion-v1',
 'Dreamlike-Photoreal-v2',
 'FlexibleDiffusion',
 'GhostMix-v2',
 'GuoFeng-v2',
 'GuoFeng-v3.3',
 'GuoFengRealMix',
 'MeinaMix-v10',
 'MeinaMix-v8',
 'MoonMix-Utopia',
 'NeverEndingDream-v1.22',
 'OpenGen-v1',
 'PixelModel',
 'ProtoGen-x5.8',
 'RealisticVision-V1.3',
 'RealisticVision-v2',
 'Stable-Diffusion-v1.5',
 'Stable-Diffusion-v2.1',
 'Vintedois-Diffusion-v0.2',
 'YunJingAnime-v1']

Model_list = []
Model_list.append(
    ModelInformationCard('A-ZovyaRPGArtistTools-v3',
                         short_intro="可生成RPG元素，用于电子游戏、桌游、书籍封面等物体或人物形象素材生成。🥳使用推荐提示词画个**火车**！",
                         link="https://civitai.com/models/8124/a-zovya-rpg-artist-tools",
                         example_prompt="(an abandoned train ((covered with moss and rust)), lying down under the waterfall), scenery, masterpiece, best quality, high quality, award winning photography, Bokeh, Depth of Field, HDR, bloom, Photorealistic, monochrome, extremely detailed, High Detail, dramatic, volumetric lighting, trending on artstation",
                         example_neg_prompt="disfigured, kitsch, ugly, oversaturated, grain, low-res, Deformed, blurry, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, poorly drawn hands, missing limb, blurry, floating limbs, disconnected limbs, malformed hands, blur, out of focus, long neck, long body, ugly, disgusting, poorly drawn, childish",
                         recommended_settings=["采样器DPM++ 2S a Karras"])
)
Model_list.append(
    ModelInformationCard('ACertainThing',
                         short_intro="动漫风格，经典模型。",
                         link="https://civitai.com/models/8124/a-zovya-rpg-artist-tools",
                         example_prompt="masterpiece, best quality, 1girl, brown hair, green eyes, colorful, autumn, cumulonimbus clouds, lighting, blue sky, falling leaves, garden",
                         example_neg_prompt="disfigured, kitsch, ugly, oversaturated, grain, low-res, Deformed, blurry, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, poorly drawn hands, missing limb, blurry, floating limbs, disconnected limbs, malformed hands, blur, out of focus, long neck, long body, ugly, disgusting, poorly drawn, childish",
                         recommended_settings=None)
)
Model_list.append(
    ModelInformationCard('AnyLora',
                         short_intro="动漫风格，画风和ACertainThing类似。模型作者基于AnyLora训练了许多Lora模型。",
                         link="https://civitai.com/models/23900/anylora-checkpoint",
                         example_prompt="masterpiece, best quality, 1girl, brown hair, green eyes, colorful, autumn, cumulonimbus clouds, lighting, blue sky, falling leaves, garden",
                         example_neg_prompt="disfigured, kitsch, ugly, oversaturated, grain, low-res, Deformed, blurry, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, poorly drawn hands, missing limb, blurry, floating limbs, disconnected limbs, malformed hands, blur, out of focus, long neck, long body, ugly, disgusting, poorly drawn, childish",
                         recommended_settings=None)
)
Model_list.append(
    ModelInformationCard('Anything-v3.2',
                         short_intro="动漫风格，经典模型。",
                         link="https://huggingface.co/cag/anything-v3-1",
                         example_prompt="masterpiece, best quality, 1girl, brown hair, green eyes, colorful, autumn, cumulonimbus clouds, lighting, blue sky, falling leaves, garden",
                         example_neg_prompt="disfigured, kitsch, ugly, oversaturated, grain, low-res, Deformed, blurry, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, poorly drawn hands, missing limb, blurry, floating limbs, disconnected limbs, malformed hands, blur, out of focus, long neck, long body, ugly, disgusting, poorly drawn, childish",
                         recommended_settings="高分辨率生成建议开启高清修复")
)
Model_list.append(
    ModelInformationCard('AsiaFaceMix',
                         short_intro="擅长绘制亚洲人脸、中国元素内容。可配合汉服lora使用。",
                         link="https://huggingface.co/dcy/AsiaFacemix/tree/main",
                         example_prompt="年轻帅小伙的照片，高清，高质量",
                         example_neg_prompt="disfigured, kitsch, ugly, oversaturated, grain, low-res, Deformed, blurry, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, poorly drawn hands, missing limb, blurry, floating limbs, disconnected limbs, malformed hands, blur, out of focus, long neck, long body, ugly, disgusting, poorly drawn, childish",
                         recommended_settings=None)
)
Model_list.append(
    ModelInformationCard('ChilloutMixNi',
                         short_intro="写实风格，能生成好看的人脸。",
                         link="https://civitai.com/models/6424/chilloutmix",
                         example_prompt="年轻帅小伙的照片，高清，高质量",
                         example_neg_prompt="disfigured, kitsch, ugly, oversaturated, grain, low-res, Deformed, blurry, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, poorly drawn hands, missing limb, blurry, floating limbs, disconnected limbs, malformed hands, blur, out of focus, long neck, long body, ugly, disgusting, poorly drawn, childish",
                         recommended_settings=None)
)
Model_list.append(
    ModelInformationCard('Counterfeit-v2.5',
                         short_intro="动漫风格，在反向提示词输入`_easy_negative_`可有效提高画面效果",
                         link="https://huggingface.co/gsdf/Counterfeit-V2.5",
                         example_prompt="(masterpiece, best quality),1girl, solo, flower, long hair, outdoors, letterboxed, school uniform, day, sky, looking up, short sleeves, parted lips, shirt, cloud, black hair, sunlight, white shirt, serafuku, upper body, from side, pink flower, blurry, brown hair, blue sky, depth of field",
                         example_neg_prompt=" _easy_negative_, extra fingers,fewer fingers,disfigured, kitsch, ugly, oversaturated, grain, low-res, Deformed, blurry, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, poorly drawn hands, missing limb, blurry, floating limbs, disconnected limbs, malformed hands, blur, out of focus, long neck, long body, ugly, disgusting, poorly drawn, childish",
                         recommended_settings=None)
)
Model_list.append(
    ModelInformationCard('Counterfeit-v3',
                         short_intro="动漫风格，在反向提示词输入`_easy_negative_v2_`可有效提高画面效果",
                         link="https://huggingface.co/gsdf/Counterfeit-V3.0",
                         example_prompt="(masterpiece, best quality),1girl, solo, flower, long hair, outdoors, letterboxed, school uniform, day, sky, looking up, short sleeves, parted lips, shirt, cloud, black hair, sunlight, white shirt, serafuku, upper body, from side, pink flower, blurry, brown hair, blue sky, depth of field",
                         example_neg_prompt=" _easy_negative_v2_, extra fingers,fewer fingers,disfigured, kitsch, ugly, oversaturated, grain, low-res, Deformed, blurry, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, poorly drawn hands, missing limb, blurry, floating limbs, disconnected limbs, malformed hands, blur, out of focus, long neck, long body, ugly, disgusting, poorly drawn, childish",
                         recommended_settings=None)
)
Model_INFO = dict()

for card in Model_list:
    Model_INFO[card.name] = card
