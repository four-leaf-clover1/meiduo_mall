from django.conf.urls import url, include
from django.contrib import admin

from meiduo_admin.views.login_views import *
from meiduo_admin.views.home_views import *
from meiduo_admin.views.user_views import *
from meiduo_admin.views.sku_views import *
from meiduo_admin.views.spu_views import *
from meiduo_admin.views.spec_views import *
from meiduo_admin.views.option_views import *
from meiduo_admin.views.image_views import *
from meiduo_admin.views.channel_views import *
from meiduo_admin.views.order_views import *
from meiduo_admin.views.perm_views import *

urlpatterns = [
        url(r'^authorizations/$', LoginView.as_view()),

        url(r'^statistical/total_count/$',HomeView.as_view({"get":"total_count"})),
        url(r'^statistical/day_increment/$',HomeView.as_view({"get":"day_increment"})),
        url(r'^statistical/day_active/$',HomeView.as_view({"get":"day_active"})),
        url(r'^statistical/day_orders/$',HomeView.as_view({"get":"day_orders"})),
        url(r'^statistical/month_increment/$',HomeView.as_view({"get":"month_increment"})),

        url(r'^statistical/goods_day_views/$',GoodsVisitCountView.as_view()),

        url(r'^users/$',UserAPIView.as_view()),

        url(r'^skus/$', SKUViewSet.as_view({"get": "list", "post": "create"})),
        url(r'^skus/(?P<pk>\d+)/$', SKUViewSet.as_view({"get": "retrieve",
                                                        "put":"update",
                                                        "delete":"destroy"})),

        url(r'^skus/categories/$', SKUCategoryView.as_view()),
        url(r'^goods/simple/$', SPUCategoryView.as_view()),
        url(r'^goods/(?P<pk>\d+)/specs/$', SPUSpecView.as_view()),

        url(r'^goods/$', SPUViewSet.as_view({"get":"list","post":"create"})),
        url(r'^goods/(?P<pk>\d+)/$', SPUViewSet.as_view({"get":"retrieve",
                                                         "put":"update",
                                                         "delete":"destroy"})),
        url(r'^goods/brands/simple/$', BreadViewSet.as_view()),
        url(r'^goods/channel/categories/$', ChannelCategoryView.as_view()),
        url(r'^goods/channel/categories/(?P<pk>\d+)/$', ChannelCategoryView.as_view()),

        url(r'^goods/specs/$',SpecsView.as_view({"get":"list","post":"create"})),
        url(r'^goods/specs/(?P<pk>\d+)/$',SpecsView.as_view({"get":"retrieve",
                                                            "put":"update",
                                                            "delete":"destroy"})),

        url(r'^specs/options/$',OptionView.as_view({"get":"list","post":"create"})),
        url(r'^specs/options/(?P<pk>\d+)/$',OptionView.as_view({"get":"retrieve",
                                                                "put":"update",
                                                                "delete":"destroy"})),
        url(r'^goods/specs/simple/$',OptionSimple.as_view()),

        url(r'^skus/images/$',ImagesView.as_view({"get":"list","post":"create"})),
        url(r'^skus/images/(?P<pk>\d+)/$',ImagesView.as_view({"get":"retrieve",
                                                              "put":"update",
                                                              "delete":"destroy"})),
        url(r'^skus/simple/$',SKUSimpleView.as_view()),

        url(r'^goods/channels/$', ChannelView.as_view({"get": "list","post":"create"})),
        url(r'^goods/channels/(?P<pk>\d+)/$', ChannelView.as_view({"get": "retrieve",
                                                                   "put":"update",
                                                                   "delete":"destroy"})),
        url(r'^goods/categories/$', CategoriesView.as_view()),

        url(r'^orders/$', OrderInfoView.as_view({"get":"list"})),
        url(r'^orders/(?P<pk>\d+)/$', OrderInfoView.as_view({"get":"retrieve","patch":"partial_update"})),
        url(r'^orders/(?P<pk>\d+)/status/$', OrderInfoView.as_view({"patch":"partial_update"})),

        #用户权限
        url(r'^permission/perms/$',PermissionView.as_view({"get":"list","post":"create"})),
        url(r'^permission/perms/(?P<pk>\d+)/$',PermissionView.as_view({"delete":"destroy",
                                                                       "put":"update",
                                                                       "get":"retrieve"})),

        url(r'^permission/content_types/$',ContentTypeView.as_view())
]

