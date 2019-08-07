from rest_framework import serializers
from goods.models import SpecificationOption,SPUSpecification


class SpecOptionSerializer(serializers.ModelSerializer):
    """规格选项"""
    spec = serializers.StringRelatedField()
    spec_id = serializers.IntegerField()
    class Meta:
        model = SpecificationOption
        fields = "__all__"


class SPUSpecificationSerializer(serializers.ModelSerializer):
    """商品SPU规格"""
    class Meta:
        model = SPUSpecification
        fields = ["id",
                  "name"]