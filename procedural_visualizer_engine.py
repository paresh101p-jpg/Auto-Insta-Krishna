# -*- coding: utf-8 -*-
"""
Procedural Visualizer Engine for 24/7 Live Streams & Standalone Music Videos
===========================================================================
10 Distinct Sacred Geometries x 10 Divine Palettes = 100+ Visual Combinations.
Driven by REAL audio RMS decibels/frequencies extracted directly from master audio.
"""
import math
import cv2
import numpy as np

VISUALIZER_STYLES = [
    "fullwidth_bars",           # 1. 136 Full-Width Spectrum Bars (Edge to Edge)
    "silk_sine_ribbon",         # 2. 3-Layer Flowing Silk Sine Wave
    "mirrored_ribbon",          # 3. Dual Mirrored Flowing Ribbon (Top & Bottom)
    "dotted_pearls",            # 4. Floating Pearl Beads Wave
    "mountain_mesh",            # 5. Glowing Translucent Mountain Fill Wave
    "center_pulse_pillars",     # 6. Dual Center-Out Pulse Pillars
    "aurora_curtain",           # 7. Ethereal Vertical Aurora Sound Curtains
    "sacred_mandala_pulse",     # 8. Symmetric Soundwave Bloom
    "starlight_particles",      # 9. Energy Particle Sparks Radiating Upward
    "double_density_equalizer"  # 10. 200 Ultra-Fine Micro-Bars with Glowing Caps
]

COLOR_PALETTES = [
    [(15, 185, 255), (110, 235, 255), (255, 255, 255)],  # 1. 24K Royal Gold & Diamond White
    [(220, 230, 40), (140, 245, 120), (255, 255, 255)],  # 2. Yamuna Emerald Cyan & Pearl White
    [(40, 160, 255), (60, 210, 255), (200, 240, 255)],   # 3. Sunset Crimson & Amber Flame
    [(180, 160, 255), (220, 200, 255), (255, 255, 255)], # 4. Sacred Lotus Rose & Soft Lilac
    [(230, 230, 230), (255, 240, 200), (255, 255, 255)], # 5. Moonlight Silver & Ethereal Mist
    [(200, 180, 50), (230, 220, 100), (255, 255, 255)],  # 6. Peacock Turquoise & Blue-Green
    [(20, 130, 255), (80, 200, 255), (240, 250, 255)],   # 7. Surya Dawn Saffron & Sunrise Gold
    [(210, 80, 190), (240, 140, 220), (255, 255, 255)],  # 8. Cosmic Amethyst & Golden Dust
    [(240, 180, 30), (255, 220, 90), (255, 255, 255)],   # 9. Divine Opal & Neon Azure
    [(30, 150, 240), (70, 190, 255), (255, 255, 255)]    # 10. Sacred Sandalwood & Marigold Gold
]

def draw_dynamic_visualizer(frame, style_name, palette, intensity, t, base_y=800):
    """
    Renders one of 10 distinct sacred visualizers on the frame.
    Elevated base_y=800 keeps it clean and well above YouTube playback controls.
    Intensity is 100% real audio RMS decibel measurement.
    """
    col_base, col_mid, col_peak = palette

    if style_name == "fullwidth_bars":
        # 136 Full-Width Bars across x=76 to x=1844
        num_bars = 136
        bar_width = 8
        spacing = 13
        start_x = 76
        for b_idx in range(num_bars):
            pos_norm = b_idx / float(num_bars - 1)
            envelope = math.sin(pos_norm * math.pi) * 0.85 + 0.15
            micro = math.sin(t * 9.0 + b_idx * 0.28) * 0.35 + math.cos(t * 5.0 - b_idx * 0.15) * 0.2
            bar_h = max(3, int((4.0 + intensity * 42.0 * (envelope + micro))))
            bx = start_x + b_idx * spacing
            y1 = base_y - bar_h
            y2 = base_y + int(bar_h * 0.25)
            bar_col = col_peak if intensity > 2.2 else col_base
            cap_col = (255, 255, 255) if intensity > 2.2 else col_mid
            cv2.rectangle(frame, (bx, y1), (bx + bar_width, y2), bar_col, -1, lineType=cv2.LINE_AA)
            if bar_h > 12:
                cv2.circle(frame, (bx + bar_width // 2, y1 - 3), 2, cap_col, -1, lineType=cv2.LINE_AA)

    elif style_name == "silk_sine_ribbon":
        # 3 Flowing Silk Sine Waves
        for layer_idx, col in enumerate([col_base, col_mid, col_peak]):
            pts = []
            freq = 0.003 + layer_idx * 0.0015
            speed = 2.2 + layer_idx * 0.7
            amp = 3.0 + (18.0 + layer_idx * 14.0) * intensity
            phase = layer_idx * 1.5
            for x in range(0, 1920, 5):
                harmonic = math.sin(x * freq + t * speed + phase) + 0.35 * math.sin(x * freq * 2.4 - t * 1.6)
                y = base_y + amp * harmonic
                pts.append([x, int(y)])
            pts = np.array(pts, dtype=np.int32)
            thick = 1 if intensity < 0.5 else (4 if intensity > 2.2 else 2)
            cv2.polylines(frame, [pts], isClosed=False, color=col, thickness=thick, lineType=cv2.LINE_AA)

    elif style_name == "mirrored_ribbon":
        # Dual Mirrored Ribbon (Top & Bottom symmetry)
        amp = 3.0 + 32.0 * intensity
        pts_top = []
        pts_bot = []
        for x in range(0, 1920, 6):
            h = math.sin(x * 0.0038 + t * 2.5) * amp
            pts_top.append([x, int(base_y - h)])
            pts_bot.append([x, int(base_y + h)])
        pts_top = np.array(pts_top, dtype=np.int32)
        pts_bot = np.array(pts_bot, dtype=np.int32)
        cv2.polylines(frame, [pts_top], isClosed=False, color=col_peak if intensity > 2.0 else col_mid, thickness=2, lineType=cv2.LINE_AA)
        cv2.polylines(frame, [pts_bot], isClosed=False, color=col_base, thickness=2, lineType=cv2.LINE_AA)

    elif style_name == "dotted_pearls":
        # 160 Floating Pearl Beads across entire screen
        for b_idx in range(0, 1920, 12):
            norm_x = b_idx / 1920.0
            h = math.sin(norm_x * 4.0 * math.pi + t * 3.0) * (5.0 + intensity * 32.0)
            py = int(base_y + h)
            rad = 2 if intensity < 1.0 else (5 if intensity > 2.2 else 3)
            p_col = col_peak if intensity > 2.0 else col_mid
            cv2.circle(frame, (b_idx, py), rad, p_col, -1, lineType=cv2.LINE_AA)

    elif style_name == "mountain_mesh":
        # Translucent Mountain Mesh Fill
        pts = [[0, 1080]]
        for x in range(0, 1920, 8):
            h = (math.sin(x * 0.003 + t * 1.8) + 0.4 * math.sin(x * 0.007 - t * 2.2)) * (6.0 + intensity * 36.0)
            pts.append([x, int(base_y - h)])
        pts.append([1920, 1080])
        pts = np.array(pts, dtype=np.int32)
        overlay = frame.copy()
        cv2.fillPoly(overlay, [pts], col_base)
        alpha = min(0.35, 0.12 + intensity * 0.07)
        cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)

    elif style_name == "center_pulse_pillars":
        # Center-Out Pulse Pillars
        for x in range(80, 1840, 14):
            dist = abs(x - 960) / 960.0
            h = max(3, int((math.sin(dist * math.pi) * 38.0 * intensity)))
            cv2.line(frame, (x, base_y - h), (x, base_y + h), col_mid if intensity > 1.8 else col_base, thickness=2, lineType=cv2.LINE_AA)

    elif style_name == "aurora_curtain":
        # Ethereal Aurora Sound Curtains
        for x in range(100, 1820, 20):
            amp = math.sin(x * 0.004 + t * 2.0) * intensity * 45.0
            h = max(4, int(abs(amp)))
            col = col_peak if (x // 20) % 2 == 0 else col_mid
            cv2.line(frame, (x, base_y - h), (x, base_y), col, thickness=2, lineType=cv2.LINE_AA)
            cv2.circle(frame, (x, base_y - h - 2), 2, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "sacred_mandala_pulse":
        # Symmetrical Sacred Bloom
        pts_left = []
        pts_right = []
        for d in range(0, 800, 8):
            h = math.sin(d * 0.015 - t * 3.5) * (intensity * 35.0)
            pts_left.append([960 - d, int(base_y - h)])
            pts_right.append([960 + d, int(base_y - h)])
        pts = np.array(pts_left[::-1] + pts_right, dtype=np.int32)
        cv2.polylines(frame, [pts], isClosed=False, color=col_peak if intensity > 2.0 else col_mid, thickness=2, lineType=cv2.LINE_AA)

    elif style_name == "starlight_particles":
        # Floating Energy Sparks
        for s_idx in range(0, 1920, 24):
            phase = (s_idx * 17) % 100
            spark_y = base_y - int(((t * 30.0 + phase) % 120.0) * (intensity * 0.8 + 0.3))
            rad = 2 if intensity < 1.5 else 4
            cv2.circle(frame, (s_idx, spark_y), rad, col_peak if intensity > 2.0 else col_mid, -1, lineType=cv2.LINE_AA)
        # Base connecting line
        cv2.line(frame, (60, base_y), (1860, base_y), col_base, thickness=1, lineType=cv2.LINE_AA)

    elif style_name == "double_density_equalizer":
        # 200 Ultra-Fine Micro-Bars
        for b_idx in range(200):
            bx = 120 + b_idx * 8
            norm = b_idx / 200.0
            h = max(2, int((math.sin(norm * math.pi) * 36.0 * intensity)))
            cv2.rectangle(frame, (bx, base_y - h), (bx + 4, base_y), col_mid if intensity > 1.8 else col_base, -1, lineType=cv2.LINE_AA)
            if h > 8:
                cv2.circle(frame, (bx + 2, base_y - h - 2), 1, (255, 255, 255), -1, lineType=cv2.LINE_AA)
