#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — SONG AUDIO ANALYZER (सुनकर मूड पहचानना)
=============================================================================
- गाने की ऑडियो फाइल को ffmpeg/ffprobe से एनालाइज़ करता है
- पहचानता है: ड्यूरेशन, वॉल्यूम, टेम्पो, मूड (शांत/ऊर्जावान/भक्ति)
- मूड के हिसाब से थंबनेल के रंग और टाइटल/डिस्क्रिप्शन का सुझाव देता है
- पूरा फ्री (कोई पेड़ API नहीं)
=============================================================================
"""

import os
import sys
import json
import subprocess
import re
import math

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FFMPEG_EXE = "ffmpeg"
FFPROBE_EXE = "ffprobe"
local_ffmpeg = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin"
if os.path.exists(os.path.join(local_ffmpeg, "ffmpeg.exe")):
    FFMPEG_EXE = os.path.join(local_ffmpeg, "ffmpeg.exe")
    FFPROBE_EXE = os.path.join(local_ffmpeg, "ffprobe.exe")


def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, timeout=120)
        return res.returncode, res.stdout, res.stderr
    except Exception as e:
        return -1, "", str(e)


def get_audio_info(file_path):
    """ffprobe से बेसिक ऑडियो इनफॉर्मेशन निकालना"""
    cmd = [
        FFPROBE_EXE, "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", file_path
    ]
    rc, out, err = run_cmd(cmd)
    if rc != 0:
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def analyze_audio_mood(file_path):
    """
    गाने को सुनकर मूड पहचानना:
    - शांत/ध्यान (Peaceful/Meditative)
    - ऊर्जावान/भक्ति (Energetic/Devotional)
    - रोमांटिक/मुलायम (Romantic/Soft)
    """
    info = get_audio_info(file_path)
    if not info:
        return get_default_analysis()

    # ड्यूरेशन
    duration = 0
    if "format" in info and "duration" in info["format"]:
        try:
            duration = float(info["format"]["duration"])
        except Exception:
            duration = 0

    # औसत वॉल्यूम (RMS) और पीक वॉल्यूम निकालना
    volume_cmd = [
        FFMPEG_EXE, "-i", file_path,
        "-af", "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level",
        "-f", "null", "-"
    ]
    rc, out, err = run_cmd(volume_cmd)

    rms_level = -60.0  # डिफ़ॉल्ट बहुत कम
    for line in err.splitlines() + out.splitlines():
        if "RMS_level" in line:
            try:
                val = float(line.split("=")[-1].strip())
                rms_level = val
            except Exception:
                pass

    # टेम्पो अंदाज़ा लगाना (बीट डिटेक्शन सरल संस्करण)
    # ffmpeg की मदद से ऑडियो वेवफॉर्म का विश्लेषण
    tempo_cmd = [
        FFMPEG_EXE, "-i", file_path,
        "-af", "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.Peak_level",
        "-f", "null", "-"
    ]
    rc2, out2, err2 = run_cmd(tempo_cmd)

    peak_level = -60.0
    for line in err2.splitlines() + out2.splitlines():
        if "Peak_level" in line:
            try:
                val = float(line.split("=")[-1].strip())
                peak_level = val
            except Exception:
                pass

    # मूड क्लासिफिकेशन (रूल बेस्ड)
    # dB में: -60 बहुत शांत, -30 मध्यम, -10 ऊंचा
    dynamic_range = peak_level - rms_level

    if duration < 60:
        mood = "Short Devotional"
        mood_hi = "छोटा भक्ति गीत"
    elif rms_level < -40 and dynamic_range < 15:
        mood = "Peaceful Meditative"
        mood_hi = "शांत ध्यान संगीत"
    elif rms_level > -25 and dynamic_range > 20:
        mood = "Energetic Devotional"
        mood_hi = "ऊर्जावान भक्ति संगीत"
    elif -35 <= rms_level <= -25:
        mood = "Romantic Soft"
        mood_hi = "मुलायम रोमांटिक गीत"
    else:
        mood = "Balanced Bhakti"
        mood_hi = "संतुलित भक्ति संगीत"

    # गाना किसके लिए है detect करना
    target_audience, target_audience_hi = detect_target_audience(
        os.path.basename(file_path)
    )

    analysis = {
        "filename": os.path.basename(file_path),
        "duration_sec": round(duration, 2),
        "duration_min": round(duration / 60, 1),
        "rms_level_db": round(rms_level, 2),
        "peak_level_db": round(peak_level, 2),
        "dynamic_range_db": round(dynamic_range, 2),
        "mood": mood,
        "mood_hi": mood_hi,
        "is_vocal_likely": peak_level > -30 and dynamic_range > 12,  # संभावित वोकल गीत
        "target_audience": target_audience,
        "target_audience_hi": target_audience_hi,
    }
    return analysis


def get_default_analysis():
    return {
        "filename": "unknown",
        "duration_sec": 0,
        "duration_min": 0,
        "rms_level_db": -40,
        "peak_level_db": -20,
        "dynamic_range_db": 20,
        "mood": "Balanced Bhakti",
        "mood_hi": "संतुलित भक्ति संगीत",
        "is_vocal_likely": True,
        "target_audience": "General",
        "target_audience_hi": "सभी के लिए",
    }


def detect_target_audience(song_name, analysis=None):
    """
    गाने के नाम से पहचानना कि यह गाना किसके लिए है:
    - भगवान/देवी-देवता (Krishna, Radha, God, Bhagwan, Devi, Maa, Laxmi, Durga, Shiva, Ram)
    - महिलाएं (Women, Mahila, Stree, Beti, Daughter, Sister)
    - पुरुष (Men, Purush, Mard, Yuva, Boy, Brother)
    - भक्त (Bhakta, Devotee, Sharanagat, Sevak)
    - सामान्य (सभी के लिए)
    """
    name_lower = song_name.lower()

    # भगवान / देवता कीवर्ड्स
    god_keywords = [
        "krishna", "कृष्ण", "radha", "राधा", "god", "भगवान", "bhagwan",
        "devi", "देवी", "maa", "maa", "मां", "laxmi", "लक्ष्मी", "durga",
        "दुर्गा", "shiva", "शिव", "ram", "राम", "hanuman", "हनुमान",
        "vishnu", "विष्णु", "ganesha", "गणेश", "sai", "साई", "divine",
        "दिव्य", "bhakti", "भक्ति", "bhajan", "भजन", "aarti", "आरती",
        "kirtan", "कीर्तन", "murli", "मुरली", "bansuri", "बाँसुरी",
        "flute", "बांसुरी", "vrindavan", "वृंदावन", "yamuna", "यमुना",
        "gopal", "गोपाल", "mohan", "मोहन", "hari", "हरि", "narayan",
        "नारायण", "govind", "गोविंद", "shyam", "श्याम"
    ]

    # महिलाओं कीवर्ड्स
    women_keywords = [
        "women", "महिला", "mahila", "stree", "स्त्री", "beti", "बेटी",
        "daughter", "बेटी", "sister", "बहन", "bahen", "mother", "माँ",
        "maata", "माता", "girl", "लड़की", "ladki", "wife", "पत्नी",
        "patni", "ladki", "लड़की", "female", "महिला"
    ]

    # पुरुषों कीवर्ड्स
    men_keywords = [
        "men", "पुरुष", "purush", "mard", "मर्द", "yuva", "युवा",
        "boy", "लड़का", "ladka", "brother", "भाई", "bhai", "husband",
        "पति", "pati", "male", "पुरुष", "man", "आदमी", "aadmi"
    ]

    # भक्त कीवर्ड्स
    bhakta_keywords = [
        "bhakta", "भक्त", "devotee", "शरणागत", "sharanagat", "sevak",
        "सेवक", "sevika", "सेविका", "worshiper", "poojari", "पुजारी",
        "sadhak", "साधक", "sadhika", "साधिका"
    ]

    for kw in god_keywords:
        if kw in name_lower:
            return "God", "भगवान के लिए"

    for kw in women_keywords:
        if kw in name_lower:
            return "Women", "महिलाओं के लिए"

    for kw in men_keywords:
        if kw in name_lower:
            return "Men", "पुरुषों के लिए"

    for kw in bhakta_keywords:
        if kw in name_lower:
            return "Bhakta", "भक्तों के लिए"

    return "General", "सभी के लिए"


def get_mood_colors(mood):
    """मूड के हिसाब से थंबनेल के ग्रेडिएंट रंग"""
    color_map = {
        "Peaceful Meditative": {
            "bg1": "#0B0E14",   # गहरा नीला-काला
            "bg2": "#1A2332",   # मध्यम नीला
            "accent": "#4FC3F7", # हल्का नीला
            "text_main": "#FFE600", # पीला
            "text_sub": "#BBDEFB",  # हल्का नीला सफेद
        },
        "Energetic Devotional": {
            "bg1": "#1B0B0E",   # गहरा लाल-काला
            "bg2": "#4A1414",   # गहरा लाल
            "accent": "#FF5252", #bright red
            "text_main": "#FFD700", # सोना
            "text_sub": "#FFCDD2",  # हल्का लाल सफेद
        },
        "Romantic Soft": {
            "bg1": "#140B1B",   # गहरा बैंगनी
            "bg2": "#3D1B4A",   # मध्यम बैंगनी
            "accent": "#CE93D8", # हल्का बैंगनी
            "text_main": "#F8BBE0", # गुलाबी
            "text_sub": "#F3E5F5",  # बहुत हल्का बैंगनी
        },
        "Short Devotional": {
            "bg1": "#0B1E0B",   # गहरा हरा
            "bg2": "#1B4A1B",   # मध्यम हरा
            "accent": "#69F0AE", # हल्का हरा
            "text_main": "#A5D6A7", # हल्का हरा
            "text_sub": "#C8E6C9",  # बहुत हल्का हरा
        },
        "Balanced Bhakti": {
            "bg1": "#0B0E14",
            "bg2": "#1A2332",
            "accent": "#FFD700",
            "text_main": "#FFE600",
            "text_sub": "#BBDEFB",
        },
    }
    return color_map.get(mood, color_map["Balanced Bhakti"])


def generate_hook_text(song_name, mood, target_audience, target_audience_hi):
    """
    क्लिक करवाने वाला हुक टेक्स्ट बनाना (थंबनेल पर बड़ा लिखा होगा)
    मूड और टारगेट ऑडियंस के हिसाब से
    """
    # मूड के हिसाब से हुक
    mood_hooks = {
        "Peaceful Meditative": [
            "मन को शांति मिलेगी 🧘‍♂️",
            "गहरी शांति का अनुभव 🌸",
            "ध्यान के लिए सर्वश्रेष्ठ 🙏",
            "तनाव दूर करें तुरंत 🕊️",
        ],
        "Energetic Devotional": [
            "भक्ति की ऊर्जा से भर दें ⚡",
            "पूजा के लिए बेस्ट 🪘",
            "ऊर्जावान भक्ति संगीत 🔥",
            "रोमांचकारी भक्ति 🎺",
        ],
        "Romantic Soft": [
            "प्रेम में डूब जाएंगे 💕",
            "कोमल भक्ति रस 🌹",
            "श्री कृष्ण के प्रेम में 💖",
            "मोहक भक्ति गीत ✨",
        ],
        "Short Devotional": [
            "छोटा लेकिन प्रभावशाली ⏱️",
            "जल्दी मन को छू लेगा ⚡",
            "लघु भक्ति संगीत 🪷",
            "तुरंत शांति पाएं 🕉️",
        ],
        "Balanced Bhakti": [
            "संतुलित भक्ति संगीत 🪷",
            "हर अवसर के लिए 🙏",
            "श्री कृष्ण का आशीर्वाद 🌸",
            "दिव्य भक्ति अनुभव ✨",
        ],
    }

    # टारगेट ऑडियंस के हिसाब से हुक
    audience_hooks = {
        "God": [
            "श्री कृष्ण के लिए 🙏",
            "भगवान को समर्पित 🪷",
            "दिव्य भक्ति गीत 🕉️",
            "कृपा पाएं तुरंत ✨",
        ],
        "Women": [
            "महिलाओं के लिए विशेष 🌸",
            "हर महिला को पसंद आएगा 💖",
            "महिलाओं के लिए भक्ति 🎵",
            "नारी शक्ति को समर्पित 💪",
        ],
        "Men": [
            "पुरुषों के लिए विशेष 💪",
            "हर पुरुष को पसंद आएगा 🔥",
            "पुरुषों के लिए भक्ति 🎺",
            "पुरुष शक्ति को समर्पित ⚡",
        ],
        "Bhakta": [
            "भक्तों के लिए सर्वश्रेष्ठ 🙏",
            "हर भक्त को पसंद आएगा 🪷",
            "भक्ति रस में डूबें 🕉️",
            "भक्तों के लिए समर्पित ✨",
        ],
        "General": [
            "सभी के लिए 🎵",
            "हर किसी को पसंद आएगा 🌸",
            "सर्वश्रेष्ठ भक्ति संगीत 🙏",
            "अभी सुनें फ्री में ✨",
        ],
    }

    # रैंडम हुक चुनना (मूड से)
    import random
    mood_hook_list = mood_hooks.get(mood, mood_hooks["Balanced Bhakti"])
    audience_hook_list = audience_hooks.get(target_audience, audience_hooks["General"])

    # हुक बनाना: टारगेट ऑडियंस हुक + मूड हुक
    hook = random.choice(audience_hook_list) + " | " + random.choice(mood_hook_list)
    return hook


def generate_title_from_analysis(song_name, mood):
    """मूड के हिसाब से टाइटल सुझाना"""
    mood_titles = {
        "Peaceful Meditative": f"{song_name} | शांत ध्यान संगीत | Krishna Vibez 🪷",
        "Energetic Devotional": f"{song_name} | ऊर्जावान भक्ति संगीत | Krishna Vibez 🪷",
        "Romantic Soft": f"{song_name} | मुलायम भक्ति गीत | Krishna Vibez 🪷",
        "Short Devotional": f"{song_name} | लघु भक्ति संगीत | Krishna Vibez 🪷",
        "Balanced Bhakti": f"{song_name} | संतुलित भक्ति संगीत | Krishna Vibez 🪷",
    }
    return mood_titles.get(mood, mood_titles["Balanced Bhakti"])


def generate_description_from_analysis(song_name, mood_hi, mood):
    """मूड के हिसाब से डिस्क्रिप्शन लिखना"""
    mood_meaning = {
        "Peaceful Meditative": "यह गीत मन को शांति और गहरी एकाग्रता प्रदान करता है। ध्यान, योग और मन की शांति के लिए आदर्श है।",
        "Energetic Devotional": "यह गीत भक्ति की ऊर्जा और उत्साह से भर देता है। पूजा, आरती और धार्मिक आयोजनों के लिए उपयुक्त है।",
        "Romantic Soft": "यह गीत श्री कृष्ण के दिव्य प्रेम को व्यक्त करता है। कोमल भाव और भक्ति रस से ओत-प्रोत है।",
        "Short Devotional": "यह एक छोटा लेकिन प्रभावशाली भक्ति गीत है जो जल्दी ही मन को छू लेता है।",
        "Balanced Bhakti": "यह गीत भक्ति और संतुलन का सुंदर संगम है जो हर अवसर के लिए उपयुक्त है।",
    }
    meaning = mood_meaning.get(mood, mood_meaning["Balanced Bhakti"])

    description = (
        f"🎵 {song_name}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🪷 दिव्य भक्ति संगीत | Divine Krishna Song\n"
        f"🎭 मूड: {mood_hi}\n\n"
        "📖 भावार्थ:\n"
        f"{meaning}\n\n"
        "✨ English Summary:\n"
        "A divine Krishna bhakti song dedicated to Lord Krishna. "
        "Listen for peace, devotion, and spiritual bliss.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🕊️ हमसे जुड़ें:\n"
        "🌐 आधिकारिक वेबसाइट: https://krishnavibez.in/\n"
        "▶️ आधिकारिक YouTube चैनल: https://www.youtube.com/@KrishnaVibezMusic\n"
        "📲 WhatsApp चैनल: https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J\n"
        "🕊️ Telegram चैनल: https://t.me/krishnavibezz\n"
        "📸 Instagram: https://www.instagram.com/krishnavibez/\n"
        "🧵 Threads: https://www.threads.net/@krishnavibez\n"
        "📘 Facebook पेज: https://www.facebook.com/1808917602588221\n"
        "📌 Pinterest: https://in.pinterest.com/MojiloMart/\n\n"
        "🛍️ Divine Recommendations (Amazon Storefront):\n"
        "👉 Explore our Amazon Store: https://www.amazon.in/shop/myhappybirthday\n"
        "(Disclaimer: As an Amazon Associate, Krishna Vibez earns from qualifying purchases.)\n\n"
        "जय श्री राधे कृष्ण! 🪷✨\n\n"
        "#Krishna #Bhakti #KrishnaVibez #KrishnaSong #DivineMusic #RadheKrishna #HindiBhajan"
    )
    return description


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        result = analyze_audio_mood(file_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: python audio_analyzer.py <audio_file_path>")
