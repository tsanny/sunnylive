import json
from collections import defaultdict
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from core.models import Stream

User = get_user_model()


class CommentConsumer(AsyncWebsocketConsumer):
    connected_clients = defaultdict(set)

    async def connect(self):
        self.group_name = self.scope["url_route"]["kwargs"]["stream_id"]
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.group_name, str(self.channel_name))
        await self.accept()

        CommentConsumer.connected_clients[self.group_name].add(self.user.username)
        await self.send_connected_clients()
        await self.send_group_connected_clients()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        CommentConsumer.connected_clients[self.group_name].remove(self.user.username)
        await self.send_group_connected_clients()

    # May not be needed since we're submitting comments from http POST endpoint

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        if not await self.valid_message(self.user, self.group_name, message):
            return

        # Prevent anonymous users from sending messages
        if self.user.is_anonymous:
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_message",
                "message": message,
                "user": {
                    "username": self.user.username,
                    "id": str(self.user.id),
                },
            },
        )

    @sync_to_async
    def valid_message(self, user_id, stream_id, content):
        author = User.objects.get(username=user_id)
        if author is None:
            return False
        stream = Stream.objects.get(pk=stream_id)
        if stream is None:
            return False
        if not stream.is_live:
            return False
        return True

    async def send_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "is_donation": False,
                    "message": event["message"],
                    "username": event["user"]["username"],
                }
            )
        )

    async def send_donation(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "is_donation": True,
                    "message": event["message"],
                    "amount": event["amount"],
                    "username": event["user"]["username"],
                }
            )
        )

    async def send_connected_clients(self):
        await self.send(
            text_data=json.dumps(
                {
                    "connected_clients": list(
                        CommentConsumer.connected_clients[self.group_name]
                    ),
                }
            )
        )

    async def send_group_connected_clients(self):
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "group_connected_clients",
            },
        )

    async def group_connected_clients(self, event):
        await self.send_connected_clients()
