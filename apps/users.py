from django.contrib.auth import get_user_model

USERS_GROUP = "users"
LATEST_LIMIT = 20


def users_snapshot():
    """Bazadagi userlar soni va oxirgi qo'shilganlar ro'yxati."""
    User = get_user_model()
    latest = User.objects.order_by("-date_joined", "-pk")[:LATEST_LIMIT]
    return {
        "count": User.objects.count(),
        "users": [
            {"id": u.pk, "username": u.username, "date_joined": u.date_joined.isoformat()}
            for u in latest
        ],
    }
