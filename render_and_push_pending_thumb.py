import os
import sys
import base64
import subprocess
import cv2
import numpy as np
import json
import shutil
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"E:\Paresh\Auto Post\Auto-Insta-Krishna"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
FFMPEG = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
TEMP_DIR = r"C:\Users\Admin\.gemini\antigravity\brain\5edf39f6-759b-4d35-b525-27352f306f0f"
TOKEN_FILE = os.path.join(BASE_DIR, "youtube_token.json")
DONE_FILE = os.path.join(BASE_DIR, "completed_music_video_thumbnails.json")

def process_and_upload(video_id, raw_img_name, hook_pill, hook_lead, hook_benefit, badge_tag, badge_title, badge_dur):
    src_img = os.path.join(BASE_DIR, "thumbnail_pool_raw", raw_img_name)
    print(f"\n[1/4] Reading source image: {src_img}")
    
    data = np.fromfile(src_img, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]

    # Watermark Telea inpainting
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

    clean_jpg = os.path.join(TEMP_DIR, f"clean_{video_id}.jpg")
    is_success, buf = cv2.imencode(".jpg", cleaned)
    with open(clean_jpg, "wb") as f:
        f.write(buf)

    with open(clean_jpg, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode("utf-8")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Hindi:ital,wght@0,400;0,700;1,400&family=Montserrat:wght@800;900&family=Poppins:wght@700;800;900&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1920px;
    height: 1080px;
    position: relative;
    overflow: hidden;
    background-color: #000;
  }}
  .bg {{
    position: absolute;
    top: 0; left: 0; width: 1920px; height: 1080px;
    background-image: url('data:image/jpeg;base64,{bg_b64}');
    background-size: cover;
    background-position: center;
  }}
  .vignette {{
    position: absolute;
    top: 0; left: 0; width: 1920px; height: 1080px;
    background: radial-gradient(circle at 25% 30%, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.5) 45%, rgba(0,0,0,0) 75%),
                linear-gradient(90deg, rgba(0,0,0,0.65) 0%, rgba(0,0,0,0.2) 45%, rgba(0,0,0,0) 65%);
    pointer-events: none;
  }}
  .text-container {{
    position: absolute;
    top: 60px;
    left: 80px;
    max-width: 1050px;
    z-index: 10;
    overflow: visible;
    padding-top: 20px;
  }}
  .hook-pill {{
    display: inline-flex;
    align-items: center;
    background: linear-gradient(90deg, #D50000 0%, #FF1744 100%);
    border: 3px solid #FFF;
    border-radius: 12px;
    padding: 10px 30px;
    margin-bottom: 25px;
    color: #FFFFFF;
    font-family: 'Poppins', 'Tiro Devanagari Hindi', sans-serif;
    font-size: 38px;
    font-weight: 900;
    letter-spacing: 1px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.9), 0 0 25px rgba(255, 23, 68, 0.7);
    text-shadow: 0 2px 4px rgba(0,0,0,0.8);
  }}
  .hook-lead {{
    font-family: 'Tiro Devanagari Hindi', 'Nirmala UI', serif;
    font-size: 92px;
    font-weight: 700;
    line-height: 1.35;
    padding-top: 15px;
    color: #FFE600;
    letter-spacing: 1px;
    text-shadow: 0 4px 0 #1A0D00, 0 8px 0 #000, 0 12px 28px rgba(0,0,0,0.98), 0 0 35px rgba(255, 230, 0, 0.85);
    margin-bottom: 5px;
    overflow: visible;
  }}
  .hook-benefit {{
    font-family: 'Tiro Devanagari Hindi', 'Nirmala UI', serif;
    font-size: 118px;
    font-weight: 700;
    line-height: 1.35;
    padding-top: 15px;
    letter-spacing: 1px;
    color: #FFF8E1;
    text-shadow: 0 4px 0 #FF8F00, 0 7px 0 #C43800, 0 10px 0 #200800, 0 14px 30px rgba(0,0,0,0.98), 0 0 45px rgba(255, 179, 0, 0.9);
    overflow: visible;
  }}

  /* High-Contrast Luxury Full-Length Bottom Base Line */
  .bottom-badge-container {{
    position: absolute;
    bottom: 30px;
    left: 50px;
    right: 50px;
    z-index: 20;
    display: flex;
    justify-content: center;
  }}
  .bottom-badge {{
    width: 100%;
    background: linear-gradient(90deg, rgba(8, 4, 1, 0.98) 0%, rgba(28, 14, 2, 0.96) 20%, rgba(45, 20, 0, 0.96) 50%, rgba(28, 14, 2, 0.96) 80%, rgba(8, 4, 1, 0.98) 100%);
    border: 3.5px solid #FFD54F;
    border-radius: 60px;
    padding: 16px 45px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 15px 40px rgba(0,0,0,0.98), 0 0 35px rgba(255, 213, 79, 0.5);
  }}
  .badge-tag {{
    font-family: 'Poppins', 'Montserrat', sans-serif;
    font-size: 38px;
    font-weight: 900;
    color: #FFD54F;
    text-shadow: 0 3px 6px #000, 0 0 20px rgba(255, 213, 79, 0.7);
    letter-spacing: 2px;
  }}
  .badge-title {{
    font-family: 'Tiro Devanagari Hindi', 'Nirmala UI', serif;
    font-size: 52px;
    font-weight: 700;
    color: #FFFFFF;
    text-shadow: 0 3px 8px #000, 0 0 25px rgba(255, 255, 255, 0.8);
    letter-spacing: 1px;
    padding-top: 6px;
  }}
  .badge-dur {{
    background: linear-gradient(135deg, #FFD54F 0%, #FF8F00 100%);
    color: #1A0D00;
    border: 3px solid #FFFDE7;
    border-radius: 35px;
    padding: 10px 30px;
    font-family: 'Poppins', sans-serif;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 2px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.9), 0 0 25px rgba(255, 213, 79, 0.6);
  }}
</style>
</head>
<body>
  <div class="bg"></div>
  <div class="vignette"></div>
  
  <div class="text-container">
    <div class="hook-pill">{hook_pill}</div>
    <div class="hook-lead">{hook_lead}</div>
    <div class="hook-benefit">{hook_benefit}</div>
  </div>

  <div class="bottom-badge-container">
    <div class="bottom-badge">
      <span class="badge-tag">{badge_tag}</span>
      <span class="badge-title">{badge_title}</span>
      <span class="badge-dur">{badge_dur}</span>
    </div>
  </div>
</body>
</html>
"""

    html_out = os.path.join(TEMP_DIR, f"thumb_{video_id}.html")
    png_out = os.path.join(TEMP_DIR, f"thumb_{video_id}.png")
    out_dir = os.path.join(BASE_DIR, "music_video_thumbnails")
    os.makedirs(out_dir, exist_ok=True)
    jpg_out = os.path.join(out_dir, f"thumb_{video_id}.jpg")

    with open(html_out, "w", encoding="utf-8") as f:
        f.write(html)

    print("[2/4] Rendering 1920x1080 with Edge Headless...")
    file_uri = "file:///" + os.path.abspath(html_out).replace("\\", "/")
    subprocess.run([
        EDGE, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--virtual-time-budget=5000", "--run-all-compositor-stages-before-draw",
        "--window-size=1920,1080", f"--screenshot={png_out}", file_uri
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    print("[3/4] Optimizing to high-res JPG with FFmpeg...")
    subprocess.run([
        FFMPEG, "-y", "-i", png_out, "-vf", "scale=1280:720", "-q:v", "2", jpg_out
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Copy to temp dir for user artifact preview
    shutil.copy2(jpg_out, os.path.join(TEMP_DIR, f"thumb_{video_id}.jpg"))
    print(f"Master thumbnail rendered: {jpg_out} ({os.path.getsize(jpg_out)} bytes)")

    print(f"[4/4] Pushing to YouTube video {video_id}...")
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        token_data = json.load(f)

    creds = Credentials.from_authorized_user_info(token_data)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    youtube = build("youtube", "v3", credentials=creds)
    media = MediaFileUpload(jpg_out, mimetype="image/jpeg", resumable=False)
    resp = youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
    print(f"YouTube Thumbnails API Response: {resp}")

    done_data = {}
    if os.path.exists(DONE_FILE):
        try:
            with open(DONE_FILE, "r", encoding="utf-8") as f:
                done_data = json.load(f)
        except Exception:
            done_data = {}

    done_data[video_id] = {
        "status": "uploaded",
        "file": jpg_out,
        "title": badge_title
    }
    with open(DONE_FILE, "w", encoding="utf-8") as f:
        json.dump(done_data, f, indent=2, ensure_ascii=False)

    print(f"SUCCESS: Video {video_id} thumbnail updated and pushed to YouTube!\n")

if __name__ == "__main__":
    process_and_upload(
        video_id="kLW2bl0x2hQ",
        raw_img_name="Woman_meditating_in_sunrise_light_0b91b176.jpg",
        hook_pill="🔔 सिर्फ 10 मिनट रोज सुनो",
        hook_lead="सारे कष्ट व तनाव दूर होंगे",
        hook_benefit="मन को असीम शांति मिलेगी",
        badge_tag="✨ SUNRISE BANSURI & TABLA",
        badge_title="सूर्योदय पावन मुरली एवं तबला",
        badge_dur="39 MIN"
    )

