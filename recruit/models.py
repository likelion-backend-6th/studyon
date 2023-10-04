from django.contrib.auth.models import User
from django.db import models
from taggit.managers import TaggableManager

from manager.models import File, Study


class Recruit(models.Model):
    study = models.OneToOneField(
        Study, on_delete=models.CASCADE, related_name="recruits"
    )
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="creator_recruits"
    )
    title = models.CharField(max_length=100)
    tags = TaggableManager()
    deadline = models.DateField()
    start = models.DateField()
    end = models.DateField()
    total_seats = models.IntegerField(default=1)
    members = models.ManyToManyField(User, related_name="members_recruits")
    target = models.TextField()
    process = models.TextField()
    info = models.TextField(null=True)
    like_users = models.ManyToManyField(User, related_name="likeusers_recruits")
    files = models.ManyToManyField(File, related_name="recruits", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.creator}의 모집글 {self.title}"

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["study"]),
        ]
        ordering = ["-created_at"]


class Register(models.Model):
    recruit = models.ForeignKey(
        Recruit, on_delete=models.CASCADE, related_name="registers"
    )
    requester = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="registers"
    )
    content = models.TextField()
    is_joined = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requester}의 {self.recruit}에 대한 신청"

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
        ]
        ordering = ["-created_at"]
