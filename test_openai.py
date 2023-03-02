import os
import openai
from secret import openai_api_key
openai.api_key = openai_api_key

image_describer= \
"You are a generative art prompt generator. \
Given some simple word, you will help me expand them to a detailed description that depicts the generated image. You will output English description first then translate to Chinese.\
Describe the picture directly and don't start with 'in this artwork,...' or 'the artwork/picture/image depicts ...'. Output format: (Eng)... \\n(中文)...  "


res = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system",  "content":image_describer },
            {"role": "user", "content": "田野上的美丽女孩"},
        ],
    temperature=1,
    n=1,
    max_tokens=400,
    user="1"
)

print(res)
print(res['choices'][0]['message']['content'])
