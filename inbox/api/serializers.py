from rest_framework import serializers

from notifications.models import Notification

from accounts.api.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(source='cached_user')
    class Meta:
        model = Notification
        fields=(
            'id',
            'recipient',
            'unread',
            'verb',
            'timestamp',
            'actor_content_type',
            'actor_object_id',
            'target_content_type',
            'target_object_id',
            'action_object_content_type',
            'action_object_object_id',
        )

class NotificationSerializerForUpdate(serializers.ModelSerializer):
    unread = serializers.BooleanField()

    class Meta:
        model = Notification
        fields=('unread',)

    def update(self, instance, validated_data):
        # 虽然父类的update也可以实现，但是这样写更加明确要修改的字段
        instance.unread = validated_data['unread']
        instance.save()
        return instance
