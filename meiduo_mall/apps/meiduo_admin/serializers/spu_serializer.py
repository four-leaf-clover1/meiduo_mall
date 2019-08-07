from rest_framework import serializers
from goods.models import SPU,Brand


class SPUModelSerializer(serializers.ModelSerializer):
    """商品SPU"""
    brand = serializers.StringRelatedField()
    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()


    class Meta:
        model = SPU
        fields = "__all__"

        extra_kwargs = {
            "category1": {"read_only":True},
            "category2": {"read_only":True},
            "category3": {"read_only":True}
        }

class SPUSimpleModelSerializer(serializers.ModelSerializer):
    """品牌"""
    class Meta:
        model = Brand
        fields = ["id","name"]