import asyncio
import os
import glob
from flask import Flask
import threading

# ⚠️ إصلاح مشكلة Python 3.14 مع Pyrogram
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

import config
from config import Client

# حذف ملفات الجلسة القديمة
for f in glob.glob("my_bot*"):
    try:
        os.remove(f)
    except:
        pass

# خادم Flask لفتح المنفذ المطلوب من Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
# تشغيل حلقة التنظيف التلقائي
from Plugins.auto_clean import _auto_clean_loop
asyncio.create_task(_auto_clean_loop(Client))
print("✅ حلقة التنظيف التلقائي تعمل")

# تشغيل Flask في خيط منفصل
threading.Thread(target=run_flask, daemon=True).start()

async def main():
    async with Client:
        me = await Client.get_me()
        print(f"✅ البوت شغال: @{me.username}")
        await asyncio.sleep(float("inf"))

if __name__ == "__main__":
    loop.run_until_complete(main())
