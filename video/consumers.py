import json

from channels.generic.websocket import AsyncWebsocketConsumer


class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "Test-Room"
        self.user = self.scope["user"]

        # 로그인 확인
        if not self.user.is_authenticated:
            self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        receive_dict = json.loads(text_data)
        user = self.scope["user"]
        receive_dict["peer"] = user.username
        action = receive_dict["action"]

        print("peer_username: ", user.username)
        print("action: ", action)
        print("self.channel_name: ", self.channel_name)

        if (action == "new-offer") or (action == "new-answer"):
            # new offer or answer일 경우
            # 각자의 peer에게 전송

            receiver_channel_name = receive_dict["message"]["receiver_channel_name"]

            print("Sending to ", receiver_channel_name)

            # set new receiver as the current sender
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

        await self.send(
            text_data=json.dumps(
                {
                    "peer": this_peer,
                    "action": action,
                    "message": message,
                }
            )
        )
