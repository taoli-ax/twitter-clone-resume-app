from rest_framework import status
from rest_framework.views import exception_handler as drf_exception_handler
from django_ratelimit.exceptions import Ratelimited

def exception_handler(exc, context):
    # 获取默认的报错响应,再包装一下
    response = drf_exception_handler(exc, context)
    if isinstance(exc, Ratelimited):
        response.data['detail'] = 'Too many requests, try again later'
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS

    return response
