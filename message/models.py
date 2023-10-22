from django.contrib.auth.models import User
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin


class Message(ExportModelOperationsMixin("message"), models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="senders")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receivers"
    )
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["sender"]),
            models.Index(fields=["receiver"]),
        ]
        ordering = ["-created_at"]


class Notice(ExportModelOperationsMixin("notice"), models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notices")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user"]),
        ]
        ordering = ["-created_at"]
