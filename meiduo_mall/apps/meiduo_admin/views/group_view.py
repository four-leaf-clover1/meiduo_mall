from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group,Permission
from rest_framework.generics import ListAPIView

from meiduo_admin.serializers.group_serializer import *
from meiduo_admin.pages import MyPage
from meiduo_admin.serializers.perm_serializer import PermissionSerializer


class GroupView(ModelViewSet):
    """用户组"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = MyPage


class PermSimpleView(ListAPIView):
    """用户列表"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer