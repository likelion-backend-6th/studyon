from django.contrib.auth.models import User
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin


class Profile(ExportModelOperationsMixin("profile"), models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)


class Review(ExportModelOperationsMixin("review"), models.Model):
    reviewer = models.ForeignKey(
        User, related_name="reviewers", on_delete=models.CASCADE
    )
    reviewee = models.ForeignKey(
        User, related_name="reviewees", on_delete=models.CASCADE
    )
    score = models.IntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer}의 {self.reviewee}에 대한 리뷰"

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["reviewer"]),
            models.Index(fields=["reviewee"]),
        ]
        ordering = ["-created_at"]
