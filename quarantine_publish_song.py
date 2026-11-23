import os
import sys
import json
import time
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

client_id = os.environ.get("YOUTUBE_CLIENT_ID")
client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

if not (client_id and client_secret and refresh_token):
    for possible in [
        r'e:\Paresh\Auto Post\Auto-Insta-Krishna\youtube_token.json',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'youtube_token.json'),
        '/home/ubuntu/youtube_token.json'
    ]:
        if os.path.exists(possible):
            try:
                with open(possible, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    client_id = client_id or data.get('client_id')
                    client_secret = client_secret or data.get('client_secret')
                    refresh_token = refresh_token or data.get('refresh_token')
                break
            except Exception:
                pass

if not (client_id and client_secret and refresh_token):
    print("ERROR: Missing YouTube OAuth credentials.")
    sys.exit(1)

info = {
    "client_id": client_id,
    "client_secret": client_secret,
    "refresh_token": refresh_token,
    "token_uri": "https://oauth2.googleapis.com/token"
}
creds = Credentials.from_authorized_user_info(info)
youtube = build('youtube', 'v3', credentials=creds)

print("=" * 60)
print("🔍 SUNDAY SONG VIDEO AUDIT & PUBLISH CHECK (9:00 AM IST)")
print("=" * 60)

try:
    channels_res = youtube.channels().list(mine=True, part='contentDetails').execute()
    uploads_playlist_id = channels_res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    playlist_res = youtube.playlistItems().list(
        playlistId=uploads_playlist_id,
        part='snippet,contentDetails',
        maxResults=10
    ).execute()
    
    video_ids = [item['contentDetails']['videoId'] for item in playlist_res.get('items', [])]
    if not video_ids:
        print("⚠️ कोई वीडियो नहीं मिला।")
        sys.exit(0)

    vid_res = youtube.videos().list(part='snippet,status,contentDetails', id=','.join(video_ids)).execute()
    
    found_unlisted = []
    for v in vid_res.get('items', []):
        vid = v['id']
        status = v.get('status', {})
        if status.get('privacyStatus') == 'unlisted':
            found_unlisted.append(v)

    if not found_unlisted:
        print("✅ कोई अनलिस्टेड वीडियो पेंडिंग नहीं है (शायद पहले से पब्लिक है)।")
        sys.exit(0)

    # सबसे हालिया अनलिस्टेड वीडियो (सुबह 6:00 बजे अपलोड किया गया गाना)
    target = found_unlisted[0]
    vid = target['id']
    title = target['snippet']['title']
    status = target.get('status', {})
    content_details = target.get('contentDetails', {})
    
    upload_status = status.get('uploadStatus')
    rejection = status.get('rejectionReason')
    blocked = content_details.get('regionRestriction', {}).get('blocked', [])
    licensed = content_details.get('licensedContent', False)
    
    print(f"\n📺 जांचा जा रहा वीडियो: {title} (ID: {vid})")

    problem_found = False
    problem_reason = ""
    
    if rejection:
        problem_found = True
        problem_reason = f"Rejection reason: {rejection}"
    elif upload_status in ['rejected', 'failed']:
        problem_found = True
        problem_reason = f"Upload status failed/rejected: {upload_status}"
    elif blocked:
        problem_found = True
        problem_reason = f"Blocked in {len(blocked)} regions: {blocked}"
    elif licensed:
        problem_found = True
        problem_reason = "3rd party Content ID / Copyright claim detected"

    if problem_found:
        print(f"\n🚨 [कॉपीराइट / पॉलिसी स्ट्राइक का खतरा] कारण: {problem_reason}")
        print(f"🗑️ [सुरक्षा नियम] वीडियो को तुरंत YouTube से डिलीट किया जा रहा है...")
        try:
            youtube.videos().delete(id=vid).execute()
            print(f"✅ वीडियो {vid} को सुरक्षा कारणों से YouTube से डिलीट कर दिया गया है!")
        except Exception as e:
            print(f"❌ डिलीट करने में त्रुटि: {e}")
        sys.exit(0)

    if upload_status != 'processed':
        print(f"⚠️ वीडियो अभी भी प्रोसेस हो रहा है (uploadStatus='{upload_status}'). अगले चक्र में चेक होगा।")
        sys.exit(0)

    # सब कुछ 100% सही और क्लीन है -> पब्लिक करें
    print("✨ वीडियो 100% साफ़ है! कोई स्ट्राइक, कॉपीराइट क्लेम या प्रतिबंध नहीं मिला।")
    print("🚀 वीडियो को पब्लिक (Public) किया जा रहा है...")
    snippet = target['snippet']
    snippet['categoryId'] = '10'
    body = {
        'id': vid,
        'snippet': snippet,
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    youtube.videos().update(part='snippet,status', body=body).execute()
    print(f"🎉 बधाई हो! वीडियो सफलतापूर्वक PUBLIC हो गया है!\nURL: https://youtube.com/watch?v={vid}")

except Exception as e:
    print(f"⚠️ ऑडिट निष्पादन सूचना: {e}")
