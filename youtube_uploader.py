# -*- coding: utf-8 -*-
"""
Automated YouTube Shorts Uploader for Krishna Vibez
Posts 3 daily high-retention Voice Reels directly to YouTube Shorts with:
- Monetization-compliant metadata (YPP standards)
- Emotion-adaptive title & deep wisdom descriptions
- Cross-promotion (krishnavibez.in, WhatsApp, Telegram)
- Resumable upload architecture with auto-recycle
"""

import os
import sys
import time
import random
import subprocess
import requests
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google import genai

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "youtube_token.json")
YT_REELS_FILE = os.path.join(BASE_DIR, "youtube_reels_urls.txt")
YT_BACKUP_FILE = os.path.join(BASE_DIR, "youtube_reels_urls_backup.txt")
YT_USED_FILE = os.path.join(BASE_DIR, "youtube_used_urls.txt")
TEMP_VIDEO = os.path.join(BASE_DIR, "temp_yt_short.mp4")

# Load Credentials (from GitHub Actions Secrets with fallback to local youtube_token.json)
CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                CLIENT_ID = CLIENT_ID or data.get("client_id")
                CLIENT_SECRET = CLIENT_SECRET or data.get("client_secret")
                REFRESH_TOKEN = REFRESH_TOKEN or data.get("refresh_token")
        except Exception as e:
            print(f"Notice reading local token file: {e}")

def get_authenticated_service():
    if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
        print("Error: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, and YOUTUBE_REFRESH_TOKEN must be set.")
        sys.exit(1)

    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube"
        ]
    )
    return build("youtube", "v3", credentials=creds)

def reload_reels_from_backup_if_needed():
    urls = []
    if os.path.exists(YT_REELS_FILE):
        with open(YT_REELS_FILE, "r", encoding="utf-8", errors="ignore") as f:
            urls = [line.strip() for line in f if line.strip()]

    if urls:
        return urls

    if os.path.exists(YT_BACKUP_FILE):
        print(f"⚠️ {YT_REELS_FILE} is empty! Auto-recycling from master backup {YT_BACKUP_FILE}...")
        with open(YT_BACKUP_FILE, "r", encoding="utf-8", errors="ignore") as f:
            backup_urls = [line.strip() for line in f if line.strip()]

        if backup_urls:
            unique_urls = list(dict.fromkeys(backup_urls))
            random.shuffle(unique_urls)
            with open(YT_REELS_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(unique_urls) + "\n")
            print(f"✅ Successfully reloaded {len(unique_urls)} reels into {YT_REELS_FILE}!")
            return unique_urls
    return []

def download_video(url):
    print(f"Downloading reel for YouTube upload: {url}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    proxies = [
        "",
        "https://api.allorigins.win/raw?url=",
        "https://corsproxy.io/?"
    ]
    for attempt in range(3):
        try:
            target_url = proxies[attempt % len(proxies)] + url
            res = requests.get(target_url, headers=headers, timeout=40)
            if res.status_code == 200 and len(res.content) > 100000:
                with open(TEMP_VIDEO, "wb") as f:
                    f.write(res.content)
                print(f"Video downloaded successfully ({len(res.content) / (1024*1024):.2f} MB)")
                return True
        except Exception as e:
            print(f"Download attempt {attempt+1} failed: {e}")
        time.sleep(2)
    return False

def generate_youtube_metadata(quote_text=""):
    """
    Generates YPP-compliant YouTube Shorts Title, Description, and Tags.
    Title Pattern: [विचार का मुख्य सार/सीख] | श्री कृष्ण अमृत वचन #Shorts #Krishna #RadheKrishna
    """
    default_title = "कर्म का फल और जीवन की सीख | श्री कृष्ण अमृत वचन #Shorts #Krishna #RadheKrishna"
    default_desc = (
        "भगवान श्री कृष्ण के अनमोल विचार और श्रीमद्भगवद्गीता का दिव्य ज्ञान जो आपके जीवन को सकारात्मक दिशा देगा।\n\n"
        "👉 अधिक प्रेरणादायक विचारों के लिए वेबसाइट देखें:\nhttps://krishnavibez.in/\n\n"
        "📲 हमारे WhatsApp चैनल से जुड़ें:\nhttps://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J\n\n"
        "🕊️ Telegram पर जुड़ें:\nhttps://t.me/krishnavibezz\n\n"
        "#KrishnaVibez #BhagavadGita #DailySuvichar #SpiritualShorts #KrishnaQuotes #RadheKrishna #Shorts"
    )
    tags = [
        "श्री कृष्ण", "Krishna Shorts", "Bhagavad Gita", "Radhe Krishna",
        "Spiritual Reels", "Krishna Vibez", "Shorts", "Daily Suvichar",
        "Krishna Gyan", "Motivational Hindi"
    ]

    if not GEMINI_API_KEY:
        return default_title, default_desc, tags

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            "You are a YouTube Shorts optimization expert for a high-traffic spiritual channel 'Krishna Vibez'.\n"
            "Create metadata for a Lord Krishna wisdom video reel.\n"
            "Rules:\n"
            "1. Title MUST strictly follow pattern: '[Short Wisdom Hook in 4-6 Hindi words] | श्री कृष्ण अमृत वचन #Shorts #Krishna #RadheKrishna'\n"
            "2. Total Title length MUST be under 95 characters.\n"
            "3. Description should be 2-3 inspiring Hindi sentences explaining the deep philosophical wisdom.\n"
            "Return EXACT valid JSON with keys 'title' and 'description_intro'."
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        data = json.loads(text)
        title = data.get("title", default_title)
        if len(title) > 95:
            title = title[:90] + " #Shorts"
        intro = data.get("description_intro", "")
        desc = f"{intro}\n\n{default_desc}"
        return title, desc, tags
    except Exception as e:
        print(f"Notice: Gemini metadata generation fallback ({e})")
        return default_title, default_desc, tags

def upload_short_to_youtube(video_path, title, description, tags):
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22", # People & Blogs
            "defaultLanguage": "hi",
            "defaultAudioLanguage": "hi"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
            "license": "youtube"
        }
    }

    print("Uploading video to YouTube Shorts via resumable upload...")
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%...", flush=True)

    video_id = response.get("id")
    print(f"🎉 SUCCESS! YouTube Short uploaded: https://youtube.com/shorts/{video_id}")
    return video_id

def git_commit_and_push(commit_msg):
    try:
        subprocess.run(["git", "config", "user.email", "actions@github.com"], check=False)
        subprocess.run(["git", "config", "user.name", "Auto Insta Bot"], check=False)
        subprocess.run(["git", "add", "youtube_reels_urls.txt", "youtube_used_urls.txt"], check=False)
        subprocess.run(["git", "commit", "-m", commit_msg], check=False)
        subprocess.run(["git", "push"], check=False)
        print("Git commit and push completed.")
    except Exception as e:
        print(f"Git push notice: {e}")

def mark_url_as_used(url):
    urls = []
    if os.path.exists(YT_REELS_FILE):
        with open(YT_REELS_FILE, "r", encoding="utf-8", errors="ignore") as f:
            urls = [line.strip() for line in f if line.strip()]
    if url in urls:
        urls.remove(url)
        with open(YT_REELS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(urls) + "\n")
    with open(YT_USED_FILE, "a", encoding="utf-8") as uf:
        uf.write(url + "\n")
    git_commit_and_push("Used and removed URL from youtube_reels_urls.txt")

def main():
    print("=" * 60)
    print("  YouTube Shorts Auto Uploader (Krishna Vibez)")
    print("=" * 60)

    urls = reload_reels_from_backup_if_needed()
    if not urls:
        print("Error: No reels available in youtube_reels_urls.txt or backup!")
        sys.exit(1)

    chosen_url = random.choice(urls)
    if not download_video(chosen_url):
        print(f"Failed to download {chosen_url}. Exiting.")
        sys.exit(1)

    title, description, tags = generate_youtube_metadata()
    print(f"Title: {title}")

    try:
        video_id = upload_short_to_youtube(TEMP_VIDEO, title, description, tags)
        mark_url_as_used(chosen_url)
        print("YouTube Short workflow completed successfully!")
    finally:
        if os.path.exists(TEMP_VIDEO):
            try:
                os.remove(TEMP_VIDEO)
            except:
                pass

if __name__ == "__main__":
    main()
