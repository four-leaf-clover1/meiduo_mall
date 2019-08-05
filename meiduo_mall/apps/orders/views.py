from django.shortcuts import render
from django_redis import get_redis_connection
from decimal import Decimal
import json
from django import http
from django.utils import timezone
from django.db import transaction

from meiduo_mall.utils.views import LoginRequiredView
from users.models import Address
from goods.models import SKU
from .models import OrderInfo,OrderGoods
from meiduo_mall.utils.response_code import RETCODE
import logging
logger = logging.getLogger('django')
# Create your views here.

class OrderSettlementView(LoginRequiredView):
    """结算订单"""

    def get(self,request):
        """提供订单结算界面"""
        #获取user
        user = request.user
        #查询登入用户所有未被逻辑删除的地址
        address = Address.objects.filter(user=user,is_deleted=False)
        #创建redis连接对象
        redis_conn = get_redis_connection('carts')
        #获取hash数据
        redis_carts = redis_conn.hgetall('carts_%s' % user.id)
        #获取set数据
        selected_ids = redis_conn.smembers('selected_%s' % user.id)
        cart_dict = {}
        #对hash数据进行过滤，筛选只要被勾选的商品
        for sku_id_bytes in selected_ids:
            cart_dict[int(sku_id_bytes)]=int(redis_carts[sku_id_bytes])

        #通过sku_id查询到所有的sku模型
        skus = SKU.objects.filter(id__in=cart_dict.keys())
        #定义两个变量一个商品总数量，一个总价
        total_count = 0
        total_amount = 0
        #遍历sku查询模型，给每个sku模型多定义一个count和amount属性
        for sku in skus:
            sku.count = cart_dict[sku.id]
            sku.amount = sku.price * sku.count

            total_count += sku.count
            total_amount += sku.amount

        freight = Decimal('10.00') #运费
        #包装成模板进行渲染
        context = {
            'addresses' : address, #收获地址
            'skus' : skus, #所有勾选的商品
            'total_count' : total_count, #商品总数量
            'total_amount' : total_amount, #商品总价格
            'freight' : freight, #运费
            'payment_amount' : total_amount + freight #总金额
        }
        return render(request,'place_order.html',context)


class OrderCommitView(LoginRequiredView):
    """提交订单"""
    def post(self,request):
        #接收请求体数据
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        user = request.user
        #校验
        if all([address_id,pay_method]) is False:
            return http.HttpResponseForbidden('缺少必要参数')
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('address_id无效')
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数有误')
        #新增订单信息记录
        #生成订单编号
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id
        #判断订单状态
        status = (OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                    if (pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'])
                    else OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
        #显示的开启一个事务
        with transaction.atomic():
            #创建事物保存点
            save_id = transaction.savepoint()

            try:
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=0,
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=status
                )
                #创建redis连接对象
                redis_conn = get_redis_connection('carts')
                #获取hash数据
                redis_carts = redis_conn.hgetall('carts_%s' % user.id)
                #获取set数据
                selected_ids = redis_conn.smembers('selected_%s' % user.id)
                #定义一个字典将所要购买的商品id和count进行存储
                cart_dict = {}
                #对redis 中hash购物车数据进行过滤,只要勾选就将其加入到字典中
                for sku_id_bytes in selected_ids:
                    # cart_dict[int(sku_id_bytes)] = int(redis_carts[sku_id_bytes]['count'])
                    cart_dict[int(sku_id_bytes)] = int(redis_carts[sku_id_bytes])

                #遍历要购买的商品数据字典
                # print(cart_dict)
                for sku_id in cart_dict:
                    while True:
                        #查询sku模型
                        sku = SKU.objects.get(id=sku_id)
                        #获取当前所要购买的数量
                        buy_count = cart_dict[sku_id]
                        #获取当前商品的库存量
                        origin_stock = sku.stock
                        #获取当前商品的原本销量
                        origin_sales = sku.sales
                        #判断库存是否充足
                        if buy_count > origin_stock:
                            #如果库存不足对事务中的操作进行回滚
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code':RETCODE.STOCKERR,'errmsg':'库存不足'})
                        #修改sku的库存和销量
                        #计算新的库存
                        new_stock = origin_stock - buy_count
                        #计算新的销量
                        new_sales = origin_sales + buy_count
                        #给sku的库存和销量属性重新赋值
                        # sku.stock = new_stock
                        # sku.sales = new_sales
                        # sku.save()
                        result = SKU.objects.filter(id=sku_id,stock=origin_stock).update(stock=new_stock,sales=new_sales)
                        if result == 0:#说明本次修改失败
                            continue

                        # 修改spu的销量
                        spu = sku.spu
                        spu.sales += buy_count
                        spu.save()
                        #新增订单中N个商品记录
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=buy_count,
                            price=sku.price
                        )
                        # 累加订单中商品的总数量
                        order.total_count += buy_count
                        order.total_amount += (sku.price * buy_count)
                        break #对当前商品下单成功，结束死循环，继续下一个商品下单
                order.total_amount += order.freight
                order.save()

            except Exception as e:
                #try里面出现任何问题，进行暴力回滚
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code':RETCODE.STOCKERR,'errmsg':'提交订单失败'})
            else:
                #提交订单成功，显示的提交一次事务
                transaction.savepoint_commit(save_id)

        #清除购物车购买过的商品数据
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *cart_dict.keys())
        pl.delete('selected_%s' % user.id)
        pl.execute()
        #响应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK','order_id':order_id})


class OrderSuccessView(LoginRequiredView):
    """展示订单界面"""

    def get(self,request):
        #获取查询参数
        query_dict = request.GET
        payment_amount = query_dict.get('payment_amount')
        order_id = query_dict.get('order_id')
        pay_method = query_dict.get('pay_method')
        #校验
        try:
            OrderInfo.objects.get(user=request.user,order_id=order_id,total_amount=payment_amount,pay_method=pay_method)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('参数有误')

        #包装要进行渲染的内容
        context = {
            'payment_amount' : payment_amount,
            'order_id' : order_id,
            'pay_method' : pay_method
        }
        #响应
        return render(request,'order_success.html',context)


class OrderInfoView(LoginRequiredView):
    """展示全部订单"""

    def get(self,request):
        user = request.user
        query_qs = OrderInfo.objects.filter(user_id=user)
        #通过遍历查询集得到订单时间，订单号
        #定义一个字典用来装订单时间，订单号
        page_orders = []
        sku_list = []
        for order in query_qs:
            # page_orders[order.order_id]['create_time'] = order.create_time
            # page_orders[order.order_id]['order_id'] = order.order_id
            status = (OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                      if (order.pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'])
                      else OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
            pay_method = (OrderInfo.PAY_METHOD_CHOICES[2]
                      if (order.status == OrderInfo.PAY_METHODS_ENUM['ALIPAY'])
                      else OrderInfo.PAY_METHOD_CHOICES[1])
            print(pay_method)
            page_orders.append(
                 {
                    'create_time': order.create_time,
                    'order_id' : order.order_id,
                    'sku_list' : sku_list,
                    'total_amount':order.total_amount,
                    'freight':order.freight,
                    'pay_method_name':pay_method[1],
                    'status':order.status,
                    'status_name':order.ORDER_STATUS_CHOICES[status][1]
                }
            )

            orders = order.skus.all()
            for skus in orders:
                default_image = skus.sku.default_image
                sku_list.append({
                'default_image' : default_image,
                'name'   : skus.sku.name,
                'price'  : skus.price,
                'count'  : skus.count,
                'amount' : skus.price * skus.count
                })


        # print(page_orders)


        context = {
            'page_orders' : page_orders
        }


        return render(request,'user_center_order.html',context)




