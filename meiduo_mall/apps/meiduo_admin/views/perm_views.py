from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from django.contrib.auth.models import Permission,ContentType

from meiduo_admin.serializers.perm_serializer import *
from meiduo_admin.pages import MyPage


class PermissionView(ModelViewSet):
    """用户权限"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = MyPage


class ContentTypeView(ListAPIView):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer