from rest_framework import serializers
from goods.models import SKU,SKUSpecification,SPU,GoodsCategory,\
    SPUSpecification,SpecificationOption


class SKUSpecSimpleSerializer(serializers.ModelSerializer):
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()
    class Meta:
        model = SKUSpecification
        fields = ['spec_id','option_id']


class SKUModelSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()

    specs = SKUSpecSimpleSerializer(many=True)

    class Meta:
        model = SKU
        fields = "__all__"

    def create(self, validated_data):
        specs = validated_data.pop("specs")

        sku = super().create(validated_data)
        for spec in specs:
            spec['sku_id']= sku.id
            SKUSpecification.objects.create(**spec)

        return sku

    def update(self, instance, validated_data):
        specs = validated_data.pop("specs")

        sku = super().update(instance,validated_data)

        SKUSpecification.objects.filter(sku_id=sku.id).delete()
        for spec in specs:
            spec['sku_id']= sku.id
            SKUSpecification.objects.create(**spec)

        return sku



class SKUCategorySimpleSerializer(serializers.ModelSerializer):
    """获取三级分类信息"""
    class Meta:
        model = GoodsCategory
        fields = ["id","name"]


class SPUSimpleSerializer(serializers.ModelSerializer):
    """获取spu表名称数据"""
    class Meta:
        model = SPU
        fields = ["id","name"]


class SpecificationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = ["id","value"]


class SPUSpecSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    options = SpecificationOptionSerializer(many=True)
    class Meta:
        model = SPUSpecification
        fields = ["id",
                  "name",
                  "spu",
                  "spu_id",
                  "options",
                  ]

