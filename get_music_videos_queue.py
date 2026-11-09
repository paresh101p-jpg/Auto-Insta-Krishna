import sys, requests, json
sys.path.insert(0, 'Auto-Insta-Krishna')
from auto_apply_master_playlist_thumbnails import get_oauth_token

token = get_oauth_token()
headers = {'Authorization': f'Bearer {token}'}

resp = requests.get('https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true', headers=headers).json()
uploads_id = resp['items'][0]['contentDetails']['relatedPlaylists']['uploads']
print('Uploads Playlist ID:', uploads_id)

videos = []
next_token = None
while True:
    url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&playlistId={uploads_id}&maxResults=50'
    if next_token:
        url += f'&pageToken={next_token}'
    res = requests.get(url, headers=headers).json()
    for item in res.get('items', []):
        vid = item['contentDetails']['videoId']
        title = item['snippet']['title']
        published = item['snippet']['publishedAt']
        videos.append({'id': vid, 'title': title, 'published': published})
    next_token = res.get('nextPageToken')
    if not next_token:
        break

print(f'Total channel videos: {len(videos)}')

long_videos = []
for i in range(0, len(videos), 50):
    batch = videos[i:i+50]
    ids = ','.join(v['id'] for v in batch)
    v_res = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part=contentDetails,snippet&id={ids}', headers=headers).json()
    for v_item in v_res.get('items', []):
        dur = v_item['contentDetails']['duration']
        v_title = v_item['snippet']['title']
        is_long = ('M' in dur or 'H' in dur) and '#Shorts' not in v_title
        if is_long:
            long_videos.append({
                'id': v_item['id'],
                'title': v_title,
                'published': v_item['snippet']['publishedAt'],
                'duration': dur
            })

long_videos_sorted = sorted(long_videos, key=lambda x: x['published'])
print(f'Total Long-Form Music Videos: {len(long_videos_sorted)}')

with open('Auto-Insta-Krishna/channel_music_videos_oldest_first.json', 'w', encoding='utf-8') as f:
    json.dump(long_videos_sorted, f, indent=2, ensure_ascii=False)

for idx, v in enumerate(long_videos_sorted):
    print(f"{idx+1}. [{v['published']}] {v['id']} | {v['title'][:60]} ({v['duration']})")

