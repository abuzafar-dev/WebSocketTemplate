from channels.testing import WebsocketCommunicator
from django.test import TestCase

from config.asgi import application


class ChatConsumerTests(TestCase):
    async def connect(self, room='python'):
        communicator = WebsocketCommunicator(
            application, f'/ws/chat/{room}/', headers=[(b'origin', b'http://localhost')]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        return communicator

    async def test_message_is_sent_to_room(self):
        first = await self.connect()
        second = await self.connect()
        await first.send_json_to({'message': 'Salom', 'username': 'Ali'})
        self.assertEqual(await second.receive_json_from(), {'message': 'Salom', 'username': 'Ali'})
        await first.disconnect()
        await second.disconnect()

    async def test_other_room_does_not_receive(self):
        first = await self.connect('python')
        other = await self.connect('django')
        await first.send_json_to({'message': 'Salom', 'username': 'Ali'})
        self.assertTrue(await other.receive_nothing())
        await first.disconnect()
        await other.disconnect()

    async def test_empty_message_ignored(self):
        communicator = await self.connect()
        await communicator.send_json_to({'message': '   '})
        self.assertTrue(await communicator.receive_nothing())
        await communicator.disconnect()

    async def test_wrong_origin_rejected(self):
        communicator = WebsocketCommunicator(
            application, '/ws/chat/python/', headers=[(b'origin', b'http://evil.com')]
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)


class PagesTests(TestCase):
    def test_index(self):
        self.assertEqual(self.client.get('/').status_code, 200)

    def test_room(self):
        response = self.client.get('/chat/python/')
        self.assertContains(response, 'python')
