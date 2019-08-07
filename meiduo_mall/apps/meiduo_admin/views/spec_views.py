from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.spec_serializer import *
from goods.models import SPUSpecification
from meiduo_admin.pages import MyPage

class SpecsView(ModelViewSet):
    queryset = SPUSpecification.objects.all()
    serializer_class = SPUSpecSerializer
    pagination_class = MyPage
