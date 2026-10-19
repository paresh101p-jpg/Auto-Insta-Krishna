import os
import sys
import asyncio
import subprocess
import json
import base64
import requests
from generate_reels import FFMPEG_PATH

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REELS_OUTPUT_DIR = os.path.join(BASE_DIR, "reels_output")
MUSIC_DIR = os.path.join(BASE_DIR, "music")
os.makedirs(REELS_OUTPUT_DIR, exist_ok=True)

bgm_path = os.path.join(MUSIC_DIR, "echoes_of_lumen-krishna-flute-music-597586.mp3")

with open(os.path.join(BASE_DIR, "sarvam_key.txt"), "r", encoding="utf-8") as f:
    SARVAM_KEY = f.read().strip()

SAMPLES = [
    {
        "file": "sample_cat_1_men.mp4",
        "category": "1. Men (पुरुष - गंभीर प्रवचन)",
        "speaker": "girish_hi_devotional",
        "pace": 0.92,
        "img": "Images/1831.png",
        "quote": "उम्र जाया कर दी लोगों ने औरों के वजूद में नुक्स निकालते-निकालते| इतना ही खुद को तराशा होता तो फ़रिश्ते बन जाते|"
    },
    {
        "file": "sample_cat_2_women.mp4",
        "category": "2. Women (महिला - शांत भक्तिमय)",
        "speaker": "ishita_hi_devotional",
        "pace": 0.95,
        "img": "Images/1833.png",
        "quote": "शुरू करने के लिए महान होना जरूरी नहीं, लेकिन महान बनने के लिए शुरू करना जरूरी है।"
    },
    {
        "file": "sample_cat_3_boy.mp4",
        "category": "3. Boy (युवा बालक - भावुक कथावाचक)",
        "speaker": "shubh_hi_devotional",
        "pace": 0.94,
        "img": "Images/1832.png",
        "quote": "गीता में स्पष्ट शब्दों में लिखा है, निराश न होना, कमजोर तेरा वक्त है, तू नहीं|"
    },
    {
        "file": "sample_cat_4_girl.mp4",
        "category": "4. Girl (युवती / कन्या - मधुर स्वर)",
        "speaker": "kavya_hi_conversational",
        "pace": 0.95,
        "img": "Images/1835.png",
        "quote": "ठोकर वही शख्स खाता है, जो रास्ते का पत्थर नहीं उठाता|"
    },
    {
        "file": "sample_cat_5_baby_kid.mp4",
        "category": "5. Baby / Kid (बाल गोपाल / नन्हा बालक)",
        "speaker": "kunal_hi_kids",
        "pace": 0.96,
        "img": "Images/1834.png",
        "quote": "धैर्य कड़वा है, लेकिन इसका फल मीठा है।"
    }
]

def synthesize_sarvam(text, speaker, pace, out_wav):
    url = "https://api.sarvam.ai/text-to-speech"
    headers = {"api-subscription-key": SARVAM_KEY, "Content-Type": "application/json"}
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
    r = requests.post(url, json=payload, headers=headers, timeout=20)
    if r.status_code == 200:
        audio_b64 = r.json()["audios"][0]
        with open(out_wav, "wb") as f:
            f.write(base64.b64decode(audio_b64))
        return True
    else:
        print("Sarvam error:", r.text)
        return False

def get_audio_duration(file_path):
    cmd = [FFMPEG_PATH, "-i", file_path]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    for line in result.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h)*3600 + float(m)*60 + float(s)
    return 10.0

def build_category_reel(item):
    out_mp4 = os.path.join(REELS_OUTPUT_DIR, item["file"])
    img_path = os.path.join(BASE_DIR, item["img"])
    temp_voice = os.path.join(BASE_DIR, f"temp_cat_{item['speaker']}.wav")
    
    print(f"\n==========================================")
    print(f"Building {item['category']}...")
    print(f"Quote: {item['quote']}")
    
    ok = synthesize_sarvam(item["quote"], item["speaker"], item["pace"], temp_voice)
    if not ok:
        print("TTS synthesis failed!")
        return
    
    voice_dur = get_audio_duration(temp_voice)
    total_dur = max(voice_dur + 2.5, 9.0)
    total_dur_str = f"{total_dur:.2f}"
    fade_out_start = max(total_dur - 1.5, 0.5)
    
    delay_ms = 600
    
    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"boxblur=25:5,eq=brightness=-0.09:saturation=1.15[bg];"
        f"[0:v]scale=1040:1750:force_original_aspect_ratio=decrease,"
        f"pad=w=1044:h=ih+4:x=2:y=2:color=black@0.4,split=2[fg_sharp1][fg_sharp2];"
        f"[fg_sharp1]boxblur=22:4[fg_blurred];"
        f"[fg_blurred][fg_sharp2]blend=all_expr='if(lte(T,2.0), A*(1-T/2.0) + B*(T/2.0), B)'[fg_dynamic];"
        f"[bg][fg_dynamic]overlay=(W-w)/2:(H-h)/2[v];"
        f"[1:a]adelay={delay_ms}|{delay_ms},highpass=f=80,equalizer=f=300:t=q:w=1.2:g=-2.0,equalizer=f=3400:t=q:w=1.5:g=2.5,compand=attacks=0.03:decays=0.25:points=-60/-60|-24/-10|0/-2:soft-knee=6,aecho=0.8:0.6:28:0.11,volume=1.20[voice];"
        f"[2:a]volume=0.35,afade=t=out:st={fade_out_start}:d=1.5[bgm];"
        f"[voice][bgm]amix=inputs=2:duration=longest:dropout_transition=0,volume=2.0[a]"
    )
    
    cmd = [
        FFMPEG_PATH, "-y",
        "-loop", "1", "-i", img_path,
        "-i", temp_voice,
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
        out_mp4
    ]
    
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.path.exists(temp_voice):
        os.remove(temp_voice)
    print(f"  --> Saved: {out_mp4} ({os.path.getsize(out_mp4)/1024/1024:.2f} MB)")

def main():
    for item in SAMPLES:
        build_category_reel(item)
    print("\nAll category samples created successfully in reels_output folder!")

if __name__ == "__main__":
    main()
