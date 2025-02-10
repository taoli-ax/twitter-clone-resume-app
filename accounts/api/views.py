from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout
)
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import(
    UserSerializer,
    SignUpSerializer,
    LoginSerializer,
    UserProfileSerializerForUpdate,
    UserSerializerWithProfile
)
from accounts.models import UserProfile
from testing.utils import CsrfExemptSessionAuthentication
from utils.permissions import IsObjectOwner


# Create your views here.
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializerWithProfile
    permission_classes = (permissions.IsAdminUser,)

class UserProfileViewSet(viewsets.GenericViewSet,
                         viewsets.mixins.UpdateModelMixin):
    queryset = UserProfile
    serializer_class = UserProfileSerializerForUpdate
    permission_classes = (IsObjectOwner,)


class AccountViewSet(viewsets.ViewSet):
    """
            定制化的ViewSet视图集，包含4个额外动作
            1. signup
            2. login
            3. logout
            4. login_status
    """
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (CsrfExemptSessionAuthentication,)

    @action(methods=['post'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='POST', block=True))
    def login(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
           return Response({
               "success":False,
                "errors":serializer.errors,
               "message":"please check input",
               }, status=400)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success":False,
                "message":"password or username is incorrect",
            },status=400)
        django_login(request, user)
        return Response({
            "success":True,
            "data":UserSerializer(user).data,
        },status=200)

    @action(methods=['post'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='POST', block=True))
    def signup(self, request, *args, **kwargs):
        # 验证是否已存在
        serializer = SignUpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success':False,
                'errors':serializer.errors,
                'message':'please check input'
            },status=400)
        user = serializer.save()
        # hack! 注册之后注册用户profile
        user.profile
        # 注册之后登录
        django_login(request, user)
        return Response({
            'success':True,
            'data':UserSerializer(user).data,
        },status=201)

    @action(methods=['post'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='POST', block=True))
    def logout(self, request):
        django_logout(request)
        return Response({
            'success':True,
        })

    @action(methods=['get'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='GET', block=True))
    def login_status(self, request):
        data = {"is_logged_in":request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user']=UserSerializer(request.user).data
        return Response(data)
