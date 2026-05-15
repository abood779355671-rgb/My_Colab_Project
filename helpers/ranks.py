"""
نظام الرتب - يحدد صلاحيات كل مستخدم
الرتب من الأعلى للأدنى:
  مطور (DEV_ID) > مالك أساسي (gowner) > مالك (owner) > مدير (mod) > ادمن (admin) > مميز (pre) > عضو
"""
from config import r, DEV_ID


# ─────────────────────────── الاسم المعروض ──────────────────────────────

def get_rank(uid: int, cid: int) -> str:
    uid, cid = str(uid), str(cid)
    owner_id = r.get(f"{DEV_ID}:owner")
    if uid == DEV_ID:                              return r.get(f"{DEV_ID}:rankName:dev")   or "مطوّر 🎖️"
    if owner_id and uid == owner_id:               return r.get(f"{DEV_ID}:rankName:owner_g") or "مالك البوت 🎖️"
    if r.get(f"{uid}:rankDEV:{DEV_ID}"):           return r.get(f"{DEV_ID}:rankName:dev2") or "مطوّر مساعد 🎖️"
    if r.get(f"{uid}:gban:{DEV_ID}"):              return "محظور عام 🔴"
    if r.get(f"{uid}:mute:{DEV_ID}"):              return "مكتوم عام 🔇"
    if r.get(f"{cid}:rankGOWNER:{uid}:{DEV_ID}"): return r.get(f"{cid}:RankGowner:{DEV_ID}") or "المالك الأساسي 👑"
    if r.get(f"{cid}:rankOWNER:{uid}:{DEV_ID}"):  return r.get(f"{cid}:RankOwner:{DEV_ID}")  or "المالك 💎"
    if r.get(f"{cid}:rankMOD:{uid}:{DEV_ID}"):    return r.get(f"{cid}:RankMod:{DEV_ID}")    or "المدير ⚙️"
    if r.get(f"{cid}:rankADMIN:{uid}:{DEV_ID}"):  return r.get(f"{cid}:RankAdm:{DEV_ID}")    or "ادمن 🛡️"
    if r.get(f"{cid}:rankPRE:{uid}:{DEV_ID}"):    return r.get(f"{cid}:RankPre:{DEV_ID}")    or "مميز ⭐"
    return r.get(f"{cid}:RankMem:{DEV_ID}") or "عضو"


# ─────────────────────────── فحص الصلاحيات ──────────────────────────────

def _base(uid: int) -> bool:
    """مطوّر البوت أو مالكه"""
    uid = str(uid)
    owner = r.get(f"{DEV_ID}:owner")
    return uid == DEV_ID or (owner and uid == owner) or bool(r.get(f"{uid}:rankDEV:{DEV_ID}"))


def is_dev(uid: int, cid: int = 0) -> bool:
    return _base(uid)


def is_gowner(uid: int, cid: int) -> bool:
    return _base(uid) or bool(r.get(f"{str(cid)}:rankGOWNER:{str(uid)}:{DEV_ID}"))


def is_owner(uid: int, cid: int) -> bool:
    return is_gowner(uid, cid) or bool(r.get(f"{str(cid)}:rankOWNER:{str(uid)}:{DEV_ID}"))


def is_mod(uid: int, cid: int) -> bool:
    return is_owner(uid, cid) or bool(r.get(f"{str(cid)}:rankMOD:{str(uid)}:{DEV_ID}"))


def is_admin(uid: int, cid: int) -> bool:
    return is_mod(uid, cid) or bool(r.get(f"{str(cid)}:rankADMIN:{str(uid)}:{DEV_ID}"))


def is_pre(uid: int, cid: int) -> bool:
    return is_admin(uid, cid) or bool(r.get(f"{str(cid)}:rankPRE:{str(uid)}:{DEV_ID}"))


# ─────────────────────────── قفل الأوامر ────────────────────────────────

LOCK_LEVELS = {0: is_gowner, 1: is_owner, 2: is_mod, 3: is_admin, 4: is_pre}

def is_locked(uid: int, cid: int, text: str) -> bool:
    """يرجع True إذا كان الأمر مقفولاً على المستخدم"""
    locks = r.hgetall(f"{DEV_ID}:locks:{cid}")
    if not locks:
        return False
    for cmd, level in locks.items():
        if cmd.lower() in text.lower():
            checker = LOCK_LEVELS.get(int(level), is_gowner)
            return not checker(uid, cid)
    return False
