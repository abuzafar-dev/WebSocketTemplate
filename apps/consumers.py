import json

from channels.generic.websocket import AsyncWebsocketConsumer


class Consumer(AsyncWebsocketConsumer):
    """Xona (room) bo'yicha xabar tarqatuvchi consumer.

    ws://host/ws/<room>/ ga ulangan barcha mijozlar bir-birining xabarini oladi.
    """

    async def connect(self):
        self.room = self.scope["url_route"]["kwargs"].get("room", "lobby")
        self.group = f"room_{self.room}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

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
        user = self.scope.get("user")
        sender = user.username if user and user.is_authenticated else "anonim"
        await self.channel_layer.group_send(
            self.group, {"type": "room.message", "message": message, "sender": sender}
        )

    async def room_message(self, event):
        await self.send(text_data=json.dumps({
            "room": self.room, "sender": event["sender"], "message": event["message"],
        }))
