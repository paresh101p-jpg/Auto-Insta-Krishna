import os
import sys
import base64
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"E:\Paresh\Auto Post\Auto-Insta-Krishna"
bg_img_path = os.path.join(BASE_DIR, "music_video_images", "All catagery Krisha music photo", "Bamboo_bansuri_and_peacock_feather_5e70cb85.jpg")

with open(bg_img_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
bg_data_uri = "data:image/jpeg;base64," + b64

html_code = f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@800;900&family=Noto+Sans+Devanagari:wght@800;900&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    width: 1280px;
    height: 720px;
    overflow: hidden;
    position: relative;
    font-family: 'Noto Sans Devanagari', 'Poppins', sans-serif;
    background-color: #050810;
  }}

  /* Full background image, top 60% completely visible and open */
  .bg {{
    position: absolute;
    top: 0;
    left: 0;
    width: 1280px;
    height: 720px;
    background-image: url('{bg_data_uri}');
    background-size: cover;
    background-position: center 20%;
    filter: contrast(1.1) saturate(1.18) brightness(0.98);
  }}

  /* Smooth dark gradient on bottom half ONLY, leaves top 50% unobstructed */
  .bottom-gradient {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 1280px;
    height: 520px;
    background: linear-gradient(to top, rgba(5, 8, 16, 0.98) 0%, rgba(5, 8, 16, 0.94) 60%, rgba(5, 8, 16, 0.5) 85%, transparent 100%);
  }}

  .content-container {{
    position: absolute;
    top: 0;
    left: 0;
    width: 1280px;
    height: 720px;
    padding: 35px 50px 38px 50px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    z-index: 10;
  }}

  /* Top Bar */
  .top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .badge-category {{
    background: linear-gradient(135deg, #FF6F00, #E65100);
    color: #ffffff;
    font-size: 24px;
    font-weight: 900;
    letter-spacing: 1px;
    padding: 8px 22px;
    border-radius: 10px;
    border: 2px solid #FFE082;
    box-shadow: 0 4px 15px rgba(230, 81, 0, 0.6);
  }}

  .badge-time {{
    background: rgba(10, 20, 35, 0.88);
    border: 2px solid #00E5FF;
    color: #00E5FF;
    font-size: 22px;
    font-weight: 800;
    padding: 8px 20px;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0, 229, 255, 0.35);
  }}

  /* Bottom Content Area shifted nicely UP */
  .bottom-box {{
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-bottom: 75px;
  }}

  /* Huge Main Title: White + Gold */
  .title-main {{
    font-size: 78px;
    font-weight: 900;
    line-height: 1.1;
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
  }}

  .c-white {{
    color: #FFFFFF;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.4), 0 4px 10px #000, 0 8px 25px rgba(0,0,0,0.9);
  }}

  .c-gold {{
    color: #FFD600;
    background: linear-gradient(180deg, #FFF9C4 0%, #FFD600 50%, #FF9100 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.95)) drop-shadow(0 0 25px rgba(255, 145, 0, 0.7));
  }}

  /* Subtitle with Dual-Tone Red Pill & Cyan Text */
  .sub-box {{
    display: flex;
    align-items: center;
    gap: 18px;
  }}

  .pill-red {{
    background: linear-gradient(90deg, #D50000 0%, #C51162 100%);
    color: #FFFFFF;
    font-size: 32px;
    font-weight: 900;
    padding: 6px 22px;
    border-radius: 8px;
    border: 2px solid #FF80AB;
    box-shadow: 0 4px 16px rgba(213, 0, 0, 0.5);
    text-shadow: 0 2px 4px rgba(0,0,0,0.8);
  }}

  .text-cyan {{
    color: #00E5FF;
    font-size: 34px;
    font-weight: 800;
    text-shadow: 0 3px 8px rgba(0,0,0,0.95), 0 0 15px rgba(0, 229, 255, 0.6);
  }}

  /* Footer bar */
  .footer-box {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.18);
  }}

  .tags-list {{
    display: flex;
    gap: 16px;
  }}

  .tag {{
    background: linear-gradient(135deg, rgba(15, 30, 50, 0.95), rgba(8, 16, 28, 0.95));
    color: #FFFFFF;
    font-size: 26px;
    font-weight: 900;
    letter-spacing: 0.5px;
    padding: 10px 24px;
    border-radius: 12px;
    border: 2.5px solid #00E5FF;
    box-shadow: 0 4px 18px rgba(0, 229, 255, 0.4), inset 0 0 10px rgba(0, 229, 255, 0.2);
    text-shadow: 0 2px 4px rgba(0,0,0,0.9);
  }}

  .brand-name {{
    color: #FFB300;
    font-size: 28px;
    font-weight: 900;
    letter-spacing: 2px;
    border: 2px solid #FFB300;
    padding: 8px 20px;
    border-radius: 10px;
    background: rgba(20, 15, 5, 0.85);
    box-shadow: 0 4px 15px rgba(255, 179, 0, 0.35);
    text-shadow: 0 2px 8px rgba(0,0,0,0.9);
  }}
</style>
</head>
<body>
  <div class="bg"></div>
  <div class="bottom-gradient"></div>

  <div class="content-container">
    <div class="top-bar">
      <div class="badge-category">🌿 दिव्य निकुंज बाँसुरी</div>
      <div class="badge-time">⏱️ 15 MIN MEDITATION</div>
    </div>

    <div class="bottom-box">
      <div class="title-main">
        <span class="c-white">प्रातःकालीन</span>
        <span class="c-gold">अमृत बाँसुरी प्रवाह</span>
      </div>

      <div class="sub-box">
        <span class="pill-red">गहरा मानसिक सुकून</span>
        <span class="text-cyan">तनाव मुक्ति एवं एकाग्रता</span>
      </div>

      <div class="footer-box">
        <div class="tags-list">
          <span class="tag">✨ 100% RELAXING</span>
          <span class="tag">🧘 DEEP SLEEP</span>
          <span class="tag">🦚 DIVINE VIBES</span>
        </div>
        <div class="brand-name">KRISHNA VIBEZ</div>
      </div>
    </div>
  </div>
</body>
</html>
"""

temp_html = os.path.join(BASE_DIR, "render_sample_dual.html")
with open(temp_html, "w", encoding="utf-8") as f:
    f.write(html_code)

out_jpg = r"C:\Users\Admin\.gemini\antigravity\brain\5edf39f6-759b-4d35-b525-27352f306f0f\perfect_dual_tone_sample_thumbnail.jpg"

browser = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(browser):
    browser = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

cmd = [
    browser,
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--window-size=1280,720",
    f"--screenshot={out_jpg}",
    os.path.abspath(temp_html)
]
subprocess.run(cmd, check=True)
print("SUCCESS! Created:", out_jpg)

