from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from meiduo_admin.serializers.order_serializer import *
from orders.models import OrderInfo
from meiduo_admin.pages import MyPage


class OrderInfoView(ModelViewSet):
    """订单表"""
    queryset = OrderInfo.objects.all()
    serializer_class = OrderInfoSerializer
    pagination_class = MyPage


    def get_queryset(self):
        keyword = self.request.query_params.get("keyword")

        if keyword:
            return self.queryset.filter(order_id__contains=keyword)
        return self.queryset.all()


