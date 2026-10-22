"""
Master Automated YouTube Shorts & Reel Generator for Lord Krishna Quotes
- 15 Rotating Distinct Voices across Men, Women, Boy, Girl, Baby/Kid (Sarvam AI, Google Cloud Neural2, Edge-TTS)
- 15 Rotating Cinematic Visual Effects & Lighting Profiles
- Dynamic Focus-Reveal Unblur Hook (0 to 2.0s) for 100% sharp YouTube thumbnails
- Anti-Crop Blurred Ambient Background (1080x1920 Full HD)
- Studio Mastered Audio with Divine Flute BGM (35% volume with 1.5s fade out)
"""

import asyncio
import os
import sys
import glob
import random
import subprocess
import json
import base64
import requests

# UTF-8 Encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(BASE_DIR, "music")
QUOTES_FILE = os.path.join(BASE_DIR, "quotes.txt")
USED_QUOTES_FILE = os.path.join(BASE_DIR, "used_quotes.txt")
local_ffmpeg = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
FFMPEG_PATH = local_ffmpeg if os.path.exists(local_ffmpeg) else "ffmpeg"
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "google_tts_service_account.json")
SARVAM_KEY_FILE = os.path.join(BASE_DIR, "sarvam_key.txt")
TRACKER_FILE = os.path.join(BASE_DIR, "gcloud_usage_tracker.json")

# 15 Rotating Cinematic Visual Effects & Color Profiles
CINEMATIC_COLOR_PROFILES = [
    {
        "name": "1. Dynamic Unblur Focus-Reveal",
        "filter": "eq=brightness=0.01:saturation=1.15:contrast=1.06"
    },
    {
        "name": "2. Divine Golden Sunrise (स्वर्ण प्रभात)",
        "filter": "colorbalance=rs=0.12:gs=0.06:bs=-0.10:rm=0.08:gm=0.04:bm=-0.06,eq=saturation=1.20:contrast=1.08"
    },
    {
        "name": "3. Sacred Saffron Sunset (संध्या भगवा आभा)",
        "filter": "colorbalance=rs=0.18:gs=-0.02:bs=-0.15:rm=0.12:gm=-0.02:bm=-0.10,eq=saturation=1.24:contrast=1.08"
    },
    {
        "name": "4. Vrindavan Divine Garden (वृंदावन कुंज आभा)",
        "filter": "colorbalance=rs=-0.03:gs=0.10:bs=-0.04:rm=-0.02:gm=0.08:bm=-0.03,eq=saturation=1.18:contrast=1.06"
    },
    {
        "name": "5. Cinematic HDR Vivid (क्रिस्टल क्लियर HDR)",
        "filter": "eq=brightness=-0.01:saturation=1.28:contrast=1.14"
    },
    {
        "name": "6. Yamuna Moonlit Glow (यमुना तट चंद्रकांति नीलिमा)",
        "filter": "colorbalance=rs=-0.08:gs=0.02:bs=0.12:rm=-0.05:gm=0.02:bm=0.10,eq=saturation=1.15:contrast=1.08"
    },
    {
        "name": "7. Cinematic Vignette Spotlight (गंभीर आध्यात्मिक फोकस)",
        "filter": "vignette=PI/4.5,eq=contrast=1.10:saturation=1.14"
    },
    {
        "name": "8. Divine Warm Glow (मधुर भक्ति कांति)",
        "filter": "eq=gamma_r=1.12:gamma_g=1.04:gamma_b=0.92:contrast=1.10:saturation=1.20"
    },
    {
        "name": "9. Sacred Vedic Parchment (प्राचीन वेद ग्रंथ)",
        "filter": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,eq=contrast=1.08:brightness=-0.01"
    },
    {
        "name": "10. Breathing Divine Pulse (सांस लेता हुआ दिव्य प्रकाश)",
        "filter": "eq=brightness='0.03*sin(2*PI*t/3.5)':contrast=1.08:saturation=1.16"
    },
    {
        "name": "11. Radiant Gold Shimmer (स्वर्णिम चमक)",
        "filter": "colorbalance=rs=0.14:gs=0.08:bs=-0.08,eq=brightness=0.02:contrast=1.10:saturation=1.22"
    },
    {
        "name": "12. Serene Ashram Dusk (शांत आश्रम गोधूलि)",
        "filter": "colorbalance=rs=0.10:gs=0.02:bs=0.06:rm=0.06:gm=0.01:bm=0.04,eq=saturation=1.16:contrast=1.07"
    },
    {
        "name": "13. White Angelic Flash-In (दिव्य ज्योति प्रकाश)",
        "filter": "fade=t=in:st=0:d=1.5:color=white,eq=saturation=1.18:contrast=1.08"
    },
    {
        "name": "14. Deep Soulful High-Contrast (गहन ध्यान मुद्रा)",
        "filter": "eq=contrast=1.20:saturation=1.10:brightness=-0.02"
    },
    {
        "name": "15. Morning Dew Bloom (प्रातःकालीन अमृत बेला)",
        "filter": "colorbalance=rs=0.04:gs=0.06:bs=0.02,eq=brightness=0.02:contrast=1.07:saturation=1.18"
    }
]

# 15 Rotating Diverse Voice Profiles (Men, Women, Boy, Girl, Baby/Kid)
VOICE_PROFILES = [
    # Category 1: Men (पुरुष - गंभीर / भक्ति / प्रवचन)
    {"engine": "sarvam", "speaker": "girish_hi_devotional", "pace": 0.92, "name": "Men - Girish (Devotional Guru)"},
    {"engine": "sarvam", "speaker": "ratan_hi_devotional", "pace": 0.92, "name": "Men - Ratan (Deep Spiritual)"},
    {"engine": "sarvam", "speaker": "ashok_hi_character", "pace": 0.93, "name": "Men - Ashok (Vedic Rishi)"},
    {"engine": "gcloud", "voice": "hi-IN-Neural2-B", "rate": "0.90", "pitch": "-2st", "name": "Men - Google Neural2-B (Baritone)"},
    {"engine": "gcloud", "voice": "hi-IN-Wavenet-C", "rate": "0.90", "pitch": "-2st", "name": "Men - Google Wavenet-C (Classical)"},

    # Category 2: Women (महिला - शांत / भक्तिमय / अमृतवाणी)
    {"engine": "sarvam", "speaker": "ishita_hi_devotional", "pace": 0.94, "name": "Women - Ishita (Devotional)"},
    {"engine": "sarvam", "speaker": "roopa_hi_narration", "pace": 0.94, "name": "Women - Roopa (Peaceful Soul)"},
    {"engine": "edge", "voice": "hi-IN-SwaraNeural", "rate": "-6%", "pitch": "+0Hz", "name": "Women - Swara (Sweet Devotion)"},
    {"engine": "gcloud", "voice": "hi-IN-Neural2-A", "rate": "0.92", "pitch": "-1st", "name": "Women - Google Neural2-A (Graceful)"},

    # Category 3: Boy (युवा बालक - कथावाचक / प्रेरणा)
    {"engine": "sarvam", "speaker": "shubh_hi_devotional", "pace": 0.93, "name": "Boy - Shubh (Emotional Storyteller)"},
    {"engine": "sarvam", "speaker": "aayan_hi_conversational", "pace": 0.94, "name": "Boy - Aayan (Expressive Youth)"},
    {"engine": "edge", "voice": "hi-IN-MadhurNeural", "rate": "-6%", "pitch": "-1Hz", "name": "Boy - Madhur (Inspiring Youth)"},

    # Category 4: Girl (युवती / कन्या - सौम्य / कोमल स्वर)
    {"engine": "sarvam", "speaker": "kavya_hi_conversational", "pace": 0.95, "name": "Girl - Kavya (Melodious & Gentle)"},
    {"engine": "sarvam", "speaker": "tanya_hi_narration", "pace": 0.94, "name": "Girl - Tanya (Calm & Reflective)"},

    # Category 5: Baby / Kid (बाल गोपाल / नन्हा बालक स्वर)
    {"engine": "sarvam", "speaker": "kunal_hi_kids", "pace": 0.96, "name": "Baby/Kid - Kunal (Bal Gopal Voice)"},
    {"engine": "sarvam", "speaker": "chhavi_hi_kids", "pace": 0.96, "name": "Baby/Kid - Chhavi (Sweet Child Voice)"}
]

# ----------------- CREDENTIALS & QUOTA -----------------
MAX_MONTHLY_CHARS = 800000

def get_sarvam_key():
    if os.path.exists(SARVAM_KEY_FILE):
        try:
            with open(SARVAM_KEY_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            pass
    return None

def get_monthly_char_usage():
    if not os.path.exists(TRACKER_FILE):
        return 0
    try:
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            from datetime import datetime
            current_month = datetime.now().strftime("%Y-%m")
            return data.get(current_month, 0)
    except:
        return 0

def add_char_usage(char_count):
    from datetime import datetime
    current_month = datetime.now().strftime("%Y-%m")
    data = {}
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {}
    data[current_month] = data.get(current_month, 0) + char_count
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_gcloud_access_token():
    try:
        from google.oauth2 import service_account
        import google.auth.transport.requests
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=scopes
        )
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return credentials.token
    except Exception as e:
        print(f"Warning: Google Cloud token error: {e}", flush=True)
        return None

def synthesize_sarvam_voice(text, speaker, pace, out_path):
    sarvam_key = get_sarvam_key()
    if not sarvam_key:
        return False
    url = "https://api.sarvam.ai/text-to-speech"
    headers = {"api-subscription-key": sarvam_key, "Content-Type": "application/json"}
    payload = {
        "inputs": [text],
        "target_language_code": "hi-IN",
        "speaker": speaker,
        "pitch": 0,
        "pace": pace,
        "loudness": 1.5,
        "speech_sample_rate": 22050,
        "enable_preprocessing": True,
        "model": "bulbul:v4-flash"
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=20)
        if r.status_code == 200:
            audio_b64 = r.json()["audios"][0]
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            return True
        else:
            print(f"Sarvam API status {r.status_code}: {r.text}", flush=True)
            return False
    except Exception as e:
        print(f"Sarvam exception: {e}", flush=True)
        return False

def synthesize_gcloud_voice(text, voice_name, rate, pitch, out_path):
    usage = get_monthly_char_usage()
    if usage + len(text) > MAX_MONTHLY_CHARS:
        print(f"Warning: Google Cloud quota limit approached ({usage} chars).", flush=True)
        return False

    token = get_gcloud_access_token()
    if not token:
        return False

    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}

    clean_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    spaced = clean_text.replace('।', '। <break time="450ms"/> ').replace('|', '| <break time="450ms"/> ')
    ssml = f"<speak><prosody rate='{rate}' pitch='{pitch}'>{spaced}</prosody></speak>"

    payload = {
        "input": {"ssml": ssml},
        "voice": {"languageCode": "hi-IN", "name": voice_name, "ssmlGender": "MALE" if "B" in voice_name or "C" in voice_name else "FEMALE"},
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": 0.92}
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        if res.status_code == 200:
            audio_content = res.json().get("audioContent")
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(audio_content))
            add_char_usage(len(text))
            return True
        else:
            print(f"Google Cloud TTS returned status {res.status_code}: {res.text}", flush=True)
            return False
    except Exception as e:
        print(f"Google Cloud TTS exception: {e}", flush=True)
        return False

async def synthesize_edge_tts(text, voice_name, rate, pitch, out_path):
    import edge_tts
    comm = edge_tts.Communicate(text, voice=voice_name, rate=rate, pitch=pitch)
    await comm.save(out_path)

def synthesize_any_voice(text, out_path, voice_idx=0):
    """Synthesizes voice using the selected voice profile with automatic fallback."""
    v_profile = VOICE_PROFILES[voice_idx % len(VOICE_PROFILES)]
    engine = v_profile["engine"]
    v_name = v_profile["name"]
    print(f"  Voice Profile: {v_name}", flush=True)

    success = False
    if engine == "sarvam":
        success = synthesize_sarvam_voice(text, v_profile["speaker"], v_profile["pace"], out_path)
    elif engine == "gcloud":
        success = synthesize_gcloud_voice(text, v_profile["voice"], v_profile["rate"], v_profile["pitch"], out_path)
    elif engine == "edge":
        try:
            asyncio.run(synthesize_edge_tts(text, v_profile["voice"], v_profile["rate"], v_profile["pitch"], out_path))
            success = os.path.exists(out_path) and os.path.getsize(out_path) > 1000
        except Exception as e:
            print(f"Edge-TTS error: {e}", flush=True)
            success = False

    # Fallback to Edge-TTS Madhur if primary failed
    if not success or not os.path.exists(out_path) or os.path.getsize(out_path) < 1000:
        print("  Notice: Primary voice failed, using Edge-TTS Madhur fallback...", flush=True)
        try:
            asyncio.run(synthesize_edge_tts(text, "hi-IN-MadhurNeural", "-6%", "-1Hz", out_path))
            success = os.path.exists(out_path) and os.path.getsize(out_path) > 1000
        except Exception as e:
            print(f"Fallback error: {e}", flush=True)
            return False

    return success

def get_audio_duration(file_path):
    cmd = [FFMPEG_PATH, "-i", file_path]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    for line in result.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h)*3600 + float(m)*60 + float(s)
    return 14.0

def get_random_flute_bgm():
    if os.path.exists(MUSIC_DIR):
        mp3s = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
        if mp3s:
            return random.choice(mp3s)
    return None

def build_reel(image_path, quote_text, output_video_path, bgm_path=None, color_profile_idx=0, voice_idx=0):
    """
    Builds the complete vertical 9:16 reel:
    1. Rotating Diverse Voices (Men, Women, Boy, Girl, Baby/Kid)
    2. Rotating 15 Cinematic Color Grading & Lighting profiles
    3. Blurred ambient background (0% cropped)
    4. Dynamic Focus-Reveal unblur hook (0 to 2.0s for sharp thumbnails)
    5. Lord Krishna flute BGM softly mixed at 35% with 1.5s fade out
    6. Minimum 11.5s total duration (strictly 10+ seconds)
    """
    temp_dir = os.path.dirname(output_video_path) or "."
    voice_file = os.path.join(temp_dir, f"_temp_voice_{os.path.basename(output_video_path)}.wav")

    # 1. Synthesize Voice
    success = synthesize_any_voice(quote_text, voice_file, voice_idx=voice_idx)
    if not success:
        return False

    voice_dur = get_audio_duration(voice_file)
    start_delay = 0.6  # 600ms divine flute intro before speech
    total_dur = max(11.5, voice_dur + start_delay + 2.5)
    total_dur_str = f"{total_dur:.2f}"
    fade_out_start = f"{total_dur - 1.5:.2f}"
    delay_ms = int(start_delay * 1000)

    # 2. Select Music
    if not bgm_path:
        bgm_path = get_random_flute_bgm()

    # 3. Select Cinematic Color Grading Profile
    profile = CINEMATIC_COLOR_PROFILES[color_profile_idx % len(CINEMATIC_COLOR_PROFILES)]
    color_filter = profile["filter"]
    print(f"  Visual Profile: {profile['name']}", flush=True)

    # 4. Filter Complex:
    # - Blurred background (1080x1920)
    # - Foreground uncropped with subtle shadow border
    # - Dynamic unblur (0 to 2.0s)
    # - Visual color grading & lighting filter
    # - Mastered audio mix
    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"boxblur=25:5,eq=brightness=-0.09:saturation=1.15[bg];"
        f"[0:v]scale=1040:1750:force_original_aspect_ratio=decrease,"
        f"pad=w=1044:h=ih+4:x=2:y=2:color=black@0.4,split=2[fg_sharp1][fg_sharp2];"
        f"[fg_sharp1]boxblur=22:4[fg_blurred];"
        f"[fg_blurred][fg_sharp2]blend=all_expr='if(lte(T,2.0), A*(1-T/2.0) + B*(T/2.0), B)'[fg_dynamic];"
        f"[bg][fg_dynamic]overlay=(W-w)/2:(H-h)/2,{color_filter}[v];"
        f"[1:a]adelay={delay_ms}|{delay_ms},highpass=f=80,equalizer=f=300:t=q:w=1.2:g=-2.0,equalizer=f=3400:t=q:w=1.5:g=2.5,compand=attacks=0.03:decays=0.25:points=-60/-60|-24/-10|0/-2:soft-knee=6,aecho=0.8:0.6:28:0.11,volume=1.20[master_voice];"
        f"[2:a]volume=0.35,afade=t=out:st={fade_out_start}:d=1.5[bgm];"
        f"[master_voice][bgm]amix=inputs=2:duration=longest:dropout_transition=0,volume=2.0[a]"
    )

    cmd = [
        FFMPEG_PATH, "-y",
        "-loop", "1", "-i", image_path,
        "-i", voice_file,
        "-i", bgm_path,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
        "-t", total_dur_str,
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_video_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(voice_file):
            try:
                os.remove(voice_file)
            except:
                pass
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode('utf-8', errors='ignore') if e.stderr else e}", flush=True)
        if os.path.exists(voice_file):
            try:
                os.remove(voice_file)
            except:
                pass
        return False
