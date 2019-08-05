from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http
from random import randint
from django.conf import settings

from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
# from meiduo_mall.libs.yuntongxun.sms import CCP
from . import constants
from celery_tasks.sms.tasks import send_sms_code
from itsdangerous import TimedJSONWebSignatureSerializer as TJW


import logging

logger = logging.getLogger('django')


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        # 使用SDK 生成图形验证码
        # name: 唯一标识
        # text: 图形验证码中的字符内容
        # image_bytes: 图片bytes类型数据
        name, text, image_bytes = captcha.generate_captcha()

        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # 把图形验证码字符内容存储到redis中  # 为下后面发短信验证码时,可以进行校验
        redis_conn.setex(uuid, constants.IMAGE_CODE_EXPIRE_REDIS, text)
        # 响应  MIME
        return http.HttpResponse(image_bytes, content_type='image/png')


class SMSCodeView(View):
    """发送短信验证码"""
    # this.host + '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
    def get(self, request, mobile):
        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # 获取此手机号是否发送过短信标记
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '频繁发送短信'})

        # 接收前端数据
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 校验
        if all([image_code_client, uuid]) is False:
            return http.HttpResponseForbidden('缺少必传参数')


        # 获取redis中图形验证码
        image_code_server = redis_conn.get(uuid)
        # 直接将redis中用过的图形验证码删除(让每个图形验证码都是一次性)
        redis_conn.delete(uuid)

        # 判断图形验证码有没有过期
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已过期'})

        # 判断用户输入的图形验证码和redis中之前存储的验证码是否一致
        # 从redis获取出来的数据都是bytes类型
        if image_code_client.lower() != image_code_server.decode().lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码输入错误'})

        # 随机生成一个6位数字来当短信验证码
        sms_code = '%06d' % randint(0, 999999)
        print(sms_code)
        logger.info(sms_code)


        # 创建管道对象(管道作用:就是将多次redis指令合并到一起,一次全部执行)
        pl = redis_conn.pipeline()
        # 把短信验证码存储到redis中以备后期注册时校验
        # redis_conn.setex('sms_code_%s' % mobile, constants.SMS_CODE_EXPIRE_REDIS, sms_code)
        pl.setex('sms_code_%s' % mobile, constants.SMS_CODE_EXPIRE_REDIS, sms_code)
        # 发送过短信后向redis存储一个此手机号发过短信的标记
        # redis_conn.setex('send_flag_%s' % mobile, 60, 1)
        pl.setex('send_flag_%s' % mobile, 60, 1)

        # 执行管道
        pl.execute()

        # # 利用第三方容联云发短信
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_EXPIRE_REDIS // 60], 1)
        send_sms_code.delay(mobile, sms_code)  # 触发异步任务,将异步任务添加到仓库
        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "OK"})

# def func():
#     print(';xxx')
#
#
# func()
#
# a = func
#
# a()
class SMS_CodeView(View):
    """发送短信验证码"""
    # this.host + '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
    # this.host + '/sms_codes/?access_token=' + this.access_token
    def get(self, request):
        access_token = request.GET.get('access_token')
        if access_token is None:
            return http.HttpResponseForbidden('缺少access_token')
        # user = check_verify_mobile_token(access_token)
        serializer = TJW(settings.SECRET_KEY, 3600 * 24)
        data = serializer.loads(access_token.encode())
        # user_id = data.get('user_id')
        mobile = data.get('mobile')
        # if user is None:
        #     return http.HttpResponseForbidden('无效access_token')
        # mobile = access_token.get('mobile')
        # user = generate_verify_mobile_url(request.user)
        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # 获取此手机号是否发送过短信标记
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '频繁发送短信'})


        sms_code = '%06d' % randint(0, 999999)
        print(sms_code)
        logger.info(sms_code)


        # 创建管道对象(管道作用:就是将多次redis指令合并到一起,一次全部执行)
        pl = redis_conn.pipeline()
        # # 把短信验证码存储到redis中以备后期注册时校验
        redis_conn.setex('sms_code_%s' % mobile, constants.SMS_CODE_EXPIRE_REDIS, sms_code)
        pl.setex('sms_code_%s' % mobile, constants.SMS_CODE_EXPIRE_REDIS, sms_code)
        # # 发送过短信后向redis存储一个此手机号发过短信的标记
        # # redis_conn.setex('send_flag_%s' % mobile, 60, 1)
        pl.setex('send_flag_%s' % mobile, 60, 1)

        # 执行管道
        pl.execute()

        # # 利用第三方容联云发短信
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_EXPIRE_REDIS // 60], 1)
        # mobile = mobile
        send_sms_code.delay(mobile, sms_code)  # 触发异步任务,将异步任务添加到仓库
        # 响应
        # return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "OK"})
        return http.JsonResponse({'message': 'OK'})