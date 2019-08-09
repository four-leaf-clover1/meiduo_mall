from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from django.contrib.auth.models import Group

from users.models import User
from meiduo_admin.serializers.admin_serializer import *
from meiduo_admin.serializers.group_serializer import GroupSerializer
from meiduo_admin.pages import MyPage


class AdminView(ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminSerializer
    pagination_class = MyPage


class GroupSimpleView(ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
