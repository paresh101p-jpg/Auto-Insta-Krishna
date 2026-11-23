#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — SONG PROCESSOR & CATBOX CDN SYNC (SEPARATE SONG PIPELINE)
=============================================================================
- स्कैन करता है 'Songs/inbox/' में नए गाने (MP3, WAV, OGG, FLAC, M4A)
- गाने को सुनकर ऑडियो एनालिसIS करता है (मूड, वॉल्यूम, टेम्पो, ड्यूरेशन)
- मेटाडेटा हटाता है (-map_metadata -1) और यूनिक ऑडियो फिंगरप्रिंट बनाता है
- Catbox.moe पर अपलोड करता है → URL मिलता है
- URL को 'song_urls.txt' और 'song_urls_backup.txt' में सेव करता है (म्यूजिक URL से अलग)
- 'song_tracks_registry.json' में URL → गाने का नाम + मूड एनालिसिस सेव करता है
- मूल फाइल को 'Songs/uploaded/' में आर्काइव करता है
- 'song_uploaded_tracker.txt' में दर्ज करता है (डुप्लीकेट रोकता है)
- जब भी गाने का URL add होता है, साथ में थंबनेल भी ऑटो बनता है ('song_thumbnails/')
=============================================================================
"""

import os
import sys
import time
import json
import re
import shutil
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- सॉन्ग-ओनली फोल्डर (म्यूजिक से अलग) ---
SONGS_DIR = os.path.join(BASE_DIR, "Songs")
SONGS_INBOX = os.path.join(SONGS_DIR, "inbox")
SONGS_UPLOADED = os.path.join(SONGS_DIR, "uploaded")

# --- सॉन्ग-ओनली URL फाइलें (म्यूजिक से अलग) ---
SONG_URLS_FILE = os.path.join(BASE_DIR, "song_urls.txt")
SONG_BACKUP_URLS_FILE = os.path.join(BASE_DIR, "song_urls_backup.txt")
SONG_USED_URLS_FILE = os.path.join(BASE_DIR, "song_used_urls.txt")

# --- सॉन्ग-ओनली रजिस्ट्री और ट्रैकर ---
SONG_REGISTRY_FILE = os.path.join(BASE_DIR, "song_tracks_registry.json")
SONG_TRACKER_FILE = os.path.join(SONGS_DIR, "song_uploaded_tracker.txt")

SUPPORTED_EXTS = (".wav", ".mp3", ".ogg", ".flac", ".m4a")

os.makedirs(SONGS_INBOX, exist_ok=True)
os.makedirs(SONGS_UPLOADED, exist_ok=True)

# FFmpeg पाथ
FFMPEG_EXE = "ffmpeg"
local_ffmpeg = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG_EXE) or sys.platform != "win32":
    FFMPEG_EXE = "ffmpeg"
elif os.path.exists(local_ffmpeg):
    FFMPEG_EXE = local_ffmpeg


def upload_file_to_catbox(file_path, retries=3):
    """फाइल को Catbox CDN पर अपलोड करना curl से"""
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
            else:
                print(f"  [Attempt {attempt+1}] Catbox response: {url}")
        except Exception as e:
            print(f"  [Attempt {attempt+1}] Catbox error: {e}")
        time.sleep(2)
    return None


def clean_song_audio(input_path, output_path):
    """
    गाने की ऑडियो साफ़ करना:
    - सारा ID3/RIFF मेटाडेटा हटाना (-map_metadata -1)
    - माइक्रो-टेम्पो शिफ्ट (atempo=1.015) यूनिक अकूस्टिक फिंगरप्रिंट के लिए
    - 320kbps MP3 में एनकोड करना
    """
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
    return (res.returncode == 0 and os.path.exists(output_path)
            and os.path.getsize(output_path) > 50000)


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


def process_all_songs():
    print("=" * 65)
    print("  KRISHNA VIBEZ — SONG PROCESSOR (गाने को सुनकर मूड पहचानना)")
    print("=" * 65)

    tracker_file = SONG_TRACKER_FILE
    already_uploaded = set()
    if os.path.exists(tracker_file):
        with open(tracker_file, "r", encoding="utf-8") as tf:
            already_uploaded = {l.strip() for l in tf if l.strip()}

    candidates = []
    if os.path.exists(SONGS_INBOX):
        for f in sorted(os.listdir(SONGS_INBOX)):
            full_p = os.path.join(SONGS_INBOX, f)
            if os.path.isfile(full_p) and f.lower().endswith(SUPPORTED_EXTS):
                candidates.append((f, full_p))

    # uploaded/ में भी पुरानी फाइलें चेक करना जो ट्रैकर में नहीं हैं
    if os.path.exists(SONGS_UPLOADED):
        for f in sorted(os.listdir(SONGS_UPLOADED)):
            full_p = os.path.join(SONGS_UPLOADED, f)
            if (os.path.isfile(full_p) and f.lower().endswith(SUPPORTED_EXTS)
                    and f not in already_uploaded):
                if not any(c[0] == f for c in candidates):
                    candidates.append((f, full_p))

    if not candidates:
        print("[INFO] कोई नया गाना नहीं मिला 'Songs/inbox/' में। सभी गाने प्रोसेस्ड हैं!")
        return []

    print(f"[मिला] {len(candidates)} नया गाना प्रोसेस के लिए तैयार है।")
    uploaded_urls = []

    # ऑडियो एनालाइज़र इम्पोर्ट करना
    sys.path.insert(0, BASE_DIR)
    try:
        from audio_analyzer import analyze_audio_mood
    except ImportError:
        analyze_audio_mood = None

    # थंबनेल जनरेटर इम्पोर्ट करना
    try:
        from create_song_thumbnails import generate_thumbnail_for_song
    except ImportError:
        generate_thumbnail_for_song = None

    for idx, (fname, raw_path) in enumerate(candidates, 1):
        temp_clean = os.path.join(SONGS_DIR, f"temp_clean_song_{int(time.time())}_{idx}.mp3")
        print(f"\n[{idx}/{len(candidates)}] गाना प्रोसेस हो रहा है: {fname}")
        print(f"  --> गाना सुनकर मूड एनालिसिस किया जा रहा है...")

        # --- स्टेप 1: गाने को सुनकर मूड पहचानना ---
        mood = "Balanced Bhakti"
        mood_hi = "संतुलित भक्ति संगीत"
        analysis_data = {}
        if analyze_audio_mood:
            try:
                analysis_data = analyze_audio_mood(raw_path)
                mood = analysis_data.get("mood", "Balanced Bhakti")
                mood_hi = analysis_data.get("mood_hi", "संतुलित भक्ति संगीत")
                print(f"  🎭 मूड पहचाना गया: {mood_hi} ({mood})")
            except Exception as e:
                print(f"  ⚠️ मूड एनालिसिस त्रुटि: {e}")

        print(f"  --> मेटाडेटा हटाना और यूनिक ऑडियो फिंगरप्रिंट बनाना...")

        if not clean_song_audio(raw_path, temp_clean):
            print(f"  ❌ FFmpeg सफाई विफल: {fname}")
            if os.path.exists(temp_clean):
                try:
                    os.remove(temp_clean)
                except Exception:
                    pass
            continue

        size_mb = os.path.getsize(temp_clean) / (1024 * 1024)
        print(f"  --> मास्टर्ड 320k MP3 बन गया: {size_mb:.2f} MB")
        print(f"  --> Catbox CDN पर अपलोड हो रहा है...")

        url = upload_file_to_catbox(temp_clean)
        if url:
            print(f"  ✅ अपलोड सफल! Catbox URL: {url}")
            uploaded_urls.append(url)

            # --- सॉन्ग-ओनली URL क्यू में सेव करना (म्यूजिक से अलग) ---
            with open(SONG_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            with open(SONG_BACKUP_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")

            # --- रजिस्ट्री में URL → गाने का नाम + मूड सेव करना ---
            clean_track = os.path.splitext(fname)[0]
            clean_track = re.sub(r'_\d+$', '', clean_track)
            clean_track = re.sub(r'\s*\(\d+\)$', '', clean_track).strip()
            reg = load_registry()
            reg[url] = {
                "name": clean_track,
                "mood": mood,
                "mood_hi": mood_hi,
                "duration_sec": analysis_data.get("duration_sec", 0),
                "duration_min": analysis_data.get("duration_min", 0),
                "rms_level_db": analysis_data.get("rms_level_db", 0),
                "peak_level_db": analysis_data.get("peak_level_db", 0),
                "dynamic_range_db": analysis_data.get("dynamic_range_db", 0),
                "is_vocal_likely": analysis_data.get("is_vocal_likely", True),
                "added_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            save_registry(reg)

            # --- मूल फाइल को Songs/uploaded/ में आर्काइव करना ---
            dest_archive = os.path.join(SONGS_UPLOADED, fname)
            if os.path.exists(dest_archive) and os.path.abspath(dest_archive) != os.path.abspath(raw_path):
                base_n, ext = os.path.splitext(fname)
                dest_archive = os.path.join(SONGS_UPLOADED, f"{base_n}_{int(time.time())}{ext}")
            try:
                if os.path.abspath(raw_path) != os.path.abspath(dest_archive):
                    shutil.move(raw_path, dest_archive)
                print(f"  --> आर्काइव किया गया: Songs/uploaded/ ({os.path.basename(dest_archive)})")
            except Exception as e:
                print(f"  --> मूव विफल: {e}")

            # --- ट्रैकर में दर्ज करना (डुप्लीकेट रोकता है) ---
            with open(tracker_file, "a", encoding="utf-8") as tf:
                tf.write(f"{fname}\n")

            # --- जब URL add हो, साथ में थंबनेल भी ऑटो बनाना ---
            if generate_thumbnail_for_song:
                print(f"  🎨 गाने के साथ थंबनेल भी बन रहा है...")
                thumb_audio_path = dest_archive if os.path.exists(dest_archive) else temp_clean
                generate_thumbnail_for_song(
                    clean_track,
                    audio_path=thumb_audio_path,
                    mood=mood,
                    mood_hi=mood_hi,
                )
        else:
            print(f"  ❌ Catbox अपलोड विफल: {fname}")

        if os.path.exists(temp_clean):
            try:
                os.remove(temp_clean)
            except Exception:
                pass

    # कुल पूल काउंट रिपोर्ट करना
    total_songs = 0
    if os.path.exists(SONG_BACKUP_URLS_FILE):
        with open(SONG_BACKUP_URLS_FILE, "r", encoding="utf-8") as f:
            total_songs = len(set(line.strip() for line in f if line.strip().startswith("http")))

    print(f"\n[पूर्ण] {len(uploaded_urls)} नए गाने सफलतापूर्वक जोड़े गए!")
    print(f"🎵 कुल सॉन्ग मास्टर पूल अब: {total_songs} गाने!")
    print(f"   URL अलग सेव हैं: song_urls.txt (म्यूजिक URL से अलग नहीं मिला)")
    return uploaded_urls


if __name__ == "__main__":
    process_all_songs()
