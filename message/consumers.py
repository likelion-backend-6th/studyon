import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
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
        data_keys = text_data_json.keys()

        # 스터디 관련 알림
        if "study_id" in data_keys and "username" not in data_keys:
            study_id = text_data_json["study_id"]
            user_ids = await self.get_members_not_creator(study_id)

            if "db_save" in data_keys:
                db_save = text_data_json["db_save"]
            else:
                db_save = True

            if db_save:
                await self.set_notice_to_db_not_creator(
                    study_id=study_id, content=content
                )

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_notice", "user_ids": user_ids, "content": content},
            )
        if "study_id" in data_keys and "username" in data_keys:
            study_id = text_data_json["study_id"]
            username = text_data_json["username"]
            user_ids = await self.get_members_not_request_user(study_id, username)

            if "db_save" in data_keys:
                db_save = text_data_json["db_save"]
            else:
                db_save = True

            if db_save:
                await self.set_notice_to_db_not_request_user(
                    study_id=study_id, content=content, username=username
                )

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_notice", "user_ids": user_ids, "content": content},
            )

        # 메세지 알림
        if "receiver_id" in data_keys:
            receiver_id = text_data_json["receiver_id"]

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_notice", "receiver_id": receiver_id, "content": content},
            )

        # 일반 알림만
        if "user_id" in data_keys:
            user_id = text_data_json["user_id"]

            await self.set_notice_to_db(content=content, user_id=user_id)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_notice", "user_id": user_id, "content": content},
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

    # 일반 알림 저장
    @database_sync_to_async
    def set_notice_to_db(self, content, user_id):
        user = get_object_or_404(User, id=user_id)
        Notice.objects.create(user=user, content=content)
