from django.contrib.contenttypes.models import ContentType
from likes.models import Likes


class LikesService:
    @classmethod
    def has_liked(cls,user, obj):
        if user.is_anonymous:
            return  False
        # 查询对象的likes是否已存在，说人话：查看某个用户是否已点赞了tweet或comment
        return Likes.objects.filter(
            content_type=ContentType.objects.get_for_model(obj.__class__),
            object_id = obj.id,
            user = user
        ).exists()
