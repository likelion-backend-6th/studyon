from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import redirect
from chat.models import Room

from manager.models import Study


class ChatRoomMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        room: Room = self.get_room()
        if not request.user in room.study.members.all():
            raise PermissionDenied("Not Authorized to Access")

        return super().dispatch(request, *args, **kwargs)

    def get_room(self):
        room_id = self.kwargs["room_id"]
        room: Room = get_object_or_404(Room, id=room_id)
        return room


def study_access_permission(func):
    def permission_check(request: HttpRequest, study_id):
        if request.user.is_anonymous:
            return redirect("users:login")

        study: Study = get_object_or_404(Study, id=study_id)

        if request.user not in study.members.all():
            raise PermissionDenied("Not Authorized to Access")

        return func(request, study_id)

    return permission_check


def chat_room_access_permission(func):
    def permission_check(request: HttpRequest, room_id):
        if request.user.is_anonymous:
            return redirect("users:login")

        room: Room = get_object_or_404(Room, id=room_id)

        if not request.user in room.study.members.all():
            raise PermissionDenied("Not Authorized to Access")

        return func(request, room_id)

    return permission_check


def chat_room_manage_permission(func):
    def permission_check(request: HttpRequest, room_id):
        if request.user.is_anonymous:
            return redirect("users:login")

        room: Room = get_object_or_404(Room, id=room_id)

        if request.user != room.study.creator:
            raise PermissionDenied("Not Authorized to Access")

        return func(request, room_id)

    return permission_check
