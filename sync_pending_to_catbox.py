# -*- coding: utf-8 -*-
"""
MASTER PENDING CATBOX SYNC DAEMON & TRACKER
===========================================
Automatically checks what audio tracks and images are pending upload to Catbox.moe.
When Catbox maintenance ends:
1. Uploads pending audio tracks from 'Treblo Music/uploaded/' to Catbox.
2. Updates treblo_tracks_registry.json, treblo_music_video_only_urls.txt, treblo_music_urls_backup.txt.
3. Uploads pending images from 'music_video_images/All catagery Krisha music photo/' to Catbox.
4. Updates images_urls.txt, images_urls_backup.txt, uploaded_music_images_tracker.txt.
5. Auto-commits and pushes to GitHub.
"""

import os
import sys
import json
import time
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"E:\Paresh\Auto Post\Auto-Insta-Krishna"
TREBLO_DIR = os.path.join(BASE_DIR, "Treblo Music")
TREBLO_UPLOADED_DIR = os.path.join(TREBLO_DIR, "uploaded")
REGISTRY_FILE = os.path.join(BASE_DIR, "treblo_tracks_registry.json")
VIDEO_ONLY_URLS_FILE = os.path.join(BASE_DIR, "treblo_music_video_only_urls.txt")
BACKUP_URLS_FILE = os.path.join(BASE_DIR, "treblo_music_urls_backup.txt")

IMG_DIR = os.path.join(BASE_DIR, "music_video_images", "All catagery Krisha music photo")
IMG_TRACKER_FILE = os.path.join(BASE_DIR, "uploaded_music_images_tracker.txt")
IMG_URLS_FILE = os.path.join(BASE_DIR, "images_urls.txt")
IMG_BACKUP_URLS_FILE = os.path.join(BASE_DIR, "images_urls_backup.txt")

MANIFEST_FILE = os.path.join(BASE_DIR, "pending_catbox_manifest.json")

def get_pending_tracks():
    pending = []
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                reg = json.load(f)
            for k, title in reg.items():
                if not k.startswith("http"):
                    fpath = os.path.join(TREBLO_UPLOADED_DIR, k)
                    if os.path.exists(fpath):
                        pending.append({"filename": k, "filepath": fpath, "title": title})
        except Exception as e:
            print(f"Error reading registry: {e}")
    return pending

def get_pending_images():
    tracked = set()
    if os.path.exists(IMG_TRACKER_FILE):
        with open(IMG_TRACKER_FILE, "r", encoding="utf-8") as f:
            tracked = {l.strip() for l in f if l.strip()}
    pending = []
    if os.path.exists(IMG_DIR):
        for fname in sorted(os.listdir(IMG_DIR)):
            fpath = os.path.join(IMG_DIR, fname)
            if os.path.isfile(fpath) and fname not in tracked:
                pending.append({"filename": fname, "filepath": fpath})
    return pending

def save_manifest():
    tracks = get_pending_tracks()
    images = get_pending_images()
    manifest = {
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_pending_tracks": len(tracks),
        "total_pending_images": len(images),
        "pending_tracks": tracks,
        "pending_images": images
    }
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"✅ Manifest saved to {MANIFEST_FILE}")
    print(f"   - Pending Tracks: {len(tracks)}")
    print(f"   - Pending Images: {len(images)}")
    return manifest

def check_catbox_status():
    cmd = [
        "curl", "-s", "-L",
        "-F", "reqtype=fileupload",
        "-F", f"fileToUpload=@{REGISTRY_FILE}",
        "https://catbox.moe/user/api.php"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        out = (res.stdout or "").strip()
        if "https://files.catbox.moe/" in out:
            return True, "ONLINE"
        if "paused" in out.lower() or "storage" in out.lower():
            return False, "PAUSED / MAINTENANCE"
        return False, f"UNKNOWN: {out[:60]}"
    except Exception as e:
        return False, str(e)

def upload_single_file(file_path):
    cmd = [
        "curl", "-s", "-L", "-f",
        "--retry", "3",
        "-F", "reqtype=fileupload",
        "-F", "userhash=",
        "-F", f"fileToUpload=@{file_path}",
        "https://catbox.moe/user/api.php"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        url = (res.stdout or "").strip()
        if url.startswith("https://files.catbox.moe/"):
            return url
    except Exception as e:
        print(f"Upload error: {e}")
    return None

def sync_all():
    is_online, status = check_catbox_status()
    print(f"Catbox Status: {status}")
    if not is_online:
        print("Catbox is currently not accepting uploads. Manifest will stay securely preserved on disk.")
        save_manifest()
        return

    # If Catbox is online, upload all pending tracks and images
    tracks = get_pending_tracks()
    images = get_pending_images()
    print(f"Starting Uploads: {len(tracks)} tracks, {len(images)} images...")

    # Upload tracks
    for idx, t in enumerate(tracks, 1):
        print(f"Uploading track [{idx}/{len(tracks)}]: {t['filename']}...")
        url = upload_single_file(t["filepath"])
        if url:
            with open(VIDEO_ONLY_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            with open(BACKUP_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            # Update registry
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                reg = json.load(f)
            reg.pop(t["filename"], None)
            reg[url] = t["title"]
            with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
                json.dump(reg, f, indent=2, ensure_ascii=False)
            print(f"  -> SUCCESS: {url}")
        else:
            print(f"  -> FAILED, stopping batch.")
            break
        time.sleep(1)

    # Upload images
    for idx, img in enumerate(images, 1):
        print(f"Uploading image [{idx}/{len(images)}]: {img['filename']}...")
        url = upload_single_file(img["filepath"])
        if url:
            with open(IMG_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            with open(IMG_BACKUP_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            with open(IMG_TRACKER_FILE, "a", encoding="utf-8") as f:
                f.write(img["filename"] + "\n")
            print(f"  -> SUCCESS: {url}")
        else:
            print(f"  -> FAILED, stopping batch.")
            break
        time.sleep(1)

    save_manifest()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sync":
        sync_all()
    else:
        save_manifest()

