"""
ملف guards_locks.py - نظام الأقفال والحماية
الأوامر المتاحة:
  تفعيل الحماية / تعطيل الحماية     → حزمة حماية شاملة (مالك+)
  قفل الكل / فتح الكل               → قفل/فتح جميع الأنواع (مدير+)
  قفل/فتح الدردشة (الشات)           → منع الكتابة للكل (مدير+)
  قفل/فتح التعديل                   → منع تعديل الرسائل (مدير+)
  قفل/فتح تعديل الميديا             → منع تعديل الوسائط (مدير+)
  قفل/فتح الفويسات (البصمات)        → منع رسائل الصوت (مدير+)
  قفل/فتح الفيديو (الفيديوهات)       → منع الفيديو (مدير+)
  قفل/فتح الاشعارات                 → حذف إشعارات الخدمة (مدير+)
  قفل/فتح الصور                     → منع الصور (مدير+)
  قفل/فتح الملصقات                  → منع الستيكرات (مدير+)
  قفل/فتح الفارسيه                  → منع الكتابة الفارسية (مدير+)
  قفل/فتح الملفات                   → منع الملفات (مدير+)
  قفل/فتح المتحركات (المتحركه)       → منع الـ GIF (مدير+)
  قفل/فتح الروابط                   → منع الروابط (مدير+)
  قفل/فتح الهشتاق (الهاشتاق)         → منع الهاشتاقات (مدير+)
  قفل/فتح البوتات                   → منع دخول البوتات (مدير+)
  قفل/فتح اليوزرات (المنشن)          → منع المنشنات (مدير+)
  قفل/فتح الكفر (الشيعه/الشيعة)      → منع كلمات الكفر (مدير+)
  قفل/فتح الإباحي (الاباحي)          → فلتر NSFW (مدير+)
  قفل/فتح الكلام الكثير (الكلايش)    → منع الرسائل الطويلة +150 حرف (مدير+)
  قفل/فتح التكرار                   → منع التكرار السريع (مدير+)
  قفل/فتح التوجيه                   → منع التوجيه (مدير+)
  قفل/فتح الانلاين                  → منع الرسائل المضمّنة (مدير+)
  قفل/فتح السب                      → منع الكلمات البذيئة (مدير+)
  قفل/فتح الاضافه (الجهات)           → منع إضافة جهات الاتصال (مدير+)
  قفل/فتح دخول البوتات (الوهمي/الايراني) → حظر البوتات فور دخولها (مدير+)
  قفل/فتح الصوت                     → منع رسائل الصوت (مدير+)
  قفل/فتح القنوات                   → منع رسائل القنوات (مدير+)
  قفل/فتح الدخول                    → طرد من يدخل (مدير+)
  تعطيل/تفعيل التحذير               → إيقاف/تشغيل رسائل التحذير (مدير+)
  منع (رد على ميديا)                → منع ملف بعينه (مدير+)
  الغاء منع (رد على ميديا)          → إلغاء منع ملف (مدير+)
  منع (رد على نص)                   → منع كلمة بعينها (مدير+)
  قائمة المنع / مسح قائمة المنع     → إدارة قائمة المنع
"""

import re
from threading import Thread

from pyrogram import Client, filters
from pyrogram.types import Message

from config import r, DEV_ID, botkey
from helpers.ranks import is_admin, is_mod, is_owner, is_gowner, is_dev, is_pre
from helpers.utils import group_enabled, resolve_text

# ────────────────────────────────────────────────────────────
# قوائم الكلمات المحظورة
# ────────────────────────────────────────────────────────────

LIST_SUB = [
    "كس", "كسمك", "كسختك", "عير", "كسخالتك", "خرا بالله", "عير بالله",
    "كسخواتكم", "كحاب", "مناويج", "كحبه", "ابن الكحبه", "فرخ", "فروخ",
    "طيزك", "طيزختك", "يا ابن الخول", "المتناك", "شرموط", "شرموطه",
    "ابن الشرموطه", "ابن الخول", "ابن العرص", "منايك", "متناك",
    "ابن المتناكه", "زبك", "عرص", "زبي", "خول", "لبوه", "لباوي",
    "ابن اللبوه", "منيوك", "كسمكك", "متناكه", "يا عرص", "يا خول",
    "قحبه", "القحبه", "شراميط", "العلق", "العلوق", "العلقه",
]

# ────────────────────────────────────────────────────────────
# مساعدات
# ────────────────────────────────────────────────────────────

def _find_urls(text: str) -> list:
    """يجد الروابط في النص"""
    pattern = r'(https?://[^\s]+|t\.me/[^\s]+|@[A-Za-z0-9_]{5,})'
    return re.findall(pattern, text)


def _k() -> str:
    return botkey()


def _warn_msg(mention: str, key: str, reason: str) -> str:
    return f"「 {mention} 」\n{key} ممنوع {reason}\n☆"


def _cooldown_warn(uid: int, cid: int) -> bool:
    """يمنع إرسال أكثر من تحذير في 60 ثانية للمستخدم"""
    key = f"{DEV_ID}:inWARN:{uid}{cid}"
    if r.get(key):
        return True
    r.set(key, 1, ex=60)
    return False


# ────────────────────────────────────────────────────────────
# معالج القفل الرئيسي (على كل رسالة في المجموعة)
# ────────────────────────────────────────────────────────────

@Client.on_message(filters.group, group=27)
def guard_handler(c: Client, m: Message):
    Thread(target=_guard_sync, args=(c, m)).start()


@Client.on_edited_message(filters.group, group=27)
def guard_edit_handler(c: Client, m: Message):
    Thread(target=_guard_edit_sync, args=(c, m)).start()


def _guard_edit_sync(c: Client, m: Message):
    """معالجة الرسائل المعدّلة"""
    if not group_enabled(m.chat.id):
        return

    k = _k()

    if m.sender_chat:
        uid = m.sender_chat.id
        mention = m.sender_chat.title
    elif m.from_user:
        uid = m.from_user.id
        mention = m.from_user.mention
    else:
        return

    # قفل التعديل النصي
    if r.get(f"{m.chat.id}:lockEdit:{DEV_ID}") and m.text and not is_admin(uid, m.chat.id):
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "التعديل"), disable_web_page_preview=True)

    # قفل تعديل الميديا
    if r.get(f"{m.chat.id}:lockEditM:{DEV_ID}") and m.media and not is_admin(uid, m.chat.id):
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "تعديل الميديا"), disable_web_page_preview=True)


def _guard_sync(c: Client, m: Message):
    """المعالج الرئيسي لجميع الأقفال"""
    if not group_enabled(m.chat.id):
        return

    k = _k()

    if m.sender_chat:
        uid = m.sender_chat.id
        mention = m.sender_chat.title
    elif m.from_user:
        uid = m.from_user.id
        mention = m.from_user.mention
    else:
        return

    # حذف إشعارات الخدمة
    if r.get(f"{m.chat.id}:lockNot:{DEV_ID}") and m.service:
        m.delete()
        return

    # منع إضافة جهات الاتصال
    if r.get(f"{m.chat.id}:lockaddContacts:{DEV_ID}") and m.from_user and m.new_chat_members:
        if not is_admin(m.from_user.id, m.chat.id):
            for mem in m.new_chat_members:
                if mem.id != m.from_user.id:
                    m.chat.ban_member(mem.id)
                    m.delete()
                    if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}"):
                        m.reply(_warn_msg(m.from_user.mention, k, "تضيف حد هنا"), disable_web_page_preview=True)
                    return

    # فحص مكتوم / صمت عام
    if r.get(f"{uid}:mute:{m.chat.id}{DEV_ID}") or r.get(f"{uid}:mute:{DEV_ID}"):
        return
    if r.get(f"{m.chat.id}:mute:{DEV_ID}") and not is_admin(uid, m.chat.id):
        m.delete()
        return

    # المميز وفوق يتخطى كل الأقفال
    if is_pre(uid, m.chat.id):
        return

    # فحص الملفات المحظورة بعينها
    if m.media:
        file_id = None
        if m.sticker:    file_id = m.sticker.file_id
        elif m.animation: file_id = m.animation.file_id
        elif m.photo:    file_id = m.photo.file_id
        elif m.video:    file_id = m.video.file_id
        elif m.voice:    file_id = m.voice.file_id
        elif m.audio:    file_id = m.audio.file_id
        elif m.document: file_id = m.document.file_id
        if file_id:
            idd = file_id[-6:]
            if r.get(f"{idd}:NotAllow:{m.chat.id}{DEV_ID}"):
                if not is_admin(uid, m.chat.id):
                    m.delete()
                    return

    # فحص الكلمات المحظورة في النص
    if m.text and r.smembers(f"{m.chat.id}:NotAllowedListText:{DEV_ID}"):
        if not is_admin(uid, m.chat.id):
            for word in r.smembers(f"{m.chat.id}:NotAllowedListText:{DEV_ID}"):
                if word in m.text:
                    m.delete()
                    return

    # حظر دخول البوتات
    if r.get(f"{m.chat.id}:lockBots:{DEV_ID}") and m.new_chat_members:
        for mem in m.new_chat_members:
            if mem.is_bot:
                m.chat.ban_member(mem.id)
        return

    # منع دخول الكل
    if r.get(f"{m.chat.id}:lockJoin:{DEV_ID}") and m.new_chat_members:
        for mem in m.new_chat_members:
            if not is_admin(mem.id, m.chat.id):
                m.chat.ban_member(mem.id)
                m.chat.unban_member(mem.id)
        return

    # منع رسائل القنوات
    if r.get(f"{m.chat.id}:lockChannels:{DEV_ID}") and m.sender_chat:
        if m.sender_chat.id != m.chat.id:
            m.chat.ban_member(m.sender_chat.id)
            return

    # منع التكرار السريع
    if r.get(f"{m.chat.id}:lockSpam:{DEV_ID}") and m.from_user:
        spam_key = f"{uid}in_spam:{m.chat.id}{DEV_ID}"
        count = r.get(spam_key)
        if not count:
            r.set(spam_key, 1, ex=10)
        else:
            count = int(count)
            if count >= 10:
                r.set(f"{uid}:mute:{m.chat.id}{DEV_ID}", 1)
                r.sadd(f"{m.chat.id}:listMUTE:{DEV_ID}", uid)
                r.delete(spam_key)
                m.reply(f"「 {mention} 」\n{k} كتمتك يالبثر عشان تتعلم تكرر\n☆")
                return
            else:
                r.set(spam_key, count + 1, ex=10)

    # قفل الانلاين (رسائل مضمّنة)
    if r.get(f"{m.chat.id}:lockInline:{DEV_ID}") and m.via_bot:
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "ترسل انلاين"), disable_web_page_preview=True)
        return

    # قفل التوجيه
    if r.get(f"{m.chat.id}:lockForward:{DEV_ID}") and m.forward_date:
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "ترسل توجيه"), disable_web_page_preview=True)
        return

    # قفل الصوت (Audio)
    if r.get(f"{m.chat.id}:lockAudios:{DEV_ID}") and m.audio:
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "ترسل صوت"), disable_web_page_preview=True)
        return

    # قفل الفيديو
    if r.get(f"{m.chat.id}:lockVideo:{DEV_ID}") and m.video:
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "ترسل فيديوهات"), disable_web_page_preview=True)
        return

    # قفل الصور
    if r.get(f"{m.chat.id}:lockPhoto:{DEV_ID}") and m.photo:
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "ترسل صور"), disable_web_page_preview=True)
        return

    # قفل الملصقات
    if r.get(f"{m.chat.id}:lockStickers:{DEV_ID}") and m.sticker:
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "ترسل ملصقات"), disable_web_page_preview=True)
        return

    # قفل المتحركات GIF
    if r.get(f"{m.chat.id}:lockAnimations:{DEV_ID}") and m.animation:
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "ترسل متحركات"), disable_web_page_preview=True)
        return

    # قفل الملفات
    if r.get(f"{m.chat.id}:lockFiles:{DEV_ID}") and m.document:
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "ترسل ملفات"), disable_web_page_preview=True)
        return

    # قفل الفارسي
    PERSIAN_CHARS = ("ه‍", "ی", "ک", "چ")
    if r.get(f"{m.chat.id}:lockPersian:{DEV_ID}"):
        txt = m.text or m.caption or ""
        if any(c in txt for c in PERSIAN_CHARS):
            m.delete()
            if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}"):
                m.reply(_warn_msg(mention, k, "ترسل فارسي"), disable_web_page_preview=True)
            return

    # قفل الروابط
    if r.get(f"{m.chat.id}:lockUrls:{DEV_ID}") and m.text:
        if len(_find_urls(m.text)) > 0:
            m.delete()
            if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
                m.reply(_warn_msg(mention, k, "ترسل روابط"), disable_web_page_preview=True)
            return

    # قفل الهاشتاق
    if r.get(f"{m.chat.id}:lockHashtags:{DEV_ID}") and m.text:
        if len(re.findall(r"#(\w+)", m.text)) > 0:
            m.delete()
            if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
                m.reply(_warn_msg(mention, k, "ترسل هاشتاق"), disable_web_page_preview=True)
            return

    # قفل الكلام الكثير (+150 حرف)
    if r.get(f"{m.chat.id}:lockMessages:{DEV_ID}") and m.text and len(m.text) > 150:
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "ترسل كلام كثير"), disable_web_page_preview=True)
        return

    # قفل الفويس (Voice)
    if r.get(f"{m.chat.id}:lockVoice:{DEV_ID}") and m.voice:
        m.delete()
        if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
            m.reply(_warn_msg(mention, k, "ترسل فويس"), disable_web_page_preview=True)
        return

    # قفل المنشنات
    if r.get(f"{m.chat.id}:lockTags:{DEV_ID}") and m.text:
        if re.search(r"@[A-Za-z0-9_]{5,}", m.text):
            m.delete()
            if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
                m.reply(_warn_msg(mention, k, "ترسل منشنات"), disable_web_page_preview=True)
            return

    # قفل السب
    if r.get(f"{m.chat.id}:lockSHTM:{DEV_ID}"):
        txt = m.caption or m.text or ""
        for word in LIST_SUB:
            if word in txt:
                m.delete()
                if not r.get(f"{m.chat.id}:disableWarn:{DEV_ID}") and not _cooldown_warn(uid, m.chat.id):
                    m.reply(_warn_msg(mention, k, "السب هنا"), disable_web_page_preview=True)
                return


# ────────────────────────────────────────────────────────────
# معالج الأوامر (group=28)
# ────────────────────────────────────────────────────────────

@Client.on_message(filters.group & filters.text, group=28)
def lock_commands_handler(c: Client, m: Message):
    if not m.from_user:
        return
    if not group_enabled(m.chat.id):
        return

    text = resolve_text(m.text, m.chat.id)
    k = _k()
    uid = m.from_user.id
    cid = m.chat.id
    mention = m.from_user.mention

    def reply(msg):
        return m.reply(msg, disable_web_page_preview=True)

    def need_mod():
        if not is_mod(uid, cid):
            reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
            return True
        return False

    def need_owner():
        if not is_owner(uid, cid):
            reply(f"{k} هذا الأمر يخص ( المالك وفوق ) بس")
            return True
        return False

    # ──── قفل الكل ────
    if text == "قفل الكل":
        if need_mod(): return
        ALL_LOCKS = [
            "mute", "lockEdit", "lockEditM", "lockVoice", "lockVideo",
            "lockNot", "lockPhoto", "lockPersian", "lockStickers", "lockFiles",
            "lockAnimations", "lockUrls", "lockHashtags", "lockBots", "lockTags",
            "lockMessages", "lockSpam", "lockForward", "lockSHTM",
            "lockaddContacts", "lockAudios", "lockChannels", "lockJoin",
            "lockInline", "lockNSFW",
        ]
        if all(r.get(f"{cid}:{lk}:{DEV_ID}") for lk in ALL_LOCKS):
            return reply(f"{k} من 「 {mention} 」\n{k} كل شي مقفل يالطيب!\n☆")
        for lk in ALL_LOCKS:
            r.set(f"{cid}:{lk}:{DEV_ID}", 1)
        return reply(f"{k} من 「 {mention} 」\n{k} ابشر قفلت كل شي\n☆")

    # ──── فتح الكل ────
    if text == "فتح الكل":
        if need_mod(): return
        ALL_LOCKS = [
            "mute", "lockEdit", "lockEditM", "lockVoice", "lockVideo",
            "lockNot", "lockPhoto", "lockPersian", "lockStickers", "lockFiles",
            "lockAnimations", "lockUrls", "lockHashtags", "lockBots", "lockTags",
            "lockMessages", "lockSpam", "lockForward", "lockSHTM",
            "lockaddContacts", "lockAudios", "lockChannels", "lockJoin",
            "lockInline", "lockNSFW", "lockKFR",
        ]
        if not any(r.get(f"{cid}:{lk}:{DEV_ID}") for lk in ALL_LOCKS):
            return reply(f"{k} من 「 {mention} 」\n{k} كل شي مفتوح يالطيب!\n☆")
        for lk in ALL_LOCKS:
            r.delete(f"{cid}:{lk}:{DEV_ID}")
        return reply(f"{k} من 「 {mention} 」\n{k} ابشر فتحت كل شي\n☆")

    # ──── تفعيل الحماية ────
    PROT_LOCKS = [
        "lockEditM", "lockVoice", "lockVideo", "lockPhoto", "lockPersian",
        "lockStickers", "lockFiles", "lockAnimations", "lockUrls", "lockTags",
        "lockMessages", "lockSpam", "lockForward", "lockSHTM", "lockAudios",
        "lockChannels", "lockNSFW",
    ]
    if text in ("تفعيل الحماية", "تفعيل الحمايه"):
        if need_owner(): return
        if all(r.get(f"{cid}:{lk}:{DEV_ID}") for lk in PROT_LOCKS):
            return reply(f"{k} من 「 {mention} 」\n{k} الحماية مفعلة من قبل\n☆")
        r.delete(f"{cid}:disableWarn:{DEV_ID}")
        for lk in PROT_LOCKS:
            r.set(f"{cid}:{lk}:{DEV_ID}", 1)
        return reply(f"{k} من 「 {mention} 」\n{k} ابشر فعّلت الحماية\n☆")

    # ──── تعطيل الحماية ────
    if text in ("تعطيل الحماية", "تعطيل الحمايه"):
        if need_owner(): return
        if not any(r.get(f"{cid}:{lk}:{DEV_ID}") for lk in PROT_LOCKS):
            return reply(f"{k} من 「 {mention} 」\n{k} الحماية معطلة من قبل\n☆")
        for lk in PROT_LOCKS:
            r.delete(f"{cid}:{lk}:{DEV_ID}")
        return reply(f"{k} من 「 {mention} 」\n{k} ابشر عطّلت الحماية\n☆")

    # ──── أوامر قفل/فتح فردية ────
    SINGLE_LOCKS = {
        # نص الأمر: (مفتاح Redis، سبب التحذير)
        "قفل الدردشة":      ("mute",              ""),
        "قفل الدردشه":      ("mute",              ""),
        "قفل الشات":        ("mute",              ""),
        "فتح الدردشة":      ("mute",              ""),
        "فتح الدردشه":      ("mute",              ""),
        "فتح الشات":        ("mute",              ""),
        "قفل التعديل":      ("lockEdit",          ""),
        "فتح التعديل":      ("lockEdit",          ""),
        "قفل تعديل الميديا":("lockEditM",         ""),
        "فتح تعديل الميديا":("lockEditM",         ""),
        "قفل الفويسات":     ("lockVoice",         ""),
        "قفل البصمات":      ("lockVoice",         ""),
        "فتح الفويسات":     ("lockVoice",         ""),
        "فتح البصمات":      ("lockVoice",         ""),
        "قفل الفيديو":      ("lockVideo",         ""),
        "قفل الفيديوهات":   ("lockVideo",         ""),
        "فتح الفيديو":      ("lockVideo",         ""),
        "فتح الفيديوهات":   ("lockVideo",         ""),
        "قفل الاشعارات":    ("lockNot",           ""),
        "فتح الاشعارات":    ("lockNot",           ""),
        "قفل الصور":        ("lockPhoto",         ""),
        "فتح الصور":        ("lockPhoto",         ""),
        "قفل الملصقات":     ("lockStickers",      ""),
        "فتح الملصقات":     ("lockStickers",      ""),
        "قفل الفارسيه":     ("lockPersian",       ""),
        "فتح الفارسيه":     ("lockPersian",       ""),
        "قفل الملفات":      ("lockFiles",         ""),
        "فتح الملفات":      ("lockFiles",         ""),
        "قفل المتحركات":    ("lockAnimations",    ""),
        "قفل المتحركه":     ("lockAnimations",    ""),
        "فتح المتحركات":    ("lockAnimations",    ""),
        "فتح المتحركه":     ("lockAnimations",    ""),
        "قفل الروابط":      ("lockUrls",          ""),
        "فتح الروابط":      ("lockUrls",          ""),
        "قفل الهشتاق":      ("lockHashtags",      ""),
        "قفل الهاشتاق":     ("lockHashtags",      ""),
        "فتح الهشتاق":      ("lockHashtags",      ""),
        "فتح الهاشتاق":     ("lockHashtags",      ""),
        "قفل البوتات":      ("lockBots",          ""),
        "فتح البوتات":      ("lockBots",          ""),
        "قفل اليوزرات":     ("lockTags",          ""),
        "قفل المنشن":       ("lockTags",          ""),
        "فتح اليوزرات":     ("lockTags",          ""),
        "فتح المنشن":       ("lockTags",          ""),
        "قفل الكفر":        ("lockKFR",           ""),
        "قفل الشيعه":       ("lockKFR",           ""),
        "قفل الشيعة":       ("lockKFR",           ""),
        "فتح الكفر":        ("lockKFR",           ""),
        "فتح الشيعه":       ("lockKFR",           ""),
        "فتح الشيعة":       ("lockKFR",           ""),
        "قفل الإباحي":      ("lockNSFW",          ""),
        "قفل الاباحي":      ("lockNSFW",          ""),
        "فتح الإباحي":      ("lockNSFW",          ""),
        "فتح الاباحي":      ("lockNSFW",          ""),
        "قفل الكلام الكثير": ("lockMessages",     ""),
        "قفل الكلايش":      ("lockMessages",      ""),
        "فتح الكلام الكثير": ("lockMessages",     ""),
        "فتح الكلايش":      ("lockMessages",      ""),
        "قفل التكرار":      ("lockSpam",          ""),
        "فتح التكرار":      ("lockSpam",          ""),
        "قفل التوجيه":      ("lockForward",       ""),
        "فتح التوجيه":      ("lockForward",       ""),
        "قفل الانلاين":     ("lockInline",        ""),
        "فتح الانلاين":     ("lockInline",        ""),
        "قفل السب":         ("lockSHTM",          ""),
        "فتح السب":         ("lockSHTM",          ""),
        "قفل الاضافه":      ("lockaddContacts",   ""),
        "قفل الاضافة":      ("lockaddContacts",   ""),
        "قفل الجهات":       ("lockaddContacts",   ""),
        "فتح الاضافه":      ("lockaddContacts",   ""),
        "فتح الاضافة":      ("lockaddContacts",   ""),
        "فتح الجهات":       ("lockaddContacts",   ""),
        "قفل دخول البوتات": ("lockBots",          ""),
        "قفل الوهمي":       ("lockBots",          ""),
        "قفل الايراني":     ("lockBots",          ""),
        "فتح دخول البوتات": ("lockBots",          ""),
        "فتح الوهمي":       ("lockBots",          ""),
        "فتح الايراني":     ("lockBots",          ""),
        "قفل الصوت":        ("lockVoice",         ""),
        "فتح الصوت":        ("lockVoice",         ""),
        "قفل القنوات":      ("lockChannels",      ""),
        "فتح القنوات":      ("lockChannels",      ""),
        "قفل الدخول":       ("lockJoin",          ""),
        "فتح الدخول":       ("lockJoin",          ""),
    }

    if text in SINGLE_LOCKS:
        if need_mod(): return
        lock_key, _ = SINGLE_LOCKS[text]
        redis_key = f"{cid}:{lock_key}:{DEV_ID}"
        is_lock = text.startswith("قفل")
        name_ar = text.replace("قفل ", "").replace("فتح ", "")
        if is_lock:
            if r.get(redis_key):
                return reply(f"{k} من 「 {mention} 」\n{k} {text} مفعّل من قبل\n☆")
            r.set(redis_key, 1)
            return reply(f"{k} من 「 {mention} 」\n{k} ابشر {text}\n☆")
        else:
            if not r.get(redis_key):
                return reply(f"{k} من 「 {mention} 」\n{k} {text} معطّل من قبل\n☆")
            r.delete(redis_key)
            return reply(f"{k} من 「 {mention} 」\n{k} ابشر {text}\n☆")

    # ──── تعطيل/تفعيل التحذير ────
    if text == "تعطيل التحذير":
        if need_mod(): return
        if r.get(f"{cid}:disableWarn:{DEV_ID}"):
            return reply(f"{k} من 「 {mention} 」\n{k} التحذير معطّل من قبل\n☆")
        r.set(f"{cid}:disableWarn:{DEV_ID}", 1)
        return reply(f"{k} من 「 {mention} 」\n{k} ابشر عطّلت التحذير\n☆")

    if text == "تفعيل التحذير":
        if need_mod(): return
        if not r.get(f"{cid}:disableWarn:{DEV_ID}"):
            return reply(f"{k} من 「 {mention} 」\n{k} التحذير مفعّل من قبل\n☆")
        r.delete(f"{cid}:disableWarn:{DEV_ID}")
        return reply(f"{k} من 「 {mention} 」\n{k} ابشر فعّلت التحذير\n☆")

    # ──── منع / الغاء منع ميديا ────
    if text == "منع" and m.reply_to_message and m.reply_to_message.media:
        if need_mod(): return
        rep = m.reply_to_message
        file_id = None
        if rep.sticker:    file_id = rep.sticker.file_id
        elif rep.animation: file_id = rep.animation.file_id
        elif rep.photo:    file_id = rep.photo.file_id
        elif rep.video:    file_id = rep.video.file_id
        elif rep.voice:    file_id = rep.voice.file_id
        elif rep.audio:    file_id = rep.audio.file_id
        elif rep.document: file_id = rep.document.file_id
        if file_id:
            idd = file_id[-6:]
            if r.get(f"{idd}:NotAllow:{cid}{DEV_ID}"):
                return reply(f"{k} هذا الملف محظور من قبل")
            r.set(f"{idd}:NotAllow:{cid}{DEV_ID}", 1)
            r.sadd(f"{cid}:NotAllowedList:{DEV_ID}", idd)
            return reply(f"{k} من 「 {mention} 」\n{k} ابشر منعت هذا الملف\n☆")

    if text == "الغاء منع" and m.reply_to_message and m.reply_to_message.media:
        if need_mod(): return
        rep = m.reply_to_message
        file_id = None
        if rep.sticker:    file_id = rep.sticker.file_id
        elif rep.animation: file_id = rep.animation.file_id
        elif rep.photo:    file_id = rep.photo.file_id
        elif rep.video:    file_id = rep.video.file_id
        elif rep.voice:    file_id = rep.voice.file_id
        elif rep.audio:    file_id = rep.audio.file_id
        elif rep.document: file_id = rep.document.file_id
        if file_id:
            idd = file_id[-6:]
            if not r.get(f"{idd}:NotAllow:{cid}{DEV_ID}"):
                return reply(f"{k} هذا الملف مو محظور")
            r.delete(f"{idd}:NotAllow:{cid}{DEV_ID}")
            r.srem(f"{cid}:NotAllowedList:{DEV_ID}", idd)
            return reply(f"{k} من 「 {mention} 」\n{k} ابشر رفعت المنع\n☆")

    # ──── منع كلمة نصية ────
    if text == "منع" and m.reply_to_message and not m.reply_to_message.media:
        if need_mod(): return
        word = m.reply_to_message.text
        if not word:
            return reply(f"{k} الرسالة ما تحتوي نص")
        r.sadd(f"{cid}:NotAllowedListText:{DEV_ID}", word)
        return reply(f"{k} من 「 {mention} 」\n{k} ابشر منعت: `{word}`\n☆")

    # ──── قائمة المنع ────
    if text in ("قائمه المنع", "قائمة المنع"):
        if need_mod(): return
        files = r.smembers(f"{cid}:NotAllowedList:{DEV_ID}")
        words = r.smembers(f"{cid}:NotAllowedListText:{DEV_ID}")
        if not files and not words:
            return reply(f"{k} قائمة المنع فارغة")
        msg = f"{k} قائمة المنع:\n\n"
        if files:
            msg += "**الملفات:**\n" + "\n".join(f"• `{f}`" for f in files) + "\n\n"
        if words:
            msg += "**الكلمات:**\n" + "\n".join(f"• `{w}`" for w in words)
        return reply(msg)

    # ──── مسح قائمة المنع ────
    if text in ("مسح قائمه المنع", "مسح قائمة المنع"):
        if need_mod(): return
        files = r.smembers(f"{cid}:NotAllowedList:{DEV_ID}")
        for f in files:
            r.delete(f"{f}:NotAllow:{cid}{DEV_ID}")
        r.delete(f"{cid}:NotAllowedList:{DEV_ID}")
        r.delete(f"{cid}:NotAllowedListText:{DEV_ID}")
        return reply(f"{k} ابشر مسحت قائمة المنع")
