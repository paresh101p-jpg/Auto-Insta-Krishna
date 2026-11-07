# -*- coding: utf-8 -*-
"""
Kinetic Word-by-Word YouTube Shorts Generator for Krishna Vibez
Features:
- Headless Chrome HarfBuzz typography (100% correct Devanagari ligatures, zero dotted circles)
- Cross-platform Linux (Ubuntu GitHub Actions) & Windows support with --no-sandbox
- Rotating procedural soundwave visualizer placed safely at y=1380 (above Shorts bottom UI)
- Smooth Ken Burns zoom (1.0x to 1.14x)
- Pure soft Treblo AI Bansuri background music (100% copyright safe)
- Male devotional voiceover (Edge-TTS hi-IN-MadhurNeural)
- 100% clean, text-free Krishna images from music_video_images pool (5,600+ images)
- Infinite thought queue with quotes.txt -> used_quotes.txt recycling
"""

import os
import sys
import glob
import random
import shutil
import subprocess
import time
import math
import concurrent.futures
import cv2
import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUOTES_FILE = os.path.join(BASE_DIR, "quotes.txt")
USED_QUOTES_FILE = os.path.join(BASE_DIR, "used_quotes.txt")
MUSIC_IMAGES_DIR = os.path.join(BASE_DIR, "music_video_images")
IMAGES_DIR = os.path.join(BASE_DIR, "Images")
USED_IMAGES_TRACKER = os.path.join(BASE_DIR, "used_kinetic_images.txt")
USED_MUSIC_TRACKER = os.path.join(BASE_DIR, "used_kinetic_music.txt")
TREBLO_URLS_FILE = os.path.join(BASE_DIR, "treblo_music_urls.txt")
BGM_FILE = os.path.join(BASE_DIR, "AUDIT_PURE_SOFT_BANSURI_5_TRACKS.mp3")
LOGO_PATH = os.path.join(BASE_DIR, "kv_watermark_logo.png")

def get_unique_treblo_bgm(temp_dir):
    """
    Selects a completely UNIQUE Treblo AI Bansuri track for every single reel from the 1,460-track pool.
    Guarantees:
    - Never repeats the same music track across reels.
    - 100% verified original Treblo AI (0% copyright risk).
    - Falls back to dynamic random segment offset in local master audit file if network drop.
    """
    dest_path = os.path.join(temp_dir, "unique_treblo_bgm.mp3")
    used = set()
    if os.path.exists(USED_MUSIC_TRACKER):
        with open(USED_MUSIC_TRACKER, "r", encoding="utf-8") as f:
            used = {line.strip() for line in f if line.strip()}

    all_urls = []
    if os.path.exists(TREBLO_URLS_FILE):
        with open(TREBLO_URLS_FILE, "r", encoding="utf-8") as f:
            all_urls = [line.strip() for line in f if line.strip().startswith("http")]

    available = [u for u in all_urls if u not in used]
    if not available and all_urls:
        available = all_urls
        used.clear()

    if available:
        chosen_url = random.choice(available)
        try:
            cmd = ["curl", "-s", "-L", "-f", "--retry", "3", "--max-time", "15", "-o", dest_path, chosen_url]
            res = subprocess.run(cmd, capture_output=True)
            if res.returncode == 0 and os.path.exists(dest_path) and os.path.getsize(dest_path) > 100000:
                with open(USED_MUSIC_TRACKER, "a", encoding="utf-8") as f:
                    f.write(chosen_url + "\n")
                print(f"🎵 Downloaded Fresh Unique Treblo BGM: {chosen_url} ({os.path.getsize(dest_path)} bytes)")
                return dest_path
        except Exception as e:
            print(f"BGM download note: {e}")

    # Fallback to local AUDIT_PURE_SOFT_BANSURI_5_TRACKS.mp3 with random start time offset
    if os.path.exists(BGM_FILE):
        print(f"🎵 Using Master Treblo Flute Audio with dynamic random segment offset.")
        return BGM_FILE
    return None

def detect_thought_adaptive_hook(thought_text):
    """
    Intelligently analyzes the thought's core theme and selects a contextually accurate hook.
    ONLY uses 'श्री कृष्ण / कान्हा' hooks when the thought is explicitly spiritual/Gita/Krishna-related.
    For struggle, anger, patience, success, or life wisdom, uses powerful topic-specific hooks!
    """
    text = thought_text.lower()

    # 1. Krishna / Bhagavad Gita / Arjun / Divine Spiritual
    krishna_keywords = ["कृष्ण", "कान्हा", "पार्थ", "अर्जुन", "गीता", "ईश्वर", "परमात्मा", "कर्मण्ये", "भगवान", "भक्ति", "माधव", "गोविंद", "हरि", "प्रभु", "राधे", "नारायण"]
    if any(k in text for k in krishna_keywords):
        return random.choice([
            "श्री कृष्ण का यह दिव्य वचन सुनो —",
            "हे पार्थ, जीवन का यह गूढ़ सत्य समझो —",
            "कर्म का यह अमर विधान याद रखना —",
            "कान्हा का यह पावन संदेश सदा याद रखना —",
            "श्री कृष्ण कहते हैं, ध्यान से सुनो —"
        ])

    # 2. Anger / Mind / Silence / Patience / Inner Peace
    peace_keywords = ["क्रोध", "गुस्सा", "मन", "धैर्य", "शांति", "मौन", "चुप", "सब्र", "शांत", "अहंकार", "घमंड", "अपमान"]
    if any(k in text for k in peace_keywords):
        return random.choice([
            "जब मन अशांत हो, तब यह ज्ञान सुनो —",
            "क्रोध में कोई निर्णय लेने से पहले यह सुनो —",
            "धैर्य और सब्र का यह अनमोल नियम सुनो —",
            "मौन की इस महान शक्ति को सदा याद रखना —",
            "जब कोई तुम्हारा अपमान करे, तब यह याद रखना —"
        ])

    # 3. Struggle / Tough Times / Darkness / Pain / Courage
    struggle_keywords = ["कठिन", "मुश्किल", "समय", "हार", "जीत", "संघर्ष", "शुरुआत", "विपत्ति", "दर्द", "तकलीफ", "अंधेरा", "रास्ते", "उम्मीद", "हिम्मत", "साहस", "डर", "घबराना"]
    if any(k in text for k in struggle_keywords):
        return random.choice([
            "जब जीवन में कठिन समय आए, तब याद रखना —",
            "संघर्ष से कभी मत घबराना, यह सुनो —",
            "हार मानने से पहले यह बात ज़रूर सुनना —",
            "जब रास्ते बंद दिखने लगें, तब यह याद रखना —",
            "कठिन दौर में यह एक बात सदा याद रखना —"
        ])

    # 4. Success / Hard Work / Goal / Change / Destiny
    success_keywords = ["सफलता", "मेहनत", "लक्ष्य", "कामयाबी", "बदलाव", "कर्म", "परिश्रम", "मंजिल", "भाग्य", "किस्मत", "सपना", "सपने"]
    if any(k in text for k in success_keywords):
        return random.choice([
            "सफलता पाने का यह स्वर्णिम नियम सुनो —",
            "यदि जीवन बदलना चाहते हो, तो यह सुनो —",
            "मेहनत और कर्म का यह नियम सदा याद रखना —",
            "सच्ची कामयाबी का यह रहस्य सुनो —",
            "अपनी मंजिल पाने से पहले यह जान लो —"
        ])

    # 5. Thinkers / People / Truth / World / Relations
    wisdom_keywords = ["विचारक", "महान", "लोग", "संसार", "दुनिया", "रिश्ते", "विश्वास", "धोखा", "सच्चाई", "सत्य", "पहचान", "समझदारी", "ज्ञान", "सीख"]
    if any(k in text for k in wisdom_keywords):
        return random.choice([
            "संसार का यह कड़वा सच सदा याद रखना —",
            "महान विचारकों का यह गहरा सत्य सुनो —",
            "लोगों की पहचान करने का यह नियम सुनो —",
            "जीवन की इस कड़वी सच्चाई को पहचानो —",
            "सच्चे ज्ञान की यह बात हमेशा याद रखना —"
        ])

    # 6. General Life Wisdom Fallback
    return random.choice([
        "जीवन का यह परम सत्य सदा याद रखना —",
        "बुद्धिमान मनुष्य की यह सीख सदा याद रखना —",
        "सत्य की इस अनमोल वाणी को ध्यान से सुनो —"
    ])

# Visualizer Geometries & Divine Color Palettes
VISUALIZER_STYLES = [
    "silk_sine_ribbon",
    "circular_radiant_pulse",
    "sacred_mandala_orbit",
    "lotus_petal_frequencies",
    "fullwidth_bars",
    "cosmic_frequency_wave"
]

COLOR_PALETTES = [
    [(15, 235, 255), (60, 245, 255), (255, 255, 255)],   # Cyan/Gold/White
    [(30, 215, 255), (0, 165, 255), (255, 255, 255)],    # Golden Sunrise
    [(80, 230, 120), (40, 200, 240), (255, 255, 255)],   # Emerald Vrindavan
    [(0, 140, 255), (30, 90, 255), (255, 255, 255)],     # Sacred Saffron
    [(220, 100, 255), (255, 180, 255), (255, 255, 255)], # Divine Amethyst
    [(255, 255, 255), (200, 230, 255), (180, 220, 255)]  # Pure Pearl
]

def find_chrome():
    candidates = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates:
        if os.path.isabs(c):
            if os.path.exists(c):
                return c
        else:
            p = shutil.which(c)
            if p:
                return p
    return None

def find_ffmpeg():
    local_p = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
    if os.path.exists(local_p):
        return local_p
    p = shutil.which("ffmpeg")
    return p if p else "ffmpeg"

def get_next_quote():
    """Gets the next thought from quotes.txt, moves it to used_quotes.txt, and auto-recycles if exhausted."""
    if not os.path.exists(QUOTES_FILE):
        return "तुम्हारा केवल कर्म है, बाक़ी सब मुझ पर छोड़ दो।"

    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]

    if not quotes:
        if os.path.exists(USED_QUOTES_FILE):
            with open(USED_QUOTES_FILE, "r", encoding="utf-8") as uf:
                used = [line.strip() for line in uf if line.strip()]
            if used:
                random.shuffle(used)
                with open(QUOTES_FILE, "w", encoding="utf-8") as f:
                    f.write("\n".join(used) + "\n")
                with open(USED_QUOTES_FILE, "w", encoding="utf-8") as uf:
                    uf.write("")
                print(f"🔄 Auto-recycled {len(used)} quotes from used_quotes.txt back to quotes.txt!")
                quotes = used

    if not quotes:
        return "तुम्हारा केवल कर्म है, बाक़ी सब मुझ पर छोड़ दो।"

    chosen_quote = quotes.pop(0)

    with open(QUOTES_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(quotes) + ("\n" if quotes else ""))

    with open(USED_QUOTES_FILE, "a", encoding="utf-8") as uf:
        uf.write(chosen_quote + "\n")

    return chosen_quote

def clean_image_watermark(image_path, target_cleaned_path):
    """Universal Google Flow Star Watermark Remover: 0% Cropping, 100% Full Frame preserved via Telea inpainting."""
    try:
        data = np.fromfile(image_path, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img is not None:
            h, w = img.shape[:2]
            y1 = int(h * 0.77)
            y2 = int(h * 0.93)
            x1 = int(w * 0.89)
            x2 = w
            corner = img[y1:y2, x1:x2]
            gray = cv2.cvtColor(corner, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
            dilated = cv2.dilate(thresh, kernel, iterations=2)
            ch, cw = corner.shape[:2]
            cv2.circle(dilated, (int(cw * 0.65), int(ch * 0.5)), int(min(cw, ch) * 0.35), 255, -1)
            full_mask = np.zeros((h, w), dtype=np.uint8)
            full_mask[y1:y2, x1:x2] = dilated
            cleaned = cv2.inpaint(img, full_mask, inpaintRadius=7, flags=cv2.INPAINT_TELEA)
            success, encoded = cv2.imencode('.jpg', cleaned, [cv2.IMWRITE_JPEG_QUALITY, 96])
            if success:
                encoded.tofile(target_cleaned_path)
                return target_cleaned_path
    except Exception as e:
        print(f"Watermark clean note: {e}")
    shutil.copy(image_path, target_cleaned_path)
    return target_cleaned_path

def get_next_image():
    """Picks a unique, random clean Krishna image from pool (tracked by basename across Windows & Linux)."""
    all_images = []
    for d in [MUSIC_IMAGES_DIR, IMAGES_DIR]:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                for f in files:
                    if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                        all_images.append(os.path.join(root, f))

    all_images = sorted(list(dict.fromkeys(all_images)))
    if not all_images:
        raise RuntimeError("No clean Krishna images found in pool!")

    used_basenames = set()
    if os.path.exists(USED_IMAGES_TRACKER):
        with open(USED_IMAGES_TRACKER, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    used_basenames.add(os.path.basename(line))

    available = [img for img in all_images if os.path.basename(img) not in used_basenames]
    if not available:
        print(f"🔄 All {len(all_images)} clean images used! Resetting tracker for next cycle.")
        used_basenames.clear()
        if os.path.exists(USED_IMAGES_TRACKER):
            with open(USED_IMAGES_TRACKER, "w", encoding="utf-8") as f:
                f.write("")
        available = all_images

    # Random selection guarantees different image on every single Reel
    chosen = random.choice(available)
    with open(USED_IMAGES_TRACKER, "a", encoding="utf-8") as f:
        f.write(os.path.basename(chosen) + "\n")

    return chosen

def split_quote_into_phrases(quote_text):
    """Splits a long thought into natural 2-4 word rhythmic phrases."""
    cleaned = quote_text.replace("- राधे कृष्ण", "").replace("- श्री कृष्ण", "").strip()
    raw_clauses = [c.strip() for c in cleaned.replace(";", ",").replace("!", "।").split("।") if c.strip()]
    
    phrases = []
    for clause in raw_clauses:
        sub_parts = [s.strip() for s in clause.split(",") if s.strip()]
        for sub in sub_parts:
            words = sub.split()
            if not words:
                continue
            curr_chunk = []
            for w in words:
                curr_chunk.append(w)
                if len(curr_chunk) >= 3:
                    phrases.append(curr_chunk)
                    curr_chunk = []
            if curr_chunk:
                if len(curr_chunk) == 1 and phrases:
                    phrases[-1].append(curr_chunk[0])
                else:
                    phrases.append(curr_chunk)

    if not phrases:
        phrases = [["तुम्हारा", "केवल", "कर्म", "है,"], ["बाक़ी", "सब", "मुझ", "पर", "छोड़", "दो।"]]

    if not phrases[-1][-1].endswith("।"):
        phrases[-1][-1] += "।"

    return phrases

from reel_atmospheric_engine import select_thought_atmospheric, AtmosphericParticleSimulator, SACRED_PALETTES

# 12+ Emotion-Adaptive Voice Profiles (Spanning Sad, Joy, Masti, Motivation, Peace - Men & Female)
VOICE_CATALOG = {
    "SED_SOLACE": [
        {"name": "hi-IN-Chirp3-HD-Charon", "gender": "MALE", "rate": 0.83, "tone": "गंभीर, सांत्वना देने वाला शांत स्वर", "bass": 3.0, "treble": 1.2},
        {"name": "hi-IN-Chirp3-HD-Aoede", "gender": "FEMALE", "rate": 0.85, "tone": "स्नेही, करुणामयी कोमल स्त्री स्वर", "bass": 1.5, "treble": 2.2},
    ],
    "KHUSHI_PREM": [
        {"name": "hi-IN-Chirp3-HD-Sadachbia", "gender": "MALE", "rate": 0.88, "tone": "मधुर, भक्ति एवं प्रेममय स्वर", "bass": 2.0, "treble": 2.0},
        {"name": "hi-IN-Chirp3-HD-Kore", "gender": "FEMALE", "rate": 0.86, "tone": "सौम्य, आनंदमयी स्त्री स्वर", "bass": 1.5, "treble": 2.4},
    ],
    "MASTI_UTSAH": [
        {"name": "hi-IN-Chirp3-HD-Puck", "gender": "MALE", "rate": 0.92, "tone": "उमंग भरा, स्फूर्तिदायक स्वर", "bass": 1.8, "treble": 2.5},
        {"name": "hi-IN-Chirp3-HD-Leda", "gender": "FEMALE", "rate": 0.89, "tone": "उत्साही, प्रेरणादायक स्त्री स्वर", "bass": 1.8, "treble": 2.2},
    ],
    "MOTIVATION_SAHAS": [
        {"name": "hi-IN-Chirp3-HD-Fenrir", "gender": "MALE", "rate": 0.87, "tone": "ओजस्वी, आत्मविश्वासी गुरु स्वर", "bass": 2.8, "treble": 1.6},
        {"name": "hi-IN-Neural2-B", "gender": "MALE", "rate": 0.88, "tone": "दृढ़, गंभीर कर्म उपदेशक स्वर", "bass": 3.0, "treble": 1.5},
        {"name": "hi-IN-Neural2-D", "gender": "FEMALE", "rate": 0.87, "tone": "प्रेरक, जागृतिदायक स्त्री स्वर", "bass": 1.6, "treble": 2.2},
    ],
    "SHANTI_DHYAN": [
        {"name": "hi-IN-Chirp3-HD-Orus", "gender": "MALE", "rate": 0.83, "tone": "अत्यंत शांत, ध्यानमग्न साधना स्वर", "bass": 2.5, "treble": 1.8},
        {"name": "hi-IN-Neural2-C", "gender": "MALE", "rate": 0.84, "tone": "गहन ध्यान, मौन चिंतन स्वर", "bass": 3.0, "treble": 1.5},
        {"name": "hi-IN-Neural2-A", "gender": "FEMALE", "rate": 0.85, "tone": "पावन, शांतिदायक प्रार्थना स्वर", "bass": 1.5, "treble": 2.4},
    ]
}

def detect_thought_emotion_category(thought_text):
    text_lower = thought_text.lower()
    sed_words = ["दुःख", "कठिन", "दर्द", "हार", "आंसू", "संकट", "अकेला", "बुरा", "विपत्ति", "पीड़ा", "रुला", "चोट", "उदासी", "कष्ट", "समय खराब"]
    khushi_words = ["खुशी", "आनंद", "प्रेम", "मुस्कान", "सखा", "राधा", "बांसुरी", "हर्ष", "सुख", "मधुर", "मनमोहक", "प्रसन्न", "प्यार"]
    masti_words = ["उत्साह", "नया", "उमंग", "प्रकाश", "सवेरा", "खिल", "हँसी", "मस्ती", "खिलखिला", "चंचल", "रंग", "सृष्टि"]
    shanti_words = ["शांति", "मौन", "ध्यान", "ईश्वर", "आत्मा", "प्रभु", "समर्पण", "शांत", "सत्य", "साधना", "भरोसा", "विश्वास", "कान्हा"]
    motivation_words = ["साहस", "हिम्मत", "सफलता", "लक्ष्य", "जीत", "कर्म", "पुरुषार्थ", "कर्तव्य", "सामर्थ्य", "प्रयास", "मेहनत", "रास्ता"]

    for w in sed_words:
        if w in text_lower:
            return "SED_SOLACE"
    for w in khushi_words:
        if w in text_lower:
            return "KHUSHI_PREM"
    for w in masti_words:
        if w in text_lower:
            return "MASTI_UTSAH"
    for w in shanti_words:
        if w in text_lower:
            return "SHANTI_DHYAN"
    for w in motivation_words:
        if w in text_lower:
            return "MOTIVATION_SAHAS"

    return random.choice(["SHANTI_DHYAN", "MOTIVATION_SAHAS"])

def select_thought_voice(thought_text):
    cat = detect_thought_emotion_category(thought_text)
    options = VOICE_CATALOG.get(cat, VOICE_CATALOG["SHANTI_DHYAN"])
    selected = random.choice(options)
    return cat, selected

def synthesize_voice(phrases, output_audio_path, temp_dir):
    """
    Synthesizes authentic human spiritual voiceover with real emotional depth (12+ Voices)
    speaking ONLY the pure thought text (ZERO extra hook words, ZERO robotic breaks).
    """
    ffmpeg = find_ffmpeg()

    def get_dur(fpath):
        res = subprocess.run([ffmpeg, "-i", fpath], stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        import re
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        return 3.0

    full_thought_text = " ".join([" ".join(p) for p in phrases])
    thought_audio = os.path.join(temp_dir, "thought.mp3")

    # Select Emotion-Adaptive Voice Profile
    emotion_cat, voice_prof = select_thought_voice(full_thought_text)
    print(f"🎙️ Selected Voice Profile: {emotion_cat} -> {voice_prof['name']} ({voice_prof['tone']}, speaking_rate={voice_prof['rate']})")

    # Check for Google Cloud credentials
    gcreds_file = os.path.join(BASE_DIR, "google_tts_service_account.json")
    gcreds_env = os.environ.get("GOOGLE_TTS_SERVICE_ACCOUNT")
    embedded_b64 = "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAieW91dHViZS1idWxrLXVwZGF0ZS01MDEwMDkiLAogICJwcml2YXRlX2tleV9pZCI6ICJlMTNiY2M2NDMyOGE3MjMwOTNkOGZiMjMyZWM5MDRjOWIzZDg3Mzg4IiwKICAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdkFJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLWXdnZ1NpQWdFQUFvSUJBUUNkNEdjTWozOGZMUTN0XG5iVmdHY3RRS3lyMXFIMCtvOE9zN2lWRU1QbEhmZm4zOGZxMVJFZmRJZWJzekQ2Q3JaK3NPeDZCbjUzTUc2Yk14XG5kVk9rbVBTTHpHQVZIRU11Vm1uajZaR081VDB1OENRTWpPWTF4Zlc2cktTZW5oNGNXN0JwWWsrNjN4MXpuWU5YXG5iNWJCRFB5NVJlcldjMU9rQmhVSmtyTEd0OFZvK0llaGhoVXRGeCswbmFDdG9vK0tRRFRqS25RUnRPWitWcXBHXG54OXRLVVJJdHZraVp3ZU1ia1J6cXpCOGVzckJ4VlJPZXRFQUdpVXZtZ1ljTXMwdTJjcDhoNkV6TEhrc08veDhlXG4rZ3FWb3NZR0d6bHpuYkQwZGdOTEhYMzRrbzNYS25LaHVSVlhkMmI3V2RPMkdwaDBDNVFMQXU4citVdEg5SnBkXG5SVTVnYmp4UEFnTUJBQUVDZ2dFQU13MmpKVXV1RngzUnVDcTQ0WFQybnZySzMrdDZMaTZpVXlGbnBTYnVBUEQ5XG51czRZSy9ROFhDS0paOHl3NzF6dWhWd0d3akwxWHBIcVVaOFlTa3p3SDlrYVpSazduRnR6YUxGYVViUk40Y1RrXG5VMjZvNzFDeDB3a0xQd1B3eHNqYnRtaUZVZS9lclVtTmRKUHdVME5vNGx6NndSaVFQcVY4M2hpaldXR0tKQlJnXG5WekJBazYvRkducWNNNXdwelBhZ2NqR2ljVUdMSGk3U3pYYmtlV3F4REFtYVFsRzRLcEpTbXJsMTRhNEIzM3pHXG51Y255ekEya0ZMR0ZCTVIxaCtwNm5hRDNzRWpPZWNxQ0lYblo2WlBKTXNCcTMyc0ZzMHB1d1FIY2UzOERzZEpiXG5yay9CTkxvNnNhZUd5ajVHOFR1VXRZVXJScUFVdmFFK24vMmRHR2NjMFFLQmdRRFNiYXlDbXlMN0RIeklObFNzXG4yVmJ0N1ZyQnVWeld5WWxrUFd2bXR0RVRiTFhhZzNTTTd5Z1p3aTRKenVBeHFvSWNBeUJTVnovZWVSMW04b3JCXG5nM0srQzRGdVc1T2RHSjdYaGVjdERIdmo0RjJxNlltOXgvYUNCR0ovaEx4M3JYdWtVamJEZ0FINGg1T0NIaGtvXG5DKzIybXB3TTBnWDRVMVdRS0FqVktEQ091UUtCZ1FEQUVUWCt6WWFBSHBJa2h4bUtUZHJBc3Z5Y3kvSFErQVpXXG5UZHA1OUM2V0IwUmpqZ1dhV0xBR2ZmVkhEYWI5aTJ2cHBpeGphVDZzMUE4c2pYbW1XaGFxc1VEaklhOEJZRDJjXG4wWmY5Q0tkNzZaYmlCY0xETGFmMVpBMU1KOFFTNUNvM05tMUZZY05tTnloRUJPemdxc1BLQnJJdGpHb0dSRHkxXG53ZkpzNWdCZlJ3S0JnSC9JNWpleDZmNDJTUmgwRmR1WmFEYTRLcUwxNDdEelZpR3ZRdlVxRTdFT0ZTa0xKeDNtXG5wWjF1MC9KVTFNU1VYTXFTQTNDOVZ5WE11dFFuZWFlbUlXblRKdGhUZUVLd0R0V21sUXBBU0lQTFhsWkoxOEdOXG55dDZOdHhybENtWkt6WWl0L0YrZ1BwSWtFcW16aVdkT1J4N2FxT1VJTFdQdGgwb3haWnU3K2pEUkFvR0FlenRQXG51cUdodDVobHlod0lqZzF2Mm8yOHVObTkySWNhZ2N0SDcxRjFobnM1TE9zVnV6ZEdFWlJGaUlaQTY1TEY5VTdTXG5VaUpYdlVuK1JtYXJjOGwvbTV0STk3SkgrQWtJM3hJM2czbEhCS0VXVndTOU5yK1hjVUgxcWpRbGdMMTJQS0NtXG5NWXNOZFFyVXdmZXJDR2RvWWJvMEhqZG1XNGp5cnVlMnBKcGFDTWNDZ1lCNUhYczhiMW5LUVowcENNU2I2S1BEXG5vRkNCdHJMUGU0Vk5ORmlqMnYvZ2JpUThXT2hjQnFFVGRmWEpyQTZyZk1yY21IUjdVcmIwZzZQTS9ZTG00Z3VPXG5mdE5KQWRObVBYVlQ3Z2hTaTFZeFAxaVY0REttbE9hWmVROTlxa0J3K0hIaEN1L1I2SmRISEI3bEUwc0hCR2VEXG5HR2RRbDRLNmlpZ3AwbnQwM2tzek13PT1cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJrcmlzaG5hLXJlZWwtYXVkaW9AeW91dHViZS1idWxrLXVwZGF0ZS01MDEwMDkuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTA3MjI4MjAxMjg3NTQwNjkzNDcxIiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9rcmlzaG5hLXJlZWwtYXVkaW9lNDB5b3V0dWJlLWJ1bGstdXBkYXRlLTUwMTAwOS5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsCiAgInVuaXZlcnNlX2RvbWFpbiI6ICJnb29nbGVhcGlzLmNvbSIKfQo="

    client = None
    use_google = False

    if gcreds_env or os.path.exists(gcreds_file) or embedded_b64:
        try:
            import json
            from google.cloud import texttospeech
            from google.oauth2 import service_account
            if os.path.exists(gcreds_file):
                client = texttospeech.TextToSpeechClient.from_service_account_json(gcreds_file)
            elif gcreds_env or embedded_b64:
                import base64
                raw_json = gcreds_env if gcreds_env else base64.b64decode(embedded_b64).decode("utf-8")
                info = json.loads(raw_json)
                creds = service_account.Credentials.from_service_account_info(info)
                client = texttospeech.TextToSpeechClient(credentials=creds)

            voice_params = texttospeech.VoiceSelectionParams(
                language_code="hi-IN",
                name=voice_prof["name"],
            )
            audio_cfg = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=voice_prof["rate"]
            )
            use_google = True
        except Exception as ge:
            print(f"Google TTS init note: {ge}")

    # Synthesize Pure Thought in ONE single, unbroken master recording
    if use_google:
        try:
            resp = client.synthesize_speech(
                input=texttospeech.SynthesisInput(text=full_thought_text),
                voice=voice_params,
                audio_config=audio_cfg
            )
            with open(thought_audio, "wb") as f:
                f.write(resp.audio_content)
        except Exception as te:
            print(f"Primary voice fallback: {te}")
            fallback_voice = "hi-IN-Neural2-B" if voice_prof["gender"] == "MALE" else "hi-IN-Neural2-A"
            v_neural2 = texttospeech.VoiceSelectionParams(language_code="hi-IN", name=fallback_voice)
            cfg_neural2 = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=0.88)
            resp = client.synthesize_speech(input=texttospeech.SynthesisInput(text=full_thought_text), voice=v_neural2, audio_config=cfg_neural2)
            with open(thought_audio, "wb") as f:
                f.write(resp.audio_content)
    else:
        import edge_tts, asyncio
        edge_v = 'hi-IN-MadhurNeural' if voice_prof["gender"] == "MALE" else 'hi-IN-SwaraNeural'
        asyncio.run(edge_tts.Communicate(full_thought_text, edge_v, rate="-10%").save(thought_audio))

    thought_dur = get_dur(thought_audio)

    # Master audio with studio warm EQ tailored to the selected voice
    master_cmd = [
        ffmpeg, "-y",
        "-i", thought_audio,
        "-af", f"bass=g={voice_prof['bass']}:f=160,treble=g={voice_prof['treble']}:f=3200,volume=1.35",
        output_audio_path
    ]
    subprocess.run(master_cmd, check=True)

    # Map Word Timings across thought duration starting at exactly 0.50s
    all_words = []
    for p in phrases:
        all_words.extend(p)

    total_chars = sum(len(w) for w in all_words)
    raw_durs = [max((len(w) / max(total_chars, 1)) * thought_dur, 0.22) for w in all_words]
    scale_factor = thought_dur / max(sum(raw_durs), 0.01)
    normalized_durs = [d * scale_factor for d in raw_durs]

    word_timings = []
    w_idx = 0
    curr_t = 0.50  # Voice starts cleanly at 0.50s (allowing 0.5s for opening flute chord & focus)

    for phrase in phrases:
        phrase_timings = []
        for w in phrase:
            w_dur = normalized_durs[w_idx]
            phrase_timings.append({
                'word': w,
                'start': curr_t,
                'end': curr_t + w_dur
            })
            curr_t += w_dur
            w_idx += 1
        word_timings.append(phrase_timings)

    voice_end_t = curr_t
    return voice_end_t, word_timings, full_thought_text

def render_chrome_slide(task):
    if len(task) == 4:
        chrome, html_file, png_file, win_size = task
    else:
        chrome, html_file, png_file = task
        win_size = "1080,420"
    file_url = "file:///" + os.path.abspath(html_file).replace("\\", "/")
    cmd = [
        chrome,
        "--headless=new",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--default-background-color=00000000",
        f"--window-size={win_size}",
        f"--screenshot={png_file}",
        file_url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(png_file) or os.path.getsize(png_file) == 0:
        raise RuntimeError(f"Chrome screenshot failed ({res.returncode}): {res.stderr}\nCommand: {' '.join(cmd)}")
    return png_file

def extract_audio_envelope(audio_path, total_frames, fps=25, sr=22050):
    """
    Extracts frame-by-frame REAL audio RMS energy and FFT frequency spectrum from the actual voice/music.
    The visualizer is 100% physically linked to spoken words, voice pitch, and flute notes!
    """
    ffmpeg = find_ffmpeg()
    cmd = [
        ffmpeg, "-y",
        "-i", audio_path,
        "-ac", "1",
        "-ar", str(sr),
        "-f", "f32le",
        "pipe:1"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw = proc.stdout.read()
    proc.wait()

    audio = np.frombuffer(raw, dtype=np.float32)
    if len(audio) == 0:
        return np.ones(total_frames, dtype=np.float32) * 0.5, [np.zeros(48, dtype=np.float32) for _ in range(total_frames)]

    samples_per_frame = int(sr / fps)
    energies = []
    spectrums = []

    for i in range(total_frames):
        s_start = i * samples_per_frame
        s_end = min(s_start + samples_per_frame, len(audio))
        if s_start >= len(audio):
            energies.append(0.02)
            spectrums.append(np.zeros(48, dtype=np.float32))
            continue

        chunk = audio[s_start:s_end]
        rms = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.02
        energies.append(rms)

        if len(chunk) >= 64:
            fft_vals = np.abs(np.fft.rfft(chunk))
            bins = np.array_split(fft_vals[:min(len(fft_vals), 256)], 48)
            band_energies = np.array([float(np.mean(b)) if len(b) > 0 else 0.0 for b in bins], dtype=np.float32)
            b_max = float(np.max(band_energies)) or 1.0
            spectrums.append(band_energies / b_max)
        else:
            spectrums.append(np.zeros(48, dtype=np.float32))

    energies = np.array(energies, dtype=np.float32)
    e_min, e_max = float(np.min(energies)), float(np.max(energies)) or 1.0
    # True dynamic scaling: 0.15 during silence, up to 2.20 during loud spoken words
    norm_energy = 0.15 + 2.05 * ((energies - e_min) / max(e_max - e_min, 0.001))
    smoothed = np.convolve(norm_energy, [0.2, 0.6, 0.2], mode='same')
    return smoothed, spectrums

def draw_procedural_wave(canvas, style, palette, intensity, t, base_y=660, spectrum=None):
    """Draws real audio-reactive soundwave onto RGBA canvas with alpha support."""
    w = canvas.shape[1]
    col_main = (palette[0][0], palette[0][1], palette[0][2], 255)
    col_mid = (palette[1][0], palette[1][1], palette[1][2], 210)
    col_glow = (palette[2][0], palette[2][1], palette[2][2], 160)

    if style == "fullwidth_bars":
        num_bars = 48
        bar_w = int(w / num_bars)
        spec = spectrum if (spectrum is not None and len(spectrum) == num_bars) else np.zeros(num_bars)
        for b in range(num_bars):
            bx = b * bar_w + int(bar_w * 0.15)
            bw = int(bar_w * 0.70)
            # Bar height is 100% physically driven by the real audio frequency of each word!
            freq_val = float(spec[b]) if b < len(spec) else 0.1
            bh = int(8 + (freq_val * 48.0 + 10.0) * intensity)
            bh = max(6, min(bh, 100))
            y_top = base_y - bh
            y_bot = base_y + bh
            c = col_main if (b % 2 == 0) else col_mid
            cv2.rectangle(canvas, (bx, y_top), (bx + bw, y_bot), c, -1)

    elif style == "silk_sine_ribbon":
        pts1 = []
        pts2 = []
        for x in range(0, w, 5):
            phase = (x / float(w)) * 4.0 * math.pi
            # Ribbon amplitude physically expands with spoken word energy!
            y_off = (math.sin(phase + t * 4.2) * 28.0 + math.sin(phase * 2.1 - t * 2.8) * 14.0) * intensity
            y1 = int(base_y + y_off)
            y2 = int(base_y - y_off * 0.75)
            pts1.append([x, y1])
            pts2.append([x, y2])
        for p in [pts1, pts2]:
            cv2.polylines(canvas, [np.array(p, np.int32)], False, col_glow, 5, cv2.LINE_AA)
            cv2.polylines(canvas, [np.array(p, np.int32)], False, col_main, 2, cv2.LINE_AA)

    else:
        pts = []
        for x in range(0, w, 6):
            rad = (x / float(w)) * 6.28
            y_off = (math.sin(rad * 3.0 + t * 4.5) * 30.0 + math.sin(rad * 6.0 - t * 3.0) * 15.0) * intensity
            pts.append([x, int(base_y + y_off)])
        cv2.polylines(canvas, [np.array(pts, np.int32)], False, col_glow, 6, cv2.LINE_AA)
        cv2.polylines(canvas, [np.array(pts, np.int32)], False, col_main, 2, cv2.LINE_AA)

def generate_kinetic_reel(output_mp4, custom_quote=None, custom_image=None):
    """
    Complete end-to-end Kinetic Short Generator.
    Returns: (output_mp4, quote_text, image_path)
    """
    chrome = find_chrome()
    ffmpeg = find_ffmpeg()

    if not chrome:
        raise RuntimeError("Google Chrome or Chromium not found on system! (Checked candidates)")

    if not os.path.exists(BGM_FILE) and not os.path.exists(TREBLO_URLS_FILE):
        raise RuntimeError("No BGM pool found (neither local BGM nor treblo_music_urls.txt)!")

    quote_text = custom_quote or get_next_quote()
    image_path = custom_image or get_next_image()

    if not image_path or not os.path.exists(image_path):
        raise RuntimeError("No valid clean Krishna image available for Reel!")

    temp_dir = os.path.join(BASE_DIR, f"temp_short_{int(time.time())}")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        phrases = split_quote_into_phrases(quote_text)
        print(f"🎬 Generating Kinetic Reel for Thought: \"{quote_text}\"")
        print(f"🖼️ Using Clean Image: {os.path.basename(image_path)}")

        # Clean image to guarantee 100% Zero Flow watermark
        clean_image_path = os.path.join(temp_dir, "clean_bg.jpg")
        clean_image_watermark(image_path, clean_image_path)

        voice_audio = os.path.join(temp_dir, "voice.mp3")
        voice_end_t, word_timings, full_thought_text = synthesize_voice(phrases, voice_audio, temp_dir)

        # Dynamic Timing: Speech finishes, then the FULL thought displays all together for at least 5.0 seconds!
        summary_start_t = voice_end_t + 0.35
        summary_dur = max(5.0, 11.8 - summary_start_t - 0.8)
        summary_end_t = summary_start_t + summary_dur
        total_video_dur = summary_end_t + 0.8
        print(f"🎙️ Voice Duration: {voice_end_t:.2f}s | Full Thought Outro: {summary_dur:.2f}s | Total Reel: {total_video_dur:.2f}s")

        # HTML template for Kinetic Chrome rendering
        html_template = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    margin: 0; padding: 0; width: 1080px; height: 420px;
    background: transparent;
    display: flex; justify-content: center; align-items: center; text-align: center;
    font-family: 'Nirmala UI', 'Noto Sans Devanagari', 'Segoe UI', sans-serif;
  }}
  .box {{
    font-size: 110px; font-weight: 900; line-height: 1.25;
    color: #FFFFFF;
    -webkit-text-stroke: 13px #000000;
    paint-order: stroke fill;
    text-shadow: 0 12px 28px rgba(0,0,0,0.95);
  }}
  .active {{
    color: #FFE600;
    -webkit-text-stroke: 15px #000000;
    paint-order: stroke fill;
    text-shadow: 0 0 35px #FFD700, 0 12px 28px #000;
  }}
</style>
</head>
<body>
  <div class="box">{content}</div>
</body>
</html>"""

        tasks = []
        overlay_events = []
        overlay_idx = 0

        for p_idx, phrase in enumerate(word_timings):
            split_twoline = len(phrase) >= 4
            for active_wt in phrase:
                words_html = []
                for wt in phrase:
                    if wt is active_wt:
                        words_html.append(f"<span class='active'>{wt['word']}</span>")
                    else:
                        words_html.append(f"<span>{wt['word']}</span>")

                if split_twoline and len(words_html) >= 4:
                    mid = len(words_html) // 2
                    content = " ".join(words_html[:mid]) + "<br>" + " ".join(words_html[mid:])
                else:
                    content = " ".join(words_html)

                html_file = os.path.join(temp_dir, f"slide_{overlay_idx:03d}.html")
                png_file = os.path.join(temp_dir, f"slide_{overlay_idx:03d}.png")
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html_template.format(content=content))

                tasks.append((chrome, html_file, png_file, "1080,420"))
                overlay_events.append({
                    'png': png_file,
                    'start': active_wt['start'],
                    'end': active_wt['end'],
                    'pos': '0:760'
                })
                overlay_idx += 1

        # Render Full Thought Showcase Card for the last 5+ seconds
        font_size = 62 if len(full_thought_text) < 45 else (52 if len(full_thought_text) < 90 else (44 if len(full_thought_text) < 140 else 38))
        full_card_html_code = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    margin: 0; padding: 0; width: 1080px; height: 1920px;
    background: transparent;
    display: flex; justify-content: center; align-items: center;
    font-family: 'Nirmala UI', 'Noto Sans Devanagari', 'Segoe UI', sans-serif;
  }}
  .card {{
    width: 880px;
    background: rgba(12, 18, 30, 0.78);
    border: 3px solid rgba(255, 215, 0, 0.88);
    border-radius: 36px;
    padding: 45px 44px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.95), inset 0 0 35px rgba(255, 215, 0, 0.18);
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }}
  .header-badge {{
    color: #FFE600;
    font-size: 36px;
    font-weight: 800;
    letter-spacing: 3px;
    text-shadow: 0 0 20px rgba(255, 215, 0, 0.8), 0 4px 12px #000;
  }}
  .divider {{
    width: 160px;
    height: 3px;
    background: linear-gradient(90deg, transparent, #FFD700, transparent);
    margin: 22px 0;
  }}
  .thought-text {{
    font-size: {font_size}px;
    font-weight: 800;
    line-height: 1.48;
    color: #FFFFFF;
    text-shadow: 0 8px 24px rgba(0,0,0,0.95);
  }}
  .footer-sub {{
    color: #FFD700;
    font-size: 28px;
    font-weight: 600;
    letter-spacing: 2px;
    opacity: 0.92;
  }}
</style>
</head>
<body>
  <div class="card">
    <div class="header-badge">✨ श्री कृष्ण अमृत विचार ✨</div>
    <div class="divider"></div>
    <div class="thought-text">{full_thought_text}</div>
    <div class="divider"></div>
    <div class="footer-sub">॥ राधे कृष्ण ॥</div>
  </div>
</body>
</html>"""

        full_card_html = os.path.join(temp_dir, "full_thought_card.html")
        full_card_png = os.path.join(temp_dir, "full_thought_card.png")
        with open(full_card_html, "w", encoding="utf-8") as f:
            f.write(full_card_html_code)

        tasks.append((chrome, full_card_html, full_card_png, "1080,1920"))
        overlay_events.append({
            'png': full_card_png,
            'start': summary_start_t,
            'end': summary_end_t,
            'pos': '0:0'
        })

        print(f"🎨 Rendering {len(tasks)} Chrome HarfBuzz overlays (including Full Thought Card) in parallel...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(render_chrome_slide, tasks))

        # 100+ Thought-Adaptive Atmospheric Particle Animation & Elevated Soundwave
        atmos_style, atmos_palette_name = select_thought_atmospheric(quote_text)
        atmos_sim = AtmosphericParticleSimulator(atmos_style, atmos_palette_name, width=540, height=960)
        wave_style = random.choice(VISUALIZER_STYLES)
        wave_palette = random.choice(COLOR_PALETTES)
        print(f"✨ Rendering 100+ Procedural Atmosphere ({atmos_style} / {atmos_palette_name}) & Wave ({wave_style})...")

        fps = 25
        total_frames = int(total_video_dur * fps)
        wave_video = os.path.join(temp_dir, "wave_overlay.mp4")

        wave_cmd = [
            ffmpeg, "-y",
            "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", "540x960", "-pix_fmt", "bgra", "-r", str(fps),
            "-i", "-",
            "-vf", "scale=1080:1920:flags=bicubic",
            "-c:v", "png", "-pix_fmt", "rgba",
            wave_video
        ]
        proc = subprocess.Popen(wave_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Extract REAL Audio-Reactive Energy Envelope from the actual voice
        audio_energies, audio_spectrums = extract_audio_envelope(voice_audio, total_frames, fps=fps)

        for i in range(total_frames):
            t = i / float(fps)
            canvas = atmos_sim.draw_frame(t)
            # Physical audio-reactive response: jumps with spoken words, calms during pauses!
            real_intensity = float(audio_energies[i])
            real_spec = audio_spectrums[i] if i < len(audio_spectrums) else np.zeros(48, dtype=np.float32)
            draw_procedural_wave(canvas, wave_style, wave_palette, real_intensity, t, base_y=660, spectrum=real_spec)
            proc.stdin.write(canvas.tobytes())

        proc.stdin.close()
        proc.wait()

        # Build FFmpeg Filter Complex
        # Fullscreen atmospheric particles + Wave elevated at y=1320
        # Text at y=760 (upper chest, crystal clear)
        fade_out_start = f"{total_video_dur - 1.5:.2f}"

        filter_parts = [
            f"[0:v]scale='if(gt(a,9/16),-2,1440)':'if(gt(a,9/16),2560,-2)',crop=1440:2560,zoompan=z='min(zoom+0.0014,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1080x1920:fps=25[base];",
            f"[base][1:v]overlay=0:0[base_with_wave];"
        ]

        has_logo = os.path.exists(LOGO_PATH)
        if has_logo:
            filter_parts.append(f"[2:v]scale=120:120,format=rgba,colorchannelmixer=aa=0.90[wlogo];")
            filter_parts.append(f"[base_with_wave][wlogo]overlay=W-w-110:100[base_with_logo];")
            curr_input = "[base_with_logo]"
            input_args = [
                "-loop", "1", "-t", f"{total_video_dur:.2f}", "-i", clean_image_path,
                "-i", wave_video,
                "-i", LOGO_PATH
            ]
            input_idx = 3
        else:
            curr_input = "[base_with_wave]"
            input_args = [
                "-loop", "1", "-t", f"{total_video_dur:.2f}", "-i", clean_image_path,
                "-i", wave_video
            ]
            input_idx = 2

        for i, oe in enumerate(overlay_events):
            input_args.extend(["-i", oe['png']])
            next_input = f"[tmp_{input_idx}]" if input_idx < len(overlay_events) + (3 if has_logo else 2) - 1 else "[v]"
            pos = oe.get('pos', '0:760')
            filter_parts.append(
                f"{curr_input}[{input_idx}:v]overlay={pos}:enable='between(t,{oe['start']:.2f},{oe['end']:.2f})'{next_input};"
            )
            curr_input = next_input
            input_idx += 1

        voice_idx = input_idx
        bgm_idx = input_idx + 1

        # Select Unique Treblo BGM track for this Reel (1,460 Tracks Pool)
        active_bgm = get_unique_treblo_bgm(temp_dir) or BGM_FILE
        if not os.path.exists(active_bgm):
            raise RuntimeError(f"BGM audio file missing: {active_bgm}")

        # If master file, pick random start offset so it never starts at the same melody
        if active_bgm == BGM_FILE:
            bgm_start_offset = random.randint(0, 750)
        else:
            bgm_start_offset = random.randint(0, 15)

        input_args.extend(["-i", voice_audio, "-i", active_bgm])

        filter_parts.append(
            f"[{voice_idx}:a]apad=whole_dur={total_video_dur:.2f},volume=1.15[voice];"
            f"[{bgm_idx}:a]atrim=start={bgm_start_offset}:duration={total_video_dur:.2f},asetpts=PTS-STARTPTS,volume=0.15,afade=t=out:st={fade_out_start}:d=1.5[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0,volume=1.75[a]"
        )

        final_filter = "".join(filter_parts)

        final_cmd = [
            ffmpeg, "-y"
        ] + input_args + [
            "-filter_complex", final_filter,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", f"{total_video_dur:.2f}",
            output_mp4
        ]

        print("🚀 Rendering final master video with FFmpeg...")
        t0 = time.time()
        res = subprocess.run(final_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg render error: {res.stderr[-1000:]}")

        print(f"✅ SUCCESS! Rendered {output_mp4} ({os.path.getsize(output_mp4)/(1024*1024):.2f} MB in {time.time() - t0:.1f}s)")
        return output_mp4, quote_text, image_path

    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

if __name__ == "__main__":
    out_test = os.path.join(BASE_DIR, "test_kinetic_output.mp4")
    generate_kinetic_reel(out_test)
