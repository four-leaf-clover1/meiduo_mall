from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from goods.models import SPU,GoodsCategory
from meiduo_admin.serializers.spu_serializer import *
from meiduo_admin.serializers.sku_serializer import *
from meiduo_admin.pages import MyPage


class SPUViewSet(ModelViewSet):
    """SPU表管理"""
    queryset = SPU.objects.all()
    serializer_class = SPUModelSerializer
    pagination_class = MyPage


class BreadViewSet(ListAPIView):
    """商品品牌"""
    queryset = Brand.objects.all()
    serializer_class = SPUSimpleModelSerializer


class ChannelCategoryView(ListAPIView):
    """获取SPU一级标签"""
    queryset = GoodsCategory.objects.all()
    serializer_class = SKUCategorySimpleSerializer

    def get_queryset(self):
        parent_id = self.kwargs.get("pk")

        if not parent_id:
            return self.queryset.filter(parent=None)
        return self.queryset.filter(parent_id=parent_id)

