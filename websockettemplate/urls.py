from django.contrib import admin
from django.urls import path

from apps.views import chat_page, users_page

urlpatterns = [
    path('', users_page, name='users'),
    path('chat/', chat_page, name='chat'),
    path('chat/<slug:room>/', chat_page, name='chat-room'),
    path('admin/', admin.site.urls),
]
