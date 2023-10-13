from .models import Message, Notice


def get_recent_message(self):
    recent_message = Message.objects.first()
    return {"recent_message": recent_message}


def get_recent_notice(self):
    recent_notice = Notice.objects.first()
    return {"recent_notice": recent_notice}
