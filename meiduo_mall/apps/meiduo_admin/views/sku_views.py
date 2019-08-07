from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from goods.models import SKU,SPU,GoodsCategory
from meiduo_admin.serializers.sku_serializer import *
from meiduo_admin.pages import MyPage

class SKUViewSet(ModelViewSet):
    queryset = SKU.objects.all()
    serializer_class = SKUModelSerializer
    pagination_class = MyPage

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(name__contains=keyword)
        return self.queryset.all()


class SKUCategoryView(ListAPIView):
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)
    serializer_class = SKUCategorySimpleSerializer


class SPUCategoryView(ListAPIView):
    queryset = SPU.objects.all()
    serializer_class = SPUSimpleSerializer


class SPUSpecView(ListAPIView):
    """获取SPU商品规格信息"""
    queryset = SPUSpecification.objects.all()
    serializer_class = SPUSpecSerializer

    def get_queryset(self):

        pk = self.kwargs['pk']

        return SPUSpecification.objects.filter(spu_id=pk)