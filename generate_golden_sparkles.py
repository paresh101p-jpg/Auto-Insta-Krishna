#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates a seamless 10-second 1080p golden sparkles particle video loop.
Floating glowing golden orbs and twinkling stars over black background (for screen blending).
"""

import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_SPARKLES_VIDEO = os.path.join(BASE_DIR, "golden_sparkles_loop.mp4")
FFMPEG_EXE = "ffmpeg"
local_ffmpeg = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if os.path.exists(local_ffmpeg):
    FFMPEG_EXE = local_ffmpeg

WIDTH, HEIGHT = 1920, 1080
FPS = 25
DURATION = 10
TOTAL_FRAMES = FPS * DURATION
NUM_PARTICLES = 75

# Reproducible divine seed
random.seed(432)

class Particle:
    def __init__(self):
        self.x0 = random.uniform(50, WIDTH - 50)
        self.y0 = random.uniform(0, HEIGHT)
        self.speed_y = random.uniform(25, 60) # upward pixels per second
        self.amp_x = random.uniform(15, 40)   # gentle drift amplitude
        self.freq_x = random.uniform(0.5, 1.5) # drift frequency
        self.phase_x = random.uniform(0, 2 * math.pi)
        self.radius = random.uniform(2.5, 6.0)
        self.twinkle_speed = random.uniform(1.0, 3.0)
        self.twinkle_phase = random.uniform(0, 2 * math.pi)
        # Gold colors: warm amber to radiant gold
        self.gold_r = 255
        self.gold_g = random.randint(200, 235)
        self.gold_b = random.randint(70, 130)

    def get_pos_and_alpha(self, t):
        # Seamless looping in Y
        total_drift = self.speed_y * t
        y = (self.y0 - total_drift) % (HEIGHT + 60) - 30
        x = self.x0 + self.amp_x * math.sin(self.freq_x * t * (2 * math.pi / DURATION) + self.phase_x)
        
        # Seamless twinkle
        twinkle = 0.4 + 0.6 * math.sin(self.twinkle_speed * t * (2 * math.pi / DURATION) + self.twinkle_phase)
        alpha = max(0.0, min(1.0, twinkle))
        return x, y, alpha

def generate_frames():
    import subprocess
    print(f"Generating {TOTAL_FRAMES} frames of seamless golden sparkles ({WIDTH}x{HEIGHT} @ {FPS}fps)...")
    particles = [Particle() for _ in range(NUM_PARTICLES)]

    # Start ffmpeg process to pipe raw frames
    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        OUTPUT_SPARKLES_VIDEO
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for f_idx in range(TOTAL_FRAMES):
        t = f_idx / FPS
        # Create black frame
        frame = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(frame)

        for p in particles:
            x, y, alpha = p.get_pos_and_alpha(t)
            if -30 <= y <= HEIGHT + 30 and -30 <= x <= WIDTH + 30:
                r = p.radius
                int_alpha = int(alpha * 255)
                color = (int(p.gold_r * alpha), int(p.gold_g * alpha), int(p.gold_b * alpha))
                # Soft glow (outer circle)
                glow_r = r * 2.2
                glow_color = (int(p.gold_r * alpha * 0.35), int(p.gold_g * alpha * 0.35), int(p.gold_b * alpha * 0.2))
                draw.ellipse([x - glow_r, y - glow_r, x + glow_r, y + glow_r], fill=glow_color)
                # Core star
                draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
                # Bright white center sparkle
                if alpha > 0.6:
                    center_r = max(1.0, r * 0.4)
                    draw.ellipse([x - center_r, y - center_r, x + center_r, y + center_r], fill=(int(255 * alpha), int(255 * alpha), int(220 * alpha)))

        # Slight blur to make particles glow naturally
        frame = frame.filter(ImageFilter.GaussianBlur(radius=0.7))
        proc.stdin.write(frame.tobytes())

        if (f_idx + 1) % 50 == 0:
            print(f"  -> Rendered frame {f_idx + 1}/{TOTAL_FRAMES}...")

    proc.stdin.close()
    proc.wait()
    print(f"[SUCCESS] Golden Sparkles Loop created: {OUTPUT_SPARKLES_VIDEO} ({os.path.getsize(OUTPUT_SPARKLES_VIDEO) / 1024:.1f} KB)")
    return OUTPUT_SPARKLES_VIDEO

if __name__ == "__main__":
    generate_frames()
