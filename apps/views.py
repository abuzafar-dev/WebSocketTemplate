from django.shortcuts import render

from apps.users import users_snapshot


def users_page(request):
    return render(request, "apps/users.html", users_snapshot())


def chat_page(request, room="lobby"):
    return render(request, "apps/chat.html", {"room": room})
