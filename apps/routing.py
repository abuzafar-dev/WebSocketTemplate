from django.urls import re_path

from apps import consumers

websocket_urlpatterns = [
    re_path(r"^ws/users/$", consumers.UsersConsumer.as_asgi()),
    re_path(r"^ws/$", consumers.Consumer.as_asgi()),
    re_path(r"^ws/(?P<room>[\w-]{1,50})/$", consumers.Consumer.as_asgi()),
]
