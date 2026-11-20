# -*- coding: utf-8 -*-
"""
Master Procedural Visualizer Engine (52 Distinct Soundwave Shapes)
==================================================================
Absolute Lifetime Guarantees:
1. ZERO TOP CLIPPING:
   - No hard clamping (no flat razor-blade cuts).
   - All peaks use smooth, non-linear tanh compression.
   - Max vertical reach is safely bounded at Y >= 885 (195px safe headroom from bottom).
2. ZERO BOTTOM CLIPPING:
   - Flat-bottom styles (Bars, Pillars, Ladders, Cities, Mountains) sit 100% flush at Y=1080 (0px bottom gap).
   - Oscillating & floating styles (Ribbons, Sines, Pearls, Arcs, Blooms) float at Y=965-995.
     Their lowest trough NEVER exceeds Y=1040 (guaranteeing at least 40px safe buffer from bottom edge).
3. EDGE-TO-EDGE FULL WIDTH: X=0 to X=1920 (0px side margin).
4. MULTI-COLOR DYNAMIC VERTICAL GRADIENT:
   - Low/Base = Deep tone
   - Mid = Vibrant 24K Gold / Cyan / Emerald / Amethyst
   - High/Peak = Diamond White Glow
5. 100% REAL AUDIO REACTIVE: Driven by PCM Float RMS Decibels.
"""

import math
import cv2
import numpy as np

COLOR_PALETTES = [
    [(20, 100, 240), (30, 210, 255), (255, 255, 255)],   # 1. Sunset Amber ➡️ 24K Gold ➡️ Diamond White
    [(40, 170, 30), (140, 245, 120), (255, 255, 255)],   # 2. Deep Emerald ➡️ Yamuna Cyan ➡️ Pearl White
    [(160, 40, 60), (255, 190, 40), (255, 255, 255)],    # 3. Cosmic Indigo ➡️ Sacred Ice Blue ➡️ Crystal White
    [(30, 80, 210), (80, 170, 255), (240, 250, 255)],    # 4. Sacred Saffron Flame ➡️ Sunrise Amber ➡️ Golden Glow
    [(160, 100, 210), (220, 160, 255), (255, 255, 255)], # 5. Royal Amethyst ➡️ Lotus Lilac ➡️ Star Dust
    [(180, 140, 30), (230, 210, 80), (255, 255, 255)],   # 6. Peacock Deep Teal ➡️ Radiant Turquoise ➡️ White
    [(40, 120, 220), (60, 200, 255), (255, 255, 255)],   # 7. Surya Dawn Gold ➡️ Marigold Yellow ➡️ White
    [(120, 50, 150), (200, 110, 240), (255, 255, 255)],  # 8. Divine Orchid ➡️ Electric Magenta ➡️ Diamond
    [(180, 160, 40), (240, 220, 100), (255, 255, 255)],  # 9. Moonlight Silver ➡️ Opal Cyan ➡️ Pure White
    [(20, 130, 230), (70, 200, 255), (255, 255, 255)]    # 10. Sacred Sandalwood ➡️ Temple Gold ➡️ Diamond Glow
]

VISUALIZER_STYLES = [
    # Group 1: Equalizer Bars & Pillars (01 - 10)
    "spectrum_bars",              # 01. 160 Full-width gradient bars (flush at bottom)
    "ultra_dense_micro_bars",     # 02. 240 Micro-bars with glowing diamond caps
    "segmented_block_bars",       # 03. 80 Segmented chunky LED ladder blocks
    "center_dome_bars",           # 04. Parabolic center dome equalizer
    "twin_peak_pillars",          # 05. Dual stereo bass pillars (left & right)
    "octave_harmonic_bars",       # 06. 120 Octave harmonic bars with white top edge cap
    "matrix_ladder_steps",        # 07. 96 Multi-color stepped LED ladder bars
    "capsule_pillars",            # 08. 110 Soft rounded pill-shaped bars
    "dual_depth_bars",            # 09. 2-Layer 3D depth bars (foreground + ghost shadow)
    "floating_cap_equalizer",     # 10. Bars with detached floating white needle indicators

    # Group 2: Silk Sine & Flowing Ribbons (11 - 20)
    "classic_sine_wave",          # 11. Single pure silk ribbon floating at Y=985 (60px bottom margin)
    "triple_harmonic_silk",       # 12. 3 Undulating silk ribbons (47px bottom margin)
    "dna_helix_ribbon",           # 13. Dual intersecting ribbons with ladder rungs (40px margin)
    "braided_river_wave",         # 14. 4 Entangled flowing braided threads (68px margin)
    "high_frequency_flutter",     # 15. Fast fluttering acoustic tremble wave
    "acoustic_horizon_swell",     # 16. Wide rolling ocean swell line (55px margin)
    "neon_luminous_ribbon",       # 17. Intense 3-pass glowing neon aura beam
    "dual_echo_wave",             # 18. Primary bright wave + trailing ghost echo wave
    "sawtooth_triangle_wave",     # 19. Crisp geometric angular sound zigzag
    "tapered_silk_swirl",         # 20. Calligraphic brushstroke line with razor tips

    # Group 3: Beads, Pearls & Particles (21 - 30)
    "pearl_necklace",             # 21. Floating glowing pearl beads (59px bottom margin)
    "multi_size_pearls",          # 22. Dynamic sizing: large bass pearls, tiny treble pearls
    "bouncing_marbles",           # 23. Dual-track oscillating beads in counter-rhythm
    "vertical_dotted_stems",      # 24. Vertical thin needles topped with glowing beads
    "starlight_constellation",    # 25. Golden energy spark field reacting to beats
    "quantum_trailing_dots",      # 26. Floating dots with downward light comet tails
    "floating_bubble_cluster",    # 27. Soft translucent sound bubbles rising upward
    "lotus_seed_pulse",           # 28. Floral 3-dot clusters arranged like sacred seeds
    "sound_spark_rain",           # 29. Downward musical golden rainfall
    "matrix_grid_dots",           # 30. 3-Row floating 3D dot terrain grid in perspective

    # Group 4: Filled Silhouettes, Mountains & Meshes (31 - 40)
    "translucent_mountain",       # 31. Soft gradient glowing mountain ridge (flush at bottom)
    "shadow_mountains",           # 32. 2-Layer mountain depth with overlapping peaks
    "poly_mesh_ridge",            # 33. Low-poly triangulated wireframe crystalline ridge
    "under_glow_horizon",         # 34. High-contrast crest line with ambient down-glow
    "aurora_curtain",             # 35. Ethereal vertical northern light sound curtains
    "architectural_skyline",      # 36. Blocky stylized geometric audio city skyline
    "cave_spire_wave",            # 37. Glowing stalagmites pulsing with bass notes
    "liquid_mercury_wave",        # 38. High-reflection molten liquid chrome wave
    "ocean_breaker_wave",         # 39. Rolling ocean tidal wave with foam dots
    "desert_sand_dunes",          # 40. Triple-layer warm glowing sand dune contours

    # Group 5: Sacred Geometric & Symmetric Motifs (41 - 52)
    "radiant_audio_bloom",        # 41. 36 Radial sunburst rays from bottom center
    "mandala_half_wheel",         # 42. Concentric sacred Vedic mandala arcs & spokes
    "trishul_spire_wave",         # 43. Shiva Trishul three-pronged central spire with ripples
    "flute_melodic_crests",       # 44. Gentle undulating bansuri notes with golden accents
    "cosmic_om_arcs",             # 45. Concentric acoustic sound ripple rings from center
    "lotus_bloom_petals",         # 46. 12 Sacred lotus petals blooming outward with bass
    "butterfly_wings_wave",       # 47. Symmetrical wings mirroring outwards from center
    "seven_chakra_nodes",         # 48. Waveform anchored by 7 glowing sacred energy chakras
    "temple_gopuram_arch",        # 49. Traditional Indian temple entrance dome arch
    "triple_horizon_arcs",        # 50. Three parallel floating rainbow bridges
    "laser_audio_grid",           # 51. Precision audio beam with vertical laser drop lines
    "spiritual_ecg_pulse"         # 52. Spiritual life-force heartbeat pulse traveling across
]


def draw_dynamic_visualizer(frame, style_name, palette, intensity, t, base_y=1080):
    """
    Renders any of the 52 distinct wave shapes.
    guaranteed ZERO top clipping and ZERO bottom clipping.
    """
    col_base, col_mid, col_peak = palette
    c_low = np.array(col_base, dtype=np.float32)
    c_mid = np.array(col_mid, dtype=np.float32)
    c_peak = np.array(col_peak, dtype=np.float32)
    y_off = base_y - 1080

    # -------------------------------------------------------------
    # GROUP 1: EQUALIZER BARS & PILLARS (01 - 10) [FLUSH AT Y=1080]
    # -------------------------------------------------------------

    if style_name in ("spectrum_bars", "fullwidth_bars"):
        num_bars = 160
        bar_w = 8
        spacing = 12
        for i in range(num_bars):
            env = math.sin((i / 159.0) * math.pi) * 0.55 + 0.45
            mic = math.sin(t * 8.0 + i * 0.28) * 0.35 + math.cos(t * 4.5 - i * 0.15) * 0.2
            raw = max(0.0, (env + mic) * (0.3 + intensity * 0.75))
            bh = int(18.0 + 160.0 * math.tanh(raw * 0.85))
            bx = i * spacing
            num_s = max(2, bh)
            fr = np.linspace(0.0, 1.0, num_s)[:, None]
            c_up = (1.0 - fr * 2.0).clip(0.0, 1.0) * c_peak + (fr * 2.0).clip(0.0, 1.0) * c_mid
            c_dn = (2.0 - fr * 2.0).clip(0.0, 1.0) * c_mid + (fr * 2.0 - 1.0).clip(0.0, 1.0) * c_low
            col = np.where(fr < 0.5, c_up, c_dn).astype(np.uint8)
            frame[1080 - bh:1080, bx:bx + bar_w] = np.repeat(col[:, None, :], bar_w, axis=1)
            if bh > 25:
                cv2.circle(frame, (bx + bar_w // 2, 1080 - bh - 3), 3, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name in ("ultra_dense_micro_bars", "double_density_equalizer"):
        num_bars = 240
        bar_w = 5
        spacing = 8
        for i in range(num_bars):
            env = math.sin((i / 239.0) * math.pi) * 0.6 + 0.4
            octv = math.sin(i * 0.2 + t * 6.0) * 0.35 + math.cos(i * 0.08 - t * 4.0) * 0.25
            raw = max(0.0, (env * 0.85 + octv * 0.4) * (0.3 + intensity * 0.75))
            bh = int(14.0 + 150.0 * math.tanh(raw * 0.85))
            bx = i * spacing
            num_s = max(2, bh)
            fr = np.linspace(0.0, 1.0, num_s)[:, None]
            c_up = (1.0 - fr * 2.0).clip(0.0, 1.0) * c_peak + (fr * 2.0).clip(0.0, 1.0) * c_mid
            c_dn = (2.0 - fr * 2.0).clip(0.0, 1.0) * c_mid + (fr * 2.0 - 1.0).clip(0.0, 1.0) * c_low
            col = np.where(fr < 0.5, c_up, c_dn).astype(np.uint8)
            frame[1080 - bh:1080, bx:bx + bar_w] = np.repeat(col[:, None, :], bar_w, axis=1)
            if bh > 20:
                cv2.circle(frame, (bx + bar_w // 2, 1080 - bh - 2), 2, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "segmented_block_bars":
        num_bars = 80
        for i in range(num_bars):
            env = math.sin((i / 79.0) * math.pi) * 0.6 + 0.4
            mic = math.sin(t * 5.0 + i * 0.3) * 0.3
            bh = int(20 + 145 * math.tanh(max(0.0, (env + mic) * (0.3 + intensity * 0.75))))
            bx = i * 24 + 4
            curr_y = 1080
            while curr_y > 1080 - bh:
                blk_top = max(1080 - bh, curr_y - 8)
                frac = (1080 - curr_y) / 160.0
                col = tuple(map(int, (1.0 - frac) * c_mid + frac * c_peak))
                cv2.rectangle(frame, (bx, blk_top), (bx + 16, curr_y), col, -1)
                curr_y -= 11

    elif style_name == "center_dome_bars":
        for i in range(160):
            norm = i / 159.0
            dome = (math.sin(norm * math.pi) ** 2.2) * 1.2
            mic = math.sin(t * 6.0 + i * 0.25) * 0.25
            bh = int(14 + 160 * math.tanh(max(0.0, (dome + mic) * (0.3 + intensity * 0.75))))
            bx = i * 12
            cv2.rectangle(frame, (bx, 1080 - bh), (bx + 8, 1080), col_mid if bh < 85 else col_peak, -1)
            cv2.circle(frame, (bx + 4, 1080 - bh - 3), 3, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "twin_peak_pillars":
        for i in range(160):
            norm = i / 159.0
            p1 = math.exp(-((norm - 0.3) ** 2) / 0.03)
            p2 = math.exp(-((norm - 0.7) ** 2) / 0.03)
            mic = math.sin(t * 7.0 + i * 0.3) * 0.2
            bh = int(15 + 155 * math.tanh(max(0.0, (p1 + p2 + mic) * (0.3 + intensity * 0.75))))
            bx = i * 12
            cv2.rectangle(frame, (bx, 1080 - bh), (bx + 7, 1080), col_base if bh < 70 else col_mid, -1)
            cv2.circle(frame, (bx + 3, 1080 - bh - 2), 2, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "octave_harmonic_bars":
        for i in range(120):
            norm = i / 119.0
            octave = math.sin(norm * 6.0 * math.pi + t * 4.0) * 0.4 + (1.0 - norm) * 0.6
            bh = int(15 + 145 * math.tanh(max(0.0, octave * (0.3 + intensity * 0.8))))
            bx = i * 16 + 2
            cv2.rectangle(frame, (bx, 1080 - bh), (bx + 11, 1080), col_mid, -1)
            cv2.line(frame, (bx, 1080 - bh), (bx + 11, 1080 - bh), (255, 255, 255), 2)

    elif style_name == "matrix_ladder_steps":
        for i in range(96):
            norm = i / 95.0
            mic = math.sin(i * 0.35 + t * 5.0) * 0.4 + math.sin(norm * math.pi) * 0.6
            steps = int(2 + 13 * math.tanh(max(0.0, mic * (0.3 + intensity * 0.75))))
            bx = i * 20 + 2
            for s in range(steps):
                sy = 1080 - s * 10 - 8
                scol = col_base if s < 5 else (col_mid if s < 10 else (255, 255, 255))
                cv2.rectangle(frame, (bx, sy), (bx + 14, sy + 7), scol, -1)

    elif style_name == "capsule_pillars":
        num_caps = 120
        for i in range(num_caps):
            norm = i / float(num_caps - 1)
            h = int(22 + 140 * math.tanh(max(0.0, (math.sin(norm * math.pi) * 0.7 + math.sin(i * 0.25 + t * 4.0) * 0.3) * (0.3 + intensity * 0.75))))
            bx = int(norm * 1919)
            cv2.line(frame, (bx, base_y), (bx, base_y - h + 6), col_mid, thickness=10, lineType=cv2.LINE_AA)
            cv2.circle(frame, (bx, base_y - h + 6), 5, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "dual_depth_bars":
        num_bars = 160
        bar_w = 8
        for i in range(num_bars):
            norm = i / 159.0
            bh_bg = int(10 + 105 * math.tanh(max(0.0, math.sin(i * 0.2 - t * 3.0) * (0.3 + intensity * 0.65))))
            bx = int(norm * (1920 - bar_w))
            cv2.rectangle(frame, (bx, base_y - bh_bg), (bx + bar_w - 1, base_y), col_base, -1)
        for i in range(num_bars):
            norm = i / 159.0
            bh_fg = int(15 + 155 * math.tanh(max(0.0, math.sin(i * 0.25 + t * 4.5) * (0.3 + intensity * 0.75))))
            bx = int(norm * (1920 - bar_w))
            cv2.rectangle(frame, (bx, base_y - bh_fg), (bx + bar_w, base_y), col_mid, -1)
            cv2.circle(frame, (bx + bar_w // 2, base_y - bh_fg - 3), 3, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "floating_cap_equalizer":
        num_bars = 160
        bar_w = 8
        for i in range(num_bars):
            norm = i / 159.0
            env = math.sin(norm * math.pi) * 0.5 + 0.5
            bh = int(12 + 130 * math.tanh(max(0.0, (env + math.sin(i * 0.3 + t * 6.0) * 0.3) * (0.3 + intensity * 0.75))))
            bx = int(norm * (1920 - bar_w))
            cv2.rectangle(frame, (bx, base_y - bh), (bx + bar_w, base_y), col_base, -1)
            cap_y = base_y - bh - 8
            cv2.rectangle(frame, (bx - 1, cap_y - 3), (bx + bar_w + 1, cap_y), (255, 255, 255), -1)

    # -------------------------------------------------------------
    # GROUP 2: SILK SINE & FLOWING RIBBONS (11 - 20) [FLOATING Y=985]
    # -------------------------------------------------------------

    elif style_name in ("classic_sine_wave", "silk_sine_ribbon"):
        pts = []
        base_y = 985
        amp = min(36.0, 10.0 + 26.0 * math.tanh(intensity * 0.65))
        for x in range(0, 1921, 5):
            y = int(base_y + amp * math.sin(x * 0.0035 + t * 2.5))
            pts.append([x, y])
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, col_mid, 4, lineType=cv2.LINE_AA)

    elif style_name == "triple_harmonic_silk":
        base_y = 985
        for l_idx, c in enumerate([col_base, col_mid, (255, 255, 255)]):
            pts = []
            amp = min(36.0, (10.0 + l_idx * 7.0) + 16.0 * math.tanh(intensity * 0.65))
            for x in range(0, 1921, 5):
                y = int(base_y + amp * (math.sin(x * 0.0032 + t * 2.2 + l_idx * 1.4) + 0.3 * math.sin(x * 0.007 - t * 1.5)))
                pts.append([x, y])
            cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, c, 3 if l_idx < 2 else 4, lineType=cv2.LINE_AA)

    elif style_name in ("dna_helix_ribbon", "mirrored_ribbon"):
        amp = min(28.0, 8.0 + 20.0 * math.tanh(intensity * 0.7))
        p1, p2 = [], []
        top_base = 965
        bot_base = 1010
        for x in range(0, 1921, 6):
            h = math.sin(x * 0.0036 + t * 2.4) * amp
            p1.append([x, int(top_base - h)])
            p2.append([x, int(bot_base + h)])
            if x % 48 == 0:
                cv2.line(frame, (x, int(top_base - h)), (x, int(bot_base + h)), col_base, 1, lineType=cv2.LINE_AA)
        cv2.polylines(frame, [np.array(p1, dtype=np.int32)], False, (255, 255, 255), 3, lineType=cv2.LINE_AA)
        cv2.polylines(frame, [np.array(p2, dtype=np.int32)], False, col_mid, 3, lineType=cv2.LINE_AA)

    elif style_name == "braided_river_wave":
        base_y = 988
        for strand in range(4):
            pts = []
            amp = min(24.0, 8.0 + 16.0 * math.tanh(intensity * 0.7))
            ph = strand * math.pi * 0.5
            for x in range(0, 1921, 6):
                y = int(base_y + amp * math.sin(x * 0.0038 + t * 2.0 + ph))
                pts.append([x, y])
            col = col_peak if strand == 0 else (col_mid if strand % 2 == 1 else col_base)
            cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, col, 2, lineType=cv2.LINE_AA)

    elif style_name == "high_frequency_flutter":
        pts = []
        base_y = 990
        amp = min(28.0, 8.0 + 20.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1921, 4):
            flutter = math.sin(x * 0.015 + t * 6.0) * 0.35 + math.sin(x * 0.003 + t * 2.0)
            y = int(base_y + amp * flutter)
            pts.append([x, y])
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, col_mid, 3, lineType=cv2.LINE_AA)

    elif style_name == "acoustic_horizon_swell":
        pts = []
        base_y = 995
        amp = min(26.0, 6.0 + 20.0 * math.tanh(intensity * 0.65))
        for x in range(0, 1921, 8):
            y = int(base_y + amp * math.sin((x / 1920.0) * math.pi * 2.5 + t * 1.5))
            pts.append([x, y])
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, (255, 255, 255), 4, lineType=cv2.LINE_AA)

    elif style_name == "neon_luminous_ribbon":
        pts = []
        base_y = 985
        amp = min(30.0, 8.0 + 22.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1921, 5):
            y = int(base_y + amp * math.sin(x * 0.0035 + t * 2.4))
            pts.append([x, y])
        p_arr = np.array(pts, dtype=np.int32)
        cv2.polylines(frame, [p_arr], False, col_base, 8, lineType=cv2.LINE_AA)
        cv2.polylines(frame, [p_arr], False, col_mid, 4, lineType=cv2.LINE_AA)
        cv2.polylines(frame, [p_arr], False, (255, 255, 255), 2, lineType=cv2.LINE_AA)

    elif style_name == "dual_echo_wave":
        base_y = 985
        amp = min(30.0, 8.0 + 22.0 * math.tanh(intensity * 0.7))
        p1 = [[x, int(base_y + amp * math.sin(x * 0.0038 + t * 2.2))] for x in range(0, 1921, 6)]
        p2 = [[x, int(base_y + amp * 0.6 * math.sin(x * 0.0038 + t * 2.2 - 0.7))] for x in range(0, 1921, 6)]
        cv2.polylines(frame, [np.array(p2, dtype=np.int32)], False, col_base, 2, lineType=cv2.LINE_AA)
        cv2.polylines(frame, [np.array(p1, dtype=np.int32)], False, (255, 255, 255), 3, lineType=cv2.LINE_AA)

    elif style_name == "sawtooth_triangle_wave":
        pts = []
        base_y = 985
        amp = min(28.0, 8.0 + 20.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1921, 24):
            pts.append([x, int(base_y - amp * ((x // 24) % 2 * 2 - 1))])
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, col_mid, 3, lineType=cv2.LINE_AA)

    elif style_name == "tapered_silk_swirl":
        base_y = 985
        amp = min(32.0, 8.0 + 24.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1915, 6):
            norm = x / 1920.0
            taper = math.sin(norm * math.pi)
            y1 = int(base_y + amp * taper * math.sin(x * 0.004 + t * 2.5))
            y2 = int(base_y + amp * taper * math.sin((x+6) * 0.004 + t * 2.5))
            th = max(1, int(6 * taper))
            cv2.line(frame, (x, y1), (x+6, y2), col_peak if taper > 0.6 else col_mid, th, lineType=cv2.LINE_AA)

    # -------------------------------------------------------------
    # GROUP 3: BEADS, PEARLS & PARTICLES (21 - 30) [FLOATING Y=990]
    # -------------------------------------------------------------

    elif style_name in ("pearl_necklace", "dotted_pearls"):
        base_y = 995
        amp = min(26.0, 6.0 + 20.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1921, 14):
            py = int(base_y + amp * math.sin((x / 1920.0) * 4.0 * math.pi + t * 2.8))
            cv2.circle(frame, (x, py), 4, (255, 255, 255), -1, lineType=cv2.LINE_AA)
            cv2.circle(frame, (x, py), 2, col_mid, -1, lineType=cv2.LINE_AA)

    elif style_name == "multi_size_pearls":
        base_y = 995
        amp = min(26.0, 6.0 + 20.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1921, 12):
            norm = x / 1920.0
            py = int(base_y + amp * math.sin(norm * 5.0 * math.pi + t * 3.0))
            rad = max(2, int(6 * math.sin(norm * math.pi)))
            cv2.circle(frame, (x, py), rad, col_peak if rad > 4 else col_mid, -1, lineType=cv2.LINE_AA)

    elif style_name == "bouncing_marbles":
        amp = min(22.0, 6.0 + 16.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1921, 16):
            h = math.sin(x * 0.005 + t * 3.0) * amp
            cv2.circle(frame, (x, int(975 - h)), 4, (255, 255, 255), -1, lineType=cv2.LINE_AA)
            cv2.circle(frame, (x, int(1015 + h)), 4, col_mid, -1, lineType=cv2.LINE_AA)

    elif style_name == "vertical_dotted_stems":
        for x in range(0, 1921, 20):
            h = int(15 + 125 * math.tanh(max(0.0, math.sin(x * 0.006 + t * 4.0) * (0.3 + intensity * 0.75))))
            cv2.line(frame, (x, 1080), (x, 1080 - h), col_base, 1, lineType=cv2.LINE_AA)
            cv2.circle(frame, (x, 1080 - h), 4, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name in ("starlight_constellation", "starlight_particles"):
        np.random.seed(42)
        base_s = 990 + y_off
        for i in range(120):
            sx = int((i / 119.0) * 1919)
            sy = int(base_s + math.sin(sx * 0.004 + t * 2.0) * 24 + np.random.uniform(-10, 10))
            rad = int(np.random.uniform(2, 5))
            cv2.circle(frame, (sx, sy), rad, (255, 255, 255) if rad > 3 else col_mid, -1, lineType=cv2.LINE_AA)

    elif style_name == "quantum_trailing_dots":
        base_y = 990
        amp = min(24.0, 6.0 + 18.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1921, 15):
            y = int(base_y + amp * math.sin(x * 0.004 + t * 3.5))
            for tail in range(4):
                ty = y + tail * 6
                al = int(255 * (1.0 - tail / 4.0))
                cv2.circle(frame, (x, ty), max(1, 4 - tail), (al, al, al), -1, lineType=cv2.LINE_AA)

    elif style_name == "floating_bubble_cluster":
        np.random.seed(99)
        base_b = 1005 + y_off
        for b in range(60):
            bx = int((b / 59.0) * 1919)
            by = int(base_b - ((t * 30 + b * 15) % 75) * math.tanh(intensity * 0.8))
            rad = int(np.random.uniform(3, 7))
            cv2.circle(frame, (bx, by), rad, col_mid, 1, lineType=cv2.LINE_AA)
            cv2.circle(frame, (bx - 1, by - 1), 1, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "lotus_seed_pulse":
        base_y = 995
        amp = min(24.0, 6.0 + 18.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1921, 16):
            y = int(base_y + amp * math.sin(x * 0.005 + t * 2.5))
            cv2.circle(frame, (x, y), 3, (255, 255, 255), -1, lineType=cv2.LINE_AA)
            cv2.circle(frame, (x - 4, y + 3), 2, col_mid, -1, lineType=cv2.LINE_AA)
            cv2.circle(frame, (x + 4, y + 3), 2, col_mid, -1, lineType=cv2.LINE_AA)

    elif style_name == "sound_spark_rain":
        base_r = 980 + y_off
        for x in range(0, 1920, 15):
            y = int(base_r + math.sin(x * 0.004 + t * 2.5) * 22)
            rain_len = int(8 + 22 * math.tanh(intensity * 0.8))
            cv2.line(frame, (x, y), (x, y + rain_len), col_mid, 2, lineType=cv2.LINE_AA)
            cv2.circle(frame, (x, y), 3, (255, 255, 255), -1, lineType=cv2.LINE_AA)
        cv2.line(frame, (1919, int(base_r)), (1919, int(base_r + 15)), col_mid, 2, lineType=cv2.LINE_AA)

    elif style_name == "matrix_grid_dots":
        for row in range(3):
            ry = 975 + row * 20
            for col in range(0, 1921, 20):
                h = math.sin(col * 0.005 + row * 0.6 + t * 3.0) * 10 * math.tanh(intensity * 0.8)
                cv2.circle(frame, (col, int(ry + h)), 3, (255, 255, 255) if row == 0 else col_mid, -1, lineType=cv2.LINE_AA)

    # -------------------------------------------------------------
    # GROUP 4: FILLED SILHOUETTES & MOUNTAINS (31 - 40)
    # -------------------------------------------------------------

    elif style_name in ("translucent_mountain", "mountain_mesh"):
        pts = [[0, 1080]]
        for x in range(0, 1921, 8):
            h = (math.sin(x * 0.003 + t * 1.5) + 0.3 * math.sin(x * 0.007 - t * 2.0)) * (15 + 120 * math.tanh(intensity * 0.8))
            pts.append([x, int(1080 - max(10, h))])
        pts.append([1920, 1080])
        pts_arr = np.array(pts, dtype=np.int32)
        overlay = frame.copy()
        cv2.fillPoly(overlay, [pts_arr], col_base)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        cv2.polylines(frame, [pts_arr[1:-1]], False, (255, 255, 255), 3, lineType=cv2.LINE_AA)

    elif style_name == "shadow_mountains":
        for layer, c, alp in [(1, col_base, 0.35), (2, col_mid, 0.5)]:
            pts = [[0, 1080]]
            amp_scale = 95 if layer == 1 else 135
            for x in range(0, 1921, 10):
                h = math.sin(x * (0.0025 * layer) + t * (1.2 * layer)) * (10 + amp_scale * math.tanh(intensity * 0.8))
                pts.append([x, int(1080 - max(8, h))])
            pts.append([1920, 1080])
            pts_arr = np.array(pts, dtype=np.int32)
            ov = frame.copy()
            cv2.fillPoly(ov, [pts_arr], c)
            cv2.addWeighted(ov, alp, frame, 1.0 - alp, 0, frame)
            cv2.polylines(frame, [pts_arr[1:-1]], False, (255, 255, 255) if layer == 2 else col_mid, 2, lineType=cv2.LINE_AA)

    elif style_name == "poly_mesh_ridge":
        pts = []
        for x in range(0, 1921, 24):
            h = int(15 + 115 * math.tanh(max(0.0, math.sin(x * 0.004 + t * 2.0) * (0.3 + intensity * 0.75))))
            pts.append((x, 1080 - h))
        for i in range(len(pts) - 1):
            tri = np.array([[pts[i][0], 1080], pts[i], pts[i+1]], dtype=np.int32)
            cv2.fillPoly(frame, [tri], col_base if i % 2 == 0 else col_mid)
            cv2.polylines(frame, [tri], True, (255, 255, 255), 1, lineType=cv2.LINE_AA)

    elif style_name == "under_glow_horizon":
        pts = [[0, 1080]]
        for x in range(0, 1921, 8):
            h = int(12 + 105 * math.tanh(max(0.0, math.sin(x * 0.0035 + t * 2.0) * (0.3 + intensity * 0.75))))
            pts.append([x, 1080 - h])
        pts.append([1920, 1080])
        p_arr = np.array(pts, dtype=np.int32)
        overlay = frame.copy()
        cv2.fillPoly(overlay, [p_arr], col_mid)
        cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)
        cv2.polylines(frame, [p_arr[1:-1]], False, (255, 255, 255), 3, lineType=cv2.LINE_AA)

    elif style_name == "aurora_curtain":
        for x in range(0, 1921, 16):
            h = int(15 + 125 * math.tanh(max(0.0, math.sin(x * 0.004 + t * 2.0) * (0.3 + intensity * 0.75))))
            cv2.line(frame, (x, 1080), (x, 1080 - h), col_mid if (x // 16) % 2 == 0 else col_base, 6, lineType=cv2.LINE_AA)
            cv2.circle(frame, (x, 1080 - h - 2), 3, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "architectural_skyline":
        for i in range(48):
            bx = i * 40
            h = int(20 + 135 * math.tanh(max(0.0, math.sin(i * 0.3 + t * 3.0) * (0.3 + intensity * 0.75))))
            cv2.rectangle(frame, (bx, 1080 - h), (bx + 36, 1080), col_base, -1)
            cv2.rectangle(frame, (bx, 1080 - h), (bx + 36, 1080), (255, 255, 255), 2)

    elif style_name == "cave_spire_wave":
        for x in range(0, 1921, 14):
            h = int(12 + 120 * math.tanh(max(0.0, (math.sin(x * 0.004 + t * 2.5) ** 3) * (0.3 + intensity * 0.8))))
            tri = np.array([[x - 6, 1080], [x, 1080 - h], [x + 6, 1080]], dtype=np.int32)
            cv2.fillPoly(frame, [tri], col_mid)
            cv2.circle(frame, (x, 1080 - h), 2, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "liquid_mercury_wave":
        pts = []
        base_y = 990
        amp = min(28.0, 8.0 + 20.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1921, 5):
            y = int(base_y + amp * (math.sin(x * 0.003 + t * 2.0) + 0.4 * math.cos(x * 0.006 - t * 3.0)))
            pts.append([x, y])
        p_arr = np.array(pts, dtype=np.int32)
        cv2.polylines(frame, [p_arr], False, (180, 200, 220), 8, lineType=cv2.LINE_AA)
        cv2.polylines(frame, [p_arr], False, (255, 255, 255), 3, lineType=cv2.LINE_AA)

    elif style_name == "ocean_breaker_wave":
        pts = []
        base_y = 990
        amp = min(30.0, 8.0 + 22.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1921, 6):
            roll = (math.sin(x * 0.004 + t * 2.2) ** 2) * math.sin(x * 0.002 + t * 1.0)
            y = int(base_y + amp * roll)
            pts.append([x, y])
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, col_mid, 4, lineType=cv2.LINE_AA)
        for x in range(0, 1921, 24):
            fy = int(base_y + amp * ((math.sin(x * 0.004 + t * 2.2) ** 2) * math.sin(x * 0.002 + t * 1.0)) - 5)
            cv2.circle(frame, (x, fy), 2, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "desert_sand_dunes":
        for d, c, spd in [(1, col_base, 1.0), (2, col_mid, 1.8), (3, (255, 255, 255), 2.5)]:
            pts = []
            base_y = 965 + d * 16
            amp = min(15.0, 4.0 + 11.0 * math.tanh(intensity * 0.7))
            for x in range(0, 1921, 8):
                y = int(base_y + amp * math.sin(x * (0.002 * d) + t * spd))
                pts.append([x, y])
            cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, c, 3, lineType=cv2.LINE_AA)

    # -------------------------------------------------------------
    # GROUP 5: SACRED GEOMETRIC & SYMMETRIC MOTIFS (41 - 52)
    # -------------------------------------------------------------

    elif style_name == "radiant_audio_bloom":
        cy = base_y
        amp = min(22.0, 6.0 + 16.0 * math.tanh(intensity * 0.7))
        pts = [[x, int(base_y - 20 + amp * math.sin(x * 0.004 + t * 2.5))] for x in range(0, 1921, 6)]
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, col_base, 2, lineType=cv2.LINE_AA)
        for cx in [320, 960, 1600]:
            for ray in range(24):
                ang = (ray / 23.0) * math.pi
                r = int(45 + 95 * math.tanh(max(0.0, math.sin(ray * 0.3 + t * 4.0) * (0.3 + intensity * 0.75))))
                x2 = int(cx + r * math.cos(ang))
                y2 = int(cy - r * math.sin(ang))
                cv2.line(frame, (cx, cy), (x2, y2), col_mid if ray % 2 == 0 else col_base, 2, lineType=cv2.LINE_AA)
                cv2.circle(frame, (x2, y2), 2, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name in ("mandala_half_wheel", "sacred_mandala_pulse"):
        cy = base_y
        amp = min(22.0, 6.0 + 16.0 * math.tanh(intensity * 0.7))
        pts = [[x, int(base_y - 18 + amp * math.sin(x * 0.004 + t * 2.2))] for x in range(0, 1921, 6)]
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, col_base, 2, lineType=cv2.LINE_AA)
        for cx in [320, 960, 1600]:
            for arc_r in [40, 70, 105]:
                r = int(arc_r * (0.8 + 0.3 * math.tanh(intensity * 0.7)))
                cv2.ellipse(frame, (cx, cy), (r, r), 0, 180, 360, col_mid, 2, lineType=cv2.LINE_AA)
            for sp in range(16):
                ang = (sp / 15.0) * math.pi
                r = int(115 * (0.8 + 0.3 * math.tanh(intensity * 0.7)))
                cv2.line(frame, (cx, cy), (int(cx + r * math.cos(ang)), int(cy - r * math.sin(ang))), (255, 255, 255), 1, lineType=cv2.LINE_AA)

    elif style_name == "trishul_spire_wave":
        for x in range(0, 1921, 12):
            dist = abs(x - 960)
            if dist < 40:
                h = int(45 + 140 * math.tanh(intensity * 0.85))
                c = (255, 255, 255)
            elif 60 < dist < 120:
                h = int(30 + 100 * math.tanh(intensity * 0.8))
                c = col_mid
            else:
                h = int(12 + 55 * math.tanh(max(0.0, math.sin(x * 0.01 + t * 3.0) * (0.3 + intensity * 0.65))))
                c = col_base
            cv2.line(frame, (x, 1080), (x, 1080 - h), c, 4, lineType=cv2.LINE_AA)

    elif style_name == "flute_melodic_crests":
        pts = []
        base_y = 985
        amp = min(28.0, 8.0 + 20.0 * math.tanh(intensity * 0.7))
        for x in range(0, 1921, 6):
            crest = math.sin(x * 0.003 + t * 2.0) + 0.25 * math.sin(x * 0.009 + t * 3.5)
            y = int(base_y + amp * crest)
            pts.append([x, y])
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, (255, 255, 255), 4, lineType=cv2.LINE_AA)
        for x in range(100, 1821, 200):
            y = int(base_y + amp * (math.sin(x * 0.003 + t * 2.0) + 0.25 * math.sin(x * 0.009 + t * 3.5)) - 10)
            cv2.circle(frame, (x, y), 4, col_mid, -1, lineType=cv2.LINE_AA)

    elif style_name == "cosmic_om_arcs":
        cy = base_y
        amp = min(22.0, 6.0 + 16.0 * math.tanh(intensity * 0.7))
        pts = [[x, int(base_y - 20 + amp * math.sin(x * 0.004 + t * 2.8))] for x in range(0, 1921, 6)]
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, col_mid, 2, lineType=cv2.LINE_AA)
        for cx in [320, 960, 1600]:
            for r_idx in range(4):
                pulse = (t * 40 + r_idx * 30) % 120
                r = int(25 + pulse * math.tanh(intensity * 0.8))
                alp = max(0, 255 - int(pulse * 1.8))
                c = (alp, int(alp * 0.8), int(alp * 0.4))
                cv2.ellipse(frame, (cx, cy), (r, r), 0, 180, 360, c, 2, lineType=cv2.LINE_AA)

    elif style_name == "lotus_bloom_petals":
        cy = base_y
        amp = min(22.0, 6.0 + 16.0 * math.tanh(intensity * 0.7))
        pts = [[x, int(base_y - 18 + amp * math.sin(x * 0.004 + t * 2.0))] for x in range(0, 1921, 6)]
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, col_base, 2, lineType=cv2.LINE_AA)
        petals = 8
        for cx in [240, 720, 1200, 1680]:
            for p in range(petals):
                ang = (p / float(petals - 1)) * math.pi
                r = int(55 + 65 * math.tanh(intensity * 0.8))
                px = int(cx + r * math.cos(ang))
                py = int(cy - r * math.sin(ang))
                cv2.ellipse(frame, (px, py), (10, 20), int(math.degrees(ang)), 0, 360, col_mid, 2, lineType=cv2.LINE_AA)
                cv2.circle(frame, (px, py), 2, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "butterfly_wings_wave":
        p_left, p_right = [], []
        amp = min(30.0, 8.0 + 22.0 * math.tanh(intensity * 0.7))
        for d in range(0, 961, 8):
            h = math.sin(d * 0.006 + t * 3.0) * amp
            p_left.append([960 - d, int(985 - h)])
            p_right.append([960 + d, int(985 - h)])
        cv2.polylines(frame, [np.array(p_left, dtype=np.int32)], False, col_mid, 3, lineType=cv2.LINE_AA)
        cv2.polylines(frame, [np.array(p_right, dtype=np.int32)], False, (255, 255, 255), 3, lineType=cv2.LINE_AA)

    elif style_name == "seven_chakra_nodes":
        base_y = 988
        amp = min(26.0, 6.0 + 20.0 * math.tanh(intensity * 0.7))
        pts = []
        for x in range(0, 1921, 6):
            pts.append([x, int(base_y + amp * math.sin(x * 0.004 + t * 2.2))])
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, col_mid, 3, lineType=cv2.LINE_AA)
        for i in range(1, 8):
            nx = int((i / 8.0) * 1920)
            ny = int(base_y + amp * math.sin(nx * 0.004 + t * 2.2))
            cv2.circle(frame, (nx, ny), 8, col_base, -1, lineType=cv2.LINE_AA)
            cv2.circle(frame, (nx, ny), 5, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "temple_gopuram_arch":
        for x in range(0, 1921, 16):
            dist = abs(x - 960) / 960.0
            arch = (1.0 - dist ** 1.8) * 135 * math.tanh(intensity * 0.8)
            h = max(10, int(arch + math.sin(x * 0.05 + t * 4.0) * 8))
            cv2.line(frame, (x, 1080), (x, 1080 - h), col_mid if dist < 0.4 else col_base, 5, lineType=cv2.LINE_AA)
            cv2.circle(frame, (x, 1080 - h - 2), 3, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    elif style_name == "triple_horizon_arcs":
        for a, c, y_off in [(1, col_base, 0), (2, col_mid, 20), (3, (255, 255, 255), 40)]:
            pts = []
            base_y = 968 + y_off
            amp = min(18.0, 4.0 + 14.0 * math.tanh(intensity * 0.7))
            for x in range(0, 1921, 6):
                pts.append([x, int(base_y + amp * math.sin(x * 0.0035 + t * 2.0))])
            cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, c, 3, lineType=cv2.LINE_AA)

    elif style_name == "laser_audio_grid":
        base_y = 990
        amp = min(28.0, 8.0 + 20.0 * math.tanh(intensity * 0.7))
        pts = []
        for x in range(0, 1921, 6):
            pts.append([x, int(base_y + amp * math.sin(x * 0.004 + t * 2.5))])
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, (255, 255, 255), 2, lineType=cv2.LINE_AA)
        for x in range(0, 1921, 60):
            y = int(base_y + amp * math.sin(x * 0.004 + t * 2.5))
            cv2.line(frame, (x, y), (x, 1080), col_mid, 1, lineType=cv2.LINE_AA)

    elif style_name == "spiritual_ecg_pulse":
        pts = []
        base_y = 990
        for x in range(0, 1921, 5):
            cyc = (x - int(t * 120)) % 400
            if 180 <= cyc <= 220:
                ecg = math.sin((cyc - 180) / 40.0 * math.pi * 2) * 45 * math.tanh(intensity * 0.85)
            else:
                ecg = math.sin(x * 0.005) * 5
            pts.append([x, int(base_y - ecg)])
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, (255, 255, 255), 3, lineType=cv2.LINE_AA)

    # Fallback to standard spectrum bars if unknown name
    else:
        draw_dynamic_visualizer(frame, "spectrum_bars", palette, intensity, t, base_y=base_y)
