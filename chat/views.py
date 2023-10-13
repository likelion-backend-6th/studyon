from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView

from chat.forms import CategoryForm


from chat.models import Chat, Room
from chat.permissions import (
    ChatRoomMixin,
    chat_room_access_permission,
    study_access_permission,
)
from manager.models import Study


@study_access_permission
def make_chat_room(request, study_id):
    category_form = CategoryForm(request.POST)
    study = get_object_or_404(Study, id=study_id)

    study_rooms = Room.objects.filter(study=study, closed_at=None).count()
    if study_rooms >= 3:
        return HttpResponse("You cannot create more than 3 rooms.")

    if category_form.is_valid():
        category = category_form.cleaned_data.get("category")

        room, created = Room.objects.get_or_create(
            study=study, category=category, defaults={"creator": request.user}
        )

        chat_room_url = reverse("chat:chat_room", kwargs={"room_id": room.id})

        return redirect(chat_room_url)


@chat_room_access_permission
def chat_room(request: HttpRequest, room_id):
    room = get_object_or_404(
        Room.objects.select_related("study"), id=room_id, closed_at=None
    )
    chats = Chat.objects.filter(room=room)
    return render(
        request,
        "chat/room.html",
        {
            "room": room,
            "chats": chats,
        },
    )


class ChatRoomView(ChatRoomMixin, ListView):
    model = Chat
    template_name = "chat/room.html"
    context_object_name = "chats"
    paginate_by = 30

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        room = get_object_or_404(
            Room.objects.select_related("study"), id=room_id, closed_at=None
        )
        queryset = Chat.objects.filter(room=room)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = self.kwargs["room_id"]
        room = get_object_or_404(
            Room.objects.select_related("study"), id=room_id, closed_at=None
        )
        context["room"] = room
        return context
