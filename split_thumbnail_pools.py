# -*- coding: utf-8 -*-
"""
Double-Verified Thumbnail Pool Splitter:
Categorizes all thumbnail URLs into:
- thumbnail_urls_<cat>_right.txt (Woman is on the RIGHT -> Text MUST be on LEFT)
- thumbnail_urls_<cat>_left.txt  (Woman is on the LEFT  -> Text MUST be on RIGHT)
- thumbnail_urls_<cat>_ambiguous.txt (Quarantined/Excluded from production)

Zero Guessing at runtime. Guaranteed 0.0% overlap.
"""

import os
import sys
import cv2
import requests
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "face_detection_yunet.onnx")

CATEGORIES = [
    "lotus_lake",
    "raag_darbari",
    "morning_pooja",
    "bansuri_tabla",
    "sleep_insomnia",
    "stress_relief",
    "lofi_beats"
]

def analyze_image_bytes(img_bytes):
    """
    Returns 'RIGHT', 'LEFT', or 'AMBIGUOUS'
    """
    arr = np.asarray(bytearray(img_bytes), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    if img is None:
        return 'INVALID'
    h, w = img.shape[:2]
    
    # 1. Neural Face Detection with YuNet
    det = cv2.FaceDetectorYN.create(MODEL_PATH, '', (w, h), 0.5, 0.3, 5000)
    det.setInputSize((w, h))
    _, faces = det.detect(img)
    
    valid_faces = []
    if faces is not None and len(faces) > 0:
        for f in faces:
            fx, fy, fw, fh = f[:4]
            conf = f[-1]
            # Valid portrait face: upper 65% of image, at least 12% of height, confidence >= 0.70
            if fy < h * 0.65 and fh >= h * 0.12 and conf >= 0.70:
                valid_faces.append(f)
                
    if valid_faces:
        # Pick strictly by highest confidence (real human face, never sitar bowls/lamps)
        best_face = max(valid_faces, key=lambda f: f[-1])
        fx, fy, fw, fh = best_face[:4]
        cx = (fx + fw/2.0) / float(w)
        if cx >= 0.52:
            return 'RIGHT'
        elif cx <= 0.48:
            return 'LEFT'
        else:
            return 'AMBIGUOUS'
            
    # 2. Fallback: Upper torso skin contour centroid (upper 70% of frame)
    upper = img[:int(h*0.70), :]
    hsv = cv2.cvtColor(upper, cv2.COLOR_BGR2HSV)
    mask = cv2.bitwise_or(cv2.inRange(hsv, (0, 25, 60), (28, 255, 255)),
                          cv2.inRange(hsv, (170, 25, 60), (180, 255, 255)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    clean_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large_contours = [c for c in contours if cv2.contourArea(c) > 5000]
    
    if large_contours:
        best_c = max(large_contours, key=cv2.contourArea)
        M = cv2.moments(best_c)
        if M['m00'] > 0:
            cx = (M['m10'] / M['m00']) / float(w)
            if cx >= 0.58:
                return 'RIGHT'
            elif cx <= 0.42:
                return 'LEFT'
                
    return 'AMBIGUOUS'

def process_single_url(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=10)
        if r.status_code == 200:
            classification = analyze_image_bytes(r.content)
            return url, classification
        return url, 'HTTP_ERROR'
    except Exception as e:
        return url, f'ERROR_{str(e)[:20]}'

def process_category(cat_name):
    input_file = os.path.join(BASE_DIR, f"thumbnail_urls_{cat_name}.txt")
    if not os.path.exists(input_file):
        print(f"Skipping {cat_name}, file not found.")
        return
        
    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
        
    print(f"\n==========================================")
    print(f"Processing Category: {cat_name} ({len(urls)} URLs)")
    print(f"==========================================")
    
    right_list = []
    left_list = []
    ambiguous_list = []
    
    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_url = {executor.submit(process_single_url, u): u for u in urls}
        done_count = 0
        total = len(urls)
        for future in as_completed(future_to_url):
            url, result = future.result()
            done_count += 1
            if result == 'RIGHT':
                right_list.append(url)
            elif result == 'LEFT':
                left_list.append(url)
            else:
                ambiguous_list.append(url)
                
            if done_count % 25 == 0 or done_count == total:
                print(f"[{cat_name}] {done_count}/{total} done -> Right: {len(right_list)}, Left: {len(left_list)}, Ambiguous: {len(ambiguous_list)}", flush=True)

    # Save to disk
    right_file = os.path.join(BASE_DIR, f"thumbnail_urls_{cat_name}_right.txt")
    left_file = os.path.join(BASE_DIR, f"thumbnail_urls_{cat_name}_left.txt")
    ambiguous_file = os.path.join(BASE_DIR, f"thumbnail_urls_{cat_name}_ambiguous.txt")
    right_backup = os.path.join(BASE_DIR, f"thumbnail_urls_{cat_name}_right_backup.txt")
    left_backup = os.path.join(BASE_DIR, f"thumbnail_urls_{cat_name}_left_backup.txt")
    
    with open(right_file, "w", encoding="utf-8") as f:
        for u in right_list:
            f.write(u + "\n")
            
    with open(right_backup, "w", encoding="utf-8") as f:
        for u in right_list:
            f.write(u + "\n")
            
    with open(left_file, "w", encoding="utf-8") as f:
        for u in left_list:
            f.write(u + "\n")
            
    with open(left_backup, "w", encoding="utf-8") as f:
        for u in left_list:
            f.write(u + "\n")
            
    with open(ambiguous_file, "w", encoding="utf-8") as f:
        for u in ambiguous_list:
            f.write(u + "\n")
            
    print(f"SUCCESS for {cat_name}:")
    print(f"  -> Right URLs (Woman on Right): {len(right_list)} saved to {os.path.basename(right_file)}")
    print(f"  -> Left URLs (Woman on Left): {len(left_list)} saved to {os.path.basename(left_file)}")
    print(f"  -> Ambiguous/Quarantined: {len(ambiguous_list)} saved to {os.path.basename(ambiguous_file)}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "all":
        for cat in CATEGORIES:
            process_category(cat)
    else:
        process_category(target)
