from rest_framework import serializers

from goods.models import GoodsChannel


class GoodsChannelSerializer(serializers.ModelSerializer):
    """商品频道"""
    group = serializers.StringRelatedField()
    group_id = serializers.IntegerField()
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()
    class Meta:
        model = GoodsChannel
        fields = "__all__"