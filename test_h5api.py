 # !/usr/bin/env Python3
 # -*- coding: utf-8 -*-

import hashlib
from urllib.parse import urlencode,unquote
'''
签名算法
'''
# 签名算法
def sign(attributes, key):
    attributes_new = {k: attributes[k] for k in sorted(attributes.keys())}
    sign_str = "&".join(
        [f"{key}={attributes_new[key]}" for key in attributes_new.keys()]
    )
    return (
        hashlib.md5((sign_str + "&key=" + key).encode(encoding="utf-8"))
        .hexdigest()
        .upper()
    )

import requests
import json
import hashlib

# 请求地址
url = "https://open.h5zhifu.com/api/native"

# 应用ID
app_id = 2308135123

# 商家订单编号
out_trade_no = "202308130001"

# 销售商品描述
description = "Example Product"

# 支付类型
pay_type = "alipay"

# 订单金额（单位为分，且为整数）
amount = 10000

# 开发者自定义数据（选填）
attach = "custom_data"

# 支付成功后回调地址
notify_url = "https://example.com/callback"

# 数据签名密钥，请根据实际情况填写
sign_key = "your_sign_key"

# 构造请求参数
data = {
    "app_id": app_id,
    "out_trade_no": out_trade_no,
    "description": description,
    "pay_type": pay_type,
    "amount": amount,
    "attach": attach,
    "notify_url": notify_url,
}

# 添加数据签名到请求参数
data["sign"] = sign(data, sign_key)

# 发起请求
response = requests.post(url, json=data)

# 获取响应结果
result = response.json()
print(result)
