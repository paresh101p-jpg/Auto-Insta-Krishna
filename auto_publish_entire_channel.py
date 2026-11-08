import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

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
    print("ERROR: Missing YouTube OAuth credentials (env vars or youtube_token.json).")
    sys.exit(1)

info = {
    "client_id": client_id,
    "client_secret": client_secret,
    "refresh_token": refresh_token,
    "token_uri": "https://oauth2.googleapis.com/token"
}
creds = Credentials.from_authorized_user_info(info)
youtube = build('youtube', 'v3', credentials=creds)

print("Fetching uploads playlist...")
channels_res = youtube.channels().list(mine=True, part='contentDetails').execute()
uploads_playlist_id = channels_res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

now = datetime.now(timezone.utc)
page_token = None
all_unlisted = []

print("Scanning channel for Unlisted videos & checking 24h quarantine status...")

while True:
    playlist_res = youtube.playlistItems().list(
        playlistId=uploads_playlist_id,
        part='snippet,contentDetails',
        maxResults=50,
        pageToken=page_token
    ).execute()
    
    video_ids = [item['contentDetails']['videoId'] for item in playlist_res.get('items', [])]
    if not video_ids:
        break
        
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        vid_res = youtube.videos().list(part='snippet,status,contentDetails', id=','.join(chunk)).execute()
        for v in vid_res.get('items', []):
            vid = v['id']
            status = v.get('status', {})
            privacy = status.get('privacyStatus')
            
            if privacy == 'unlisted':
                published_at_str = v['snippet']['publishedAt']
                pub_dt = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                age_hours = (now - pub_dt).total_seconds() / 3600.0
                title = v['snippet']['title'][:50]
                
                # Check for copyright or processing issues
                upload_status = status.get('uploadStatus')
                rejection_reason = status.get('rejectionReason')
                content_details = v.get('contentDetails', {})
                region_restriction = content_details.get('regionRestriction', {})
                blocked_regions = region_restriction.get('blocked', [])
                
                all_unlisted.append({
                    'id': vid,
                    'title': title,
                    'age_hours': age_hours,
                    'snippet': v['snippet'],
                    'status': status,
                    'upload_status': upload_status,
                    'rejection_reason': rejection_reason,
                    'blocked_regions': blocked_regions
                })
                
    page_token = playlist_res.get('nextPageToken')
    if not page_token:
        break

print(f"\nTotal Unlisted videos found: {len(all_unlisted)}")
ready_candidates = [x for x in all_unlisted if x['age_hours'] >= 24.0]
still_in_quarantine = [x for x in all_unlisted if x['age_hours'] < 24.0]

print(f"Candidates >= 24h: {len(ready_candidates)}")
print(f"Still in 24h Quarantine (< 24h): {len(still_in_quarantine)}")

published_count = 0
flagged_count = 0

for item in ready_candidates:
    vid = item['id']
    title = item['title']
    age = item['age_hours']
    upload_status = item['upload_status']
    rejection = item['rejection_reason']
    blocked = item['blocked_regions']
    
    # Pre-flight Safety Verification:
    # 1. Must be fully processed
    # 2. Must not have any rejection reason (copyright, termsOfUse, etc.)
    # 3. Must not have blocked country restrictions
    if rejection:
        print(f"❌ [QUARANTINE BLOCKED] Video {vid} has rejectionReason='{rejection}'! DO NOT PUBLISH. Title: {title}")
        flagged_count += 1
        continue
    
    if upload_status != 'processed':
        print(f"⚠️ [PROCESSING INCOMPLETE] Video {vid} uploadStatus='{upload_status}'. Skipping for now. Title: {title}")
        flagged_count += 1
        continue
        
    if blocked:
        print(f"❌ [QUARANTINE BLOCKED] Video {vid} has blocked regions ({len(blocked)} countries)! DO NOT PUBLISH. Title: {title}")
        flagged_count += 1
        continue
        
    # Safety checks passed 100% -> Publish to Public
    snippet = item['snippet']
    snippet['categoryId'] = '10'  # Music category
    body = {
        'id': vid,
        'snippet': snippet,
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    try:
        youtube.videos().update(part='snippet,status', body=body).execute()
        published_count += 1
        print(f"✅ [PUBLISHED PUBLIC] {vid} | Age: {age:.1f}h | {title}")
    except Exception as e:
        print(f"❌ [ERROR PUBLISHING] {vid}: {e}")

print(f"\nSummary:")
print(f"  Successfully Published: {published_count}")
print(f"  Quarantine Flagged/Skipped: {flagged_count}")
print(f"  Waiting in Quarantine (<24h): {len(still_in_quarantine)}")

if still_in_quarantine:
    print("\n--- Videos Currently in 24h Quarantine Shield ---")
    for item in still_in_quarantine:
        rem = 24.0 - item['age_hours']
        print(f"  ⏳ {item['id']} | Age: {item['age_hours']:.1f}h ({rem:.1f}h remaining) | {item['title']}")
