from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "user_id", "title", "message", "is_read", "created_at"]
        read_only_fields = ["id", "is_read", "created_at"]


class MarkReadSerializer(serializers.Serializer):
    is_read = serializers.BooleanField()