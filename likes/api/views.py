from likes.api.serializers import LikesSerializer, LikeSerializerForCreate
from likes.models import Likes
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from tweets.utils.decotators import required_params


class LikesViewSet(GenericViewSet):
    queryset = Likes.objects.all()
    serializer_class = LikeSerializerForCreate
    permission_classes = [IsAuthenticated]

    @required_params(query_attr='data', params=['content_type','object_id'])
    def create(self, request, *args, **kwargs):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return  Response({
                "success": False,
                "error": serializer.errors,
                "message":"please check input."
            })
        instance = serializer.save()
        return Response(
            LikesSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )


