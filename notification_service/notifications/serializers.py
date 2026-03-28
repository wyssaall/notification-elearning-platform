from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Handles serialization (model → JSON) and deserialization (JSON → validated data).
    read_only_fields ensures clients can't forge timestamps or IDs.
    """

    class Meta:
        model = Notification
        fields = ["id", "user_id", "title", "message", "is_read", "created_at"]
        read_only_fields = ["id", "is_read", "created_at"]


class MarkReadSerializer(serializers.Serializer):
    """
    A dedicated serializer for the mark-as-read action.
    Using a separate serializer for each action keeps each one focused
    and makes API changes safer (open/closed principle).
    """
    is_read = serializers.BooleanField()