from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from meiduo_admin.serializers.channel_serializer import *
from goods.models import GoodsChannel
from meiduo_admin.pages import MyPage


class ChannelView(ModelViewSet):
    """商品频道"""
    queryset = GoodsChannel.objects.all()
    serializer_class = GoodsChannelSerializer
    pagination_class = MyPage


class CategoriesView(ListAPIView):
    """频道分类"""
    queryset = GoodsChannel.objects.all()
    serializer_class = GoodsChannelSerializer