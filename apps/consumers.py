import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.models import Message
from apps.users import USERS_GROUP, users_snapshot

MAX_MESSAGE = 1000
HISTORY_LIMIT = 50


class Consumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room = self.scope["url_route"]["kwargs"].get("room", "lobby")
        self.group = f"room_{self.room}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        for item in await self.get_history():
            await self.send(text_data=json.dumps(item))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "")
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "JSON yuboring"}))
            return
        message = str(data.get("message", "")).strip()
        if not message:
            await self.send(text_data=json.dumps({"error": "message bo'sh"}))
            return
        if len(message) > MAX_MESSAGE:
            await self.send(text_data=json.dumps({"error": f"message {MAX_MESSAGE} belgidan uzun"}))
            return
        user = self.scope.get("user")
        sender = user.username if user and user.is_authenticated else "anonim"
        await self.save_message(sender, message)
        await self.channel_layer.group_send(
            self.group, {"type": "room.message", "message": message, "sender": sender}
        )

    async def room_message(self, event):
        await self.send(text_data=json.dumps({
            "room": self.room, "sender": event["sender"], "message": event["message"],
        }))

    @database_sync_to_async
    def get_history(self):
        last = Message.objects.filter(room=self.room).order_by("-id")[:HISTORY_LIMIT]
        return [
            {"room": self.room, "sender": m.sender, "message": m.text, "history": True}
            for m in reversed(list(last))
        ]

    @database_sync_to_async
    def save_message(self, sender, text):
        Message.objects.create(room=self.room, sender=sender, text=text)


class UsersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(USERS_GROUP, self.channel_name)
        await self.accept()
        snapshot = await database_sync_to_async(users_snapshot)()
        await self.send(text_data=json.dumps({"event": "snapshot", **snapshot}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(USERS_GROUP, self.channel_name)

    async def users_update(self, event):
        await self.send(text_data=json.dumps({
            "event": event["event"], "username": event["username"],
            "count": event["count"], "users": event["users"],
        }))
