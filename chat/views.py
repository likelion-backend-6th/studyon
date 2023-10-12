from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView

from taggit.models import Tag

from chat.forms import TagsForm


from chat.models import Chat, Room
from chat.permissions import (
    ChatRoomMixin,
    chat_room_access_permission,
    study_access_permission,
)
from manager.models import Study


@study_access_permission
def room_tag_list(request, study_id):
    study = get_object_or_404(Study, pk=study_id)
    tag_list = list(Tag.objects.all().values_list("name", flat=True))
    room_tag_list = list(
        Room.objects.filter(study=study).values_list("tags__name", flat=True)
    )
    return JsonResponse({"tag_list": tag_list, "room_tag_list": room_tag_list})


@study_access_permission
def make_chat_room(request, study_id):
    tags_form = TagsForm(request.POST)
    study = get_object_or_404(Study, id=study_id)

    study_rooms = Room.objects.filter(study=study).count()

    if study_rooms >= 3:
        return HttpResponse("You cannot create more than 3 rooms.")

    if tags_form.is_valid():
        tag_name = tags_form.cleaned_data.get("tag_name")

        room, created = Room.objects.get_or_create(
            study=study, tags__name=tag_name, defaults={"creator": request.user}
        )

        if created:
            room.tags.add(tag_name)

        chat_room_url = reverse("chat:chat_room", kwargs={"room_id": room.id})

        return redirect(chat_room_url)


@chat_room_access_permission
def chat_room(request: HttpRequest, room_id):
    room = get_object_or_404(Room.objects.select_related("study"), id=room_id)
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
        room = get_object_or_404(Room.objects.select_related("study"), id=room_id)
        queryset = Chat.objects.filter(room=room)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = self.kwargs["room_id"]
        room = get_object_or_404(Room.objects.select_related("study"), id=room_id)
        context["room"] = room
        return context
