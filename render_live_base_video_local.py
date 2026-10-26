#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local high-speed renderer for 24/7 Live Stream Base Video Loop (1080p, 200s, 8 slides)
Renders with multi-core CPU/GPU locally in ~45 seconds, ready to SCP to Oracle Cloud.
"""

import os
import sys
import glob
import time
import math
import random
import subprocess
import cv2
import numpy as np

BASE_DIR = r"e:\Paresh\Auto Post\Auto-Insta-Krishna"
IMAGES_DIR = os.path.join(BASE_DIR, "music_video_images")
LOGO_PATH = os.path.join(BASE_DIR, "website", "public", "assets", "logo.png")
FEATHER_GREEN_SCREEN = os.path.join(BASE_DIR, "morpankh_green_screen.mp4")
OUTPUT_BASE_VIDEO = os.path.join(BASE_DIR, "live_base_video.mp4")
CLIPS_DIR = os.path.join(BASE_DIR, "live_clips_temp")
os.makedirs(CLIPS_DIR, exist_ok=True)

FFMPEG_EXE = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG_EXE):
    FFMPEG_EXE = "ffmpeg"


def create_corner_logo_badge(size=120):
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


def load_and_key_feather_frames():
    if not os.path.exists(FEATHER_GREEN_SCREEN):
        return []
    cap = cv2.VideoCapture(FEATHER_GREEN_SCREEN)
    raw_frames = []
    x1, x2 = 310, 970
    y1, y2 = 20, 700
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        raw_frames.append(frame[y1:y2, x1:x2])
    cap.release()
    
    keyed_frames = []
    for f in raw_frames:
        b = f[:, :, 0].astype(np.float32)
        g = f[:, :, 1].astype(np.float32)
        r = f[:, :, 2].astype(np.float32)
        greenness = g - np.maximum(r, b)
        alpha = np.clip(1.0 - (greenness - 25.0) / 45.0, 0.0, 1.0)
        alpha = (alpha * 255.0).astype(np.uint8)
        suppressed_g = np.minimum(g, np.maximum(r, b) * 1.15).astype(np.uint8)
        clean_rgb = np.stack([f[:, :, 0], suppressed_g, f[:, :, 2]], axis=-1)
        rgba = np.dstack([clean_rgb, alpha])
        
        # Golden halo around feather
        h, w = rgba.shape[:2]
        pad = 28
        padded = np.zeros((h + pad*2, w + pad*2, 4), dtype=np.uint8)
        padded[pad:pad+h, pad:pad+w] = rgba
        pad_alpha = padded[:, :, 3]
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
        dilated = cv2.dilate(pad_alpha, kernel, iterations=2)
        blurred_glow = cv2.GaussianBlur(dilated, (25, 25), 0).astype(np.float32) / 255.0
        
        glow_b = (blurred_glow * 45).astype(np.uint8)
        glow_g = (blurred_glow * 195).astype(np.uint8)
        glow_r = (blurred_glow * 255).astype(np.uint8)
        glow_a = (blurred_glow * 135).astype(np.uint8)
        glow_rgba = np.dstack([glow_b, glow_g, glow_r, glow_a])
        
        f_a = padded[:, :, 3:].astype(np.float32) / 255.0
        g_a = glow_rgba[:, :, 3:].astype(np.float32) / 255.0 * (1.0 - f_a)
        out_rgb = padded[:, :, :3].astype(np.float32) * f_a + glow_rgba[:, :, :3].astype(np.float32) * g_a
        out_a = np.clip(f_a + g_a, 0.0, 1.0) * 255.0
        keyed_frames.append(np.dstack([out_rgb.astype(np.uint8), out_a.astype(np.uint8)]))
    return keyed_frames


def overlay_rgba(bg_img, fg_rgba, center_x, center_y, scale, angle_deg):
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
        rotated = cv2.warpAffine(resized, M, (bound_w, bound_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
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
    if cx1 >= cx2 or cy1 >= cy2:
        return
        
    fx1 = cx1 - x1
    fy1 = cy1 - y1
    fx2 = fx1 + (cx2 - cx1)
    fy2 = fy1 + (cy2 - cy1)
    
    fg_crop = rotated[fy1:fy2, fx1:fx2]
    bg_crop = bg_img[cy1:cy2, cx1:cx2]
    
    alpha = fg_crop[:, :, 3:].astype(np.float32) / 255.0
    fg_bgr = fg_crop[:, :, :3].astype(np.float32)
    bg_bgr = bg_crop.astype(np.float32)
    blended = (fg_bgr * alpha + bg_bgr * (1.0 - alpha)).astype(np.uint8)
    bg_img[cy1:cy2, cx1:cx2] = blended


def get_image_adapted_gold(img_bgr):
    sample = cv2.resize(img_bgr, (64, 36), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(sample, cv2.COLOR_BGR2HSV)
    avg_val = np.mean(hsv[:, :, 2])
    avg_sat = np.mean(hsv[:, :, 1])
    if avg_val > 140:
        return (60, 215, 255)
    elif avg_sat < 70:
        return (100, 220, 255)
    else:
        return (35, 185, 255)


def prebuild_sparkle_sprites(gold_bgr):
    b, g, r = gold_bgr
    sprites = {}
    for rad_int in range(2, 8):
        size = rad_int * 6 + 1
        c = size // 2
        circle_img = np.zeros((size, size, 4), dtype=np.uint8)
        for y in range(size):
            for x in range(size):
                d = math.hypot(x - c, y - c)
                if d <= rad_int * 2.2:
                    a = max(0.0, 1.0 - d / (rad_int * 2.2))
                    a = int((a ** 1.5) * 230)
                    circle_img[y, x] = [b, g, r, a]
        star_img = circle_img.copy()
        for i in range(-rad_int * 2, rad_int * 2 + 1):
            if 0 <= c + i < size:
                al = int(240 * (1.0 - abs(i) / (rad_int * 2 + 1)))
                star_img[c, c + i] = [255, 255, 255, max(int(star_img[c, c + i, 3]), al)]
                star_img[c + i, c] = [255, 255, 255, max(int(star_img[c + i, c, 3]), al)]
        sprites[(rad_int, False)] = circle_img
        sprites[(rad_int, True)] = star_img
    return sprites


def fast_draw_sparkle(frame, x, y, rad, star, brightness, sprites):
    rad_int = max(2, min(7, int(round(rad))))
    sprite = sprites.get((rad_int, star))
    if sprite is None:
        return
    sh, sw = sprite.shape[:2]
    x1 = int(round(x)) - sw // 2
    y1 = int(round(y)) - sh // 2
    x2 = x1 + sw
    y2 = y1 + sh
    fh, fw = frame.shape[:2]
    cx1 = max(0, x1)
    cy1 = max(0, y1)
    cx2 = min(fw, x2)
    cy2 = min(fh, y2)
    if cx1 >= cx2 or cy1 >= cy2:
        return
    sx1 = cx1 - x1
    sy1 = cy1 - y1
    sx2 = sx1 + (cx2 - cx1)
    sy2 = sy1 + (cy2 - cy1)
    
    sp_crop = sprite[sy1:sy2, sx1:sx2]
    alpha = (sp_crop[:, :, 3].astype(np.float32) / 255.0) * brightness
    alpha = alpha[:, :, np.newaxis]
    sp_bgr = sp_crop[:, :, :3].astype(np.float32)
    bg_bgr = frame[cy1:cy2, cx1:cx2].astype(np.float32)
    frame[cy1:cy2, cx1:cx2] = (sp_bgr * alpha + bg_bgr * (1.0 - alpha)).astype(np.uint8)


def generate_feather_configs(seed=108):
    rng = random.Random(seed)
    return [
        {"type": "breeze", "scale": rng.uniform(0.70, 0.85), "base_x": rng.randint(1450, 1680), "base_y": rng.randint(480, 680), "amp_x": 35, "amp_y": 25, "freq_x": 0.35, "freq_y": 0.45, "base_rot": rng.uniform(-15, 10), "amp_rot": 8, "offset": rng.randint(0, 100)},
        {"type": "falling", "scale": rng.uniform(0.35, 0.48), "base_x": rng.randint(350, 750), "drift_cycle": rng.uniform(16.0, 22.0), "drift_phase": rng.uniform(0, 15), "amp_x": 45, "freq_x": 0.55, "amp_rot": 18, "offset": rng.randint(0, 100)},
        {"type": "falling", "scale": rng.uniform(0.20, 0.30), "base_x": rng.randint(950, 1400), "drift_cycle": rng.uniform(14.0, 19.0), "drift_phase": rng.uniform(0, 15), "amp_x": 30, "freq_x": 0.65, "amp_rot": 22, "offset": rng.randint(0, 100)},
        {"type": "breeze", "scale": rng.uniform(0.40, 0.52), "base_x": rng.randint(220, 420), "base_y": rng.randint(650, 850), "amp_x": 28, "amp_y": 20, "freq_x": 0.38, "freq_y": 0.48, "base_rot": rng.uniform(10, 35), "amp_rot": 10, "offset": rng.randint(0, 100)}
    ]


def render_all():
    slides = sorted(glob.glob(os.path.join(IMAGES_DIR, "*.jpg")))[:16]
    print(f"Selected {len(slides)} diverse slides for 4-minute 24/7 Live base loop. Starting high-speed render...")
    logo_badge = create_corner_logo_badge(size=120)
    feather_frames = load_and_key_feather_frames()
    
    clip_paths = []
    fps = 25
    clip_duration = 15
    total_frames = int(clip_duration * fps)
    fade_frames = int(1.2 * fps)
    
    for idx, slide_path in enumerate(slides):
        clip_path = os.path.join(CLIPS_DIR, f"clip_{idx+1:02d}.mp4")
        clip_paths.append(clip_path)
        print(f"[{idx+1}/{len(slides)}] Rendering Slide {os.path.basename(slide_path)}...")
        
        src_img = cv2.imread(slide_path)
        src_img = cv2.resize(src_img, (1920, 1080), interpolation=cv2.INTER_LANCZOS4)
        adapted_gold = get_image_adapted_gold(src_img)
        sprites = prebuild_sparkle_sprites(adapted_gold)
        feather_configs = generate_feather_configs(seed=idx * 23 + 108)
        
        rng_spk = random.Random(idx * 47 + 108)
        sparkles = []
        for i in range(45):
            sx = rng_spk.randint(40, 1880)
            sy = rng_spk.randint(40, 1040)
            rad = rng_spk.uniform(2.5, 6.2)
            phase = rng_spk.uniform(0, math.pi * 2)
            speed = rng_spk.uniform(0.8, 1.8)
            star = (i % 2 == 0)
            sparkles.append((sx, sy, rad, phase, speed, star))
            
        cmd = [
            FFMPEG_EXE, "-y",
            "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", "1920x1080", "-pix_fmt", "bgr24", "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            clip_path
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        
        for i in range(total_frames):
            t = i / float(fps)
            mode = idx % 3
            if mode == 0:
                zoom = 1.0 + 0.06 * (t / float(clip_duration))
                pan_x = 18.0 * (t / float(clip_duration))
                pan_y = 10.0 * (t / float(clip_duration))
            elif mode == 1:
                zoom = 1.06 - 0.05 * (t / float(clip_duration))
                pan_x = -15.0 * (t / float(clip_duration))
                pan_y = 8.0 * (t / float(clip_duration))
            else:
                zoom = 1.0 + 0.05 * (t / float(clip_duration))
                pan_x = 20.0 * math.sin((t / float(clip_duration)) * math.pi)
                pan_y = -8.0 * (t / float(clip_duration))
                
            cx, cy = 960.0, 540.0
            M = np.array([
                [zoom, 0, (1.0 - zoom) * cx - pan_x],
                [0, zoom, (1.0 - zoom) * cy - pan_y]
            ], dtype=np.float32)
            frame = cv2.warpAffine(src_img, M, (1920, 1080), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            
            if feather_frames:
                for cfg in feather_configs:
                    f_idx = int((t * 30.0 + cfg["offset"]) % len(feather_frames))
                    f_rgba = feather_frames[f_idx]
                    if cfg["type"] == "breeze":
                        fx = cfg["base_x"] + cfg["amp_x"] * math.sin(t * cfg["freq_x"])
                        fy = cfg["base_y"] + cfg["amp_y"] * math.sin(t * cfg["freq_y"])
                        frot = cfg["base_rot"] + cfg["amp_rot"] * math.sin(t * cfg["freq_x"] * 1.1)
                    else:
                        cycle = (t + cfg["drift_phase"]) % cfg["drift_cycle"]
                        fy = -100 + cycle * (1280.0 / cfg["drift_cycle"])
                        fx = cfg["base_x"] + cfg["amp_x"] * math.sin(cycle * cfg["freq_x"])
                        frot = cfg["amp_rot"] * math.cos(cycle * cfg["freq_x"] * 1.15)
                    overlay_rgba(frame, f_rgba, fx, fy, scale=cfg["scale"], angle_deg=frot)
                    
            for sx, sy, rad, phase, speed, star in sparkles:
                cur_y = (sy - (t * 22.0 * speed)) % 1080
                cur_x = sx + 15.0 * math.sin(t * 1.2 + phase)
                brightness = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * speed * 2.0 + phase))
                fast_draw_sparkle(frame, cur_x, cur_y, rad, star, brightness, sprites)
                
            if logo_badge is not None:
                overlay_rgba(frame, logo_badge, center_x=95, center_y=95, scale=1.0, angle_deg=0)
                
            if i < fade_frames:
                alpha = float(i) / float(fade_frames)
                frame = (frame.astype(np.float32) * alpha).astype(np.uint8)
            elif i > total_frames - fade_frames:
                alpha = float(total_frames - i) / float(fade_frames)
                frame = (frame.astype(np.float32) * alpha).astype(np.uint8)
                
            proc.stdin.write(frame.tobytes())
            
        proc.stdin.close()
        proc.wait()
        
    concat_txt = os.path.join(CLIPS_DIR, "clips_concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for cp in clip_paths:
            f.write(f"file '{cp}'\n")
            
    concat_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-c:v", "copy",
        OUTPUT_BASE_VIDEO
    ]
    subprocess.run(concat_cmd, check=True)
    print(f"\n🎉 SUCCESS: Base video loop generated at {OUTPUT_BASE_VIDEO} ({os.path.getsize(OUTPUT_BASE_VIDEO)//1024//1024} MB)!")

if __name__ == "__main__":
    render_all()
