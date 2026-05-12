import urllib.request
import json
import os
import hmac
import hashlib
import base64
import sys
from datetime import datetime

UID = os.environ.get("BILI_UID", "3706967623207490")
SESSDATA = os.environ.get("BILI_SESSDATA", "")
BILI_JCT = os.environ.get("BILI_JCT", "")
DEDE_USERID = os.environ.get("BILI_DEDE_USERID", "")
DINGTALK_TOKEN = os.environ.get("DINGTALK_TOKEN", "")
DINGTALK_SECRET = os.environ.get("DINGTALK_SECRET", "")

STATE_FILE = "state.json"

def send_dingtalk(title, text):
    timestamp = str(round(time.time() * 1000))
    secret_enc = DINGTALK_SECRET.encode("utf-8")
    string_to_sign = f"{timestamp}\n{DINGTALK_SECRET}".encode("utf-8")
    hmac_code = hmac.new(secret_enc, string_to_sign, digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode("utf-8")
    url = f"https://oapi.dingtalk.com/robot/send?access_token={DINGTALK_TOKEN}&timestamp={timestamp}&sign={sign}"
    payload = {"msgtype": "markdown", "markdown": {"title": title, "text": text}}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read()).get("errcode") == 0

def bili_headers():
    cookie = f"SESSDATA={SESSDATA}; bili_jct={BILI_JCT}; DedeUserID={DEDE_USERID}"
    return {"User-Agent": "Mozilla/5.0", "Referer": f"https://space.bilibili.com/{UID}", "Cookie": cookie}

def fetch_dynamics():
    url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={UID}&offset_dynamic_id=0"
    req = urllib.request.Request(url, headers=bili_headers())
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    if data.get("code") != 0:
        raise Exception(f"API error: {data.get('message')}")
    return data.get("data", {}).get("cards", [])

def fetch_comments(oid, ctype=11, ps=5):
    url = f"https://api.bilibili.com/x/v2/reply/main?oid={oid}&type={ctype}&mode=3&ps={ps}"
    req = urllib.request.Request(url, headers=bili_headers())
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    if data.get("code") != 0:
        return [], 0
    replies = data.get("data", {}).get("replies", [])
    total = data.get("data", {}).get("cursor", {}).get("all_count", 0)
    return replies, total

def get_post_info(card):
    ctype = card.get("desc", {}).get("type", 0)
    card_data = json.loads(card.get("card", "{}"))
    rid = card.get("desc", {}).get("rid_str", "")
    ts = card.get("desc", {}).get("timestamp", 0)
    time_str = datetime.fromtimestamp(ts).strftime("%m-%d %H:%M") if ts else "?"
    if ctype == 2:
        item = card_data.get("item") or {}
        text = item.get("description", "") or "(图片)"
        pics = item.get("pictures") or []
        text += f" [{len(pics)}张]"
    elif ctype == 8:
        text = f"[视频] {card_data.get('title','?')}"
    elif ctype == 4:
        item = card_data.get("item") or {}
        text = item.get("content", "")
    elif ctype == 1:
        text = card_data.get("content", "(转发)")
    elif ctype == 64:
        text = f"[专栏] {card_data.get('title','?')}"
    else:
        text = f"[动态{ctype}]"
    return text, rid, 11, time_str

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"last_id": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def main():
    state = load_state()
    cards = fetch_dynamics()
    if not cards:
        return
    latest_id = cards[0].get("desc", {}).get("dynamic_id", 0)
    last_id = state.get("last_id")
    if last_id is None:
        state["last_id"] = latest_id
        save_state(state)
        print(f"init: {latest_id}")
        return
    if latest_id == last_id:
        print("no new")
        return
    new_cards = []
    for card in cards:
        did = card.get("desc", {}).get("dynamic_id", 0)
        if did and did != last_id:
            new_cards.append(card)
        else:
            break
    new_cards.reverse()
    for card in new_cards:
        text, oid, ctype, time_str = get_post_info(card)
        replies, total_comments = fetch_comments(oid, ctype)
        msg = f"### [观势浮生] 新动态\n时间: {time_str}\n\n{text[:500]}\n\n"
        if total_comments > 0:
            msg += f"评论 ({total_comments}条):\n"
            for i, r in enumerate(replies[:5]):
                uname = r.get("member", {}).get("uname", "?")
                message = r.get("content", {}).get("message", "")
                likes = r.get("like", 0)
                msg += f"> {i+1}. {uname}: {message[:100]} like:{likes}\n"
            if total_comments > 5:
                msg += f"> ...等{total_comments}条\n"
        send_dingtalk("观势浮生新动态", msg)
        print(f"sent: {text[:60]}")
    state["last_id"] = latest_id
    save_state(state)
    print(f"done: {latest_id}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"err: {e}")
    sys.exit(0)
