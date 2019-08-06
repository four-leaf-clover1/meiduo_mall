from django.conf.urls import url, include
from django.contrib import admin

from meiduo_admin.views.login_views import *
from meiduo_admin.views.home_views import *

urlpatterns = [
        url(r'^authorizations/$', LoginView.as_view()),

        url(r'^statistical/total_count/$',HomeView.as_view({"get":"total_count"})),
        url(r'^statistical/day_increment/$',HomeView.as_view({"get":"day_increment"})),
        url(r'^statistical/day_active/$',HomeView.as_view({"get":"day_active"})),
        url(r'^statistical/day_orders/$',HomeView.as_view({"get":"day_orders"})),
        url(r'^statistical/month_increment/$',HomeView.as_view({"get":"month_increment"})),

        url(r'^statistical/goods_day_views/$',GoodsVisitCountView.as_view()),
]
