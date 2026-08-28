# ======================================================================
#  NIROB BBZ - MULTI ACCOUNT ROOM BOT (API)
#
#  /join?room=123456&password=0000   -> every bot joins the custom room
#  /join?bot=20&room=...&password=... -> only the first N bots join
#  /leave?room=123456                -> every bot leaves the room
#  /leave                            -> leave whatever room they are in
#  /status                           -> per-bot connection + room state
#
#  Packet formats are customized and branded for NIROB BBZ
# ======================================================================

import requests, os, json, time, asyncio, random, base64, binascii, re, socket, ssl, subprocess, sys, pickle, signal
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import aiohttp
from NIROBxC4 import *
from xHeaders import *
from flask import Flask, request, jsonify
from threading import Thread
from datetime import datetime

app = Flask(__name__)

# ==================== ACCOUNTS ====================
# Every account below logs in and stays online at the same time.
# Set MAX_ACCOUNTS to a number to use only the first N of them.
MAX_ACCOUNTS = None

ACCOUNTS = [
    {"uid": "7206241106", "password": "speed x_NIROB_BBZ_gt0UOKzt"},
    {"uid": "7206240760", "password": "speed x_NIROB_BBZ_3NMqrgfl"},
    {"uid": "7206241208", "password": "speed x_NIROB_BBZ_3HzGrcgt"},
    {"uid": "7206240942", "password": "speed x_NIROB_BBZ_x5Un69Ns"},
    {"uid": "7206241275", "password": "speed x_NIROB_BBZ_pgTB1smf"},
    {"uid": "7206241041", "password": "speed x_NIROB_BBZ_SaYJISeo"},
    {"uid": "7206241447", "password": "speed x_NIROB_BBZ_lLHIFnCa"},
    {"uid": "7206240807", "password": "speed x_NIROB_BBZ_dsoo2JrW"},
    {"uid": "7206240808", "password": "speed x_NIROB_BBZ_lvmhmbxw"},
    {"uid": "7206241000", "password": "speed x_NIROB_BBZ_JEPRlmqC"},
    {"uid": "7206241097", "password": "speed x_NIROB_BBZ_nVYJ0PWZ"},
    {"uid": "7206266454", "password": "speed x_NIROB_BBZ_wmEDq8yR"},
    {"uid": "7206267446", "password": "speed x_NIROB_BBZ_IfvUnf8v"},
    {"uid": "7206267879", "password": "speed x_NIROB_BBZ_4s8TuoO9"},
    {"uid": "7206267637", "password": "speed x_NIROB_BBZ_jZ13htKk"},
    {"uid": "7206266830", "password": "speed x_NIROB_BBZ_o2Er0DaT"},
    {"uid": "7206267342", "password": "speed x_NIROB_BBZ_R36Na7oY"},
    {"uid": "7206266461", "password": "speed x_NIROB_BBZ_c1UQQQ4h"},
    {"uid": "7206267549", "password": "speed x_NIROB_BBZ_2WxEIk8I"},
    {"uid": "7206267651", "password": "speed x_NIROB_BBZ_AyIZiIiC"},
    {"uid": "7206293083", "password": "speed x_NIROB_BBZ_dmw9wlPJ"},
    {"uid": "7206293593", "password": "speed x_NIROB_BBZ_ZEZoLVl3"},
    {"uid": "7206293757", "password": "speed x_NIROB_BBZ_Ci648Zq1"},
    {"uid": "7206294369", "password": "speed x_NIROB_BBZ_eDaHspQb"},
    {"uid": "7206294074", "password": "speed x_NIROB_BBZ_5pXQZZxK"},
    {"uid": "7206292940", "password": "speed x_NIROB_BBZ_OT5ckJgq"},
    {"uid": "7206294292", "password": "speed x_NIROB_BBZ_SM7MdnUb"},
    {"uid": "7206293659", "password": "speed x_NIROB_BBZ_VCNhxk7P"},
    {"uid": "7206293112", "password": "speed x_NIROB_BBZ_YYLS6wG3"},
    {"uid": "7206294429", "password": "speed x_NIROB_BBZ_yBtOUj9Q"},
    {"uid": "7206293187", "password": "speed x_NIROB_BBZ_eSH9yWJs"},
    {"uid": "7206319299", "password": "speed x_NIROB_BBZ_r0g3QQbr"},
    {"uid": "7206320592", "password": "speed x_NIROB_BBZ_7q0LNC3b"},
    {"uid": "7206320271", "password": "speed x_NIROB_BBZ_X4cMA3qT"},
    {"uid": "7206320527", "password": "speed x_NIROB_BBZ_4RsWEvuM"},
    {"uid": "7206320235", "password": "speed x_NIROB_BBZ_NaPxF8nf"},
    {"uid": "7206320530", "password": "speed x_NIROB_BBZ_lvYYljmO"},
    {"uid": "7206320519", "password": "speed x_NIROB_BBZ_wH0mTIi6"},
    {"uid": "7206320590", "password": "speed x_NIROB_BBZ_dC01vOrA"},
    {"uid": "7206319351", "password": "speed x_NIROB_BBZ_MaQrBuGZ"},
    {"uid": "7206320155", "password": "speed x_NIROB_BBZ_G2xzIpZy"},
    {"uid": "7206319676", "password": "speed x_NIROB_BBZ_Xri8tazh"},
    {"uid": "7206319346", "password": "speed x_NIROB_BBZ_91uIL21S"},
    {"uid": "7206321096", "password": "speed x_NIROB_BBZ_hzs3n9CC"},
    {"uid": "7206320559", "password": "speed x_NIROB_BBZ_M6z7NOQD"},
    {"uid": "7206319421", "password": "speed x_NIROB_BBZ_JQWkDA9l"},
    {"uid": "7206345911", "password": "speed x_NIROB_BBZ_wqOTCOEL"},
    {"uid": "7206345871", "password": "speed x_NIROB_BBZ_Z7yTG26g"},
    {"uid": "7206347671", "password": "speed x_NIROB_BBZ_dlHMnYVq"},
    {"uid": "7206346436", "password": "speed x_NIROB_BBZ_phobGqkK"},
    {"uid": "7206346772", "password": "speed x_NIROB_BBZ_nnZYjOZr"},
    {"uid": "7206346871", "password": "speed x_NIROB_BBZ_IT9ZGvSR"},
    {"uid": "7206350176", "password": "speed x_NIROB_BBZ_sjg7SUq8"},
    {"uid": "7206353022", "password": "speed x_NIROB_BBZ_bButnLf8"},
    {"uid": "7206350151", "password": "speed x_NIROB_BBZ_PnTlQw2w"},
    {"uid": "7206350275", "password": "speed x_NIROB_BBZ_vnRWGGl2"},
    {"uid": "7206352937", "password": "speed x_NIROB_BBZ_UMQqLH0M"},
    {"uid": "7206346244", "password": "speed x_NIROB_BBZ_g6mlEUBw"},
    {"uid": "7206351377", "password": "speed x_NIROB_BBZ_wC5TSUUn"},
    {"uid": "7206353219", "password": "speed x_NIROB_BBZ_EfupI3nJ"},
    {"uid": "7206350669", "password": "speed x_NIROB_BBZ_lTwq149i"},
    {"uid": "7206352969", "password": "speed x_NIROB_BBZ_pcTxdYaa"},
    {"uid": "7206352880", "password": "speed x_NIROB_BBZ_mD7p5HmP"},
    {"uid": "7206350816", "password": "speed x_NIROB_BBZ_JHwMN12l"},
    {"uid": "7206352829", "password": "speed x_NIROB_BBZ_dqP9DdNJ"},
    {"uid": "7206353386", "password": "speed x_NIROB_BBZ_ZzfzzqtO"},
    {"uid": "7206352796", "password": "speed x_NIROB_BBZ_jhiyQuGN"},
    {"uid": "7206353017", "password": "speed x_NIROB_BBZ_c14ry9qB"},
    {"uid": "7206353091", "password": "speed x_NIROB_BBZ_niwPsznC"},
    {"uid": "7206350486", "password": "speed x_NIROB_BBZ_DxjVLTwL"},
    {"uid": "7206352816", "password": "speed x_NIROB_BBZ_fkIqEqIu"},
    {"uid": "7206350902", "password": "speed x_NIROB_BBZ_r06Cx2S5"},
    {"uid": "7206352744", "password": "speed x_NIROB_BBZ_d6Cfw3Ma"},
    {"uid": "7206353239", "password": "speed x_NIROB_BBZ_fSR8fNaa"},
    {"uid": "7206357335", "password": "speed x_NIROB_BBZ_SCReWXjn"},
    {"uid": "7206351380", "password": "speed x_NIROB_BBZ_kzlP7EI9"},
    {"uid": "7206353072", "password": "speed x_NIROB_BBZ_QuLgyCdU"},
    {"uid": "7206350908", "password": "speed x_NIROB_BBZ_tDuXiElp"},
    {"uid": "7206353051", "password": "speed x_NIROB_BBZ_Jus9GKkb"},
    {"uid": "7206353127", "password": "speed x_NIROB_BBZ_F3mx0mhd"},
    {"uid": "7206353037", "password": "speed x_NIROB_BBZ_kEbto7pF"},
    {"uid": "7206357245", "password": "speed x_NIROB_BBZ_ekL3a5FF"},
    {"uid": "7206357476", "password": "speed x_NIROB_BBZ_OFu7OeA7"},
    {"uid": "7206352820", "password": "speed x_NIROB_BBZ_ufbfiDpv"},
    {"uid": "7206354458", "password": "speed x_NIROB_BBZ_xkuUZ2Yo"},
    {"uid": "7206352948", "password": "speed x_NIROB_BBZ_1dQ5NAj3"},
    {"uid": "7206353078", "password": "speed x_NIROB_BBZ_PKd02obv"},
    {"uid": "7206353932", "password": "speed x_NIROB_BBZ_ICuVGPjm"},
    {"uid": "7206351391", "password": "speed x_NIROB_BBZ_bzIXh3De"},
    {"uid": "7206357422", "password": "speed x_NIROB_BBZ_aM2uco8Y"},
    {"uid": "7206356546", "password": "speed x_NIROB_BBZ_0lP3Hl0U"},
    {"uid": "7206352842", "password": "speed x_NIROB_BBZ_xUKpQsvS"},
    {"uid": "7206357681", "password": "speed x_NIROB_BBZ_MTJPC2eE"},
    {"uid": "7206357138", "password": "speed x_NIROB_BBZ_skcK7Am7"},
    {"uid": "7206357458", "password": "speed x_NIROB_BBZ_K0JGyHBC"},
    {"uid": "7206357649", "password": "speed x_NIROB_BBZ_nW1TJLp9"},
    {"uid": "7206357396", "password": "speed x_NIROB_BBZ_iuXJuUsd"},
]

if MAX_ACCOUNTS is None:
    MAX_ACCOUNTS = len(ACCOUNTS)

# ==================== SETTINGS ====================
JOIN_CHAT_DELAY = 0.25           
JOIN_REPLY_TIMEOUT = 8.0         
JOIN_DEBUG = False               

JOIN_ERRORS = {
    1: "Wrong password",
    2: "Room is full",
    3: "Room not found",
    4: "Room is closed",
    5: "Already in this room",
}
LOGIN_BATCH_SIZE = 12            
LOGIN_BATCH_GAP = 2.5

KEEPALIVE_INTERVAL = 20          
RECONNECT_BASE_DELAY = 3
RECONNECT_MAX_DELAY = 60

# ==================== STATE ====================
region = "IND"
loop = None
bot_running = True
bot_start_time = None

SESSIONS = {}
SESSIONS_LOCK = None
JOIN_IN_PROGRESS = {"busy": False, "room": None}


# ==================== PROTOCOL SHIM ====================
def _encode_varint(value):
    out = bytearray()
    value = int(value)
    if value < 0:
        value += 1 << 64
    while True:
        chunk = value & 0x7F
        value >>= 7
        if value:
            out.append(chunk | 0x80)
        else:
            out.append(chunk)
            break
    return bytes(out)


def create_protobuf_packet(fields):
    out = bytearray()

    for field_num, value in fields.items():
        field_num = int(field_num)

        if isinstance(value, bool):
            value = int(value)

        if isinstance(value, int):
            out += _encode_varint((field_num << 3) | 0)
            out += _encode_varint(value)

        elif isinstance(value, str):
            data = value.encode('utf-8')
            out += _encode_varint((field_num << 3) | 2)
            out += _encode_varint(len(data))
            out += data

        elif isinstance(value, (bytes, bytearray)):
            out += _encode_varint((field_num << 3) | 2)
            out += _encode_varint(len(value))
            out += bytes(value)

        elif isinstance(value, dict):
            nested = create_protobuf_packet(value)
            out += _encode_varint((field_num << 3) | 2)
            out += _encode_varint(len(nested))
            out += nested

        elif value is None:
            continue

        else:
            data = str(value).encode('utf-8')
            out += _encode_varint((field_num << 3) | 2)
            out += _encode_varint(len(data))
            out += data

    return bytes(out)


def dec_to_hex(n):
    h = format(int(n), 'x')
    return h if len(h) % 2 == 0 else '0' + h


def encrypt_packet(packet_hex, enc_key, enc_iv):
    if isinstance(enc_key, str):
        enc_key = enc_key.encode()
    if isinstance(enc_iv, str):
        enc_iv = enc_iv.encode()

    if isinstance(packet_hex, (bytes, bytearray)):
        data = bytes(packet_hex)
    else:
        data = bytes.fromhex(packet_hex)

    return AES.new(enc_key, AES.MODE_CBC, enc_iv).encrypt(pad(data, AES.block_size)).hex()


def patch_protocol_module():
    import sys

    targets = []
    for fname in ("join_room_chanel", "GeneRaTePk", "CrEaTe_ProTo"):
        fn = globals().get(fname)
        if fn is None:
            continue
        mod = sys.modules.get(getattr(fn, "__module__", ""), None)
        if mod is not None and mod not in targets:
            targets.append(mod)

    injected = []
    for mod in targets:
        for helper_name, helper in (
            ("create_protobuf_packet", create_protobuf_packet),
            ("dec_to_hex", dec_to_hex),
            ("encrypt_packet", encrypt_packet),
        ):
            if not hasattr(mod, helper_name):
                setattr(mod, helper_name, helper)
                injected.append(f"{mod.__name__}.{helper_name}")

    if injected:
        print(f"[SHIM] Injected: {', '.join(injected)}")
    else:
        print("[SHIM] Nothing to inject (module already complete)")

    return injected


# ==================== PACKET HELPERS ====================

def aes_encrypt_hex(packet_hex, enc_key, enc_iv):
    if isinstance(enc_key, str):
        enc_key = enc_key.encode()
    if isinstance(enc_iv, str):
        enc_iv = enc_iv.encode()
    data = bytes.fromhex(packet_hex)
    return AES.new(enc_key, AES.MODE_CBC, enc_iv).encrypt(pad(data, AES.block_size)).hex()


def wrap_packet(packet_hex, header, enc_key, enc_iv):
    encrypted = aes_encrypt_hex(packet_hex, enc_key, enc_iv)
    length = len(encrypted) // 2
    return bytes.fromhex(header + format(length, '08x') + encrypted)


# ==================== ROOM PACKETS ====================

async def build_join_packet(room_id, password, session):
    fields = {
        1: 3,
        2: {
            1: int(room_id),
            2: str(password),
            8: {1: "IDC3", 2: 149, 3: (session.get("region") or "IND").upper()},
            9: b"\x01\x03\x04\x07\x09\x0a\x0b\x12\x0e\x16\x19\x20\x1d",
            10: 1,
            12: {},
            13: 1,
            14: 1,
            16: "en",
            22: {1: 21},
        }
    }
    proto = await CrEaTe_ProTo(fields)
    return wrap_packet(proto.hex(), "0e15", session["key"], session["iv"])


async def build_leave_packet(room_id, session):
    fields = {
        1: 6,
        2: {
            1: int(room_id),
            8: {1: "IDC3", 2: 149, 3: (session.get("region") or "IND").upper()},
            9: b"\x01\x03\x04\x07\x09\x0a\x0b\x12\x0e\x16\x19\x20\x1d",
            10: 1,
            13: 1,
            14: 1,
            16: "en",
            22: {1: 21},
        }
    }
    proto = await CrEaTe_ProTo(fields)
    return wrap_packet(proto.hex(), "0e15", session["key"], session["iv"])


async def build_room_chat_join_packet(room_id, session):
    maker = globals().get("join_room_chanel")
    if not maker:
        return None
    try:
        r = maker(room_id, session["key"], session["iv"])
        if asyncio.iscoroutine(r):
            r = await r
        return r
    except Exception as e:
        print(f"[ROOM CHAT] join_room_chanel failed: {e}")
        return None


# ==================== JOIN REPLY ====================

def interpret_join_reply(parsed):
    if not isinstance(parsed, dict):
        return False, "Unreadable reply"

    def unwrap(node):
        if isinstance(node, dict) and "data" in node:
            return node["data"]
        return node

    body = unwrap(parsed.get("5")) or unwrap(parsed.get("2")) or parsed
    if not isinstance(body, dict):
        body = parsed

    for f in ("3", "4", "5", "2"):
        v = unwrap(body.get(f))
        if isinstance(v, int) and v in JOIN_ERRORS:
            return False, JOIN_ERRORS[v]

    for f in ("1", "2"):
        v = unwrap(body.get(f))
        if isinstance(v, int) and v > 1000:
            return True, f"Joined {v}"
        if isinstance(v, dict):
            inner = unwrap(v.get("1"))
            if isinstance(inner, int) and inner > 1000:
                return True, f"Joined {inner}"

    return False, "Rejected by server"


# ==================== ROOM ACTIONS ====================

async def join_one(session, room_id, password):
    if not session.get("writer"):
        return {"uid": session["uid"], "ok": False, "message": "Not connected"}

    if str(session.get("in_room") or "") == str(room_id):
        return {"uid": session["uid"], "ok": True, "message": "Already in room"}

    session["join_event"] = asyncio.Event()
    session["join_result"] = {}

    try:
        pkt = await build_join_packet(room_id, password, session)
        session["writer"].write(pkt)
        await session["writer"].drain()

        try:
            await asyncio.wait_for(session["join_event"].wait(),
                                   timeout=JOIN_REPLY_TIMEOUT)
        except asyncio.TimeoutError:
            return {"uid": session["uid"], "ok": False, "message": "No reply from server"}

        result = dict(session["join_result"])
        if not result.get("ok"):
            return {"uid": session["uid"], "ok": False,
                    "message": result.get("message", "Rejected")}

        await asyncio.sleep(JOIN_CHAT_DELAY)
        chat_pkt = await build_room_chat_join_packet(room_id, session)
        if chat_pkt and session.get("chat_writer"):
            session["chat_writer"].write(chat_pkt)
            await session["chat_writer"].drain()
            session["chat_room"] = str(room_id)

        session["in_room"] = str(room_id)
        session["room_password"] = password
        return {"uid": session["uid"], "ok": True,
                "message": result.get("message", f"Joined {room_id}")}

    except Exception as e:
        return {"uid": session["uid"], "ok": False, "message": str(e)}
    finally:
        session["join_event"] = None


async def join_all(room_id, password, bot_count=None):
    JOIN_IN_PROGRESS["busy"] = True
    JOIN_IN_PROGRESS["room"] = str(room_id)
    try:
        async with SESSIONS_LOCK:
            available = [s for s in SESSIONS.values() if s.get("writer")]

            if bot_count is not None:
                bot_count = max(1, min(int(bot_count), len(available)))
                sessions = available[:bot_count]
            else:
                sessions = available

            print(f"[JOIN] {len(sessions)}/{len(available)} bots -> room {room_id} "
                  f"(password: {password or 'none'})")

            results = await asyncio.gather(
                *[join_one(s, room_id, password) for s in sessions],
                return_exceptions=True
            )

            details, joined, failed = [], 0, 0
            for s, r in zip(sessions, results):
                if isinstance(r, dict):
                    details.append(r)
                    if r.get("ok"):
                        joined += 1
                    else:
                        failed += 1
                else:
                    failed += 1
                    details.append({"uid": s["uid"], "ok": False, "message": str(r)})

            reasons = {}
            for d in details:
                if not d.get("ok"):
                    reasons[d["message"]] = reasons.get(d["message"], 0) + 1
            print(f"[JOIN] Done -> joined {joined}, failed {failed}"
                  + (f" | {reasons}" if reasons else ""))
            return {"joined": joined, "failed": failed,
                    "requested": len(sessions), "available": len(available),
                    "details": details}
    finally:
        JOIN_IN_PROGRESS["busy"] = False
        JOIN_IN_PROGRESS["room"] = None


async def leave_one(session, room_id=None):
    target = str(room_id or session.get("in_room") or "")

    if not session.get("writer"):
        return {"uid": session["uid"], "ok": False, "message": "Not connected"}
    if not target:
        return {"uid": session["uid"], "ok": False, "message": "Not in a room"}

    try:
        pkt = await build_leave_packet(target, session)
        session["writer"].write(pkt)
        await session["writer"].drain()

        session["in_room"] = None
        session["last_room"] = None
        session["chat_room"] = None

        return {"uid": session["uid"], "ok": True, "message": f"Left {target}"}

    except Exception as e:
        return {"uid": session["uid"], "ok": False, "message": str(e)}


async def leave_all(room_id=None):
    async with SESSIONS_LOCK:
        sessions = [s for s in SESSIONS.values() if s.get("writer")]
        print(f"[LEAVE] {len(sessions)} bots -> room {room_id or 'current'}")

        results = await asyncio.gather(
            *[leave_one(s, room_id) for s in sessions],
            return_exceptions=True
        )

        details, left, skipped = [], 0, 0
        for s, r in zip(sessions, results):
            if isinstance(r, dict):
                details.append(r)
                if r.get("ok"):
                    left += 1
                else:
                    skipped += 1
            else:
                skipped += 1
                details.append({"uid": s["uid"], "ok": False, "message": str(r)})

        print(f"[LEAVE] Done -> left {left}, skipped {skipped}")
        return {"left": left, "skipped": skipped,
                "requested": len(sessions), "details": details}


# ==================== API ====================

@app.route('/join', methods=['GET'])
@app.route('/joinroom', methods=['GET'])
def join_api():
    try:
        room_id = request.args.get('room', '') or request.args.get('room_id', '')
        password = request.args.get('password', '')
        bot_arg = request.args.get('bot', '')
        room_id = "".join(c for c in str(room_id) if c.isdigit())

        if not room_id:
            return jsonify({
                "STATUS": "ERROR",
                "MESSAGE": "Usage: /join?room=ROOM_ID&password=PASSWORD",
                "EXAMPLE": "/join?room=123456&password=0000"
            })

        bot_count = None
        if bot_arg:
            digits = "".join(c for c in str(bot_arg) if c.isdigit())
            if digits:
                bot_count = int(digits)

        if JOIN_IN_PROGRESS.get("busy"):
            return jsonify({
                "STATUS": "ERROR",
                "MESSAGE": "A join is already running",
                "ROOM": JOIN_IN_PROGRESS.get("room")
            })

        online = [s for s in SESSIONS.values() if s.get("writer")]
        if not online:
            return jsonify({"status": "error", "message": "No bot is connected yet."})

        started = time.time()
        fut = asyncio.run_coroutine_threadsafe(join_all(room_id, password, bot_count), loop)
        result = fut.result(timeout=120)
        took = round(time.time() - started, 2)

        total = min(MAX_ACCOUNTS, len(ACCOUNTS))
        online = result["available"]
        joined = result["joined"]

        really_in = sum(
            1 for s in SESSIONS.values()
            if str(s.get("in_room") or "") == str(room_id)
        )

        reasons = {}
        for d in result["details"]:
            if not d.get("ok"):
                reasons[d["message"]] = reasons.get(d["message"], 0) + 1

        body = {
            "STATUS": "ROOM JOINED SUCCESSFULLY" if joined else "ROOM JOIN FAILED",
            "ROOM": room_id,
            "TOTAL BOTS ONLINE": f"{online}/{total}",
            "JOIN SUCCESSFULLY": f"{joined}/{result['requested']}",
            "CONFIRMED IN ROOM": f"{really_in}/{result['requested']}",
            "TIME": f"{took}s",
            "DEVELOPER": "NIROB BBZ"
        }

        if reasons:
            body["FAILED"] = reasons

        return jsonify(body)

    except Exception as e:
        return jsonify({"STATUS": "ERROR", "MESSAGE": str(e)})


@app.route('/leave', methods=['GET'])
def leave_api():
    try:
        room_id = request.args.get('room', '') or request.args.get('room_id', '')
        room_id = "".join(c for c in str(room_id) if c.isdigit())

        online = [s for s in SESSIONS.values() if s.get("writer")]
        if not online:
            return jsonify({"STATUS": "ERROR", "MESSAGE": "No bot is connected yet"})

        started = time.time()
        fut = asyncio.run_coroutine_threadsafe(leave_all(room_id or None), loop)
        result = fut.result(timeout=120)
        took = round(time.time() - started, 2)

        total = min(MAX_ACCOUNTS, len(ACCOUNTS))

        still_in = sum(1 for s in SESSIONS.values() if s.get("in_room"))

        reasons = {}
        for d in result["details"]:
            if not d.get("ok"):
                reasons[d["message"]] = reasons.get(d["message"], 0) + 1

        body = {
            "STATUS": "ROOM LEFT SUCCESSFULLY" if result["left"] else "NO BOT WAS IN A ROOM",
            "ROOM": room_id or "current",
            "TOTAL BOTS ONLINE": f"{len(online)}/{total}",
            "LEFT SUCCESSFULLY": f"{result['left']}/{result['requested']}",
            "STILL IN A ROOM": still_in,
            "TIME": f"{took}s",
            "DEVELOPER": "NIROB BBZ"
        }

        if reasons:
            body["SKIPPED"] = reasons

        return jsonify(body)

    except Exception as e:
        return jsonify({"STATUS": "ERROR", "MESSAGE": str(e)})


@app.route('/status', methods=['GET'])
def status_api():
    uptime = int(time.time() - bot_start_time) if bot_start_time else 0
    total = min(MAX_ACCOUNTS, len(ACCOUNTS))

    online = sum(1 for s in SESSIONS.values() if s.get("writer"))
    chat = sum(1 for s in SESSIONS.values() if s.get("chat_writer"))
    in_room = sum(1 for s in SESSIONS.values() if s.get("in_room"))

    room_counts = {}
    for s in SESSIONS.values():
        if s.get("in_room"):
            r = str(s["in_room"])
            room_counts[r] = room_counts.get(r, 0) + 1

    return jsonify({
        "STATUS": "RUNNING",
        "DEVELOPER": "NIROB BBZ",
        "TOTAL BOTS ONLINE": f"{online}/{total}",
        "CHAT CONNECTED": f"{chat}/{total}",
        "IN ROOM": f"{in_room}/{total}",
        "ROOMS": room_counts,
        "REGION": region,
        "UPTIME": f"{uptime // 3600}h {(uptime % 3600) // 60}m {uptime % 60}s",
        "ENDPOINTS": {
            "/join?room=ID&password=PASS": "All bots join the room",
            "/leave?room=ID": "All bots leave the room",
            "/status": "This page",
        }
    })


@app.route('/', methods=['GET'])
def index_api():
    return jsonify({
        "BOT": "NIROB BBZ - MULTI ACCOUNT ROOM BOT",
        "DEVELOPER": "NIROB BBZ",
        "ENDPOINTS": {
            "/join?room=ID&password=PASS": "All bots join the room",
            "/leave?room=ID": "All bots leave the room",
            "/status": "Bot count & room state",
        }
    })


def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)


# ==================== PER-ACCOUNT SOCKETS ====================

async def account_online_loop(session, ip, port, auth_token):
    name = session["name"]
    delay = RECONNECT_BASE_DELAY

    while bot_running:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            session["writer"] = writer
            writer.write(bytes.fromhex(auth_token))
            await writer.drain()
            print(f"[{name}] Online connected")

            ka = await create_keep_alive(session["key"], session["iv"])
            if ka:
                writer.write(ka)
                await writer.drain()

            delay = RECONNECT_BASE_DELAY

            while True:
                data = await reader.read(9999)
                if not data:
                    break

                event = session.get("join_event")
                if event is not None and not event.is_set():
                    data_hex = data.hex()
                    if JOIN_DEBUG:
                        print(f"[{name}][RX] {data_hex[:120]}")

                    parsed = None
                    for offset in (10, 8, 12, 0):
                        try:
                            parsed = json.loads(await DeCode_PackEt(data_hex[offset:]))
                            break
                        except Exception:
                            continue

                    if parsed is not None:
                        if JOIN_DEBUG:
                            print(f"[{name}][DECODED] {json.dumps(parsed)[:300]}")
                        ok, message = interpret_join_reply(parsed)
                        session["join_result"] = {"ok": ok, "message": message}
                        event.set()

        except Exception as e:
            print(f"[{name}] Online error: {e}")

        session["writer"] = None
        if session.get("in_room"):
            session["last_room"] = session["in_room"]
        session["in_room"] = None

        if bot_running:
            await asyncio.sleep(delay)
            delay = min(delay * 2, RECONNECT_MAX_DELAY)


async def account_chat_loop(session, ip, port, auth_token, login_data):
    name = session["name"]
    delay = RECONNECT_BASE_DELAY

    while bot_running:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            session["chat_writer"] = writer
            writer.write(bytes.fromhex(auth_token))
            await writer.drain()
            print(f"[{name}] Chat connected")

            if getattr(login_data, "Clan_ID", None):
                try:
                    pK = await AuthClan(login_data.Clan_ID,
                                        login_data.Clan_Compiled_Data,
                                        session["key"], session["iv"])
                    if pK:
                        writer.write(pK)
                        await writer.drain()
                except Exception:
                    pass

            delay = RECONNECT_BASE_DELAY

            room = session.get("in_room") or session.get("last_room")
            if room:
                try:
                    await asyncio.sleep(0.5)
                    pkt = await build_room_chat_join_packet(room, session)
                    if pkt:
                        writer.write(pkt)
                        await writer.drain()
                        session["chat_room"] = str(room)
                except Exception:
                    pass

            while True:
                data = await reader.read(9999)
                if not data:
                    break

        except Exception as e:
            print(f"[{name}] Chat error: {e}")

        session["chat_writer"] = None
        session["chat_room"] = None

        if bot_running:
            await asyncio.sleep(delay)
            delay = min(delay * 2, RECONNECT_MAX_DELAY)


async def keep_alive_loop(session):
    while bot_running:
        await asyncio.sleep(KEEPALIVE_INTERVAL)
        w = session.get("writer")
        if not w:
            continue
        try:
            pkt = await create_keep_alive(session["key"], session["iv"])
            if pkt:
                w.write(pkt)
                await w.drain()
        except Exception:
            pass


async def login_account(account):
    name = account.get("name") or f"ACC_{account['uid']}"

    try:
        open_id, access_token = await GeNeRaTeAccEss(account["uid"], account["password"])
        if not open_id or not access_token:
            print(f"[{name}] Invalid account")
            return None

        payload = await EncRypTMajoRLoGin(open_id, access_token)
        major = await MajorLogin(payload)
        if not major:
            print(f"[{name}] Banned / not registered")
            return None

        auth = await DecRypTMajoRLoGin(major)
        if not auth or not auth.token:
            print(f"[{name}] No token")
            return None

        login_data = await GetLoginData(auth.url, payload, auth.token)
        if not login_data:
            print(f"[{name}] Could not get ports")
            return None

        decoded = await DecRypTLoGinDaTa(login_data)
        online_ip, online_port = decoded.Online_IP_Port.split(":")
        chat_ip, chat_port = decoded.AccountIP_Port.split(":")

        auth_token = await xAuThSTarTuP(int(auth.account_uid), auth.token,
                                        int(auth.timestamp), auth.key, auth.iv)

        session = {
            "name": name,
            "uid": str(auth.account_uid),
            "password": account["password"],
            "key": auth.key,
            "iv": auth.iv,
            "region": getattr(auth, 'region', 'IND'),
            "writer": None,
            "chat_writer": None,
            "in_room": None,
            "last_room": None,
            "chat_room": None,
            "room_password": "",
            "join_event": None,
            "join_result": {},
            "tasks": [],
        }

        session["tasks"] = [
            asyncio.create_task(account_online_loop(session, online_ip, online_port, auth_token)),
            asyncio.create_task(account_chat_loop(session, chat_ip, chat_port, auth_token, decoded)),
            asyncio.create_task(keep_alive_loop(session)),
        ]

        return session

    except Exception as e:
        print(f"[{name}] Login error: {e}")
        return None


# ==================== AUTH CHAIN ====================

async def GeNeRaTeAccEss(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": await Ua(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status != 200:
                return None, None
            data = await response.json()
            open_id = data.get("open_id")
            access_token = data.get("access_token")
            return (open_id, access_token) if open_id and access_token else (None, None)

async def EncRypTMajoRLoGin(open_id, access_token):
    from JEXAR import MajoRLoGinrEq_pb2
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = "2026-06-26 17:55:50"
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.126.5"
    major_login.system_software = "Android OS 9 / API-28 (SKQ1.220617.001/S.c2cce3-2_95f)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 960
    major_login.screen_height = 540
    major_login.screen_dpi = "240"
    major_login.processor_details = "ARMv7 VFPv3 NEON | 2000 | 2"
    major_login.memory = 1993
    major_login.gpu_renderer = "Adreno (TM) 540"
    major_login.gpu_version = "OpenGL ES 3.2 (4.5.0 - Build 27.20.100.8280)"
    major_login.unique_device_id = "Google|97a4cfa9-6e02-44f3-88b6-3412bb015e78"
    major_login.client_ip = "103.145.77.67"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 128886
    major_login.external_storage_available = 117200
    major_login.internal_storage_total = 7998
    major_login.internal_storage_available = 5785
    major_login.game_disk_storage_available = 123770
    major_login.game_disk_storage_total = 128886
    major_login.external_sdcard_avail_storage = 123770
    major_login.external_sdcard_total_storage = 128886
    major_login.login_by = 1
    major_login.library_path = "/data/app/com.dts.freefireth-OWQl3ttcU3rQzpLdiDS1Kw==/lib/arm"
    major_login.reg_avatar = 1
    major_login.library_token = "4c322aeb56444feaa151d1ea91a8f7f2|/data/app/com.dts.freefireth-OWQl3ttcU3rQzpLdiDS1Kw==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 1
    major_login.cpu_architecture = "32"
    major_login.client_version_code = "2019120776"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 4095
    major_login.login_open_id_type = 4
    major_login.loading_time = 13094
    major_login.release_channel = "android"
    major_login.android_engine_init_flag = 111207
    major_login.if_push = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    string = major_login.SerializeToString()
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(string, AES.block_size)
    encrypted_payload = cipher.encrypt(padded_message)
    return encrypted_payload

async def MajorLogin(payload):
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB54"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
            return None

async def DecRypTMajoRLoGin(MajoRLoGinResPonsE):
    from JEXAR import MajoRLoGinrEs_pb2
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(MajoRLoGinResPonsE)
    return proto

async def DecRypTLoGinDaTa(LoGinDaTa):
    from JEXAR import PorTs_pb2
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(LoGinDaTa)
    return proto

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB54",
        "Authorization": f"Bearer {token}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
            return None

async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9:
        headers = '0000000'
    elif uid_length == 8:
        headers = '00000000'
    elif uid_length == 10:
        headers = '000000'
    elif uid_length == 7:
        headers = '000000000'
    else:
        headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"

# =================== TCP CONNECTIONS ===================

# ==================== HELPERS ====================

async def AuthClan(clan_id, clan_data, key, iv):
    try:
        fields = {1: 4, 2: {1: int(clan_id), 2: clan_data}}
        packet = await CrEaTe_ProTo(fields)
        return await GeneRaTePk(packet.hex(), '1215', key, iv)
    except Exception:
        return None


async def create_keep_alive(key, iv):
    try:
        fields = {1: 1, 2: {1: int(time.time()), 2: 1}}
        packet = await CrEaTe_ProTo(fields)
        return await GeneRaTePk(packet.hex(), '0514', key, iv)
    except Exception:
        return None


# ==================== MAIN ====================

async def MaiiiinE():
    global bot_start_time, loop, SESSIONS_LOCK, SESSIONS, region, bot_running

    patch_protocol_module()

    SESSIONS_LOCK = asyncio.Lock()
    SESSIONS = {}
    bot_running = True
    bot_start_time = time.time()

    pool = ACCOUNTS[:MAX_ACCOUNTS]

    print("\n" + "=" * 60)
    print("NIROB BBZ - MULTI ACCOUNT ROOM BOT")
    print("=" * 60)
    print(f"Logging in {len(pool)} accounts...")
    print("=" * 60 + "\n")

    Thread(target=run_flask, daemon=True).start()
    print("API Server started on port 5000 (Developer: NIROB BBZ)\n")

    for i in range(0, len(pool), LOGIN_BATCH_SIZE):
        batch = pool[i:i + LOGIN_BATCH_SIZE]
        results = await asyncio.gather(
            *[login_account(acc) for acc in batch],
            return_exceptions=True
        )
        for r in results:
            if isinstance(r, dict):
                SESSIONS[r["uid"]] = r

        done = min(i + LOGIN_BATCH_SIZE, len(pool))
        print(f"[LOGIN] {len(SESSIONS)} online after {done}/{len(pool)} attempted")

        if done < len(pool):
            await asyncio.sleep(LOGIN_BATCH_GAP)

    if SESSIONS:
        region = next(iter(SESSIONS.values())).get("region", "IND")

    print("\n" + "=" * 60)
    print(f"ACCOUNTS LOGGED IN: {len(SESSIONS)}/{len(pool)}")
    print("DEVELOPER: NIROB BBZ")
    print("=" * 60)
    print("API: http://0.0.0.0:5000")
    print("  /join?room=123456&password=0000   -> all bots join")
    print("  /join?bot=20&room=123456&password=0000")
    print("  /leave?room=123456                -> all bots leave")
    print("  /leave                            -> leave current room")
    print("  /status                           -> bot list & state")
    print("=" * 60 + "\n")

    if not SESSIONS:
        print("No account could log in. Check the credentials.")
        return

    try:
        while bot_running:
            await asyncio.sleep(30)
    except asyncio.CancelledError:
        print("Bot tasks cancelled")


async def shutdown_sessions():
    global bot_running
    bot_running = False

    for s in list(SESSIONS.values()):
        for t in s.get("tasks", []):
            if not t.done():
                t.cancel()
        for w in (s.get("writer"), s.get("chat_writer")):
            try:
                if w:
                    w.close()
            except Exception:
                pass

    SESSIONS.clear()
    await asyncio.sleep(0.5)


async def StarTinG():
    global loop
    loop = asyncio.get_event_loop()

    while True:
        try:
            await asyncio.wait_for(MaiiiinE(), timeout=7 * 60 * 60)
        except KeyboardInterrupt:
            break
        except asyncio.TimeoutError:
            print("\n[AUTO-RESTART] 7 hours completed, re-logging every account...\n")
            await shutdown_sessions()
        except Exception as e:
            print(f"Error: {e}")
            await shutdown_sessions()
            await asyncio.sleep(5)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(StarTinG())
    except KeyboardInterrupt:
        print("\nBot Stopped")
