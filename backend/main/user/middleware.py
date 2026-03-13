from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError, DecodeError
from rest_framework_jwt.settings import api_settings
import traceback


class JwtAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        white_list = ["/user/login"]  # 请求白名单
        path = request.path
        if path not in white_list and not path.startswith("/media"):
            print("要进行token验证")
            token = request.META.get('HTTP_AUTHORIZATION')
            print("token:", token)
            if not token:
                return HttpResponse('Token不存在，请先登录！')
            # 去除 Bearer 前缀（如果有）
            if token.startswith('Bearer '):
                token = token[7:]
            try:
                jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
                print("准备解码token...")
                payload = jwt_decode_handler(token)
                print("payload:", payload)
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
