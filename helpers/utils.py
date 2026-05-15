"""
وظائف مساعدة مشتركة - التحقق من الشروط الأساسية قبل معالجة الأوامر
"""
from config import r, DEV_ID, botname
from helpers.ranks import is_admin


def group_enabled(cid: int) -> bool:
    """هل البوت مفعّل في هذه المجموعة؟"""
    return bool(r.get(f"{cid}:enable:{DEV_ID}"))


def is_muted_user(uid: int, cid: int) -> bool:
    """هل المستخدم مكتوم (محلي أو عام)؟"""
    return bool(
        r.get(f"{uid}:mute:{cid}:{DEV_ID}") or
        r.get(f"{uid}:mute:{DEV_ID}")
    )


def is_gbanned(uid: int) -> bool:
    return bool(r.get(f"{uid}:gban:{DEV_ID}"))


def group_muted(cid: int) -> bool:
    """هل المجموعة في وضع الصمت العام؟"""
    return bool(r.get(f"{cid}:mute:{DEV_ID}"))


def can_speak(uid: int, cid: int) -> bool:
    """هل يحق لهذا المستخدم الكلام في هذه المجموعة؟"""
    if group_muted(cid) and not is_admin(uid, cid):
        return False
    if is_muted_user(uid, cid):
        return False
    return True


def resolve_text(text: str, cid: int) -> str:
    """
    يحلّ أسماء البوت وأوامر مخصصة.
    إذا بدأت الرسالة باسم البوت → يحذفه.
    إذا كان هناك استبدال مخصص → يطبّقه.
    """
    name = botname()
    if text.startswith(f"{name} "):
        text = text[len(name) + 1:]
    # استبدال محلي (للمجموعة)
    local = r.get(f"{cid}:Custom:{cid}:{DEV_ID}&text={text}")
    if local:
        text = local
    # استبدال عام (لكل المجموعات)
    global_ = r.get(f"Custom:{DEV_ID}&text={text}")
    if global_:
        text = global_
    return text
