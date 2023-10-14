from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Room


@receiver(post_save, sender=Room)
def room_on_post_save(sender, instance, **kwargs):
    if instance.closed_at:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            instance.chat_group_name,
            {
                "type": "chat.room.delete",
            },
        )
