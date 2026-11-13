import json

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase

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


class UsersSocketTests(TransactionTestCase):
    async def connect(self):
        comm = WebsocketCommunicator(application, "/ws/users/")
        connected, _ = await comm.connect()
        self.assertTrue(connected)
        return comm

    async def test_snapshot_shows_count_from_database(self):
        await database_sync_to_async(get_user_model().objects.create_user)("ali")
        comm = await self.connect()
        data = json.loads(await comm.receive_from())
        self.assertEqual(data["event"], "snapshot")
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["users"][0]["username"], "ali")
        await comm.disconnect()

    async def test_new_user_is_broadcast(self):
        comm = await self.connect()
        self.assertEqual(json.loads(await comm.receive_from())["count"], 0)
        await database_sync_to_async(get_user_model().objects.create_user)("vali")
        data = json.loads(await comm.receive_from())
        self.assertEqual(data["event"], "added")
        self.assertEqual(data["username"], "vali")
        self.assertEqual(data["count"], 1)
        await comm.disconnect()

    async def test_deleted_user_is_broadcast(self):
        user = await database_sync_to_async(get_user_model().objects.create_user)("gani")
        comm = await self.connect()
        await comm.receive_from()
        await database_sync_to_async(user.delete)()
        data = json.loads(await comm.receive_from())
        self.assertEqual((data["event"], data["count"]), ("removed", 0))
        await comm.disconnect()


class UsersPageTests(TestCase):
    def test_page_shows_count(self):
        get_user_model().objects.create_user("ali")
        response = self.client.get("/")
        self.assertContains(response, 'id="count">1<')
        self.assertContains(response, "ali")


class ChatHistoryTests(TransactionTestCase):
    async def connect(self, path):
        comm = WebsocketCommunicator(application, path)
        connected, _ = await comm.connect()
        self.assertTrue(connected)
        return comm

    async def test_message_is_saved(self):
        from apps.models import Message
        comm = await self.connect("/ws/tarix/")
        await comm.send_to(text_data=json.dumps({"message": "saqlansin"}))
        await comm.receive_from()
        await comm.disconnect()
        count = await database_sync_to_async(Message.objects.filter(room="tarix", text="saqlansin").count)()
        self.assertEqual(count, 1)

    async def test_history_sent_on_connect(self):
        a = await self.connect("/ws/tarix/")
        await a.send_to(text_data=json.dumps({"message": "birinchi"}))
        await a.receive_from()
        await a.disconnect()
        b = await self.connect("/ws/tarix/")
        data = json.loads(await b.receive_from())
        self.assertEqual((data["message"], data["history"]), ("birinchi", True))
        await b.disconnect()

    async def test_history_is_per_room(self):
        a = await self.connect("/ws/x/")
        await a.send_to(text_data=json.dumps({"message": "faqat x"}))
        await a.receive_from()
        await a.disconnect()
        b = await self.connect("/ws/y/")
        self.assertTrue(await b.receive_nothing())
        await b.disconnect()

    async def test_too_long_message_rejected(self):
        comm = await self.connect("/ws/")
        await comm.send_to(text_data=json.dumps({"message": "a" * 1001}))
        self.assertIn("error", json.loads(await comm.receive_from()))
        await comm.disconnect()


class ChatPageTests(TestCase):
    def test_chat_page(self):
        response = self.client.get("/chat/python/")
        self.assertContains(response, 'const ROOM = "python"')
