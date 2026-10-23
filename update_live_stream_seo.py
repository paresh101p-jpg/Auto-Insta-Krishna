#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — 24/7 YOUTUBE LIVE STREAM AUTOMATIC WEEKLY SEO UPDATER
=============================================================================
Automatically rotates and updates the Live Stream Title, Long Description,
and Trending Tags every 7 days without stopping or interrupting the stream.
Boosts YouTube algorithmic discovery, search rankings, and click-through-rate.
=============================================================================
"""

import os
import sys
import json
import time
import random
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "youtube_token.json")
LIVE_VIDEO_ID = "4RNGpmv8S1s"

# Rotating High-CTR Weekly Themes
WEEKLY_THEMES = [
    {
        "title": "🔴 24/7 LIVE: Lord Krishna Flute Meditation Music | श्री कृष्ण बांसुरी धुन | Deep Peace, Sleep & Relax",
        "hook": "Experience profound peace and calmness with non-stop divine Bansuri flute music dedicated to Lord Shri Krishna.",
        "focus": "Deep Sleep, Insomnia Relief, Meditation, Relaxation"
    },
    {
        "title": "🔴 LIVE 24/7: Radha Krishna Peaceful Flute Music | दिव्य बांसुरी की धुन | Stress Relief & Morning Dhyan",
        "hook": "Start your day with positive energy and divine vibrations of Radha Krishna flute melodies in Vrindavan.",
        "focus": "Morning Meditation, Stress Relief, Positive Energy, Mind Healing"
    },
    {
        "title": "🔴 24/7 LIVE: Shri Krishna Bansuri Healing Music | मानसिक शांति और ध्यान | Study, Focus & Deep Sleep",
        "hook": "Calm your mind and improve concentration with soulful Indian classical flute meditation by Krishna Vibez.",
        "focus": "Study Focus, Work Concentration, Mental Clarity, Inner Healing"
    },
    {
        "title": "🔴 LIVE 24/7: Divine Vrindavan Flute Meditation | श्री कृष्ण अमृत बांसुरी | Positive Energy & Relaxation",
        "hook": "Immerse in the soothing aura of Vrindavan with authentic Lord Krishna flute ragas and peaceful spiritual ambiance.",
        "focus": "Spiritual Awakening, Soulful Peace, Anxiety Relief, Deep Relaxation"
    }
]

def get_authenticated_service():
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    client_id = client_id or data.get("client_id")
                    client_secret = client_secret or data.get("client_secret")
                    refresh_token = refresh_token or data.get("refresh_token")
            except Exception as e:
                print(f"Notice reading local token file: {e}")

    if not (client_id and client_secret and refresh_token):
        print("Error: YouTube credentials not found.")
        return None

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube"]
    )
    return build("youtube", "v3", credentials=creds)

def update_live_seo():
    print("=================================================================")
    print("KRISHNA VIBEZ — LIVE STREAM WEEKLY AUTO-SEO UPDATE")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=================================================================")

    # Pick theme based on week number of the year
    week_num = datetime.now().isocalendar()[1]
    theme = WEEKLY_THEMES[week_num % len(WEEKLY_THEMES)]

    description = f"""🌸 Welcome to Krishna Vibez 24/7 Official Live Stream 🌸
{theme['hook']}

🪶 Ideal For:
• {theme['focus']}
• Chanting, Prayer & Temple Atmosphere
• Pure relaxation after a long, tiring day

✨ Official Platforms & Connect:
🌐 Official Website: https://krishnavibez.in/
📱 WhatsApp Channel: https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J
✈️ Telegram Channel: https://t.me/krishnavibezz
📷 Instagram: https://www.instagram.com/pareshpadsala_/

🔍 Searches & Topics Covered:
Krishna flute music live, shri krishna bansuri live, radhe krishna live stream, 24/7 krishna flute, peaceful flute meditation, relaxing sleep music, bansuri dhun, vrindavan live music, devotional flute music, daily krishna meditation, stress relief music, study focus flute.

#Krishna #RadheKrishna #LiveStream #FluteMusic #Meditation #BansuriDhun #KrishnaVibez #PeacefulMusic #247Live #Vrindavan"""

    tags = [
        "krishna flute music", "krishna live", "radhe krishna live", "bansuri dhun",
        "24/7 live stream", "meditation flute", "deep sleep music", "peaceful flute",
        "krishna bhajan flute", "relaxing krishna music", "vrindavan live",
        "flute music live", "stress relief music", "krishna vibez", "shri krishna live"
    ]

    youtube = get_authenticated_service()
    if not youtube:
        print("Authentication failed. Skipping update.")
        return False

    try:
        body = {
            "id": LIVE_VIDEO_ID,
            "snippet": {
                "title": theme["title"],
                "description": description,
                "tags": tags,
                "categoryId": "1"  # Film & Animation
            }
        }
        res = youtube.videos().update(part="snippet", body=body).execute()
        print(f"🎉 SUCCESS! Live stream SEO updated successfully!")
        print(f"  -> Title: {theme['title']}")
        print(f"  -> Video ID: {LIVE_VIDEO_ID}")
        return True
    except Exception as e:
        print(f"⚠️ Error updating live SEO: {e}")
        return False

if __name__ == "__main__":
    update_live_seo()
