from rest_framework import serializers

from orders.models import OrderInfo,OrderGoods
from goods.models import SKU


class SKUSerializer(serializers.ModelSerializer):
    """SKU"""
    class Meta:
        model = SKU
        fields = ["name","default_image"]


class OrderGoodsSerializer(serializers.ModelSerializer):
    """订单商品"""
    sku = SKUSerializer(read_only=True)
    class Meta:
        model = OrderGoods
        fields = ["count","price","sku"]


class OrderInfoSerializer(serializers.ModelSerializer):
    """订单表"""
    user = serializers.StringRelatedField()
    skus = OrderGoodsSerializer(many=True,read_only=True)
    create_time = serializers.DateTimeField(format("%Y-%m-%d"))
    class Meta:
        model = OrderInfo
        fields = "__all__"

