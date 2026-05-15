import asyncio
import glob
import os
import sys

import config
from config import Client


# حذف ملفات الجلسة القديمة
for f in glob.glob("my_bot*"):
    try:
        os.remove(f)
    except Exception:
        pass


async def main():
    try:
        async with Client:
            me = await Client.get_me()
            print(f"✅ البوت يعمل: @{me.username}")
            await asyncio.sleep(float("inf"))
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
