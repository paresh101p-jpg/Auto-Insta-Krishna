"""
Automated YouTube Shorts & Reel Generator for Lord Krishna Quotes
- Emotion-Adaptive Humanized Voiceover Engine
- Dynamic Focus-Reveal Unblur Hook (0 to 3.5s)
- Anti-Crop Blurred Ambient Background (1080x1920 Full HD)
- Studio Mastered Audio with Divine Flute BGM
"""

import asyncio
import os
import sys
import glob
import random
import subprocess
import edge_tts

# UTF-8 Encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(BASE_DIR, "music")
QUOTES_FILE = os.path.join(BASE_DIR, "quotes.txt")
USED_QUOTES_FILE = os.path.join(BASE_DIR, "used_quotes.txt")
FFMPEG_PATH = r"C:\Users\Admin\.antigravity-ide\extensions\kilocode.kilo-code-7.8.12-win32-x64\bin\ffmpeg.exe"

def detect_thought_emotion(text):
    """
    Analyzes the Hindi text and detects the emotional delivery style.
    Returns: 'struggle_victory', 'karma_strength', 'peace_meditation', 'devotion_love', or 'deep_wisdom'
    """
    struggle_words = ["कठिन", "शुरुआत", "उलझा", "बदलाव", "हार", "दर्द", "संघर्ष", "धैर्य", "समय", "परीक्षा", "विपत्ति"]
    karma_words = ["कर्म", "साहस", "कर्तव्य", "लक्ष्य", "मेहनत", "सामर्थ्य", "शक्ति", "सफलता", "कर्मण्येवाधिकारस्ते"]
    peace_words = ["शांत", "शांति", "मौन", "क्रोध", "आत्मा", "ध्यान", "ईश्वर", "परमात्मा", "विवेक", "संयम"]
    devotion_words = ["प्रेम", "भक्ति", "राधे", "विश्वास", "समर्पण", "कृपा", "गोविंद", "माधव", "आनंद"]
    
    # Check for contrast pattern (struggle -> resolution)
    if any(w in text for w in struggle_words) and any(w in text for w in ["अंत", "अच्छा", "जीत", "सुकून", "सफलता"]):
        return "struggle_victory"
    elif any(w in text for w in karma_words):
        return "karma_strength"
    elif any(w in text for w in peace_words):
        return "peace_meditation"
    elif any(w in text for w in devotion_words):
        return "devotion_love"
    else:
        return "deep_wisdom"

async def synthesize_adaptive_voice(text, output_mp3_path):
    """
    Synthesizes soulful Hindi narration automatically adapted to the emotion of the thought.
    """
    emotion = detect_thought_emotion(text)
    print(f"Detected Thought Emotion: [{emotion.upper()}]")
    
    temp_dir = os.path.dirname(output_mp3_path)
    
    if emotion == "struggle_victory":
        # Split into contrast phrases if possible
        # e.g., "बदलाव शुरुआत में सबसे कठिन, बीच में सबसे उलझा हुआ और अंत में सबसे अच्छा लगता है"
        parts = []
        if "कठिन" in text or "उलझा" in text:
            # Multi-stage contrast delivery
            # 1. Beginning struggle
            # 2. Transition
            # 3. Joyful resolution
            clauses = [c.strip() for c in text.replace("।", ",").split(",") if c.strip()]
            if len(clauses) >= 2:
                # Stage 1: Struggle (slow, deep)
                p1_file = os.path.join(temp_dir, "_part1.mp3")
                c1 = edge_tts.Communicate(clauses[0] + "...", voice="hi-IN-MadhurNeural", rate="-12%", pitch="-2Hz")
                await c1.save(p1_file)
                parts.append(p1_file)
                
                # Middle stages
                for i, cl in enumerate(clauses[1:-1]):
                    pm_file = os.path.join(temp_dir, f"_part_mid_{i}.mp3")
                    cm = edge_tts.Communicate(cl + "...", voice="hi-IN-MadhurNeural", rate="-10%", pitch="-1Hz")
                    await cm.save(pm_file)
                    parts.append(pm_file)
                
                # Final stage: Joyful resolution (uplifting)
                p_end_file = os.path.join(temp_dir, "_part_end.mp3")
                cend = edge_tts.Communicate(clauses[-1] + "!", voice="hi-IN-MadhurNeural", rate="-6%", pitch="+1Hz")
                await cend.save(p_end_file)
                parts.append(p_end_file)
                
                # Concat parts
                inputs = []
                for p in parts:
                    inputs.extend(["-i", p])
                filter_str = "".join([f"[{i}:a]" for i in range(len(parts))]) + f"concat=n={len(parts)}:v=0:a=1[a]"
                cmd = [FFMPEG_PATH, "-y"] + inputs + ["-filter_complex", filter_str, "-map", "[a]", "-c:a", "libmp3lame", "-q:a", "2", output_mp3_path]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return
    
    # Standard Adaptive Delivery based on emotion category
    if emotion == "karma_strength":
        rate = "-9%"
        pitch = "-1Hz"
    elif emotion == "peace_meditation":
        rate = "-13%"
        pitch = "-2Hz"
    elif emotion == "devotion_love":
        rate = "-8%"
        pitch = "+0Hz"
    else:  # deep_wisdom
        rate = "-10%"
        pitch = "-1Hz"
        
    # Natural breathing pause insertion at commas and clauses
    formatted_text = text.replace(",", "... ").replace("।", "... ").replace(";", "... ")
    if not formatted_text.endswith("..."):
        formatted_text += "..."
        
    try:
        c = edge_tts.Communicate(formatted_text, voice="hi-IN-MadhurNeural", rate=rate, pitch=pitch)
        await c.save(output_mp3_path)
    except Exception as ex:
        print(f"Warning: edge_tts ({ex}), retrying with default params...", flush=True)
        c = edge_tts.Communicate(formatted_text, voice="hi-IN-MadhurNeural")
        await c.save(output_mp3_path)

def get_audio_duration(file_path):
    cmd = [FFMPEG_PATH, "-i", file_path]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    for line in result.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h)*3600 + float(m)*60 + float(s)
    return 16.0

def get_random_flute_bgm():
    if os.path.exists(MUSIC_DIR):
        mp3s = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
        if mp3s:
            return random.choice(mp3s)
    return None

def build_reel(image_path, quote_text, output_video_path, bgm_path=None):
    """
    Builds the complete vertical 9:16 reel:
    1. Emotion-adaptive voice
    2. Blurred ambient background (0% cropped)
    3. Dynamic Focus-Reveal unblur hook (0 to 3.5s)
    4. Lord Krishna flute BGM softly mixed at 14%
    """
    temp_dir = os.path.dirname(output_video_path) or "."
    voice_mp3 = os.path.join(temp_dir, "temp_adaptive_voice.mp3")
    
    # 1. Generate Voice
    asyncio.run(synthesize_adaptive_voice(quote_text, voice_mp3))
    voice_dur = get_audio_duration(voice_mp3)
    print(f"Generated Voice Duration: {voice_dur:.2f} seconds")
    
    start_delay = 0.7  # 700ms flute intro before speech
    total_dur = voice_dur + start_delay + 1.8
    total_dur_str = f"{total_dur:.2f}"
    fade_out_start = f"{total_dur - 1.5:.2f}"
    
    # 2. Select Music
    if not bgm_path:
        bgm_path = get_random_flute_bgm()
    print(f"Using Flute Track: {os.path.basename(bgm_path) if bgm_path else 'None'}")
    
    # 3. Build FFmpeg Filter Graph
    filter_complex = (
        # Blurred background (fills 1080x1920)
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"boxblur=25:5,eq=brightness=-0.09:saturation=1.15[bg];"
        
        # Foreground sharp (fitted uncropped)
        f"[0:v]scale=1040:1750:force_original_aspect_ratio=decrease,"
        f"pad=w=1044:h=ih+4:x=2:y=2:color=black@0.4,split=2[fg_sharp1][fg_sharp2];"
        
        # Foreground blurred version
        f"[fg_sharp1]boxblur=22:4[fg_blurred];"
        
        # Dynamic unblur focus reveal (0 to 3.5s)
        f"[fg_blurred][fg_sharp2]blend=all_expr='if(lte(T,3.5), A*(1-T/3.5) + B*(T/3.5), B)'[fg_dynamic];"
        
        # Overlay centered
        f"[bg][fg_dynamic]overlay=(W-w)/2:(H-h)/2[v];"
        
        # Audio mastering: studio warmth, natural delay, room ambiance
        f"[1:a]adelay=700|700,bass=g=3:f=160,treble=g=2:f=3200,aecho=0.8:0.7:30:0.10,volume=1.15[master_voice];"
        f"[2:a]volume=0.14,afade=t=out:st={fade_out_start}:d=1.5[bgm];"
        f"[master_voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
    )
    
    cmd = [
        FFMPEG_PATH, "-y",
        "-loop", "1", "-i", image_path,
        "-i", voice_mp3,
        "-i", bgm_path,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
        "-t", total_dur_str,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        output_video_path
    ]
    
    print(f"Rendering Reel: {output_video_path}...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0:
        print(f"SUCCESS: Created {output_video_path} ({os.path.getsize(output_video_path)/(1024*1024):.2f} MB)")
        return True
    else:
        print("FFmpeg Error:", res.stderr[-500:])
        return False

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        img = sys.argv[1]
        quote = sys.argv[2]
        out = sys.argv[3] if len(sys.argv) > 3 else "output_reel.mp4"
        build_reel(img, quote, out)
    else:
        print("Usage: python generate_reels.py <image_path> <quote_text> [output_path]")
