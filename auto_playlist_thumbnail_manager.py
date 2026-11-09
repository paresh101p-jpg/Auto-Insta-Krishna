# -*- coding: utf-8 -*-
"""
Auto Playlist Thumbnail Manager & 100% Pure 3D AI Artwork Engine
- ZERO HTML, ZERO TEXT OVERLAYS, ZERO BADGES, ZERO CSS BOXES.
- Strictly uses 100% Genuine 8K Photorealistic 3D Master AI Artworks.
- Dynamically pairs category/theme keywords with dedicated Master AI Artworks.
- Sets Lead Video (Position 0) and refreshes playlist server cache immediately.
"""

import os
import sys
import json
import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

sys.stdout.reconfigure(encoding="utf-8")

def log(msg):
    print(msg, flush=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "youtube_token.json")

# Category mapping to 100% Pure 8K 3D Master AI Artworks (ZERO HTML)
CATEGORY_AI_MAP = [
    {
        "keywords": ["lotus", "lake", "sarovar", "kamal"],
        "ai_file": "master_ai_thumb_lotus_lake_sanctum.jpg",
        "theme": "Sacred Vrindavan Lotus Pond at Dawn"
    },
    {
        "keywords": ["sleep", "night", "neend", "insomnia", "soye"],
        "ai_file": "master_ai_thumb_zen_bamboo_sleep.jpg",
        "theme": "Moonlit Zen Bamboo Forest & Night Lake"
    },
    {
        "keywords": ["morning", "gokul", "pooja", "subah"],
        "ai_file": "master_ai_thumb_morning_peace.jpg",
        "theme": "Sacred Morning Awakening & Peaceful Dhyan"
    },
    {
        "keywords": ["sunrise", "dawn", "prabhat", "golden"],
        "ai_file": "master_ai_thumb_morning_awakening_v2.jpg",
        "theme": "Majestic Golden Sunrise Awakening Over Ghats"
    },
    {
        "keywords": ["yamuna", "river", "ghat", "nadi"],
        "ai_file": "master_ai_thumb_yamuna_ghats_dusk.jpg",
        "theme": "Twilight Sacred Yamuna River with Floating Diyas"
    },
    {
        "keywords": ["darbari", "raga", "raag", "royal"],
        "ai_file": "master_ai_thumb_raga_darbari_royal.jpg",
        "theme": "Royal Stepwell Baori Courtyard Under Crescent Moon"
    },
    {
        "keywords": ["jugalbandi", "tabla", "taal", "classical"],
        "ai_file": "master_ai_thumb_bansuri_tabla_awakening.jpg",
        "theme": "Authentic Classical Bansuri & Live Tabla with Petals"
    },
    {
        "keywords": ["live", "chanting", "stream", "radio", "akhand"],
        "ai_file": "master_ai_thumb_live_temple_sanctum.jpg",
        "theme": "Ancient Vedic Temple Sanctum with Hanging Bells & Diyas"
    },
    {
        "keywords": ["stress", "relief", "mental", "chinta", "tanav"],
        "ai_file": "master_ai_thumb_stress_relief_emerald.jpg",
        "theme": "Tranquil Emerald Mountain Lake in Morning God Rays"
    },
    {
        "keywords": ["krishna", "divine", "meditation", "dhyan", "peace"],
        "ai_file": "master_ai_thumb_soul_healing.jpg",
        "theme": "Deep Soul Dhyan & Cosmic Golden Energy Aura"
    }
]

def pick_ai_thumb_for_title(playlist_title):
    clean = playlist_title.lower()
    for cat in CATEGORY_AI_MAP:
        for kw in cat["keywords"]:
            if kw in clean:
                file_path = os.path.join(BASE_DIR, cat["ai_file"])
                if os.path.exists(file_path):
                    return file_path, cat["theme"]
    # Fallback default
    fallback = os.path.join(BASE_DIR, "master_ai_thumb_soul_healing.jpg")
    return fallback, "Deep Soul Dhyan & Divine Flute"

def get_oauth_token():
    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        t = json.load(f)
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": t["client_id"],
        "client_secret": t["client_secret"],
        "refresh_token": t["refresh_token"],
        "grant_type": "refresh_token"
    }, timeout=15)
    return resp.json()["access_token"]

def upload_thumbnail_to_video(vid, thumb_path, access_token):
    thumb_url = f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}&uploadType=media"
    upload_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "image/jpeg"
    }
    with open(thumb_path, "rb") as tf:
        up_res = requests.post(thumb_url, headers=upload_headers, data=tf, timeout=30)
    return up_res.status_code in [200, 201], up_res.status_code, up_res.text

def generate_and_apply_cover(pl_id, title, lead_vid, access_token):
    ai_thumb, theme_name = pick_ai_thumb_for_title(title)
    file_size = os.path.getsize(ai_thumb)
    log(f"  -> Selected Pure 8K AI Artwork: {os.path.basename(ai_thumb)} ({file_size / 1024:.1f} KB)")
    log(f"  -> Visual Hook Theme: '{theme_name}' (ZERO HTML)")
    log(f"  -> 🚀 Uploading Pure AI Artwork to Lead Video [{lead_vid}]...")
    
    ok, code, txt = upload_thumbnail_to_video(lead_vid, ai_thumb, access_token)
    if ok:
        log(f"  -> 🌟 SUCCESS! Lead Video [{lead_vid}] set to Pure AI Artwork!")
        # Touch cache
        try:
            with open(TOKEN_PATH, "r", encoding="utf-8") as f:
                creds_data = json.load(f)
            creds = Credentials.from_authorized_user_info(creds_data)
            yt = build("youtube", "v3", credentials=creds)
            pl_data = yt.playlists().list(id=pl_id, part="snippet").execute()
            if pl_data.get("items"):
                snippet = pl_data["items"][0]["snippet"]
                yt.playlists().update(part="snippet", body={"id": pl_id, "snippet": snippet}).execute()
                log(f"  -> 🔄 YouTube Server Cache Refreshed for Playlist '{pl_id}'!")
        except Exception as cache_err:
            log(f"  -> Cache touch notice: {cache_err}")
    else:
        log(f"  -> Upload notice ({code}): {txt}")
    return ai_thumb
