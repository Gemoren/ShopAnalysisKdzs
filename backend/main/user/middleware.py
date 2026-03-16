from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError, DecodeError
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
import traceback


class JwtAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        white_list = ["/user/login", "/user/captcha"]  # 请求白名单
        path = request.path
        if path not in white_list and not path.startswith("/media"):
            # print("要进行token验证")
            token = request.META.get('HTTP_AUTHORIZATION')
            # print("token:", token)
            if not token:
                return HttpResponse('Token不存在，请先登录！')
            # 去除 Bearer 前缀（如果有）
            if token.startswith('Bearer '):
                token = token[7:]
            try:
                jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
                # print("准备解码token...")
                payload = jwt_decode_handler(token)
                # print("payload:", payload)

                # 将用户信息存储到 request 中，供后续使用
                request.user_id = payload.get('user_id') or payload.get('id')
                request.username = payload.get('username')

                # 标记需要刷新 token
                request.should_refresh_token = True

            except ExpiredSignatureError as e:
                print("Token过期异常:", e)
                return HttpResponse('登录过期，请重新登录！', status=401)
            except DecodeError as e:
                print("Token解码异常:", e)
                return HttpResponse('登录过期，请重新登录！', status=401)
            except InvalidTokenError as e:
                print("Token无效异常:", e)
                return HttpResponse('登录过期，请重新登录！', status=401)
            except PyJWTError as e:
                print("JWT异常:", e)
                traceback.print_exc()
                return HttpResponse('登录过期，请重新登录！', status=401)
            except Exception as e:
                print("Token验证异常:", e)
                traceback.print_exc()
                return HttpResponse('登录过期，请重新登录！', status=401)
        else:
            print("不验证验证")
            return None

    def process_response(self, request, response):
        # 如果请求需要刷新 token，则生成新 token 并添加到响应头
        if hasattr(request, 'should_refresh_token') and request.should_refresh_token:
            try:
                # 从数据库重新获取用户对象
                from .models import SysUser
                user = SysUser.objects.get(id=request.user_id)

                # 生成新的 token
                payload = jwt_payload_handler(user)
                new_token = jwt_encode_handler(payload)

                # 将新 token 添加到响应头
                response['Access-Control-Expose-Headers'] = 'Authorization'
                response['Authorization'] = new_token

                # print(f"Token已刷新: {request.username}")
            except Exception as e:
                print(f"Token刷新失败: {e}")
                traceback.print_exc()

        return response
