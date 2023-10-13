from django.db import models
from django.contrib.auth.models import User

from manager.models import Study


class Room(models.Model):
    class CategoryChoices(models.IntegerChoices):
        계획 = 1
        진행 = 2
        질의응답 = 3
        리뷰 = 4
        기타 = 5

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="rooms")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
    category = models.IntegerField(choices=CategoryChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.study}의 채팅방 : {self.category}"

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["study"]),
        ]
        ordering = ["-created_at"]

    @property
    def chat_group_name(self):
        return self.make_chat_group_name(room=self)

    @staticmethod
    def make_chat_group_name(room=None, room_pk=None):
        return f"chat-{room_pk or room.pk}"


class Chat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="chats")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["room"]),
        ]
        ordering = ["-created_at"]
