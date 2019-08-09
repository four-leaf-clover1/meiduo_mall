from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from users.models import User


class AdminSerializer(serializers.ModelSerializer):
    """超级管理员"""
    class Meta:
        model = User
        fields = ["id",
                  "username",
                  "email",
                  "mobile",

                  "password",
                  "groups",
                  "user_permissions"
                  ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, attrs):
        attrs["password"] = make_password(attrs["password"])
        attrs["is_staff"] = True
        return attrs