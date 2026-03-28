from django.db import models


class Notification(models.Model):
    """In-app notification; user_id is an opaque ID from another service (no cross-DB FK)."""

    user_id = models.PositiveIntegerField(db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_id", "is_read"]),
        ]

    def __str__(self):
        return f"[user={self.user_id}] {self.title}"