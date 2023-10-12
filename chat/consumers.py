from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from chat.models import Chat, Room


class ChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self):
        super().__init__()
        self.group_name = ""
        self.room = None

    async def connect(self):
        user = self.scope["user"]
        room_id = self.scope["url_route"]["kwargs"]["room_id"]

        if not user.is_authenticated:
            self.close()

        try:
            self.room = await self.get_room_by_room_id(room_id)
            study_members = await self.get_study_members_by_room(self.room)
            study_member_list = study_members
            if user not in study_member_list:
                self.close()
        except Room.DoesNotExist:
            self.close()
        else:
            self.group_name = self.room.chat_group_name

            await self.channel_layer.group_add(self.group_name, self.channel_name)

            await self.accept()

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        user = self.scope["user"]
        _type = content["type"]

        if _type == "chat.message":
            sender = user.username
            message = content["message"]
            room_id = self.scope["url_route"]["kwargs"]["room_id"]
            chat = await self.save_message(
                username=sender, room_id=room_id, content=message
            )
            message_dict = {
                "type": "chat.message",
                "message": message,
                "sender": sender,
                "datetime": chat.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            await self.channel_layer.group_send(
                self.group_name,
                message_dict,
            )
        else:
            print(f"Invalid message type : {_type}")

    async def chat_message(self, message_dict):
        await self.send_json(
            {
                "type": "chat.message",
                "message": message_dict["message"],
                "sender": message_dict["sender"],
                "datetime": message_dict["datetime"],
            }
        )

    @database_sync_to_async
    def save_message(self, username, room_id, content):
        user = User.objects.get(username=username)
        room = Room.objects.get(id=room_id)
        chat = Chat.objects.create(creator=user, room=room, content=content)
        return chat

    @database_sync_to_async
    def get_room_by_room_id(self, room_id):
        room = get_object_or_404(Room, id=room_id)
        return room

    @database_sync_to_async
    def get_study_members_by_room(self, room):
        study_members = room.study.members.all()
        return study_members
