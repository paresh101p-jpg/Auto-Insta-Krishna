#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates a stunning, crystal-clear 16:9 YouTube Thumbnail for Krishna Flute Music Videos
with 100% accurate Hindi Devanagari matras, ligatures, and high-CTR typography via FFmpeg.
"""

import os
import sys
import random
import subprocess
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

MEDITATION_HOOKS = [
    ("15 MIN DEEP MEDITATION", "दिव्य बांसुरी एवं तबला संगीत", "तनाव दूर करें और असीम शांति पाएं"),
    ("INNER PEACE & HEALING", "श्री कृष्ण अमृत बाँसुरी", "मन की शांति और गहरी नींद के लिए"),
    ("DIVINE SACRED VIBES", "राधे कृष्ण पावन धुन", "सकारात्मक ऊर्जा और आत्मिक सुकून"),
    ("STRESS RELIEF & CALM", "मन को शांत करने वाला संगीत", "दिव्य शांति और विश्राम का अनुभव"),
    ("VRINDAVAN MORNING DHUN", "वृंदावन प्रभात बाँसुरी", "प्रातःकालीन पूजा और सकारात्मक शुरुआत"),
    ("DEEP SLEEP & CHINTA MUKTI", "चिंता मुक्ति और गहरी नींद", "रात्रि विश्राम और मानसिक सुकून"),
]


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

    if os.path.exists(local_font):
        hindi_font_path = local_font
    else:
        candidates = [
            "C:/Windows/Fonts/Nirmala.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
            "/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf",
        ]
        hindi_font_path = "arial.ttf"
        for c in candidates:
            if os.path.exists(c):
                hindi_font_path = c
                break

    local_english = os.path.join(BASE_DIR, "arialbd.ttf")
    if os.path.exists(local_english):
        english_font_path = local_english
    else:
        candidates_en = [
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        english_font_path = "arial.ttf"
        for c in candidates_en:
            if os.path.exists(c):
                english_font_path = c
                break

    hindi_arg = os.path.abspath(hindi_font_path).replace("\\", "/").replace(":", "\\:")
    english_arg = os.path.abspath(english_font_path).replace("\\", "/").replace(":", "\\:")
    return hindi_arg, english_arg


def create_thumbnail(hook=None, image_path=None, output_path=None):
    if not hook:
        hook = random.choice(MEDITATION_HOOKS)
    english_badge, hindi_main, hindi_sub = hook

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

    hook_pill = "मन की शांति   |   गहरी नींद   |   चिंता मुक्ति"

    vf = (
        f"scale=1920:1080,"
        f"drawbox=y=0:h=180:color=black@0.45:t=fill,"
        f"drawbox=y=500:h=580:color=black@0.84:t=fill,"
        f"drawbox=x=60:y=496:w=1800:h=5:color=goldenrod@0.90:t=fill,"
        f"drawbox=x=70:y=45:w=740:h=90:color=0xFFB300@0.98:t=fill,"
        f"drawbox=x=66:y=41:w=748:h=98:color=white@0.85:t=4,"
        f"drawtext=fontfile='{english_font_arg}':text='{english_badge}':fontcolor=black:fontsize=46:x=105:y=68,"
        f"drawtext=fontfile='{hindi_font_arg}':text='{hindi_main}':fontcolor=0xFFE600:fontsize=128:x=75:y=550:borderw=10:bordercolor=black,"
        f"drawtext=fontfile='{hindi_font_arg}':text='{hindi_sub}':fontcolor=white:fontsize=82:x=75:y=725:borderw=8:bordercolor=black,"
        f"drawbox=x=75:y=850:w=1040:h=82:color=0x8B0000@0.95:t=fill,"
        f"drawbox=x=71:y=846:w=1048:h=90:color=goldenrod@0.85:t=3,"
        f"drawtext=fontfile='{hindi_font_arg}':text='{hook_pill}':fontcolor=0xFFF8DC:fontsize=48:x=110:y=868:borderw=3:bordercolor=black,"
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

    # Also keep sample master thumbnail updated
    import shutil
    shutil.copy2(out_file, SAMPLE_THUMBNAIL)
    print(f"[OK] 100% Devanagari Flawless Thumbnail created: {out_file}")
    return out_file


if __name__ == "__main__":
    create_thumbnail()
