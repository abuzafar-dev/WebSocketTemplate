# WebSocket Template

A minimal Django + Channels starter for real-time features: an ASGI
application that serves HTTP and WebSocket side by side, with a Redis channel
layer so messages can be broadcast across multiple server processes.

## Stack

- Django 6.1 + Channels 4.3 (ASGI)
- Daphne as the ASGI server
- Redis via `channels_redis` (channel layer)
- PostgreSQL (psycopg 3)

## Getting started

Redis and PostgreSQL must be running first:

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env          # then set SECRET_KEY and the DB credentials

.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

`runserver` picks up Daphne automatically because `channels` is installed, so
it serves both HTTP and WebSocket.

## Trying the socket

Connect to `ws://127.0.0.1:8000/ws/` — from the browser console:

```js
const ws = new WebSocket("ws://127.0.0.1:8000/ws/");
ws.onopen = () => ws.send("hello");
```

The consumer accepts the connection; `receive` is left empty on purpose — that
is where your own logic goes.

## Layout

```
websockettemplate/       # project settings, urls, wsgi
websockettemplate/asgi.py  # ProtocolTypeRouter: http -> Django, websocket -> apps.routing
apps/consumers.py        # AsyncWebsocketConsumer (connect / disconnect / receive)
apps/routing.py          # websocket_urlpatterns
manage.py
```

To add a socket, write a consumer in `apps/consumers.py` and register its path
in `apps/routing.py`.

## Environment variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key (required — startup fails without it) |
| `DEBUG` | `True` / `False` (default `True`) |
| `ALLOWED_HOSTS` | Comma-separated hosts |
| `DB_NAME` `DB_USER` `DB_PASSWORD` `DB_HOST` `DB_PORT` | PostgreSQL connection |
| `REDIS_HOST` `REDIS_PORT` | Channel layer backend (default `127.0.0.1:6379`) |
