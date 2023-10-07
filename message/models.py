from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="senders")
    reciever = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recievers"
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
            models.Index(fields=["reciever"]),
        ]
        ordering = ["-created_at"]
