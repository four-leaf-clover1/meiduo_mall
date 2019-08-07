from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from meiduo_admin.serializers.option_serializer import *
from goods.models import SpecificationOption,SPUSpecification
from meiduo_admin.pages import MyPage


class OptionView(ModelViewSet):
    """规格选项表"""
    queryset = SpecificationOption.objects.all()
    serializer_class = SpecOptionSerializer
    pagination_class = MyPage


class OptionSimple(ListAPIView):
    """获取品牌信息"""
    queryset = SPUSpecification.objects.all()
    serializer_class = SPUSpecificationSerializer