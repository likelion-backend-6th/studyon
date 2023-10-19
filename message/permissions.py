from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from manager.models import Study
from message.models import Message, Notice


class NoticeAccessMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        notice: Notice = self.get_notice()
        if request.user != notice.user:
            raise PermissionDenied("Not Authorized to Access")
        return super().dispatch(request, *args, **kwargs)

    def get_notice(self):
        notice_id = self.kwargs["pk"]
        notice: Notice = get_object_or_404(User, id=notice_id)
        return notice


class MessageSendMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        receiver: User = self.get_receiver()
        shared_study = Study.objects.filter(members__in=[request.user, receiver])
        if not shared_study.exists():
            raise PermissionDenied("Not Authorized to Access")
        return super().dispatch(request, *args, **kwargs)

    def get_receiver(self):
        receiver_id = self.kwargs["user_id"]
        receiver: User = get_object_or_404(User, id=receiver_id)
        return receiver


class MessageAccessMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        message: Message = self.get_message()
        if request.user != message.reciever:
            raise PermissionDenied("Not Authorized to Access")
        return super().dispatch(request, *args, **kwargs)

    def get_message(self):
        pk = self.kwargs["pk"]
        message: Message = get_object_or_404(Message, id=pk)
        return message
