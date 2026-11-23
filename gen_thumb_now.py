import subprocess, os, glob

BASE_DIR = os.getcwd()
hindi_font = os.path.join(BASE_DIR, "NotoSansDevanagari-Bold.ttf")
english_font = os.path.join(BASE_DIR, "arialbd.ttf")

base_img = "music_video_images/krishna_morning_meditation_flute_real_ai.jpg"
if not os.path.exists(base_img):
    imgs = glob.glob("music_video_images/*.jpg")
    base_img = imgs[0]

out = "suprabhat_thumbnail_final.jpg"

badge = "SHUBH PRABHAT"
hindi_main = "शुभ प्रभात अमृत बाँसुरी"
hindi_sub = "घर में सुख शांति और समृद्धि लाएं"
hook_pill = "सुख समृद्धि | पावन वातावरण | मानसिक शांति"

h_arg = os.path.abspath(hindi_font).replace("\\", "/").replace(":", "\\:")
e_arg = os.path.abspath(english_font).replace("\\", "/").replace(":", "\\:")

vf = (
    f"scale=1920:1080,"
    f"drawbox=y=0:h=180:color=black@0.45:t=fill,"
    f"drawbox=y=500:h=580:color=black@0.84:t=fill,"
    f"drawbox=x=60:y=496:w=1800:h=5:color=goldenrod@0.90:t=fill,"
    f"drawbox=x=70:y=45:w=740:h=90:color=0xFFB300@0.98:t=fill,"
    f"drawbox=x=66:y=41:w=748:h=98:color=white@0.85:t=4,"
    f"drawtext=fontfile='{h_arg}':text='{badge}':fontcolor=black:fontsize=46:x=105:y=68,"
    f"drawtext=fontfile='{h_arg}':text='{hindi_main}':fontcolor=0xFFE600:fontsize=128:x=75:y=550:borderw=10:bordercolor=black,"
    f"drawtext=fontfile='{h_arg}':text='{hindi_sub}':fontcolor=white:fontsize=82:x=75:y=725:borderw=8:bordercolor=black,"
    f"drawbox=x=75:y=850:w=1040:h=82:color=0x8B0000@0.95:t=fill,"
    f"drawbox=x=71:y=846:w=1048:h=90:color=goldenrod@0.85:t=3,"
    f"drawtext=fontfile='{h_arg}':text='{hook_pill}':fontcolor=0xFFF8DC:fontsize=48:x=110:y=868:borderw=3:bordercolor=black,"
    f"drawtext=fontfile='{e_arg}':text='KRISHNA VIBEZ':fontcolor=0xFFD700:fontsize=46:x=1500:y=995:borderw=5:bordercolor=black"
)

cmd = [
    "ffmpeg", "-y",
    "-i", base_img,
    "-vf", vf,
    "-frames:v", "1",
    "-q:v", "2",
    out
]
result = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(out):
    print("SUCCESS:", out, os.path.getsize(out), "bytes")
else:
    print("FAILED")
    print(result.stderr[-1000:])
