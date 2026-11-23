#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — FULL SONG AUTO PIPELINE (गिटहब पर 100% ऑटोमैटिक)
=============================================================================
1. स्कैन करता है 'Songs/inbox/' में नए गाने
2. गाने के लिए मैचिंग थंबनेल ('song_thumbnails/') और वीडियो इमेज ('song_images/') खोजता है
3. गाने को साफ करके Catbox.moe पर अपलोड करता है
4. 1080p एनिमेटेड म्यूजिक वीडियो बनाता है (Ken Burns, 3 विशिष्ट फ्लोरा पार्टिकल्स, गोल्डन स्पार्कल्स, लोगो)
5. यूट्यूब पर अनलिस्टेड (Unlisted) स्टेटस में अपलोड करता है
6. वीडियो पर यूज़र द्वारा दिया गया थंबनेल सेट करता है
7. हर रविवार सुबह 9 AM IST पर शेड्यूल से, या कभी भी मैन्युअल रन से चलता है
=============================================================================
"""

import os
import sys
import json
import time
import re
import shutil
import subprocess
import random
import urllib.request
from datetime import datetime, timezone, timedelta

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- फोल्डर ---
SONGS_DIR = os.path.join(BASE_DIR, "Songs")
SONGS_INBOX = os.path.join(SONGS_DIR, "inbox")
SONGS_UPLOADED = os.path.join(SONGS_DIR, "uploaded")
SONG_THUMB_DIR = os.path.join(BASE_DIR, "song_thumbnails")
SONG_IMAGES_DIR = os.path.join(BASE_DIR, "song_images")
ANIMATIONS_DIR = os.path.join(BASE_DIR, "extracted_petals")

# --- डेटा फाइलें ---
SONG_URLS_FILE = os.path.join(BASE_DIR, "song_urls.txt")
SONG_BACKUP_URLS_FILE = os.path.join(BASE_DIR, "song_urls_backup.txt")
SONG_USED_URLS_FILE = os.path.join(BASE_DIR, "song_used_urls.txt")
SONG_REGISTRY_FILE = os.path.join(BASE_DIR, "song_tracks_registry.json")
SONG_TRACKER_FILE = os.path.join(SONGS_DIR, "song_uploaded_tracker.txt")
SONG_DAILY_TRACKER = os.path.join(BASE_DIR, "song_daily_tracker.json")

# --- टेम्प फाइलें ---
TEMP_AUDIO = os.path.join(BASE_DIR, "temp_song_audio.mp3")
TEMP_VIDEO = os.path.join(BASE_DIR, "temp_song_video.mp4")

SUPPORTED_EXTS = (".wav", ".mp3", ".ogg", ".flac", ".m4a")
IMAGE_EXTS = (".jpg", ".jpeg", ".png")

os.makedirs(SONGS_INBOX, exist_ok=True)
os.makedirs(SONGS_UPLOADED, exist_ok=True)
os.makedirs(SONG_THUMB_DIR, exist_ok=True)
os.makedirs(SONG_IMAGES_DIR, exist_ok=True)

FFMPEG_EXE = "ffmpeg"
local_ffmpeg = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if sys.platform == "win32" and os.path.exists(local_ffmpeg):
    FFMPEG_EXE = local_ffmpeg


def run_cmd(cmd, timeout=300):
    try:
        res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, timeout=timeout)
        return res.returncode == 0, res.stderr
    except Exception as e:
        return False, str(e)


def download_file(url, out_path):
    """Catbox या वेब URL से फाइल डाउनलोड करना"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            with open(out_path, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
        return os.path.exists(out_path) and os.path.getsize(out_path) > 1000
    except Exception as e:
        print(f"  ⚠️ डाउनलोड त्रुटि ({url}): {e}")
        return False


def upload_to_catbox(file_path, retries=3):
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
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True, timeout=90)
            url = res.stdout.strip()
            if url.startswith("https://files.catbox.moe/"):
                return url
        except Exception:
            pass
        time.sleep(2)
    return None


def clean_audio(input_path, output_path):
    """ऑडियो को साफ करना, साइलेंस हटाना व 192k MP3 में बदलना"""
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", input_path,
        "-af", "silenceremove=start_periods=1:start_duration=0.5:start_threshold=-50dB:detection=peak,"
               "silenceremove=stop_periods=1:stop_duration=1.0:stop_threshold=-50dB:detection=peak,"
               "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "libmp3lame", "-b:a", "192k",
        "-ar", "44100",
        output_path
    ]
    success, _ = run_cmd(cmd, timeout=180)
    return success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000


def load_registry():
    if os.path.exists(SONG_REGISTRY_FILE):
        try:
            with open(SONG_REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_registry(reg):
    with open(SONG_REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)


def load_urls(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def save_urls(filepath, urls):
    with open(filepath, "w", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")


def find_thumbnail(song_name, song_info=None):
    """गाने के लिए सही थंबनेल खोजना (रजिस्ट्री, लोकल फोल्डर या कैटबॉक्स डाउनलोड)"""
    found = None
    # 1. यदि रजिस्ट्री में thumb_url मौजूद है
    if song_info and song_info.get("thumb_url"):
        thumb_url = song_info["thumb_url"]
        local_thumb = os.path.join(SONG_THUMB_DIR, f"{song_name}.jpg")
        if os.path.exists(local_thumb) and os.path.getsize(local_thumb) > 5000:
            found = local_thumb
        elif download_file(thumb_url, local_thumb):
            print(f"  🖼️ थंबनेल CDN से डाउनलोड किया: {local_thumb}")
            found = local_thumb

    # 2. लोकल song_thumbnails फोल्डर में खोजें
    if not found:
        safe = re.sub(r'[<>:"/\\|?*]', '_', song_name).strip('_')
        for ext in IMAGE_EXTS:
            candidates = [
                os.path.join(SONG_THUMB_DIR, f"{song_name}{ext}"),
                os.path.join(SONG_THUMB_DIR, f"{safe}{ext}"),
            ]
            for c in candidates:
                if os.path.exists(c) and os.path.getsize(c) > 5000:
                    found = c
                    break
            if found:
                break

    # 3. यदि कोई भी थंबनेल फाइल मौजूद है
    if not found and os.path.exists(SONG_THUMB_DIR):
        for f in os.listdir(SONG_THUMB_DIR):
            if f.lower().endswith(IMAGE_EXTS):
                fp = os.path.join(SONG_THUMB_DIR, f)
                if os.path.getsize(fp) > 5000:
                    found = fp
                    break

    if found:
        # थंबनेल से फ्लो का वाटरमार्क हटाएं बिना क्रॉप किए (Telea Inpaint)
        try:
            from song_video_generator import clean_and_save_thumbnail
            cleaned_thumb = os.path.join(BASE_DIR, "temp_cleaned_thumbnail.jpg")
            clean_and_save_thumbnail(found, cleaned_thumb)
            if os.path.exists(cleaned_thumb) and os.path.getsize(cleaned_thumb) > 5000:
                return cleaned_thumb
        except Exception as e:
            print(f"  ⚠️ थंबनेल क्लीनिंग सूचना: {e}")
        return found

    return None


def find_slide_images(song_name, song_info=None):
    """वीडियो में दिखाने के लिए यूज़र द्वारा दी गई इमेज(स्लाइड्स) खोजना"""
    slides = []

    # 1. यदि रजिस्ट्री में image_urls हैं, उन्हें डाउनलोड करें
    if song_info and song_info.get("image_urls"):
        for idx, url in enumerate(song_info["image_urls"]):
            slide_path = os.path.join(SONG_IMAGES_DIR, f"{song_name}_slide{idx+1}.jpg")
            if os.path.exists(slide_path) and os.path.getsize(slide_path) > 5000:
                slides.append(slide_path)
            elif download_file(url, slide_path):
                slides.append(slide_path)

    if slides:
        return slides

    # 2. लोकल song_images/ फोल्डर में खोजें
    if os.path.exists(SONG_IMAGES_DIR):
        for f in sorted(os.listdir(SONG_IMAGES_DIR)):
            if f.lower().endswith(IMAGE_EXTS):
                fp = os.path.join(SONG_IMAGES_DIR, f)
                if os.path.getsize(fp) > 5000:
                    slides.append(fp)

    if slides:
        return slides

    # 3. यदि कोई अलग स्लाइड इमेज नहीं है, तो थंबनेल को ही मुख्य दृश्य के रूप में यूज़ करें
    thumb = find_thumbnail(song_name, song_info)
    if thumb:
        return [thumb]

    return []


def generate_metadata(song_name, song_info, audio_file=None):
    """
    ऑडियो को सुनकर और उसके भाव/मूड को पहचानकर AI (Gemini) द्वारा
    आकर्षक टाइटल (Clickable Hook Title), विस्तृत भक्तिपूर्ण डिस्क्रिप्शन (Chapters, Benefits, Social Links)
    और ट्रेंडिंग YouTube SEO टैग्स जनरेट करना।
    """
    # 1. ऑडियो विश्लेषण (टेम्पो, वॉल्यूम, भाव, अवधि)
    analysis = None
    try:
        from audio_analyzer import analyze_audio_mood
        if audio_file and os.path.exists(audio_file):
            analysis = analyze_audio_mood(audio_file)
    except Exception as e:
        print(f"  ⚠️ ऑडियो विश्लेषण सूचना: {e}")

    mood = song_info.get("mood", "Balanced Bhakti")
    mood_hi = song_info.get("mood_hi", "संतुलित भक्ति संगीत")
    target_hi = song_info.get("target_audience_hi", "भगवान के लिए")
    dur_min = song_info.get("duration_min", 3.0)

    if analysis:
        mood = analysis.get("mood", mood)
        mood_hi = analysis.get("mood_hi", mood_hi)
        dur_min = analysis.get("duration_min", dur_min)
        if analysis.get("target_audience_hi"):
            target_hi = analysis.get("target_audience_hi")

    # 2. जेमिनी AI से टाइटल और डिस्क्रिप्शन जनरेशन
    gemini_key = os.environ.get("GEMINI_API_KEY")
    ai_title = None
    ai_desc_meaning = None
    ai_hook = None
    ai_tags = []

    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)

            prompt = (
                f"You are a master YouTube music producer & SEO strategist for 'Krishna Vibez'.\n"
                f"We are releasing a divine Lord Krishna song & music video on YouTube.\n"
                f"Audio Details:\n"
                f"- Raw Track Hint: '{song_name}'\n"
                f"- Musical Mood: {mood} ({mood_hi})\n"
                f"- Target Audience: {target_hi}\n"
                f"- Track Duration: {dur_min} minutes\n\n"
                f"RULES:\n"
                f"1. DO NOT simply use the raw filename '{song_name}' as the title! Instead, craft a deeply emotional, viral, spiritual YouTube title.\n"
                f"   - Format: [Soulful Hindi Devotional Hook] | [English Meditation / Flute / Kirtan Hook] | Krishna Vibez\n"
                f"   - Keep title under 75 characters total so it doesn't truncate on mobile.\n"
                f"   - Examples: 'मन को मोह लेगी यह बाँसुरी | Vrindavan Flute Meditation | Krishna Vibez' or 'साँवरिया की पावन धुन | Peaceful Krishna Kirtan | Krishna Vibez'\n"
                f"2. Write a captivating, spiritual 2-3 paragraph explanation in pure devotional Hindi & English detailing how listening to this specific melody brings peace, removes stress, purifies the soul, and awakens Krishna bhakti.\n"
                f"3. Provide 15 highly searched devotional YouTube tags.\n\n"
                f"Return JSON strictly with keys:\n"
                f"{{\n"
                f'  "title": "...",\n'
                f'  "spiritual_meaning": "...",\n'
                f'  "tags": ["..."]\n'
                f"}}"
            )

            models_to_try = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-2.0-flash"]
            response = None
            for m in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=prompt
                    )
                    if response and response.text:
                        break
                except Exception as me:
                    print(f"  ⚠️ Gemini model {m} notice: {me}")

            if response and response.text:
                txt = response.text.strip()
                if "```json" in txt:
                    txt = txt.split("```json")[1].split("```")[0].strip()
                elif "```" in txt:
                    txt = txt.split("```")[1].split("```")[0].strip()
                data = json.loads(txt)
                ai_title = data.get("title")
                ai_desc_meaning = data.get("spiritual_meaning")
                ai_tags = data.get("tags", [])
        except Exception as e:
            print(f"  ⚠️ Gemini AI मेटाडेटा निर्माण सूचना: {e}")

    # टाइटल फॉलबैक
    if not ai_title:
        clean_hint = re.sub(r'[-_]', ' ', song_name)
        clean_hint = re.sub(r'\b(Treblo|Official|Audio|Song|Wav|Mp3)\b', '', clean_hint, flags=re.I).strip()
        ai_title = f"{clean_hint} | श्री कृष्ण अमृत बाँसुरी एवं कीर्तन | Krishna Vibez"

    if len(ai_title) > 95:
        ai_title = ai_title[:92] + "..."

    # विस्तृत, भव्य और संपूर्ण यूट्यूब डिस्क्रिप्शन
    meaning_block = ai_desc_meaning if ai_desc_meaning else (
        "भगवान श्री कृष्ण के पावन चरणों में समर्पित यह दिव्य संगीत मन के समस्त तनाव, चिंता और "
        "नकारात्मकता को समाप्त कर अंतरात्मा को असीम शांति, आनंद और सकारात्मक ऊर्जा से भर देता है। "
        "यह मधुर धुन ध्यान (Meditation), पूजा एवं गहरी एकाग्रता के लिए सर्वोत्तम है।"
    )

    description = (
        f"🌸 स्वागत है Krishna Vibez के पावन संगीत संसार में 🌸\n\n"
        f"Experience profound inner peace, deep tranquility, and divine healing with this sacred "
        f"Lord Krishna Devotional & Flute Meditation music video.\n\n"
        f"🌿 आज का पावन प्रसंग: {ai_title}\n"
        f"🎭 संगीत भाव: {mood_hi} ({mood})\n"
        f"👥 समर्पण: {target_hi}\n\n"
        f"📖 पावन भावार्थ (Spiritual Meaning):\n"
        f"{meaning_block}\n\n"
        "✨ पावन संगीत का महत्व (Spiritual Peace & Mind Healing):\n"
        "यह संगीत मन को शांत करने वाली सकारात्मक तरंगों पर आधारित है। यह मधुर धुन मस्तिष्क की अल्फा तरंगों (Alpha Waves) को "
        "सक्रिय करती है, मानसिक तनाव व अनिद्रा को दूर करती है, हृदय स्पंदन को शांत करती है और आत्मिक सुकून प्रदान करती है।\n\n"
        "🧘 इस पावन संगीत के सर्वोत्तम उपयोग (Ideal For):\n"
        "• ध्यान, योग और दैनिक साधना (Deep Meditation, Dhyan & Daily Yoga)\n"
        "• तनाव, चिंता और अधिक सोचने (Overthinking) से मुक्ति (Stress Relief & Mental Peace)\n"
        "• गहरी और सुकून भरी नींद (Deep Sleep & Restorative Rest)\n"
        "• प्रातःकालीन पूजा, आरती और घर में सकारात्मक ऊर्जा (Morning Pooja & Positive Home Vibes)\n"
        "• पढ़ाई और कार्य में एकाग्रता (Deep Study & Work Focus)\n\n"
        "⏱️ समय सारणी (Chapters / Timestamps):\n"
        "00:00 🪷 दिव्य मंगलाचरण एवं बाँसुरी प्रवेश (Divine Awakening)\n"
        "01:00 🪶 वृंदावन अमृत प्रवाह (Sacred Flow)\n"
        "02:00 🌊 आत्मिक शांति और गहन ध्यान (Deep Meditation Flow)\n"
        "02:30 ✨ असीम शांति एवं समापन विश्राम (Closing Shanti & Gratitude)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🕊️ कृष्ण वाइब्स के आध्यात्मिक परिवार से जुड़ें:\n"
        "🌐 आधिकारिक वेबसाइट: https://krishnavibez.in/\n"
        "▶️ आधिकारिक YouTube: https://www.youtube.com/@KrishnaVibezMusic\n"
        "📲 WhatsApp चैनल: https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J\n"
        "📢 Telegram चैनल: https://t.me/krishnavibezz\n"
        "📸 Instagram: https://www.instagram.com/krishnavibez/\n"
        "🧵 Threads: https://www.threads.net/@krishnavibez\n"
        "📘 Facebook पेज: https://www.facebook.com/1808917602588221\n"
        "📌 Pinterest: https://in.pinterest.com/MojiloMart/\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🛍️ Divine Recommendations (Amazon Storefront):\n"
        "👉 Explore our Amazon Store: https://www.amazon.in/shop/myhappybirthday\n"
        "(Disclaimer: Krishna Vibez earns from qualifying purchases at no extra cost to you.)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚖️ आधिकारिक कॉपीराइट एवं संगीत अस्वीकरण (Copyright & Music Disclaimer):\n"
        "• संगीत एवं ऑडियो (Music & Audio): यह संगीत 100% मूल (Original) एवं कृष्ण वाइब्स (Krishna Vibez) द्वारा एक्सक्लूसिव रूप से निर्मित है। All compositions are copyright-safe and owned/mastered by Krishna Vibez.\n"
        "• दृश्य एवं वीडियो (Visuals & Art): सभी 16:9 सिनेमैटिक विजुअल्स एवं कलाकृतियां कृष्ण वाइब्स की मूल संपत्ति हैं।\n"
        "• उद्देश्य (Purpose): यह पावन संगीत केवल मानसिक शांति, ध्यान, योग, तनाव मुक्ति और अनिद्रा से राहत के आध्यात्मिक कल्याण हेतु निर्मित है।\n"
        "• सुरक्षा सूचना (Safety Notice): कृपया वाहन चलाते समय या भारी मशीनरी चलाते समय ध्यान/नींद संगीत न सुनें।\n"
        "• कॉपीराइट सूचना (Copyright Notice): इस चैनल के किसी भी ऑडियो या वीडियो को पुनः अपलोड (re-upload) करना पूर्णतः प्रतिबंधित है। All Rights Reserved © 2026 Krishna Vibez.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🙏 यदि इस संगीत ने आपके मन को शांति और सुकून दिया हो, तो वीडियो को लाइक करें, अपने परिजनों के साथ साझा करें और चैनल को सब्सक्राइब अवश्य करें।\n\n"
        "जय श्री राधे कृष्ण! 🪷✨\n\n"
        "#Krishna #Flute #Bansuri #MeditationMusic #KrishnaMusic #DivineMusic #RadhaKrishna #RelaxingMusic #InnerPeace #DeepSleep #BansuriTabla #KrishnaVibez #DailyMeditation #Bhakti"
    )

    tags = list(dict.fromkeys(ai_tags + [
        "Krishna Vibez", "Krishna Song", "Krishna Flute", "Bansuri Dhun", "Vrindavan Kirtan",
        "Bansuri Se Bula Le", "Krishna Bhajan", "Radhe Krishna", "Bhakti Song",
        "Flute Meditation", "Spiritual Music", "Deep Sleep Music", "Relaxing Music", "Peaceful Instrumental"
    ]))

    return ai_title, description, tags


def process_all_pending_songs():
    """Songs/inbox से नए गाने स्कैन, क्लीन व Catbox पर अपलोड करना"""
    print("\n" + "=" * 60)
    print("  KRISHNA VIBEZ — FULL SONG AUTO PIPELINE (Process Mode)")
    print("=" * 60)

    pending_files = []
    if os.path.exists(SONGS_INBOX):
        for f in os.listdir(SONGS_INBOX):
            if f.lower().endswith(SUPPORTED_EXTS):
                pending_files.append(os.path.join(SONGS_INBOX, f))

    if not pending_files:
        print("[INFO] कोई नया गाना Songs/inbox/ में नहीं मिला। सभी प्रोसेस हैं।")
        return

    reg = load_registry()
    urls = load_urls(SONG_URLS_FILE)

    for song_path in pending_files:
        raw_name = os.path.splitext(os.path.basename(song_path))[0]
        print(f"\n🎧 नया गाना मिला: {raw_name}")

        temp_clean = os.path.join(BASE_DIR, "temp_clean_song.mp3")
        if not clean_audio(song_path, temp_clean):
            print("  ⚠️ ऑडियो क्लीनिंग विफल, मूल फाइल प्रयोग कर रहा हूँ")
            shutil.copy2(song_path, temp_clean)

        print("  ☁️ Catbox पर अपलोड हो रहा है...")
        catbox_url = upload_to_catbox(temp_clean)
        if not catbox_url:
            print("  ❌ Catbox अपलोड विफल, बाद में पुनः प्रयास होगा")
            continue

        print(f"  ✅ Catbox URL: {catbox_url}")

        # थंबनेल जांच व अपलोड
        thumb_path = find_thumbnail(raw_name)
        thumb_url = None
        if thumb_path:
            thumb_url = upload_to_catbox(thumb_path)
            print(f"  🖼️ थंबनेल CDN URL: {thumb_url}")

        # वीडियो स्लाइड्स जांच व अपलोड
        slides = find_slide_images(raw_name)
        slide_urls = []
        for s in slides:
            u = upload_to_catbox(s)
            if u:
                slide_urls.append(u)

        reg[catbox_url] = {
            "name": raw_name,
            "mood": "Balanced Bhakti",
            "mood_hi": "संतुलित भक्ति संगीत",
            "target_audience": "God",
            "target_audience_hi": "भगवान के लिए",
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "thumb_url": thumb_url,
            "image_urls": slide_urls,
            "status": "pending"
        }

        if catbox_url not in urls:
            urls.append(catbox_url)

        # फाइल मूव करें
        dest = os.path.join(SONGS_UPLOADED, os.path.basename(song_path))
        shutil.move(song_path, dest)
        if os.path.exists(temp_clean):
            os.remove(temp_clean)

    save_registry(reg)
    save_urls(SONG_URLS_FILE, urls)
    save_urls(SONG_BACKUP_URLS_FILE, urls)
    print("\n✅ सभी नए गाने सफलतापूर्वक क्यू में जोड़े गए।")


def upload_next_to_youtube():
    """अगला गाना 1080p एनिमेटेड वीडियो बनाकर YouTube पर Unlisted अपलोड करना"""
    print("\n" + "=" * 60)
    print("  KRISHNA VIBEZ — YOUTUBE SONG UPLOADER (Unlisted Mode)")
    print("=" * 60)

    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        print("❌ YouTube क्रेडेंशियल्स उपलब्ध नहीं हैं (CLIENT_ID, SECRET, REFRESH_TOKEN)")
        return False

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube"
        ]
    )
    youtube = build("youtube", "v3", credentials=creds)

    reg = load_registry()
    urls = load_urls(SONG_URLS_FILE)

    # फोर्स यूआरएल चेक (एनवायरनमेंट से)
    force_url = os.environ.get("FORCE_SONG_URL")
    target_url = None

    if force_url and force_url in reg:
        target_url = force_url
    else:
        # पेंडिंग गाना खोजें जिसका स्टेटस uploaded न हो
        for u in urls:
            info = reg.get(u, {})
            if info.get("status") != "uploaded":
                target_url = u
                break

    if not target_url and urls:
        target_url = urls[0]

    fix_id = os.environ.get("FIX_PREV_VIDEO_ID")
    if not target_url and fix_id:
        print(f"[INFO] कोई नया गाना क्यू में नहीं है, लेकिन FIX_PREV_VIDEO_ID={fix_id} दिया गया है।")
        print("  🛠️ पुराने वीडियो का वाटरमार्क-मुक्त थंबनेल और AI मेटाडेटा अपडेट किया जा रहा है...")
        # रजिस्ट्री से अंतिम गाना या डिफ़ॉल्ट गाना लें
        last_url = list(reg.keys())[-1] if reg else "https://files.catbox.moe/752c43.mp3"
        s_info = reg.get(last_url, {
            "name": "Vrindavan Maha Kirtan - Bansuri Se Bula Le - Treblo",
            "mood": "Balanced Bhakti", "mood_hi": "संतुलित भक्ति संगीत",
            "target_audience": "God", "target_audience_hi": "भगवान के लिए"
        })
        s_name = s_info.get("name", "Vrindavan Maha Kirtan - Bansuri Se Bula Le")
        
        # ऑडियो डाउनलोड करके विश्लेषण
        if not os.path.exists(TEMP_AUDIO) and last_url.startswith("http"):
            download_file(last_url, TEMP_AUDIO)

        t_title, t_desc, t_tags = generate_metadata(s_name, s_info, TEMP_AUDIO if os.path.exists(TEMP_AUDIO) else None)
        t_thumb = find_thumbnail(s_name, s_info)

        try:
            youtube.videos().update(
                part="snippet,status",
                body={
                    "id": fix_id,
                    "snippet": {
                        "title": t_title,
                        "description": t_desc,
                        "tags": t_tags,
                        "categoryId": "10",
                        "defaultLanguage": "hi",
                        "defaultAudioLanguage": "hi"
                    },
                    "status": {"privacyStatus": "unlisted"}
                }
            ).execute()
            print(f"  ✅ वीडियो {fix_id} का AI टाइटल और विस्तृत विवरण अपडेट हुआ:\n  📝 {t_title}")
        except Exception as e:
            print(f"  ⚠️ वीडियो अपडेट त्रुटि: {e}")

        if t_thumb and os.path.exists(t_thumb):
            try:
                youtube.thumbnails().set(
                    videoId=fix_id,
                    media_body=MediaFileUpload(t_thumb, mimetype="image/jpeg")
                ).execute()
                print(f"  ✅ वीडियो {fix_id} का वाटरमार्क-मुक्त थंबनेल अपडेट हुआ!")
            except Exception as e:
                print(f"  ⚠️ थंबनेल अपडेट त्रुटि: {e}")
        return True

    if not target_url:
        print("[INFO] क्यू खाली है। अपलोड करने के लिए कोई पेंडिंग गाना नहीं।")
        return False

    song_info = reg.get(target_url, {})
    song_name = song_info.get("name", "Vrindavan Maha Kirtan - Bansuri Se Bula Le - Treblo")
    print(f"\n🎵 यूट्यूब अपलोड प्रारंभ: {song_name}")
    print(f"  🔗 ऑडियो स्रोत: {target_url}")

    # ऑडियो प्राप्त करना (लोकल या डाउनलोड)
    local_audio_cand = os.path.join(SONGS_UPLOADED, f"{song_name}.wav")
    if os.path.exists(local_audio_cand):
        shutil.copy2(local_audio_cand, TEMP_AUDIO)
        print(f"  📁 लोकल ऑडियो प्रयुक्त: {local_audio_cand}")
    else:
        print("  📥 Catbox से ऑडियो डाउनलोड हो रहा है...")
        if not download_file(target_url, TEMP_AUDIO):
            print("❌ ऑडियो डाउनलोड विफल!")
            return False

    # थंबनेल खोजना
    thumb_path = find_thumbnail(song_name, song_info)
    if not thumb_path:
        print("❌ कोई थंबनेल नहीं मिला!")
        return False
    print(f"  🖼️ उपयोग होने वाला थंबनेल: {thumb_path}")

    # वीडियो स्लाइड्स खोजना
    slide_paths = find_slide_images(song_name, song_info)
    if not slide_paths:
        slide_paths = [thumb_path]
    print(f"  🎨 वीडियो स्लाइड्स संख्या: {len(slide_paths)}")

    # 1080p एनिमेटेड वीडियो जनरेशन
    print("\n🎬 1080p एनिमेटेड म्यूजिक वीडियो तैयार हो रहा है (Ken Burns + Flora Particles + Sparkles)...")
    from song_video_generator import generate_song_music_video
    video_ready = generate_song_music_video(TEMP_AUDIO, slide_paths, TEMP_VIDEO)
    if not video_ready:
        print("❌ वीडियो जनरेशन विफल!")
        return False

    # मेटाडेटा जनरेशन (AI द्वारा ऑडियो का भाव समझकर टाइटल व विस्तृत विवरण)
    title, description, tags = generate_metadata(song_name, song_info, TEMP_AUDIO)

    # प्राइवेसी स्टेटस (डिफ़ॉल्ट Unlisted)
    privacy_status = os.environ.get("PRIVACY_STATUS", "unlisted").lower()
    if privacy_status not in ["unlisted", "private", "public"]:
        privacy_status = "unlisted"

    print(f"  🔒 प्राइवेसी स्टेटस: {privacy_status.upper()}")
    print(f"  📝 टाइटल: {title}")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "10",
            "defaultLanguage": "hi",
            "defaultAudioLanguage": "hi"
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
            "license": "youtube"
        }
    }

    media = MediaFileUpload(TEMP_VIDEO, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  ⬆️ अपलोड प्रगति: {int(status.progress() * 100)}%...", flush=True)

    video_id = response.get("id")
    video_url = f"https://youtube.com/watch?v={video_id}"
    print(f"\n🎉 शानदार! नया म्यूजिक वीडियो सफलतापूर्वक अपलोड हुआ!")
    print(f"  🔗 लिंक: {video_url} ({privacy_status.upper()})")

    # कस्टम थंबनेल सेट करना
    print("  🖼️ यूट्यूब पर कस्टम थंबनेल अपलोड किया जा रहा है...")
    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumb_path, mimetype="image/jpeg")
        ).execute()
        print("  ✅ कस्टम थंबनेल सफलतापूर्वक सेट हो गया!")
    except Exception as e:
        print(f"  ⚠️ थंबनेल अपलोड चेतावनी: {e}")

    # पुराने वीडियो (यदि हो) को Unlisted करना व थंबनेल और AI मेटाडेटा अपडेट करना
    fix_id = os.environ.get("FIX_PREV_VIDEO_ID", "jpCARdivrts")
    if fix_id:
        # अगर fix_id वर्तमान वीडियो id ही है, तो भी उसका टाइटल व डिस्क्रिप्शन अपडेट करें
        target_fix_id = fix_id if fix_id != video_id else video_id
        print(f"\n🛠️ वीडियो ({target_fix_id}) को Unlisted, थंबनेल व AI मेटाडेटा से अपडेट किया जा रहा है...")
        try:
            youtube.videos().update(
                part="snippet,status",
                body={
                    "id": target_fix_id,
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": tags,
                        "categoryId": "10",
                        "defaultLanguage": "hi",
                        "defaultAudioLanguage": "hi"
                    },
                    "status": {"privacyStatus": "unlisted"}
                }
            ).execute()
            print(f"  ✅ वीडियो {target_fix_id} का AI टाइटल, विस्तृत विवरण व अनलिस्टेड स्टेटस अपडेट हुआ!")
        except Exception as e:
            print(f"  ⚠️ वीडियो मेटाडेटा अपडेट चेतावनी: {e}")

        try:
            youtube.thumbnails().set(
                videoId=target_fix_id,
                media_body=MediaFileUpload(thumb_path, mimetype="image/jpeg")
            ).execute()
            print(f"  ✅ वीडियो {target_fix_id} का वॉटरमार्क-मुक्त थंबनेल अपडेट किया गया!")
        except Exception as e:
            print(f"  ⚠️ थंबनेल अपडेट चेतावनी: {e}")

    # रजिस्ट्री व ट्रैकर अपडेट करना
    song_info["status"] = "uploaded"
    song_info["youtube_id"] = video_id
    song_info["youtube_url"] = video_url
    song_info["uploaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reg[target_url] = song_info
    save_registry(reg)

    if target_url in urls:
        urls.remove(target_url)
        save_urls(SONG_URLS_FILE, urls)

    with open(SONG_USED_URLS_FILE, "a", encoding="utf-8") as uf:
        uf.write(target_url + "\n")

    with open(SONG_TRACKER_FILE, "a", encoding="utf-8") as tf:
        tf.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {song_name} | {video_url} | {privacy_status}\n")

    # क्लीनअप
    for f in [TEMP_AUDIO, TEMP_VIDEO]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

    return True


def git_commit_push(msg):
    try:
        subprocess.run(["git", "config", "user.email", "actions@github.com"], check=False)
        subprocess.run(["git", "config", "user.name", "Krishna Vibez Bot"], check=False)
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=False)
        diff = subprocess.run(["git", "diff", "--staged", "--quiet"], cwd=BASE_DIR)
        if diff.returncode == 0:
            print("ℹ️ कोई नया बदलाव कमिट करने के लिए नहीं है।")
            return
        subprocess.run(["git", "commit", "-m", msg], cwd=BASE_DIR, check=False)
        for _ in range(3):
            subprocess.run(["git", "pull", "--rebase", "origin", "master"], cwd=BASE_DIR, check=False)
            res = subprocess.run(["git", "push", "origin", "master"], cwd=BASE_DIR,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                print("✅ गिटहब पुश पूर्ण")
                return
            time.sleep(4)
    except Exception as e:
        print(f"गिट पुश सूचना: {e}")


def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    mode = args[0] if args else "upload"

    if mode == "process":
        process_all_pending_songs()
        git_commit_push("Auto-processed new songs & updated queues [skip ci]")

    elif mode == "upload":
        success = upload_next_to_youtube()
        if success:
            ist_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
            today_str = ist_now.strftime("%Y-%m-%d")
            data = {}
            if os.path.exists(SONG_DAILY_TRACKER):
                try:
                    with open(SONG_DAILY_TRACKER, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    pass
            data["last_upload_date"] = today_str
            data["last_upload_timestamp"] = int(time.time())
            with open(SONG_DAILY_TRACKER, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            git_commit_push("Auto-uploaded 1080p song video to YouTube [skip ci]")


if __name__ == "__main__":
    main()
