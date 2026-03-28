from django.http import JsonResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from notifications.views import NotificationViewSet


def health(request):
    return JsonResponse({"status": "ok"})


router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("health/", health),
    path("api/v1/", include(router.urls)),
]