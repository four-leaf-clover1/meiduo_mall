from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from meiduo_admin.serializers.image_serializer import *
from goods.models import SKUImage,SKU
from meiduo_admin.pages import MyPage


class ImagesView(ModelViewSet):
    """图片表管理"""
    queryset = SKUImage.objects.all()
    serializer_class = SKUImageSerializer
    pagination_class = MyPage


class SKUSimpleView(ListAPIView):
    """SKU商品"""
    queryset = SKU.objects.all()
    serializer_class = SKUSimpleSerializer