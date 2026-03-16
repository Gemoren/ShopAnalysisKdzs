import base64
import json
import uuid
import random
from io import BytesIO

from captcha.image import ImageCaptcha
from django.core.cache import cache
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from rest_framework_jwt.settings import api_settings

from .models import SysUser, ImportTask


# Create your views here.
class Login(View):

    def post(self, request):
        try:
            data_str = request.body.decode('utf-8')
            data = json.loads(data_str)
        except Exception as e:
            return JsonResponse({'info': '数据格式非法！'}, status=400)

        # 验证码验证
        captcha = data.get('captcha')
        uuid = data.get('uuid')

        if not captcha or not uuid:
            return JsonResponse({'status': False, 'info': '验证码不能为空！'}, status=200)

        # 从缓存中获取验证码
        cached_captcha = cache.get(str(uuid))
        if not cached_captcha:
            return JsonResponse({'status': False, 'info': '验证码已过期，请刷新！'}, status=200)

        # 验证码不区分大小写
        if captcha.lower() != cached_captcha.lower():
            return JsonResponse({'status': False, 'info': '验证码错误！'}, status=200)

        # 验证成功后删除缓存的验证码
        cache.delete(str(uuid))

        try:
            user = SysUser.objects.get(username=data.get('username'), password=data.get('password'))
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 小写快捷键 ctrl + shift + U
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            # 将用户对象传递进去，获取到该对象的属性值
            payload = jwt_payload_handler(user)
            # 将属性值编码成jwt格式的字符串
            token = jwt_encode_handler(payload)
        except Exception as e:
            return JsonResponse({'status': False, 'info': '用户名或者密码错误！'}, status=200)
        return JsonResponse({'status': True, 'token': token, 'info': '登录成功！'}, status=200)


# 通用任务状态查询视图
class GetTaskStatus(View):
    def get(self, request):
        task_id = request.GET.get('task_id')
        if not task_id:
            return JsonResponse({'code': 400, 'errorInfo': '缺少task_id参数'})

        try:
            task = ImportTask.objects.get(task_id=task_id)
            return JsonResponse({
                'code': 200,
                'data': {
                    'task_id': task.task_id,
                    'file_name': task.file_name,
                    'status': task.status,
                    'total_rows': task.total_rows,
                    'processed_rows': task.processed_rows,
                    'error_message': task.error_message,
                    'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else None,
                    'updated_at': task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else None
                }
            })
        except ImportTask.DoesNotExist:
            return JsonResponse({'code': 404, 'errorInfo': '任务不存在'})


class CaptchaView(View):

    def get(self, request):
        characters ='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        data = ''.join(random.sample(characters, 4))
        # print("data", data)
        captcha = ImageCaptcha()
        imageData: BytesIO = captcha.generate(data)
        base64_str = base64.b64encode(imageData.getvalue()).decode()
        # print(type(base64_str), base64_str)
        random_uuid = uuid.uuid4()  # 生成一个随机数
        # print(random_uuid)
        cache.set(random_uuid, data, timeout=300)  # 存到redis缓存中 有效期5分钟
        return JsonResponse({'code': 200, 'base64str': 'data:image/png;base64,'
                                                       + base64_str, 'uuid': random_uuid})
