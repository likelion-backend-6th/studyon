import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from manager.models import Study
from .models import Notice


class NoticeConsumer(AsyncWebsocketConsumer):
    # 연결
    async def connect(self):
        self.room_group_name = "notice"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    # 연결해제
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # 알림 받기
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json["content"]

        # 스터디 관련 알림
        if (
            "study_id" in text_data_json.keys()
            and "username" not in text_data_json.keys()
        ):
            study_id = text_data_json["study_id"]
            user_ids = await self.get_members_not_creator(study_id)

            await self.set_notice_to_db_not_creator(study_id=study_id, content=content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_notice", "user_ids": user_ids, "content": content},
            )
        if "study_id" in text_data_json.keys() and "username" in text_data_json.keys():
            study_id = text_data_json["study_id"]
            username = text_data_json["username"]
            user_ids = await self.get_members_not_request_user(study_id, username)

            await self.set_notice_to_db_not_request_user(
                study_id=study_id, content=content, username=username
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_notice", "user_ids": user_ids, "content": content},
            )

        # 메세지 알림
        if "reciever_id" in text_data_json.keys():
            reciever_id = text_data_json["reciever_id"]

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_notice", "reciever_id": reciever_id, "content": content},
            )

    async def send_notice(self, event):
        await self.send(text_data=json.dumps(event))

    # 알림 보낼 스터디원 분류
    # 스터디 장을 제외한 스터디원
    @database_sync_to_async
    def get_members_not_creator(self, study_id):
        study = get_object_or_404(Study, id=study_id)
        user_ids = [
            member.id for member in study.members.all() if member != study.creator
        ]
        return user_ids

    # 요청자를 제외한 스터디원
    @database_sync_to_async
    def get_members_not_request_user(self, study_id, username):
        study = get_object_or_404(Study, id=study_id)
        user_ids = [
            member.id for member in study.members.all() if member.username != username
        ]
        return user_ids

    # 알림 정보 db 저장
    # 스터디 장을 제외한 스터디원
    @database_sync_to_async
    def set_notice_to_db_not_creator(self, study_id, content):
        study = get_object_or_404(Study, id=study_id)
        for user in study.members.all():
            if user != study.creator:
                Notice.objects.create(user=user, content=content)

    # 요청자를 제외한 스터디원
    @database_sync_to_async
    def set_notice_to_db_not_request_user(self, study_id, content, username):
        study = get_object_or_404(Study, id=study_id)
        for user in study.members.all():
            if user.username != username:
                Notice.objects.create(user=user, content=content)
