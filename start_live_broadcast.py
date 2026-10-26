#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Starts a permanent 24/7 Live Broadcast on YouTube linked to the Oracle Cloud Stream.
Sets enableAutoStop = False so the stream never terminates on minor hiccups.
"""

import os
import sys
import json
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "youtube_token.json")

def start_new_broadcast():
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        t = json.load(f)
    creds = Credentials.from_authorized_user_info(t)
    yt = build("youtube", "v3", credentials=creds)

    # 1. Get the active stream
    streams = yt.liveStreams().list(part="snippet,status,cdn", mine=True).execute()
    active_stream = None
    for s in streams.get("items", []):
        if s["cdn"]["ingestionInfo"].get("streamName") == "jvp4-jpdp-2hfk-mpjc-8x0m":
            active_stream = s
            break
    if not active_stream:
        print("❌ Could not find stream jvp4-jpdp-2hfk-mpjc-8x0m")
        return

    stream_id = active_stream["id"]
    print(f"✅ Found Ingestion Stream: {stream_id} (Status: {active_stream['status']['streamStatus']})")

    # 2. Insert new Live Broadcast
    now_iso = datetime.now(timezone.utc).isoformat()
    body = {
        "snippet": {
            "title": "🔴 LIVE 24/7: Divine Vrindavan Flute Meditation | श्री कृष्ण अमृत बांसुरी | Krishna Vibez",
            "description": (
                "🌸 Welcome to Krishna Vibez 24/7 Divine Live Stream! 🌸\n\n"
                "Immerse yourself in non-stop peaceful Indian Classical Bansuri flute melodies dedicated to Lord Krishna.\n"
                "Perfect for deep sleep, stress relief, inner peace, puja, and soulful relaxation.\n\n"
                "✨ Official Channels & Updates:\n"
                "🌐 Website: https://krishnavibez.in/\n"
                "📱 WhatsApp Channel: https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J\n"
                "✈️ Telegram: https://t.me/krishnavibezz\n"
                "📸 Instagram: @krishnavibez\n"
                "🧵 Threads: @krishnavibez\n\n"
                "#Krishna #RadheKrishna #LiveStream #MeditationMusic #FluteMusic #Bansuri #DeepSleep #Peaceful #KrishnaVibez"
            ),
            "scheduledStartTime": now_iso
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        },
        "contentDetails": {
            "enableAutoStart": True,
            "enableAutoStop": False,   # CRITICAL: YouTube will NEVER close the stream on temporary lag
            "enableDvr": True,
            "latencyPreference": "normal"
        }
    }

    print("🚀 Creating new Live Broadcast on YouTube...")
    b_res = yt.liveBroadcasts().insert(part="snippet,status,contentDetails", body=body).execute()
    broadcast_id = b_res["id"]
    print(f"✅ Broadcast created! Video ID: {broadcast_id}")

    # 3. Bind to the active stream
    print(f"🔗 Binding Broadcast {broadcast_id} to Stream {stream_id}...")
    bind_res = yt.liveBroadcasts().bind(
        id=broadcast_id,
        part="id,contentDetails,snippet,status",
        streamId=stream_id
    ).execute()
    print("🎉 SUCCESS! Stream is bound and LIVE!")
    print(f"📺 Watch URL: https://www.youtube.com/watch?v={broadcast_id}")

    # 4. Update LIVE_VIDEO_ID in update_live_stream_seo.py
    seo_file = os.path.join(BASE_DIR, "update_live_stream_seo.py")
    if os.path.exists(seo_file):
        with open(seo_file, "r", encoding="utf-8") as f:
            content = f.read()
        import re
        new_content = re.sub(r'LIVE_VIDEO_ID\s*=\s*"[^"]*"', f'LIVE_VIDEO_ID = "{broadcast_id}"', content)
        with open(seo_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ Updated LIVE_VIDEO_ID in update_live_stream_seo.py to {broadcast_id}")

    return broadcast_id

if __name__ == "__main__":
    start_new_broadcast()
