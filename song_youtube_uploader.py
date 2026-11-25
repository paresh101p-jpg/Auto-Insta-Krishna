#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — SONG YOUTUBE UPLOADER (SEPARATE PIPELINE)
=============================================================================
- हर रविवार सुबह 9:00 AM IST पर चलता है (GitHub Actions cron)
- 'song_urls.txt' से अगला गाना URL पिक करता है (म्यूजिक URL से अलग)
- क्यू खाली होने पर 'song_urls_backup.txt' से रीस्टार्ट (पर्से हो जाएगा, डुप्लीकेट नहीं)
- Catbox URL से गाने का ऑडियो डाउनलोड करता है
- पहले से बना थंबनेल ('song_thumbnails/') वीडियो में जोड़ता है
- मूड एनालिसिस के हिसाब से टाइटल और डिस्क्रिप्शन लिखता है
- URL को 'song_used_urls.txt' में भेजता है (डुप्लीकेट अपलोड नहीं होता)
- नया गाना आते ही अपने आप क्यू में जुड़ता है और अगले रविवार अपलोड होता है
- सोशल मीडिया और अमेज़न लिंक वही रहती हैं
=============================================================================
"""

import os
import sys
import time
import json
import subprocess
import random
import re
import cv2
from datetime import datetime, timezone, timedelta

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- सॉन्ग-ओनली फाइलें ---
SONG_URLS_FILE = os.path.join(BASE_DIR, "song_urls.txt")
SONG_BACKUP_URLS_FILE = os.path.join(BASE_DIR, "song_urls_backup.txt")
SONG_USED_URLS_FILE = os.path.join(BASE_DIR, "song_used_urls.txt")
SONG_REGISTRY_FILE = os.path.join(BASE_DIR, "song_tracks_registry.json")
SONG_THUMB_DIR = os.path.join(BASE_DIR, "song_thumbnails")
SONGS_UPLOADED = os.path.join(BASE_DIR, "Songs", "uploaded")

# --- टेम्प फाइलें ---
TEMP_AUDIO = os.path.join(BASE_DIR, "temp_song_audio.mp3")
TEMP_VIDEO = os.path.join(BASE_DIR, "temp_song_video.mp4")

# YouTube OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

TOKEN_FILE = os.path.join(BASE_DIR, "song_youtube_token.json")

if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                CLIENT_ID = CLIENT_ID or data.get("client_id")
                CLIENT_SECRET = CLIENT_SECRET or data.get("client_secret")
                REFRESH_TOKEN = REFRESH_TOKEN or data.get("refresh_token")
        except Exception as e:
            print(f"टोकन फाइल पढ़ने में सूचना: {e}")

OFFICIAL_LINKS = {
    "website": "https://krishnavibez.in/",
    "youtube": "https://www.youtube.com/@KrishnaVibezMusic",
    "whatsapp": "https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J",
    "telegram": "https://t.me/krishnavibezz",
    "instagram": "https://www.instagram.com/krishnavibez/",
    "threads": "https://www.threads.net/@krishnavibez",
    "facebook": "https://www.facebook.com/1808917602588221",
    "pinterest": "https://in.pinterest.com/MojiloMart/",
    "amazon_shop": "https://www.amazon.in/shop/myhappybirthday",
}


def get_authenticated_service():
    if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
        print("त्रुटि: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN ज़रूरी हैं।")
        sys.exit(1)
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube"]
    )
    return build("youtube", "v3", credentials=creds)


def load_urls(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip().startswith("http")]


def save_urls(filepath, urls):
    with open(filepath, "w", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")


def load_registry():
    if os.path.exists(SONG_REGISTRY_FILE):
        try:
            with open(SONG_REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def get_next_song_url():
    """
    अगला गाना URL एक्टिव क्यू से पिक करना।
    क्यू खाली होने पर बैकअप से रीस्टार्ट (पर्से हो जाएगा, डुप्लीकेट नहीं)।
    (url, song_info) या (None, None) लौटाता है।
    """
    active = load_urls(SONG_URLS_FILE)
    used = set(load_urls(SONG_USED_URLS_FILE))

    # यूज़ हुए URL को एक्टिव क्यू से हटाना (डुप्लीकेट नहीं)
    active = [u for u in active if u not in used]
    save_urls(SONG_URLS_FILE, active)

    if active:
        url = active[0]
        reg = load_registry()
        song_info = reg.get(url, {"name": "Unknown Song", "mood": "Balanced Bhakti", "mood_hi": "संतुलित भक्ति संगीत"})
        return url, song_info

    # क्यू खाली → बैकअप से रीस्टार्ट (पर्से हो जाएगा, डुप्लीकेट नहीं)
    backup = load_urls(SONG_BACKUP_URLS_FILE)
    if backup:
        backup = [u for u in backup if u not in used]
        if backup:
            random.shuffle(backup)  # हर चक्र में क्रम बदलना (ताज़ा अनुभव)
            save_urls(SONG_URLS_FILE, backup)
            url = backup[0]
            reg = load_registry()
            song_info = reg.get(url, {"name": "Unknown Song", "mood": "Balanced Bhakti", "mood_hi": "संतुलित भक्ति संगीत"})
            print(f"🔄 सभी गाने पूरे हुए! बैकअप पूल से ऑटो-रीस्टार्ट ({len(backup)} गाने)।")
            return url, song_info

    return None, None


def download_audio(url):
    """Catbox URL से गाने का ऑडियो डाउनलोड करना"""
    if os.path.exists(TEMP_AUDIO):
        try:
            os.remove(TEMP_AUDIO)
        except Exception:
            pass

    try:
        cmd = [
            "curl", "-s", "-L", "-f",
            "--connect-timeout", "15", "--max-time", "90", "--retry", "3",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            "-o", TEMP_AUDIO, url
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=100)
        if res.returncode == 0 and os.path.exists(TEMP_AUDIO):
            size = os.path.getsize(TEMP_AUDIO)
            if size > 50000:
                print(f"✅ गाना डाउनलोड हुआ: {size / (1024*1024):.2f} MB")
                return True
    except Exception as e:
        print(f"सूचना: curl डाउनलोड त्रुटि: {e}")

    # फॉलबैक: urllib
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=45) as resp:
            if resp.status == 200:
                with open(TEMP_AUDIO, "wb") as f:
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
                size = os.path.getsize(TEMP_AUDIO) if os.path.exists(TEMP_AUDIO) else 0
                if size > 50000:
                    print(f"✅ गाना डाउनलोड हुआ (urllib): {size / (1024*1024):.2f} MB")
                    return True
    except Exception as e:
        print(f"सूचना: urllib डाउनलोड त्रुटि: {e}")

    return False


def find_thumbnail(song_name):
    """गाने के लिए पहले से बना थंबनेल खोजना"""
    safe = re.sub(r'[<>:"/\\|?*]', '_', song_name)
    safe = re.sub(r'\s+', '_', safe).strip('_')
    path = os.path.join(SONG_THUMB_DIR, f"{safe}.jpg")
    if os.path.exists(path):
        return path
    # फॉलबैक: फोल्डर में कोई भी थंबनेल
    if os.path.exists(SONG_THUMB_DIR):
        for f in sorted(os.listdir(SONG_THUMB_DIR)):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                return os.path.join(SONG_THUMB_DIR, f)
    return None


def find_local_audio(song_name):
    """लोकल uploaded फोल्डर में गाने की ऑडियो फाइल खोजना (थंबनेल वेवफॉर्म के लिए)"""
    if not os.path.exists(SONGS_UPLOADED):
        return None
    for f in os.listdir(SONGS_UPLOADED):
        name_without_ext = os.path.splitext(f)[0]
        if name_without_ext.lower() == song_name.lower():
            return os.path.join(SONGS_UPLOADED, f)
    return None


def create_video_from_audio_and_thumb(audio_path, thumb_path, output_path):
    """ऑडियो + थंबनेल इमेज से वीडियो बनाना (YouTube अपलोड के लिए)"""
    ffmpeg_bin = "ffmpeg"
    local = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
    if os.path.exists(local):
        ffmpeg_bin = local

    cmd = [
        ffmpeg_bin, "-y",
        "-loop", "1", "-i", thumb_path,
        "-i", audio_path,
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black",
        output_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 100000


def generate_song_metadata(song_info):
    """
    मूड एनालिसिस के हिसाब से टाइटल, डिस्क्रिप्शन, टैग्स बनाना।
    सोशल मीडिया और अमेज़न लिंक वही रहती हैं।
    """
    song_name = song_info.get("name", "Unknown Song")
    mood = song_info.get("mood", "Balanced Bhakti")
    mood_hi = song_info.get("mood_hi", "संतुलित भक्ति संगीत")
    duration_min = song_info.get("duration_min", 0)
    is_vocal = song_info.get("is_vocal_likely", True)

    # टाइटल
    if duration_min > 0:
        title = f"{song_name} | {mood_hi} | {duration_min} मिनट | Krishna Vibez 🪷"
    else:
        title = f"{song_name} | {mood_hi} | Krishna Vibez 🪷"

    # डिस्क्रिप्शन (मूड-बेस्ड भावार्थ)
    mood_meaning = {
        "Peaceful Meditative": "यह गीत मन को गहरी शांति और एकाग्रता प्रदान करता है। ध्यान, योग और मन की शांति के लिए आदर्श है।",
        "Energetic Devotional": "यह गीत भक्ति की ऊर्जा और उत्साह से भर देता है। पूजा, आरती और धार्मिक आयोजनों के लिए उपयुक्त है।",
        "Romantic Soft": "यह गीत श्री कृष्ण के दिव्य प्रेम को व्यक्त करता है। कोमल भाव और भक्ति रस से ओत-प्रोत है।",
        "Short Devotional": "यह एक छोटा लेकिन प्रभावशाली भक्ति गीत है जो जल्दी ही मन को छू लेता है।",
        "Balanced Bhakti": "यह गीत भक्ति और संतुलन का सुंदर संगम है जो हर अवसर के लिए उपयुक्त है।",
    }
    meaning = mood_meaning.get(mood, mood_meaning["Balanced Bhakti"])

    vocal_note = ""
    if is_vocal:
        vocal_note = "इस गीत में मधुर स्वर और भावपूर्ण गायन है।"

    lyrics_block = ""
    raw_lyrics = song_info.get("lyrics", "")
    if raw_lyrics:
        extracted = []
        for l in str(raw_lyrics).splitlines():
            l = l.strip()
            if not l or "-->" in l or l.isdigit():
                continue
            l = re.sub(r'\[.*?\]', '', l).strip()
            if l and l not in extracted:
                extracted.append(l)
        if extracted:
            lyrics_block = "📜 गीत के मुख्य पावन बोल (Song Lyrics Highlights):\n" + "\n".join(extracted[:6]) + "\n\n"

    description = (
        f"🎵 {song_name}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🪷 दिव्य भक्ति संगीत | Divine Devotional Song\n"
        f"🎭 मूड: {mood_hi}\n"
        f"🎙️ {vocal_note}\n\n"
        "📖 भावार्थ (Song Meaning):\n"
        f"{meaning}\n\n"
        f"{lyrics_block}"
        "✨ English Summary:\n"
        "A divine Krishna bhakti song dedicated to Lord Krishna. "
        "Listen for peace, devotion, and spiritual bliss.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🕊️ हमसे जुड़ें:\n"
        f"🌐 आधिकारिक वेबसाइट: {OFFICIAL_LINKS['website']}\n"
        f"▶️ आधिकारिक YouTube चैनल: {OFFICIAL_LINKS['youtube']}\n"
        f"📲 WhatsApp चैनल: {OFFICIAL_LINKS['whatsapp']}\n"
        f"🕊️ Telegram चैनल: {OFFICIAL_LINKS['telegram']}\n"
        f"📸 Instagram: {OFFICIAL_LINKS['instagram']}\n"
        f"🧵 Threads: {OFFICIAL_LINKS['threads']}\n"
        f"📘 Facebook पेज: {OFFICIAL_LINKS['facebook']}\n"
        f"📌 Pinterest: {OFFICIAL_LINKS['pinterest']}\n\n"
        "🛍️ Divine Recommendations (Amazon Storefront):\n"
        f"👉 Explore our Amazon Store: {OFFICIAL_LINKS['amazon_shop']}\n"
        "(Disclaimer: As an Amazon Associate, Krishna Vibez earns from qualifying purchases.)\n\n"
        "जय श्री राधे कृष्ण! 🪷✨\n\n"
        "#Krishna #Bhakti #KrishnaVibez #KrishnaSong #DivineMusic #RadheKrishna #HindiBhajan"
    )

    tags = [
        "Krishna", "Bhakti Song", "Krishna Vibez", "Krishna Song",
        "Radhe Krishna", "Divine Music", "Hindi Bhajan", "Spiritual",
        "Krishna Bhajan", "Devotional", "Peace Music", mood_hi
    ]
    return title, description, tags


def upload_song_to_youtube(video_path, title, description, tags):
    """गाने का वीडियो YouTube पर अपलोड करना"""
    youtube = get_authenticated_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "10",  # Music
            "defaultLanguage": "hi",
            "defaultAudioLanguage": "hi"
        },
        "status": {
            "privacyStatus": "private",  # फिलहाल अनपब्लिश्ड/प्राइवेट रखना है
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
            "license": "youtube"
        }
    }
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"अपलोड हो रहा है {int(status.progress() * 100)}%...", flush=True)
    video_id = response.get("id")
    print(f"🎉 सफल! गाना अपलोड हुआ: https://youtube.com/watch?v={video_id}")
    return video_id


def mark_song_used(url):
    """URL को एक्टिव क्यू से हटाकर यूज़्ड लिस्ट में भेजना (डुप्लीकेट नहीं)"""
    urls = load_urls(SONG_URLS_FILE)
    if url in urls:
        urls.remove(url)
        save_urls(SONG_URLS_FILE, urls)
    with open(SONG_USED_URLS_FILE, "a", encoding="utf-8") as uf:
        uf.write(url + "\n")
    git_commit_and_push("गाने का URL यूज़ किया गया और हटाया गया [skip ci]")


def git_commit_and_push(commit_msg):
    try:
        subprocess.run(["git", "config", "user.email", "actions@github.com"], check=False)
        subprocess.run(["git", "config", "user.name", "Krishna Vibez Song Bot"], check=False)
        subprocess.run(["git", "add",
                        "song_urls.txt", "song_urls_backup.txt",
                        "song_used_urls.txt", "song_uploaded_tracker.txt",
                        "song_thumbnails_tracker.txt", "song_tracks_registry.json",
                        "song_daily_tracker.json"],
                       cwd=BASE_DIR, check=False)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=False)
        for _ in range(3):
            subprocess.run(["git", "pull", "--rebase", "origin", "master"],
                           cwd=BASE_DIR, check=False)
            res = subprocess.run(["git", "push", "origin", "master"],
                                 cwd=BASE_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True)
            if res.returncode == 0:
                print("✅ गिट पुश पूर्ण हुआ।")
                return
            time.sleep(2)
    except Exception as e:
        print(f"गिट पुश सूचना: {e}")


def check_sunday_limit():
    """सुनिश्चित करना कि रविवार को केवल 1 गाना अपलोड हो"""
    tracker_file = os.path.join(BASE_DIR, "song_daily_tracker.json")
    ist_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    today_str = ist_now.strftime("%Y-%m-%d")
    today_weekday = ist_now.strftime("%A")

    if today_weekday != "Sunday":
        print(f"[स्किप] आज {today_weekday} है, रविवार नहीं। बाहर निकल रहा हूँ।")
        sys.exit(0)

    if os.path.exists(tracker_file):
        try:
            with open(tracker_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            last_date = data.get("last_song_upload_date")
            if last_date == today_str:
                print(f"[स्किप] आज ({today_str} IST) गाना पहले ही अपलोड हो चुका है। बाहर निकल रहा हूँ।")
                sys.exit(0)
        except Exception:
            pass
    return tracker_file, today_str


def record_song_uploaded(tracker_file, today_str):
    data = {}
    if os.path.exists(tracker_file):
        try:
            with open(tracker_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    data["last_song_upload_date"] = today_str
    data["last_song_upload_timestamp"] = int(time.time())
    with open(tracker_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    print("=" * 60)
    print("  KRISHNA VIBEZ — सॉन्ग यूट्यूब अपलोडर")
    print("  समय: हर रविवार सुबह 9:00 AM IST")
    print("=" * 60)

    tracker_file, today_str = check_sunday_limit()

    url, song_info = get_next_song_url()
    if not url:
        print("[सूचना] क्यू में कोई गाना URL उपलब्ध नहीं है।")
        print("   गाने Songs/inbox/ में डालें और process_songs.py चलाएं।")
        sys.exit(0)

    song_name = song_info.get("name", "Unknown Song")
    mood = song_info.get("mood", "Balanced Bhakti")
    mood_hi = song_info.get("mood_hi", "संतुलित भक्ति संगीत")

    print(f"\n🎵 चुना गया गाना: {song_name}")
    print(f"🎭 मूड: {mood_hi} ({mood})")
    print(f"🔗 Catbox URL: {url}")

    # गाने का ऑडियो डाउनलोड करना (Catbox से)
    if not download_audio(url):
        print("❌ Catbox से गाना डाउनलोड करने में विफल।")
        sys.exit(1)

    # पहले से बना थंबनेल खोजना
    thumb_path = find_thumbnail(song_name)
    if not thumb_path:
        print("⚠️ कोई पहले से बना थंबनेल नहीं मिला। सॉलिड बैकग्राउंड का उपयोग कर रहा हूँ।")
        thumb_path = os.path.join(BASE_DIR, "temp_song_thumb.jpg")
        ffmpeg_bin = "ffmpeg"
        subprocess.run([ffmpeg_bin, "-y", "-f", "lavfi",
                        "-i", "color=c=0B0E14:size=1280x720",
                        "-frames:v", "1", thumb_path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # वीडियो बनाना (ऑडियो + थंबनेल इमेज)
    print("🎬 वीडियो बन रहा है (ऑडियो + थंबनेल)...")
    if not create_video_from_audio_and_thumb(TEMP_AUDIO, thumb_path, TEMP_VIDEO):
        print("❌ वीडियो बनाने में विफल।")
        sys.exit(1)

    # मूड-बेस्ड मेटाडेटा बनाना
    title, description, tags = generate_song_metadata(song_info)
    print(f"📝 टाइटल: {title}")

    # YouTube पर अपलोड करना
    try:
        video_id = upload_song_to_youtube(TEMP_VIDEO, title, description, tags)
        record_song_uploaded(tracker_file, today_str)
        mark_song_used(url)
        print(f"\n✅ गाना अपलोड पूर्ण! वीडियो ID: {video_id}")
        print(f"   गाना: {song_name}")
        print(f"   अपलोड किया: {today_str} IST (रविवार 9 AM)")

        # गिट में अपडेटेड क्यू कमिट करना
        git_commit_and_push(f"रविवार का गाना '{song_name}' YouTube पर अपलोड किया गया [skip ci]")

    finally:
        for temp_f in [TEMP_AUDIO, TEMP_VIDEO]:
            if os.path.exists(temp_f):
                try:
                    os.remove(temp_f)
                except Exception:
                    pass


if __name__ == "__main__":
    main()
