from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    这个类检查请求的User是不是评论(obj)的user, request.user==obj.user
    detail=False 只会检查 has_permission
    detail=True 会检查 has_permission 和 has_object_permission
    返回 True之后会放行 如果验证出错，会返回 message的消息
    """
    message = 'you dont have permission to access this object'

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return True