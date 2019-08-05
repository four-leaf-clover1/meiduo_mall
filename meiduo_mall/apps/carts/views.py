from django.shortcuts import render
from django.views import View
import json,pickle,base64
from django import http
from django_redis import get_redis_connection


from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
# Create your views here.

class CartsView(View):
    """购物车管理"""

    def post(self,request):
        """添加购物车"""
        #接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected',True)

        #校验参数
        if all([sku_id,count]) is False:
            return http.HttpResponseForbidden('缺少必传参数')
        #判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')
        #判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')
        #判断selected是否为bool值
        if selected:
            if not isinstance(selected,bool):
                return http.HttpResponseForbidden('参数selected有误')

        #判断用户是否登入
        user = request.user
        if user.is_authenticated:
            #登入用户，操作redis购物车
            #创建redis连接对象
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            #新增购物车数据
            pl.hincrby('carts_%s' % user.id,sku_id,count)
            #新增选中状态
            if selected:
                pl.sadd('selected_%s' % user.id,sku_id)
            #执行管道
            pl.execute()
            #响应结果
            return http.JsonResponse({'code':RETCODE.OK,'errmsg':'添加购物车成功'})

        else:
            #未登入用户，操作cookie购物车
            cart_str = request.COOKIES.get('carts')
            #如果用户操作过cookie购物车
            if cart_str:
                #有cookie购物车数据，就把他从字符串转到字典类型
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
                # 判断本次添加到的商品之前是否已经添加过,如果添加过,就把count进行累加
                if sku_id in cart_dict:
                    #获取它原有的购买数量
                    origin_count = cart_dict[sku_id]['count']
                    count += origin_count



            else:
                # 没有cookie购物车数据，准备一个字典
                cart_dict = {}

            #添加or修改
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            #将购物车数据设置在cookie之前，将cart_dict字典转为字符串
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            #创建响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            #设置cookie
            response.set_cookie('carts',cart_str)

            return response


    def get(self,request):
        """购物车数据展示"""
        #先获取请求对象user
        user = request.user

        #判断是否是登录用户
        if user.is_authenticated:
            #登录用户，查询redis购物车
            #连接redis对象
            redis_conn = get_redis_connection('carts')
            #获取redis中的购物车的数据
            redis_carts = redis_conn.hgetall('carts_%s' % user.id)
            #获取redis选中状态
            selected_ids = redis_conn.smembers('selected_%s' % user.id)

            #将redis中的数据构造成cookie中的格式一致,方便统一查询
            cart_dict = {}
            for sku_id_bytes in redis_carts:
                cart_dict[int(sku_id_bytes)] = {
                    'count' : int(redis_carts[sku_id_bytes]),
                    'selected' : (sku_id_bytes in selected_ids)
                }

        else:
            #未登录用户获取cookie购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                #有cookie购物车数据就将它从字符串转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                #没有cookie购物车数据，就将一个空页面展示出来
                return render(request,'cart.html')

        #对sku_id进行查询sku模型及包装模型需要渲染的数据,登入和未登入共用一个代码
        #为了查询sku模型
        sku_qs = SKU.objects.filter(id__in=cart_dict.keys())
        cart_skus = []
        for sku in sku_qs:
            count = cart_dict[sku.id]['count']
            cart_skus.append({
                'id' : sku.id,
                'name' : sku.name,
                'default_image_url' : sku.default_image.url,
                'price' : str(sku.price),
                'count' : count,
                'selected' : str(cart_dict[sku.id]['selected']),
                'amount' : str(sku.price * count)

            })
        context = {
            'cart_skus': cart_skus
        }
        return render(request,'cart.html',context)


    def put(self,request):
        """修改购物车"""
        #接收和校验参数
        #判断用户是否登入
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected',True)

        #判断参数是否齐全
        if all([sku_id,count]) is False:
            return http.HttpResponseForbidden('缺少必传参数')
        #判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id无效')
        #判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('商品sku_id不存在')
        #判断selected是否为bool值
        if selected:
            if not isinstance(selected,bool):
                return http.HttpResponseForbidden('参数selected有误')

        user = request.user
        if user.is_authenticated:
            #登入用户，修改redis购物车
            #创建redis连接对象
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            #修改hash数据
            pl.hset('carts_%s' % user.id,sku_id,count)
            #修改set数据
            if selected:
                #如果勾选，就把sku_id添加到set中
                pl.sadd('selected_%s' % user.id,sku_id)
            else:
                #如果没有勾选，就把sku_id从set中移除
                pl.srem('selected_%s' % user.id,sku_id)
            pl.execute()
            #查出sku_id对应的sku模型,然后包装修改的购物车响应给后段
            sku = SKU.objects.get(id=sku_id)
            sku_dict = {
                'id' : sku.id,
                'name' : sku.name,
                'default_image_url' : sku.default_image.url,
                'price' : str(sku.price),
                'count' : count,
                'selected' : selected,
                'amount' : str(sku.price * count)

            }
            #响应
            return http.JsonResponse({'code':RETCODE.OK,'errmsg':'修改购物车成功','cart_sku':sku_dict})
        else:
            #未登入用户，修改cookie购物车
            #获取cookie数据
            cart_str = request.COOKIES.get('carts')
            #判断cookie是否有
            if cart_str:
                #把cookie字符串转化为字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                #如果没有cookie，提前响应结束
                return render(request,'cart.html')
            #修改cart_dict中的数据
            cart_dict[sku_id] = {
                'count' : count,
                'selected' : selected
            }
            #把cookie字典转为字符串
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            sku = SKU.objects.get(id=sku_id)
            sku_dict = {
                'id' : sku.id,
                'name' : sku.name,
                'default_image_url' : sku.default_image.url,
                'price' : str(sku.price),
                'count' : count,
                'selected' : selected,
                'amount' : str(sku.price * count)
            }
            #创建响应对象
            response = http.JsonResponse({'code':RETCODE.OK,'errmsg':'修改购物车成功','cart_sku':sku_dict})
            #设置cookie
            response.set_cookie('carts',cart_str)
            #响应
            return response


    def delete(self,request):
        """删除购物车"""
        #接收和校验参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id不存在')
        #判断用户是否登入
        user = request.user
        if user.is_authenticated:
            #登入用户，删除redis购物车
            #创建redis连接对象
            redis_conn = get_redis_connection('carts')
            #创建管道
            pl = redis_conn.pipeline()
            #把指定的sku_id对应的键值对从hash中删除
            pl.hdel('carts_%s' % user.id,sku_id)
            #把对应的sku_id从set移除
            pl.srem('selected_%s' % user.id,sku_id)
            pl.execute()

            #响应
            return http.JsonResponse({'code':RETCODE.OK,'errmsg':'删除成功'})

        else:
            #未登入用户,删除cookie购物车
            #获取cookies购物车数据
            cart_str = request.COOKIES.get('carts')
            #判断是否有cookie
            if cart_str:
                #把cookie字符串转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

            else:
                # 没有提前响应
                return render(request,'cart.html')
            #删除cookie字典中指定的键值对
            if sku_id in cart_dict:
                del cart_dict[sku_id]
            #创建响应对像
            response = http.JsonResponse({'code':RETCODE.OK,'errmsg':'删除成功'})
            #如果cookie大字典已经没了cookie数据，直接删除cookie所有数据
            if not cart_dict:
                response.delete_cookie('carts')
                return response
            #把cookie字典转回为字符串
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            #重新设置cookie
            response.set_cookie('carts',cart_str)
            return response


class CartSelectAllView(View):
    """全选购物车"""

    def put(self,request):
        #接收和校验参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected',True)
        if selected:
            if not isinstance(selected,bool):
                return http.HttpResponseForbidden('参数selected有误')
        #判断用户是否登入
        user = request.user
        if user.is_authenticated:
            #登入用户，操作redis购物车
            #创建redis连接对象
            redis_conn = get_redis_connection('carts')
            if selected:
                #全选
                #将hash中所有的sku_id添加到set中
                redis_carts = redis_conn.hgetall('carts_%s' % user.id)
                #取得redis_carts中所有的keys
                sku_ids = redis_carts.keys()
                redis_conn.sadd('selected_%s' % user.id, *sku_ids)
            else:
                #取消全选
                #将set中所有的sku_id的值置为False
                redis_conn.delete('selected_%s' % user.id)
            #响应
            return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK'})

        else:
            #未登入用户，操作cookie购物车
            #获取cookie购物车数据
            cart_str = request.COOKIES.get('carts')
            #判断cookie中是否有值
            if cart_str:
                #有值，把字符串转为字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

            else:
                #没值则提前响应
                return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':'没有cookie值'})
            #修改字典中每个value中的selected中的值为True或False
            for sku_id in cart_dict:
                cart_dict[sku_id] = {
                    'count' : cart_dict[sku_id]['count'],
                    'selected' : selected
                }
            #再把字典转为字符串
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            #创建响应对象
            response = http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK'})
            #设置cookie
            response.set_cookie('carts',cart_str)
            #响应
            return response


class CartSimpleView(View):
    """简单版购物车"""

    def get(self,request):

        #判断是否是登入用户
        user = request.user
        if user.is_authenticated:
            #登入用户
            #创建redis连接对像
            redis_conn = get_redis_connection('carts')
            #获取hash中所有的键值对
            redis_carts = redis_conn.hgetall('carts_%s' % user.id)
            #获取set中所有的键值对
            selected_ids = redis_conn.smembers('selected_%s' % user.id)
            #把redis购物车的数据格式转化为cookie购物车的数据格式
            #创建一个空字典
            cart_dict = {}
            for sku_id_bytes,count in redis_carts.items():
                cart_dict[int(sku_id_bytes)] = {
                    'count': int(count),
                    'selected': (sku_id_bytes in selected_ids)
                }

        else:
            #未登入用户
            #获取cookie
            #判断cookie是否有值
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                #有cookie购物车数据就将字符串转为字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                #没有cookie购物车数据，就显示为一个空白的购物车界面
                return render(request,'cart.html')
        #为了sku_id查询sku模型代码模板需要渲染的数据代码，登入和未登入共用一个代码
        #查询sku模型
        #构造一个列表包装前端界面来渲染所有购物车数据
        sku_qs = SKU.objects.filter(id__in=cart_dict.keys())
        cart_skus = []
        for sku in sku_qs:
            # 获取指定商品要购买的数量
            count = cart_dict[sku.id]['count']
            cart_skus.append({
                'id':sku.id,
                'name':sku.name,
                'default_image_url':sku.default_image.url,
                'count':count,
            })

        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK','cart_skus':cart_skus})





