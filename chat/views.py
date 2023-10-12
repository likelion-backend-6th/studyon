from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from taggit.models import Tag

from chat.forms import TagsForm


from chat.models import Room
from manager.models import Study


def room_tag_list(request, study_id):
    study = get_object_or_404(Study, pk=study_id)
    tag_list = list(Tag.objects.all().values_list("name", flat=True))
    room_tag_list = list(
        Room.objects.filter(study=study).values_list("tags__name", flat=True)
    )
    return JsonResponse({"tag_list": tag_list, "room_tag_list": room_tag_list})


def make_chat_room(request, study_id):
    tags_form = TagsForm(request.POST)
    study = get_object_or_404(Study, id=study_id)

    study_rooms = Room.objects.filter(study=study).count()

    if study_rooms >= 3:
        return HttpResponse("You cannot create more than 3 rooms.")

    if tags_form.is_valid():
        tag_name = tags_form.data.get("tag_name")
        tag_id = tags_form.cleaned_data.get("tag_name")

        room, created = Room.objects.get_or_create(
            study=study, tags__name=tag_name, defaults={"creator": request.user}
        )

        if created:
            room.tags.add(tag_name)

        chat_room_url = reverse(
            "chat:chat_room", kwargs={"study_id": study_id, "tag_id": tag_id}
        )

        return redirect(chat_room_url)


def chat_room(request: HttpRequest, study_id, tag_id):
    room = get_object_or_404(Room, study_id=study_id, tags__id=tag_id)
    print(f"room:{room}")
    return render(
        request,
        "chat/room.html",
        {
            "room": room,
        },
    )
