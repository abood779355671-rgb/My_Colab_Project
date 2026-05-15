import asyncio
import os
from flask import Flask
import threading

# إصلاح Pyrogram لبايثون 3.14
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from config import Client
import config

# خادم Flask لفتح المنفذ
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app_flask.run(host="0.0.0.0", port=port)

# تشغيل Flask في خيط منفصل
threading.Thread(target=run_flask, daemon=True).start()

async def main():
    async with Client:
        me = await Client.get_me()
        print(f"✅ تم تشغيل البوت: @{me.username}")
        await asyncio.sleep(float("inf"))

if __name__ == "__main__":
    loop.run_until_complete(main())
