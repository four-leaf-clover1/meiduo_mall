from django.shortcuts import render
from django.views import View
from .models import Area
from django import http
from django.core.cache import cache


from meiduo_mall.utils.response_code import RETCODE
# Create your views here.

class AreasView(View):
    """省市区数据"""
    def get(self,request):

        #获取查询参数area_id
        area_id = request.GET.get('area_id')

        #判断area_id是否有值
        #如果area_id为None:代表要查询所有省的数据
        if area_id is None:
            # 先尝试去redis获取所有省的缓存数据
            province_list = cache.get('province_list')
            if province_list is None:

                province_qs = Area.objects.filter(parent=None)

                #用来装所有省的数据字典
                province_list = []
                # 遍历查询集,将里面的每一个模型转换成字典格式
                for province_model in province_qs:
                    province_list.append(
                        {'id': province_model.id,
                         'name' : province_model.name
                         })
                # 没有缓存,就设置缓存
                cache.set('province_list', province_list, 3600)
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})

        else:
            # 先去缓存读写数据,如果缓存中没有再去mysql
            data_dict = cache.get('sub_area' + area_id)
            if data_dict is None:
                # 如果area_id有值: 代表查询指定area_id的下级所有行政区
                # sub_qs = Area.objects.filter(parent_id=area_id)
                parent_model = Area.objects.get(id=area_id)
                sub_qs = parent_model.subs.all()

                sub_list = [] # 包装所有下级行政区字典
                for sub_model in sub_qs:
                    sub_list.append(
                        {
                            'id' : sub_model.id,
                            'name' : sub_model.name,
                        }
                    )
                #包装要响应的数据
                data_dict = {
                    'id' : parent_model.id,
                    'name' : parent_model.name,
                    'subs' : sub_list
                }
                # 设置缓存
                cache.set('sub_area' + area_id, data_dict, 3600)
            return http.JsonResponse({'code':RETCODE.OK,'errmsg' : 'OK','sub_data':data_dict})

