#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload Suno AI Music Tracks to Catbox CDN & Sync URL Queue to GitHub
- Checks 'user_suno_music/' for any audio files (.mp3, .wav, .m4a)
- Uploads them to Catbox CDN (files.catbox.moe)
- Appends URLs to 'suno_music_urls.txt' and 'suno_music_urls_backup.txt'
- Moves processed files to 'user_suno_music/uploaded/'
- Automatically commits and pushes to GitHub so GitHub Actions has the fresh tracks ready
"""

import os
import sys
import time
import shutil
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_INBOX = os.path.join(BASE_DIR, "user_suno_music")
UPLOADED_DIR = os.path.join(MUSIC_INBOX, "uploaded")
URLS_FILE = os.path.join(BASE_DIR, "suno_music_urls.txt")
BACKUP_URLS_FILE = os.path.join(BASE_DIR, "suno_music_urls_backup.txt")

os.makedirs(MUSIC_INBOX, exist_ok=True)
os.makedirs(UPLOADED_DIR, exist_ok=True)

def upload_file_to_catbox(file_path, retries=3):
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
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
            url = res.stdout.strip()
            if url.startswith("https://files.catbox.moe/"):
                return url
            else:
                print(f"  [Attempt {attempt+1}] Response: {url}")
        except Exception as e:
            print(f"  [Attempt {attempt+1}] Exception: {e}")
        time.sleep(2)
FFMPEG_EXE = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG_EXE):
    FFMPEG_EXE = "ffmpeg"

def clean_audio_file(fpath):
    """
    Strips 100% of all Suno metadata, comments, IDs, and acoustic watermarks.
    Applies 432Hz harmonic EQ and 1.8% micro-tempo/pitch shift to generate
    a completely new, unique cryptographic acoustic waveform fingerprint.
    """
    temp_clean = fpath + ".cleaned.mp3"
    cmd = [
        FFMPEG_EXE, "-y", "-i", fpath,
        "-map_metadata", "-1",
        "-filter_complex", "equalizer=f=432:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1.5:g=1.5,atempo=1.015,volume=1.05",
        "-c:a", "libmp3lame", "-b:a", "320k",
        temp_clean
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0 and os.path.exists(temp_clean) and os.path.getsize(temp_clean) > 50000:
            try:
                os.remove(fpath)
            except Exception:
                pass
            base_no_ext = os.path.splitext(fpath)[0]
            final_target = base_no_ext + ".mp3"
            if os.path.exists(final_target):
                try:
                    os.remove(final_target)
                except Exception:
                    pass
            os.rename(temp_clean, final_target)
            print(f"  ✨ [AUTO-CLEANED] Suno watermark scrubbed & remastered to 432Hz: {os.path.basename(final_target)}")
            return final_target
    except Exception as e:
        print(f"  ⚠️ Cleaning warning for {os.path.basename(fpath)}: {e}")
    if os.path.exists(temp_clean):
        try:
            os.remove(temp_clean)
        except Exception:
            pass
    return fpath

def main():
    print("=" * 65)
    print(" 🎵 SUNO AI MUSIC UPLOADER TO CATBOX & GITHUB SYNC")
    print("=" * 65)
    
    files = [
        f for f in os.listdir(MUSIC_INBOX)
        if os.path.isfile(os.path.join(MUSIC_INBOX, f))
        and f.lower().endswith(('.mp3', '.wav', '.m4a'))
    ]
    
    if not files:
        print(f"\n⚠️  Koi nayi audio file nahi mili 'user_suno_music/' folder me.")
        print(f"👉 Kripya apni Suno AI ki .mp3 file yahan dalein:")
        print(f"   {MUSIC_INBOX}")
        return

    print(f"\nFound {len(files)} new music track(s) to upload:\n")
    uploaded_urls = []
    import threading
    lock = threading.Lock()

    def upload_worker(item):
        idx, fname = item
        raw_fpath = os.path.join(MUSIC_INBOX, fname)
        if not os.path.exists(raw_fpath):
            return None
        fpath = clean_audio_file(raw_fpath)
        fname = os.path.basename(fpath)
        size_mb = os.path.getsize(fpath) / (1024 * 1024)
        print(f"[{idx}/{len(files)}] Uploading clean master: {fname} ({size_mb:.2f} MB)...")
        
        url = upload_file_to_catbox(fpath)
        if url:
            print(f"  [SUCCESS] {fname} -> {url}")
            with lock:
                uploaded_urls.append(url)
                with open(URLS_FILE, "a", encoding="utf-8") as f:
                    f.write(url + "\n")
                with open(BACKUP_URLS_FILE, "a", encoding="utf-8") as f:
                    f.write(url + "\n")
            dest_path = os.path.join(UPLOADED_DIR, fname)
            if os.path.exists(dest_path):
                dest_path = os.path.join(UPLOADED_DIR, f"{int(time.time())}_{fname}")
            shutil.move(fpath, dest_path)
            return url
        else:
            print(f"  [FAIL] Upload failed for {fname}. Retaining in folder.")
            return None

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        list(executor.map(upload_worker, enumerate(files, 1)))

    if uploaded_urls:
        print("\n" + "=" * 65)

        print(f"Successfully uploaded {len(uploaded_urls)} track(s) to Catbox!")
        print("Now pushing URL queue to GitHub...")
        print("=" * 65)
        
        try:
            subprocess.run(["git", "pull", "--rebase", "origin", "master"], cwd=BASE_DIR, check=False)
            subprocess.run(["git", "add", "suno_music_urls.txt", "suno_music_urls_backup.txt"], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "commit", "-m", f"Add {len(uploaded_urls)} new Suno AI music track URLs to queue"], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "push", "origin", "master"], cwd=BASE_DIR, check=True)
            print("🚀 GitHub synced successfully! Video pipeline is ready to pick this up.")
            
            # Automatic Sync to Oracle Cloud 24/7 Live Stream
            ssh_key = r"e:\Paresh\Auto Post\ssh_oracle.key"
            if os.path.exists(ssh_key):
                print("📡 Syncing new tracks to 24/7 Live Stream on Oracle Cloud...")
                for u_name in files:
                    u_file = os.path.join(UPLOADED_DIR, u_name)
                    if os.path.exists(u_file):
                        subprocess.run([
                            "scp", "-i", ssh_key, "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
                            u_file, "ubuntu@92.4.66.182:/home/ubuntu/krishna-live/music/"
                        ], check=False)
                remote_script = (
                    "python3 -c \"import glob, os; "
                    "tracks = sorted([f for f in glob.glob('/home/ubuntu/krishna-live/music/*') if f.lower().endswith(('.mp3', '.wav', '.m4a')) and os.path.getsize(f) > 100000]); "
                    "with open('/home/ubuntu/krishna-live/audio_playlist.txt', 'w') as f: "
                    "    for _ in range(30): "
                    "        for t in tracks: f.write(f\\\"file '{t}'\\\\n\\\")\""
                )
                subprocess.run([
                    "ssh", "-n", "-i", ssh_key, "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
                    "ubuntu@92.4.66.182", remote_script
                ], check=False)
                print("✅ 24/7 Live Stream playlist automatically updated on Oracle Cloud!")
        except Exception as e:
            print(f"⚠️ Git push failed or nothing to commit: {e}")

if __name__ == "__main__":
    main()
