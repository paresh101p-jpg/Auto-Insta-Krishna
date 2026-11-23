#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — SONG THUMBNAIL GENERATOR (मूड-बेस्ड, फ्री)
=============================================================================
- गाने की ऑडियो एनालिसिस (मूड) के हिसाब से थंबनेल के रंग तय करता है
- हिंदी देववनागरी टेक्स्ट (गाने का नाम + Krishna Vibez ब्रांडिंग)
- 1280x720 YouTube थंबनेल
- 'song_thumbnails/' फोल्डर में स्टोर करता है
- जब भी गाने का URL add होता है, साथ में थंबनेल भी बनता है
- पूरा फ्री (ffmpeg + स्थानीय फॉन्ट्स, कोई पेड़ API नहीं)
=============================================================================
"""

import os
import sys
import json
import subprocess
import re
import shutil

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- फोल्डर ---
SONG_THUMB_DIR = os.path.join(BASE_DIR, "song_thumbnails")
SONG_REGISTRY_FILE = os.path.join(BASE_DIR, "song_tracks_registry.json")
SONG_THUMB_TRACKER = os.path.join(BASE_DIR, "song_thumbnails_tracker.txt")
SONGS_INBOX = os.path.join(BASE_DIR, "Songs", "inbox")

os.makedirs(SONG_THUMB_DIR, exist_ok=True)

FFMPEG_EXE = "ffmpeg"
local_ffmpeg = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if sys.platform != "win32" or not os.path.exists(local_ffmpeg):
    FFMPEG_EXE = "ffmpeg"
elif os.path.exists(local_ffmpeg):
    FFMPEG_EXE = local_ffmpeg

# फॉन्ट पाथ
HINDI_FONT = os.path.join(BASE_DIR, "NotoSansDevanagari-Bold.ttf")
ENGLISH_FONT = os.path.join(BASE_DIR, "arialbd.ttf")


def resolve_fonts():
    hindi_candidates = [
        HINDI_FONT,
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "C:/Windows/Fonts/Nirmala.ttf",
        "C:/Windows/Fonts/NirmalaB.ttf",
    ]
    hindi_font_path = HINDI_FONT if os.path.exists(HINDI_FONT) else "arial.ttf"
    for c in hindi_candidates:
        if os.path.exists(c):
            hindi_font_path = c
            break

    english_candidates = [
        ENGLISH_FONT,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    english_font_path = "arial.ttf"
    for c in english_candidates:
        if os.path.exists(c):
            english_font_path = c
            break

    return hindi_font_path, english_font_path


def sanitize_filename(name):
    safe = re.sub(r'[<>:"/\\|?*]', '_', name)
    safe = re.sub(r'\s+', '_', safe).strip('_')
    return safe or "song"


def load_tracker():
    if os.path.exists(SONG_THUMB_TRACKER):
        with open(SONG_THUMB_TRACKER, "r", encoding="utf-8") as f:
            return {l.strip() for l in f if l.strip()}
    return set()


def save_tracker(tracker):
    with open(SONG_THUMB_TRACKER, "w", encoding="utf-8") as f:
        for name in sorted(tracker):
            f.write(name + "\n")


def load_registry():
    if os.path.exists(SONG_REGISTRY_FILE):
        try:
            with open(SONG_REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def get_fallback_bg():
    """मौजूदा कृष्णा थीम इमेज को बैकग्राउंड के रूप में इस्तेमाल करना"""
    for cand in [
        "master_ai_thumb_divine_krishna_pure.jpg",
        "master_ai_thumb_temple_dawn_pure.jpg",
        "hook_thumb_lotus_lake.jpg",
        "MUSIC_VIDEO_HIGH_CTR_SAMPLE_THUMBNAIL.jpg",
    ]:
        p = os.path.join(BASE_DIR, cand)
        if os.path.exists(p):
            return p
    return None


def generate_waveform_bg(audio_path, output_path):
    """
    गाने की ऑडियो वेवफॉर्म से बैकग्राउंड इमेज बनाना (फ्री)
    इससे थंबनेल में गाने की असली ध्वनि का विजुअल आएगा
    """
    try:
        cmd = [
            FFMPEG_EXE, "-y", "-i", audio_path,
            "-filter_complex",
            "[0:a]showwavespic=s=1280x720:colors=#FFD700@0.6:scale=sqrt:mode=average[v]",
            "-map", "[v]", "-frames:v", "1",
            output_path
        ]
        subprocess.run(cmd, cwd=BASE_DIR, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    except Exception:
        return None


def create_song_thumbnail(song_name, audio_path=None, output_path=None,
                          mood="Balanced Bhakti", mood_hi="संतुलित भक्ति संगीत"):
    """
    मूड के हिसाब से रंगों के साथ गाने का थंबनेल बनाना।
    अगर audio_path दिया गया है तो वेवफॉर्म भी जोड़ेगा।
    """
    hindi_font, english_font = resolve_fonts()
    colors = get_mood_colors(mood)

    if not output_path:
        safe_name = sanitize_filename(song_name)
        output_path = os.path.join(SONG_THUMB_DIR, f"{safe_name}.jpg")

    # बैकग्राउंड तय करना: वेवफॉर्म > फॉलबैक इमेज > ग्रेडिएंट
    bg_input = None
    vf_start = f"color={colors['bg1']}:1280x720:format=rgb24,"

    if audio_path and os.path.exists(audio_path):
        # गाने की असली वेवफॉर्म से बैकग्राउंड बनाना
        wave_path = os.path.join(BASE_DIR, "temp_song_waveform.jpg")
        if generate_waveform_bg(audio_path, wave_path):
            bg_input = wave_path
            vf_start = "scale=1280x720:force_original_aspect_ratio=increase,crop=1280:720,"
        else:
            # वेवफॉर्म नहीं बना तो फॉलबैक इमेज
            fb = get_fallback_bg()
            if fb:
                bg_input = fb
                vf_start = "scale=1280x720:force_original_aspect_ratio=increase,crop=1280x720,"
    else:
        fb = get_fallback_bg()
        if fb:
            bg_input = fb
            vf_start = "scale=1280x720:force_original_aspect_ratio=increase,crop=1280x720,"

    # टेक्स्ट फाइलें (UTF-8)
    badge_txt = os.path.join(BASE_DIR, "temp_song_badge.txt")
    main_txt = os.path.join(BASE_DIR, "temp_song_main.txt")
    sub_txt = os.path.join(BASE_DIR, "temp_song_sub.txt")

    with open(badge_txt, "w", encoding="utf-8") as f:
        f.write("KRISHNA VIBEZ")
    with open(main_txt, "w", encoding="utf-8") as f:
        f.write(song_name)
    with open(sub_txt, "w", encoding="utf-8") as f:
        f.write(f"{mood_hi} • श्री कृष्ण भक्ति")

    badge_arg = os.path.abspath(badge_txt).replace("\\", "/").replace(":", "\\:")
    main_arg = os.path.abspath(main_txt).replace("\\", "/").replace(":", "\\:")
    sub_arg = os.path.abspath(sub_txt).replace("\\", "/").replace(":", "\\:")
    hindi_arg = os.path.abspath(hindi_font).replace("\\", "/").replace(":", "\\:")
    english_arg = os.path.abspath(english_font).replace("\\", "/").replace(":", "\\:")

    vf = (
        f"{vf_start}"
        f"drawbox=y=0:h=100:color=black@0.5:t=fill,"
        f"drawbox=x=60:y=310:w=1160:h=5:color={colors['accent']}@0.9:t=fill,"
        f"drawbox=x=60:y=460:w=1160:h=5:color={colors['accent']}@0.9:t=fill,"
        f"drawtext=fontfile='{english_font}':textfile='{badge_arg}':fontcolor={colors['accent']}:fontsize=40:x=50:y=35:borderw=3:bordercolor=black,"
        f"drawtext=fontfile='{hindi_font}':textfile='{main_arg}':fontcolor={colors['text_main']}:fontsize=72:x=60:y=340:borderw=8:bordercolor=black:text_shaping=1,"
        f"drawtext=fontfile='{hindi_font}':textfile='{sub_arg}':fontcolor={colors['text_sub']}:fontsize=40:x=60:y=520:borderw=5:bordercolor=black:text_shaping=1,"
        f"drawtext=fontfile='{english_font}':text='Krishna Vibez':fontcolor={colors['accent']}:fontsize=36:x=920:y=660:borderw=3:bordercolor=black"
    )

    cmd = [FFMPEG_EXE, "-y", "-update", "1", "-q:v", "2"]
    if bg_input:
        cmd += ["-i", bg_input]
    cmd += ["-vf", vf, "-frames:v", "1", output_path]

    try:
        subprocess.run(cmd, cwd=BASE_DIR, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # अस्थायी वेवफॉर्म हटाना
        if audio_path and os.path.exists(os.path.join(BASE_DIR, "temp_song_waveform.jpg")):
            try:
                os.remove(os.path.join(BASE_DIR, "temp_song_waveform.jpg"))
            except Exception:
                pass
        return True
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode()[:200] if e.stderr else str(e)
        print(f"  ❌ Thumbnail FFmpeg failed for '{song_name}': {err_msg}")
        return False
    finally:
        for tf in [badge_txt, main_txt, sub_txt]:
            if os.path.exists(tf):
                try:
                    os.remove(tf)
                except Exception:
                    pass


def generate_thumbnails_for_all_songs():
    """रजिस्ट्री में मौजूद सभी गानों के लिए थंबनेल बनाना"""
    print("=" * 60)
    print("  KRISHNA VIBEZ — SONG THUMBNAIL GENERATOR (मूड-बेस्ड)")
    print("=" * 60)

    reg = load_registry()
    if not reg:
        print("[INFO] कोई गाना रजिस्ट्री में नहीं है। पहले process_songs.py चलाएं।")
        return []

    already_done = load_tracker()
    new_thumbs = []

    for url, song_name in reg.items():
        if song_name in already_done:
            continue

        safe_name = sanitize_filename(song_name)
        out_path = os.path.join(SONG_THUMB_DIR, f"{safe_name}.jpg")

        # ऑडियो फाइल खोजना (inbox या uploaded में)
        audio_path = None
        for folder in [SONGS_INBOX, os.path.join(BASE_DIR, "Songs", "uploaded")]:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    if f.lower().endswith((".mp3", ".wav", ".ogg", ".flac", ".m4a")):
                        name_without_ext = os.path.splitext(f)[0]
                        if name_without_ext.lower() == song_name.lower():
                            audio_path = os.path.join(folder, f)
                            break
                    if audio_path:
                        break

        print(f"\n🎨 थंबनेल बन रहा है: {song_name}")
        if create_song_thumbnail(song_name, audio_path=audio_path,
                                 output_path=out_path, mood="Balanced Bhakti",
                                 mood_hi="संतुलित भक्ति संगीत"):
            print(f"  ✅ सेव हुआ: {out_path}")
            already_done.add(song_name)
            new_thumbs.append(out_path)
        else:
            print(f"  ❌ असफल: {song_name}")

    save_tracker(already_done)
    print(f"\n[COMPLETE] {len(new_thumbs)} नए थंबनेल बने।")
    print(f"   कुल थंबनेल song_thumbnails/ में: {len(os.listdir(SONG_THUMB_DIR))}")
    return new_thumbs


def generate_thumbnail_for_song(song_name, audio_path=None, mood="Balanced Bhakti",
                                mood_hi="संतुलित भक्ति संगीत"):
    """एक खास गाने का थंबनेल बनाना (जब नया URL add हो)"""
    safe_name = sanitize_filename(song_name)
    out_path = os.path.join(SONG_THUMB_DIR, f"{safe_name}.jpg")

    if os.path.exists(out_path):
        print(f"[INFO] थंबनेल पहले से मौजूद है: {out_path}")
        return out_path

    print(f"\n🎨 नया थंबनेल बन रहा है: {song_name}")
    if create_song_thumbnail(song_name, audio_path=audio_path,
                             output_path=out_path, mood=mood, mood_hi=mood_hi):
        already_done = load_tracker()
        already_done.add(song_name)
        save_tracker(already_done)
        print(f"  ✅ थंबनेल तैयार: {out_path}")
        return out_path
    else:
        print(f"  ❌ थंबनेल बनाने में असफल: {song_name}")
        return None


if __name__ == "__main__":
    generate_thumbnails_for_all_songs()
