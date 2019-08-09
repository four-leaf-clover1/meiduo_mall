from rest_framework import serializers
from django.contrib.auth.models import Group


class GroupSerializer(serializers.ModelSerializer):
    """用户组"""
    class Meta:
        model = Group
        fields = ["id","name","permissions"]