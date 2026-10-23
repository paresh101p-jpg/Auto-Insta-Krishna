# -*- coding: utf-8 -*-
"""
Automated YouTube Shorts Uploader for Krishna Vibez
Posts 3 daily high-retention Voice Reels directly to YouTube Shorts with:
- Smart Anti-Duplicate Engine: Automatically applies subtle video/audio fingerprint variations on every cycle
- AI Vision: Automatically transcribes the exact thought spoken and displayed on screen
- Rich, long website-style description with भावार्थ (meaning), व्यावहारिक सीख (lessons), and English wisdom
- All 6 fully clickable social links (Website, WhatsApp, Telegram, Instagram, Facebook, Pinterest)
- Reel-specific dynamic SEO hashtags & tags for top search ranking
- 100% YPP monetization-compliant metadata
- Resumable upload architecture with infinite auto-recycling
"""

import os
import sys
import time
import random
import shutil
import subprocess
import requests
import json
import cv2
from PIL import Image
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
CYCLE_TRACKER_FILE = os.path.join(BASE_DIR, "youtube_cycle_tracker.txt")
TEMP_VIDEO = os.path.join(BASE_DIR, "temp_yt_short.mp4")
TEMP_ENHANCED = os.path.join(BASE_DIR, "temp_enhanced_short.mp4")
TEMP_FRAME = os.path.join(BASE_DIR, "temp_frame.jpg")

# Official Social & Platform Links (Clickable in YouTube description)
OFFICIAL_LINKS = {
    "website": "https://krishnavibez.in/",
    "youtube": "https://www.youtube.com/@KrishnaVibezofficial",
    "whatsapp": "https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J",
    "telegram": "https://t.me/krishnavibezz",
    "instagram": "https://www.instagram.com/pareshpadsala_/",
    "facebook": "https://www.facebook.com/1808917602588221",
    "pinterest": "https://in.pinterest.com/MojiloMart/"
}

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

def get_current_cycle():
    if os.path.exists(CYCLE_TRACKER_FILE):
        try:
            with open(CYCLE_TRACKER_FILE, "r", encoding="utf-8") as f:
                val = f.read().strip()
                return int(val) if val.isdigit() else 1
        except:
            pass
    return 1

def save_current_cycle(cycle_num):
    try:
        with open(CYCLE_TRACKER_FILE, "w", encoding="utf-8") as f:
            f.write(str(cycle_num) + "\n")
    except Exception as e:
        print(f"Notice saving cycle: {e}")

def reload_reels_from_backup_if_needed():
    urls = []
    if os.path.exists(YT_REELS_FILE):
        with open(YT_REELS_FILE, "r", encoding="utf-8", errors="ignore") as f:
            urls = [line.strip() for line in f if line.strip()]

    if urls:
        return urls

    if os.path.exists(YT_BACKUP_FILE):
        curr_cycle = get_current_cycle()
        next_cycle = curr_cycle + 1
        save_current_cycle(next_cycle)
        print(f"🔄 All reels in active queue completed! Initiating Auto-Recycle Cycle {next_cycle}...")
        
        with open(YT_BACKUP_FILE, "r", encoding="utf-8", errors="ignore") as f:
            backup_urls = [line.strip() for line in f if line.strip()]

        if backup_urls:
            unique_urls = list(dict.fromkeys(backup_urls))
            random.shuffle(unique_urls)
            with open(YT_REELS_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(unique_urls) + "\n")
            print(f"✅ Successfully reloaded & shuffled {len(unique_urls)} reels into {YT_REELS_FILE} for Cycle {next_cycle}!")
            return unique_urls
    return []

def verify_video_integrity(file_path):
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return False
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        cap.release()
        return frames > (fps * 3.0)  # Must have at least 3 seconds of valid readable frames
    except Exception:
        return os.path.exists(file_path) and os.path.getsize(file_path) > 3000000

def download_video(url):
    print(f"Downloading reel for YouTube upload: {url}...")
    if os.path.exists(TEMP_VIDEO):
        try:
            os.remove(TEMP_VIDEO)
        except:
            pass

    # 1. Primary method: curl (Native HTTP/2 & modern TLS stack, 100% resilient on cloud runners)
    try:
        cmd = [
            "curl", "-s", "-L", "-f",
            "--connect-timeout", "15",
            "--max-time", "90",
            "--retry", "3",
            "--retry-delay", "2",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "-o", TEMP_VIDEO,
            url
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=100)
        if res.returncode == 0 and os.path.exists(TEMP_VIDEO):
            file_size = os.path.getsize(TEMP_VIDEO)
            if file_size > 500000 and verify_video_integrity(TEMP_VIDEO):
                print(f"✅ Video downloaded & verified successfully via curl ({file_size / (1024*1024):.2f} MB)")
                return True, False
            else:
                print(f"Warning: curl download completed but failed integrity check (size: {file_size} bytes).")
                return False, True
    except Exception as ce:
        print(f"Notice: curl invocation error: {ce}")

    # 2. Fallback: urllib.request (uses distinct socket implementation)
    try:
        import urllib.request
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "*/*"
            }
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            if resp.status == 200:
                with open(TEMP_VIDEO, "wb") as f:
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
                file_size = os.path.getsize(TEMP_VIDEO) if os.path.exists(TEMP_VIDEO) else 0
                if file_size > 500000 and verify_video_integrity(TEMP_VIDEO):
                    print(f"✅ Video downloaded & verified successfully via urllib ({file_size / (1024*1024):.2f} MB)")
                    return True, False
    except Exception as ue:
        print(f"Notice: urllib download attempt error: {ue}")

    # 3. Fallback: requests with Connection: close
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Connection": "close"
    }
    for attempt in range(1, 3):
        try:
            print(f"Attempt {attempt} downloading via requests from: {url[:80]}...")
            with requests.get(url, headers=headers, timeout=60, stream=True) as res:
                if res.status_code == 200:
                    with open(TEMP_VIDEO, "wb") as f:
                        for chunk in res.iter_content(chunk_size=65536):
                            if chunk:
                                f.write(chunk)
                    file_size = os.path.getsize(TEMP_VIDEO) if os.path.exists(TEMP_VIDEO) else 0
                    if file_size > 500000 and verify_video_integrity(TEMP_VIDEO):
                        print(f"✅ Video downloaded & verified successfully via requests ({file_size / (1024*1024):.2f} MB)")
                        return True, False
                elif res.status_code == 404:
                    print(f"Notice: Video returned 404 Not Found.")
                    return False, True
        except Exception as e:
            print(f"Download attempt {attempt} error: {e}")
        time.sleep(2)

    return False, False

def find_ffmpeg():
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    candidates = [
        r"C:\Users\Admin\.antigravity-ide\extensions\kilocode.kilo-code-7.8.12-win32-x64\bin\ffmpeg.exe",
        r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def apply_smart_video_fingerprint(input_path, output_path=TEMP_ENHANCED):
    """
    Applies subtle dynamic audio-visual variations so that every cycle/upload
    has a 100% unique cryptographic file hash, audio waveform, and pixel matrix.
    Prevents YouTube's Content ID duplicate video detection while preserving pristine quality.
    """
    ffmpeg_bin = find_ffmpeg()
    if not ffmpeg_bin:
        print("Notice: FFmpeg not detected, using original video stream.")
        return input_path

    try:
        # Micro-speed variation: 0.985x to 1.015x (imperceptible to ear, changes audio waveform & duration)
        speed = random.choice([0.985, 0.992, 1.008, 1.015])
        
        # Micro-color grading: subtle contrast & saturation shift (alters every single pixel checksum)
        sat = random.choice([1.02, 1.03, 1.04])
        contrast = random.choice([1.01, 1.02])
        bright = random.choice([0.005, 0.01])

        vf = f"setpts={(1.0 / speed):.4f}*PTS,eq=saturation={sat:.2f}:contrast={contrast:.2f}:brightness={bright:.3f}"
        af = f"atempo={speed:.4f},bass=g=1.5:f=150,treble=g=1.2:f=3500"

        cmd = [
            ffmpeg_bin, "-y",
            "-i", input_path,
            "-filter_complex", f"[0:v]{vf}[v];[0:a]{af}[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "192k",
            "-metadata", "title=Krishna Vibez Daily Shorts",
            "-metadata", f"comment=Cycle Unique Fingerprint {time.time()}",
            output_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            print(f"✅ Smart Anti-Duplicate Fingerprint applied successfully! (Speed: {speed:.3f}x, Saturation: {sat:.2f})")
            return output_path
        else:
            print(f"Notice: FFmpeg fingerprint returned code {res.returncode}. Using original video.")
    except Exception as e:
        print(f"Notice: Video fingerprinting fallback: {e}")
    return input_path

def extract_sharp_frame(video_path, output_image_path=TEMP_FRAME, target_sec=4.0):
    """
    Extracts a frame at second 4.0 where the unblur transition is 100% complete
    and the quote text is crystal sharp and readable.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        target_frame = int(fps * target_sec)
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
        cap.release()
        if ret:
            cv2.imwrite(output_image_path, frame)
            print(f"Captured sharp frame at {target_sec}s for AI vision.")
            return True
    except Exception as e:
        print(f"Notice: Frame extraction error: {e}")
    return False

def generate_youtube_metadata_from_video(video_path):
    """
    Extracts the frame at second 4.0 and uses Gemini Vision to transcribe the exact thought
    and generate a long, beautiful, ranking-optimized description with Hindi & English wisdom.
    """
    has_frame = extract_sharp_frame(video_path)
    
    default_quote = "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।"
    default_title = "कर्म का फल और जीवन की सीख | श्री कृष्ण अमृत वचन #Shorts #Krishna #RadheKrishna"
    default_desc = (
        "🌸 कर्म का मर्म और जीवन की सच्ची शांति\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🪷 दिव्य विचार (Divine Thought):\n"
        f"\"{default_quote}\"\n\n"
        "📖 पावन भावार्थ (Spiritual Meaning):\n"
        "भगवान श्री कृष्ण श्रीमद्भगवद्गीता में समझाते हैं कि मनुष्य का अधिकार केवल अपने पवित्र कर्म करने में है, "
        "उसके परिणामों की चिंता करने में नहीं। जब मन फल की आसक्ति से मुक्त होता है, तब अंतरात्मा में सच्चा आनंद और शांति उत्पन्न होती है।\n\n"
        "🌟 जीवन में व्यावहारिक सीख (Practical Application):\n"
        "• बिना किसी भय या चिंता के अपने दैनिक कर्तव्यों का पूरी निष्ठा से पालन करें।\n"
        "• परिस्थितियों के अनुकूल या प्रतिकूल होने पर भी मन का संतुलन बनाए रखें।\n"
        "• सब कुछ परमात्मा को समर्पित करके निस्वार्थ भाव से जीवन जिएं।\n\n"
        "✨ English Wisdom Summary:\n"
        "\"Focus on your sincere efforts without being attached to the results. Pure dedication brings true peace of mind.\"\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔍 Searches & Topics Covered:\n"
        "Karm Ka Fal | Bhagavad Gita Karma Yoga | Nishkam Karma Hindi | Krishna Suvichar Karma | कर्म का सिद्धांत\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🕊️ श्री कृष्ण के दिव्य सान्निध्य और दैनिक प्रेरणा के लिए हमसे जुड़ें:\n"
        f"🌐 आधिकारिक वेबसाइट: {OFFICIAL_LINKS['website']}\n"
        f"▶️ आधिकारिक YouTube चैनल: {OFFICIAL_LINKS['youtube']}\n"
        f"📲 WhatsApp चैनल: {OFFICIAL_LINKS['whatsapp']}\n"
        f"🕊️ Telegram चैनल: {OFFICIAL_LINKS['telegram']}\n"
        f"📸 Instagram: {OFFICIAL_LINKS['instagram']}\n"
        f"📘 Facebook पेज: {OFFICIAL_LINKS['facebook']}\n"
        f"📌 Pinterest: {OFFICIAL_LINKS['pinterest']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🙏 यदि इस विचार ने आपके हृदय को छुआ हो, तो वीडियो को लाइक करें, अपने परिजनों के साथ शेयर करें और चैनल को सब्सक्राइब अवश्य करें।\n\n"
        "जय श्री राधे कृष्ण! 🪷✨\n\n"
        "#Shorts #Krishna #RadheKrishna #KrishnaVibez #DailySuvichar #Karma #KarmYoga #GeetaGyan #Inspiration"
    )
    default_tags = [
        "Karm Ka Fal", "Karma Yoga", "Bhagavad Gita Karma", "Nishkam Karma",
        "श्री कृष्ण", "Krishna Shorts", "Radhe Krishna", "Krishna Vibez",
        "Shorts", "Daily Suvichar", "Krishna Gyan", "Motivational Hindi"
    ]

    if not GEMINI_API_KEY:
        return default_title, default_desc, default_tags

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = (
            "You are a YouTube Shorts growth & spiritual content optimization expert for 'Krishna Vibez'.\n"
            "Analyze this video frame from our Lord Krishna reel.\n"
            "Task:\n"
            "1. Read and transcribe the EXACT Hindi spiritual thought/suvichar printed physically on the image.\n"
            "2. Identify the core theme/topic of this thought (e.g. Karma, Dhairya/Patience, Krodh/Anger, Prem/Love, Bura Waqt/Hard Times, Vishwas/Faith, etc.).\n"
            "3. Generate highly relevant YouTube metadata matching THIS SPECIFIC THOUGHT (never generic):\n"
            "   - 'hook_title': A high-CTR viral hook (4-6 Hindi words with strong emotional keywords directly from the thought).\n"
            "   - 'exact_thought': The exact Hindi thought transcribed from the frame.\n"
            "   - 'spiritual_meaning': 2-3 deep, inspiring Hindi sentences explaining the spiritual philosophy of this specific thought.\n"
            "   - 'practical_lessons': List of 3 concise, actionable bullet points in Hindi for daily life based on this thought.\n"
            "   - 'english_summary': 1-2 soulful sentences in English explaining the core wisdom of this specific thought.\n"
            "   - 'thought_hashtags': 5-8 hashtags that DIRECTLY reflect this specific thought and its topic (e.g. if about Dhairya: #Dhairya, #Patience, #BuraWaqt, #Samay; if about Karma: #Karma, #KarmFal, #Duty; if about Anger: #Krodh, #AngerManagement, #InnerPeace).\n"
            "   - 'thought_search_queries': 6-8 exact long-tail search queries in Hindi and Hinglish that people search on YouTube for this specific topic (e.g. 'mushkil samay me kya kare', 'dhairya par krishna suvichar', 'krodh par geeta gyan').\n"
            "   - 'thought_tags': 10-15 YouTube search tags specifically matching this thought's theme.\n"
            "Return valid JSON ONLY."
        )

        contents = []
        if has_frame and os.path.exists(TEMP_FRAME):
            img = Image.open(TEMP_FRAME)
            contents = [img, prompt]
        else:
            contents = [prompt]

        models_to_try = ["gemini-3.8-flash", "gemini-3.8-pro", "gemini-3.7-flash"]
        response = None
        for m in models_to_try:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=contents
                )
                if response and response.text:
                    break
            except Exception as me:
                print(f"Notice: Model {m} failed: {me}")

        if not (response and response.text):
            try:
                for dyn_m in client.models.list():
                    m_name = dyn_m.name.replace("models/", "") if hasattr(dyn_m, "name") and dyn_m.name else ""
                    if m_name and m_name not in models_to_try and "flash" in m_name.lower():
                        try:
                            print(f"Trying dynamic model: {m_name}...")
                            response = client.models.generate_content(model=m_name, contents=contents)
                            if response and response.text:
                                break
                        except Exception as dyn_err:
                            print(f"Notice with {m_name}: {dyn_err}")
            except Exception as dyn_list_err:
                print(f"Notice listing models: {dyn_list_err}")
        
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        data = json.loads(text)
        
        hook = data.get("hook_title", "जीवन का दिव्य संदेश")
        exact_thought = data.get("exact_thought", default_quote)
        meaning = data.get("spiritual_meaning", "श्री कृष्ण का यह पावन विचार हमारे मन को शांति और सही दिशा प्रदान करता है।")
        lessons = data.get("practical_lessons", [
            "परिस्थितियों से घबराने के बजाय धैर्य और विश्वास बनाए रखें।",
            "अपने सभी कर्मों को ईश्वर को समर्पित करके शांति से कार्य करें।",
            "सकारात्मक सोच और निष्ठा से आगे बढ़ते रहें।"
        ])
        english = data.get("english_summary", "True peace comes from surrender and righteous action guided by the Divine.")

        # 1. Thought-specific hashtags matching the exact reel
        raw_hashtags = data.get("thought_hashtags", []) or data.get("custom_hashtags", [])
        formatted_thought_tags = []
        for ht in raw_hashtags:
            clean_ht = str(ht).strip()
            if not clean_ht.startswith("#"):
                clean_ht = f"#{clean_ht}"
            if clean_ht and clean_ht not in formatted_thought_tags:
                formatted_thought_tags.append(clean_ht)

        # Base platform tags + thought-specific hashtags
        base_hashtags = ["#Shorts", "#Krishna", "#RadheKrishna", "#KrishnaVibez", "#DailySuvichar"]
        all_hashtags = base_hashtags + [t for t in formatted_thought_tags if t not in base_hashtags]
        hashtags_str = " ".join(all_hashtags)

        # 2. Thought-specific search queries matching the exact reel
        raw_searches = data.get("thought_search_queries", [])
        if raw_searches and isinstance(raw_searches, list):
            dynamic_searches_str = " | ".join([str(s).strip() for s in raw_searches if str(s).strip()])
        else:
            dynamic_searches_str = f"{hook} | श्री कृष्ण अमृत वचन | Krishna Suvichar Hindi | Radha Krishna Status"

        reel_seo_block = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔍 Searches & Topics Covered:\n"
            f"{dynamic_searches_str}\n"
        )

        # 3. Thought-specific backend tags: Reel-specific tags FIRST, then anchor tags
        thought_tags = data.get("thought_tags", []) or data.get("tags", [])
        anchor_tags = ["Krishna Shorts", "Radhe Krishna", "श्री कृष्ण", "Krishna Vibez", "Shorts", "Daily Suvichar", "Geeta Gyan"]
        
        ranking_tags = []
        seen = set()
        total_chars = 0
        for tag in (thought_tags + anchor_tags):
            clean_tag = str(tag).strip().replace("#", "")
            if clean_tag and clean_tag.lower() not in seen:
                seen.add(clean_tag.lower())
                if total_chars + len(clean_tag) + 1 <= 480:
                    ranking_tags.append(clean_tag)
                    total_chars += len(clean_tag) + 1

        # Title formatting: must be under 95 characters
        title = f"{hook} | श्री कृष्ण अमृत वचन #Shorts #Krishna #RadheKrishna"
        if len(title) > 95:
            title = f"{hook[:35]} | श्री कृष्ण अमृत वचन #Shorts #Krishna"

        # Build Rich, Aesthetic Description
        lessons_text = "\n".join([f"• {item}" for item in lessons])
        
        description = (
            f"🌸 {hook}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🪷 दिव्य विचार (Divine Thought):\n"
            f"\"{exact_thought}\"\n\n"
            "📖 पावन भावार्थ (Spiritual Meaning):\n"
            f"{meaning}\n\n"
            "🌟 जीवन में व्यावहारिक सीख (Practical Application):\n"
            f"{lessons_text}\n\n"
            "✨ English Wisdom Summary:\n"
            f"\"{english}\"\n\n"
            + reel_seo_block +
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🕊️ श्री कृष्ण के दिव्य सान्निध्य और दैनिक प्रेरणा के लिए हमसे जुड़ें:\n"
            f"🌐 आधिकारिक वेबसाइट: {OFFICIAL_LINKS['website']}\n"
            f"▶️ आधिकारिक YouTube चैनल: {OFFICIAL_LINKS['youtube']}\n"
            f"📲 WhatsApp चैनल: {OFFICIAL_LINKS['whatsapp']}\n"
            f"🕊️ Telegram चैनल: {OFFICIAL_LINKS['telegram']}\n"
            f"📸 Instagram: {OFFICIAL_LINKS['instagram']}\n"
            f"📘 Facebook पेज: {OFFICIAL_LINKS['facebook']}\n"
            f"📌 Pinterest: {OFFICIAL_LINKS['pinterest']}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🙏 यदि इस विचार ने आपके हृदय को स्पर्श किया हो, तो कृपया लाइक करें, अपने प्रियजनों के साथ शेयर करें और चैनल को सब्सक्राइब अवश्य करें।\n\n"
            "जय श्री राधे कृष्ण! 🪷✨\n\n"
            f"{hashtags_str}"
        )

        return title, description, ranking_tags
    except Exception as e:
        print(f"Notice: Gemini metadata generation fallback: {e}")
        return default_title, default_desc, default_tags

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
        subprocess.run(["git", "add", "youtube_reels_urls.txt", "youtube_used_urls.txt", "youtube_cycle_tracker.txt"], check=False)
        subprocess.run(["git", "commit", "-m", commit_msg], check=False)
        for _ in range(3):
            subprocess.run(["git", "pull", "--rebase", "origin", "master"], check=False)
            res = subprocess.run(["git", "push"], check=False)
            if res.returncode == 0:
                print("Git commit and push completed.")
                return
            time.sleep(2)
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

    chosen_url = None
    upload_video_path = None
    max_url_attempts = 5

    for attempt_idx in range(max_url_attempts):
        if not urls:
            urls = reload_reels_from_backup_if_needed()
            if not urls:
                break

        candidate_url = random.choice(urls)
        print(f"\n[Attempt {attempt_idx + 1}/{max_url_attempts}] Selecting candidate reel: {candidate_url}")

        success, is_corrupt = download_video(candidate_url)
        if success:
            chosen_url = candidate_url
            break
        else:
            if is_corrupt:
                print(f"⚠️ Video at {candidate_url} confirmed corrupted or 404. Discarding broken URL from queue...")
                if candidate_url in urls:
                    urls.remove(candidate_url)
                    try:
                        with open(YT_REELS_FILE, "w", encoding="utf-8") as f:
                            f.write("\n".join(urls) + "\n")
                    except Exception as ef:
                        print(f"Notice updating reels file: {ef}")
            else:
                print(f"⚠️ Temporary network error with {candidate_url}. Keeping in queue and trying another candidate reel...")
            time.sleep(2)

    if not chosen_url:
        print("Error: Failed to download a valid reel after trying multiple candidate URLs. Exiting.")
        sys.exit(1)

    # Check current cycle:
    # Cycle 1 (First 2000+ original reels): Post pristine original video without any changes!
    # Cycle 2+ (When URLs run out and reload from backup): Automatically apply smart fingerprint & transformations!
    curr_cycle = get_current_cycle()
    if curr_cycle > 1:
        print(f"🔄 Loop Cycle {curr_cycle} Active: Applying Smart Video Fingerprint & Variations for YouTube...")
        upload_video_path = apply_smart_video_fingerprint(TEMP_VIDEO, TEMP_ENHANCED)
    else:
        print("✨ Cycle 1 (Original Run): Uploading pristine original voice reel without modifications.")
        upload_video_path = TEMP_VIDEO

    # 2. Extract crystal-clear frame & generate rich AI metadata
    title, description, tags = generate_youtube_metadata_from_video(upload_video_path)
    print("=" * 60)
    print(f"Generated Title: {title}")
    print("=" * 60)
    print("Generated Description Preview:")
    print(description[:300] + "...\n[Links & Tags included]")
    print("=" * 60)

    try:
        video_id = upload_short_to_youtube(upload_video_path, title, description, tags)
        mark_url_as_used(chosen_url)
        print(f"YouTube Short workflow completed successfully! ID: {video_id}")
    finally:
        for temp_f in [TEMP_VIDEO, TEMP_ENHANCED, TEMP_FRAME]:
            if os.path.exists(temp_f):
                try:
                    os.remove(temp_f)
                except:
                    pass

if __name__ == "__main__":
    main()
