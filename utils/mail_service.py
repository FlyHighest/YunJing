import json
from tencentcloud.common import credential

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ses.v20201002 import ses_client, models
from secret import tencentcloud_secret_id,tencentcloud_secret_key

def send_verification_mail(target_address, verif_code):
    try:
        print(target_address,verif_code)
        cred = credential.Credential(tencentcloud_secret_id, tencentcloud_secret_key)
        client = ses_client.SesClient(cred, "ap-hongkong")

        req = models.SendEmailRequest()
        verif_json = {
            "verif_code": verif_code
        }
        params = {
            "FromEmailAddress": "yunjing@dong-liu.com",
            "Destination": [ target_address ],
            "Template": {
                "TemplateID": 65369,
                "TemplateData":json.dumps(verif_json)
            },
            "Subject": "云景平台注册-验证码",
            "TriggerType": 1
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个SendEmailResponse的实例，与请求对象对应
        resp = client.SendEmail(req)
        # 输出json格式的字符串回包
        print(resp.to_json_string())
        return True 
    except TencentCloudSDKException as err:
        print(err)
        return False