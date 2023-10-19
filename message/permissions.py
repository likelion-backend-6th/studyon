from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from manager.models import Study


class MessageAccessMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        receiver: User = self.get_receiver()
        shared_study = Study.objects.filter(members__in=[request.user, receiver])
        if not shared_study.exists():
            raise PermissionDenied("Not Authorized to Access")
        return super().dispatch(request, *args, **kwargs)

    def get_receiver(self):
        recruit_id = self.kwargs["user_id"]
        receiver: User = get_object_or_404(User, id=recruit_id)
        return receiver
