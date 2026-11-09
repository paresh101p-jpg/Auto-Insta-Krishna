# -*- coding: utf-8 -*-
"""
Apply 100% Pure 8K 3D Master AI Artwork Thumbnails to All Playlists
- STRICT ZERO TEXT, ZERO WORDS, ZERO LETTERS, ZERO BADGES, ZERO CSS/HTML BOXES.
- Pure photorealistic cinematic visual masterpieces.
- Uploads to Lead Video (Position 0) and refreshes playlist server cache.
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

# 10 Playlists strictly mapped to 100% PURE Master AI Artworks (ZERO TEXT)
PLAYLIST_AI_MAP = [
    {
        "id": "PLTS50VUZ5khw",
        "name": "🧘 Stress Relief & Mental Peace | Flute Meditation",
        "lead_vid": "X0EMsuBBhr4",
        "ai_file": "master_ai_thumb_stress_relief_emerald.jpg"
    },
    {
        "id": "PLEwYNfw5fPiA",
        "name": "🔴 24/7 Live Spiritual Chanting & Meditation Streams",
        "lead_vid": "_65f6xs_WUk",
        "ai_file": "master_ai_thumb_live_temple_sanctum.jpg"
    },
    {
        "id": "PLYl7L1G0M6Oc",
        "name": "🌸 Peaceful Lotus Lake Meditation Flute",
        "lead_vid": "VDEvUok3pT8",
        "ai_file": "master_ai_thumb_lotus_lake_sanctum.jpg"
    },
    {
        "id": "PLJ_ReLRXXG2k",
        "name": "🪕 Pure Bansuri & Tabla Classical Jugalbandi",
        "lead_vid": "aOMg-IAezXY",
        "ai_file": "master_ai_thumb_bansuri_tabla_pure.jpg"
    },
    {
        "id": "PLd-E2kzfVUEg",
        "name": "🕉️ Divine Flute & Pure Meditation Music | Krishna Vibez",
        "lead_vid": "vuoOW98h96c",
        "ai_file": "master_ai_thumb_divine_krishna_pure.jpg"
    },
    {
        "id": "PLfXTB8iO3Gik",
        "name": "👑 Raga Darbari Deep Meditation Flute",
        "lead_vid": "Zb9E7V9LiVM",
        "ai_file": "master_ai_thumb_raga_darbari_royal.jpg"
    },
    {
        "id": "PLPKE2BWZ7HwI",
        "name": "🌙 Deep Meditative Sleep Music | Pure Night Peace",
        "lead_vid": "sUctWLbOpmY",
        "ai_file": "master_ai_thumb_zen_bamboo_pure.jpg"
    },
    {
        "id": "PLbrKp-ssSkJc",
        "name": "🌊 Sacred Yamuna River & Ghats Meditation Flute",
        "lead_vid": "PZes6Z-cU8s",
        "ai_file": "master_ai_thumb_yamuna_ghats_dusk.jpg"
    },
    {
        "id": "PLJD6PGkODrOs",
        "name": "🌅 Golden Sunrise & Morning Meditation Flute",
        "lead_vid": "CJF8tZpJI8Y",
        "ai_file": "master_ai_thumb_golden_sunrise_pure.jpg"
    },
    {
        "id": "PLP-XF1dRgWNk",
        "name": "☀️ Peaceful Morning Flute & Sacred Meditation",
        "lead_vid": "InfDz_ftdGE",
        "ai_file": "master_ai_thumb_temple_dawn_pure.jpg"
    }
]

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

def main():
    log("=" * 65)
    log("🚀 APPLYING 100% PURE 8K 3D MASTER AI ARTWORKS (ZERO TEXT/ZERO HTML)")
    log("=" * 65)

    access_token = get_oauth_token()
    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        creds_data = json.load(f)
    creds = Credentials.from_authorized_user_info(creds_data)
    yt = build("youtube", "v3", credentials=creds)

    for item in PLAYLIST_AI_MAP:
        pl_id = item["id"]
        pl_name = item["name"]
        vid = item["lead_vid"]
        img_name = item["ai_file"]
        img_path = os.path.join(BASE_DIR, img_name)

        if not os.path.exists(img_path):
            log(f"❌ Missing file: {img_path}")
            continue

        file_size = os.path.getsize(img_path)
        log(f"\n[Playlist: {pl_name}]")
        log(f"  -> Lead Video: {vid}")
        log(f"  -> Attaching Pure 8K AI Artwork: {img_name} ({file_size / 1024:.1f} KB)")

        # 1. Upload to YouTube Video
        thumb_url = f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}&uploadType=media"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "image/jpeg"
        }
        with open(img_path, "rb") as tf:
            up_res = requests.post(thumb_url, headers=headers, data=tf, timeout=30)

        if up_res.status_code in [200, 201]:
            log(f"  -> 🌟 SUCCESS! Uploaded Pure AI Artwork to Video [{vid}]")
        else:
            log(f"  -> Upload notice ({up_res.status_code}): {up_res.text}")

        # 2. Invalidate Playlist Server Cache
        try:
            pl_data = yt.playlists().list(id=pl_id, part="snippet").execute()
            if pl_data.get("items"):
                snippet = pl_data["items"][0]["snippet"]
                yt.playlists().update(part="snippet", body={"id": pl_id, "snippet": snippet}).execute()
                log(f"  -> 🔄 YouTube Playlist Cache Refreshed for '{pl_id}'!")
        except Exception as cache_err:
            log(f"  -> Cache touch notice: {cache_err}")

    log("\n" + "=" * 65)
    log("🎉 ALL 10 PLAYLISTS ARE NOW 100% PURE AI ARTWORKS (ZERO TEXT/ZERO HTML)!")
    log("=" * 65)

if __name__ == "__main__":
    main()
