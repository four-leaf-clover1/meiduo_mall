import pickle,base64
from django_redis import get_redis_connection

#将cookie购物车数据合并到redis中
#QQ登入和账号登入都需要进行合并
#合并数据：购物车商品数据和勾选状态
#redis购物车数据保留
#如果cookie购物车数据已存在redis购物车数据，就将cookie数据覆盖redis数据
#如果cookie购物车数据不存在redis购物车数据，就将cookie数据追加到redis中
#最终购物车数据的勾选状态以cookie数据为准
#合并完之后将cookie数据删除


def merge_cart_cookie_to_redis(request,response):
    """
    登入时合并购物车
    :param request:登入时借用过来的请求对象
    :param response: 登入时借过来删除cookie数据的响应对象
    :return:
    """
    #获取cookie
    cart_str = request.COOKIES.get('carts')
    #判断cookie是否有值
    # 如果没有，则提前结束
    if cart_str is None:
        return
    #如果有，则把cookie字符串转为字典
    cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
    #创建redis连接对象
    redis_conn = get_redis_connection('carts')
    #创建管道
    pl = redis_conn.pipeline()
    #获取登入用户
    user = request.user
    #遍历cookie字典，把cookie中sku_id和count存储到redis中hash中，如果有则覆盖，没有则新增
    for sku_id in cart_dict:
        pl.hset('carts_%s' % user.id,sku_id,cart_dict[sku_id]['count'])
        #判断cookie中selected勾选状态,如果勾选直接把勾选的sku_id存储到set集合中
        if cart_dict[sku_id]['selected']:
            pl.sadd('selected_%s' % user.id,sku_id)
        #没有勾选就将它移除
        else:
            pl.srem('selected_%s' % user.id,sku_id)
    #执行管道
    pl.execute()

    #删除cookie中存储的值
    response.delete_cookie('carts')