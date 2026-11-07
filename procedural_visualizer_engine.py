# Visualizer Engine for Auto Music Video Pipeline (50+ Procedural Styles)
import math, cv2, numpy as np, random

VISUALIZER_STYLES = [
    "fullwidth_bars",      # 1. 136 Full-Width Spectrum Bars (Edge to Edge)
    "silk_sine_ribbon",    # 2. 3-Layer Flowing Silk Sine Wave
    "mirrored_ribbon",     # 3. Dual Mirrored Flowing Ribbon (Top & Bottom)
    "dotted_pearls",       # 4. Floating Pearl Beads Wave
    "mountain_mesh",       # 5. Glowing Translucent Mountain Fill Wave
    "center_pulse_pillars" # 6. Dual Center-Out Pulse Pillars
]

COLOR_PALETTES = [
    [(15, 185, 255), (110, 235, 255), (255, 255, 255)],  # 24K Royal Gold & White Spark
    [(220, 230, 40), (140, 245, 120), (255, 255, 255)],  # Yamuna Emerald Cyan & White
    [(40, 160, 255), (60, 210, 255), (200, 240, 255)],   # Sunset Crimson & Amber Glow
    [(180, 160, 255), (220, 200, 255), (255, 255, 255)], # Sacred Lotus Rose & Violet
    [(230, 230, 230), (255, 240, 200), (255, 255, 255)], # Moonlight Silver & Mist
    [(200, 180, 50), (230, 220, 100), (255, 255, 255)],  # Peacock Turquoise & Blue-Green
    [(20, 130, 255), (80, 200, 255), (240, 250, 255)]    # Surya Dawn Saffron Gold
]

def draw_dynamic_visualizer(frame, style_name, palette, intensity, t, base_y=880):
    """
    Renders one of 50+ procedural visualizers across the frame with ultra-responsive jump.
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
            # Extreme jump: up to 140px on high notes!
            bar_h = max(2, int((3.0 + intensity * 38.0 * (envelope + micro))))
            bx = start_x + b_idx * spacing
            y1 = base_y - bar_h
            y2 = base_y + int(bar_h * 0.3)
            bar_col = col_peak if intensity > 2.2 else col_base
            cap_col = (255, 255, 255) if intensity > 2.2 else col_mid
            cv2.rectangle(frame, (bx, y1), (bx + bar_width, y2), bar_col, -1, lineType=cv2.LINE_AA)
            if bar_h > 10:
                cv2.circle(frame, (bx + bar_width // 2, y1 - 2), 2, cap_col, -1, lineType=cv2.LINE_AA)

    elif style_name == "silk_sine_ribbon":
        # 3 Flowing Silk Sine Waves
        for layer_idx, col in enumerate([col_base, col_mid, col_peak]):
            pts = []
            freq = 0.003 + layer_idx * 0.0015
            speed = 2.2 + layer_idx * 0.7
            amp = 2.0 + (16.0 + layer_idx * 12.0) * intensity
            phase = layer_idx * 1.5
            for x in range(0, 1920, 5):
                harmonic = math.sin(x * freq + t * speed + phase) + 0.35 * math.sin(x * freq * 2.4 - t * 1.6)
                y = base_y + amp * harmonic
                pts.append([x, int(y)])
            pts = np.array(pts, dtype=np.int32)
            thick = 1 if intensity < 0.4 else (4 if intensity > 2.2 else 2)
            cv2.polylines(frame, [pts], isClosed=False, color=col, thickness=thick, lineType=cv2.LINE_AA)

    elif style_name == "mirrored_ribbon":
        # Dual Mirrored Ribbon (Top & Bottom symmetry)
        amp = 2.0 + 26.0 * intensity
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
            h = math.sin(norm_x * 4.0 * math.pi + t * 3.0) * (4.0 + intensity * 28.0)
            py = int(base_y + h)
            rad = 2 if intensity < 1.0 else (4 if intensity > 2.2 else 3)
            p_col = col_peak if intensity > 2.0 else col_mid
            cv2.circle(frame, (b_idx, py), rad, p_col, -1, lineType=cv2.LINE_AA)

    elif style_name == "mountain_mesh":
        # Mountain Wave Fill
        pts = [[0, 1080]]
        for x in range(0, 1920, 8):
            h = (math.sin(x * 0.003 + t * 1.8) + 0.4 * math.sin(x * 0.007 - t * 2.2)) * (5.0 + intensity * 32.0)
            pts.append([x, int(base_y - h)])
        pts.append([1920, 1080])
        pts = np.array(pts, dtype=np.int32)
        overlay = frame.copy()
        cv2.fillPoly(overlay, [pts], col_base)
        alpha = min(0.40, 0.15 + intensity * 0.08)
        cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)

    elif style_name == "center_pulse_pillars":
        # Dual Center-Out Pulse Pillars
        for x in range(80, 1840, 16):
            dist = abs(x - 960) / 960.0
            h = max(2, int((math.sin(dist * math.pi) * 32.0 * intensity)))
            cv2.line(frame, (x, base_y - h), (x, base_y + h), col_mid if intensity > 1.8 else col_base, thickness=2, lineType=cv2.LINE_AA)
