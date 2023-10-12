from django.core.exceptions import ObjectDoesNotExist
from django.http import (
    HttpResponseServerError,
    HttpResponseNotFound,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import reverse
from taggit.utils import parse_tags

from chat.models import Room, Chat
from manager.models import Study


# Create your views here.
def study_chat(request, study_id):
    try:
        study = Study.objects.get(id=study_id)
        study_rooms = Room.objects.filter(study=study).count()

        if study_rooms >= 3:
            return HttpResponse("You cannot create more than 3 rooms.")

        if "tags" in request.POST:
            tags = parse_tags(request.POST["tags"])

            room, created = Room.objects.get_or_create(
                study=study, defaults={"creator": request.user}
            )
            if created:
                room.tags.add(*tags)
        else:
            return HttpResponse("Tags are required to create or join a room.")

        chats = Chat.objects.filter(room=room).order_by("created_at")[:50]
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Study not found")
    except Room.DoesNotExist:
        return HttpResponseNotFound("Room not found")
    except Exception as e:
        return HttpResponseServerError(str(e))
    return render(
        request,
        "chat/room.html",
        {"study": study, "chats": chats},
    )
