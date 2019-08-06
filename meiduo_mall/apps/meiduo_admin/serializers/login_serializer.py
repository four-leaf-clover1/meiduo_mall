from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_jwt.utils import jwt_payload_handler,jwt_encode_handler


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(**attrs)

        if not user:
            #用户对象为None,传统用户身份认证失败
            raise serializers.ValidationError("传统身份认证失败，请检查用户名和密码是否正确")

        #2.检验通过，颁发jwt_token
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return {
            'user':user,
            'token':token,
        }