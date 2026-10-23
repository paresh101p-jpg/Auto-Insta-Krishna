"""
Catbox Reels Uploader for Auto-Insta-Krishna
- Continuously monitors new_video/*.mp4
- Clears old silent reel URLs on first run and archives to old_silent_reels_backup.txt
- Uploads new .mp4 voice reels to Catbox
- Appends new URLs to reels_urls.txt & reels_urls_backup.txt
- Pushes to GitHub every 10 uploaded reels
"""

import os
import sys
import glob
import time
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEW_VIDEO_DIR = os.path.join(BASE_DIR, "new_video")
REELS_OUTPUT_DIR = os.path.join(BASE_DIR, "reels_output")
REELS_URLS_FILE = os.path.join(BASE_DIR, "reels_urls.txt")
BACKUP_REELS_URLS_FILE = os.path.join(BASE_DIR, "reels_urls_backup.txt")
YT_REELS_URLS_FILE = os.path.join(BASE_DIR, "youtube_reels_urls.txt")
BACKUP_YT_REELS_URLS_FILE = os.path.join(BASE_DIR, "youtube_reels_urls_backup.txt")
TRACKER_FILE = os.path.join(BASE_DIR, "uploaded_reels_tracker.txt")
OLD_SILENT_BACKUP = os.path.join(BASE_DIR, "old_silent_reels_backup.txt")

def init_clean_reels_files():
    """Ensures reels URL files exist without ever clearing or overwriting existing URLs."""
    for fpath in [REELS_URLS_FILE, BACKUP_REELS_URLS_FILE, YT_REELS_URLS_FILE, BACKUP_YT_REELS_URLS_FILE]:
        if not os.path.exists(fpath):
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("")

def get_already_uploaded():
    uploaded = set()
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                name = line.strip()
                if name:
                    uploaded.add(name)
    return uploaded

def save_uploaded_name(name):
    with open(TRACKER_FILE, "a", encoding="utf-8") as f:
        f.write(name + "\n")

def upload_file_to_catbox(file_path, retries=3):
    curl_path = r"C:\Windows\System32\curl.exe"
    cmd = [
        curl_path, "-k", "-s",
        "-F", "reqtype=fileupload",
        "-F", f"fileToUpload=@{file_path}",
        "https://catbox.moe/user/api.php"
    ]
    for attempt in range(retries):
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
            url = res.stdout.strip()
            if url.startswith("https://files.catbox.moe/"):
                return url
            else:
                print(f"Warning: Attempt {attempt+1} got response: {url}", flush=True)
        except Exception as e:
            print(f"Error on attempt {attempt+1}: {e}", flush=True)
        time.sleep(3)
    return None

def push_urls_to_github():
    print("Pushing updated Voice Reel URLs to GitHub...", flush=True)
    subprocess.run(["git", "pull", "--rebase", "origin", "master"], cwd=BASE_DIR)
    subprocess.run(["git", "add", "reels_urls.txt", "reels_urls_backup.txt", "youtube_reels_urls.txt", "youtube_reels_urls_backup.txt", "uploaded_reels_tracker.txt", "old_silent_reels_backup.txt"], cwd=BASE_DIR)
    subprocess.run(["git", "commit", "-m", "feat: Add new high-retention Voice Reel URLs to queue"], cwd=BASE_DIR)
    res = subprocess.run(["git", "push", "origin", "master"], cwd=BASE_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0:
        print("GitHub reels push SUCCESS!", flush=True)
    else:
        print(f"GitHub reels push notice: {res.stderr.strip() or res.stdout.strip()}", flush=True)

def run_reels_uploader(continuous=True):
    init_clean_reels_files()
    print("Catbox Reels Uploader active. Monitoring reels_output & new_video for .mp4 files...", flush=True)
    
    total_uploaded = 0
    while True:
        all_mp4s = glob.glob(os.path.join(REELS_OUTPUT_DIR, "*.mp4")) + glob.glob(os.path.join(NEW_VIDEO_DIR, "*.mp4"))
        all_mp4s.sort()
        
        already_done = get_already_uploaded()
        # Only upload complete mp4s (> 500KB) that are not already tracked
        pending = [f for f in all_mp4s if os.path.basename(f) not in already_done and os.path.getsize(f) > 500000]
        
        if pending:
            print(f"\nFound {len(pending)} new voice reels ready to upload!", flush=True)
            for idx, fpath in enumerate(pending):
                fname = os.path.basename(fpath)
                fsize_mb = os.path.getsize(fpath) / (1024 * 1024)
                print(f"[{idx+1}/{len(pending)}] Uploading Reel {fname} ({fsize_mb:.2f} MB)...", end=" ", flush=True)
                
                url = upload_file_to_catbox(fpath)
                if url:
                    print(f"OK -> {url}", flush=True)
                    with open(REELS_URLS_FILE, "a", encoding="utf-8") as f:
                        f.write(url + "\n")
                    with open(BACKUP_REELS_URLS_FILE, "a", encoding="utf-8") as f:
                        f.write(url + "\n")
                    with open(YT_REELS_URLS_FILE, "a", encoding="utf-8") as f:
                        f.write(url + "\n")
                    with open(BACKUP_YT_REELS_URLS_FILE, "a", encoding="utf-8") as f:
                        f.write(url + "\n")
                    save_uploaded_name(fname)
                    total_uploaded += 1
                else:
                    print(f"FAILED to upload {fname}", flush=True)
                    
                time.sleep(1)
                
                # Push every 10 uploaded reels
                if total_uploaded > 0 and total_uploaded % 10 == 0:
                    print(f"--- Checkpoint: {total_uploaded} new reels uploaded. Pushing to GitHub ---", flush=True)
                    push_urls_to_github()
            
            # Push remaining
            if total_uploaded > 0:
                push_urls_to_github()
                
        if not continuous:
            break
            
        # Check every 30 seconds for newly generated reels
        time.sleep(30)

if __name__ == "__main__":
    run_reels_uploader(continuous=True)
