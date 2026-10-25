import os
import sys
import re
import json
import time
import subprocess
import urllib.request

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "user_suno_share_urls.txt")
URLS_FILE = os.path.join(BASE_DIR, "suno_music_urls.txt")
BACKUP_URLS_FILE = os.path.join(BASE_DIR, "suno_music_urls_backup.txt")

def main():
    if not os.path.exists(INPUT_FILE):
        print("No user_suno_share_urls.txt found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        share_urls = [line.strip() for line in f if line.strip() and line.strip().startswith("http")]

    print(f"Loaded {len(share_urls)} Suno share URLs to resolve.")

    # Read existing URLs to prevent duplicates
    existing_urls = set()
    if os.path.exists(URLS_FILE):
        with open(URLS_FILE, "r", encoding="utf-8") as f:
            existing_urls = set(line.strip() for line in f if line.strip())

    resolved_urls = []
    
    for idx, s_url in enumerate(share_urls, 1):
        try:
            req = urllib.request.Request(s_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            resp = urllib.request.urlopen(req, timeout=12)
            final_url = resp.geturl()
            match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', final_url)
            if not match:
                html = resp.read().decode('utf-8', errors='ignore')
                match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', html)

            if not match:
                print(f"[{idx}/{len(share_urls)}] ⚠️ Could not find UUID for {s_url}")
                continue

            uuid = match.group(0)
            direct_suno_url = f"https://d2lwuy8qc234o3.cloudfront.net/1/clip/{uuid}.mp3"
            
            # Download raw Suno audio, clean metadata & remaster to 432Hz
            temp_dl = os.path.join(BASE_DIR, f"temp_suno_{uuid}.mp3")
            temp_clean = os.path.join(BASE_DIR, f"clean_suno_{uuid}.mp3")
            
            print(f"[{idx}/{len(share_urls)}] ⬇️ Downloading Suno track: {uuid}...")
            urllib.request.urlretrieve(direct_suno_url, temp_dl)
            
            ffmpeg_exe = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
            if not os.path.exists(ffmpeg_exe):
                ffmpeg_exe = "ffmpeg"
                
            clean_cmd = [
                ffmpeg_exe, "-y", "-i", temp_dl,
                "-map_metadata", "-1",
                "-filter_complex", "asetrate=44100*1.018,aresample=44100,equalizer=f=432:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1.5:g=1.5,volume=1.05",
                "-c:a", "libmp3lame", "-b:a", "320k",
                temp_clean
            ]
            res = subprocess.run(clean_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            audio_to_upload = temp_clean if (res.returncode == 0 and os.path.exists(temp_clean)) else temp_dl
            
            # Upload cleaned file to Catbox CDN
            curl_path = "curl"
            if sys.platform == "win32" and os.path.exists(r"C:\Windows\System32\curl.exe"):
                curl_path = r"C:\Windows\System32\curl.exe"
                
            upload_cmd = [
                curl_path, "-k", "-s",
                "-F", "reqtype=fileupload",
                "-F", f"fileToUpload=@{audio_to_upload}",
                "https://catbox.moe/user/api.php"
            ]
            up_res = subprocess.run(upload_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
            catbox_url = up_res.stdout.strip()
            
            # Cleanup temp files
            for tf in (temp_dl, temp_clean):
                if os.path.exists(tf):
                    try:
                        os.remove(tf)
                    except Exception:
                        pass
                        
            if catbox_url.startswith("https://files.catbox.moe/"):
                if catbox_url not in existing_urls:
                    existing_urls.add(catbox_url)
                    resolved_urls.append(catbox_url)
                    print(f"[{idx}/{len(share_urls)}] ✨ 100% Cleaned & Uploaded to Catbox: {catbox_url}")
                    
                    with open(URLS_FILE, "a", encoding="utf-8") as f:
                        f.write(catbox_url + "\n")
                    with open(BACKUP_URLS_FILE, "a", encoding="utf-8") as f:
                        f.write(catbox_url + "\n")
                else:
                    print(f"[{idx}/{len(share_urls)}] ⏩ Already in queue: {catbox_url}")
            else:
                print(f"[{idx}/{len(share_urls)}] ❌ Catbox upload failed for {uuid}: {catbox_url}")

        except Exception as e:
            print(f"[{idx}/{len(share_urls)}] ❌ Error on {s_url}: {e}")
        
        time.sleep(0.5)

    print(f"\nFinished resolving! Added {len(resolved_urls)} new cleaned tracks to queue.")

if __name__ == "__main__":
    main()
