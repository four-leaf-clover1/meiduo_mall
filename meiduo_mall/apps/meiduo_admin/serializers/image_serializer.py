from rest_framework import serializers
from fdfs_client.client import Fdfs_client
from django.conf import settings

from goods.models import SKUImage,SKU


class SKUImageSerializer(serializers.ModelSerializer):
    """SKU图片"""
    class Meta:
        model = SKUImage
        fields = ["id",
                  "sku",
                  "image"]

    def validate(self, attrs):
        file = attrs.pop("image")
        file_content = file.read()

        conn = Fdfs_client(settings.FDFS_CONF_PATH)
        res = conn.upload_by_buffer(file_content)
        """
        @return dict
        {
            'Group name': group_name,
            'Remote file_id': remote_file_id,
            'Status': 'Upload successed.',
            'Local file name': '',
            'Uploaded size': upload_size,
            'Storage IP': storage_ip
        } if success else Non123456e
        """
        if res.get("Status") != 'Upload successed.' or not res:
            raise serializers.ValidationError("图片上传失败")
        file_id = res.get("Remote file_id")
        attrs["image"] = file_id

        return attrs


class SKUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ["id","name"]