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


def overlay_rgba(bg_img, fg_rgba, center_x, center_y, scale=1.0, angle_deg=0.0):
    """Fast, boundary-checked alpha compositing of RGBA sprite onto BGR frame."""
    import cv2
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
    alpha = fg_crop[:, :, 3:].astype(np.float32) / 255.0
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
    Universal Google Flow Star Watermark Remover:
    Automatically locates and completely erases the 4-pointed Flow watermark
    from the bottom-right corner without cropping or distorting the image.
    Works dynamically for any 16:9 or custom resolution image.
    """
    import cv2
    if img is None:
        return img
    h, w = img.shape[:2]

    # Coordinates of Flow watermark: 77% to 96% Y, 86% to 100% X
    y1 = int(h * 0.77)
    y2 = int(h * 0.96)
    x1 = int(w * 0.86)
    x2 = w

    corner = img[y1:y2, x1:x2]
    gray = cv2.cvtColor(corner, cv2.COLOR_BGR2GRAY)

    # 1. Target the star brightness
    _, thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    # 2. Targeted circular inpaint core for Flow star
    ch, cw = corner.shape[:2]
    cv2.circle(dilated, (int(cw * 0.65), int(ch * 0.5)), int(min(cw, ch) * 0.35), 255, -1)

    # 3. Create full frame mask
    full_mask = np.zeros((h, w), dtype=np.uint8)
    full_mask[y1:y2, x1:x2] = dilated

    # 4. Telea Inpaint (Fills seamlessly using surrounding natural pixels)
    cleaned = cv2.inpaint(img, full_mask, inpaintRadius=7, flags=cv2.INPAINT_TELEA)
    return cleaned


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


def generate_song_music_video(audio_path, slide_image_paths, output_video_path, fps=25):
    """
    Renders full HD 1080p animated music video with:
    - Dynamic Ken Burns motion
    - 3 Unique random flora particles selected per song
    - Golden sparkling stars
    - Corner luxury logo
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
        "-c:a", "aac",
        "-b:a", "192k",
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
