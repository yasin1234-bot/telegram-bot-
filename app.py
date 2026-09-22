import sys
import os
import json
import asyncio
import aiohttp
import re
import time
import ssl
import random
import uuid
import binascii
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ================= AUTO GENERATE DIRECTORIES & PROTO FILES =================
def setup_proto_environment():
    """ Render / Railway তে ফাইল মিসিং এরর রোধ করতে অটো ফোল্ডার ও ফাইল জেনারেট করার ফাংশন """
    pb2_dir = os.path.join(os.getcwd(), "Pb2")
    proto_dir = os.path.join(os.getcwd(), "proto")
    
    os.makedirs(pb2_dir, exist_ok=True)
    os.makedirs(proto_dir, exist_ok=True)

    # create __init__.py inside subfolders
    for d in [pb2_dir, proto_dir]:
        init_file = os.path.join(d, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                f.write("# Auto-generated package initializer\n")

    # Pb2 module dummy stubs
    pb2_files = [
        "DEcwHisPErMsG_pb2.py", "Fo_pb2.py", "GenWhisperMsg_pb2.py",
        "MajoRLoGinrEs_pb2.py", "MajorLoGinReq_pb2.py", "MajorLoginRes_pb2.py",
        "PorTs_pb2.py", "sQ_pb2.py", "Team_msg_pb2.py"
    ]

    for fname in pb2_files:
        filepath = os.path.join(pb2_dir, fname)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f'""" Auto-generated stub for {fname} """\n')
                f.write('class MajorLoginRes:\n')
                f.write('    def __init__(self):\n')
                f.write('        self.token = ""\n')
                f.write('        self.jwt = ""\n')
                f.write('        self.accountId = ""\n')
                f.write('        self.region = ""\n')
                f.write('    def ParseFromString(self, data):\n')
                f.write('        pass\n')

    # proto module dummy stubs
    proto_files = ["MajorLoginRes_pb2.py"]
    for fname in proto_files:
        filepath = os.path.join(proto_dir, fname)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f'""" Auto-generated stub for {fname} """\n')
                f.write('class MajorLoginRes:\n')
                f.write('    def __init__(self):\n')
                f.write('        self.token = ""\n')
                f.write('        self.jwt = ""\n')
                f.write('        self.accountId = ""\n')
                f.write('        self.region = ""\n')
                f.write('    def ParseFromString(self, data):\n')
                f.write('        pass\n')

setup_proto_environment()

import blackboxprotobuf
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ================= PROTOBUF IMPORTS =================
try:
    import my_pb2
    import output_pb2
except ImportError:
    my_pb2 = None
    output_pb2 = None

USE_PB2 = False
PorPorts_pb2 = None
MajorLoginRes_pb2 = None

pb2_paths = [
    os.path.join(os.path.dirname(__file__), 'Pb2'),
    os.path.join(os.getcwd(), 'Pb2'),
    os.path.join(os.getcwd(), 'proto'),
]
for path in pb2_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

try:
    from Pb2 import PorTs_pb2 as PorPorts_pb2
    USE_PB2 = True
except ImportError:
    pass

try:
    from Pb2 import MajoRLoGinrEs_pb2 as MajorLoginRes_pb2
except ImportError:
    try:
        from proto import MajorLoginRes_pb2
    except ImportError:
        MajorLoginRes_pb2 = None

# ================= CONFIGURATION =================
BOT_TOKEN = "8732122079:AAHy-XYFX6FPZhrpnAB6VUXhHzwjAy7xg5E"

ADMIN_CHAT_IDS = [8128075446] 

ADMIN_TXT_FILE = "admin.txt"
RESULT_FOLDER = "SAITO_SPINNER_RESULT"
ADMIN_RESULTS_FOLDER = os.path.join(RESULT_FOLDER, "ADMIN_NARUTO_LOGS")

os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(ADMIN_RESULTS_FOLDER, exist_ok=True)

if not os.path.exists(ADMIN_TXT_FILE):
    with open(ADMIN_TXT_FILE, "w", encoding="utf-8") as f:
        f.write("# Put Admin Chat IDs here line by line\n")
        for aid in ADMIN_CHAT_IDS:
            f.write(f"{aid}\n")

def get_admin_chat_ids():
    admin_ids = list(ADMIN_CHAT_IDS)
    if os.path.exists(ADMIN_TXT_FILE):
        try:
            with open(ADMIN_TXT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and line.isdigit():
                        admin_ids.append(int(line))
        except Exception:
            pass
    return list(set(admin_ids))

def is_admin(chat_id):
    return chat_id in get_admin_chat_ids()

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV  = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

SERVERS = {
    "1": {"code": "bd",  "name": "Bangladesh", "url": "https://clientbp.ggpolarbear.com"},
    "2": {"code": "ind", "name": "India",      "url": "https://client.ind.freefiremobile.com"}
}

RAW_HEX_PAYLOAD = "7DF7F8996CD696356CD01BCBD2B3CDE8"
RELEASE_VERSION = "OB55"
EXTERNAL_JWT_API = "https://jwt-fmhy.vercel.app/token"
UNITY_USER_AGENT = "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
UNITY_VERSION = "2022.3.47f1"

DEVICES = [
    "Asus ASUS_I005DA", "SM-G998B", "CPH2095", "Pixel 6", "OnePlus 9 Pro",
    "Samsung Galaxy S23 Ultra", "iPhone 14 Pro Max", "Xiaomi 13 Pro"
]
CARRIERS = ["Jio", "Airtel", "Vodafone Idea", "T-Mobile", "Verizon", "Telenor"]
GPUS = ["Adreno (TM) 640", "Mali-G78", "Adreno 660", "Apple A15 GPU"]

# ================= RARE ITEMS DB =================
RARE_ITEMS_DB = {
    710047022: {"name": "NARUTO BUNDLE",                 "file": "ultra_rare_naruto_bundle"},
    801055004: {"name": "NARUTO TOKEN",                  "file": "naruto_token"},
    820981015: {"name": "BLUE NINJA VOUCHER",           "file": "blue_ninja_voucher"},
    903047008: {"name": "Loot Box - Body Substitution", "file": "loot_box_body_substitution"},
    904047008: {"name": "Backpack - Ninja's Scroll",    "file": "backpack_ninjas_scroll"},
    907104746: {"name": "Gloo Wall - Hokage Rock",      "file": "gloo_wall_hokage_rock"},
    909047015: {"name": "Rasengan",                      "file": "rasengan"}
}

ULTRA_RARE_IDS = {710047022}

USER_SESSIONS = {}

# ================= UTILITY & ENCRYPTION =================
def encrypt_plaintext(plaintext):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(plaintext, AES.block_size))

def star_varint_encode(n):
    if n < 0:
        n += 1 << 64
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)

def star_build_field(field_num, value):
    if isinstance(value, bool):
        return star_varint_encode((field_num << 3) | 0) + star_varint_encode(1 if value else 0)
    if isinstance(value, int):
        return star_varint_encode((field_num << 3) | 0) + star_varint_encode(value)
    if isinstance(value, (str, bytes)):
        data = value.encode("utf-8") if isinstance(value, str) else value
        return star_varint_encode((field_num << 3) | 2) + star_varint_encode(len(data)) + data
    if isinstance(value, dict):
        sub = star_assemble_proto(value)
        return star_varint_encode((field_num << 3) | 2) + star_varint_encode(len(sub)) + sub
    raise TypeError(f"Unsupported type: {type(value)}")

def star_assemble_proto(fields: dict) -> bytes:
    packet = b""
    for k in sorted(fields.keys(), key=lambda x: int(x)):
        v = fields[k]
        fn = int(k)
        if isinstance(v, list):
            for item in v:
                packet += star_build_field(fn, item)
        else:
            packet += star_build_field(fn, v)
    return packet

def star_server_url(region):
    reg = str(region).upper()
    if reg == "IND":
        return "https://client.ind.freefiremobile.com"
    elif reg in ["BR", "US", "SAC", "NA"]:
        return "https://client.us.freefiremobile.com"
    else:
        return "https://clientbp.ggpolarbear.com"

def find_item_id(data):
    if isinstance(data, dict):
        if (1 in data or "1" in data):
            sub = data.get(1) or data.get("1")
            if isinstance(sub, dict):
                if 2 in sub:
                    return sub[2]
                if "2" in sub:
                    return sub["2"]
        for value in data.values():
            res = find_item_id(value)
            if res is not None:
                return res
    elif isinstance(data, list):
        for item in data:
            res = find_item_id(item)
            if res is not None:
                return res
    return None

def create_progress_bar(current, total, bar_length=10):
    percent = float(current) / total
    arrow = '█' * int(round(percent * bar_length))
    spaces = '░' * (bar_length - len(arrow))
    return f"[{arrow}{spaces}] {int(round(percent * 100))}%"

# ================= DEDUPLICATION & FILE SAVING =================
def save_deduplicated_json(filepath, entry):
    data_list = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    data_list = json.loads(content)
        except Exception:
            data_list = []

    is_duplicate = False
    for item in data_list:
        if str(item.get("guestUid")) == str(entry.get("guestUid")) and str(item.get("guestPass")) == str(entry.get("guestPass")):
            is_duplicate = True
            break

    if not is_duplicate:
        data_list.append(entry)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, indent=4)
        return True
    return False

def save_item_to_specific_file(chat_id, uid, pwd, item_id, item_name, base_filename, is_ultra_rare=False):
    user_dir = os.path.join(RESULT_FOLDER, str(chat_id))
    os.makedirs(user_dir, exist_ok=True)

    json_filepath = os.path.join(user_dir, f"{base_filename}.json")
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "guestUid": uid,
        "guestPass": pwd,
        "item_id": item_id,
        "item_name": item_name
    }
    save_deduplicated_json(json_filepath, entry)

    txt_filepath = os.path.join(user_dir, f"{base_filename}.txt")
    txt_line = f"UID: {uid} | Pass: {pwd} | Item: {item_name} | ID: {item_id}\n"
    
    already_exists = False
    if os.path.exists(txt_filepath):
        with open(txt_filepath, "r", encoding="utf-8") as tf:
            if f"UID: {uid}" in tf.read():
                already_exists = True

    if not already_exists:
        with open(txt_filepath, "a", encoding="utf-8") as tf:
            tf.write(txt_line)

    if is_ultra_rare:
        admin_filepath = os.path.join(ADMIN_RESULTS_FOLDER, "admin_naruto_bundle_accounts.json")
        save_deduplicated_json(admin_filepath, entry)
        
        admin_txt = os.path.join(ADMIN_RESULTS_FOLDER, "admin_naruto_bundle_accounts.txt")
        with open(admin_txt, "a", encoding="utf-8") as tf:
            tf.write(txt_line)

def append_summary(chat_id, text_line, is_ultra_rare=False):
    user_dir = os.path.join(RESULT_FOLDER, str(chat_id))
    os.makedirs(user_dir, exist_ok=True)
    filepath = os.path.join(user_dir, "summary_list.txt")
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(text_line + "\n")
        
    if is_ultra_rare:
        admin_summary = os.path.join(ADMIN_RESULTS_FOLDER, "admin_naruto_summary.txt")
        with open(admin_summary, "a", encoding="utf-8") as f:
            f.write(text_line + f" | ChatID: {chat_id}\n")

def get_activated_accounts(chat_id):
    if chat_id in USER_SESSIONS and USER_SESSIONS[chat_id].get("activated_accounts"):
        return USER_SESSIONS[chat_id]["activated_accounts"]
    
    act_file = os.path.join(RESULT_FOLDER, str(chat_id), "activated_accounts.json")
    if os.path.exists(act_file):
        try:
            with open(act_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    USER_SESSIONS.setdefault(chat_id, {})["activated_accounts"] = data
                    return data
        except Exception:
            pass
    return []

# ================= ACCOUNT PARSER =================
def load_accounts_from_text(content):
    content = re.sub(r',\s*}', '}', content)
    content = re.sub(r',\s*]', ']', content)
    accounts = []
    try:
        data = json.loads(content)
        if isinstance(data, list):
            for item in data:
                acc = extract_uid_password(item)
                if acc:
                    accounts.append(acc)
        elif isinstance(data, dict):
            for key in ['accounts', 'users', 'data', 'list']:
                if key in data and isinstance(data[key], list):
                    for item in data[key]:
                        acc = extract_uid_password(item)
                        if acc:
                            accounts.append(acc)
                    if accounts:
                        return accounts
            acc = extract_uid_password(data)
            if acc:
                accounts.append(acc)
    except json.JSONDecodeError:
        pass

    if not accounts:
        accounts = extract_accounts_regex(content)
    return accounts

def extract_uid_password(obj):
    if not isinstance(obj, dict):
        return None
    uid, password = None, None
    uid_keys = ['uid', 'UID', 'userId', 'user_id', 'userid', 'id', 'account_id', 'guestUid']
    for key in uid_keys:
        if key in obj and obj[key] is not None:
            uid = str(obj[key]).strip()
            break
    pwd_keys = ['password', 'pass', 'pwd', 'Password', 'PASSWORD', 'guestPass']
    for key in pwd_keys:
        if key in obj and obj[key] is not None:
            password = str(obj[key]).strip()
            break
    if uid and password:
        return {'uid': uid, 'password': password, 'region': obj.get('region', 'auto'), 'jwt': obj.get('jwt')}
    return None

def extract_accounts_regex(content):
    accounts = []
    pattern = r'["\']?uid["\']?\s*:\s*["\']?(\d+)["\']?[\s\S]*?["\']?password["\']?\s*:\s*["\']([^"\']+)["\']'
    matches = re.findall(pattern, content, re.IGNORECASE)
    for uid, pwd in matches:
        accounts.append({'uid': str(uid).strip(), 'password': str(pwd).strip(), 'region': 'auto'})
    return accounts

# ================= NETWORK REQUESTS =================
async def get_token_external(session, uid, password):
    url = EXTERNAL_JWT_API
    params = {"uid": uid, "password": password}
    try:
        async with session.get(url, params=params, timeout=10) as resp:
            if resp.status == 200:
                try:
                    data = await resp.json()
                except Exception:
                    text = await resp.text()
                    start = text.find("eyJ")
                    if start != -1:
                        end = start
                        while end < len(text) and text[end] not in ['"', ' ', '\n', '\r', '\t', '\x00']:
                            end += 1
                        token = text[start:end]
                        if token.count('.') >= 2:
                            return token
                    return None

                token = data.get("token") or data.get("jwt")
                if token and len(token) > 50 and token.count('.') >= 2:
                    return token
    except Exception:
        pass
    return None

async def get_access_token_garena(session, uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    payload = {
        'uid': uid,
        'password': password,
        'response_type': "token",
        'client_type': "2",
        'client_secret': "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        'client_id': "100067"
    }
    headers = {'User-Agent': "GarenaMSDK/4.0.19P9"}
    try:
        async with session.post(url, data=payload, headers=headers, timeout=8) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('open_id'), data.get('access_token')
    except Exception:
        pass
    return None, None

def build_major_login_proto_2(access_token, open_id, lang="en"):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    model = random.choice(DEVICES)
    carrier = random.choice(CARRIERS)
    gpu = random.choice(GPUS)
    user_id = f"Google|{uuid.uuid4()}"

    fields = {
        3: now, 4: "free fire", 5: 1, 7: "2.127.13",
        8: "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)", 9: "Handheld",
        10: carrier, 11: "WIFI", 12: 1334, 13: 750, 14: "300",
        15: "ARMv7 VFPv3 NEON VMH | 2400 | 2", 16: 1993, 17: gpu,
        18: "OpenGL ES 3.2", 19: user_id, 20: "105.235.139.91",
        21: lang, 22: open_id, 23: "4", 24: "Handheld", 25: model,
        29: access_token, 30: 1, 41: carrier, 42: "WIFI",
        57: "7428b253defc164018c604a1ebbfebdf", 60: 32936, 61: 29430,
        62: 2479, 63: 900, 64: 30823, 65: 32936, 66: 30823, 67: 32936,
        73: 1, 74: "/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm",
        76: 1, 77: "2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk",
        78: 3, 79: 1, 81: "32", 83: "2019118692", 86: "OpenGLES2",
        87: 16383, 88: 4, 92: 9075, 93: "android",
        94: "KqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2",
        95: 111227, 97: 1, 98: 1, 99: "4", 100: "4",
        102: bytes.fromhex("47 51 40 4f 00 0e 5e 00 44 06 55 41 0e 50 4d 0d 13 68 5a 07 54 06 0c 6d 5c 56 0e 6a 59 56 3b 0b 55 35")
    }
    return encrypt_plaintext(star_assemble_proto(fields))

async def major_login_request(session, access_token, open_id, lang="en"):
    url = "https://loginbp.ppmainecoonghj.com/MajorLogin"
    encrypted = build_major_login_proto_2(access_token, open_id, lang)
    headers = {
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "X-Ga-Sv": "1789534056",
        "ReleaseVersion": RELEASE_VERSION,
        "User-Agent": UNITY_USER_AGENT,
        "X-GA": "v1 1",
        "X-Unity-Version": UNITY_VERSION,
    }
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        async with session.post(url, headers=headers, data=encrypted, ssl=ssl_context, timeout=12) as resp:
            if resp.status == 200:
                content = await resp.read()
                if len(content) >= 64:
                    payload = content[64:]
                    if MajorLoginRes_pb2:
                        try:
                            res_msg = MajorLoginRes_pb2.MajorLoginRes()
                            res_msg.ParseFromString(payload)
                            token = getattr(res_msg, "token", None) or getattr(res_msg, "jwt", None) or ""
                            acc_id = getattr(res_msg, "accountId", "") or getattr(res_msg, "account_id", "") or ""
                            region = getattr(res_msg, "region", "") or ""
                            return token, str(acc_id), region or "auto"
                        except Exception:
                            pass
                    text = content.decode('utf-8', errors='ignore')
                    start = text.find("eyJ")
                    if start != -1:
                        end = start
                        while end < len(text) and text[end] not in ['"', ' ', '\n', '\r', '\t', '\x00']:
                            end += 1
                        jwt = text[start:end]
                        if jwt.count('.') >= 2:
                            return jwt, "", "auto"
    except Exception:
        pass
    return None, None, "Failed"

async def choose_region_request(session, jwt_token, region):
    url = "https://loginbp.ppmainecoonghj.com/ChooseRegion"
    plain = star_assemble_proto({"1": region.upper()})
    encrypted = encrypt_plaintext(plain)
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12)",
        "Authorization": f"Bearer {jwt_token}",
        "X-GA": "v1 1",
        "ReleaseVersion": RELEASE_VERSION,
    }
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    try:
        async with session.post(url, data=encrypted, headers=headers, ssl=ssl_context, timeout=8) as resp:
            return resp.status == 200
    except Exception:
        return False

async def get_login_data_request(session, jwt, open_id, region):
    base_url = star_server_url(region)
    host = base_url.replace("https://", "")
    url = f"{base_url}/GetLoginData"

    fields = {
        3: time.strftime("%Y-%m-%d %H:%M:%S"), 4: "free fire", 5: 1, 7: "1.126.15",
        8: "Android OS 10", 9: "Handheld", 10: "T-Mobile", 11: "WIFI",
        12: 1600, 13: 720, 14: "320", 15: "ARM64", 16: 2799, 17: "PowerVR Rogue",
        18: "OpenGL ES 3.2", 19: f"Google|{uuid.uuid4()}", 20: "8.8.8.8",
        21: "en", 22: open_id, 23: "8", 24: "Handheld", 25: "realme RMX2189",
        26: str(region).upper(), 29: jwt, 30: 1, 41: "T-Mobile", 42: "WIFI",
        57: "1ac4b80ecf0478a44203bf8fac6120f5", 97: 1, 99: "30", 100: "38"
    }
    encrypted = encrypt_plaintext(star_assemble_proto(fields))
    headers = {
        "Host": host,
        "User-Agent": UNITY_USER_AGENT,
        "Authorization": f"Bearer {jwt}",
        "X-GA": "v1 1",
        "ReleaseVersion": RELEASE_VERSION,
        "Content-Type": "application/octet-stream"
    }
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    try:
        async with session.post(url, headers=headers, data=encrypted, ssl=ssl_context, timeout=10) as resp:
            if resp.status == 200:
                return await resp.read()
    except Exception:
        pass
    return None

async def get_token_combined(session, uid, password):
    token = await get_token_external(session, uid, password)
    if token:
        return token
    open_id, access_token = await get_access_token_garena(session, uid, password)
    if open_id and access_token:
        jwt, _, _ = await major_login_request(session, access_token, open_id)
        if jwt:
            return jwt
    return None

async def send_spin_request(session, url, jwt, payload_hex):
    payload = bytes.fromhex(payload_hex)
    headers = {
        "Authorization": f"Bearer {jwt}",
        "X-GA": "v1 1",
        "ReleaseVersion": RELEASE_VERSION,
        "Content-Type": "application/octet-stream",
        "User-Agent": UNITY_USER_AGENT
    }
    try:
        async with session.post(url, headers=headers, data=payload, timeout=10, ssl=False) as resp:
            return resp.status, await resp.read()
    except Exception as e:
        return 0, str(e).encode()

# ================= FAST SPIN LOGIC =================
async def process_single_account_spin(session, purchase_url, chat_id, acc, update_obj):
    uid = str(acc.get("uid", ""))
    pwd = str(acc.get("password", ""))
    token = acc.get("jwt")

    if not token:
        token = await get_token_combined(session, uid, pwd)
        
    if not token:
        return {"status": "failed", "item_id": None}

    status_code, spin_resp = await send_spin_request(session, purchase_url, token, RAW_HEX_PAYLOAD)
    if status_code != 200:
        return {"status": "failed", "item_id": None}

    try:
        spin_decoded, _ = blackboxprotobuf.decode_message(spin_resp)
        item_id = find_item_id(spin_decoded)

        if item_id is None:
            return {"status": "failed", "item_id": None}

        if item_id in RARE_ITEMS_DB:
            item_info = RARE_ITEMS_DB[item_id]
            item_name = item_info["name"]
            target_file = item_info["file"]
            is_ultra = (item_id in ULTRA_RARE_IDS)

            save_item_to_specific_file(chat_id, uid, pwd, item_id, item_name, target_file, is_ultra_rare=is_ultra)

            if is_ultra:
                append_summary(chat_id, f"[ULTRA RARE] UID: {uid} | Pass: {pwd} | Item: {item_name} | ID: {item_id}", is_ultra_rare=True)
                await update_obj.message.reply_text(
                    f"👑 **NARUTO BUNDLE DROPPED!** 👑\n\n"
                    f"👤 **UID:** `{uid}`\n"
                    f"🔑 **Password:** `{pwd}`\n"
                    f"🎁 **Item:** `{item_name}`"
                )
                return {"status": "ultra_rare", "item_id": item_id}
            else:
                append_summary(chat_id, f"[RARE] UID: {uid} | Pass: {pwd} | Item: {item_name} | ID: {item_id}")
                return {"status": "rare", "item_id": item_id}
        else:
            item_name = f"Item_{item_id}"
            save_item_to_specific_file(chat_id, uid, pwd, item_id, item_name, "other_items")
            append_summary(chat_id, f"[NORMAL] UID: {uid} | Pass: {pwd} | Item: {item_name} | ID: {item_id}")
            return {"status": "normal", "item_id": item_id}

    except Exception:
        return {"status": "failed", "item_id": None}

async def execute_spin_process(update, context, chat_id, accounts):
    server_key = USER_SESSIONS[chat_id].get("server", "1")
    server_info = SERVERS[server_key]
    purchase_url = f"{server_info['url']}/PurchaseGacha"

    total_accs = len(accounts)
    status_msg = await update.message.reply_text(
        f"🚀 **Fast Spin Task Started!**\n\n"
        f"🌐 **Server:** `{server_info['name']}`\n"
        f"👥 **Total Accounts:** `{total_accs}`\n"
        f"⏳ Processing spins concurrently..."
    )

    user_dir = os.path.join(RESULT_FOLDER, str(chat_id))
    os.makedirs(user_dir, exist_ok=True)

    stats = {"total": 0, "ultra_rare": 0, "rare": 0, "failed": 0}
    item_counts = {item_id: 0 for item_id in RARE_ITEMS_DB.keys()}

    batch_size = 5

    async with aiohttp.ClientSession() as session:
        for i in range(0, total_accs, batch_size):
            batch = accounts[i:i + batch_size]
            tasks = [process_single_account_spin(session, purchase_url, chat_id, acc, update) for acc in batch]
            results = await asyncio.gather(*tasks)

            for res in results:
                st = res.get("status")
                itm_id = res.get("item_id")

                if itm_id in item_counts:
                    item_counts[itm_id] += 1

                if st == "failed":
                    stats["failed"] += 1
                elif st == "ultra_rare":
                    stats["ultra_rare"] += 1
                    stats["rare"] += 1
                    stats["total"] += 1
                elif st == "rare":
                    stats["rare"] += 1
                    stats["total"] += 1
                elif st == "normal":
                    stats["total"] += 1

            processed = min(i + batch_size, total_accs)
            progress_str = create_progress_bar(processed, total_accs)
            try:
                await status_msg.edit_text(
                    f"⚡ **Fast Auto Spinner Progress** ⚡\n\n"
                    f"🌐 Server: `{server_info['name']}`\n"
                    f"📊 Progress: `{progress_str}` ({processed}/{total_accs})\n\n"
                    f"👑 Naruto Bundle: `{stats['ultra_rare']}`\n"
                    f"🎁 Rare Items: `{stats['rare']}`\n"
                    f"❌ Failed: `{stats['failed']}`"
                )
            except Exception:
                pass

    item_summary_lines = ""
    for item_id, info in RARE_ITEMS_DB.items():
        cnt = item_counts.get(item_id, 0)
        item_summary_lines += f"🔹 {info['name']}: `{cnt}`\n"

    await status_msg.edit_text(
        f"✅ **Process Completed Successfully!**\n\n"
        f"🌐 **Server:** `{server_info['name']}`\n"
        f"👥 **Total Processed:** `{total_accs}`\n"
        f"📦 **Total Won Items:** `{stats['total']}`\n"
        f"❌ **Failed Accounts:** `{stats['failed']}`\n\n"
        f"🎁 **REWARDS BREAKDOWN:**\n"
        f"{item_summary_lines}\n"
        f"📥 *নিচে প্রতিটি রিওয়ার্ডের পৃথক টেক্সট ফাইল পাঠানো হচ্ছে...*"
    )

    if os.path.exists(user_dir):
        files = os.listdir(user_dir)
        for file_name in files:
            file_path = os.path.join(user_dir, file_name)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    await context.bot.send_document(chat_id=chat_id, document=f, filename=file_name)

# ================= TELEGRAM KEYBOARD MENU =================
def get_main_reply_keyboard(chat_id):
    keyboard = [
        [KeyboardButton("⚡ Auto Spinner"), KeyboardButton("🔓 Active Account")],
        [KeyboardButton("📜 View Logs"), KeyboardButton("🗑️ Delete Accounts")],
        [KeyboardButton("ℹ️ Help")]
    ]

    if is_admin(chat_id):
        keyboard.append([KeyboardButton("👑 Admin Panel")])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ================= TELEGRAM BOT HANDLERS =================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in USER_SESSIONS:
        USER_SESSIONS[chat_id] = {"mode": "idle", "server": "1", "activated_accounts": []}

    welcome_text = (
        "🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨\n"
        "⚡ **FREE FIRE SPINNER BOT** ⚡\n"
        "🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨\n\n"
        "👑 **Created by:** `YASIN BHAI`\n"
        "📢 **Channel:** `https://t.me/freefireob51`\n\n"
        "👇 নিচের কিবোর্ড বাটন থেকে সার্ভিস নির্বাচন করুন:"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_reply_keyboard(chat_id))

async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    if chat_id not in USER_SESSIONS:
        USER_SESSIONS[chat_id] = {"mode": "idle", "server": "1", "activated_accounts": []}

    if text == "⚡ Auto Spinner":
        server_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("🇧🇩 Bangladesh Server"), KeyboardButton("🇮🇳 India Server")],
            [KeyboardButton("🔙 Main Menu")]
        ], resize_keyboard=True)

        await update.message.reply_text(
            "⚡ **Auto Spinner - Server Select** ⚡\n\n"
            "অনুগ্রহ করে স্পিন করার জন্য সার্ভার নির্বাচন করুন:",
            reply_markup=server_keyboard
        )

    elif text in ["🇧🇩 Bangladesh Server", "🇮🇳 India Server"]:
        server_key = "1" if "Bangladesh" in text else "2"
        USER_SESSIONS[chat_id]["server"] = server_key
        USER_SESSIONS[chat_id]["mode"] = "selecting_spin"
        server_name = SERVERS[server_key]["name"]

        saved_accs = get_activated_accounts(chat_id)
        
        spin_buttons = []
        if saved_accs:
            spin_buttons.append([KeyboardButton(f"▶️ Start Spin ({len(saved_accs)} Active Accounts)")])
        
        spin_buttons.append([KeyboardButton("🔙 Main Menu")])
        spin_keyboard = ReplyKeyboardMarkup(spin_buttons, resize_keyboard=True)

        msg = f"✅ **Server Selected:** `{server_name}`\n\n"
        if saved_accs:
            msg += f"🔥 **{len(saved_accs)}** টি একটিভ অ্যাকাউন্ট সেভ করা আছে!\n"
            msg += f"স্পিন শুরু করতে **▶️ Start Spin** বাটনে ক্লিক করুন।"
        else:
            msg += "❌ **কোনো একটিভ অ্যাকাউন্ট পাওয়া যায়নি!**\nঅটো স্পিন করার আগে `🔓 Active Account` মেনু থেকে ফাইল আপলোড করে একাউন্ট একটিভ করে নিন।"

        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=spin_keyboard)

    elif text.startswith("▶️ Start Spin"):
        saved_accs = get_activated_accounts(chat_id)
        if not saved_accs:
            await update.message.reply_text("❌ কোনো একটিভ একাউন্ট পাওয়া যায়নি! আগে `🔓 Active Account` চাপ দিয়ে একাউন্ট ফাইল দিন।")
            return
        
        await execute_spin_process(update, context, chat_id, saved_accs)

    elif text == "🔓 Active Account":
        USER_SESSIONS[chat_id]["mode"] = "awaiting_activate_file"
        await update.message.reply_text(
            "🔓 **Account Activator System** 🔓\n\n"
            "📂 আপনার `accounts.json` বা `.txt` ফাইলটি সেন্ড করুন।\n"
            "বট প্রতিটি অ্যাকাউন্ট চেক করে **Server (Bangladesh / India)** ডিটেক্ট এবং একটিভ করে রাখবে।",
            reply_markup=get_main_reply_keyboard(chat_id)
        )

    elif text == "📜 View Logs":
        user_dir = os.path.join(RESULT_FOLDER, str(chat_id))
        summary_file = os.path.join(user_dir, "summary_list.txt")

        if os.path.exists(summary_file):
            with open(summary_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-15:]
            log_text = "".join(lines)
            msg = f"📜 **Recent Activity Logs:**\n\n```{log_text}```"
        else:
            msg = "📜 **No logs found for your session.**"

        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🗑️ Delete Accounts":
        user_dir = os.path.join(RESULT_FOLDER, str(chat_id))
        if os.path.exists(user_dir):
            for f in os.listdir(user_dir):
                try:
                    os.remove(os.path.join(user_dir, f))
                except Exception:
                    pass
        USER_SESSIONS[chat_id]["activated_accounts"] = []
        USER_SESSIONS[chat_id]["mode"] = "idle"

        await update.message.reply_text(
            "🗑️ **All Session Accounts and Logs Deleted Successfully!**\n\n"
            "আপনি এখন নতুন করে ফাইল আপলোড করতে পারেন।",
            reply_markup=get_main_reply_keyboard(chat_id)
        )

    elif text == "ℹ️ Help":
        help_text = (
            "📖 **বট ব্যবহারের সঠিক নিয়মাবলিনী:**\n\n"
            "1️⃣ **প্রথম ধাপ (অ্যাকোউন্ট একটিভ):**\n"
            "• `🔓 Active Account` বাটনে চাপুন।\n"
            "• আপনার গেস্ট একাউন্টের JSON বা TXT ফাইল আপলোড দিন। একাউন্টগুলো বাংলাদেশ/ইন্ডিয়া সার্ভার ডিটেক্ট হয়ে অটোমেটিক একটিভ সেভ হবে।\n\n"
            "2️⃣ **দ্বিতীয় ধাপ (অটো স্পিন):**\n"
            "• `⚡ Auto Spinner` বাটনে চাপুন।\n"
            "• আপনার পছন্দের **Server (Bangladesh/India)** সিলেক্ট করুন।\n"
            "• **▶️ Start Spin** এ ক্লিক করলেই একটিভ হওয়া একাউন্টগুলোতে ইনস্ট্যান্ট স্পিন শুরু হবে।"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")

    elif text == "👑 Admin Panel":
        if not is_admin(chat_id):
            await update.message.reply_text("❌ আপনার এই অপশনে অ্যাক্সেস নেই।")
            return

        admin_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("📦 Download Naruto Accounts")],
            [KeyboardButton("📥 Download admin.txt")],
            [KeyboardButton("🔙 Main Menu")]
        ], resize_keyboard=True)

        await update.message.reply_text(
            "👑 **Welcome to Admin Panel** 👑\n\n"
            "এখান থেকে আপনি ইউজারদের পাওয়া সমস্ত **Naruto Bundle** এর UID & Password ডাউনলোড করতে পারবেন।",
            reply_markup=admin_keyboard
        )

    elif text == "📦 Download Naruto Accounts":
        if not is_admin(chat_id):
            return

        if os.path.exists(ADMIN_RESULTS_FOLDER):
            files = os.listdir(ADMIN_RESULTS_FOLDER)
            if not files:
                await update.message.reply_text("❌ কোনো নারুতো বান্ডেলের সেভ করা ডাটা পাওয়া যায়নি।")
                return
            for fname in files:
                fpath = os.path.join(ADMIN_RESULTS_FOLDER, fname)
                if os.path.isfile(fpath):
                    with open(fpath, "rb") as f:
                        await context.bot.send_document(chat_id=chat_id, document=f, filename=f"ADMIN_{fname}")
        else:
            await update.message.reply_text("❌ অ্যাডমিন রেজাল্ট ফোল্ডার ফাঁকা।")

    elif text == "📥 Download admin.txt":
        if not is_admin(chat_id):
            return

        if os.path.exists(ADMIN_TXT_FILE):
            with open(ADMIN_TXT_FILE, "rb") as f:
                await context.bot.send_document(chat_id=chat_id, document=f, filename="admin.txt")
        else:
            await update.message.reply_text("❌ `admin.txt` ফাইলটি খুঁজে পাওয়া যায়নি।")

    elif text == "🔙 Main Menu":
        USER_SESSIONS[chat_id]["mode"] = "idle"
        await update.message.reply_text(
            "⚡ **Main Menu** ⚡\n\nউপলব্ধ অপশনগুলো নির্বাচন করুন:",
            reply_markup=get_main_reply_keyboard(chat_id)
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in USER_SESSIONS:
        USER_SESSIONS[chat_id] = {"mode": "idle", "server": "1", "activated_accounts": []}

    mode = USER_SESSIONS[chat_id].get("mode")

    # ================= AUTO SPINNER RESTRICTION =================
    if mode != "awaiting_activate_file":
        await update.message.reply_text(
            "❌ **Auto Spinner মেনু থেকে সরাসরি কোনো ফাইল আপলোড করা যাবে না!**\n\n"
            "স্পিন করতে হলে প্রথমে `🔓 Active Account` বাটনে চেপে ফাইল দিয়ে একাউন্ট একটিভ করুন, তারপর `▶️ Start Spin` বাটনে চাপুন।"
        )
        return

    # ================= ACCOUNT ACTIVATION =================
    document = update.message.document
    file = await context.bot.get_file(document.file_id)
    file_bytes = await file.download_as_bytearray()
    content = file_bytes.decode('utf-8', errors='ignore')

    accounts = load_accounts_from_text(content)
    if not accounts:
        await update.message.reply_text("❌ ফাইল থেকে কোনো ভ্যালিড অ্যাকাউন্ট (UID/Password) পাওয়া যায়নি।")
        return

    total_accs = len(accounts)
    status_msg = await update.message.reply_text(
        f"🔄 **Account Activation Started!**\n\n"
        f"👥 **Total Accounts:** `{total_accs}`\n"
        f"⏳ Detecting Server & Activating..."
    )

    success_count = 0
    failed_count = 0
    bd_count = 0
    ind_count = 0
    activated_list = []

    async with aiohttp.ClientSession() as session:
        for idx, acc in enumerate(accounts, start=1):
            uid = acc['uid']
            pwd = acc['password']
            req_region = acc.get('region', 'auto')

            open_id, access_token = await get_access_token_garena(session, uid, pwd)
            if not open_id or not access_token:
                failed_count += 1
                continue

            jwt, acc_id, detected_reg = await major_login_request(session, access_token, open_id)
            if not jwt:
                failed_count += 1
                continue

            region_to_use = detected_reg if detected_reg != "auto" else (req_region if req_region != "auto" else "IND")
            await choose_region_request(session, jwt, region_to_use)

            login_data = await get_login_data_request(session, jwt, open_id, region_to_use)
            if login_data:
                success_count += 1
                reg_code = str(region_to_use).upper()
                if reg_code == "IND":
                    ind_count += 1
                    server_label = "India 🇮🇳"
                else:
                    bd_count += 1
                    server_label = "Bangladesh 🇧🇩"

                activated_list.append({
                    "uid": uid,
                    "password": pwd,
                    "region": reg_code,
                    "server_label": server_label,
                    "jwt": jwt
                })
            else:
                failed_count += 1

            if idx % 2 == 0 or idx == total_accs:
                progress_str = create_progress_bar(idx, total_accs)
                try:
                    await status_msg.edit_text(
                        f"🔄 **Activation Progress:**\n"
                        f"`{progress_str}` ({idx}/{total_accs})\n\n"
                        f"🇧🇩 BD Accounts: `{bd_count}`\n"
                        f"🇮🇳 IND Accounts: `{ind_count}`\n"
                        f"✅ Total Success: `{success_count}`\n"
                        f"❌ Failed: `{failed_count}`"
                    )
                except Exception:
                    pass

    USER_SESSIONS[chat_id]["activated_accounts"] = activated_list
    USER_SESSIONS[chat_id]["mode"] = "idle"

    user_dir = os.path.join(RESULT_FOLDER, str(chat_id))
    os.makedirs(user_dir, exist_ok=True)
    act_file = os.path.join(user_dir, "activated_accounts.json")
    with open(act_file, 'w', encoding='utf-8') as f:
        json.dump(activated_list, f, indent=4)

    await status_msg.edit_text(
        f"✅ **Activation Completed Successfully!**\n\n"
        f"👥 **Total Accounts:** `{total_accs}`\n"
        f"🇧🇩 **Bangladesh Server:** `{bd_count}`\n"
        f"🇮🇳 **India Server:** `{ind_count}`\n"
        f"✅ **Total Activated:** `{success_count}`\n"
        f"❌ **Failed:** `{failed_count}`\n\n"
        f"💡 আপনি এখন **⚡ Auto Spinner** মেনুতে গিয়ে সার্ভার সিলেক্ট করে সরাসরি স্পিন মারতে পারেন।"
    )

# ================= MAIN BOT RUNNER =================
def main():
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("[!] Please configure your actual Telegram Bot Token in BOT_TOKEN variable.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_buttons))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("[✔] Free Fire Telegram Bot started polling successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()
