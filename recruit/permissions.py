from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from recruit.models import Recruit, Register


class ReviewAccessMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        recruit: Recruit = self.get_recruit()
        if request.user != recruit.creator:
            raise PermissionDenied("Not Authorized to Access")

        requester: User = self.get_requester()
        if not Register.objects.filter(recruit=recruit, requester=requester).exists():
            raise PermissionDenied("Not Authorized to Access")
        return super().dispatch(request, *args, **kwargs)

    def get_recruit(self):
        recruit_id = self.kwargs["pk"]
        recruit: Recruit = get_object_or_404(Recruit, id=recruit_id)
        return recruit

    def get_requester(self):
        requester_id = self.kwargs["user_id"]
        requester: User = get_object_or_404(User, id=requester_id)
        return requester
