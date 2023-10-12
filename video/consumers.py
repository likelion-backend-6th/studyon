import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from manager.models import Study


class VideoConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def _check_authenticated(self, study_id, user):
        # 로그인 확인
        if not user.is_authenticated:
            self.close()
            return

        # 스터디 멤버 확인
        if not Study.objects.filter(id=study_id, members=user).exists():
            self.close()

    async def connect(self):
        study_id = self.scope["url_route"]["kwargs"]["study_id"]
        self.room_group_name = f"study_room_{study_id}"
        self.user = self.scope["user"]

        await self._check_authenticated(study_id, self.user)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        receive_dict = {
            "peer": self.user.username,
            "action": "disconnect",
            "message": {
                "receiver_channel_name": self.channel_name,
            },
        }
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send.sdp",
                "receive_dict": receive_dict,
            },
        )

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        receive_dict = json.loads(text_data)

        action = receive_dict["action"]

        receive_dict["peer"] = self.user.username

        if (action == "new-offer") or (action == "new-answer"):
            # new offer or answer일 경우
            # 각자의 peer에게 전송

            receiver_channel_name = receive_dict["message"]["receiver_channel_name"]

            # 수신자 정보 변경
            receive_dict["message"]["receiver_channel_name"] = self.channel_name

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    "type": "send.sdp",
                    "receive_dict": receive_dict,
                },
            )
            return

        # 수신자 데이터를 추가하여 전송
        receive_dict["message"]["receiver_channel_name"] = self.channel_name

        # send to all peers
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send.sdp",
                "receive_dict": receive_dict,
            },
        )

    async def send_sdp(self, event):
        receive_dict = event["receive_dict"]

        this_peer = receive_dict["peer"]
        action = receive_dict["action"]
        message = receive_dict["message"]

        if this_peer != self.user.username:
            await self.send(
                text_data=json.dumps(
                    {
                        "peer": this_peer,
                        "action": action,
                        "message": message,
                    }
                )
            )
