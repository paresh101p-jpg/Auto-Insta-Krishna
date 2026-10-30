import os
import sys
import json
import base64
import subprocess
import glob
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"E:\Paresh\Auto Post\Auto-Insta-Krishna"
token_file = os.path.join(BASE_DIR, "youtube_token.json")
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ffmpeg_path = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"

with open(token_file, "r", encoding="utf-8") as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

youtube = build("youtube", "v3", credentials=creds)

videos_to_fix = [
    {
        "id": "PZes6Z-cU8s",
        "badge": "YAMUNA GHAT BANSURI",
        "hindi_main": "यमुना तट शास्त्रीय प्रवाह",
        "hindi_sub": "लहरों के साथ गूंजती मधुर मुरली",
        "pills": ["यमुना तट", "शास्त्रीय प्रवाह", "पावन लहरें"]
    },
    {
        "id": "CJF8tZpJI8Y",
        "badge": "SUNRISE DIVINE FLUTE",
        "hindi_main": "सूर्योदय पावन मुरली एवं तबला",
        "hindi_sub": "प्रभात की पावन बेला में आत्मिक शांति",
        "pills": ["सूर्योदय बांसुरी", "पावन मुरली", "सुबह की पूजा"]
    },
    {
        "id": "sUctWLbOpmY",
        "badge": "CALM SLEEP BANSURI",
        "hindi_main": "सोने से पहले मन को हल्का करें",
        "hindi_sub": "गहरी नींद और मानसिक शांति के लिए",
        "pills": ["गहरी नींद", "तनाव मुक्ति", "शांत मन"]
    },
    {
        "id": "i97gU7o9kmI",
        "badge": "CALM SLEEP BANSURI",
        "hindi_main": "सोने से पहले मन को हल्का करें",
        "hindi_sub": "गहरी नींद और मानसिक शांति के लिए",
        "pills": ["गहरी नींद", "तनाव मुक्ति", "शांत मन"]
    },
    {
        "id": "RZ5C8A2KHlw",
        "badge": "INSOMNIA RELIEF BANSURI",
        "hindi_main": "अनिद्रा और बेचैनी से तुरंत राहत",
        "hindi_sub": "मन को शांत करने वाला रात्रि संगीत",
        "pills": ["अनिद्रा से मुक्ति", "रात्रि संगीत", "शांत विश्राम"]
    },
    {
        "id": "FekKTdgJaPo",
        "badge": "PEACEFUL NIGHT SLEEP",
        "hindi_main": "शांत निद्रा अमृत वर्षा बाँसुरी",
        "hindi_sub": "थकान मिटाकर गहरी नींद देने वाला संगीत",
        "pills": ["अमृत वर्षा", "थकान मुक्ति", "सुखद निद्रा"]
    },
    {
        "id": "InfDz_ftdGE",
        "badge": "MORNING PUJA FLUTE",
        "hindi_main": "गोकुल की प्रातःकालीन बाँसुरी",
        "hindi_sub": "मंदिर और दैनिक पूजा के लिए पावन संगीत",
        "pills": ["दैनिक पूजा", "प्रातःकालीन धुन", "भक्ति रस"]
    },
    {
        "id": "LGy7TAIeYQ8",
        "badge": "MORNING PUJA FLUTE",
        "hindi_main": "गोकुल की प्रातःकालीन बाँसुरी",
        "hindi_sub": "मंदिर और दैनिक पूजा के लिए पावन संगीत",
        "pills": ["दैनिक पूजा", "प्रातःकालीन धुन", "भक्ति रस"]
    }
]

slides = glob.glob(os.path.join(BASE_DIR, "music_video_images", "*.jpg"))

for idx, item in enumerate(videos_to_fix, 1):
    vid = item["id"]
    print(f"[{idx}/{len(videos_to_fix)}] Fixing video: {vid} ({item['hindi_main']})...")
    bg_slide = slides[abs(hash(vid)) % len(slides)]
    with open(bg_slide, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    pills_html = "".join([f'<div class="pill">{p}</div>' for p in item["pills"]])
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Hindi:ital@0;1&family=Cinzel:wght@700;900&family=Montserrat:wght@800;900&family=Poppins:wght@700;800;900&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1920px;
    height: 1080px;
    position: relative;
    overflow: hidden;
    background-color: #000;
    font-family: 'Poppins', 'Tiro Devanagari Hindi', 'Nirmala UI', sans-serif;
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
    background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.1) 35%, rgba(0,0,0,0.7) 65%, rgba(0,0,0,0.95) 100%),
                linear-gradient(90deg, rgba(0,0,0,0.88) 0%, rgba(0,0,0,0.5) 50%, rgba(0,0,0,0) 80%);
  }}
  .badge {{
    position: absolute;
    top: 50px;
    left: 80px;
    background: linear-gradient(135deg, #FFB300 0%, #FF8F00 100%);
    border: 3px solid #FFF8E1;
    border-radius: 12px;
    padding: 14px 34px;
    color: #1A0D00;
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 2px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.7);
  }}
  .content-box {{
    position: absolute;
    bottom: 70px;
    left: 80px;
    max-width: 1350px;
    z-index: 10;
  }}
  .main-title {{
    font-size: 114px;
    font-weight: 900;
    line-height: 1.15;
    color: #FFE600;
    text-shadow: 0 6px 0 #000, 0 12px 35px rgba(0,0,0,0.95), 0 0 50px rgba(255, 230, 0, 0.4);
    letter-spacing: 1px;
    margin-bottom: 12px;
  }}
  .sub-title {{
    font-size: 64px;
    font-weight: 700;
    line-height: 1.25;
    color: #FFFFFF;
    text-shadow: 0 4px 0 #000, 0 8px 25px rgba(0,0,0,0.95);
    margin-bottom: 30px;
  }}
  .pills-container {{
    display: flex;
    gap: 20px;
  }}
  .pill {{
    background: rgba(20, 20, 20, 0.88);
    border: 3px solid #FFD54F;
    border-radius: 50px;
    padding: 12px 34px;
    font-size: 38px;
    font-weight: 700;
    color: #FFF9C4;
    text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    box-shadow: 0 6px 20px rgba(0,0,0,0.6);
  }}
  .brand {{
    position: absolute;
    bottom: 50px;
    right: 80px;
    font-family: 'Cinzel', serif;
    font-size: 38px;
    font-weight: 900;
    color: #FFD700;
    letter-spacing: 4px;
    text-shadow: 0 3px 10px rgba(0,0,0,0.9);
  }}
</style>
</head>
<body>
  <div class="bg"></div>
  <div class="vignette"></div>
  <div class="badge">{item['badge']}</div>
  <div class="content-box">
    <div class="main-title">{item['hindi_main']}</div>
    <div class="sub-title">{item['hindi_sub']}</div>
    <div class="pills-container">
      {pills_html}
    </div>
  </div>
  <div class="brand">KRISHNA VIBEZ</div>
</body>
</html>"""

    temp_h = os.path.join(BASE_DIR, f"temp_{vid}.html")
    temp_png = os.path.join(BASE_DIR, f"temp_{vid}.png")
    temp_jpg = os.path.join(BASE_DIR, f"temp_{vid}.jpg")
    
    with open(temp_h, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    file_uri = "file:///" + os.path.abspath(temp_h).replace("\\", "/")
    cmd = [
        edge_path,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1920,1080",
        f"--screenshot={temp_png}",
        file_uri
    ]
    subprocess.run(cmd, check=True)
    
    subprocess.run([
        ffmpeg_path, "-y",
        "-i", temp_png,
        "-vf", "scale=1280:720",
        "-q:v", "2",
        temp_jpg
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    media = MediaFileUpload(temp_jpg, mimetype="image/jpeg", resumable=False)
    req = youtube.thumbnails().set(videoId=vid, media_body=media)
    resp = req.execute()
    print(f"  -> SUCCESS! Updated video {vid}")
    
    for p in [temp_h, temp_png, temp_jpg]:
        if os.path.exists(p):
            try: os.remove(p)
            except Exception: pass

print("\n🎉 ALL REMAINING MUSIC VIDEO THUMBNAILS UPDATED SUCCESSFULLY!")
