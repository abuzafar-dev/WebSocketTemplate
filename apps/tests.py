import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from asgiref.sync import async_to_sync
from channels.layers import channel_layers
from channels.testing import WebsocketCommunicator
from django.test import SimpleTestCase, override_settings

IN_MEMORY_LAYER = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}


@override_settings(CHANNEL_LAYERS=IN_MEMORY_LAYER, ALLOWED_HOSTS=["localhost"])
class WebSocketOriginTests(SimpleTestCase):
    def setUp(self):
        channel_layers.backends.clear()  # override qilingan in-memory qatlam ishlatilsin

    def connects(self, origin):
        from websockettemplate.asgi import application

        async def attempt():
            headers = [(b"host", b"localhost")]
            if origin is not None:
                headers.append((b"origin", origin))
            communicator = WebsocketCommunicator(application, "/ws/", headers=headers)
            connected, _ = await communicator.connect()
            await communicator.disconnect()
            return connected

        return async_to_sync(attempt)()

    def test_foreign_origin_rejected(self):
        self.assertFalse(self.connects(b"https://evil.example"))

    def test_same_host_origin_allowed(self):
        self.assertTrue(self.connects(b"http://localhost"))


class ProductionDefaultsTests(SimpleTestCase):
    def test_debug_off_and_no_wildcard_host_when_env_missing(self):
        root = Path(__file__).resolve().parent.parent
        copy = Path(tempfile.mkdtemp()) / "project"
        shutil.copytree(root, copy, ignore=shutil.ignore_patterns(".env", ".git"))
        env = {k: v for k, v in os.environ.items() if k not in ("DEBUG", "ALLOWED_HOSTS")}
        env.update(SECRET_KEY="x" * 50, DJANGO_SETTINGS_MODULE="websockettemplate.settings")
        code = "from django.conf import settings as s; print(s.DEBUG, s.ALLOWED_HOSTS)"
        result = subprocess.run([sys.executable, "-c", code], cwd=copy, env=env, capture_output=True, text=True)
        self.assertEqual(result.stdout.strip(), "False ['localhost', '127.0.0.1']", result.stderr)
