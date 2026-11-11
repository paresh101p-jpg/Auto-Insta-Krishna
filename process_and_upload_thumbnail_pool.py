import os
import sys
import glob
import time
import subprocess
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"E:\Paresh\Auto Post\Auto-Insta-Krishna"
RAW_DIR = os.path.join(BASE_DIR, "music_video_thumbnails") if os.path.exists(os.path.join(BASE_DIR, "music_video_thumbnails")) else os.path.join(BASE_DIR, "thumbnail_pool_raw")
CLEAN_DIR = os.path.join(BASE_DIR, "thumbnail_pool_clean")
TRACKER_FILE = os.path.join(BASE_DIR, "uploaded_thumbnail_images_tracker.txt")

os.makedirs(CLEAN_DIR, exist_ok=True)

CATEGORIES = ["morning_pooja", "bansuri_tabla", "raag_darbari", "lotus_lake", "sleep_insomnia", "stress_relief", "lofi_beats"]

def classify_image_with_ai_vision(image_path):
    """
    AI Vision Classifier: Uses Gemini 3.8 Flash Vision to look at the image directly
    when filename has no keywords (e.g. 01.jpg, 02.png, generic numbers).
    """
    if not image_path or not os.path.exists(image_path):
        return []
    try:
        from google import genai
        from PIL import Image
        key_path = os.path.join(BASE_DIR, "gemini_key.txt")
        if not os.path.exists(key_path):
            return []
        with open(key_path, "r", encoding="utf-8") as kf:
            gemini_key = kf.read().strip()
        if not gemini_key:
            return []
            
        client = genai.Client(api_key=gemini_key, http_options={"timeout": 45000})
        img = Image.open(image_path)
        img.thumbnail((512, 512))
        prompt = """Look at this thumbnail image of an Indian woman. Classify it into one or two of these exact categories:
1. sleep_insomnia (night scene, lying in bed, sleeping, dark ambient, moonlight, deep relaxation, eyes closed, nightwear)
2. lotus_lake (lake, water, pond, river, lotus flowers, serene water balcony)
3. raag_darbari (royal palace, heavy royal choli, ornate gold/kundan necklace, fortress, classical sitar/veena)
4. bansuri_tabla (flute, bansuri, tabla, musical performance, morpankh)
5. morning_pooja (sunrise, dawn, temple, diya, morning golden sunlight, morning prayers)
6. stress_relief (calm peaceful nature, soft light, meditation, relaxing serene atmosphere)
7. lofi_beats (cozy, warm ambient, aesthetic lofi mood)

Reply ONLY with the matching category name(s) separated by commas, nothing else."""
        res = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[img, prompt]
        )
        raw_text = res.text.strip().lower()
        matched = []
        for cat in CATEGORIES:
            if cat in raw_text:
                matched.append(cat)
        if matched:
            print(f"  -> [AI Vision] '{os.path.basename(image_path)}' classified as: {matched}")
            return matched
    except Exception as e:
        print(f"  -> [AI Vision Notice] Fallback for '{os.path.basename(image_path)}': {e}")
    return []

def classify_by_color_heuristic(image_path):
    """Quick CV heuristic fallback: detects night/dark images for sleep_insomnia"""
    try:
        data = np.fromfile(image_path, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            mean_b = np.mean(gray)
            if mean_b < 65:
                return ['sleep_insomnia']
    except Exception:
        pass
    return []

def get_matched_categories(fname, clean_path=None):
    """
    Multi-category matching:
    1. First checks filename keywords.
    2. If filename has no keywords (e.g. 01.jpg, 02.png), uses AI Vision (Gemini 3.8 Flash)
       to look at the image directly and classify it accurately!
    """
    fl = fname.lower()
    cats = set()
    
    # 1. Sleep & Insomnia (night, sleep, closing eyes, blue sapphire, relaxing, trance)
    if any(k in fl for k in ['closing_eyes', 'closing', 'sapphire', 'blue', 'sleep', 'night', 'moon', 'stars', 'dark', 'tilting', 'head_back', 'relax', 'rain']):
        cats.add('sleep_insomnia')
        
    # 2. Lotus Lake & Water (lake, lotus, river, fortress balcony over water, water ripples)
    if any(k in fl for k in ['lotus', 'lake', 'water', 'pond', 'river', 'balcony', 'fortress_balcony', 'mist', 'tranquil', 'sarovar']):
        cats.add('lotus_lake')
        
    # 3. Raag Darbari & Royal Classical (royal choli, magenta, ruby, kundan, royal necklace, gold choker, fortress)
    if any(k in fl for k in ['choli', 'magenta', 'ruby', 'kundan', 'necklace', 'choker', 'gold_choker', 'fortress', 'royal', 'princess', 'bride', 'attire', 'classical', 'veena']):
        cats.add('raag_darbari')
        
    # 4. Bansuri & Tabla / Spiritual Instruments (peacock feather, morpankh, flute, bansuri, bamboo, tabla)
    if any(k in fl for k in ['peacock', 'feather', 'morpankh', 'flute', 'bansuri', 'bamboo', 'tabla', 'instrument', 'tanpura']):
        cats.add('bansuri_tabla')
        
    # 5. Morning Pooja (gold, smiling, courtyard, temple, sunrise, morning)
    if any(k in fl for k in ['smiling', 'gold', 'temple', 'courtyard', 'sunrise', 'morning', 'dawn', 'sun', 'prabhat', 'balcony', 'pooja']):
        cats.add('morning_pooja')

    # If filename has no keywords (e.g. 01.jpg, 02.png, generic numbers) -> Use AI Vision!
    if not cats and clean_path and os.path.exists(clean_path):
        vision_cats = classify_image_with_ai_vision(clean_path)
        for vc in vision_cats:
            cats.add(vc)
        if not cats:
            heuristic_cats = classify_by_color_heuristic(clean_path)
            for hc in heuristic_cats:
                cats.add(hc)
        
    if not cats:
        cats = {'morning_pooja', 'raag_darbari'}
    elif len(cats) == 1:
        c = list(cats)[0]
        if c == 'raag_darbari':
            cats.add('lotus_lake')
        elif c == 'bansuri_tabla':
            cats.add('morning_pooja')
        elif c == 'sleep_insomnia':
            cats.add('lotus_lake')
        elif c == 'lotus_lake':
            cats.add('sleep_insomnia')
            
    return list(cats)

def clean_watermark(raw_path, clean_path):
    data = np.fromfile(raw_path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        return False
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    x1, x2 = int(w * 0.88), int(w * 0.99)
    y1, y2 = int(h * 0.80), int(h * 0.96)
    corner = img[y1:y2, x1:x2]
    corner_gray = cv2.cvtColor(corner, cv2.COLOR_BGR2GRAY)
    mean_val = np.mean(corner_gray)
    _, thresh = cv2.threshold(corner_gray, int(mean_val + 18), 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    mask[y1:y2, x1:x2] = cv2.dilate(thresh, kernel, iterations=2)
    cleaned = cv2.inpaint(img, mask, inpaintRadius=7, flags=cv2.INPAINT_TELEA)
    is_success, buf = cv2.imencode('.jpg', cleaned, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if is_success:
        with open(clean_path, 'wb') as f:
            f.write(buf)
        return True
    return False

def upload_file_to_catbox(file_path, retries=3):
    curl_path = r"C:\Windows\System32\curl.exe"
    cmd = [
        curl_path, "-k", "-s",
        "-F", "reqtype=fileupload",
        "-F", f"fileToUpload=@{file_path}",
        "https://catbox.moe/user/api.php"
    ]
    for attempt in range(retries):
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=45)
            url = res.stdout.strip()
            if url.startswith("https://files.catbox.moe/"):
                return url
        except Exception:
            pass
        time.sleep(1.5)
    return None

def process_single_image(fname):
    raw_path = os.path.join(RAW_DIR, fname)
    safe_name = fname.replace("…", "_").replace(" ", "_")
    clean_path = os.path.join(CLEAN_DIR, "clean_" + safe_name)
    if not clean_path.lower().endswith(".jpg"):
        clean_path += ".jpg"

    if not os.path.exists(clean_path):
        if not clean_watermark(raw_path, clean_path):
            return fname, [], None

    matched_cats = get_matched_categories(fname, clean_path)
    url = upload_file_to_catbox(clean_path)
    return fname, matched_cats, url, clean_path

def main():
    uploaded_files = set()
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            uploaded_files = {line.strip() for line in f if line.strip()}

    all_files = [f for f in os.listdir(RAW_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    to_process = [f for f in all_files if f not in uploaded_files]

    print(f"Total raw images in pool: {len(all_files)}")
    print(f"Already uploaded: {len(uploaded_files)}")
    print(f"Pending upload (new batch): {len(to_process)}")

    if not to_process:
        print("All images are already uploaded and synced!")
        return

    tracker_f = open(TRACKER_FILE, "a", encoding="utf-8")

    print(f"\nStarting multi-threaded upload of {len(to_process)} images with 10 workers...")
    start_time = time.time()
    success_count = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_single_image, f): f for f in to_process}
        for future in as_completed(futures):
            fname, matched_cats, url, clean_path = future.result()
            if url:
                success_count += 1
                # Classify side for 100% deterministic zero-error placement
                side = "right"
                try:
                    from split_thumbnail_pools import analyze_image_bytes
                    with open(clean_path, "rb") as cf:
                        s_res = analyze_image_bytes(cf.read())
                        if s_res in ["RIGHT", "LEFT"]:
                            side = s_res.lower()
                except Exception:
                    pass

                # Multi-category sync: copy URL into ALL matching category queues!
                for cat in matched_cats:
                    q_path = os.path.join(BASE_DIR, f"thumbnail_urls_{cat}.txt")
                    b_path = os.path.join(BASE_DIR, f"thumbnail_urls_{cat}_backup.txt")
                    with open(q_path, "a", encoding="utf-8") as qf:
                        qf.write(url + "\n")
                    with open(b_path, "a", encoding="utf-8") as bf:
                        bf.write(url + "\n")

                    # Also sync into split deterministic Left/Right queues!
                    sq_path = os.path.join(BASE_DIR, f"thumbnail_urls_{cat}_{side}.txt")
                    sb_path = os.path.join(BASE_DIR, f"thumbnail_urls_{cat}_{side}_backup.txt")
                    with open(sq_path, "a", encoding="utf-8") as sqf:
                        sqf.write(url + "\n")
                    with open(sb_path, "a", encoding="utf-8") as sbf:
                        sbf.write(url + "\n")

                tracker_f.write(fname + "\n")
                tracker_f.flush()

                if success_count % 15 == 0 or success_count == len(to_process):
                    elapsed = round(time.time() - start_time, 1)
                    print(f"  [+] Uploaded {success_count}/{len(to_process)} in {elapsed}s... (Cats: {matched_cats})")
            else:
                print(f"  [-] Failed to upload: {fname}")

    tracker_f.close()

    total_time = round(time.time() - start_time, 1)
    print(f"\n=======================================================")
    print(f"Batch Upload Complete: {success_count}/{len(to_process)} in {total_time}s!")
    print(f"=======================================================\n")

if __name__ == "__main__":
    main()
