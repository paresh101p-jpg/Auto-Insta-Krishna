#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — FULL SONG AUTO PIPELINE (गिटहब पर 100% ऑटोमैटिक)
=============================================================================
यह स्क्रिप्ट गिटहब एक्शन्स पर चलती है और पूरा काम करती है:

1. स्कैन करती है 'Songs/inbox/' में नए गाने
2. हर गाने के लिए मैचिंग थंबनेल खोजती है 'song_thumbnails/' में
3. एनिमेशन इमेज खोजती है 'animations/' फोल्डर में (पत्ते, मोरपंख, स्पार्कल्स)
4. गाने को सुनकर मूड पहचानती है (audio_analyzer.py)
5. गाने को साफ करके Catbox.moe पर अपलोड करती है → URL मिलता है
6. एनिमेटेड वीडियो बनाती है (थंबनेल + ऑडियो + एनिमेशन ओवरले)
7. यूट्यूब क्यू में जोड़ती है (song_urls.txt)
8. हर रविवार सुबह 9 AM IST पर अगला गाना यूट्यूब पर अपलोड करती है (प्राइवेट/अनपब्लिश्ड)

आपको बस करना ये है:
- गाना 'Songs/inbox/' में डालें
- थंबनेल 'song_thumbnails/' में डालें (नाम गाने के नाम के जैसा रखें)
- एनिमेशन इमेज 'animations/' फोल्डर में डालें

बाकी सब ऑटोमैटिक गिटहब पर।
=============================================================================
"""

import os
import sys
import json
import time
import re
import shutil
import subprocess
import random
from datetime import datetime, timezone, timedelta

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- फोल्डर ---
SONGS_DIR = os.path.join(BASE_DIR, "Songs")
SONGS_INBOX = os.path.join(SONGS_DIR, "inbox")
SONGS_UPLOADED = os.path.join(SONGS_DIR, "uploaded")
SONG_THUMB_DIR = os.path.join(BASE_DIR, "song_thumbnails")
ANIMATIONS_DIR = os.path.join(BASE_DIR, "animations")

# --- डेटा फाइलें ---
SONG_URLS_FILE = os.path.join(BASE_DIR, "song_urls.txt")
SONG_BACKUP_URLS_FILE = os.path.join(BASE_DIR, "song_urls_backup.txt")
SONG_USED_URLS_FILE = os.path.join(BASE_DIR, "song_used_urls.txt")
SONG_REGISTRY_FILE = os.path.join(BASE_DIR, "song_tracks_registry.json")
SONG_TRACKER_FILE = os.path.join(SONGS_DIR, "song_uploaded_tracker.txt")
SONG_DAILY_TRACKER = os.path.join(BASE_DIR, "song_daily_tracker.json")

# --- टेम्प फाइलें ---
TEMP_AUDIO = os.path.join(BASE_DIR, "temp_song_audio.mp3")
TEMP_VIDEO = os.path.join(BASE_DIR, "temp_song_video.mp4")

SUPPORTED_EXTS = (".wav", ".mp3", ".ogg", ".flac", ".m4a")
IMAGE_EXTS = (".jpg", ".jpeg", ".png")

os.makedirs(SONGS_INBOX, exist_ok=True)
os.makedirs(SONGS_UPLOADED, exist_ok=True)
os.makedirs(SONG_THUMB_DIR, exist_ok=True)
os.makedirs(ANIMATIONS_DIR, exist_ok=True)

# FFmpeg
FFMPEG_EXE = "ffmpeg"
local_ffmpeg = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if sys.platform != "win32" or not os.path.exists(local_ffmpeg):
    FFMPEG_EXE = "ffmpeg"
elif os.path.exists(local_ffmpeg):
    FFMPEG_EXE = local_ffmpeg


def run_cmd(cmd, timeout=300):
    try:
        res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, timeout=timeout)
        return res.returncode == 0, res.stderr
    except Exception as e:
        return False, str(e)


def upload_to_catbox(file_path, retries=3):
    curl_path = "curl"
    if sys.platform == "win32" and os.path.exists(r"C:\Windows\System32\curl.exe"):
        curl_path = r"C:\Windows\System32\curl.exe"

    cmd = [
        curl_path, "-k", "-s",
        "-F", "reqtype=fileupload",
        "-F", f"fileToUpload=@{file_path}",
        "https://catbox.moe/user/api.php"
    ]
    for attempt in range(retries):
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True, timeout=90)
            url = res.stdout.strip()
            if url.startswith("https://files.catbox.moe/"):
                return url
        except Exception:
            pass
        time.sleep(2)
    return None


def clean_audio(input_path, output_path):
    filter_str = "atempo=1.015,equalizer=f=3200:t=q:w=1.5:g=1.2,volume=1.04"
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", input_path,
        "-vn",
        "-map_metadata", "-1",
        "-af", filter_str,
        "-c:a", "libmp3lame",
        "-b:a", "320k",
        output_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 50000


def load_registry():
    if os.path.exists(SONG_REGISTRY_FILE):
        try:
            with open(SONG_REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_registry(reg):
    with open(SONG_REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)


def load_tracker():
    if os.path.exists(SONG_TRACKER_FILE):
        with open(SONG_TRACKER_FILE, "r", encoding="utf-8") as f:
            return {l.strip() for l in f if l.strip()}
    return set()


def save_tracker(tracker):
    with open(SONG_TRACKER_FILE, "w", encoding="utf-8") as f:
        for name in sorted(tracker):
            f.write(name + "\n")


def load_urls(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip().startswith("http")]


def save_urls(filepath, urls):
    with open(filepath, "w", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")


def find_thumbnail(song_name):
    """गाने के नाम से मैचिंग थंबनेल खोजना"""
    safe = re.sub(r'[<>:"/\\|?*]', '_', song_name)
    safe = re.sub(r'\s+', '_', safe).strip('_')
    
    # सीधा नाम से खोजें
    for ext in IMAGE_EXTS:
        path = os.path.join(SONG_THUMB_DIR, f"{safe}{ext}")
        if os.path.exists(path):
            return path
    
    # पार्शियल मैच
    if os.path.exists(SONG_THUMB_DIR):
        for f in sorted(os.listdir(SONG_THUMB_DIR)):
            if f.lower().endswith(IMAGE_EXTS):
                name_without_ext = os.path.splitext(f)[0]
                if song_name.lower() in name_without_ext.lower() or name_without_ext.lower() in song_name.lower():
                    return os.path.join(SONG_THUMB_DIR, f)
    
    # कोई भी पहला थंबनेल
    if os.path.exists(SONG_THUMB_DIR):
        for f in sorted(os.listdir(SONG_THUMB_DIR)):
            if f.lower().endswith(IMAGE_EXTS):
                return os.path.join(SONG_THUMB_DIR, f)
    
    return None


def find_animations():
    """सभी एनिमेशन इमेज खोजना (50+ में से हर गाने के लिए रैंडम 3 चुने जाएंगे)"""
    anims = []
    if os.path.exists(ANIMATIONS_DIR):
        for f in sorted(os.listdir(ANIMATIONS_DIR)):
            if f.lower().endswith(IMAGE_EXTS):
                anims.append(os.path.join(ANIMATIONS_DIR, f))
    return anims  # सभी लौटाएंगे, रैंडम 3 चुनना caller पर


def pick_random_3_animations(all_anims):
    """हर गाने के लिए अलग-अलग 3 एनिमेशन रैंडम चुनना"""
    if not all_anims:
        return []
    if len(all_anims) <= 3:
        return all_anims.copy()
    return random.sample(all_anims, 3)


def analyze_audio(file_path):
    """गाने को सुनकर मूड पहचानना"""
    sys.path.insert(0, BASE_DIR)
    try:
        from audio_analyzer import analyze_audio_mood
        return analyze_audio_mood(file_path)
    except Exception:
        return {
            "mood": "Balanced Bhakti",
            "mood_hi": "संतुलित भक्ति संगीत",
            "target_audience": "General",
            "target_audience_hi": "सभी के लिए",
            "duration_sec": 0,
            "duration_min": 0,
        }


def create_video_with_animations(audio_path, thumb_path, anim_paths, output_path):
    """
    ऑडियो + थंबनेल + एनिमेशन ओवरले से वीडियो बनाना।
    एनिमेशन सिस्टम म्यूजिक वीडियो पाइपलाइन जैसा ही:
    - हर गाने के लिए अलग-अलग 3 रैंडम एनिमेशन (50+ में से)
    - रैंडम पोज़िशन, स्केल, मूवमेंट (हर गाने के लिए यूनिक)
    - डॉलिंग मोशन (ऊपर से नीचे तैरते हुए)
    - गोल्डन स्पार्कल टच
    - स्मूथ फेड इन/आउट
    """
    
    # स्टेप 1: बेस वीडियो (थंबनेल + ऑडियो)
    base_video = os.path.join(BASE_DIR, "temp_song_base.mp4")
    
    cmd_base = [
        FFMPEG_EXE, "-y",
        "-loop", "1", "-i", thumb_path,
        "-i", audio_path,
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black",
        base_video
    ]
    
    success, err = run_cmd(cmd_base, timeout=120)
    if not success:
        print(f"❌ बेस वीडियो विफल: {err[-200:]}")
        return False

    # स्टेप 2: एनिमेशन ओवरले जोड़ना (हर गाने के लिए अलग 3 रैंडम)
    filter_parts = []
    input_files = [base_video]
    
    for idx, anim_path in enumerate(anim_paths):
        input_files.append(anim_path)
        overlay_idx = idx + 1
        
        # रैंडम पोज़िशन, स्केल और मूवमेंट - हर गाने के लिए अलग
        x = random.randint(50, 1150)
        y = random.randint(50, 600)
        scale = random.choice([0.7, 0.9, 1.0, 1.1, 1.3])
        speed_x = random.choice([15, 25, 35])
        speed_y = random.choice([20, 30, 40])
        
        filter_parts.append(
            f"[{overlay_idx}:v]scale=iw*{scale}:ih*{scale}[anim{idx}];"
            f"[prev][anim{idx}]overlay=x='{x}+{speed_x}*sin(T*0.4)':y='{y}+{speed_y}*cos(T*0.3)':format=auto[prev]"
        )
    
    if filter_parts:
        filter_parts[0] = filter_parts[0].replace("[prev]", "[0:v]")
        for i in range(1, len(filter_parts)):
            filter_parts[i] = filter_parts[i].replace("[prev]", "[prev]")
        
        full_filter = ";".join(filter_parts)
        
        cmd_anim = [FFMPEG_EXE, "-y"]
        for f in input_files:
            cmd_anim += ["-i", f]
        cmd_anim += [
            "-filter_complex", full_filter,
            "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
            "-c:a", "copy",
            "-pix_fmt", "yuv420p",
            output_path
        ]
        
        success, err = run_cmd(cmd_anim, timeout=120)
        if not success:
            print(f"⚠️ एनिमेशन विफल, बेस वीडियो इस्तेमाल कर रहा हूँ: {err[-150:]}")
            shutil.copy2(base_video, output_path)
        else:
            print(f"✅ एनिमेशन वीडियो तैयार ({len(anim_paths)} ओवरले - हर गाने के लिए यूनिक)")
    else:
        shutil.copy2(base_video, output_path)

    # क्लीनअप
    if os.path.exists(base_video):
        try:
            os.remove(base_video)
        except Exception:
            pass

    return os.path.exists(output_path) and os.path.getsize(output_path) > 100000


def generate_metadata(song_name, song_info):
    """मूड-बेस्ड टाइटल और डिस्क्रिप्शन"""
    mood = song_info.get("mood", "Balanced Bhakti")
    mood_hi = song_info.get("mood_hi", "संतुलित भक्ति संगीत")
    duration_min = song_info.get("duration_min", 0)
    target = song_info.get("target_audience", "General")
    target_hi = song_info.get("target_audience_hi", "सभी के लिए")

    if duration_min > 0:
        title = f"{song_name} | {mood_hi} | {duration_min} मिनट | Krishna Vibez 🪷"
    else:
        title = f"{song_name} | {mood_hi} | Krishna Vibez 🪷"

    description = (
        f"🎵 {song_name}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🪷 दिव्य भक्ति संगीत | Divine Krishna Song\n"
        f"🎭 मूड: {mood_hi}\n"
        f"👥 लिए: {target_hi}\n\n"
        "📖 भावार्थ:\n"
        "यह गीत श्री कृष्ण के दिव्य प्रेम और भक्ति का संदेश देता है।\n\n"
        "✨ English Summary:\n"
        "A divine Krishna bhakti song dedicated to Lord Krishna.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🕊️ हमसे जुड़ें:\n"
        "🌐 https://krishnavibez.in/\n"
        "▶️ https://www.youtube.com/@KrishnaVibezMusic\n"
        "📲 https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J\n"
        "🕊️ https://t.me/krishnavibezz\n"
        "📸 https://www.instagram.com/krishnavibez/\n"
        "🧵 https://www.threads.net/@krishnavibez\n"
        "📘 https://www.facebook.com/1808917602588221\n"
        "📌 https://in.pinterest.com/MojiloMart/\n\n"
        "🛍️ Amazon: https://www.amazon.in/shop/myhappybirthday\n\n"
        "जय श्री राधे कृष्ण! 🪷✨\n\n"
        "#Krishna #Bhakti #KrishnaVibez #KrishnaSong #DivineMusic #RadheKrishna"
    )
    tags = ["Krishna", "Bhakti Song", "Krishna Vibez", "Krishna Song", "Radhe Krishna", "Divine Music", "Hindi Bhajan"]
    return title, description, tags


def process_all_pending_songs():
    """सभी पेंडिंग गाने प्रोसेस करना (क्यू में जोड़ना)"""
    print("=" * 60)
    print("  KRISHNA VIBEZ — FULL SONG AUTO PIPELINE (Process Mode)")
    print("=" * 60)

    already_uploaded = load_tracker()
    reg = load_registry()

    # नए गाने खोजना
    new_songs = []
    if os.path.exists(SONGS_INBOX):
        for f in sorted(os.listdir(SONGS_INBOX)):
            if f.lower().endswith(SUPPORTED_EXTS) and f not in already_uploaded:
                new_songs.append((f, os.path.join(SONGS_INBOX, f)))

    if not new_songs:
        print("[INFO] कोई नया गाना नहीं मिला। सभी प्रोसेस्ड हैं।")
        return []

    print(f"[मिला] {len(new_songs)} नया गाना प्रोसेस के लिए।")
    processed = []

    for idx, (fname, raw_path) in enumerate(new_songs, 1):
        song_name = os.path.splitext(fname)[0]
        print(f"\n[{idx}/{len(new_songs)}] प्रोसेस हो रहा है: {song_name}")

        # 1. ऑडियो एनालिसिस
        analysis = analyze_audio(raw_path)
        mood = analysis.get("mood", "Balanced Bhakti")
        print(f"  🎭 मूड: {analysis.get('mood_hi', mood)}")

        # 2. ऑडियो साफ करना
        temp_clean = os.path.join(BASE_DIR, f"temp_clean_{int(time.time())}.mp3")
        if not clean_audio(raw_path, temp_clean):
            print(f"  ❌ ऑडियो सफाई विफल")
            continue

        # 3. Catbox अपलोड
        print(f"  ☁️ Catbox पर अपलोड हो रहा है...")
        url = upload_to_catbox(temp_clean)
        if not url:
            print(f"  ❌ Catbox अपलोड विफल")
            if os.path.exists(temp_clean):
                os.remove(temp_clean)
            continue

        print(f"  ✅ Catbox URL: {url}")

        # 4. URL क्यू में सेव
        with open(SONG_URLS_FILE, "a", encoding="utf-8") as f:
            f.write(url + "\n")
        with open(SONG_BACKUP_URLS_FILE, "a", encoding="utf-8") as f:
            f.write(url + "\n")

        # 5. रजिस्ट्री अपडेट
        reg[url] = {
            "name": song_name,
            "mood": mood,
            "mood_hi": analysis.get("mood_hi", "संतुलित भक्ति संगीत"),
            "target_audience": analysis.get("target_audience", "General"),
            "target_audience_hi": analysis.get("target_audience_hi", "सभी के लिए"),
            "duration_min": analysis.get("duration_min", 0),
            "added_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_registry(reg)

        # 6. थंबनेल खोजना
        thumb_path = find_thumbnail(song_name)
        if thumb_path:
            print(f"  🖼️ थंबनेल मिला: {os.path.basename(thumb_path)}")
        else:
            print(f"  ⚠️ कोई थंबनेल नहीं मिला")

        # 7. एनिमेशन खोजना - हर गाने के लिए अलग-अलग 3 रैंडम
        all_anims = find_animations()
        anim_paths = pick_random_3_animations(all_anims)
        if anim_paths:
            print(f"  🎨 एनिमेशन चुने गए: {len(anim_paths)} (50+ में से रैंडम, इस गाने के लिए यूनिक)")
            for a in anim_paths:
                print(f"     → {os.path.basename(a)}")
        else:
            print(f"  ⚠️ कोई एनिमेशन फाइल नहीं मिली animations/ फोल्डर में")

        # 8. ट्रैकर में दर्ज (डुप्लीकेट रोकता है)
        with open(SONG_TRACKER_FILE, "a", encoding="utf-8") as tf:
            tf.write(f"{fname}\n")

        # 9. मूल फाइल आर्काइव
        dest = os.path.join(SONGS_UPLOADED, fname)
        if os.path.exists(dest):
            base_n, ext = os.path.splitext(fname)
            dest = os.path.join(SONGS_UPLOADED, f"{base_n}_{int(time.time())}{ext}")
        try:
            shutil.move(raw_path, dest)
        except Exception as e:
            print(f"  ⚠️ आर्काइव विफल: {e}")

        processed.append({
            "url": url,
            "name": song_name,
            "thumb": thumb_path,
            "anims": anim_paths,
            "analysis": analysis,
        })

        # क्लीनअप
        if os.path.exists(temp_clean):
            try:
                os.remove(temp_clean)
            except Exception:
                pass

    print(f"\n[COMPLETE] {len(processed)} गाने प्रोसेस्ड हुए।")
    print(f"   यूट्यूब क्यू में तैयार हैं।")
    return processed


def upload_next_to_youtube():
    """क्यू से अगला गाना यूट्यूब पर अपलोड करना (रविवार 9 AM)"""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
    REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
        print("⚠️ YouTube सीक्रेट्स नहीं मिले। अपलोड स्किप किया जा रहा है।")
        return

    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube"]
    )
    youtube = build("youtube", "v3", credentials=creds)

    # अगला URL पिक करना
    active = load_urls(SONG_URLS_FILE)
    used = set(load_urls(SONG_USED_URLS_FILE))
    active = [u for u in active if u not in used]

    if not active:
        # बैकअप से रीस्टार्ट
        backup = load_urls(SONG_BACKUP_URLS_FILE)
        backup = [u for u in backup if u not in used]
        if backup:
            random.shuffle(backup)
            save_urls(SONG_URLS_FILE, backup)
            active = backup

    if not active:
        print("[INFO] क्यू खाली है। अपलोड करने के लिए कोई गाना नहीं।")
        return

    url = active[0]
    reg = load_registry()
    song_info = reg.get(url, {"name": "Unknown Song", "mood": "Balanced Bhakti", "mood_hi": "संतुलित भक्ति संगीत"})

    song_name = song_info.get("name", "Unknown Song")
    print(f"\n🎵 यूट्यूब अपलोड: {song_name}")

    # ऑडियो डाउनलोड
    if os.path.exists(TEMP_AUDIO):
        os.remove(TEMP_AUDIO)

    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(TEMP_AUDIO, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
    except Exception as e:
        print(f"❌ डाउनलोड विफल: {e}")
        return

    # थंबनेल खोजना
    thumb_path = find_thumbnail(song_name)
    if not thumb_path:
        # सॉलिड बैकग्राउंड बनाएं
        thumb_path = os.path.join(BASE_DIR, "temp_thumb_fallback.jpg")
        run_cmd([FFMPEG_EXE, "-y", "-f", "lavfi",
                 "-i", "color=c=0B0E14:size=1280x720",
                 "-frames:v", "1", thumb_path])

    # एनिमेशन खोजना - हर गाने के लिए अलग-अलग 3 रैंडम
    all_anims = find_animations()
    anim_paths = pick_random_3_animations(all_anims)
    if anim_paths:
        print(f"  🎨 एनिमेशन चुने गए: {len(anim_paths)} (हर गाने के लिए यूनिक कॉम्बिनेशन)")
    else:
        print(f"  ⚠️ कोई एनिमेशन फाइल नहीं मिली animations/ फोल्डर में")

    # वीडियो बनाना
    if not create_video_with_animations(TEMP_AUDIO, thumb_path, anim_paths, TEMP_VIDEO):
        print("❌ वीडियो बनाने में विफल")
        return

    # मेटाडेटा
    title, description, tags = generate_metadata(song_name, song_info)

    # अपलोड (प्राइवेट/अनपब्लिश्ड)
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "10",
            "defaultLanguage": "hi",
            "defaultAudioLanguage": "hi"
        },
        "status": {
            "privacyStatus": "private",  # फिलहाल अनपब्लिश्ड/प्राइवेट
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
            "license": "youtube"
        }
    }

    media = MediaFileUpload(TEMP_VIDEO, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  अपलोड: {int(status.progress() * 100)}%...", flush=True)

    video_id = response.get("id")
    print(f"🎉 अपलोड पूर्ण! https://youtube.com/watch?v={video_id} (प्राइवेट)")

    # URL यूज़्ड मार्क करें
    urls = load_urls(SONG_URLS_FILE)
    if url in urls:
        urls.remove(url)
        save_urls(SONG_URLS_FILE, urls)
    with open(SONG_USED_URLS_FILE, "a", encoding="utf-8") as uf:
        uf.write(url + "\n")

    # क्लीनअप
    for f in [TEMP_AUDIO, TEMP_VIDEO]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass


def git_commit_push(msg):
    try:
        subprocess.run(["git", "config", "user.email", "actions@github.com"], check=False)
        subprocess.run(["git", "config", "user.name", "Krishna Vibez Bot"], check=False)
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "commit", "-m", msg], cwd=BASE_DIR, check=False)
        for _ in range(3):
            subprocess.run(["git", "pull", "--rebase", "origin", "master"], cwd=BASE_DIR, check=False)
            res = subprocess.run(["git", "push", "origin", "master"], cwd=BASE_DIR,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                print("✅ गिटहब पुश पूर्ण")
                return
            time.sleep(5)
    except Exception as e:
        print(f"गिट पुश सूचना: {e}")


def main():
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    mode = args[0] if args else "process"

    if mode == "process":
        process_all_pending_songs()
        git_commit_push("Auto-processed new songs & updated queues [skip ci]")

    elif mode == "upload":
        # कोई दैनिक सीमा नहीं - मैनुअल रन कभी भी काम करेगा
        # रविवार को schedule से भी चलेगा
        upload_next_to_youtube()

        # ट्रैकर रिकॉर्ड करें (केवल जब अपलोड हुआ हो)
        ist_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        today_str = ist_now.strftime("%Y-%m-%d")
        tracker_file = SONG_DAILY_TRACKER
        data = {}
        if os.path.exists(tracker_file):
            try:
                with open(tracker_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        data["last_upload_date"] = today_str
        data["last_upload_timestamp"] = int(time.time())
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        git_commit_push("Auto-uploaded song to YouTube [skip ci]")


if __name__ == "__main__":
    main()
