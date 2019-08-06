from rest_framework.viewsets import ViewSet
from datetime import date
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from rest_framework.generics import ListAPIView

from users.models import User
from orders.models import OrderInfo
from goods.models import GoodsVisitCount
from meiduo_admin.serializers.home_serializer import *

import pytz


class HomeView(ViewSet):

    def total_count(self,request):
        """用户总数"""
        now_date = date.today()
        count = User.objects.all().count()

        return Response({
            'count':count,
            'date':now_date
        })

    def day_increment(self,request):
        """日增用户"""
        cur_date = timezone.now()

        shanghai_date = cur_date.astimezone(tz=pytz.timezone(settings.TIME_ZONE))

        shanghai_0_date = shanghai_date.replace(hour=0, minute=0, second=0, microsecond=0)

        count = User.objects.filter(date_joined__gte=shanghai_0_date).count()

        return Response({
            "count": count,
            "date": shanghai_0_date.date()
        })

    def day_active(self,request):
        """日活跃用户"""
        cur_date = timezone.now()
        shanghai_date = cur_date.astimezone(tz=pytz.timezone(settings.TIME_ZONE))
        shanghai_0_date = shanghai_date.replace(hour=0,minute=0,second=0,microsecond=0)
        count = User.objects.filter(last_login__gte=shanghai_0_date).count()

        return Response({
            "count":count,
            "date":shanghai_0_date.date()
        })

    def day_orders(self,request):
        """日下单用户"""
        cur_date = timezone.now()
        shanghai_date = cur_date.astimezone(tz=pytz.timezone(settings.TIME_ZONE))
        shanghai_0_date = shanghai_date.replace(hour=0, minute=0, second=0, microsecond=0)
        # user_queryset = User.objects.filter(orderinfo_set__create_time__gte=shanghai_0_date)
        # count = len(set(user_queryset))
        # 从从表入手
        # 2.1、找出今天下的所有订单
        order_queryset = OrderInfo.objects.filter(create_time__gte=shanghai_0_date)
        # 2.2 取出每个从表对象关联的主表，并统计主表数据
        user_list = []
        for order in order_queryset:
        # order是单一的订单对象
            user_list.append(order.user)
        count = len(set(user_list))

        return Response({
            "count": count,
            "date": shanghai_0_date.date()
        })

    def month_increment(self,request):
        """月增用户统计"""
        cur_0_time = timezone.now().astimezone(tz=pytz.timezone(settings.TIME_ZONE)).replace(hour=0,
                                                                                             minute=0,
                                                                                             second=0,
                                                                                             microsecond=0)
        begin_0_time = cur_0_time - timedelta(days=29)

        calc_list = []
        for index in range(30):
            calc_o_time = begin_0_time + timedelta(days=index)

            count = User.objects.filter(date_joined__gte=calc_o_time,
                                        date_joined__lt=calc_o_time+timedelta(days=1)).count()

            calc_list.append({
                "count":count,
                "date": calc_o_time.date()
            })
        return Response(calc_list)


class GoodsVisitCountView(ListAPIView):
    queryset = GoodsVisitCount.objects.all()
    serializer_class = GoodsVisitCountSerializer

    def get_queryset(self):
        cur_0_time = timezone.now().astimezone(tz=pytz.timezone(settings.TIME_ZONE)).replace(hour=0,
                                                                                             minute=0,
                                                                                             second=0,
                                                                                             microsecond=0)

        return self.queryset.filter(create_time__gte=cur_0_time)







