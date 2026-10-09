import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websockettemplate.settings")
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import apps.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # Origin ALLOWED_HOSTS bilan tekshiriladi: boshqa sayt foydalanuvchining sessiya
    # cookie'si bilan WebSocket ochib, uning nomidan ishlay olmaydi (CSWSH).
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(apps.routing.websocket_urlpatterns)
        )
    ),
})