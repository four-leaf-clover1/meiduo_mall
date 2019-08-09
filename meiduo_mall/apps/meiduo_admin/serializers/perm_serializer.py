from rest_framework import serializers

from django.contrib.auth.models import Permission,ContentType


class PermissionSerializer(serializers.ModelSerializer):
    """用户权限"""
    class Meta:
        model = Permission
        fields = ["id","name","codename","content_type"]


class ContentTypeSerializer(serializers.ModelSerializer):
    """获取权限列表"""
    class Meta:
        model = ContentType
        fields = ["id","name"]