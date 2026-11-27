#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import re
from PIL import Image, ImageDraw, ImageFont

def strip_unsupported_emojis(text: str) -> str:
    """Removes emoji characters that lack glyphs in Devanagari fonts to prevent square boxes (tofu)."""
    # Remove emoji characters (surrogate pairs / high unicode codepoints)
    return re.sub(r'[\U00010000-\U0010ffff]', '', text).strip()

def create_high_ctr_thumbnail(image_path, badge_text, headline_line1, headline_line2, output_path):
    """
    Overlays ULTRA-BOLD, unmissable, viral YouTube/Google Discover Hindi typography
    with thick solid borders & badges on the 16:9 thumbnail.
    Ensures 100% clean Hindi text with ZERO square box symbols.
    """
    badge_text = strip_unsupported_emojis(badge_text)
    headline_line1 = strip_unsupported_emojis(headline_line1)
    headline_line2 = strip_unsupported_emojis(headline_line2)

    im = Image.open(image_path).convert("RGBA")
    w, h = im.size
    
    # 1. Dark bottom gradient overlay for maximum text contrast
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_over = ImageDraw.Draw(overlay)
    
    for y in range(int(h * 0.40), h):
        ratio = (y - h * 0.40) / (h * 0.60)
        alpha = int(240 * ratio)
        d_over.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
        
    for y in range(0, int(h * 0.22)):
        alpha = int(160 * (1 - (y / (h * 0.22))))
        d_over.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
        
    im = Image.alpha_composite(im, overlay)
    draw = ImageDraw.Draw(im)
    
    # Fonts
    hindi_font_paths = [
        r"C:\Windows\Fonts\Nirmala.ttc",
        r"C:\Windows\Fonts\arialbd.ttf",
        "/system/fonts/NotoSansDevanagari-VF.ttf",
        "/system/fonts/MiSansDevanagariVF.ttf",
        "/data/user/0/ai.antigem/files/home/extensions/.antigem-backup/2d-video-editing-studio/fonts/hindi/Baloo2-Bold.ttf",
        "/system/fonts/NotoSansDevanagariUI-VF.ttf"
    ]
    font_path = None
    font_index = 0
    for p in hindi_font_paths:
        if os.path.exists(p):
            font_path = p
            if p.lower().endswith(".ttc"):
                font_index = 1
            break
            
    badge_size = int(h * 0.065)
    line1_size = int(h * 0.115)
    line2_size = int(h * 0.125)
    
    if font_path.lower().endswith(".ttc"):
        badge_font = ImageFont.truetype(font_path, badge_size, index=font_index)
        h_font1 = ImageFont.truetype(font_path, line1_size, index=font_index)
        h_font2 = ImageFont.truetype(font_path, line2_size, index=font_index)
    else:
        badge_font = ImageFont.truetype(font_path, badge_size)
        h_font1 = ImageFont.truetype(font_path, line1_size)
        h_font2 = ImageFont.truetype(font_path, line2_size)
    
    # --- Top Badge ---
    bx, by = int(w * 0.04), int(h * 0.05)
    bbox = draw.textbbox((bx, by), badge_text, font=badge_font)
    pad_x, pad_y = 22, 10
    draw.rounded_rectangle([bbox[0]-pad_x, bbox[1]-pad_y, bbox[2]+pad_x, bbox[3]+pad_y], radius=14, fill=(225, 20, 20, 255), outline=(255, 230, 80, 255), width=3)
    draw.text((bx, by), badge_text, font=badge_font, fill=(255, 255, 255, 255))
    
    # --- Line 1 (White 3D Heavy) ---
    x1, y1 = int(w * 0.04), int(h * 0.58)
    stroke_w1 = 6
    for dx in range(-stroke_w1, stroke_w1 + 1):
        for dy in range(-stroke_w1, stroke_w1 + 1):
            if dx*dx + dy*dy <= stroke_w1*stroke_w1:
                draw.text((x1 + dx, y1 + dy), headline_line1, font=h_font1, fill=(0, 0, 0, 255))
    draw.text((x1, y1), headline_line1, font=h_font1, fill=(255, 255, 255, 255))
    
    # --- Line 2 (Radiant Golden Yellow Heavy) ---
    x2, y2 = int(w * 0.04), int(h * 0.76)
    stroke_w2 = 7
    for dx in range(-stroke_w2, stroke_w2 + 1):
        for dy in range(-stroke_w2, stroke_w2 + 1):
            if dx*dx + dy*dy <= stroke_w2*stroke_w2:
                draw.text((x2 + dx, y2 + dy), headline_line2, font=h_font2, fill=(0, 0, 0, 255))
    draw.text((x2, y2), headline_line2, font=h_font2, fill=(255, 215, 0, 255))
    
    im = im.convert("RGB")
    im.save(output_path, "JPEG", quality=95)
    print(f"Generated clean ultra bold viral thumbnail: {output_path}")

if __name__ == "__main__":
    src = r"E:\Paresh\Auto Post\Auto-Insta-Krishna\website\public\images\articles\kalikaal-overthinking-gita-upay-hero.jpg"
    out = r"E:\Paresh\Auto Post\Auto-Insta-Krishna\website\public\images\articles\krishna-arjuna-viral-thumb-v2.jpg"
    create_high_ctr_thumbnail(
        src,
        "भगवद्गीता का गुप्त रहस्य",
        "मन शांत नहीं रहता?",
        "श्रीकृष्ण का 1 अचूक नियम!",
        out
    )
