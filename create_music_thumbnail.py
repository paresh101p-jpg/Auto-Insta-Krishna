#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates a stunning 16:9 YouTube Thumbnail for Krishna Flute Music Videos.
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "music_video_images")
OUTPUT_THUMBNAIL = os.path.join(BASE_DIR, "test_generated_thumbnail.jpg")

MEDITATION_HOOKS = [
    ("15 MIN DEEP MEDITATION", "श्री कृष्ण दिव्य बाँसुरी", "तनाव और अशांति होगी दूर"),
    ("INNER PEACE & HEALING", "मन की शांति के लिए बाँसुरी", "गहरी नींद और सुकून"),
    ("432 Hz DIVINE VIBES", "श्री कृष्ण बाँसुरी एवं तबला", "सकारात्मक ऊर्जा का संचार"),
    ("SACRED FLUTE MEDITATION", "राधे कृष्ण अमृत धुन", "ध्यान और आत्मिक शांति"),
    ("STRESS RELIEF & SLEEP", "मन को शांत करने वाला संगीत", "दिव्य शांति का अनुभव"),
]

def create_thumbnail(hook=None, image_path=None):
    if not hook:
        hook = random.choice(MEDITATION_HOOKS)
    english_badge, hindi_main, hindi_sub = hook

    if not image_path:
        images = [os.path.join(IMAGES_DIR, f) for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.png'))]
        image_path = random.choice(images) if images else None

    if not image_path or not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # 1. Base Image - 1920x1080 (16:9)
    img = Image.open(image_path).convert("RGBA")
    img = img.resize((1920, 1080), Image.Resampling.LANCZOS)

    # 2. Gradient Overlay for Text Readability
    overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Left & Bottom shadow gradient so Krishna on right/center remains vivid
    for y in range(1080):
        # Bottom gradient
        if y > 600:
            alpha = int(220 * ((y - 600) / 480))
            draw.line([(0, y), (1920, y)], fill=(10, 5, 2, alpha))
        # Top gradient for badge
        if y < 200:
            alpha = int(140 * ((200 - y) / 200))
            draw.line([(0, y), (1920, y)], fill=(10, 5, 2, alpha))

    # Darker subtle vignette on left side for text prominence
    for x in range(1100):
        alpha = int(120 * ((1100 - x) / 1100))
        draw.line([(x, 0), (x, 1080)], fill=(5, 3, 1, alpha))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # 3. Fonts
    hindi_font_path = "C:/Windows/Fonts/Nirmala.ttc"
    english_font_path = "C:/Windows/Fonts/arialbd.ttf"
    if not os.path.exists(hindi_font_path):
        hindi_font_path = "C:/Windows/Fonts/arial.ttf"
    if not os.path.exists(english_font_path):
        english_font_path = hindi_font_path

    font_badge = ImageFont.truetype(english_font_path, 34)
    font_main = ImageFont.truetype(hindi_font_path, 80)
    font_sub = ImageFont.truetype(hindi_font_path, 50)
    font_brand = ImageFont.truetype(english_font_path, 30)

    # 4. English Badge (Top-Left)
    badge_x, badge_y = 80, 80
    badge_text = f"  ✨  {english_badge}  ✨  "
    bbox = draw.textbbox((badge_x, badge_y), badge_text, font=font_badge)
    # Draw glowing pill background
    draw.rounded_rectangle([bbox[0]-15, bbox[1]-10, bbox[2]+15, bbox[3]+10], radius=16, fill=(212, 160, 23, 230), outline=(255, 235, 150), width=2)
    draw.text((badge_x, badge_y), badge_text, font=font_badge, fill=(20, 10, 0))

    # 5. Hindi Main Title (Bottom Left)
    main_x, main_y = 80, 720
    # Shadow
    for dx, dy in [(-3,-3), (3,-3), (-3,3), (3,3), (0, 4), (4, 0)]:
        draw.text((main_x + dx, main_y + dy), hindi_main, font=font_main, fill=(0, 0, 0, 240))
    # Golden Gradient / Yellow Color
    draw.text((main_x, main_y), hindi_main, font=font_main, fill=(255, 230, 80))

    # 6. Hindi Subtitle
    sub_x, sub_y = 80, 840
    for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2), (0, 3)]:
        draw.text((sub_x + dx, sub_y + dy), hindi_sub, font=font_sub, fill=(0, 0, 0, 240))
    draw.text((sub_x, sub_y), hindi_sub, font=font_sub, fill=(255, 255, 255))

    # 7. Brand Watermark (Bottom Right)
    brand_text = "KRISHNA VIBEZ"
    bbox_br = draw.textbbox((0, 0), brand_text, font=font_brand)
    bw = bbox_br[2] - bbox_br[0]
    draw.text((1920 - bw - 80, 990), brand_text, font=font_brand, fill=(255, 215, 0, 200))

    # Save
    final_img = img.convert("RGB")
    final_img.save(OUTPUT_THUMBNAIL, quality=95)
    print(f"[OK] Thumbnail created: {OUTPUT_THUMBNAIL}")
    return OUTPUT_THUMBNAIL

if __name__ == "__main__":
    create_thumbnail()
