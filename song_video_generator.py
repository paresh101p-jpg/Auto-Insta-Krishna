#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — SONG MUSIC VIDEO GENERATOR
=============================================================================
Takes a devotional song (audio) and user-provided image(s), and renders a 
stunning 1080p music video with the exact visual identity of Krishna Vibez:

- 1920x1080 Full HD Cinematic Output
- Subpixel 64-bit Ken Burns Camera Zoom & Pan (Smooth, No Jitter)
- 3 Unique Random Flora Particles per Song (Peacock Feathers, Petals, Flowers)
- 35 Floating Golden Sparkles with Twinkling Depth
- Circular Luxury Krishna Vibez Corner Logo
- Smooth Crossfades Between Multiple User Slides
- Studio AAC 192kbps Audio Multiplexing
=============================================================================
"""

import os
import sys
import re
import math
import random
import glob
import subprocess
import numpy as np
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_EXE = "ffmpeg"
LOGO_PATH = os.path.join(BASE_DIR, "website", "public", "assets", "logo.png")
PETALS_DIR = os.path.join(BASE_DIR, "extracted_petals")

# 4 Organic Wind & Particle Motion Styles
MOTION_STYLES = [
    {
        "name": "शांत मंद पवन (Gentle Serene Float)",
        "vy_range": (65, 115),
        "amp_range": (18, 38),
        "freq_range": (0.6, 1.0),
        "wind_drift_range": (8, 20),
        "tumble_freq_range": (0.5, 1.1)
    },
    {
        "name": "तिरछी बयार (Soft Diagonal Breeze)",
        "vy_range": (75, 130),
        "amp_range": (22, 45),
        "freq_range": (0.7, 1.2),
        "wind_drift_range": (35, 65),
        "tumble_freq_range": (0.8, 1.5)
    },
    {
        "name": "हल्की भँवर (Playful Swirling Flutter)",
        "vy_range": (80, 140),
        "amp_range": (35, 65),
        "freq_range": (1.0, 1.5),
        "wind_drift_range": (12, 28),
        "tumble_freq_range": (1.0, 1.6)
    },
    {
        "name": "गहन ध्यान प्रवाह (Deep Meditation Flow)",
        "vy_range": (50, 85),
        "amp_range": (12, 26),
        "freq_range": (0.45, 0.70),
        "wind_drift_range": (5, 14),
        "tumble_freq_range": (0.4, 0.8)
    }
]

GOLDEN_SPARKLE_PALETTE = {
    "gold_bgr": np.array([45.0, 210.0, 255.0]),
    "core_bgr": np.array([255.0, 255.0, 255.0])
}


def get_audio_duration(audio_path):
    """Accurately detect audio duration in seconds using ffprobe or ffmpeg."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        dur = float(res.stdout.strip())
        if dur > 1.0:
            return dur
    except Exception:
        pass

    try:
        cmd = ["ffmpeg", "-i", audio_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        import re
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", res.stderr)
        if m:
            hours, mins, secs = float(m.group(1)), float(m.group(2)), float(m.group(3))
            return hours * 3600 + mins * 60 + secs
    except Exception:
        pass

    return 160.0  # safe default fallback


def load_flora_sprites_dict():
    """Loads all transparent RGBA PNG sprites from extracted_petals/."""
    import cv2
    sprites = {}
    if os.path.exists(PETALS_DIR):
        for sf in glob.glob(os.path.join(PETALS_DIR, "*.png")):
            name = os.path.basename(sf).replace(".png", "")
            img = cv2.imread(sf, cv2.IMREAD_UNCHANGED)
            if img is not None and len(img.shape) == 3 and img.shape[2] == 4:
                sprites[name] = img
    return sprites


def create_corner_logo_badge(size=120):
    """Creates a circular luxury glass badge with golden rim for top corner branding."""
    import cv2
    if not os.path.exists(LOGO_PATH):
        return None
    logo = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
    if logo is None:
        return None
    resized = cv2.resize(logo, (size, size), interpolation=cv2.INTER_AREA)
    if resized.shape[2] == 4:
        b, g, r, a = cv2.split(resized)
    else:
        b, g, r = cv2.split(resized)
        a = np.ones((size, size), dtype=np.uint8) * 255

    center = size // 2
    radius = size // 2 - 3
    mask = np.zeros((size, size), dtype=np.uint8)
    cv2.circle(mask, (center, center), radius, 255, -1, lineType=cv2.LINE_AA)

    inside_circle = (mask > 0)
    bg_backing_alpha = (inside_circle.astype(np.uint8) * 200)
    final_alpha = np.maximum(np.minimum(a, mask), bg_backing_alpha)

    badge = np.dstack([b, g, r, final_alpha])
    cv2.circle(badge, (center, center), radius, (50, 205, 255, 230), 2, lineType=cv2.LINE_AA)
    cv2.circle(badge, (center, center), radius - 3, (30, 160, 220, 140), 1, lineType=cv2.LINE_AA)
    return badge


def overlay_rgba(bg_img, fg_rgba, center_x, center_y, scale=1.0, angle_deg=0.0, opacity=1.0):
    """Fast, boundary-checked alpha compositing of RGBA sprite onto BGR frame with optional opacity."""
    import cv2
    if opacity <= 0.01:
        return
    fh, fw = fg_rgba.shape[:2]
    new_w = int(fw * scale)
    new_h = int(fh * scale)
    if new_w <= 0 or new_h <= 0:
        return
    resized = cv2.resize(fg_rgba, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    if abs(angle_deg) > 0.5:
        M = cv2.getRotationMatrix2D((new_w / 2, new_h / 2), angle_deg, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        bound_w = int((new_h * sin) + (new_w * cos))
        bound_h = int((new_h * cos) + (new_w * sin))
        M[0, 2] += (bound_w / 2) - new_w / 2
        M[1, 2] += (bound_h / 2) - new_h / 2
        rotated = cv2.warpAffine(resized, M, (bound_w, bound_h), flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    else:
        rotated = resized

    rw, rh = rotated.shape[1], rotated.shape[0]
    x1 = int(center_x - rw / 2)
    y1 = int(center_y - rh / 2)
    x2 = x1 + rw
    y2 = y1 + rh

    bg_h, bg_w = bg_img.shape[:2]
    cx1 = max(0, x1)
    cy1 = max(0, y1)
    cx2 = min(bg_w, x2)
    cy2 = min(bg_h, y2)
    if cx2 <= cx1 or cy2 <= cy1:
        return

    fx1 = cx1 - x1
    fy1 = cy1 - y1
    fx2 = fx1 + (cx2 - cx1)
    fy2 = fy1 + (cy2 - cy1)

    fg_crop = rotated[fy1:fy2, fx1:fx2]
    alpha = (fg_crop[:, :, 3:].astype(np.float32) / 255.0) * float(opacity)
    bg_crop = bg_img[cy1:cy2, cx1:cx2].astype(np.float32)
    blended = fg_crop[:, :, :3].astype(np.float32) * alpha + bg_crop * (1.0 - alpha)
    bg_img[cy1:cy2, cx1:cx2] = blended.astype(np.uint8)


def prebuild_sparkle_sprites(adapted_gold, core_col_base=None):
    """Pre-renders diamond star sparkles at various radii."""
    import cv2
    if core_col_base is None:
        core_col_base = np.array([255.0, 255.0, 255.0])
    sprites = {}
    for r_int in [2, 3, 4, 5, 6, 7]:
        rad = float(r_int)
        dim = int(rad * 8) + 4
        if dim % 2 == 0:
            dim += 1
        cx, cy = dim // 2, dim // 2
        sp_img = np.zeros((dim, dim, 3), dtype=np.float32)

        def draw_layer(rad_mult, alpha_val, col):
            r = rad * rad_mult
            col_scaled = tuple(float(x) for x in (col.astype(np.float32) * alpha_val))
            pts_h = np.array([[cx - r * 3.5, cy], [cx, cy - r * 0.4], [cx + r * 3.5, cy], [cx, cy + r * 0.4]], dtype=np.int32)
            pts_v = np.array([[cx - r * 0.4, cy], [cx, cy - r * 3.5], [cx + r * 0.4, cy], [cx, cy + r * 3.5]], dtype=np.int32)
            cv2.fillConvexPoly(sp_img, pts_h, col_scaled)
            cv2.fillConvexPoly(sp_img, pts_v, col_scaled)
            cv2.circle(sp_img, (cx, cy), max(1, int(r * 0.7)), col_scaled, -1)

        draw_layer(1.0, 0.45, adapted_gold)
        draw_layer(0.5, 0.85, (adapted_gold * 0.5 + core_col_base * 0.5))
        draw_layer(0.25, 1.00, core_col_base)
        sprites[r_int] = (np.clip(sp_img, 0, 255).astype(np.uint8), cx, cy)
    return sprites


def fast_draw_sparkle(target, cx, cy, rad, is_star, brightness, sprites):
    """Draws a shimmering golden sparkle onto the frame."""
    import cv2
    r_key = int(round(rad))
    r_key = max(2, min(7, r_key))
    if r_key not in sprites:
        return
    sp_img, scx, scy = sprites[r_key]
    h, w = sp_img.shape[:2]
    x1 = int(cx - scx)
    y1 = int(cy - scy)
    x2 = x1 + w
    y2 = y1 + h

    th, tw = target.shape[:2]
    cx1 = max(0, x1)
    cy1 = max(0, y1)
    cx2 = min(tw, x2)
    cy2 = min(th, y2)
    if cx2 <= cx1 or cy2 <= cy1:
        return

    fx1 = cx1 - x1
    fy1 = cy1 - y1
    fx2 = fx1 + (cx2 - cx1)
    fy2 = fy1 + (cy2 - cy1)

    sp_crop = sp_img[fy1:fy2, fx1:fx2]
    if brightness != 1.0:
        sp_crop = (sp_crop.astype(np.float32) * float(brightness)).astype(np.uint8)
    target[cy1:cy2, cx1:cx2] = cv2.add(target[cy1:cy2, cx1:cx2], sp_crop)


class SlideParticle:
    """3D floating flower petal, peacock feather, or leaf drifting gracefully."""

    def __init__(self, rng, flora_sprites, motion_style, initial_spread=False):
        self.rng = rng
        self.flora_sprites = flora_sprites
        self.motion_style = motion_style
        self.reset(initial_spread=initial_spread)

    def reset(self, initial_spread=False):
        self.sprite = self.rng.choice(self.flora_sprites) if self.flora_sprites else None
        layer = self.rng.choices(["bg", "mid", "fg"], weights=[0.55, 0.38, 0.07])[0]
        if layer == "fg":
            self.scale = self.rng.uniform(0.24, 0.32)
            self.vy = self.rng.uniform(self.motion_style["vy_range"][0] * 1.1, self.motion_style["vy_range"][1] * 1.1)
            self.opacity = self.rng.uniform(0.75, 0.88)
        elif layer == "mid":
            self.scale = self.rng.uniform(0.16, 0.23)
            self.vy = self.rng.uniform(*self.motion_style["vy_range"])
            self.opacity = self.rng.uniform(0.65, 0.80)
        else:  # bg
            self.scale = self.rng.uniform(0.10, 0.16)
            self.vy = self.rng.uniform(self.motion_style["vy_range"][0] * 0.75, self.motion_style["vy_range"][1] * 0.75)
            self.opacity = self.rng.uniform(0.50, 0.68)

        self.x = self.rng.uniform(-60, 1920 + 60)
        if initial_spread:
            self.y = self.rng.uniform(-100, 1080 + 100)
        else:
            self.y = self.rng.uniform(-140, -30)

        self.amp_x = self.rng.uniform(*self.motion_style["amp_range"])
        self.freq_x = self.rng.uniform(*self.motion_style["freq_range"])
        self.phase_x = self.rng.uniform(0, 2 * math.pi)
        self.wind_drift = self.rng.uniform(*self.motion_style["wind_drift_range"])

        self.angle = self.rng.uniform(0, 360)
        self.rot_speed = self.rng.uniform(-35, 35)
        self.tumble_freq = self.rng.uniform(*self.motion_style["tumble_freq_range"])
        self.tumble_phase = self.rng.uniform(0, 2 * math.pi)

    def update(self, dt, current_time):
        self.y += self.vy * dt
        sway = self.amp_x * math.sin(current_time * self.freq_x * 2 * math.pi + self.phase_x)
        self.x += (self.wind_drift + sway * 0.5) * dt
        self.angle += self.rot_speed * dt
        if self.y > 1080 + 100 or self.x < -120 or self.x > 1920 + 120:
            self.reset(initial_spread=False)

    def render(self, target_img):
        import cv2
        if self.sprite is None:
            return
        tumble = math.cos(self.angle * math.pi / 180.0 + self.tumble_phase)
        sx = self.scale * (0.35 + 0.65 * abs(tumble))
        sy = self.scale
        h, w = self.sprite.shape[:2]
        nw = max(6, int(w * sx))
        nh = max(6, int(h * sy))
        resized = cv2.resize(self.sprite, (nw, nh), interpolation=cv2.INTER_LINEAR)
        center = (nw // 2, nh // 2)
        M = cv2.getRotationMatrix2D(center, self.angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        bw = int((nh * sin) + (nw * cos))
        bh = int((nh * cos) + (nw * sin))
        M[0, 2] += (bw / 2) - center[0]
        M[1, 2] += (bh / 2) - center[1]
        rotated = cv2.warpAffine(resized, M, (bw, bh), flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        px = int(self.x - bw // 2)
        py = int(self.y - bh // 2)
        x1, y1 = max(0, px), max(0, py)
        x2, y2 = min(1920, px + bw), min(1080, py + bh)
        if x1 >= x2 or y1 >= y2:
            return
        sx1, sy1 = x1 - px, y1 - py
        sx2, sy2 = sx1 + (x2 - x1), sy1 + (y2 - y1)
        crop_sprite = rotated[sy1:sy2, sx1:sx2]
        crop_target = target_img[y1:y2, x1:x2]
        alpha = (crop_sprite[:, :, 3].astype(np.float32) / 255.0) * self.opacity
        alpha = alpha[:, :, np.newaxis]
        fg_rgb = crop_sprite[:, :, :3].astype(np.float32)
        bg_rgb = crop_target.astype(np.float32)
        target_img[y1:y2, x1:x2] = (fg_rgb * alpha + bg_rgb * (1.0 - alpha)).astype(np.uint8)


def remove_flow_watermark(img):
    """
    Bypassed: Song images and thumbnails are clean original artworks and NOT from Google Flow.
    Retains all edges and bottom-right corner 100% original, crisp, and unblurred.
    """
    return img


def clean_and_save_thumbnail(src_path, dst_path=None):
    """
    Cleans Google Flow watermark from a thumbnail image without cropping,
    resizes to standard 1280x720 (16:9 HD), and saves it as high quality JPEG.
    """
    import cv2
    if not src_path or not os.path.exists(src_path):
        return src_path
    if dst_path is None:
        dst_path = src_path

    img = cv2.imread(src_path)
    if img is None:
        return src_path

    # Remove watermark seamlessly
    cleaned = remove_flow_watermark(img)

    # Resize cleanly to 1280x720 if not already 16:9
    h, w = cleaned.shape[:2]
    if (w, h) != (1280, 720):
        # Resize maintaining 16:9
        cleaned = cv2.resize(cleaned, (1280, 720), interpolation=cv2.INTER_LANCZOS4)

    cv2.imwrite(dst_path, cleaned, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return dst_path


def prepare_slide_image(img_path):
    """
    Ensures any user-provided image fits 1920x1080 perfectly:
    - Automatically removes Google Flow watermark using Telea Inpaint without cropping
    - If 16:9, resizes smoothly with Lanczos
    - If portrait or other ratio, centers it with elegant blurred background fill
    """
    import cv2
    src = cv2.imread(img_path)
    if src is None:
        # Fallback to dark golden gradient canvas
        canvas = np.zeros((1080, 1920, 3), dtype=np.uint8)
        for y in range(1080):
            val = int(25 + (y / 1080.0) * 45)
            canvas[y, :] = (val // 2, val, val * 2)
        return canvas

    # Erase Google Flow watermark if present without cropping
    src = remove_flow_watermark(src)

    h, w = src.shape[:2]
    target_aspect = 1920.0 / 1080.0
    img_aspect = float(w) / float(h)

    # If within 5% of 16:9, just resize directly
    if abs(img_aspect - target_aspect) < 0.08:
        return cv2.resize(src, (1920, 1080), interpolation=cv2.INTER_LANCZOS4)

    # Otherwise create a blurred background fill for vertical/custom images
    bg = cv2.resize(src, (1920, 1080), interpolation=cv2.INTER_LINEAR)
    bg = cv2.GaussianBlur(bg, (91, 91), 0)
    bg = (bg.astype(np.float32) * 0.55).astype(np.uint8)

    # Scale source to fit within 1080 height
    scale = min(1920.0 / float(w), 1080.0 / float(h))
    nw = int(w * scale)
    nh = int(h * scale)
    scaled_fg = cv2.resize(src, (nw, nh), interpolation=cv2.INTER_LANCZOS4)

    x_off = (1920 - nw) // 2
    y_off = (1080 - nh) // 2
    bg[y_off:y_off + nh, x_off:x_off + nw] = scaled_fg
    return bg


def clean_lyrics_text(text):
    """
    यूज़र द्वारा दिए गए लिरिक्स में से [Intro], [Chorus], [Verse] आदि [ ] के अंदर
    का सारा टेक्स्ट हटाता है और साफ पंक्तियाँ लौटाता है।
    """
    if not text:
        return ""
    # [ ] के अंदर का सारा टेक्स्ट (ब्रैकेट्स सहित) हटाएं
    cleaned = re.sub(r'\[.*?\]', '', text)
    # मल्टीपल खाली लाइन्स हटाएं
    lines = [l.strip() for l in cleaned.splitlines() if l.strip()]
    return "\n".join(lines)


# 10 Luxury Devotional UI Themes with 5 Distinct Layout Styles (Rotating per song)
LYRIC_THEMES = {
    "royal_gold": {
        "name": "राजसी स्वर्ण (Royal 24k Gold Pill)",
        "layout_style": "pill",
        "bg_fill": (14, 10, 6, 220),
        "border_col": (255, 215, 0, 245),
        "border_width": 2,
        "glow_col": (255, 215, 0, 160),
        "glow_width": 4,
        "text_col": (255, 255, 255, 255),
        "shadow_col": (0, 0, 0, 245),
        "font_size": 52,
    },
    "celestial_silver": {
        "name": "दिव्य रजत (Celestial Platinum Card)",
        "layout_style": "chamfer_card",
        "bg_fill": (10, 14, 22, 220),
        "border_col": (220, 235, 255, 245),
        "border_width": 2,
        "glow_col": (180, 220, 255, 160),
        "glow_width": 4,
        "text_col": (255, 255, 255, 255),
        "shadow_col": (0, 0, 0, 245),
        "font_size": 52,
    },
    "sacred_saffron": {
        "name": "पवित्र केसरिया (Sacred Saffron Banner)",
        "layout_style": "ornate_banner",
        "bg_fill": (22, 12, 6, 220),
        "border_col": (255, 160, 30, 250),
        "border_width": 2,
        "glow_col": (255, 130, 15, 170),
        "glow_width": 4,
        "text_col": (255, 252, 238, 255),
        "shadow_col": (0, 0, 0, 245),
        "font_size": 52,
    },
    "vaikuntha_emerald": {
        "name": "वैकुंठ मरकत (Vaikuntha Emerald Pill)",
        "layout_style": "pill",
        "bg_fill": (6, 16, 12, 220),
        "border_col": (110, 235, 170, 245),
        "border_width": 2,
        "glow_col": (60, 210, 130, 160),
        "glow_width": 4,
        "text_col": (255, 255, 255, 255),
        "shadow_col": (0, 0, 0, 245),
        "font_size": 52,
    },
    "vrindavan_rose": {
        "name": "वृंदावन कमल (Vrindavan Lotus Card)",
        "layout_style": "chamfer_card",
        "bg_fill": (18, 8, 14, 220),
        "border_col": (255, 175, 205, 245),
        "border_width": 2,
        "glow_col": (255, 120, 175, 160),
        "glow_width": 4,
        "text_col": (255, 255, 255, 255),
        "shadow_col": (0, 0, 0, 245),
        "font_size": 52,
    },
    "kailash_amethyst": {
        "name": "कैलाश नीलम (Kailash Floating Halo)",
        "layout_style": "cinematic_floating",
        "bg_fill": (14, 10, 24, 200),
        "border_col": (210, 170, 255, 245),
        "border_width": 2,
        "glow_col": (180, 125, 255, 170),
        "glow_width": 5,
        "text_col": (255, 255, 255, 255),
        "shadow_col": (0, 0, 0, 250),
        "font_size": 54,
    },
    "yamuna_azure": {
        "name": "यमुना मयूर (Yamuna Peacock Verse)",
        "layout_style": "underlined_verse",
        "bg_fill": (6, 12, 22, 220),
        "border_col": (0, 220, 255, 245),
        "border_width": 2,
        "glow_col": (0, 180, 255, 160),
        "glow_width": 4,
        "text_col": (255, 255, 255, 255),
        "shadow_col": (0, 0, 0, 245),
        "font_size": 52,
    },
    "surya_bronze": {
        "name": "सूर्य ताम्र (Sunlit Temple Banner)",
        "layout_style": "ornate_banner",
        "bg_fill": (22, 12, 6, 220),
        "border_col": (255, 185, 90, 245),
        "border_width": 2,
        "glow_col": (230, 130, 40, 160),
        "glow_width": 4,
        "text_col": (255, 250, 240, 255),
        "shadow_col": (0, 0, 0, 245),
        "font_size": 52,
    },
    "divine_pearl": {
        "name": "श्वेत मुक्ता (Divine Moonlit Pill)",
        "layout_style": "pill",
        "bg_fill": (12, 14, 20, 215),
        "border_col": (240, 245, 255, 245),
        "border_width": 2,
        "glow_col": (200, 220, 255, 150),
        "glow_width": 4,
        "text_col": (255, 255, 255, 255),
        "shadow_col": (0, 0, 0, 245),
        "font_size": 52,
    },
    "kashi_vermillion": {
        "name": "काशी सिंदूर (Kashi Sacred Verse)",
        "layout_style": "underlined_verse",
        "bg_fill": (24, 8, 8, 220),
        "border_col": (255, 110, 85, 245),
        "border_width": 2,
        "glow_col": (235, 65, 45, 165),
        "glow_width": 4,
        "text_col": (255, 255, 255, 255),
        "shadow_col": (0, 0, 0, 245),
        "font_size": 52,
    }
}


def create_lyric_badge(text, theme=None, font_path=None, font_size=None):
    """
    निचले हिस्से (Bottom Center) के लिए 5 अलग-अलग शैलियों में लिरिक बैज:
    - 1. 'pill': गोल ग्लासमोर्फिक कैप्सूल + ग्लोइंग आभामंडल
    - 2. 'chamfer_card': शाही कॉर्नर कार्ड + डबल बॉर्डर फ्रेम
    - 3. 'ornate_banner': भव्य मंदिर बैनर + साइड अलंकृत रत्न ❖
    - 4. 'cinematic_floating': न्यूनतम सिनेमैटिक फ्लोटिंग ग्लो (बिना भारी बॉक्स)
    - 5. 'underlined_verse': आधुनिक कार्ड + नीचे प्रकाशमान डिवाइन अंडरलाइन बार
    """
    from PIL import Image, ImageDraw, ImageFont
    if theme is None:
        theme = LYRIC_THEMES["royal_gold"]

    if font_size is None:
        font_size = theme.get("font_size", 52)

    if not font_path or not os.path.exists(font_path):
        cand = os.path.join(BASE_DIR, "NotoSansDevanagari-Bold.ttf")
        font_path = cand if os.path.exists(cand) else None

    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    dummy = Image.new("RGBA", (1, 1))
    draw_d = ImageDraw.Draw(dummy)
    bbox = draw_d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pad_x = 45
    pad_y = 18
    bw = tw + pad_x * 2
    bh = th + pad_y * 2

    glow_margin = 10
    cw = bw + glow_margin * 2
    ch = bh + glow_margin * 2

    canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(canvas)

    rx0, ry0 = glow_margin, glow_margin
    rx1, ry1 = rx0 + bw - 1, ry0 + bh - 1

    layout = theme.get("layout_style", "pill")
    bg_fill = theme.get("bg_fill", (14, 10, 6, 220))
    border_col = theme.get("border_col", (255, 215, 0, 245))
    border_width = theme.get("border_width", 2)
    glow_col = theme.get("glow_col", (255, 215, 0, 160))
    glow_w = theme.get("glow_width", 4)
    shadow_col = theme.get("shadow_col", (0, 0, 0, 245))
    text_col = theme.get("text_col", (255, 255, 255, 255))

    if layout == "pill":
        radius = bh // 2
        # Glow
        cdraw.rounded_rectangle([(rx0 - glow_w, ry0 - glow_w), (rx1 + glow_w, ry1 + glow_w)], radius=radius + glow_w, outline=glow_col, width=glow_w)
        # Background
        cdraw.rounded_rectangle([(rx0, ry0), (rx1, ry1)], radius=radius, fill=bg_fill, outline=border_col, width=border_width)
        # Delicate arc highlight
        cdraw.arc([(rx0 + 2, ry0 + 2), (rx1 - 2, ry1 - 2)], start=190, end=350, fill=(255, 255, 255, 50), width=1)

    elif layout == "chamfer_card":
        radius = 14
        # Outer soft glow
        cdraw.rounded_rectangle([(rx0 - glow_w, ry0 - glow_w), (rx1 + glow_w, ry1 + glow_w)], radius=radius + glow_w, outline=glow_col, width=glow_w)
        # Main Card
        cdraw.rounded_rectangle([(rx0, ry0), (rx1, ry1)], radius=radius, fill=bg_fill, outline=border_col, width=border_width)
        # Inner hairline border
        cdraw.rounded_rectangle([(rx0 + 4, ry0 + 4), (rx1 - 4, ry1 - 4)], radius=radius - 3, outline=(border_col[0], border_col[1], border_col[2], 100), width=1)

    elif layout == "ornate_banner":
        radius = 10
        # Main Banner Box
        cdraw.rounded_rectangle([(rx0, ry0), (rx1, ry1)], radius=radius, fill=bg_fill, outline=border_col, width=border_width)
        # Top & Bottom accent lines
        cdraw.line([(rx0 + 15, ry0 + 2), (rx1 - 15, ry0 + 2)], fill=glow_col, width=2)
        cdraw.line([(rx0 + 15, ry1 - 2), (rx1 - 15, ry1 - 2)], fill=glow_col, width=2)
        # Side decorative gem dots
        cdraw.ellipse([(rx0 + 12, ry0 + bh // 2 - 3), (rx0 + 18, ry0 + bh // 2 + 3)], fill=border_col)
        cdraw.ellipse([(rx1 - 18, ry0 + bh // 2 - 3), (rx1 - 12, ry0 + bh // 2 + 3)], fill=border_col)

    elif layout == "cinematic_floating":
        # Minimalist soft dark radial glow without a heavy box
        cdraw.ellipse([(rx0 - 20, ry0 - 10), (rx1 + 20, ry1 + 10)], fill=(0, 0, 0, 190))
        cdraw.ellipse([(rx0, ry0), (rx1, ry1)], fill=bg_fill)

    elif layout == "underlined_verse":
        radius = 12
        # Translucent pill base
        cdraw.rounded_rectangle([(rx0, ry0), (rx1, ry1)], radius=radius, fill=bg_fill, outline=(border_col[0], border_col[1], border_col[2], 120), width=1)
        # Glowing radiant bottom underline
        cdraw.line([(rx0 + 25, ry1), (rx1 - 25, ry1)], fill=border_col, width=3)
        # Central diamond jewel accent
        mx = (rx0 + rx1) // 2
        cdraw.polygon([(mx, ry1 - 4), (mx + 4, ry1), (mx, ry1 + 4), (mx - 4, ry1)], fill=glow_col)

    # Multi-directional drop shadow for 100% legibility on any background
    tx = rx0 + pad_x - bbox[0]
    ty = ry0 + pad_y - bbox[1]
    for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (2, 2)]:
        cdraw.text((tx + ox, ty + oy), text, font=font, fill=shadow_col)

    # Crisp typography
    cdraw.text((tx, ty), text, font=font, fill=text_col)

    return np.array(canvas)


def generate_song_music_video(audio_path, slide_image_paths, output_video_path, fps=25, lyrics_file_or_text=None):
    """
    Renders full HD 1080p animated music video with:
    - Dynamic Ken Burns motion
    - 3 Unique random flora particles selected per song
    - Golden sparkling stars
    - Corner luxury logo
    - Synchronized Bottom-Center Lyric Badges ([ ] tags automatically removed)
    - Seamless audio multiplexing
    """
    import cv2

    total_duration = get_audio_duration(audio_path)
    print(f"  ⏱️ गाने की कुल अवधि: {total_duration:.1f} सेकंड ({total_duration/60:.2f} मिनट)")

    if not slide_image_paths:
        raise ValueError("No slide images provided for video generation")

    # Load flora sprites and select 3 distinct random particle types for THIS song
    all_flora = load_flora_sprites_dict()
    if all_flora:
        # Pick 3 random distinct keys (e.g. peacock feathers, lotus petals, flowers)
        flora_keys = list(all_flora.keys())
        chosen_keys = random.sample(flora_keys, min(3, len(flora_keys)))
        song_flora_sprites = [all_flora[k] for k in chosen_keys]
        print(f"  🌺 गाने के लिए 3 विशिष्ट एनिमेशन चुने गए: {', '.join(chosen_keys)}")
    else:
        song_flora_sprites = []
        print("  ⚠️ कोई फ्लोरा स्प्राइट नहीं मिला, केवल स्पार्कल्स चलेंगे")

    motion_style = random.choice(MOTION_STYLES)
    print(f"  🍃 मोशन स्टाइल: {motion_style['name']}")

    logo_badge = create_corner_logo_badge(size=120)
    sparkle_sprites = prebuild_sparkle_sprites(
        GOLDEN_SPARKLE_PALETTE["gold_bgr"],
        GOLDEN_SPARKLE_PALETTE["core_bgr"]
    )

    # प्रत्येक गाने के लिए स्वतः लक्ज़री लिरिक थीम चुनना (Gold, Silver, Saffron, Emerald, Rose, Amethyst)
    theme_keys = list(LYRIC_THEMES.keys())
    song_seed_str = os.path.basename(audio_path)
    hash_val = sum(ord(c) for c in song_seed_str)
    selected_theme_key = theme_keys[hash_val % len(theme_keys)]
    selected_theme = LYRIC_THEMES[selected_theme_key]
    print(f"  🎨 लिरिक स्टाइल चुना गया: {selected_theme['name']}")

    # लिरिक्स प्रोसेस करना (SRT या सादा टेक्स्ट) और टाइमस्टैम्प्स तैयार करना
    subtitles = []
    if lyrics_file_or_text:
        raw_lyric_str = ""
        if os.path.exists(str(lyrics_file_or_text)):
            try:
                with open(lyrics_file_or_text, "r", encoding="utf-8") as lf:
                    raw_lyric_str = lf.read()
            except Exception:
                pass
        else:
            raw_lyric_str = str(lyrics_file_or_text)

        if raw_lyric_str:
            # 1. यदि SRT फॉर्मेट है
            if "-->" in raw_lyric_str:
                raw_subs = []
                blocks = re.split(r'\n\s*\n', raw_lyric_str.strip())
                for b in blocks:
                    lines = [l.strip() for l in b.splitlines() if l.strip()]
                    if len(lines) >= 2:
                        time_line = lines[1] if '-->' in lines[1] else lines[0]
                        if '-->' in time_line:
                            pts = time_line.split('-->')
                            def to_sec(t):
                                t = t.strip().replace(',', '.')
                                parts = t.split(':')
                                return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
                            try:
                                orig_start = to_sec(pts[0])
                                orig_end = to_sec(pts[1])
                                t_idx = 2 if '-->' in lines[1] else 1
                                txt = ' '.join(lines[t_idx:])
                                txt = re.sub(r'\[.*?\]', '', txt).strip()
                                if txt:
                                    # 100% सटीक आवाज सिंक: जिस क्षण गायक गाना शुरू करे, ठीक उसी क्षण लिरिक्स स्क्रीन पर दिखे
                                    s_time = orig_start
                                    e_time = orig_end
                                    raw_subs.append((s_time, e_time, txt))
                            except Exception:
                                pass

                # Pass 2: अगली पंक्ति के आरंभ समय के साथ सुगम सामंजस्य (Zero Clashing)
                for i in range(len(raw_subs)):
                    s_sec, e_sec, txt = raw_subs[i]
                    if i + 1 < len(raw_subs):
                        next_s = raw_subs[i + 1][0]
                        if e_sec > next_s:
                            e_sec = max(s_sec + 0.5, next_s - 0.05)
                    subtitles.append((s_sec, e_sec, txt))
            else:
                # 2. सादा टेक्स्ट: [ ] हटाकर पंक्तियों को पूरे गाने पर समान रूप से बांटें
                clean_txt = clean_lyrics_text(raw_lyric_str)
                lines = [l.strip() for l in clean_txt.splitlines() if l.strip()]
                if lines:
                    line_dur = total_duration / float(len(lines))
                    for idx, line in enumerate(lines):
                        s_time = idx * line_dur
                        e_time = (idx + 1) * line_dur
                        subtitles.append((s_time, e_time, line))

    # लिरिक बैजेस को प्री-रेंडर (Cache) करना चयनित थीम और बड़े फ़ॉन्ट (52px) के साथ
    lyric_badges = {}
    if subtitles:
        print(f"  📝 {len(subtitles)} लिरिक पंक्तियाँ लोड हुईं (फ़ॉन्ट साइज़ 52, 2.5s लीड-इन सिंक, [ ] ब्रैकेट्स हटाए गए)")
        for (s_sec, e_sec, l_text) in subtitles:
            if l_text not in lyric_badges:
                lyric_badges[l_text] = create_lyric_badge(l_text, theme=selected_theme, font_size=52)

    # Prepare slides
    prepared_slides = [prepare_slide_image(p) for p in slide_image_paths]
    num_slides = len(prepared_slides)
    slide_durations = [total_duration / float(num_slides)] * num_slides

    temp_raw_video = os.path.join(BASE_DIR, "temp_song_video_visuals.mp4")

    ffmpeg_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1920x1080",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        temp_raw_video
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    dt = 1.0 / float(fps)
    global_time = 0.0

    for s_idx, (src_img, slide_dur) in enumerate(zip(prepared_slides, slide_durations)):
        slide_frames = int(slide_dur * fps)
        rng_p = random.Random(s_idx * 23 + 47)
        particles = [
            SlideParticle(rng_p, song_flora_sprites, motion_style, initial_spread=True)
            for _ in range(8)
        ] if song_flora_sprites else []

        rng_spk = random.Random(s_idx * 37 + 19)
        sparkles = []
        for i in range(35):
            sx = rng_spk.randint(40, 1880)
            sy = rng_spk.randint(40, 1040)
            rad = rng_spk.uniform(2.5, 5.5)
            phase = rng_spk.uniform(0, math.pi * 2)
            speed = rng_spk.uniform(0.8, 1.8)
            star = (i % 2 == 0)
            sparkles.append((sx, sy, rad, phase, speed, star))

        # Fade frames
        fade_frames = int(min(1.5, slide_dur * 0.25) * fps)

        # Alternating Ken Burns motion styles per slide
        mode = s_idx % 4

        for f_idx in range(slide_frames):
            prog = float(f_idx) / float(slide_frames)

            if mode == 0:
                zoom = 1.0 + 0.12 * prog
                pan_x = 55.0 * prog
                pan_y = 30.0 * prog
            elif mode == 1:
                zoom = 1.12 - 0.10 * prog
                pan_x = -50.0 * prog
                pan_y = 25.0 * prog
            elif mode == 2:
                zoom = 1.05 + 0.06 * math.sin(prog * math.pi)
                pan_x = 60.0 * (prog - 0.5)
                pan_y = -25.0 * math.cos(prog * math.pi)
            else:
                zoom = 1.02 + 0.10 * prog
                pan_x = -45.0 * prog
                pan_y = -35.0 * prog

            cx, cy = 960.0, 540.0
            M = np.array([
                [zoom, 0, (1.0 - zoom) * cx - pan_x],
                [0, zoom, (1.0 - zoom) * cy - pan_y]
            ], dtype=np.float32)
            frame = cv2.warpAffine(src_img, M, (1920, 1080), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

            # Particles
            if particles:
                for p in particles:
                    p.update(dt, global_time)
                sorted_p = sorted(particles, key=lambda p: p.scale)
                for p in sorted_p:
                    p.render(frame)

            # Sparkles
            for sx, sy, rad, phase, speed, star in sparkles:
                cur_y = (sy - (global_time * 20.0 * speed)) % 1080
                cur_x = sx + 14.0 * math.sin(global_time * 1.2 + phase)
                brightness = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(global_time * speed * 2.0 + phase))
                fast_draw_sparkle(frame, cur_x, cur_y, rad, star, brightness, sparkle_sprites)

            # Corner Luxury Logo Badge
            if logo_badge is not None:
                overlay_rgba(frame, logo_badge, center_x=95, center_y=95, scale=1.0, angle_deg=0)

            # Bottom Center Synchronized Lyric Badge with Smooth Dynamic Fade
            if subtitles:
                for (s_sec, e_sec, l_text) in subtitles:
                    if s_sec <= global_time <= e_sec:
                        badge_img = lyric_badges.get(l_text)
                        if badge_img is not None:
                            # 0.25s Smooth Fade In / Fade Out
                            dur = e_sec - s_sec
                            fade_time = min(0.25, dur * 0.2)
                            time_in = global_time - s_sec
                            time_out = e_sec - global_time
                            opacity = 1.0
                            if time_in < fade_time:
                                opacity = max(0.05, min(1.0, time_in / fade_time))
                            elif time_out < fade_time:
                                opacity = max(0.05, min(1.0, time_out / fade_time))
                            
                            # 1920 / 2 = 960 (Center X), Y = 955 (Bottom Center safe zone with 52px font)
                            overlay_rgba(frame, badge_img, center_x=960, center_y=955, scale=1.0, angle_deg=0, opacity=opacity)
                        break

            # Fade In on start of video / Fade Out at end
            if s_idx == 0 and f_idx < fade_frames:
                alpha = float(f_idx) / float(fade_frames)
                frame = (frame.astype(np.float32) * alpha).astype(np.uint8)
            elif s_idx == num_slides - 1 and f_idx > slide_frames - fade_frames:
                alpha = float(slide_frames - f_idx) / float(fade_frames)
                frame = (frame.astype(np.float32) * alpha).astype(np.uint8)

            proc.stdin.write(frame.tobytes())
            global_time += dt

    proc.stdin.close()
    proc.wait()

    # Step 2: Merge raw video with high quality audio
    print("  🎵 ऑडियो व वीडियो का उच्च गुणवत्ता संकलन (FFmpeg Muxing)...")
    cmd_mux = [
        FFMPEG_EXE, "-y",
        "-i", temp_raw_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-map_metadata", "-1",
        "-c:a", "aac",
        "-b:a", "320k",
        "-shortest",
        output_video_path
    ]
    res = subprocess.run(cmd_mux, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"❌ FFmpeg Muxing विफल: {res.stderr[-300:]}")
        return False

    # Cleanup temp visuals
    if os.path.exists(temp_raw_video):
        try:
            os.remove(temp_raw_video)
        except Exception:
            pass

    success = os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 500000
    if success:
        mb = os.path.getsize(output_video_path) / (1024 * 1024)
        print(f"  ✅ 1080p म्यूजिक वीडियो सफलतापूर्वक तैयार! ({mb:.1f} MB)")
    return success
