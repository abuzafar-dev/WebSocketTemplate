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

Without `DB_HOST` / `REDIS_HOST` in `.env` it runs on SQLite and an in-memory
channel layer, so nothing else is needed. For production set both and start them:

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
const ws = new WebSocket("ws://127.0.0.1:8000/ws/python/");
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.onopen = () => ws.send(JSON.stringify({ message: "hello" }));
```

Every client connected to the same room (`/ws/<room>/`, default `lobby`)
receives the message as `{"room", "sender", "message"}`. Invalid JSON or an
empty message returns `{"error": ...}`.

## Tests

```bash
bash scripts/ci.sh      # check + migrations + 5 WebSocket tests
```

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
