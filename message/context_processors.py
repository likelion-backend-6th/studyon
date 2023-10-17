from .models import Message, Notice


def get_recent_message(request):
    recent_message = Message.objects.filter(reciever=request.user).first()
    return {"recent_message": recent_message}


def get_recent_notice(request):
    recent_notice = Notice.objects.filter(user=request.user).first()
    return {"recent_notice": recent_notice}
