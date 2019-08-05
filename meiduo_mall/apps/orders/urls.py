from django.conf.urls import url

from . import views


urlpatterns = [
    #结算
    url(r'^orders/settlement/$',views.OrderSettlementView.as_view()),
    #提交订单
    url(r'^orders/commit/$', views.OrderCommitView.as_view()),
    #订单成功展示界面
    url(r'^orders/success/$',views.OrderSuccessView.as_view()),
    #展示全部订单
    url(r'^orders/info/1/$', views.OrderInfoView.as_view())


]