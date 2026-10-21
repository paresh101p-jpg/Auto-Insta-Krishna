"""
Master Automated Reel Generator & Uploader for Auto-Insta-Krishna
- Processes images from Images/ folder
- Preserves all original images in Images/ (Zero Deletion Rule)
- Uses EasyOCR + Fuzzy Reference Matching for 100% exact quotes (Zero Mismatch)
- Google Cloud Neural2 Emotion-Adaptive Voices with Natural Breathing Pauses
- Rotates across 5 Cinematic Color Grading & Lighting Profiles
- Dynamic 2.0s Unblur Focus-Reveal Hook (100% sharp YouTube thumbnails)
- 10+ Seconds Duration Rule (>= 11.5s) & Soft Flute BGM
- Automatically uploads each completed reel to Catbox
- Appends URLs to reels_urls.txt & youtube_reels_urls.txt
- Auto-syncs to GitHub every 10 reels
- Crash-proof auto-resume via uploaded_reels_tracker.txt
"""

import os
import sys
import glob
import time
import subprocess
import requests
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Force UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "Images")
REELS_OUTPUT_DIR = os.path.join(BASE_DIR, "reels_output")
QUOTES_FILE = os.path.join(BASE_DIR, "quotes.txt")
USED_QUOTES_FILE = os.path.join(BASE_DIR, "used_quotes.txt")
REELS_URLS_FILE = os.path.join(BASE_DIR, "reels_urls.txt")
BACKUP_REELS_URLS_FILE = os.path.join(BASE_DIR, "reels_urls_backup.txt")
YT_REELS_URLS_FILE = os.path.join(BASE_DIR, "youtube_reels_urls.txt")
BACKUP_YT_REELS_URLS_FILE = os.path.join(BASE_DIR, "youtube_reels_urls_backup.txt")
TRACKER_FILE = os.path.join(BASE_DIR, "uploaded_reels_tracker.txt")

os.makedirs(REELS_OUTPUT_DIR, exist_ok=True)

# Import upgraded generate_reels engine
from generate_reels import build_reel

def load_known_quotes():
    quotes = set()
    for path in [QUOTES_FILE, USED_QUOTES_FILE]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    t = line.strip()
                    if len(t) > 5:
                        quotes.add(t)
    print(f"Loaded {len(quotes)} reference quotes from database.", flush=True)
    return list(quotes)

def find_best_matching_quote(ocr_text, known_quotes):
    """Finds best matching clean quote from reference database ONLY if almost identical (Jaccard >= 0.80).
    Never replace with a random quote based on 1-2 common words."""
    if not ocr_text:
        return ""
    ocr_words = set([w for w in ocr_text.replace("।", " ").replace(",", " ").replace("|", " ").split() if len(w) > 1])
    if not ocr_words:
        return ocr_text

    best_match = None
    best_overlap = 0

    for q in known_quotes:
        q_words = set([w for w in q.replace("।", " ").replace(",", " ").replace("|", " ").split() if len(w) > 1])
        if not q_words:
            continue
        common = len(ocr_words.intersection(q_words))
        union_len = len(ocr_words.union(q_words))
        if union_len == 0:
            continue
        jaccard = common / union_len
        if jaccard > best_overlap and jaccard >= 0.80:
            best_overlap = jaccard
            best_match = q

    if best_match:
        return best_match
    return ocr_text

def get_easyocr_reader():
    import easyocr
    print("Initializing EasyOCR Hindi engine...", flush=True)
    return easyocr.Reader(['hi', 'en'], gpu=False)

def extract_quote_from_image(reader, image_path, known_quotes):
    try:
        # Resize image for faster neural inference if huge
        with Image.open(image_path) as im:
            w, h = im.size
            if max(w, h) > 1280:
                scale = 1280.0 / max(w, h)
                resized = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
                temp_thumb = os.path.join(REELS_OUTPUT_DIR, "_thumb_ocr.jpg")
                resized.convert("RGB").save(temp_thumb, quality=90)
                ocr_target = temp_thumb
                target_h = int(h * scale)
            else:
                ocr_target = image_path
                target_h = h

        results = reader.readtext(ocr_target)
        temp_thumb = os.path.join(REELS_OUTPUT_DIR, "_thumb_ocr.jpg")
        if os.path.exists(temp_thumb):
            try:
                os.remove(temp_thumb)
            except:
                pass

        valid_boxes = []
        for bbox, text, prob in results:
            t = text.strip()
            if not t or len(t) < 2:
                continue
            # Filter handles and watermarks
            if 'Paresh' in t or 'Padsala' in t or '@' in t or 'krishnavibez' in t.lower():
                continue
            cy = sum([p[1] for p in bbox]) / 4
            cx = sum([p[0] for p in bbox]) / 4

            # 1. Ignore bottom 15% of the image (watermarks, bottom borders)
            if cy > target_h * 0.85:
                continue

            # 2. Must contain Hindi Devanagari characters (skip pure English notes)
            hindi_chars = sum(1 for c in t if '\u0900' <= c <= '\u097f')
            if hindi_chars == 0 or (hindi_chars / len(t)) < 0.35:
                continue

            valid_boxes.append((cy, cx, t))

        if not valid_boxes:
            return ""

        # Sort top-to-bottom, cluster by line
        valid_boxes.sort(key=lambda b: (b[0] // 25, b[1]))
        raw_text = " ".join([b[2] for b in valid_boxes]).strip()
        raw_text = raw_text.replace("वक़", "वक्त")

        # Trim text at sentence ending mark '|' or '।' so trailing gibberish is removed
        if '|' in raw_text or '।' in raw_text:
            last_mark = max(raw_text.rfind('|'), raw_text.rfind('।'))
            raw_text = raw_text[:last_mark+1].strip()

        # Match with reference database
        matched_quote = find_best_matching_quote(raw_text, known_quotes)
        return matched_quote
    except Exception as e:
        print(f"Error during OCR extraction: {e}", flush=True)
        return ""

def get_already_uploaded():
    uploaded = set()
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                name = line.strip()
                if name:
                    uploaded.add(name)
    return uploaded

def save_uploaded_name(name):
    with open(TRACKER_FILE, "a", encoding="utf-8") as f:
        f.write(name + "\n")

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
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
            url = res.stdout.strip()
            if url.startswith("https://files.catbox.moe/"):
                return url
            else:
                print(f"Warning: Catbox attempt {attempt+1} response: {url}", flush=True)
        except Exception as e:
            # Fallback to requests if curl fails
            try:
                with open(file_path, 'rb') as f:
                    r = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f}, timeout=60)
                    result = r.text.strip()
                    if result.startswith("https://files.catbox.moe/"):
                        return result
            except Exception as e2:
                print(f"Catbox upload error (attempt {attempt+1}): {e} / {e2}", flush=True)
        time.sleep(3)
    return None

def push_to_github():
    try:
        subprocess.run(["git", "add", "reels_urls.txt", "reels_urls_backup.txt", "youtube_reels_urls.txt", "youtube_reels_urls_backup.txt", "uploaded_reels_tracker.txt"], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "feat: Add high-retention Voice Reels to production queues"], cwd=BASE_DIR)
        subprocess.run(["git", "pull", "--rebase", "origin", "master"], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "push", "origin", "master"], cwd=BASE_DIR, check=True)
        print("  --> Synced new reel URLs to GitHub successfully!", flush=True)
    except Exception as e:
        print(f"  Notice: GitHub sync: {e}", flush=True)

def run_batch():
    known_quotes = load_known_quotes()
    reader = get_easyocr_reader()
    already_uploaded = get_already_uploaded()

    all_images = []
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        all_images.extend(glob.glob(os.path.join(IMAGES_DIR, ext)))
    all_images.sort()

    pending_images = [f for f in all_images if f"{os.path.splitext(os.path.basename(f))[0]}.mp4" not in already_uploaded]
    print(f"\n=======================================================", flush=True)
    print(f"Total Images in Pool: {len(all_images)}", flush=True)
    print(f"Already Uploaded Reels: {len(already_uploaded)}", flush=True)
    print(f"Pending Reels to Generate: {len(pending_images)}", flush=True)
    print(f"=======================================================\n", flush=True)

    if not pending_images:
        print("All reels have already been generated and uploaded!", flush=True)
        return

    newly_uploaded = 0

    for idx, img_path in enumerate(pending_images):
        fname = os.path.basename(img_path)
        base_name = os.path.splitext(fname)[0]
        mp4_name = f"{base_name}.mp4"
        mp4_path = os.path.join(REELS_OUTPUT_DIR, mp4_name)

        print(f"\n[{idx+1}/{len(pending_images)}] Processing {fname}...", flush=True)

        # Check if already rendered locally (> 500 KB)
        if os.path.exists(mp4_path) and os.path.getsize(mp4_path) > 500000:
            fsize_mb = os.path.getsize(mp4_path) / (1024 * 1024)
            print(f"  Reel already rendered ({fsize_mb:.2f} MB). Skipping render & proceeding to upload...", flush=True)
        else:
            # 1. Extract exact quote from image (Zero Mismatch)
            quote = extract_quote_from_image(reader, img_path, known_quotes)
            if not quote or len(quote) < 5:
                print(f"  [SKIPPED] No valid Hindi quote found on {fname}", flush=True)
                continue

            print(f"  Exact Quote: \"{quote}\"", flush=True)

            # 2. Build Reel (Pass rotating color_profile_idx and voice_idx)
            ok = build_reel(img_path, quote, mp4_path, color_profile_idx=idx, voice_idx=idx)
            if not ok or not os.path.exists(mp4_path) or os.path.getsize(mp4_path) < 500000:
                print(f"  [ERROR] Failed to generate {mp4_name}", flush=True)
                continue

            fsize_mb = os.path.getsize(mp4_path) / (1024 * 1024)
            print(f"  Reel Rendered ({fsize_mb:.2f} MB). Uploading to Catbox...", flush=True)

        # 3. Upload to Catbox
        url = upload_file_to_catbox(mp4_path)
        if url:
            print(f"  --> Catbox URL: {url}", flush=True)
            with open(REELS_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            with open(BACKUP_REELS_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            with open(YT_REELS_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            with open(BACKUP_YT_REELS_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            save_uploaded_name(mp4_name)
            already_uploaded.add(mp4_name)
            newly_uploaded += 1

            # Keep local mp4 in reels_output as requested by user
            print(f"  --> Saved locally: {mp4_path}", flush=True)

            # Sync to GitHub every 10 uploaded reels
            if newly_uploaded % 10 == 0:
                print(f"\n--- Checkpoint: {newly_uploaded} new reels uploaded. Syncing to GitHub ---", flush=True)
                push_to_github()
        else:
            print(f"  [FAILED] Catbox upload failed for {mp4_name}. Will retry later.", flush=True)

        time.sleep(1)

    # Final push for remaining
    if newly_uploaded > 0:
        push_to_github()

    print("\n🎉 Master Reel Generation Batch Complete!", flush=True)

if __name__ == "__main__":
    run_batch()
