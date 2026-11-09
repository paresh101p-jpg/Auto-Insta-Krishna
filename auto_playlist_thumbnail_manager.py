# -*- coding: utf-8 -*-
"""
Auto Playlist Thumbnail Manager & Hook Cover Engine
- Analyzes playlist titles to create high-CTR, hook-styled 16:9 thumbnails.
- Automatically pairs with lead video (Position 0) to set official playlist cover on YouTube.
- Callable both standalone (for auditing/updating all playlists) and inside auto_music_video_pipeline.py (whenever a new playlist is created).
"""

import os
import sys
import json
import re
import subprocess
import shutil
import requests

sys.stdout.reconfigure(encoding="utf-8")

def log(msg):
    print(msg, flush=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "youtube_token.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "playlist_thumbnails")
IMAGES_DIR = os.path.join(BASE_DIR, "music_video_images")
ARTIFACTS_DIR = r"C:\Users\Admin\.gemini\antigravity\brain\5edf39f6-759b-4d35-b525-27352f306f0f"

os.makedirs(OUTPUT_DIR, exist_ok=True)

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE_PATH):
    EDGE_PATH = "msedge"

# Knowledge base of themes mapped to playlist title keywords (Specific themes first!)
THEME_PRESETS = [
    {
        "keywords": ["lotus", "lake", "sarovar", "kamal"],
        "badge": "🌸 SACRED LOTUS LAKE",
        "main_title": "शांत कमल सरोवर बाँसुरी",
        "sub_title": "मन की एकाग्रता • दिव्य शांति • आत्मिक सुकून",
        "time_badge": "LOTUS DHYAN",
        "gold_glow": "#f472b6",
        "badge_grad": "linear-gradient(135deg, #db2777, #f472b6)",
        "badge_border": "#fbcfe8",
        "sub_color": "#fce7f3",
        "bg_keyword": "lotus"
    },
    {
        "keywords": ["sleep", "night", "neend", "insomnia", "soye"],
        "badge": "🌙 DEEP MEDITATION SLEEP",
        "main_title": "गहरी निद्रा बाँसुरी",
        "sub_title": "अनिद्रा व तनाव से तुरंत राहत • 100% शांत मन",
        "time_badge": "15 MIN SLEEP",
        "gold_glow": "#38bdf8",
        "badge_grad": "linear-gradient(135deg, #0284c7, #38bdf8)",
        "badge_border": "#7dd3fc",
        "sub_color": "#bae6fd",
        "bg_keyword": "sleep"
    },
    {
        "keywords": ["morning", "gokul", "pooja", "subah"],
        "badge": "☀️ GOKUL MORNING FLUTE",
        "main_title": "गोकुल प्रातःकालीन बाँसुरी",
        "sub_title": "नित्य पूजा व ध्यान • दिन की शुभ शुरुआत",
        "time_badge": "MORNING POOJA",
        "gold_glow": "#fbbf24",
        "badge_grad": "linear-gradient(135deg, #b45309, #f59e0b)",
        "badge_border": "#fde68a",
        "sub_color": "#fef08a",
        "bg_keyword": "morning"
    },
    {
        "keywords": ["sunrise", "dawn", "prabhat", "golden"],
        "badge": "🌅 GOLDEN DAWN MEDITATION",
        "main_title": "सूर्योदय पावन मुरली",
        "sub_title": "प्रातः काल ध्यान • सकारात्मक ऊर्जा • शुभ प्रभात",
        "time_badge": "SUNRISE DHYAN",
        "gold_glow": "#f59e0b",
        "badge_grad": "linear-gradient(135deg, #d97706, #f59e0b)",
        "badge_border": "#fde68a",
        "sub_color": "#fef3c7",
        "bg_keyword": "sunrise"
    },
    {
        "keywords": ["yamuna", "river", "ghat", "nadi"],
        "badge": "🌊 SACRED YAMUNA RIVER",
        "main_title": "यमुना तट पावन प्रवाह",
        "sub_title": "संध्या आरती • बहती जल तरंगें • अलौकिक शांति",
        "time_badge": "RIVER DHUN",
        "gold_glow": "#60a5fa",
        "badge_grad": "linear-gradient(135deg, #2563eb, #60a5fa)",
        "badge_border": "#bfdbfe",
        "sub_color": "#dbeafe",
        "bg_keyword": "yamuna"
    },
    {
        "keywords": ["darbari", "raga", "raag", "royal"],
        "badge": "👑 MAJESTIC RAAG DARBARI",
        "main_title": "राग दरबारी दिव्य बाँसुरी",
        "sub_title": "गहरा ध्यान • शास्त्रीय तानपुरा व बाँसुरी प्रवाह",
        "time_badge": "ROYAL DHYAN",
        "gold_glow": "#fbbf24",
        "badge_grad": "linear-gradient(135deg, #b45309, #d97706)",
        "badge_border": "#fde047",
        "sub_color": "#fef08a",
        "bg_keyword": "stepwell"
    },
    {
        "keywords": ["jugalbandi", "tabla", "taal", "classical"],
        "badge": "🪕 BANSURI & TABLA JUGALBANDI",
        "main_title": "बाँसुरी व तबला पावन जुगलबंदी",
        "sub_title": "कहरवा ताल • शास्त्रीय धुन • सकारात्मक ऊर्जा",
        "time_badge": "PURE TAAL",
        "gold_glow": "#fbbf24",
        "badge_grad": "linear-gradient(135deg, #d97706, #fbbf24)",
        "badge_border": "#fde68a",
        "sub_color": "#fef08a",
        "bg_keyword": "tanpura"
    },
    {
        "keywords": ["live", "chanting", "stream", "radio", "akhand"],
        "badge": "🔴 24/7 LIVE STREAM RADIO",
        "main_title": "अखंड दिव्य लाइव प्रवाह",
        "sub_title": "24 घंटे अखंड बाँसुरी व महामंत्र • घर में शांति",
        "time_badge": "24/7 LIVE",
        "gold_glow": "#ef4444",
        "badge_grad": "linear-gradient(135deg, #dc2626, #ef4444)",
        "badge_border": "#fca5a5",
        "sub_color": "#fecaca",
        "bg_keyword": "temple"
    },
    {
        "keywords": ["stress", "relief", "mental", "chinta", "tanav"],
        "badge": "🧘 STRESS RELIEF & PEACE",
        "main_title": "तनाव व चिंता मुक्ति बाँसुरी",
        "sub_title": "मानसिक शांति • 100% तनाव मुक्त • विश्राम",
        "time_badge": "STRESS FREE",
        "gold_glow": "#10b981",
        "badge_grad": "linear-gradient(135deg, #059669, #10b981)",
        "badge_border": "#6ee7b7",
        "sub_color": "#a7f3d0",
        "bg_keyword": "meditation"
    },
    {
        "keywords": ["krishna", "divine", "meditation", "dhyan", "peace"],
        "badge": "🕉️ DIVINE MEDITATION FLUTE",
        "main_title": "श्री कृष्ण अमृत बाँसुरी",
        "sub_title": "दिव्य शांति • मानसिक तनाव मुक्ति • अलौकिक आनंद",
        "time_badge": "MEDITATION MASTER",
        "gold_glow": "#facc15",
        "badge_grad": "linear-gradient(135deg, #ca8a04, #eab308)",
        "badge_border": "#fef08a",
        "sub_color": "#fef9c3",
        "bg_keyword": "kadamba"
    }
]

def analyze_playlist_theme(playlist_title):
    clean_title = playlist_title.lower()
    for preset in THEME_PRESETS:
        for kw in preset["keywords"]:
            if kw in clean_title:
                return preset
    return THEME_PRESETS[-1]

def find_bg_image(bg_keyword):
    matches = []
    for root, dirs, files in os.walk(IMAGES_DIR):
        for f in sorted(files):
            if bg_keyword.lower() in f.lower() and f.lower().endswith(('.jpg', '.png', '.jpeg')):
                matches.append(os.path.join(root, f))
                if len(matches) >= 3:
                    break
        if matches:
            break
            
    if matches:
        return matches[0]
        
    pool = os.path.join(IMAGES_DIR, "All catagery Krisha music photo")
    if os.path.exists(pool):
        for f in os.listdir(pool):
            if bg_keyword.lower() in f.lower() and f.lower().endswith(('.jpg', '.png', '.jpeg')):
                return os.path.join(pool, f)
        first_files = [f for f in os.listdir(pool) if f.lower().endswith(('.jpg', '.png'))]
        if first_files:
            return os.path.join(pool, first_files[0])
            
    for root, dirs, files in os.walk(IMAGES_DIR):
        for f in files:
            if f.lower().endswith(('.jpg', '.png')):
                return os.path.join(root, f)
    return None

def render_playlist_thumbnail(design, output_jpg):
    bg_file = find_bg_image(design["bg_keyword"])
    if not bg_file:
        raise FileNotFoundError(f"No background image found for {design['bg_keyword']}")
        
    bg_uri = bg_file.replace("\\", "/")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Hindi:ital@0;1&family=Cinzel:wght@700;900&family=Montserrat:wght@800;900&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    width: 1280px; height: 720px;
    background: #000;
    overflow: hidden;
    font-family: 'Tiro Devanagari Hindi', serif;
}}
.container {{
    position: relative; width: 1280px; height: 720px;
}}
.bg {{
    position: absolute; width: 100%; height: 100%;
    background-image: url('file:///{bg_uri}');
    background-size: cover; background-position: center;
    filter: brightness(0.68) saturate(1.25) contrast(1.1);
}}
.vignette {{
    position: absolute; width: 100%; height: 100%;
    background: radial-gradient(circle at 60% 45%, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.65) 60%, rgba(0,0,0,0.92) 100%),
                linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.4) 35%, transparent 65%);
}}
.border-frame {{
    position: absolute; top: 22px; left: 22px; right: 22px; bottom: 22px;
    border: 3px solid {design['gold_glow']}88;
    border-radius: 12px;
    box-shadow: inset 0 0 35px {design['gold_glow']}44, 0 0 30px rgba(0, 0, 0, 0.9);
    pointer-events: none;
}}
.badge-top {{
    position: absolute; top: 40px; left: 45px;
    background: linear-gradient(135deg, rgba(20, 20, 20, 0.92), rgba(40, 40, 40, 0.95));
    border: 1.5px solid {design['gold_glow']};
    padding: 8px 24px; border-radius: 30px;
    font-family: 'Cinzel', serif; font-size: 19px; font-weight: 900;
    color: #fff; letter-spacing: 2px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.7), 0 0 15px {design['gold_glow']}55;
}}
.badge-right {{
    position: absolute; top: 40px; right: 45px;
    background: {design['badge_grad']};
    border: 1.5px solid {design['badge_border']};
    padding: 8px 22px; border-radius: 8px;
    font-family: 'Montserrat', sans-serif; font-size: 17px; font-weight: 900;
    color: #ffffff; letter-spacing: 1.5px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.6);
}}
.content-box {{
    position: absolute; bottom: 42px; left: 45px; right: 45px;
    text-align: left;
}}
.main-title {{
    font-size: 84px; font-weight: 900; line-height: 1.15;
    color: #ffffff;
    letter-spacing: 0.5px;
    text-shadow: 0 4px 12px rgba(0,0,0,0.95), 0 0 35px {design['gold_glow']};
    margin-bottom: 8px;
}}
.sub-title {{
    font-size: 34px; font-weight: 700;
    color: {design['sub_color']};
    text-shadow: 0 3px 10px rgba(0,0,0,0.95), 0 0 15px {design['gold_glow']}88;
    letter-spacing: 0.5px;
}}
</style>
</head>
<body>
<div class="container">
    <div class="bg"></div>
    <div class="vignette"></div>
    <div class="border-frame"></div>
    <div class="badge-top">{design['badge']}</div>
    <div class="badge-right">{design['time_badge']}</div>
    <div class="content-box">
        <div class="main-title">{design['main_title']}</div>
        <div class="sub-title">{design['sub_title']}</div>
    </div>
</div>
</body>
</html>"""

    temp_id = re.sub(r'[^a-zA-Z0-9]', '', design.get("id", "temp"))
    html_file = os.path.join(OUTPUT_DIR, f"temp_{temp_id}.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    temp_png = os.path.join(OUTPUT_DIR, f"temp_{temp_id}.png")
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1280,720",
        f"--screenshot={temp_png}",
        f"file:///{html_file.replace(os.sep, '/')}"
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    import cv2
    img = cv2.imread(temp_png)
    cv2.imwrite(output_jpg, img, [cv2.IMWRITE_JPEG_QUALITY, 95])

    try:
        os.remove(html_file)
        os.remove(temp_png)
    except Exception:
        pass
        
    return output_jpg

def get_oauth_token():
    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        t = json.load(f)
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": t["client_id"],
        "client_secret": t["client_secret"],
        "refresh_token": t["refresh_token"],
        "grant_type": "refresh_token"
    }, timeout=15)
    return resp.json()["access_token"]

def upload_thumbnail_to_video(vid, thumb_path, access_token):
    thumb_url = f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}&uploadType=media"
    upload_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "image/jpeg"
    }
    with open(thumb_path, "rb") as tf:
        up_res = requests.post(thumb_url, headers=upload_headers, data=tf, timeout=30)
    return up_res.status_code in [200, 201], up_res.status_code, up_res.text

def generate_and_apply_cover(pl_id, title, lead_vid, access_token):
    design = analyze_playlist_theme(title)
    design["id"] = pl_id
    log(f"  -> Selected Theme: '{design['main_title']}' | Badge: '{design['badge']}'")
    
    thumb_path = os.path.join(OUTPUT_DIR, f"Playlist_Cover_{pl_id}.jpg")
    render_playlist_thumbnail(design, thumb_path)
    log(f"  -> ✅ Generated: {thumb_path}")
    
    # Copy to artifacts directory
    if os.path.exists(ARTIFACTS_DIR):
        artifact_copy = os.path.join(ARTIFACTS_DIR, f"playlist_cover_{pl_id}.jpg")
        shutil.copy2(thumb_path, artifact_copy)
        
    log(f"  -> 🚀 Uploading Custom Hook Thumbnail to Lead Video [{lead_vid}]...")
    ok, code, txt = upload_thumbnail_to_video(lead_vid, thumb_path, access_token)
    if ok:
        log(f"  -> 🌟 SUCCESS! Lead Video [{lead_vid}] thumbnail set — Playlist Cover is LIVE!")
    else:
        log(f"  -> Notice on upload ({code}): {txt}")
    return thumb_path

def process_all_playlists():
    log("=" * 65)
    log("🎨 AUTONOMOUS PLAYLIST HOOK THUMBNAIL MANAGER")
    log("=" * 65)
    
    access_token = get_oauth_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 1. Fetch all playlists
    p_url = "https://www.googleapis.com/youtube/v3/playlists?part=snippet,contentDetails&mine=true&maxResults=50"
    p_resp = requests.get(p_url, headers=headers, timeout=15).json()
    playlists = p_resp.get("items", [])
    log(f"Found {len(playlists)} Playlists on Channel.\n")
    
    used_lead_videos = set()
    processed_count = 0
    
    for pl in playlists:
        pl_id = pl["id"]
        title = pl["snippet"]["title"]
        log(f"-----------------------------------------------------------------")
        log(f"🎵 Processing Playlist: '{title}' (ID: {pl_id})")
        
        # Get items in playlist
        it_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={pl_id}&maxResults=20"
        it_resp = requests.get(it_url, headers=headers, timeout=15).json()
        items = it_resp.get("items", [])
        if not items:
            log(f"  ⚠️ Playlist is empty. Skipping.")
            continue
            
        # Pick lead video
        lead_vid = items[0]["snippet"]["resourceId"]["videoId"]
        if lead_vid in used_lead_videos and len(items) > 1:
            for cand in items[1:]:
                cand_vid = cand["snippet"]["resourceId"]["videoId"]
                if cand_vid not in used_lead_videos:
                    log(f"  -> Setting video '{cand_vid}' as unique cover video for playlist...")
                    lead_vid = cand_vid
                    break
                    
        used_lead_videos.add(lead_vid)
        log(f"  -> Lead Video Assigned: [{lead_vid}]")
        
        generate_and_apply_cover(pl_id, title, lead_vid, access_token)
        processed_count += 1
        
    log(f"\n🎉 ALL {processed_count} PLAYLIST THUMBNAILS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    process_all_playlists()
