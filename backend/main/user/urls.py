from django.urls import path
from .views import Login, GetTaskStatus, CaptchaView

urlpatterns = [
    path('login', Login.as_view(), name='login'),  # 登录
    path('task_status', GetTaskStatus.as_view(), name='task_status'),  # 任务状态查询
    path('captcha', CaptchaView.as_view(), name='captcha'),  # 验证码
]
