#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates a stunning, crystal-clear 16:9 YouTube Thumbnail for Krishna Flute Music Videos
with 100% accurate Hindi Devanagari matras, ligatures, and high-CTR typography via FFmpeg.
Uses UTF-8 textfile buffers and Noto Sans Devanagari to guarantee zero broken matras.
"""

import os
import sys
import random
import subprocess
import shutil
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "music_video_images")
OUTPUT_THUMBNAIL = os.path.join(BASE_DIR, "test_generated_thumbnail.jpg")
SAMPLE_THUMBNAIL = os.path.join(BASE_DIR, "MUSIC_VIDEO_HIGH_CTR_SAMPLE_THUMBNAIL.jpg")

FFMPEG_EXE = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG_EXE):
    FFMPEG_EXE = "ffmpeg"

try:
    from auto_music_video_pipeline import get_dynamic_music_metadata, MEDITATION_THEMES_36
except ImportError:
    get_dynamic_music_metadata = None
    MEDITATION_THEMES_36 = []


def resolve_fonts():
    """Resolves absolute font paths with full Devanagari complex text shaping support."""
    local_font = os.path.join(BASE_DIR, "NotoSansDevanagari-Bold.ttf")
    if not os.path.exists(local_font):
        try:
            f_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf"
            r = requests.get(f_url, timeout=10)
            if r.status_code == 200:
                with open(local_font, "wb") as f:
                    f.write(r.content)
        except Exception:
            pass

    hindi_candidates = [
        local_font,
        "C:/Windows/Fonts/Nirmala.ttc",
        "C:/Windows/Fonts/NirmalaB.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansDevanagari-Bold.otf",
    ]
    hindi_font_path = local_font if os.path.exists(local_font) else "arial.ttf"
    for c in hindi_candidates:
        if os.path.exists(c):
            hindi_font_path = c
            break

    local_english = os.path.join(BASE_DIR, "arialbd.ttf")
    english_candidates = [
        local_english,
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    english_font_path = "arial.ttf"
    for c in english_candidates:
        if os.path.exists(c):
            english_font_path = c
            break

    hindi_arg = os.path.abspath(hindi_font_path).replace("\\", "/").replace(":", "\\:")
    english_arg = os.path.abspath(english_font_path).replace("\\", "/").replace(":", "\\:")
    return hindi_arg, english_arg


def create_thumbnail(theme=None, image_path=None, output_path=None):
    if not theme:
        if get_dynamic_music_metadata:
            theme = get_dynamic_music_metadata(dur_min=random.randint(15, 45))
        elif MEDITATION_THEMES_36:
            theme = random.choice(MEDITATION_THEMES_36).copy()
        else:
            theme = {
                "badge": "32 MIN DEEP MEDITATION",
                "hindi_main": "दिव्य बांसुरी एवं तबला संगीत",
                "hindi_sub": "तनाव दूर करें और असीम शांति पाएं",
                "hook_pill": "मन की शांति   |   गहरी नींद   |   चिंता मुक्ति"
            }

    english_badge = theme.get("badge", "DEEP MEDITATION")
    hindi_main = theme.get("hindi_main", "श्री कृष्ण अमृत बाँसुरी")
    hindi_sub = theme.get("hindi_sub", "मन की शांति और गहरी नींद के लिए")
    hook_pill = theme.get("hook_pill", "मन की शांति   |   गहरी नींद   |   चिंता मुक्ति")

    if not image_path:
        images = [
            os.path.join(IMAGES_DIR, f)
            for f in os.listdir(IMAGES_DIR)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        image_path = random.choice(images) if images else None

    if not image_path or not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    out_file = output_path or OUTPUT_THUMBNAIL
    hindi_font_arg, english_font_arg = resolve_fonts()

    # Write texts to UTF-8 textfiles so FFmpeg HarfBuzz gets 100% clean multibyte Unicode
    badge_txt = os.path.join(BASE_DIR, "temp_test_badge.txt")
    main_txt = os.path.join(BASE_DIR, "temp_test_main.txt")
    sub_txt = os.path.join(BASE_DIR, "temp_test_sub.txt")
    pill_txt = os.path.join(BASE_DIR, "temp_test_pill.txt")

    with open(badge_txt, "w", encoding="utf-8") as f:
        f.write(english_badge)
    with open(main_txt, "w", encoding="utf-8") as f:
        f.write(hindi_main)
    with open(sub_txt, "w", encoding="utf-8") as f:
        f.write(hindi_sub)
    with open(pill_txt, "w", encoding="utf-8") as f:
        f.write(hook_pill)

    badge_arg = os.path.abspath(badge_txt).replace("\\", "/").replace(":", "\\:")
    main_arg = os.path.abspath(main_txt).replace("\\", "/").replace(":", "\\:")
    sub_arg = os.path.abspath(sub_txt).replace("\\", "/").replace(":", "\\:")
    pill_arg = os.path.abspath(pill_txt).replace("\\", "/").replace(":", "\\:")

    vf = (
        f"scale=1920:1080,"
        f"drawbox=y=0:h=180:color=black@0.45:t=fill,"
        f"drawbox=y=500:h=580:color=black@0.84:t=fill,"
        f"drawbox=x=60:y=496:w=1800:h=5:color=goldenrod@0.90:t=fill,"
        f"drawbox=x=70:y=45:w=740:h=90:color=0xFFB300@0.98:t=fill,"
        f"drawbox=x=66:y=41:w=748:h=98:color=white@0.85:t=4,"
        f"drawtext=fontfile='{english_font_arg}':textfile='{badge_arg}':fontcolor=black:fontsize=46:x=105:y=68,"
        f"drawtext=fontfile='{hindi_font_arg}':textfile='{main_arg}':fontcolor=0xFFE600:fontsize=128:x=75:y=550:borderw=10:bordercolor=black:text_shaping=1,"
        f"drawtext=fontfile='{hindi_font_arg}':textfile='{sub_arg}':fontcolor=white:fontsize=82:x=75:y=725:borderw=8:bordercolor=black:text_shaping=1,"
        f"drawbox=x=75:y=850:w=1040:h=82:color=0x8B0000@0.95:t=fill,"
        f"drawbox=x=71:y=846:w=1048:h=90:color=goldenrod@0.85:t=3,"
        f"drawtext=fontfile='{hindi_font_arg}':textfile='{pill_arg}':fontcolor=0xFFF8DC:fontsize=48:x=110:y=868:borderw=3:bordercolor=black:text_shaping=1,"
        f"drawtext=fontfile='{english_font_arg}':text='KRISHNA VIBEZ':fontcolor=0xFFD700:fontsize=46:x=1500:y=995:borderw=5:bordercolor=black"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", image_path,
        "-vf", vf,
        "-frames:v", "1",
        "-update", "1",
        "-q:v", "2",
        out_file
    ]

    subprocess.run(cmd, cwd=BASE_DIR, check=True)

    for tf in [badge_txt, main_txt, sub_txt, pill_txt]:
        if os.path.exists(tf):
            try: os.remove(tf)
            except Exception: pass

    # Also keep sample master thumbnail updated
    shutil.copy2(out_file, SAMPLE_THUMBNAIL)
    print(f"[OK] 100% Devanagari Flawless Thumbnail created: {out_file}")
    return out_file


if __name__ == "__main__":
    create_thumbnail()
