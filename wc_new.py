"""
name:望潮
author:食翔狂魔
version:1.0
desc:每天0.16
date:2025-04-09 21:40:02
log:登录算法,密码使用的是RSA加密算法,采用PKCS#1 v1.5的填充方式,找到公钥即可;请求签名算法为SHA-256
notice:先写个登录算法和签名算法，今天累了，慢慢研究
"""
from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import requests
import uuid
import hashlib
import time
tokens = [
  {
    "phone":"18888888888",
    "pwd":"km88888",
    "remark":"狂魔1"
  }
]
def getXsignHeaders(token):
  strUuid = str(uuid.uuid4())
  xtime = int(time.time() * 1000)
  data = f"/api/zbtxz/login&&67f67c2e3f293a31f196cf50&&{strUuid}&&{xtime}&&FR*r!isE5W&&64"
  hash_object = hashlib.sha256(data.encode('utf-8'))
  signature_hex = hash_object.hexdigest()
  headers = {
    'X-SESSION-ID': "67f67c2e3f293a31f196cf50",
    'X-REQUEST-ID': strUuid,
    'X-TIMESTAMP': str(xtime),
    'X-SIGNATURE': signature_hex,
    'X-TENANT-ID': "64"
  }
  return headers

def getJmp(pwd):
  pk = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXizPqQeXv68i5vqw9pFREsrqiBTRcg7wB0RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXFc+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlTHMlluw4ZYmnOwg+thwIDAQAB"
  pk2 = RSA.import_key(b64decode(pk))
  cipher = PKCS1_v1_5.new(pk2)
  pwdtext = cipher.encrypt(pwd.encode('utf-8'))
  eb = b64encode(pwdtext).decode('utf-8')
  return eb

def login2(token):
  url = "https://vapp.taizhou.com.cn/api/zbtxz/login"

  payload = {
    'check_token': "",
    'code': token["code"],
    'token': "",
    'type': "-1",
    'union_id': ""
  }
  response = requests.post(url, data=payload, headers=getXsignHeaders(token))
  res = response.json()
  if res['code'] == 0:
    print(f"【{token['remark']}】登录成功, sessionId:{res['data']['session']['id']},device_id:{res['data']['session']['device_id']}")
    token["sessionId"] = res['data']['session']['id']
    token["device_id"] = res['data']['session']['device_id']
  else:
    print(f"【{token['remark']}】登录失败,{response.text}.")
def login(token):
  url = "https://passport.tmuyun.com/web/oauth/credential_auth"
  payload = {
    'client_id': "10019",
    'password': getJmp(token["pwd"]),
    'phone_number': token["phone"]
  }
  response = requests.post(url, data=payload)
  res = response.json()
  if res['code'] == 0:
    print(f"【{token['remark']}】获取登录code成功, code:{res['data']['authorization_code']['code']}")
    token["code"] = res['data']['authorization_code']['code']
    login2(token)
  else:
    print(f"【{token['remark']}】获取登录code失败,{response.text}.")

if __name__ == "__main__":
  for token in tokens:
    login(token)
