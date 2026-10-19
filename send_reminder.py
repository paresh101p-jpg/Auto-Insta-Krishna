# -*- coding: utf-8 -*-
"""
Krishna Vibez - Daily Reminder to Personal Telegram
Dispatches the latest 4K artwork/reel and 1-tap copy caption to Paresh bhai's personal Telegram
with direct 1-click links to WhatsApp Channel and YouTube Community.
"""

import os
import sys
import json
import re
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DATA_PATH = os.path.join(BASE_DIR, "website", "public", "js", "posts-data.js")
TELEGRAM_TOKEN_FILE = os.path.join(BASE_DIR, "telegram_token.txt")

def get_creds():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    admin_chat_id = os.environ.get("TELEGRAM_ADMIN_CHAT_ID")
    if not bot_token or not admin_chat_id:
        if os.path.exists(TELEGRAM_TOKEN_FILE):
            try:
                with open(TELEGRAM_TOKEN_FILE, "r", encoding="utf-8") as tf:
                    for line in tf:
                        if line.startswith("TELEGRAM_BOT_TOKEN="):
                            bot_token = line.split("=", 1)[1].strip()
                        elif line.startswith("TELEGRAM_ADMIN_CHAT_ID="):
                            admin_chat_id = line.split("=", 1)[1].strip()
            except Exception:
                pass
    admin_chat_id = admin_chat_id or "753762808"
    return bot_token, admin_chat_id

def get_latest_post():
    if not os.path.exists(POSTS_DATA_PATH):
        print(f"Error: {POSTS_DATA_PATH} not found.")
        return None
    try:
        with open(POSTS_DATA_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r'window\.KRISHNA_POSTS\s*=\s*(\[.*?\]);', content, re.DOTALL)
        if match:
            posts = json.loads(match.group(1))
            if posts and len(posts) > 0:
                return posts[0]
    except Exception as e:
        print(f"Error loading posts: {e}")
    return None

def send_reminder():
    bot_token, admin_chat_id = get_creds()
    if not bot_token or not admin_chat_id:
        print("Error: Telegram bot token or admin chat ID missing.")
        return False

    post = get_latest_post()
    if not post:
        print("No post found.")
        return False

    is_video = post.get("mediaType") == "video"
    media_url = post.get("videoUrl") if is_video else post.get("imageUrl")
    quote_text = post.get("quote", "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।")
    post_id = post.get("id", "today")
    post_url = f"https://krishnavibez.in/post.html?id={post_id}"
    whatsapp_channel = "https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J"
    youtube_community = "https://youtube.com/@krishnavibezofficial/community"

    caption = (
        f"🔔 <b>परेश भाई, आज का नया पोस्ट तैयार है!</b>\n"
        f"👉 <i>नीचे दी गई रील/फ़ोटो को WhatsApp Channel और YouTube पर पोस्ट कर दीजिए:</i>\n\n"
        f"✨ <b>श्री कृष्ण पावन अमृत विचार</b> ✨\n\n"
        f"<i>\"{quote_text}\"</i>\n\n"
        f"🌸 <b>4K दर्शन व डाउनलोड:</b>\n{post_url}\n\n"
        f"🕊️ <b>Krishna Vibez Official:</b>\n"
        f"🟢 WhatsApp: {whatsapp_channel}\n"
        f"▶️ YouTube: https://youtube.com/@krishnavibezofficial\n\n"
        f"जय श्री राधे कृष्ण! 🙏✨\n\n"
        f"#Krishna #RadheKrishna #BhagavadGita #KrishnaQuotes"
    )

    markup = {
        "inline_keyboard": [
            [
                {"text": "🟢 WhatsApp चैनल खोलें", "url": whatsapp_channel},
                {"text": "▶️ YouTube Community खोलें", "url": youtube_community}
            ],
            [
                {"text": "🌸 4K दर्शन वेबसाइट पर देखें", "url": post_url}
            ]
        ]
    }

    endpoint = "sendVideo" if is_video else "sendPhoto"
    param_name = "video" if is_video else "photo"

    payload = {
        "chat_id": admin_chat_id,
        param_name: media_url,
        "caption": caption[:1024],
        "parse_mode": "HTML",
        "reply_markup": json.dumps(markup)
    }

    api_url = f"https://api.telegram.org/bot{bot_token}/{endpoint}"
    print(f"Sending {'Video' if is_video else 'Photo'} reminder to Paresh bhai ({admin_chat_id})...")
    res = requests.post(api_url, data=payload, timeout=25).json()

    if res.get("ok"):
        print("✅ Media reminder sent successfully!")
        
        # Follow up with 1-tap copy message
        clean_copy_text = (
            f"✨ श्री कृष्ण पावन अमृत विचार ✨\n\n"
            f"\"{quote_text}\"\n\n"
            f"🌸 4K दर्शन व डाउनलोड:\n{post_url}\n\n"
            f"🕊️ Krishna Vibez Official:\n"
            f"🟢 WhatsApp: {whatsapp_channel}\n"
            f"▶️ YouTube: https://youtube.com/@krishnavibezofficial\n\n"
            f"जय श्री राधे कृष्ण! 🙏✨\n\n"
            f"#Krishna #RadheKrishna #BhagavadGita #KrishnaQuotes"
        )
        copy_msg = (
            f"📋 <b>नीचे दिए गए बॉक्स पर सिर्फ 1 बार टैप (Click) करें — पूरा Caption तुरंत Copy हो जाएगा:</b>\n\n"
            f"<code>{clean_copy_text}</code>"
        )
        copy_payload = {
            "chat_id": admin_chat_id,
            "text": copy_msg,
            "parse_mode": "HTML"
        }
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data=copy_payload, timeout=15)
        print("✅ 1-Tap Auto-Copy caption box sent successfully!")
        return True
    else:
        print(f"❌ Error: {res.get('description')}")
        return False

if __name__ == "__main__":
    send_reminder()
