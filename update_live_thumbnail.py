#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — 24/7 YOUTUBE LIVE STREAM ULTRA HIGH-CTR THUMBNAIL UPDATER
=============================================================================
Generates a stunning, magnetic, high-CTR 16:9 thumbnail with:
- Huge 128px Radiant Golden Devanagari Headline
- 82px Pure Diamond White Sub-headline
- Glowing Crimson Live Badge: "🔴 24/7 LIVE STREAM • VRINDAVAN"
- Emotional Benefit Retention Strip: "✨ 100% मन शांत • गहरी नींद • चिंता मुक्ति ✨"
- Luxury Gold "KRISHNA VIBEZ" Brand Signature
- Direct Upload to YouTube Live Stream (Video ID: JOTMkj_W2RE) via REST API
=============================================================================
"""

import os
import sys
import json
import random
import subprocess
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "youtube_token.json")
LIVE_VIDEO_ID = "JOTMkj_W2RE"
IMAGES_DIR = os.path.join(BASE_DIR, "music_video_images")
TEMP_THUMBNAIL = os.path.join(BASE_DIR, "temp_live_thumbnail.jpg")

FFMPEG_EXE = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG_EXE):
    FFMPEG_EXE = "ffmpeg"


def get_youtube_access_token():
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                    t_data = json.load(f)
                    client_id = client_id or t_data.get("client_id")
                    client_secret = client_secret or t_data.get("client_secret")
                    refresh_token = refresh_token or t_data.get("refresh_token")
            except Exception as e:
                print(f"Notice reading token file: {e}")

    if not (client_id and client_secret and refresh_token):
        print("[Error] YouTube credentials missing.")
        return None

    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    resp = requests.post(token_url, data=token_payload)
    if resp.status_code == 200:
        return resp.json().get("access_token")
    else:
        print("[Error] Failed to refresh token:", resp.text)
        return None


def generate_live_thumbnail():
    print("🎨 Generating Ultra High-CTR 24/7 Live Stream Thumbnail...")

    slides = [
        os.path.join(IMAGES_DIR, f) for f in os.listdir(IMAGES_DIR)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]
    if not slides:
        raise FileNotFoundError(f"No slides found in {IMAGES_DIR}")

    selected_slide = random.choice(slides)
    print(f"  -> Selected 16:9 Base Artwork: {os.path.basename(selected_slide)}")

    local_font = os.path.join(BASE_DIR, "NotoSansDevanagari-Bold.ttf")
    if not os.path.exists("C:/Windows/Fonts/Nirmala.ttc") and not os.path.exists(local_font):
        try:
            f_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf"
            r = requests.get(f_url, timeout=10)
            if r.status_code == 200:
                with open(local_font, "wb") as f:
                    f.write(r.content)
        except Exception:
            pass

    hindi_candidates = [
        local_font,
        "C:/Windows/Fonts/Nirmala.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf",
    ]
    hindi_font_file = local_font if os.path.exists(local_font) else "arial.ttf"
    for hc in hindi_candidates:
        if os.path.exists(hc):
            hindi_font_file = hc
            break

    english_candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "arial.ttf"
    ]
    english_font_file = "arial.ttf"
    for ec in english_candidates:
        if os.path.exists(ec):
            english_font_file = ec
            break

    local_english = os.path.join(BASE_DIR, "arialbd.ttf")
    if os.path.exists(local_english):
        english_font_arg = os.path.abspath(local_english).replace("\\", "/").replace(":", "\\:")
    else:
        english_font_arg = os.path.abspath(english_font_file).replace("\\", "/").replace(":", "\\:")

    if os.path.exists(local_font):
        hindi_font_arg = os.path.abspath(local_font).replace("\\", "/").replace(":", "\\:")
    else:
        hindi_font_arg = os.path.abspath(hindi_font_file).replace("\\", "/").replace(":", "\\:")

    badge = "LIVE 24/7   |   VRINDAVAN MEDITATION"
    main_text = "श्री कृष्ण दिव्य बाँसुरी धुन"
    sub_text = "मानसिक शांति और सकारात्मक ऊर्जा"
    hook_pill = "मन की शांति   |   गहरी नींद   |   चिंता मुक्ति"

    vf = (
        f"scale=1920:1080,"
        f"drawbox=y=0:h=180:color=black@0.45:t=fill,"
        f"drawbox=y=500:h=580:color=black@0.84:t=fill,"
        f"drawbox=x=60:y=496:w=1800:h=5:color=goldenrod@0.90:t=fill,"
        f"drawbox=x=70:y=45:w=920:h=90:color=0xCC0000@0.98:t=fill,"
        f"drawbox=x=66:y=41:w=928:h=98:color=0xFFD700@0.90:t=4,"
        f"drawtext=fontfile='{english_font_arg}':text='{badge}':fontcolor=white:fontsize=46:x=105:y=68,"
        f"drawtext=fontfile='{hindi_font_arg}':text='{main_text}':fontcolor=0xFFE600:fontsize=128:x=75:y=550:borderw=10:bordercolor=black,"
        f"drawtext=fontfile='{hindi_font_arg}':text='{sub_text}':fontcolor=white:fontsize=82:x=75:y=725:borderw=8:bordercolor=black,"
        f"drawbox=x=75:y=850:w=1040:h=82:color=0x8B0000@0.95:t=fill,"
        f"drawbox=x=71:y=846:w=1048:h=90:color=goldenrod@0.85:t=3,"
        f"drawtext=fontfile='{hindi_font_arg}':text='{hook_pill}':fontcolor=0xFFF8DC:fontsize=48:x=110:y=868:borderw=3:bordercolor=black,"
        f"drawtext=fontfile='{english_font_arg}':text='KRISHNA VIBEZ':fontcolor=0xFFD700:fontsize=46:x=1500:y=995:borderw=5:bordercolor=black"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", selected_slide,
        "-vf", vf,
        "-frames:v", "1",
        "-update", "1",
        "-q:v", "2",
        TEMP_THUMBNAIL
    ]
    subprocess.run(cmd, cwd=BASE_DIR, check=True)
    # Also save permanent master thumbnail
    import shutil
    perm_path = os.path.join(BASE_DIR, "LIVE_STREAM_HIGH_CTR_THUMBNAIL.jpg")
    shutil.copy2(TEMP_THUMBNAIL, perm_path)
    print(f"  -> High-CTR Live Thumbnail Created: {perm_path}")
    return TEMP_THUMBNAIL


def upload_live_thumbnail(access_token, thumb_path):
    print(f"🚀 Uploading High-CTR Thumbnail to YouTube Live Stream ({LIVE_VIDEO_ID})...")
    thumb_url = f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={LIVE_VIDEO_ID}&uploadType=media"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "image/jpeg"
    }
    with open(thumb_path, "rb") as tf:
        thumb_res = requests.post(thumb_url, headers=headers, data=tf)

    if thumb_res.status_code in [200, 201]:
        print(f"🎉 SUCCESS! Live stream thumbnail updated successfully on YouTube!")
        return True
    else:
        print(f"⚠️ Error uploading live thumbnail: {thumb_res.status_code} - {thumb_res.text}")
        return False


def main():
    thumb_path = generate_live_thumbnail()
    access_token = get_youtube_access_token()
    if access_token:
        upload_live_thumbnail(access_token, thumb_path)
    if os.path.exists(thumb_path):
        try: os.remove(thumb_path)
        except Exception: pass
    print("✨ All Done! High-CTR Live Stream Thumbnail is now live on YouTube!")


if __name__ == "__main__":
    main()
