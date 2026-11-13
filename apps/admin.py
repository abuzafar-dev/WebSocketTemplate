from django.contrib import admin

from apps.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("room", "sender", "text", "created_at")
    list_filter = ("room",)
    search_fields = ("text", "sender")
