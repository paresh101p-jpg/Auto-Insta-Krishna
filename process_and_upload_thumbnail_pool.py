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
RAW_DIR = os.path.join(BASE_DIR, "thumbnail_pool_raw")
CLEAN_DIR = os.path.join(BASE_DIR, "thumbnail_pool_clean")
TRACKER_FILE = os.path.join(BASE_DIR, "uploaded_thumbnail_images_tracker.txt")

os.makedirs(CLEAN_DIR, exist_ok=True)

CATEGORIES = ["morning_pooja", "bansuri_tabla", "raag_darbari", "lotus_lake", "sleep_insomnia"]

def categorize(fname):
    fl = fname.lower()
    if any(k in fl for k in ['sleep', 'night', 'moon', 'star', 'insomnia', 'deep_sleep', 'relaxing', 'rain', 'blue', 'dark', 'midnight']):
        return 'sleep_insomnia'
    elif any(k in fl for k in ['lotus', 'lake', 'sarovar', 'water', 'pond', 'swan', 'river', 'mist', 'ghat', 'tranquil']):
        return 'lotus_lake'
    elif any(k in fl for k in ['royal', 'darbari', 'darbar', 'palace', 'rajkumari', 'attire', 'queen', 'princess', 'bride', 'bridal', 'kundan', 'jewelry', 'saree', 'choli', 'classical', 'veena']):
        return 'raag_darbari'
    elif any(k in fl for k in ['tabla', 'jugalbandi', 'rhythm', 'tanpura', 'sitar', 'instrument', 'flute', 'bansuri', 'bamboo']):
        return 'bansuri_tabla'
    elif any(k in fl for k in ['sunrise', 'morning', 'dawn', 'sun', 'prabhat', 'temple', 'courtyard', 'pooja', 'golden']):
        return 'morning_pooja'
    else:
        return 'morning_pooja'

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
            return fname, None, None

    cat = categorize(fname)
    url = upload_file_to_catbox(clean_path)
    return fname, cat, url

def main():
    uploaded_files = set()
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            uploaded_files = {line.strip() for line in f if line.strip()}

    all_files = [f for f in os.listdir(RAW_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    to_process = [f for f in all_files if f not in uploaded_files]

    print(f"Total raw images: {len(all_files)}")
    print(f"Already uploaded: {len(uploaded_files)}")
    print(f"Pending upload: {len(to_process)}")

    if not to_process:
        print("All thumbnail images are already uploaded!")
        return

    # Categorized file handlers
    cat_files = {}
    cat_backups = {}
    for c in CATEGORIES:
        cat_files[c] = open(os.path.join(BASE_DIR, f"thumbnail_urls_{c}.txt"), "a", encoding="utf-8")
        cat_backups[c] = open(os.path.join(BASE_DIR, f"thumbnail_urls_{c}_backup.txt"), "a", encoding="utf-8")

    tracker_f = open(TRACKER_FILE, "a", encoding="utf-8")

    print(f"\nStarting multi-threaded upload with 10 workers...")
    start_time = time.time()
    success_count = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_single_image, f): f for f in to_process}
        for future in as_completed(futures):
            fname, cat, url = future.result()
            if url:
                success_count += 1
                cat_files[cat].write(url + "\n")
                cat_files[cat].flush()
                cat_backups[cat].write(url + "\n")
                cat_backups[cat].flush()
                tracker_f.write(fname + "\n")
                tracker_f.flush()
                if success_count % 25 == 0 or success_count == len(to_process):
                    elapsed = round(time.time() - start_time, 1)
                    print(f"  [+] Uploaded {success_count}/{len(to_process)} images in {elapsed}s... (Latest: {cat})")
            else:
                print(f"  [-] Failed to upload: {fname}")

    for c in CATEGORIES:
        cat_files[c].close()
        cat_backups[c].close()
    tracker_f.close()

    total_time = round(time.time() - start_time, 1)
    print(f"\n=======================================================")
    print(f"Batch Upload Complete: {success_count}/{len(to_process)} in {total_time}s!")
    print(f"=======================================================\n")

if __name__ == "__main__":
    main()

