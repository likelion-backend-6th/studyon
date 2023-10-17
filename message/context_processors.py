from .models import Message, Notice


def get_recent_message(request):
    if request.user.is_authenticated:
        recent_message = Message.objects.filter(reciever=request.user).first()
        return {"recent_message": recent_message}
    else:
        recent_message = None
        return {"recent_message": recent_message}


def get_recent_notice(request):
    if request.user.is_authenticated:
        recent_notice = Notice.objects.filter(user=request.user).first()
        return {"recent_notice": recent_notice}
    else:
        recent_notice = None
        return {"recent_notice": recent_notice}
