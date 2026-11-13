from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.users import USERS_GROUP, users_snapshot


def broadcast_users(event, username):
    layer = get_channel_layer()
    if layer is None:
        return
    async_to_sync(layer.group_send)(USERS_GROUP, {
        "type": "users.update", "event": event, "username": username, **users_snapshot(),
    })


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def user_added(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: broadcast_users("added", instance.username))


@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def user_removed(sender, instance, **kwargs):
    transaction.on_commit(lambda: broadcast_users("removed", instance.username))
