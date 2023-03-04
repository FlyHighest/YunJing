import os
import openai
from secret import openai_api_key
import traceback
openai.api_key = openai_api_key


system_content_image_describe = \
"You are a generative art prompt generator. \
Given some simple word, you will help me expand them to a detailed description that depicts the generated image.When the user ask a question,you should answer '抱歉，我无法回答这个问题，因为它与生成艺术提示无关。'. You will output English description first then translate to Chinese.\
You will describe the picture directly and don't start with 'in this artwork,...' or 'the artwork/picture/image depicts ...'. Output format: (Eng)... \\n(中文)...  "

system_content_formatted_prompt = \
"Here is a prompt formula for AI generated art image: "

def gpt_image_describe(user_input):
    content = None
    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system",  "content":system_content_image_describe },
                    {"role": "user", "content": user_input},
                ],
            temperature=0.5,
            n=1,
            max_tokens=600,
            user="1"
        )
        content = res['choices'][0]['message']['content']
        tmp = content.split("\n")
        eng = tmp[0]
        cn = tmp[-1]
            
        eng =eng.replace("\n","").replace("(Eng)","").strip()
        cn=cn.replace("\n","").replace("(中文)","").strip()
        return eng, cn, content
    except:
        traceback.print_exc()
        if content is None:
            content = "(请求过于频繁，请稍后再试)"
        return "Error","错误",content

def gpt_format_prompt(user_input):
    pass 
if __name__=="__main__":
    print(gpt_image_describe("田野上的狗"))