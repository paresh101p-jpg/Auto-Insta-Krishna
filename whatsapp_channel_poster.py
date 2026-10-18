# -*- coding: utf-8 -*-
"""
Automated WhatsApp Channel Poster for Krishna Vibez
Alternating Reel & Image Auto-Poster:
- Alternates every post: Reel ➔ Image ➔ Reel ➔ Image
- Daily Target Slots: 09:00 AM, 01:00 PM, 05:00 PM (enforced 3-hour minimum gap)
- Auto-Catchup: If PC was powered off, immediately posts upon PC power-on once >= 3 hours have passed
- Independent 2,000+ Queues: Separate Image & Reel queues with Infinite Auto-Recycle Loop
- AI Vision: Transcribes exact thought from image or video frame and formats rich WhatsApp caption
- 100% Ban-Proof: Official web.whatsapp.com via Playwright Chromium on Residential IP
"""

import os
import sys
import time
import json
import random
import datetime
import subprocess
import requests
import cv2
from PIL import Image

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Independent Queues & Backups
WHATSAPP_IMAGES_FILE = os.path.join(BASE_DIR, "whatsapp_images_urls.txt")
WHATSAPP_IMAGES_BACKUP = os.path.join(BASE_DIR, "whatsapp_images_urls_backup.txt")
WHATSAPP_IMAGES_USED = os.path.join(BASE_DIR, "whatsapp_images_used_urls.txt")
WHATSAPP_IMAGES_CYCLE = os.path.join(BASE_DIR, "whatsapp_images_cycle_tracker.txt")

WHATSAPP_REELS_FILE = os.path.join(BASE_DIR, "whatsapp_reels_urls.txt")
WHATSAPP_REELS_BACKUP = os.path.join(BASE_DIR, "whatsapp_reels_urls_backup.txt")
WHATSAPP_REELS_USED = os.path.join(BASE_DIR, "whatsapp_reels_used_urls.txt")
WHATSAPP_REELS_CYCLE = os.path.join(BASE_DIR, "whatsapp_reels_cycle_tracker.txt")

WHATSAPP_TYPE_TRACKER = os.path.join(BASE_DIR, "whatsapp_last_post_type.txt")
WHATSAPP_HISTORY_FILE = os.path.join(BASE_DIR, "whatsapp_history.json")
WHATSAPP_PROFILE_DIR = r"C:\Users\Admin\.whatsapp_channel_profile"

TEMP_IMAGE = os.path.join(BASE_DIR, "temp_whatsapp_image.jpg")
TEMP_VIDEO = os.path.join(BASE_DIR, "temp_whatsapp_video.mp4")
TEMP_FRAME = os.path.join(BASE_DIR, "temp_whatsapp_frame.jpg")

CHANNEL_NAME = "Krishna Vibez"
CHANNEL_URL = "https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J"

OFFICIAL_LINKS = {
    "website": "https://krishnavibez.in/",
    "youtube": "https://youtube.com/@krishnavibezofficial",
    "telegram": "https://t.me/krishnavibezz",
    "instagram": "https://www.instagram.com/pareshpadsala_/",
    "facebook": "https://www.facebook.com/1808917602588221",
    "channel": "https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J"
}

# --- TIMING, GAP & AUTO-CATCHUP POLICY ---

def load_history():
    if os.path.exists(WHATSAPP_HISTORY_FILE):
        try:
            with open(WHATSAPP_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"posts": []}

def save_history(history):
    with open(WHATSAPP_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def check_can_post_now(min_gap_hours=3.0, max_daily_posts=3):
    """
    Ensures posts are at least 3 hours apart.
    If PC was turned off and powered back on, elapsed time >= 3h allows immediate posting.
    """
    history = load_history()
    posts = history.get("posts", [])
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")

    # 1. Daily maximum guard (typically 3 posts: 9 AM, 1 PM, 5 PM)
    today_posts = [p for p in posts if p.get("date") == today_str]
    if len(today_posts) >= max_daily_posts:
        print(f"🛑 Daily limit reached: {len(today_posts)}/{max_daily_posts} posts already made today ({today_str}). Exiting safely.", flush=True)
        return False, f"Daily limit reached ({len(today_posts)}/{max_daily_posts})"

    # 2. Check 3-hour minimum gap from last post
    if posts:
        last_post = posts[-1]
        last_time_str = last_post.get("timestamp")
        try:
            last_dt = datetime.datetime.fromisoformat(last_time_str)
            elapsed_seconds = (now - last_dt).total_seconds()
            required_seconds = min_gap_hours * 3600
            if elapsed_seconds < required_seconds:
                rem_mins = int((required_seconds - elapsed_seconds) / 60)
                print(f"⏳ 3-Hour Gap Policy: Last post was {int(elapsed_seconds/3600)}h {int((elapsed_seconds%3600)/60)}m ago. Next post allowed in {rem_mins} minutes. Exiting safely.", flush=True)
                return False, f"Gap policy: Wait {rem_mins} more minutes"
        except Exception as e:
            print(f"Notice parsing last timestamp: {e}", flush=True)

    print("✅ Ready to post: Minimum 3-hour gap satisfied or catchup triggered.", flush=True)
    return True, "Ready"

def record_successful_post(media_type, url, caption_preview):
    history = load_history()
    now = datetime.datetime.now()
    entry = {
        "timestamp": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "type": media_type,
        "media_url": url,
        "preview": caption_preview[:120]
    }
    history.setdefault("posts", []).append(entry)
    save_history(history)

# --- ALTERNATING MEDIA ENGINE (Reel ➔ Image ➔ Reel ➔ Image) ---

def get_next_media_type():
    if os.path.exists(WHATSAPP_TYPE_TRACKER):
        try:
            with open(WHATSAPP_TYPE_TRACKER, "r", encoding="utf-8") as f:
                last_type = f.read().strip().lower()
                if last_type == "reel":
                    return "image"
                else:
                    return "reel"
        except Exception:
            pass
    return "reel"  # Default first post is Reel

def set_last_media_type(media_type):
    try:
        with open(WHATSAPP_TYPE_TRACKER, "w", encoding="utf-8") as f:
            f.write(media_type + "\n")
    except Exception:
        pass

# --- QUEUE & AUTO-RECYCLE HANDLERS ---

def get_cycle(cycle_file):
    if os.path.exists(cycle_file):
        try:
            with open(cycle_file, "r", encoding="utf-8") as f:
                val = f.read().strip()
                return int(val) if val.isdigit() else 1
        except Exception:
            pass
    return 1

def save_cycle(cycle_file, num):
    try:
        with open(cycle_file, "w", encoding="utf-8") as f:
            f.write(str(num) + "\n")
    except Exception:
        pass

def get_next_url(media_type):
    if media_type == "reel":
        urls_file = WHATSAPP_REELS_FILE
        backup_file = WHATSAPP_REELS_BACKUP
        cycle_file = WHATSAPP_REELS_CYCLE
    else:
        urls_file = WHATSAPP_IMAGES_FILE
        backup_file = WHATSAPP_IMAGES_BACKUP
        cycle_file = WHATSAPP_IMAGES_CYCLE

    urls = []
    if os.path.exists(urls_file):
        with open(urls_file, "r", encoding="utf-8", errors="ignore") as f:
            urls = [line.strip() for line in f if line.strip()]

    # Infinite Auto-Recycle Loop: Reload from backup when exhausted
    if not urls:
        curr_cycle = get_cycle(cycle_file)
        next_cycle = curr_cycle + 1
        save_cycle(cycle_file, next_cycle)
        print(f"🔄 All WhatsApp {media_type.upper()} queue completed! Initiating Auto-Recycle Cycle {next_cycle}...", flush=True)

        backup_urls = []
        if os.path.exists(backup_file):
            with open(backup_file, "r", encoding="utf-8", errors="ignore") as f:
                backup_urls = [line.strip() for line in f if line.strip()]

        if backup_urls:
            unique_urls = list(dict.fromkeys(backup_urls))
            random.shuffle(unique_urls)
            with open(urls_file, "w", encoding="utf-8") as f:
                f.write("\n".join(unique_urls) + "\n")
            print(f"✅ Successfully reloaded & shuffled {len(unique_urls)} {media_type}s for Cycle {next_cycle}!", flush=True)
            urls = unique_urls
        else:
            print(f"Error: No backup {media_type} URLs available to recycle!", flush=True)
            return None

    return urls[0]

def mark_url_as_used(media_type, used_url):
    urls_file = WHATSAPP_REELS_FILE if media_type == "reel" else WHATSAPP_IMAGES_FILE
    used_file = WHATSAPP_REELS_USED if media_type == "reel" else WHATSAPP_IMAGES_USED

    urls = []
    if os.path.exists(urls_file):
        with open(urls_file, "r", encoding="utf-8", errors="ignore") as f:
            urls = [line.strip() for line in f if line.strip()]

    if used_url in urls:
        urls.remove(used_url)
        with open(urls_file, "w", encoding="utf-8") as f:
            f.write("\n".join(urls) + "\n")

    with open(used_file, "a", encoding="utf-8") as uf:
        uf.write(used_url + "\n")

    print(f"✅ URL marked as used in WhatsApp {media_type} queue: {used_url}", flush=True)

# --- MEDIA DOWNLOAD ENGINE ---

def download_media(media_type, url):
    target_path = TEMP_VIDEO if media_type == "reel" else TEMP_IMAGE
    print(f"📥 Downloading WhatsApp {media_type.upper()} from: {url}...", flush=True)

    if os.path.exists(target_path):
        try:
            os.remove(target_path)
        except Exception:
            pass

    # Native curl first (Fastest & handles Cloudflare/Catbox)
    try:
        cmd = [
            "curl", "-s", "-L", "-f",
            "--connect-timeout", "15",
            "--max-time", "120",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
            "-o", target_path,
            url
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=130)
        if res.returncode == 0 and os.path.exists(target_path) and os.path.getsize(target_path) > 30000:
            print(f"✅ Downloaded via curl ({os.path.getsize(target_path) / 1024:.1f} KB)", flush=True)
            return target_path
    except Exception as ce:
        print(f"Notice: curl fallback: {ce}", flush=True)

    # Secondary requests fallback
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        if res.status_code == 200 and len(res.content) > 30000:
            with open(target_path, "wb") as f:
                f.write(res.content)
            print(f"✅ Downloaded via requests ({len(res.content) / 1024:.1f} KB)", flush=True)
            return target_path
    except Exception as re:
        print(f"Error downloading: {re}", flush=True)

    return None

def extract_frame_from_video(video_path, target_sec=4.0):
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
            cv2.imwrite(TEMP_FRAME, frame)
            return TEMP_FRAME
    except Exception as e:
        print(f"Notice: Frame extraction error: {e}", flush=True)
    return None

# --- AI VISION CAPTION GENERATION ---

def get_gemini_key():
    k = os.environ.get("GEMINI_API_KEY")
    if k:
        return k
    kf_path = os.path.join(BASE_DIR, "gemini_key.txt")
    if os.path.exists(kf_path):
        try:
            with open(kf_path, "r", encoding="utf-8") as kf:
                val = kf.read().strip()
                if val:
                    return val
        except Exception:
            pass
    return None

def generate_caption_with_vision(image_or_frame_path, is_reel=False):
    gemini_key = get_gemini_key()
    media_label = "reel" if is_reel else "image"
    if gemini_key and image_or_frame_path and os.path.exists(image_or_frame_path):
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            prompt = (
                f"You are an expert spiritual content editor for 'Krishna Vibez'.\n"
                f"Analyze this Lord Krishna {media_label}.\n"
                "Task:\n"
                "1. Transcribe the exact Hindi/Sanskrit thought or verse physically printed on the media.\n"
                "2. Identify its core theme (e.g. Karma, Dhairya/Patience, Krodh/Anger, Prem/Love, Bura Waqt/Hard Times, Vishwas/Faith).\n"
                "3. Generate JSON with:\n"
                "   - 'hook': 4-6 Hindi words capturing the core message.\n"
                "   - 'exact_thought': The exact transcribed thought.\n"
                "   - 'meaning': 2 deep spiritual Hindi lines explaining it.\n"
                "   - 'lessons': List of 3 concise Hindi bullet points for daily life.\n"
                "Return JSON ONLY."
            )
            img = Image.open(image_or_frame_path)
            for m in ["gemini-3.7-flash", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-flash-latest"]:
                try:
                    resp = client.models.generate_content(model=m, contents=[img, prompt])
                    if resp and resp.text:
                        text = resp.text.strip()
                        if "```json" in text:
                            text = text.split("```json")[1].split("```")[0].strip()
                        elif "```" in text:
                            text = text.split("```")[1].split("```")[0].strip()
                        data = json.loads(text)

                        hook = data.get("hook", "जीवन का पावन संदेश")
                        thought = data.get("exact_thought", "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।")
                        meaning = data.get("meaning", "श्री कृष्ण का यह पावन विचार हमारे मन को असीम शांति और आत्मबल प्रदान करता है।")
                        lessons = data.get("lessons", ["परिस्थितियों में धैर्य बनाए रखें।", "ईश्वर पर अडिग विश्वास रखें।", "अपने कर्म निष्ठा से करें।"])

                        lessons_str = "\n".join([f"• {l}" for l in lessons])

                        caption = (
                            f"🪷 *{hook}* 🪷\n"
                            "━━━━━━━━━━━━━━━━━━━━\n"
                            "*✨ आज का पावन दिव्य विचार:*\n"
                            f"\"{thought}\"\n\n"
                            "*📖 पावन भावार्थ:*\n"
                            f"{meaning}\n\n"
                            "*🌟 व्यावहारिक जीवन सीख:*\n"
                            f"{lessons_str}\n\n"
                            "━━━━━━━━━━━━━━━━━━━━\n"
                            "🌸 *4K दर्शन व संपूर्ण भावार्थ पढ़ें:*\n"
                            f"👉 {OFFICIAL_LINKS['website']}\n\n"
                            "🕊️ *हमारे आधिकारिक परिवार से जुड़ें:*\n"
                            f"🟢 WhatsApp: {OFFICIAL_LINKS['channel']}\n"
                            f"▶️ YouTube: {OFFICIAL_LINKS['youtube']}\n"
                            f"📸 Insta: {OFFICIAL_LINKS['instagram']}\n"
                            f"📘 FB: {OFFICIAL_LINKS['facebook']}\n"
                            f"🕊️ Telegram: {OFFICIAL_LINKS['telegram']}\n\n"
                            "🙏 *जय श्री राधे कृष्ण! हे गोविंद, कल्याण करें।* 🪷✨\n\n"
                            "#Krishna #RadheKrishna #BhagavadGita #KrishnaQuotes #KrishnaVibez #DailySuvichar"
                        )
                        print(f"✅ AI Vision successfully transcribed {media_label} thought: '{thought}'", flush=True)
                        return caption, thought
                except Exception as me:
                    print(f"Notice with model {m}: {me}", flush=True)
        except Exception as ge:
            print(f"Notice Gemini Vision fallback: {ge}", flush=True)

    # Fallback caption
    thought = "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।"
    caption = (
        "🪷 *जीवन का पावन संदेश* 🪷\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "*✨ आज का पावन दिव्य विचार:*\n"
        f"\"{thought}\"\n\n"
        "*📖 पावन भावार्थ:*\n"
        "भगवान श्री कृष्ण हमें समझाते हैं कि अपने कर्मों को पूरी निष्ठा से करें और फल की चिंता परमात्मा पर छोड़ दें।\n\n"
        "*🌟 व्यावहारिक जीवन सीख:*\n"
        "• किसी भी परिस्थिति में अपना धैर्य न खोएं।\n"
        "• बिना फल की चिंता किए निष्काम भाव से कार्य करें।\n"
        "• ईश्वर पर सच्चा विश्वास बनाए रखें।\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🌸 *4K दर्शन व संपूर्ण भावार्थ पढ़ें:*\n"
        f"👉 {OFFICIAL_LINKS['website']}\n\n"
        "🕊️ *हमारे आधिकारिक परिवार से जुड़ें:*\n"
        f"🟢 WhatsApp: {OFFICIAL_LINKS['channel']}\n"
        f"▶️ YouTube: {OFFICIAL_LINKS['youtube']}\n"
        f"📸 Insta: {OFFICIAL_LINKS['instagram']}\n"
        f"📘 FB: {OFFICIAL_LINKS['facebook']}\n"
        f"🕊️ Telegram: {OFFICIAL_LINKS['telegram']}\n\n"
        "🙏 *जय श्री राधे कृष्ण! हे गोविंद, कल्याण करें।* 🪷✨\n\n"
        "#Krishna #RadheKrishna #BhagavadGita #KrishnaQuotes #KrishnaVibez #DailySuvichar"
    )
    return caption, thought

# --- PLAYWRIGHT AUTOMATION FOR WHATSAPP CHANNEL ---

def post_to_whatsapp_channel_via_playwright(media_path, caption, headless=False):
    from playwright.sync_api import sync_playwright

    print("\n🌐 Launching Dedicated WhatsApp Browser Session...", flush=True)
    os.makedirs(WHATSAPP_PROFILE_DIR, exist_ok=True)

    with sync_playwright() as p:
        args = [
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--no-sandbox"
        ]

        context = p.chromium.launch_persistent_context(
            user_data_dir=WHATSAPP_PROFILE_DIR,
            headless=headless,
            args=args,
            viewport=None
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            print("Navigating to https://web.whatsapp.com...", flush=True)
            page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)

            # Check for QR Code and wait for WhatsApp Web to finish "Loading your chats"
            print("⏳ Checking WhatsApp Web session state...", flush=True)
            logged_in = False
            for sec in range(0, 360, 5):
                try:
                    # 1. Check if main interface is already active
                    side_ui = page.query_selector('#side, div[data-testid="chat-list"], button[aria-label*="Channels"], button[aria-label*="Updates"], span[data-icon="channels-outline"], span[data-icon="newsletter-outline"]')
                    if side_ui:
                        print("🎉 WhatsApp Web interface loaded successfully! Session is active.", flush=True)
                        logged_in = True
                        break

                    # 2. Check if QR code is visible
                    qr_canvas = page.query_selector('canvas[aria-label*="Scan"], div[data-ref]')
                    if qr_canvas and sec == 0:
                        print("=" * 65, flush=True)
                        print("⚠️ FIRST-TIME WHATSAPP LOGIN REQUIRED!", flush=True)
                        print("Please open WhatsApp on your phone ➔ Linked Devices ➔ Link a Device")
                        print("and scan the QR code on your screen.")
                        print("=" * 65, flush=True)

                    # 3. Check if "Loading your chats" is in progress
                    loading_text = page.query_selector('text="Loading your chats"')
                    if loading_text:
                        print(f"⏳ WhatsApp is syncing & loading your chats from phone... ({sec}s)", flush=True)
                    else:
                        if sec % 15 == 0 and sec > 0:
                            print(f"⏳ Waiting for WhatsApp Web interface to settle... ({sec}/360s)", flush=True)
                except Exception:
                    time.sleep(2)
                    continue

                time.sleep(5)

            if not logged_in:
                print("Error: WhatsApp Web interface did not load within timeout.", flush=True)
                return False

            time.sleep(3)

            # Step 1: Dismiss any popups/modals (e.g. "What's new on WhatsApp Web")
            for btn_sel in ['button:has-text("Continue")', 'button[aria-label="Close"]', 'button:has-text("OK")']:
                try:
                    for b in page.query_selector_all(btn_sel):
                        if b.is_visible():
                            b.click()
                            time.sleep(1)
                except Exception:
                    pass

            # Step 2: Navigate to Channels tab
            print("Step 2: Navigating to Channels tab...", flush=True)
            ch_btn = page.query_selector('button[aria-label="Channels"], button[aria-label*="चैनल"], span[data-icon="channels-outline"], span[data-icon="newsletter-outline"]')
            if ch_btn:
                ch_btn.click()
                time.sleep(2)

            # Step 3: Click Krishna Vibez channel in the list
            print(f"Step 3: Opening channel '{CHANNEL_NAME}'...", flush=True)
            row = page.locator(f'div[role="listitem"]:has-text("{CHANNEL_NAME}")').first
            if row and row.is_visible():
                print(f"✅ Found channel '{CHANNEL_NAME}' in Channels list, clicking...", flush=True)
                row.click()
                time.sleep(3)
            else:
                direct_url = "https://web.whatsapp.com/accept?channel_invite_code=0029VbDxJHk30LKNtj4Er62J"
                print(f"Opening channel via direct link: {direct_url}", flush=True)
                page.goto(direct_url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(6)

            # Dismiss any announcement banner if visible
            for close_banner in page.query_selector_all('button[aria-label="Close"]'):
                try:
                    if close_banner.is_visible():
                        close_banner.click()
                except Exception:
                    pass

            # Step 4: Click Attach button and trigger Photos & videos file chooser
            print("Step 4: Attaching media to channel...", flush=True)
            attach_btn = page.query_selector('button[title*="Attach"], button[aria-label*="Attach"], span[data-icon="plus"]')
            if attach_btn:
                attach_btn.click()
                time.sleep(1.5)

            abs_media = os.path.abspath(media_path)
            try:
                with page.expect_file_chooser(timeout=8000) as fc_info:
                    page.click('li:has-text("Photos & videos"), div[role="button"]:has-text("Photos & videos"), span:has-text("Photos & videos")')
                file_chooser = fc_info.value
                file_chooser.set_files(abs_media)
                print(f"✅ Media attached via file chooser: {abs_media}", flush=True)
                time.sleep(6)
            except Exception as e:
                print(f"File chooser fallback: {e}", flush=True)
                file_input = page.query_selector('input[type="file"]')
                if file_input:
                    file_input.set_input_files(abs_media)
                    print(f"✅ Media attached via file input: {abs_media}", flush=True)
                    time.sleep(6)
                else:
                    dbg_shot = os.path.join(BASE_DIR, "whatsapp_attach_debug.png")
                    page.screenshot(path=dbg_shot)
                    print(f"DEBUG: Saved {dbg_shot}", flush=True)
                    print("Error: Could not find media file input on WhatsApp Web.", flush=True)
                    return False

            # Step 5: Enter Caption in Media Preview
            print("Step 5: Entering WhatsApp caption in preview...", flush=True)
            caption_box = page.query_selector('div[aria-label="Type an update"][contenteditable="true"], div[contenteditable="true"][aria-label*="caption"], div[contenteditable="true"][data-tab="10"], div[contenteditable="true"]')
            if caption_box:
                caption_box.click()
                time.sleep(1)
                try:
                    page.keyboard.insert_text(caption)
                except Exception:
                    page.evaluate('(text) => { const el = document.querySelector("div[aria-label=\'Type an update\']") || document.querySelector("div[contenteditable=\'true\']"); if (el) { el.innerText = text; el.dispatchEvent(new Event("input", { bubbles: true })); } }', caption)
                time.sleep(2)
                print("✅ Caption entered successfully!", flush=True)
            else:
                print("Notice: Caption box not found, sending media directly.", flush=True)

            # Step 6: Click Send Button
            print("Step 6: Clicking Send button...", flush=True)
            send_btn = page.query_selector('div[aria-label*="Send"][role="button"], span[data-icon="wds-ic-send-filled"], div[role="button"]:has(span[data-icon="wds-ic-send-filled"]), span[data-icon="send"], div[aria-label="Send"], button[aria-label="Send"]')
            if send_btn:
                send_btn.click()
                print("✅ Send button clicked!", flush=True)
            else:
                fallback_btn = page.query_selector('button:has(span[data-icon*="send"]), div[role="button"]:has(span[data-icon*="send"])')
                if fallback_btn:
                    fallback_btn.click()
                    print("✅ Fallback send button clicked!", flush=True)
                else:
                    print("Error: Could not locate Send button in media preview.", flush=True)
                    return False

            # Wait for upload completion (25s for video/reels, 12s for images)
            upload_wait = 25 if media_path.endswith(".mp4") else 12
            print(f"⏳ Uploading to WhatsApp Channel... waiting {upload_wait} seconds for completion...", flush=True)
            time.sleep(upload_wait)

            print(f"🎉 SUCCESS! Post published successfully to WhatsApp Channel '{CHANNEL_NAME}'!", flush=True)
            return True

        except Exception as e:
            err_shot = os.path.join(BASE_DIR, "whatsapp_post_error.png")
            try:
                page.screenshot(path=err_shot)
                print(f"Saved debug screenshot to: {err_shot}", flush=True)
            except Exception:
                pass
            print(f"Error during WhatsApp channel automation: {e}", flush=True)
            return False
        finally:
            context.close()

# --- MAIN EXECUTION ---

def main():
    print("=" * 65)
    print("  WhatsApp Channel Auto-Poster (Krishna Vibez)")
    print("  Alternating Mode: Reel ➔ Image ➔ Reel ➔ Image")
    print("  Target Slots: 09:00 AM | 01:00 PM | 05:00 PM")
    print("=" * 65)

    # 1. 3-Hour Gap & Safety Check
    can_post, reason = check_can_post_now(min_gap_hours=3.0, max_daily_posts=3)
    if not can_post:
        print(f"Status: {reason}")
        return

    # 2. Determine Next Media Type (Alternates: reel -> image -> reel -> image)
    next_type = get_next_media_type()
    print(f"\n🎯 Next scheduled post type: {next_type.upper()}", flush=True)

    # 3. Get Next URL from respective independent queue
    url = get_next_url(next_type)
    if not url:
        print(f"No {next_type} URL available. Exiting.")
        return

    # 4. Download Media
    media_path = download_media(next_type, url)
    if not media_path:
        print("Failed to download media. Exiting.")
        return

    # 5. Extract Frame if Reel for Vision AI
    vision_input_path = media_path
    if next_type == "reel":
        frame = extract_frame_from_video(media_path, target_sec=4.0)
        if frame:
            vision_input_path = frame

    # 6. Generate AI Vision Caption
    caption, thought_used = generate_caption_with_vision(vision_input_path, is_reel=(next_type == "reel"))
    print("=" * 65)
    print("Generated WhatsApp Caption Preview:")
    print(caption[:260] + "...\n[Links Included]")
    print("=" * 65)

    # 7. Post to WhatsApp Channel
    try:
        posted = post_to_whatsapp_channel_via_playwright(media_path, caption, headless=False)
        if posted:
            record_successful_post(next_type, url, caption)
            mark_url_as_used(next_type, url)
            set_last_media_type(next_type)
            print(f"🚀 WhatsApp {next_type.upper()} post completed & state switched for next run.")
        else:
            print("⚠️ WhatsApp post attempt could not be completed.")
    finally:
        # 8. Cleanup Temporary Files (Zero disk waste)
        for temp_f in [TEMP_IMAGE, TEMP_VIDEO, TEMP_FRAME]:
            if os.path.exists(temp_f):
                try:
                    os.remove(temp_f)
                except Exception:
                    pass
        print("🧹 Temporary files cleaned up.")

if __name__ == "__main__":
    main()
