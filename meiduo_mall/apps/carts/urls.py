from django.conf.urls import url


from . import views


urlpatterns = [
    #购物车增删改查
    url(r'^carts/$',views.CartsView.as_view()),
    #购物车增删改查
    url(r'^carts/selection/$',views.CartSelectAllView.as_view()),
    #购物车增删改查
    url(r'^carts/simple/$',views.CartSimpleView.as_view()),



]