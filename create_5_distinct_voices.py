import os
import sys
import asyncio
import subprocess
import json
import base64
import requests
import edge_tts
from generate_reels import FFMPEG_PATH, get_gcloud_access_token

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REELS_OUTPUT_DIR = os.path.join(BASE_DIR, "reels_output")
MUSIC_DIR = os.path.join(BASE_DIR, "music")

bgm_path = os.path.join(MUSIC_DIR, "echoes_of_lumen-krishna-flute-music-597586.mp3")

SAMPLES = [
    {
        "file": "sample_v1_male_guru.mp4",
        "name": "1. पुरुष गुरु स्वर (Google Neural2-B)",
        "engine": "gcloud",
        "voice": "hi-IN-Neural2-B",
        "rate": "0.90",
        "pitch": "-2st",
        "img": "Images/1831.png",
        "quote": "उम्र जाया कर दी लोगों ने औरों के वजूद में नुक्स निकालते-निकालते| इतना ही खुद को तराशा होता तो फ़रिश्ते बन जाते|"
    },
    {
        "file": "sample_v2_male_deep.mp4",
        "name": "2. भारी गंभीर स्वर (Google Neural2-C)",
        "engine": "gcloud",
        "voice": "hi-IN-Neural2-C",
        "rate": "0.88",
        "pitch": "-3st",
        "img": "Images/1832.png",
        "quote": "गीता में स्पष्ट शब्दों में लिखा है, निराश न होना, कमजोर तेरा वक्त है, तू नहीं|"
    },
    {
        "file": "sample_v3_male_storyteller.mp4",
        "name": "3. कथावाचक स्वर (Google Wavenet-B)",
        "engine": "gcloud",
        "voice": "hi-IN-Wavenet-B",
        "rate": "0.92",
        "pitch": "-1st",
        "img": "Images/1833.png",
        "quote": "शुरू करने के लिए महान होना जरूरी नहीं, लेकिन महान बनने के लिए शुरू करना जरूरी है।"
    },
    {
        "file": "sample_v4_male_classical.mp4",
        "name": "4. शास्त्रीय पारंपरिक स्वर (Google Wavenet-C)",
        "engine": "gcloud",
        "voice": "hi-IN-Wavenet-C",
        "rate": "0.90",
        "pitch": "-2st",
        "img": "Images/1834.png",
        "quote": "धैर्य कड़वा है, लेकिन इसका फल मीठा है।"
    },
    {
        "file": "sample_v5_male_madhur.mp4",
        "name": "5. मधुर युवा स्वर (Microsoft Madhur)",
        "engine": "edge",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-6%",
        "pitch": "-1Hz",
        "img": "Images/1835.png",
        "quote": "ठोकर वही शख्स खाता है, जो रास्ते का पत्थर नहीं उठाता|"
    }
]

def synthesize_gcloud(text, voice_name, rate, pitch, out_mp3):
    token = get_gcloud_access_token()
    clean = text.replace('&', '&amp;').replace('<', '').replace('>', '').replace('"', '&quot;')
    spaced = clean.replace('।', '। <break time="450ms"/> ').replace('|', '| <break time="450ms"/> ')
    ssml = f"<speak><prosody rate='{rate}' pitch='{pitch}'>{spaced}</prosody></speak>"
    
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "input": {"ssml": ssml},
        "voice": {"languageCode": "hi-IN", "name": voice_name, "ssmlGender": "MALE"},
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": 0.92}
    }
    r = requests.post(url, json=payload, headers=headers, timeout=15)
    if r.status_code == 200:
        with open(out_mp3, "wb") as f:
            f.write(base64.b64decode(r.json()["audioContent"]))
        return True
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

async def build_sample_reel(item):
    out_mp4 = os.path.join(REELS_OUTPUT_DIR, item["file"])
    temp_voice = os.path.join(REELS_OUTPUT_DIR, f"_temp_{item['file']}.mp3")
    img_path = os.path.join(BASE_DIR, item["img"])
    
    print(f"\n==========================================")
    print(f"Building {item['name']}...")
    print(f"Quote: {item['quote']}")
    
    if item["engine"] == "gcloud":
        synthesize_gcloud(item["quote"], item["voice"], item["rate"], item["pitch"], temp_voice)
    else:
        comm = edge_tts.Communicate(item["quote"], voice=item["voice"], rate=item["rate"], pitch=item["pitch"])
        await comm.save(temp_voice)
        
    voice_dur = get_audio_duration(temp_voice)
    start_delay = 0.7
    total_dur = max(11.5, voice_dur + start_delay + 2.5)
    total_dur_str = f"{total_dur:.2f}"
    fade_out_start = f"{total_dur - 1.5:.2f}"
    delay_ms = int(start_delay * 1000)
    
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

async def main():
    for item in SAMPLES:
        await build_sample_reel(item)
    print("\nAll 5 distinct voice samples created successfully in reels_output folder!")

if __name__ == "__main__":
    asyncio.run(main())
