# -*- coding: utf-8 -*-
"""
Auto Apply Master Playlist Thumbnails
- Integrates master_thumbnail_prompt_engine.py
- Generates bespoke prompts tailored to every playlist's title, track, and mood.
- Uploads thumbnails directly to Lead Video and refreshes playlist server cache.
- Fully automated for existing 10 playlists and any future new playlist or music video.
"""

import os
import sys
import json
import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from master_thumbnail_prompt_engine import build_master_thumbnail_prompt, CATEGORY_CONFIGS

sys.stdout.reconfigure(encoding="utf-8")

def log(msg):
    print(msg, flush=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "youtube_token.json")
PROMPTS_FILE = os.path.join(BASE_DIR, "playlist_master_prompts.json")

# All 10 Channel Playlists
PLAYLIST_REGISTRY = [
    {"id": "PLTS50VUZ5khw", "name": "🧘 Stress Relief & Mental Peace | Flute Meditation", "lead_vid": "X0EMsuBBhr4"},
    {"id": "PLEwYNfw5fPiA", "name": "🔴 24/7 Live Spiritual Chanting & Meditation Streams", "lead_vid": "_65f6xs_WUk"},
    {"id": "PLYl7L1G0M6Oc", "name": "🌸 Peaceful Lotus Lake Meditation Flute", "lead_vid": "VDEvUok3pT8"},
    {"id": "PLJ_ReLRXXG2k", "name": "🪕 Pure Bansuri & Tabla Classical Jugalbandi", "lead_vid": "aOMg-IAezXY"},
    {"id": "PLd-E2kzfVUEg", "name": "🕉️ Divine Flute & Pure Meditation Music | Krishna Vibez", "lead_vid": "vuoOW98h96c"},
    {"id": "PLfXTB8iO3Gik", "name": "👑 Royal Raga Darbari & Ancient Heritage Meditation", "lead_vid": "Zb9E7V9LiVM"},
    {"id": "PLPKE2BWZ7HwI", "name": "🌙 Deep Meditative Sleep Music | 432Hz Stress Release", "lead_vid": "sUctWLbOpmY"},
    {"id": "PLbrKp-ssSkJc", "name": "🌊 Sacred Yamuna River & Evening Twilight Ghats", "lead_vid": "PZes6Z-cU8s"},
    {"id": "PLJD6PGkODrOs", "name": "🌅 Golden Sunrise Awakening & Morning Pooja Dhyan", "lead_vid": "CJF8tZpJI8Y"},
    {"id": "PLP-XF1dRgWNk", "name": "🌿 Peaceful Morning Flute & Sacred Meditation", "lead_vid": "InfDz_ftdGE"}
]

def export_all_playlist_prompts():
    """Generates and exports bespoke master prompts for all playlists."""
    exported = []
    for pl in PLAYLIST_REGISTRY:
        prompt, cfg = build_master_thumbnail_prompt(pl["name"])
        entry = {
            "playlist_id": pl["id"],
            "playlist_name": pl["name"],
            "lead_vid": pl["lead_vid"],
            "category_id": cfg["id"],
            "hook_title": cfg["hook_title"],
            "hook_sub": cfg["hook_sub"],
            "prompt": prompt
        }
        exported.append(entry)
    
    with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
        json.dump(exported, f, indent=2, ensure_ascii=False)
    log(f"✅ Exported {len(exported)} bespoke playlist prompts to {PROMPTS_FILE}")
    return exported

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

def refresh_playlist_cache(pl_id):
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
    except Exception as e:
        log(f"  -> Cache touch notice: {e}")

if __name__ == "__main__":
    log("=" * 65)
    log("  KRISHNA VIBEZ — MASTER PLAYLIST THUMBNAIL AUTOMATION")
    log("=" * 65)
    export_all_playlist_prompts()

