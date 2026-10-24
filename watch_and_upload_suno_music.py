#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Continuous Background Watcher for Suno AI Music & URLs.
Automatically detects when user adds new files to 'user_suno_music/'
or pastes links into 'user_suno_share_urls.txt', then:
  1. Uploads to Catbox CDN
  2. Updates suno_music_urls.txt
  3. Pushes to GitHub
  4. Syncs directly to Oracle Cloud 24/7 Live Stream
Zero manual interaction needed.
"""

import os
import sys
import time
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_INBOX = os.path.join(BASE_DIR, "user_suno_music")
SHARE_URLS_FILE = os.path.join(BASE_DIR, "user_suno_share_urls.txt")
UPLOAD_SCRIPT = os.path.join(BASE_DIR, "upload_suno_music_to_catbox.py")
RESOLVE_SCRIPT = os.path.join(BASE_DIR, "resolve_suno_urls.py")

os.makedirs(MUSIC_INBOX, exist_ok=True)

def has_pending_audio_files():
    if not os.path.exists(MUSIC_INBOX):
        return False
    valid_exts = ('.mp3', '.m4a', '.wav', '.aac', '.flac')
    for f in os.listdir(MUSIC_INBOX):
        full_p = os.path.join(MUSIC_INBOX, f)
        if os.path.isfile(full_p) and f.lower().endswith(valid_exts):
            # Ensure file is completely written (not still downloading)
            try:
                sz1 = os.path.getsize(full_p)
                time.sleep(0.5)
                sz2 = os.path.getsize(full_p)
                if sz1 == sz2 and sz1 > 5000:
                    return True
            except Exception:
                pass
    return False

def has_pending_share_urls():
    if not os.path.exists(SHARE_URLS_FILE):
        return False
    try:
        with open(SHARE_URLS_FILE, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip() and l.strip().startswith("http")]
        return len(lines) > 0
    except Exception:
        return False

def run_watcher():
    print("=" * 65)
    print(" 👀 AUTO-WATCHER: SUNO MUSIC & LIVE STREAM AUTO-SYNC ACTIVE")
    print(" Monitoring 'user_suno_music/' and 'user_suno_share_urls.txt'...")
    print("=" * 65)

    py_exe = sys.executable

    while True:
        try:
            # Check 1: Pending share URLs in txt file
            if has_pending_share_urls():
                print("\n[Auto-Watcher] 🌐 Detected new Suno Share URLs! Resolving...")
                subprocess.run([py_exe, RESOLVE_SCRIPT], check=False)
                # Clear the share URLs file once processed
                try:
                    with open(SHARE_URLS_FILE, "w", encoding="utf-8") as f:
                        f.write("")
                except Exception:
                    pass

            # Check 2: Pending local audio files in folder
            if has_pending_audio_files():
                print("\n[Auto-Watcher] 🎵 Detected new Suno Audio Files! Uploading & Syncing...")
                subprocess.run([py_exe, UPLOAD_SCRIPT], check=False)

        except Exception as e:
            print(f"[Auto-Watcher Error] {e}")

        time.sleep(8)

if __name__ == "__main__":
    run_watcher()
