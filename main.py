import asyncio
import glob
import os
import sys

# ⚠️ إصلاح مشكلة Python 3.14 مع Pyrogram 2.0.106
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

async def main():
    async with Client:
        me = await Client.get_me()
        print(f"✅ تم تشغيل البوت: @{me.username}")
        await asyncio.sleep(float("inf"))

if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("تم إيقاف البوت")
