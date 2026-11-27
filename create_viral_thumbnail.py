#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_high_ctr_thumbnail(image_path, badge_text, headline_line1, headline_line2, output_path):
    """
    Overlays viral, high-CTR YouTube/Google Discover style Hindi typography
    onto the 16:9 Google Flow thumbnail.
    """
    im = Image.open(image_path).convert("RGBA")
    w, h = im.size
    
    # Create dark gradient overlay for top and bottom readability
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Bottom vignette/gradient
    for y in range(int(h * 0.45), h):
        alpha = int(210 * ((y - h * 0.45) / (h * 0.55)))
        draw.line([(0, y), (w, y)], fill=(5, 5, 10, alpha))
        
    # Top badge shadow
    for y in range(0, int(h * 0.22)):
        alpha = int(140 * (1 - (y / (h * 0.22))))
        draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
        
    im = Image.alpha_composite(im, overlay)
    draw = ImageDraw.Draw(im)
    
    # Fonts
    # Hindi font candidates
    hindi_font_paths = [
        "/system/fonts/NotoSansDevanagari-VF.ttf",
        "/system/fonts/MiSansDevanagariVF.ttf",
        "/data/user/0/ai.antigem/files/home/extensions/.antigem-backup/2d-video-editing-studio/fonts/hindi/Baloo2-Bold.ttf",
        "/system/fonts/NotoSansDevanagariUI-VF.ttf"
    ]
    font_path = None
    for p in hindi_font_paths:
        if os.path.exists(p):
            font_path = p
            break
            
    badge_font = ImageFont.truetype(font_path, int(h * 0.055))
    headline_font1 = ImageFont.truetype(font_path, int(h * 0.095))
    headline_font2 = ImageFont.truetype(font_path, int(h * 0.105))
    
    # 1. Draw Top Badge (e.g. "🔥 भगवद्गीता का गुप्त रहस्य")
    badge_x = int(w * 0.05)
    badge_y = int(h * 0.06)
    
    # Badge background pill
    bbox = draw.textbbox((badge_x, badge_y), badge_text, font=badge_font)
    pad_x, pad_y = 18, 8
    badge_rect = [bbox[0] - pad_x, bbox[1] - pad_y, bbox[2] + pad_x, bbox[3] + pad_y]
    draw.rounded_rectangle(badge_rect, radius=12, fill=(230, 40, 40, 240), outline=(255, 215, 0, 255), width=2)
    draw.text((badge_x, badge_y), badge_text, font=badge_font, fill=(255, 255, 255, 255))
    
    # 2. Draw Headline Line 1 (e.g. "मन शांत नहीं रहता?")
    # Shadow / Outline for 3D Pop
    y1 = int(h * 0.62)
    x1 = int(w * 0.05)
    
    for ox, oy in [(-3,-3), (3,-3), (-3,3), (3,3), (0,4), (4,0), (-4,0), (0,-4)]:
        draw.text((x1 + ox, y1 + oy), headline_line1, font=headline_font1, fill=(0, 0, 0, 255))
    draw.text((x1, y1), headline_line1, font=headline_font1, fill=(255, 255, 255, 255)) # Pure crisp white
    
    # 3. Draw Headline Line 2 (e.g. "श्रीकृष्ण का 1 अचूक नियम!")
    y2 = int(h * 0.77)
    x2 = int(w * 0.05)
    
    # Golden glow / black stroke
    for ox, oy in [(-4,-4), (4,-4), (-4,4), (4,4), (0,5), (5,0), (-5,0), (0,-5)]:
        draw.text((x2 + ox, y2 + oy), headline_line2, font=headline_font2, fill=(0, 0, 0, 255))
    draw.text((x2, y2), headline_line2, font=headline_font2, fill=(255, 215, 0, 255)) # Glowing Golden Amber
    
    # Save back to RGB JPEG
    im = im.convert("RGB")
    im.save(output_path, "JPEG", quality=92)
    print(f"Viral CTR Thumbnail created at {output_path}")

if __name__ == "__main__":
    src = "/data/user/0/ai.antigem/files/home/projects/Auto-Insta-Krishna/website/public/images/articles/gita-upay-krishna-arjuna-hero.jpg"
    out = "/data/user/0/ai.antigem/files/home/projects/Auto-Insta-Krishna/website/public/images/articles/gita-upay-krishna-arjuna-hero.jpg"
    create_high_ctr_thumbnail(
        src,
        "🔥 भगवद्गीता का गुप्त रहस्य",
        "मन शांत नहीं रहता?",
        "श्रीकृष्ण का 1 अचूक नियम!",
        out
    )
