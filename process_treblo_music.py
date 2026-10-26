#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TREBLO AI MUSIC PROCESSOR & CATBOX CDN SYNC (KRISHNA VIBEZ)
=============================================================================
- Scans 'Treblo Music/' for new lossless WAV, MP3, FLAC, or OGG tracks
- Strips 100% of all external metadata (-map_metadata -1)
- Applies 432Hz harmonic meditation EQ & studio audio mastering
- Uploads directly to Catbox CDN (files.catbox.moe)
- Appends to 'treblo_music_urls.txt' and 'treblo_music_urls_backup.txt'
- Keeps local storage clean by archiving to 'Treblo Music/uploaded/'
- Syncs seamlessly with 15-min Music Videos and 24/7 YouTube Live Stream
=============================================================================
"""

import os
import sys
import time
import shutil
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TREBLO_DIR = os.path.join(BASE_DIR, "Treblo Music")
TREBLO_UPLOADED_DIR = os.path.join(TREBLO_DIR, "uploaded")
TREBLO_URLS_FILE = os.path.join(BASE_DIR, "treblo_music_urls.txt")
TREBLO_BACKUP_URLS_FILE = os.path.join(BASE_DIR, "treblo_music_urls_backup.txt")
TREBLO_USED_URLS_FILE = os.path.join(BASE_DIR, "treblo_music_used_urls.txt")

os.makedirs(TREBLO_DIR, exist_ok=True)
os.makedirs(TREBLO_UPLOADED_DIR, exist_ok=True)

FFMPEG_EXE = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG_EXE):
    FFMPEG_EXE = "ffmpeg"


def upload_file_to_catbox(file_path, retries=3):
    """Uploads file to Catbox CDN via native curl (HTTP/2 & TLS 1.3)."""
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
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90)
            url = res.stdout.strip()
            if url.startswith("https://files.catbox.moe/"):
                return url
            else:
                print(f"  [Attempt {attempt+1}] Catbox response: {url}")
        except Exception as e:
            print(f"  [Attempt {attempt+1}] Catbox error: {e}")
        time.sleep(2)
    return None


def clean_treblo_audio(input_path, output_path):
    """
    Cleans audio:
    - Strips 100% ID3/RIFF metadata (-map_metadata -1)
    - Applies 1.5% micro-tempo shift (atempo=1.015) to guarantee unique acoustic waveform fingerprint
    - Applies 432Hz harmonic meditation EQ & flute studio presence
    - Encodes to broadcast-grade 320kbps MP3
    """
    filter_str = "atempo=1.015,equalizer=f=432:t=q:w=1.2:g=2,equalizer=f=3200:t=q:w=1.5:g=1.2,volume=1.04"
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


def process_all_treblo_music():
    print("=" * 65)
    print("  KRISHNA VIBEZ — TREBLO MUSIC AUTOMATION ENGINE")
    print("=" * 65)

    supported_exts = (".wav", ".mp3", ".ogg", ".flac", ".m4a")
    tracker_file = os.path.join(TREBLO_DIR, "treblo_uploaded_tracker.txt")
    already_uploaded = set()
    if os.path.exists(tracker_file):
        with open(tracker_file, "r", encoding="utf-8") as tf:
            already_uploaded = {l.strip() for l in tf if l.strip()}

    candidates = []
    # 1. Any file directly in TREBLO_DIR (inbox) is ALWAYS a new track added by the user
    if os.path.exists(TREBLO_DIR):
        for f in sorted(os.listdir(TREBLO_DIR)):
            full_p = os.path.join(TREBLO_DIR, f)
            if os.path.isfile(full_p) and f.lower().endswith(supported_exts):
                candidates.append((f, full_p))

    # 2. Also check uploaded/ for any legacy files not yet recorded in tracker
    if os.path.exists(TREBLO_UPLOADED_DIR):
        for f in sorted(os.listdir(TREBLO_UPLOADED_DIR)):
            full_p = os.path.join(TREBLO_UPLOADED_DIR, f)
            if os.path.isfile(full_p) and f.lower().endswith(supported_exts) and f not in already_uploaded:
                if not any(c[0] == f for c in candidates):
                    candidates.append((f, full_p))

    if not candidates:
        print("[INFO] No pending tracks found in 'Treblo Music/'. All tracks already processed!")
        return []

    print(f"[FOUND] {len(candidates)} new Treblo music track(s) ready to process.")
    uploaded_urls = []

    for idx, (fname, raw_path) in enumerate(candidates, 1):
        temp_clean = os.path.join(TREBLO_DIR, f"temp_clean_{int(time.time())}_{idx}.mp3")
        print(f"\n[{idx}/{len(candidates)}] Processing Treblo track: {fname}")
        print(f"  --> Stripping metadata & applying 432Hz harmonic fingerprint modulation...")

        if not clean_treblo_audio(raw_path, temp_clean):
            print(f"  ❌ FFmpeg cleaning failed for: {fname}")
            if os.path.exists(temp_clean):
                try: os.remove(temp_clean)
                except Exception: pass
            continue

        size_mb = os.path.getsize(temp_clean) / (1024 * 1024)
        print(f"  --> Mastered 320k MP3 created: {size_mb:.2f} MB")
        print(f"  --> Uploading to Catbox CDN...")

        url = upload_file_to_catbox(temp_clean)
        if url:
            print(f"  ✅ Upload Success! Catbox URL: {url}")
            uploaded_urls.append(url)

            # Append to queues
            with open(TREBLO_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            with open(TREBLO_BACKUP_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")

            # Move raw file to uploaded folder so Treblo Music inbox stays 100% clean
            dest_archive = os.path.join(TREBLO_UPLOADED_DIR, fname)
            if os.path.exists(dest_archive) and os.path.abspath(dest_archive) != os.path.abspath(raw_path):
                base_n, ext = os.path.splitext(fname)
                dest_archive = os.path.join(TREBLO_UPLOADED_DIR, f"{base_n}_{int(time.time())}{ext}")
            
            try:
                if os.path.abspath(raw_path) != os.path.abspath(dest_archive):
                    shutil.move(raw_path, dest_archive)
                print(f"  --> Archived to Treblo Music/uploaded/ ({os.path.basename(dest_archive)})")
            except Exception as e:
                print(f"  --> Move failed: {e}")

            # Record in tracker
            with open(tracker_file, "a", encoding="utf-8") as tf:
                tf.write(f"{fname}\n")
        else:
            print(f"  ❌ Catbox upload failed for: {fname}")

        if os.path.exists(temp_clean):
            try: os.remove(temp_clean)
            except Exception: pass

    # Calculate and report total pool count
    total_tracks = 0
    if os.path.exists(TREBLO_BACKUP_URLS_FILE):
        with open(TREBLO_BACKUP_URLS_FILE, "r", encoding="utf-8") as f:
            total_tracks = len(set(line.strip() for line in f if line.strip().startswith("http")))

    print(f"\n[COMPLETE] Successfully added {len(uploaded_urls)} new Treblo track(s)!")
    print(f"🎵 TOTAL TREBLO MASTER POOL IS NOW: {total_tracks} TRACKS!")
    return uploaded_urls


if __name__ == "__main__":
    process_all_treblo_music()
