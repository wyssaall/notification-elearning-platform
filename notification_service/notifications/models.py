from django.db import models


class Notification(models.Model):
    """
    Represents a single notification sent to a user.
    user_id is an integer FK reference — we don't import the User model
    from another service; we just store the ID. This keeps the service
    fully decoupled (loose coupling is a core microservice principle).
    """
    user_id = models.PositiveIntegerField(db_index=True)  # index speeds up per-user queries
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # set once on creation, never mutated

    class Meta:
        ordering = ["-created_at"]           # newest first by default
        indexes = [
            models.Index(fields=["user_id", "is_read"]),  # compound index for filtered queries
        ]

    def __str__(self):
        return f"[user={self.user_id}] {self.title}"