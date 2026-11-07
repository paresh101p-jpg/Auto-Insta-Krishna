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
BGM_FILE = os.path.join(BASE_DIR, "AUDIT_PURE_SOFT_BANSURI_5_TRACKS.mp3")

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

def get_next_image():
    """Picks the next 100% clean, text-free Krishna image from music_video_images pool."""
    all_images = []
    if os.path.exists(MUSIC_IMAGES_DIR):
        for root, dirs, files in os.walk(MUSIC_IMAGES_DIR):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    all_images.append(os.path.join(root, f))

    all_images = sorted(list(dict.fromkeys(all_images)))
    if not all_images and os.path.exists(IMAGES_DIR):
        for root, dirs, files in os.walk(IMAGES_DIR):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    all_images.append(os.path.join(root, f))
        all_images = sorted(list(dict.fromkeys(all_images)))

    if not all_images:
        raise RuntimeError(f"No clean Krishna images found in {MUSIC_IMAGES_DIR} or {IMAGES_DIR}!")

    used_images = set()
    if os.path.exists(USED_IMAGES_TRACKER):
        with open(USED_IMAGES_TRACKER, "r", encoding="utf-8") as f:
            used_images = set(line.strip() for line in f if line.strip())

    available = [img for img in all_images if img not in used_images]
    if not available:
        print(f"🔄 All {len(all_images)} clean images used! Resetting tracker for next cycle.")
        used_images.clear()
        available = all_images

    chosen = available[0]
    with open(USED_IMAGES_TRACKER, "a", encoding="utf-8") as f:
        f.write(chosen + "\n")

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

def synthesize_voice(phrases, output_audio_path):
    """
    Synthesizes speech using Edge-TTS hi-IN-MadhurNeural.
    Returns total audio duration and word timings list.
    """
    all_words = []
    for p in phrases:
        all_words.extend(p)

    full_text = " ".join([" ".join(p) for p in phrases])

    import edge_tts
    import asyncio

    async def _run():
        comm = edge_tts.Communicate(full_text, 'hi-IN-MadhurNeural', rate='-6%', pitch='-1Hz')
        await comm.save(output_audio_path)

    # Retry loop up to 3 times
    for attempt in range(3):
        try:
            asyncio.run(_run())
            if os.path.exists(output_audio_path) and os.path.getsize(output_audio_path) > 1000:
                break
        except Exception as te:
            print(f"TTS attempt {attempt+1} warning: {te}")
            time.sleep(2)

    if not os.path.exists(output_audio_path) or os.path.getsize(output_audio_path) < 1000:
        raise RuntimeError("Failed to synthesize voiceover with Edge-TTS!")

    ffmpeg = find_ffmpeg()
    cmd = [ffmpeg, "-i", output_audio_path]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    import re
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if m:
        dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    else:
        dur = max(len(all_words) * 0.45, 10.0)

    total_chars = sum(len(w) for w in all_words)
    speech_start = 0.55
    usable_speech_dur = max(dur - 0.2, 5.0)

    word_timings = []
    curr_t = speech_start

    for phrase_idx, phrase in enumerate(phrases):
        phrase_timings = []
        for w in phrase:
            w_len = len(w)
            w_dur = (w_len / max(total_chars, 1)) * usable_speech_dur
            w_dur = max(w_dur, 0.22)
            if "।" in w or "—" in w:
                w_dur += 0.35
            elif "," in w:
                w_dur += 0.18
            phrase_timings.append({
                'word': w,
                'start': curr_t,
                'end': curr_t + w_dur
            })
            curr_t += w_dur
        word_timings.append(phrase_timings)

    total_video_dur = curr_t + 1.6
    return total_video_dur, word_timings

def render_chrome_slide(task):
    chrome, html_file, png_file = task
    cmd = [
        chrome,
        "--headless=new",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--default-background-color=00000000",
        "--window-size=1080,420",
        f"--screenshot={png_file}",
        html_file
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(png_file) or os.path.getsize(png_file) == 0:
        raise RuntimeError(f"Chrome screenshot failed ({res.returncode}): {res.stderr}\nCommand: {' '.join(cmd)}")
    return png_file

def draw_procedural_wave(canvas, style, palette, intensity, t, base_y=140):
    """Draws dynamic beat-reactive procedural soundwaves onto RGBA canvas with alpha support."""
    w = canvas.shape[1]
    col_main = palette[0]
    col_mid = palette[1]
    col_glow = palette[2]

    if style == "silk_sine_ribbon":
        pts1 = []
        pts2 = []
        for x in range(0, w, 6):
            phase = (x / float(w)) * 4.0 * math.pi
            y_off = math.sin(phase + t * 4.2) * 45.0 * intensity + math.sin(phase * 2.1 - t * 2.8) * 22.0
            y1 = int(base_y + y_off)
            y2 = int(base_y - y_off * 0.75)
            pts1.append([x, y1])
            pts2.append([x, y2])
        for p in [pts1, pts2]:
            cv2.polylines(canvas, [np.array(p, np.int32)], False, col_glow, 7, cv2.LINE_AA)
            cv2.polylines(canvas, [np.array(p, np.int32)], False, col_main, 3, cv2.LINE_AA)

    elif style == "fullwidth_bars":
        num_bars = 48
        bar_w = int(w / num_bars)
        for b in range(num_bars):
            bx = b * bar_w + int(bar_w * 0.15)
            bw = int(bar_w * 0.7)
            b_phase = (b / float(num_bars)) * math.pi * 3.0
            bh = int(abs(math.sin(b_phase + t * 5.0) * 85.0 * intensity + math.cos(b * 0.6 + t * 3.2) * 35.0))
            bh = max(10, min(bh, 130))
            y_top = base_y - bh
            y_bot = base_y + bh
            c = col_main if (b % 2 == 0) else col_mid
            cv2.rectangle(canvas, (bx, y_top), (bx + bw, y_bot), c, -1)

    else:
        pts = []
        for x in range(0, w, 8):
            rad = (x / float(w)) * 6.28
            y_off = math.sin(rad * 3.0 + t * 4.5) * 50.0 * intensity + math.sin(rad * 6.0 - t * 3.0) * 25.0
            pts.append([x, int(base_y + y_off)])
        cv2.polylines(canvas, [np.array(pts, np.int32)], False, col_glow, 8, cv2.LINE_AA)
        cv2.polylines(canvas, [np.array(pts, np.int32)], False, col_main, 3, cv2.LINE_AA)

    mask = np.any(canvas[:, :, :3] > 15, axis=2)
    canvas[mask, 3] = 255

def generate_kinetic_reel(output_mp4, custom_quote=None, custom_image=None):
    """
    Complete end-to-end Kinetic Short Generator.
    Returns: (output_mp4, quote_text, image_path)
    """
    chrome = find_chrome()
    ffmpeg = find_ffmpeg()

    if not chrome:
        raise RuntimeError("Google Chrome or Chromium not found on system! (Checked candidates)")

    if not os.path.exists(BGM_FILE):
        raise RuntimeError(f"BGM audio file missing: {BGM_FILE}")

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

        voice_audio = os.path.join(temp_dir, "voice.mp3")
        total_video_dur, word_timings = synthesize_voice(phrases, voice_audio)
        print(f"🎙️ Synthesized Voiceover: {total_video_dur:.2f}s")

        # HTML template for Chrome rendering
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

        for phrase in word_timings:
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

                tasks.append((chrome, html_file, png_file))
                overlay_events.append({
                    'png': png_file,
                    'start': active_wt['start'],
                    'end': active_wt['end']
                })
                overlay_idx += 1

        print(f"🎨 Rendering {len(tasks)} Chrome HarfBuzz overlays in parallel...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(render_chrome_slide, tasks))

        # Generate Procedural Soundwave Overlay Video
        fps = 25
        total_frames = int(total_video_dur * fps)
        wave_video = os.path.join(temp_dir, "wave_overlay.mp4")

        wave_style = random.choice(VISUALIZER_STYLES)
        wave_palette = random.choice(COLOR_PALETTES)
        print(f"🌊 Rendering Soundwave ({wave_style}) at elevated y=1380 safe-zone...")

        wave_cmd = [
            ffmpeg, "-y",
            "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", "1080x280", "-pix_fmt", "bgra", "-r", str(fps),
            "-i", "-",
            "-c:v", "png", "-pix_fmt", "rgba",
            wave_video
        ]
        proc = subprocess.Popen(wave_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for i in range(total_frames):
            t = i / float(fps)
            canvas = np.zeros((280, 1080, 4), dtype=np.uint8)
            intensity = 1.1 + 0.65 * math.sin(t * 2.2) + 0.35 * math.cos(t * 4.1)
            draw_procedural_wave(canvas, wave_style, wave_palette, intensity, t, base_y=140)
            proc.stdin.write(canvas.tobytes())

        proc.stdin.close()
        proc.wait()

        # Build FFmpeg Filter Complex
        # Wave elevated to y=1380 (completely above YouTube Shorts bottom UI & handle)
        # Text at y=760 (upper chest, crystal clear)
        fade_out_start = f"{total_video_dur - 1.5:.2f}"

        # Universal aspect ratio fit: scales & crops cleanly to 1080x1920 then zooms
        filter_parts = [
            f"[0:v]scale='if(gt(a,9/16),-2,1440)':'if(gt(a,9/16),2560,-2)',crop=1440:2560,zoompan=z='min(zoom+0.0006,1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1080x1920:fps=25[base];",
            f"[base][1:v]overlay=0:1380[base_with_wave];"
        ]

        curr_input = "[base_with_wave]"
        input_args = [
            "-loop", "1", "-t", f"{total_video_dur:.2f}", "-i", image_path,
            "-i", wave_video
        ]

        input_idx = 2
        for oe in overlay_events:
            input_args.extend(["-i", oe['png']])
            next_input = f"[tmp_{input_idx}]" if input_idx < len(overlay_events) + 1 else "[v]"
            filter_parts.append(
                f"{curr_input}[{input_idx}:v]overlay=0:760:enable='between(t,{oe['start']:.2f},{oe['end']:.2f})'{next_input};"
            )
            curr_input = next_input
            input_idx += 1

        voice_idx = input_idx
        bgm_idx = input_idx + 1

        input_args.extend(["-i", voice_audio, "-i", BGM_FILE])

        filter_parts.append(
            f"[{voice_idx}:a]adelay=550|550,volume=1.40[voice];"
            f"[{bgm_idx}:a]volume=0.14,afade=t=out:st={fade_out_start}:d=1.5[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0,volume=1.8[a]"
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
