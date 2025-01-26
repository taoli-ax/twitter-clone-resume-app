from functools import wraps
from rest_framework.response import Response

def required_params(method:str='GET', params=None):
    if params is None:
        params = []

    def decorated(func):
        @wraps(func)
        def _wrapper(instance,request,*args, **kwargs):
            # add支持post方式
            if method.lower() == 'get':
                data = request.query_params
            else:
                data = request.data

            for param in params:
                if param not in data:
                    return Response({
                        "message": "param {} is required".format(param)
                    },status=400)
            return func(instance,request,*args, **kwargs)
        return _wrapper
    return decorated

