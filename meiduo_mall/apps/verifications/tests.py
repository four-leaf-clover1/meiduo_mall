from django.test import TestCase

# Create your tests here.
import json,base64,hmac,hashlib


header = {
  'typ': 'JWT',
  'alg': 'HS256' # sha256签名算法（加密）
}
header = json.dumps(header)
header = base64.b64encode(header.encode())


payload = {
    'iss': "weiwei",
    'aud': "zhangsan",
    'username': "zhangsan",
    "age":18
}
