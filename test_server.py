import httpx
import msgpack
from secret import MODEL_URL
text2image_data = {
    "type":"text2image",
    "model_name": "openjourney",
    "scheduler_name": "DPM",
    "prompt": "a dog with wings flying in the sky, clouds, golden beautiful sunshine, highres",
    "negative_prompt":"",
    "height":512,
    "width": 512,
    "num_inference_steps": 20,
    "guidance_scale": 7
}
import json

prediction = httpx.post(
    MODEL_URL,
    data=json.dumps(text2image_data),
)

if prediction.status_code == 200:
    print(json.loads(prediction.content)['img_url'])
else:
    print(prediction.status_code, prediction.content)