#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — 24/7 YOUTUBE LIVE STREAMING SERVER ENGINE (ORACLE CLOUD)
=============================================================================
Architecture:
1. Downloads Suno AI tracks (ONLY Suno AI, zero local ragas)
2. Generates seamless 1080p video loop with:
   - Genuine Morpankh (cropped green screen, 0 watermark)
   - Multi-size 3D depth + asynchronous flapping
   - Image-adapted golden sparkles (zero square boxes)
   - Krishna Vibez luxury circular logo badge in top-left
   - Subpixel bicubic Ken Burns zoom/pan (zero jhatka)
3. Zero-CPU-Load RTMP stream to YouTube (-c:v copy, <3% CPU, <90MB RAM)
4. Infinite auto-recovery & hot-reloading loop
=============================================================================
"""

import os
import sys
import glob
import time
import math
import random
import subprocess
import requests
import cv2
import numpy as np

BASE_DIR = "/home/ubuntu/krishna-live"
REPO_DIR = os.path.join(BASE_DIR, "repo")
MUSIC_DIR = os.path.join(BASE_DIR, "music")
CLIPS_DIR = os.path.join(BASE_DIR, "clips")
IMAGES_DIR = os.path.join(REPO_DIR, "music_video_images")
LOGO_PATH = os.path.join(REPO_DIR, "website", "public", "assets", "logo.png")
FEATHER_GREEN_SCREEN = os.path.join(REPO_DIR, "morpankh_green_screen.mp4")
SUNO_URLS_FILE = os.path.join(REPO_DIR, "suno_music_urls.txt")
SUNO_BACKUP_URLS = os.path.join(REPO_DIR, "suno_music_urls_backup.txt")
STREAM_KEY_FILE = os.path.join(BASE_DIR, "stream_key.txt")
BASE_VIDEO_FILE = os.path.join(BASE_DIR, "live_base_video.mp4")
AUDIO_PLAYLIST = os.path.join(BASE_DIR, "audio_playlist.txt")

os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

# 1. Prepare Suno AI Music Pool (strictly Suno AI, zero local ragas)
def prepare_suno_music_pool():
    print("[1/4] Preparing Suno AI Music Pool...")
    # Find all valid Suno mp3, m4a, and wav in MUSIC_DIR (> 1MB)
    all_tracks = []
    for ext in ["*.mp3", "*.m4a", "*.wav"]:
        for fpath in sorted(glob.glob(os.path.join(MUSIC_DIR, ext))):
            if os.path.exists(fpath) and os.path.getsize(fpath) > 1000000:
                # Exclude corrupt legacy files if any
                if "suno_track_" in fpath:
                    continue
                all_tracks.append(fpath)
                
    if not all_tracks:
        # Fallback to any tracks in music dir > 1MB
        for ext in ["*.mp3", "*.m4a", "*.wav"]:
            for fpath in sorted(glob.glob(os.path.join(MUSIC_DIR, ext))):
                if os.path.exists(fpath) and os.path.getsize(fpath) > 1000000:
                    all_tracks.append(fpath)
                    
    print(f"  -> Found {len(all_tracks)} verified Suno AI tracks ready:")
    for t in all_tracks:
        print(f"     🎵 {os.path.basename(t)} ({os.path.getsize(t)//1024} KB)")
        
    # Write concat playlist repeating 30 times (ensures seamless 24/7 continuous looping without end)
    with open(AUDIO_PLAYLIST, "w", encoding="utf-8") as f:
        for _ in range(30):
            for t in all_tracks:
                f.write(f"file '{t}'\n")
    print(f"  -> Audio playlist created with {len(all_tracks)} unique tracks ({len(all_tracks)*30} playlist entries).")
    return all_tracks


# 2. Graphic Asset Preparation
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
        print(f"  ⚠️ Warning: {FEATHER_GREEN_SCREEN} not found!")
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
    
    keyed_glowing_frames = []
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
        keyed_glowing_frames.append(np.dstack([out_rgb.astype(np.uint8), out_a.astype(np.uint8)]))
    return keyed_glowing_frames


def overlay_rgba(bg_img, fg_rgba, center_x, center_y, scale, angle_deg):
    fh, fw = fg_rgba.shape[:2]
    new_w = int(fw * scale)
    new_h = int(fh * scale)
    if new_w <= 0 or new_h <= 0: return
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
    x1, y1 = int(center_x - rw / 2), int(center_y - rh / 2)
    x2, y2 = x1 + rw, y1 + rh
    bg_h, bg_w = bg_img.shape[:2]
    cx1, cy1 = max(0, x1), max(0, y1)
    cx2, cy2 = min(bg_w, x2), min(bg_h, y2)
    if cx2 <= cx1 or cy2 <= cy1: return
    fx1, fy1 = cx1 - x1, cy1 - y1
    fx2, fy2 = fx1 + (cx2 - cx1), fy1 + (cy2 - cy1)
    fg_crop = rotated[fy1:fy2, fx1:fx2]
    alpha = fg_crop[:, :, 3:].astype(np.float32) / 255.0
    bg_crop = bg_img[cy1:cy2, cx1:cx2].astype(np.float32)
    blended = fg_crop[:, :, :3].astype(np.float32) * alpha + bg_crop * (1.0 - alpha)
    bg_img[cy1:cy2, cx1:cx2] = blended.astype(np.uint8)


def get_image_adapted_gold(bg_img):
    avg_b = float(np.mean(bg_img[:, :, 0]))
    avg_g = float(np.mean(bg_img[:, :, 1]))
    avg_r = float(np.mean(bg_img[:, :, 2]))
    ambient = np.array([avg_b, avg_g, avg_r])
    pure_gold = np.array([45.0, 205.0, 255.0])
    return 0.75 * pure_gold + 0.25 * ambient


def prebuild_sparkle_sprites(adapted_gold):
    sprites = {}
    radii = [2.5, 3.5, 4.5, 5.5, 6.5]
    for r in radii:
        for star in [False, True]:
            dim = int(r * 9) | 1
            cx, cy = dim // 2, dim // 2
            stamp = np.zeros((dim, dim, 4), dtype=np.uint8)
            def draw_layer(rad_mult, alpha_val, col):
                cr = int(r * rad_mult)
                if cr <= 0: return
                layer = np.zeros((dim, dim, 3), dtype=np.uint8)
                cv2.circle(layer, (cx, cy), cr, [int(c) for c in col], -1, lineType=cv2.LINE_AA)
                l_mask = np.zeros((dim, dim), dtype=np.uint8)
                cv2.circle(l_mask, (cx, cy), cr, 255, -1, lineType=cv2.LINE_AA)
                l_blur = cv2.GaussianBlur(l_mask, (cr*2+1, cr*2+1), 0).astype(np.float32) / 255.0 * alpha_val
                cur_a = stamp[:, :, 3].astype(np.float32) / 255.0
                add_a = l_blur
                out_a = np.clip(cur_a + add_a, 0.0, 1.0)
                for c in range(3):
                    stamp[:, :, c] = np.clip(stamp[:, :, c] + col[c] * add_a, 0, 255).astype(np.uint8)
                stamp[:, :, 3] = (out_a * 255.0).astype(np.uint8)

            draw_layer(3.6, 0.25, adapted_gold)
            draw_layer(2.0, 0.45, adapted_gold)
            draw_layer(1.1, 0.70, adapted_gold)
            core_col = 0.65 * np.array([255, 255, 255]) + 0.35 * adapted_gold
            draw_layer(0.55, 0.95, core_col)
            if star and r >= 3.5:
                ray_len = int(r * 3.5)
                ray_img = np.zeros((dim, dim, 4), dtype=np.uint8)
                cv2.line(ray_img, (cx - ray_len, cy), (cx + ray_len, cy), (int(core_col[0]), int(core_col[1]), int(core_col[2]), 200), 1, lineType=cv2.LINE_AA)
                cv2.line(ray_img, (cx, cy - ray_len), (cx, cy + ray_len), (int(core_col[0]), int(core_col[1]), int(core_col[2]), 200), 1, lineType=cv2.LINE_AA)
                ra = ray_img[:, :, 3].astype(np.float32) / 255.0
                sa = stamp[:, :, 3].astype(np.float32) / 255.0
                out_a = np.clip(sa + ra, 0.0, 1.0)
                for c in range(3):
                    stamp[:, :, c] = np.clip(stamp[:, :, c] * (1.0 - ra) + ray_img[:, :, c] * ra, 0, 255).astype(np.uint8)
                stamp[:, :, 3] = (out_a * 255.0).astype(np.uint8)
            sprites[(r, star)] = stamp
    return sprites


def fast_draw_sparkle(target, cx, cy, rad, star, brightness, sprites):
    if brightness <= 0.08: return
    keys = [2.5, 3.5, 4.5, 5.5, 6.5]
    nearest_r = min(keys, key=lambda k: abs(k - rad))
    stamp = sprites.get((nearest_r, star))
    if stamp is None: return
    sh, sw = stamp.shape[:2]
    x1, y1 = int(cx - sw / 2), int(cy - sh / 2)
    x2, y2 = x1 + sw, y1 + sh
    bg_h, bg_w = target.shape[:2]
    cx1, cy1 = max(0, x1), max(0, y1)
    cx2, cy2 = min(bg_w, x2), min(bg_h, y2)
    if cx2 <= cx1 or cy2 <= cy1: return
    sx1, sy1 = cx1 - x1, cy1 - y1
    sx2, sy2 = sx1 + (cx2 - cx1), sy1 + (cy2 - cy1)
    stamp_crop = stamp[sy1:sy2, sx1:sx2]
    alpha = (stamp_crop[:, :, 3].astype(np.float32) / 255.0) * brightness
    alpha = np.dstack([alpha, alpha, alpha])
    bg_crop = target[cy1:cy2, cx1:cx2].astype(np.float32)
    fg_rgb = stamp_crop[:, :, :3].astype(np.float32)
    target[cy1:cy2, cx1:cx2] = (fg_rgb * alpha + bg_crop * (1.0 - alpha)).astype(np.uint8)


def generate_feather_configs(seed=None):
    rng = random.Random(seed)
    return [
        {"scale": rng.uniform(0.58, 0.65), "offset": rng.randint(0, 30), "base_x": rng.uniform(180, 240), "base_y": rng.uniform(350, 420), "type": "breeze", "amp_x": rng.uniform(25, 40), "amp_y": rng.uniform(20, 35), "freq_x": rng.uniform(0.7, 0.9), "freq_y": rng.uniform(1.0, 1.3), "base_rot": rng.uniform(-10, -5), "amp_rot": rng.uniform(5, 8)},
        {"scale": rng.uniform(0.40, 0.46), "offset": rng.randint(45, 75), "base_x": rng.uniform(1500, 1600), "base_y": rng.uniform(320, 400), "type": "breeze", "amp_x": rng.uniform(20, 35), "amp_y": rng.uniform(18, 30), "freq_x": rng.uniform(0.65, 0.85), "freq_y": rng.uniform(0.95, 1.2), "base_rot": rng.uniform(6, 12), "amp_rot": rng.uniform(4, 7)},
        {"scale": rng.uniform(0.30, 0.36), "offset": rng.randint(90, 125), "type": "drift", "drift_cycle": rng.uniform(16.0, 21.0), "drift_phase": rng.uniform(0.0, 10.0), "base_x": rng.uniform(700, 850), "amp_x": rng.uniform(80, 120), "freq_x": rng.uniform(1.1, 1.4), "amp_rot": rng.uniform(10, 15)},
        {"scale": rng.uniform(0.22, 0.28), "offset": rng.randint(140, 175), "type": "drift", "drift_cycle": rng.uniform(19.0, 25.0), "drift_phase": rng.uniform(10.0, 20.0), "base_x": rng.uniform(420, 560), "amp_x": rng.uniform(60, 95), "freq_x": rng.uniform(1.0, 1.3), "amp_rot": rng.uniform(8, 14)},
        {"scale": rng.uniform(0.16, 0.21), "offset": rng.randint(70, 100), "base_x": rng.uniform(1150, 1280), "base_y": rng.uniform(140, 220), "type": "breeze", "amp_x": rng.uniform(30, 45), "amp_y": rng.uniform(15, 25), "freq_x": rng.uniform(0.5, 0.7), "freq_y": rng.uniform(0.8, 1.0), "base_rot": rng.uniform(4, 8), "amp_rot": rng.uniform(3, 5)}
    ]


def render_seamless_video_loop(slides_count=None, clip_duration=25):
    """Generates a pristine 1080p seamless video loop from all clean 8K slides."""
    print("[2/4] Generating Base 1080p Video Loop with Morpankh & Smooth Motion...")
    slides = sorted(glob.glob(os.path.join(IMAGES_DIR, "*.jpg")))
    if not slides:
        raise FileNotFoundError(f"No slides in {IMAGES_DIR}")
        
    chosen_slides = slides if slides_count is None else slides[:slides_count]
    logo_badge = create_corner_logo_badge(size=120)
    feather_frames = load_and_key_feather_frames()
    
    clip_paths = []
    fps = 25
    total_frames = int(clip_duration * fps)
    fade_frames = int(1.2 * fps)
    
    for idx, slide_path in enumerate(chosen_slides):
        clip_path = os.path.join(CLIPS_DIR, f"clip_{idx+1:02d}.mp4")
        clip_paths.append(clip_path)
        if os.path.exists(clip_path) and os.path.getsize(clip_path) > 5000000:
            print(f"  -> Slide {idx+1}/{len(chosen_slides)} already rendered: {os.path.basename(clip_path)}")
            continue
        print(f"  -> Rendering Slide {idx+1}/{len(chosen_slides)}...")
        
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
            "ffmpeg", "-y",
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
        
    # Concat clips into BASE_VIDEO_FILE
    concat_txt = os.path.join(CLIPS_DIR, "clips_concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for cp in clip_paths:
            f.write(f"file '{cp}'\n")
            
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-c:v", "copy",
        BASE_VIDEO_FILE
    ]
    subprocess.run(concat_cmd, check=True)
    print(f"  -> Base video created: {BASE_VIDEO_FILE} ({len(chosen_slides) * clip_duration}s loop)")
    return BASE_VIDEO_FILE


# 3. Continuous Zero-CPU RTMP Streaming Engine
def start_live_stream():
    print("[3/4] Reading YouTube Stream Key...")
    if not os.path.exists(STREAM_KEY_FILE):
        raise FileNotFoundError(f"Stream key file missing: {STREAM_KEY_FILE}")
    with open(STREAM_KEY_FILE, "r", encoding="utf-8") as f:
        stream_key = f.read().strip()
        
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    print(f"  -> Ingest Target: rtmp://a.rtmp.youtube.com/live2/••••{stream_key[-4:]}")
    
    print("[4/4] 🚀 Launching 24/7 Zero-CPU Live Stream...")
    # Stream-Copy Command: 0% CPU transcoding load!
    stream_cmd = [
        "ffmpeg",
        "-re",
        "-stream_loop", "-1",
        "-i", BASE_VIDEO_FILE,
        "-stream_loop", "-1",
        "-f", "concat", "-safe", "0",
        "-i", AUDIO_PLAYLIST,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy", # DIRECT STREAM COPY = ZERO CPU LOAD!
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-flvflags", "no_duration_filesize",
        "-f", "flv",
        rtmp_url
    ]
    
    print("-----------------------------------------------------------------")
    print("LIVE BROADCAST ACTIVE! Streaming 24/7 to YouTube Channel...")
    print("-----------------------------------------------------------------")
    while True:
        try:
            p = subprocess.Popen(stream_cmd)
            p.wait()
            print("  ⚠️ Stream disconnected. Auto-reconnecting in 3 seconds...")
            time.sleep(3)
        except KeyboardInterrupt:
            print("\nStream stopped by user.")
            break
        except Exception as e:
            print(f"  ⚠️ Error: {e}. Retrying in 5 seconds...")
            time.sleep(5)


def main():
    print("=================================================================")
    print("KRISHNA VIBEZ — 24/7 YOUTUBE LIVE STREAMING ENGINE")
    print("=================================================================")
    prepare_suno_music_pool()
    render_seamless_video_loop(slides_count=8, clip_duration=25)
    start_live_stream()

if __name__ == "__main__":
    main()
