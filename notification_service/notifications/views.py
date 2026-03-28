from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Notification
from .serializers import MarkReadSerializer, NotificationSerializer


class NotificationViewSet(ModelViewSet):
    """
    A ViewSet groups all CRUD operations for a resource under one class.
    We override get_queryset() so every request is automatically scoped
    to a specific user — a critical security boundary.
    """
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """
        Always filter by user_id from query params.
        Returns an empty queryset (not an error) if user_id is missing —
        callers should always supply it.
        """
        user_id = self.request.query_params.get("user_id")
        if not user_id:
            return Notification.objects.none()
        return Notification.objects.filter(user_id=user_id)

    def create(self, request, *args, **kwargs):
        """
        POST /notifications/
        Creates a new notification. Validates input via the serializer
        before touching the database.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # returns 400 with field errors automatically
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        """
        PUT /notifications/{id}/mark-read/
        A custom action — cleaner than a generic PATCH and self-documenting
        in the URL. The @action decorator registers this as a named route.
        """
        notification = self.get_object()  # handles 404 automatically
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification.is_read = serializer.validated_data["is_read"]
        notification.save(update_fields=["is_read"])  # only update the one changed field
        return Response(NotificationSerializer(notification).data, status=status.HTTP_200_OK)