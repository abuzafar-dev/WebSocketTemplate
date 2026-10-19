# WebSocket Template

Django Channels asosidagi oddiy real-time chat shablon. Har bir xona alohida guruh, xabarlar faqat shu xonadagilarga boradi.

## Ishga tushirish

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

`daphne` INSTALLED_APPS ning birinchi qatorida turgani uchun `runserver` ASGI rejimida ishlaydi.

http://127.0.0.1:8000/ — xona nomini kiriting, keyin shu xonani ikkita oynada oching va yozib ko'ring.

## Tuzilishi

- `config/asgi.py` — `http` va `websocket` uchun `ProtocolTypeRouter`
- `chat/consumers.py` — `ChatConsumer` (connect, receive, disconnect)
- `chat/routing.py` — `ws/chat/<room_name>/`
- `CHANNEL_LAYERS` — `InMemoryChannelLayer` (production uchun Redis kerak bo'ladi)

## Testlar

```bash
python manage.py test
```
