import os
import redis
from pyrogram import Client

API_ID    = int(os.getenv("API_ID", "0"))
API_HASH  = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
REDIS_URL = os.getenv("REDIS_URL", "")
DEV_ID    = os.getenv("DEV_ID", "123456789")   # ضع ID المطور هنا

# Redis
if REDIS_URL:
    r = redis.from_url(REDIS_URL, decode_responses=True)
else:
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# مفتاح البوت الافتراضي في الردود
def botkey() -> str:
    return r.get(f"{DEV_ID}:botkey") or "⚡"

# اسم البوت الافتراضي
def botname() -> str:
    return r.get(f"{DEV_ID}:BotName") or "بوتي"

Client = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="Plugins"),
)
