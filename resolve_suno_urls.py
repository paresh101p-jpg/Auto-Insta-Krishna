import os
import sys
import re
import json
import time
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
            
            # Direct CloudFront audio URL
            audio_url = f"https://d2lwuy8qc234o3.cloudfront.net/1/clip/{uuid}.m4a"
            
            if audio_url not in existing_urls:
                existing_urls.add(audio_url)
                resolved_urls.append(audio_url)
                print(f"[{idx}/{len(share_urls)}] ✅ Resolved: {uuid} -> {audio_url}")
                
                # Append incrementally
                with open(URLS_FILE, "a", encoding="utf-8") as f:
                    f.write(audio_url + "\n")
                with open(BACKUP_URLS_FILE, "a", encoding="utf-8") as f:
                    f.write(audio_url + "\n")
            else:
                print(f"[{idx}/{len(share_urls)}] ⏩ Already exists: {uuid}")

        except Exception as e:
            print(f"[{idx}/{len(share_urls)}] ❌ Error on {s_url}: {e}")
        
        time.sleep(0.1)

    print(f"\nFinished resolving! Added {len(resolved_urls)} new direct audio URLs to queue.")

if __name__ == "__main__":
    main()
