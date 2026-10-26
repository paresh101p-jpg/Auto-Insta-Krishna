#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sync Treblo AI tracks on Oracle Cloud server and rebuild audio_playlist.txt (100% Treblo Only)
"""

import os
import subprocess
import glob
import random

BASE_DIR = "/home/ubuntu/krishna-live"
REPO_DIR = os.path.join(BASE_DIR, "repo")
URLS_FILE = os.path.join(REPO_DIR, "treblo_music_urls.txt")
BACKUP_URLS_FILE = os.path.join(REPO_DIR, "treblo_music_urls_backup.txt")
MUSIC_DIR = os.path.join(BASE_DIR, "music", "treblo")
PLAYLIST_FILE = os.path.join(BASE_DIR, "audio_playlist.txt")

os.makedirs(MUSIC_DIR, exist_ok=True)

urls = []
for fpath in [URLS_FILE, BACKUP_URLS_FILE]:
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            urls.extend([l.strip() for l in f if l.strip() and l.strip().startswith("http")])
urls = list(dict.fromkeys(urls))

print(f"Total Treblo URLs to sync: {len(urls)}")

downloaded = 0
for idx, url in enumerate(urls, 1):
    base = os.path.basename(url.split("?")[0])
    dest = os.path.join(MUSIC_DIR, f"track_{idx:03d}_{base}")

    if os.path.exists(dest) and os.path.getsize(dest) > 50000:
        continue

    cmd = ["curl", "-s", "-L", "-f", "--retry", "3", url, "-o", dest]
    res = subprocess.run(cmd)
    if res.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 50000:
        downloaded += 1
        if downloaded % 10 == 0:
            print(f"Downloaded {downloaded} new Treblo tracks...")

print(f"New Treblo tracks downloaded: {downloaded}")

# Gather all Treblo tracks
all_tracks = []
for ext in ["*.mp3", "*.ogg", "*.wav", "*.m4a"]:
    all_tracks.extend(glob.glob(os.path.join(MUSIC_DIR, ext)))
all_tracks = sorted([t for t in all_tracks if os.path.exists(t) and os.path.getsize(t) > 50000])

print(f"Total valid Treblo tracks on disk: {len(all_tracks)}")

# Rebuild audio_playlist.txt (50 repetitions for infinite loop)
with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
    for _ in range(50):
        for t in all_tracks:
            f.write(f"file '{t}'\n")

print(f"Updated {PLAYLIST_FILE} with {len(all_tracks)} Treblo tracks ({len(all_tracks)*50} loop entries)!")
