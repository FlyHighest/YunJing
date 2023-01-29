import json
from tencentcloud.common import credential
import traceback
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ses.v20201002 import ses_client, models
from secret import tencentcloud_secret_id,tencentcloud_secret_key,email_netease_code,email_netease_addr
import smtplib,ssl 
from email.message import EmailMessage

def send_verification_mail(target_address, verif_code):
    success = send_verification_mail_tencent(target_address,verif_code)
    if not success:
        success = send_verification_mail_netease(target_address, verif_code)
    return success 

def send_verification_mail_netease(target_address, verif_code):
    try:
        context = ssl.create_default_context()
        sender = email_netease_addr
        receiver = target_address
        subject = "云景AI-验证码"
        body = f"感谢您注册云景AI平台账号！\n\n您的验证码是：\n{verif_code}\n\n如果您没有请求此代码，可忽略这封电子邮件。别人可能错误地键入了您的电子邮件地址。\n-----\n来自: 云景·AI https://yunjing.gallery "
        msg = EmailMessage()
        msg['subject'] = subject
        msg['From'] = sender 
        msg['To'] = receiver
        msg.set_content(body) 
        with smtplib.SMTP_SSL("smtp.163.com",465,context=context) as smtp:
            smtp.login(email_netease_addr,email_netease_code)
            smtp.send_message(msg)
        return True 
    except:
        traceback.print_exc()
        return False 

def send_verification_mail_tencent(target_address, verif_code):
    try:
        print(target_address,verif_code)
        cred = credential.Credential(tencentcloud_secret_id, tencentcloud_secret_key)
        client = ses_client.SesClient(cred, "ap-hongkong")

        req = models.SendEmailRequest()
        verif_json = {
            "veri_code": verif_code
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