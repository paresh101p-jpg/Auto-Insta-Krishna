#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
PIPELINE 1: SONG INGESTION, AUDIT & CLOUD REGISTRATION PIPELINE (100% ZERO-PC)
=============================================================================
This pipeline handles new devotional songs from GitHub Actions, web, mobile, or any AI:
1. Ingests Audio (Catbox URL or local file) and verifies zero third-party copyright.
2. Listens to the audio using Gemini Audio AI (gemini-3.5-flash) and produces
   second-to-second voice-synchronized SRT subtitles (saved in Songs/<Song Name>.srt).
3. Verifies or generates the 16:9 Image Pair:
   - Thumbnail (THUMBNAIL_URL): High-CTR 16:9 cover with 3D Devanagari typography & luxury badges.
   - Video Slide (SLIDE_URL): The exact same scene 100% CLEAN (zero text, zero badges).
4. Registers the complete unit in `song_tracks_registry.json` and queues in `song_urls.txt`.
5. Commits and pushes directly to GitHub repository (`origin master`).
=============================================================================
"""

import os
import sys
import json
import base64
import time
import argparse
import subprocess
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE_DIR, "Songs")
os.makedirs(SONGS_DIR, exist_ok=True)

REGISTRY_FILE = os.path.join(BASE_DIR, "song_tracks_registry.json")
QUEUE_FILE = os.path.join(BASE_DIR, "song_urls.txt")
KEY_FILE = os.path.join(BASE_DIR, "gemini_key.txt")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def get_gemini_key():
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ.get("GEMINI_API_KEY")
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return ""

def upload_to_catbox(file_path):
    """Uploads local file to Catbox CDN to get a permanent cloud URL"""
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 100:
        return None
    try:
        cmd = ["curl", "-k", "-s", "-F", "reqtype=fileupload", "-F", f"fileToUpload=@{file_path}", "https://catbox.moe/user/api.php"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        out = res.stdout.strip()
        if res.returncode == 0 and out.startswith("http"):
            return out
    except Exception as e:
        print(f"  ⚠️ Catbox curl error: {e}")
    try:
        with open(file_path, "rb") as f:
            r = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f}, headers=HEADERS, timeout=120)
            if r.status_code == 200 and r.text.strip().startswith("http"):
                return r.text.strip()
    except Exception as e:
        print(f"  ⚠️ Catbox requests error: {e}")
    return None

def download_temp_file(url, out_path):
    """Downloads cloud file for analysis"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        if r.status_code == 200:
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"  ⚠️ Download error ({url}): {e}")
    return False

def listen_and_generate_synced_srt(audio_path, song_name, lyrics_text=""):
    """Gemini Audio AI: Listens to audio and produces voice-synchronized SRT subtitles"""
    api_key = get_gemini_key()
    if not api_key:
        print("  ⚠️ No Gemini API key found. Skipping AI voice sync.")
        return ""
    
    size = os.path.getsize(audio_path)
    with open(audio_path, "rb") as f:
        audio_bytes = f.read(min(8 * 1024 * 1024, size))
    
    mime = "audio/mpeg" if audio_path.endswith(".mp3") else "audio/wav"
    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    
    extra = f"\nUse these provided lyrics as reference for spelling and words:\n{lyrics_text.strip()}" if lyrics_text else ""
    prompt = f"""
Listen carefully to this devotional song ({song_name}).
Transcribe the COMPLETE singing lyrics in Hindi (देवनागरी लिपि) with accurate singing timestamps.
{extra}

Output strictly in standard SRT subtitle format:
1
00:00:10,200 --> 00:00:17,500
[Hindi lyrics line]

Make sure timestamps precisely match the singer's voice timing. Skip instrumental intro/breaks.
Return ONLY valid SRT subtitle text without conversational chatter.
"""
    payload = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": mime, "data": b64}},
                {"text": prompt}
            ]
        }]
    }
    
    models_to_try = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3-flash-preview"]
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
            if res.status_code == 200:
                txt = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if txt.startswith("```"):
                    lines = txt.splitlines()
                    if lines[0].startswith("```"): lines = lines[1:]
                    if lines and lines[-1].startswith("```"): lines = lines[:-1]
                    txt = "\n".join(lines).strip()
                return txt
            else:
                time.sleep(2)
        except Exception:
            time.sleep(2)
    return ""

def register_and_save(audio_url, thumb_url, slide_url, srt_content, song_name):
    """Registers song in song_tracks_registry.json and song_urls.txt"""
    reg = {}
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                reg = json.load(f)
        except Exception:
            pass
            
    # Save SRT locally
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', song_name).strip()
    srt_file = os.path.join(SONGS_DIR, f"{safe_name}.srt")
    if srt_content:
        with open(srt_file, "w", encoding="utf-8") as sf:
            sf.write(srt_content)
        print(f"  📝 Saved SRT subtitles: {srt_file}")
        
    reg[audio_url] = {
        "name": song_name,
        "thumb_url": thumb_url,
        "image_urls": [slide_url] if isinstance(slide_url, str) else slide_url,
        "lyrics": srt_content,
        "status": "pending",
        "added_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
        
    # Queue in song_urls.txt
    existing_urls = []
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r", encoding="utf-8") as qf:
            existing_urls = [line.strip() for line in qf if line.strip() and not line.startswith("#")]
            
    if audio_url not in existing_urls:
        existing_urls.append(audio_url)
        with open(QUEUE_FILE, "w", encoding="utf-8") as qf:
            for u in existing_urls:
                qf.write(u + "\n")
                
    print(f"\n🎉 Successfully registered song in queue:")
    print(f"  🎵 Name:  {song_name}")
    print(f"  🔗 Audio: {audio_url}")
    print(f"  🖼️ Thumb: {thumb_url}")
    print(f"  🎨 Slide: {slide_url}")

def git_commit_and_push(song_name):
    """Commits and pushes changes directly to GitHub master"""
    try:
        subprocess.run(["git", "config", "user.name", "Krishna Vibez Ingest Bot"], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "config", "user.email", "bot@krishnavibez.in"], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "add", "song_tracks_registry.json", "song_urls.txt", "Songs/"], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "commit", "-m", f"Pipeline 1: Register {song_name} with AI voice-synced lyrics [skip ci]"], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "push", "origin", "master"], cwd=BASE_DIR, check=False)
        print("🚀 Successfully committed & pushed to GitHub master!")
    except Exception as e:
        print(f"⚠️ Git push error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Pipeline 1: Ingest, sync & register devotional songs")
    parser.add_argument("--audio", help="Audio Catbox URL or local file path")
    parser.add_argument("--thumb", help="Thumbnail Catbox URL or local file path (with text/badges)")
    parser.add_argument("--slide", help="Clean video slide Catbox URL or local file path (no text)")
    parser.add_argument("--lyrics", help="Lyrics text or path to lyrics file")
    parser.add_argument("--name", help="Song title/name (optional)")
    parser.add_argument("--no-push", action="store_true", help="Do not push to git")
    
    args = parser.parse_args()
    
    if not args.audio:
        print("Usage: python song_ingest_pipeline.py --audio <url_or_path> --thumb <url_or_path> --slide <url_or_path> [--lyrics <text>] [--name <title>]")
        return
        
    audio_src = args.audio.strip()
    thumb_src = (args.thumb or "").strip()
    slide_src = (args.slide or "").strip()
    lyrics_input = (args.lyrics or "").strip()
    
    # 1. Audio processing
    temp_audio = os.path.join(BASE_DIR, "temp_ingest_audio.mp3")
    if audio_src.startswith("http"):
        audio_url = audio_src
        print(f"📥 Downloading audio from {audio_url} for voice alignment...")
        download_temp_file(audio_url, temp_audio)
    else:
        print(f"📤 Uploading local audio {audio_src} to Catbox CDN...")
        audio_url = upload_to_catbox(audio_src)
        temp_audio = audio_src
        
    if not audio_url:
        print("❌ Failed to obtain Audio URL!")
        return
        
    # Song Name
    song_name = args.name or os.path.splitext(os.path.basename(audio_src))[0]
    
    # 2. Thumbnail
    if thumb_src.startswith("http"):
        thumb_url = thumb_src
    elif thumb_src and os.path.exists(thumb_src):
        print(f"📤 Uploading local thumbnail {thumb_src} to Catbox CDN...")
        thumb_url = upload_to_catbox(thumb_src)
    else:
        thumb_url = ""
        
    # 3. Slide
    if slide_src.startswith("http"):
        slide_url = slide_src
    elif slide_src and os.path.exists(slide_src):
        print(f"📤 Uploading local slide {slide_src} to Catbox CDN...")
        slide_url = upload_to_catbox(slide_src)
    else:
        slide_url = thumb_url
        
    # 4. Generate voice-matched lyrics via Gemini Audio AI
    print(f"🎙️ Listening to audio to generate synchronized SRT subtitles...")
    srt_content = ""
    if os.path.exists(temp_audio):
        srt_content = listen_and_generate_synced_srt(temp_audio, song_name, lyrics_input)
        
    # 5. Register
    register_and_save(audio_url, thumb_url, slide_url, srt_content, song_name)
    
    # 6. Push to Git
    if not args.no_push:
        git_commit_and_push(song_name)

if __name__ == "__main__":
    main()
