class LoRAInformationCard:
    def __init__(self, name, command, 
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
        markdown_strs.append(f"* 提示词指令：`<lora:{self.command}:{self.default_weight}>`")
        if self.best_fit_model is not None:
            markdown_strs.append(f"* 推荐模型：{self.best_fit_model}")
        if len(self.trigger_words)>0:
            trigger_words = ";".join( [f'`{i}`' for i in self.trigger_words] )
            markdown_strs.append(f"* 触发词：{trigger_words}")
        if len(self.additional_words)>0:
            additional_words = ";".join( [f'`{i}`' for i in self.additional_words] )
            markdown_strs.append(f"* 可附加提示词：{additional_words}")
        
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
                        default_weight=0.66,best_fit_model="AsiaFacemix",
                        trigger_words=["hanfugirl,hanfu"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-国风汉服少女仿明风格","hanfu2ming",
                        short_intro=None,
                        default_weight=0.66,best_fit_model="AsiaFacemix",
                        trigger_words=["duijin","ouqun","yunjian"],additional_words=["girlface"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-国风汉服少女仿宋风格","hanfu2song",
                        short_intro=None,
                        default_weight=0.66,best_fit_model="AsiaFacemix",
                        trigger_words=["songmo"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-墨心","moxin",
                        short_intro="水墨画风，中国画风格",
                        default_weight=0.7,best_fit_model=None,
                        trigger_words=["shuimobysim"],additional_words=["wuchangshuo","bonian","zhengbanqiao","badashanren"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-疏可走马","shukezouma",
                        short_intro="增加图像留白面积，配合墨心使用",
                        default_weight=0.7,best_fit_model=None,
                        trigger_words=["shukezouma"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-线稿风格","anime_lineart",
                        default_weight=1.0,best_fit_model=None,
                        trigger_words=["lineart, monochrome"])
)
LoRA_list.append(
    LoRAInformationCard("LoRA-立绘风格","gacha_splash",
                        default_weight=0.5,best_fit_model=None,
                        trigger_words=["[(white background:1.5), ::5]"])
)

LoRA_INFO = dict()

for card in LoRA_list:
    LoRA_INFO[card.name] = str(card) 


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