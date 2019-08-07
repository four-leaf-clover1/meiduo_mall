from rest_framework import serializers
from goods.models import SPUSpecification


class SPUSpecSerializer(serializers.ModelSerializer):
    """商品SPU规格"""
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    class Meta:
        model = SPUSpecification
        fields = ["id",
                  "name",
                  "spu",
                  "spu_id"
                  ]