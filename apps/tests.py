import json

from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase

from websockettemplate.asgi import application


class ConsumerTests(TransactionTestCase):
    async def connect(self, path):
        comm = WebsocketCommunicator(application, path)
        connected, _ = await comm.connect()
        self.assertTrue(connected)
        return comm

    async def test_default_room_connects(self):
        comm = await self.connect("/ws/")
        await comm.send_to(text_data=json.dumps({"message": "salom"}))
        data = json.loads(await comm.receive_from())
        self.assertEqual(data, {"room": "lobby", "sender": "anonim", "message": "salom"})
        await comm.disconnect()

    async def test_message_broadcast_to_same_room(self):
        a = await self.connect("/ws/python/")
        b = await self.connect("/ws/python/")
        await a.send_to(text_data=json.dumps({"message": "hammaga"}))
        self.assertEqual(json.loads(await a.receive_from())["message"], "hammaga")
        self.assertEqual(json.loads(await b.receive_from())["message"], "hammaga")
        await a.disconnect()
        await b.disconnect()

    async def test_other_room_does_not_receive(self):
        a = await self.connect("/ws/a/")
        b = await self.connect("/ws/b/")
        await a.send_to(text_data=json.dumps({"message": "faqat a"}))
        await a.receive_from()
        self.assertTrue(await b.receive_nothing())
        await a.disconnect()
        await b.disconnect()

    async def test_invalid_json_returns_error(self):
        comm = await self.connect("/ws/")
        await comm.send_to(text_data="bu json emas")
        self.assertIn("error", json.loads(await comm.receive_from()))
        await comm.disconnect()

    async def test_empty_message_returns_error(self):
        comm = await self.connect("/ws/")
        await comm.send_to(text_data=json.dumps({"message": "  "}))
        self.assertIn("error", json.loads(await comm.receive_from()))
        await comm.disconnect()
