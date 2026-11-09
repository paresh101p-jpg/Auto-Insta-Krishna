import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

pipeline_path = r"E:\Paresh\Auto Post\Auto-Insta-Krishna\auto_music_video_pipeline.py"
with open(pipeline_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Helper function to auto-manage and add videos to category playlists
playlist_helper_code = '''
def add_video_to_category_playlist(video_id, category_name, access_token):
    """
    100% Legal & Official YouTube Data API v3 Playlist Automation.
    Finds or creates a dedicated category playlist and adds the newly uploaded video into it.
    """
    if not video_id or not access_token:
        return

    # Map category keyword to clean, beautiful high-CTR YouTube Playlist Titles
    playlist_titles = {
        "temple": "🏛️ Ancient Temple Bells & Sacred Chants | Peaceful Dhyan",
        "bell": "🔔 Auspicious Temple Bells & Flute Meditation",
        "rain": "🌧️ Monsoon Rain & Peaceful Flute Meditation",
        "monsoon": "🌧️ Sawan Monsoon Rain & Serene Nature Flute",
        "yamuna": "🌊 Sacred Yamuna River & Ghats Meditation Flute",
        "river": "🌊 Flowing Mountain River & Nature Flute Meditation",
        "sleep": "🌙 Deep Meditative Sleep Music | Pure Night Peace",
        "night": "✨ Starlight & Moonlight Deep Sleep Meditation",
        "sunrise": "🌅 Golden Sunrise & Morning Meditation Flute",
        "morning": "☀️ Peaceful Morning Flute & Birds Meditation",
        "sunset": "🌇 Sandhya Twilight & Dusk Meditation Dhun",
        "cows": "🐮 Surabhi Cows & Peaceful Vrindavan Meadows",
        "peacock": "🦚 Divine Peacock Van & Kadamba Forest Flute",
        "lotus": "🪷 Sacred Lotus Pond & Water Lily Ambient Meditation",
        "kadamba": "🌳 Kadamba Tree Grove & Forest Ambient Flute",
        "banyan": "🌿 Ancient Banyan Tree & Deep Dhyan Meditation",
        "stepwell": "🏰 Ancient Stepwell & Serene Water Reflection",
        "mountain": "🏔️ Himalayan Mist & Mountain Pine Forest Flute",
        "tanpura": "🪕 Classical Tanpura & Bansuri Jugalbandi Meditation",
        "bamboo": "🎋 Swaying Bamboo Forest & Pure Wind Flute",
        "fireflies": "✨ Glowing Fireflies & Serene Night Meditation",
        "cosmic": "🌌 Cosmic Tanpura & Deep Sound Meditation",
        "aarti": "🪔 Divine Temple Aarti & Ghee Diya Meditation",
        "garland": "🌺 Garlands & Fresh Flower Offering Ambient Flute",
        "flower": "🌸 Fresh Vrindavan Blossoms & Flute Meditation",
        "krishna": "🦚 Lord Krishna Divine Bansuri & Vrindavan Flute",
        "darbari": "👑 Raga Darbari Deep Meditation Flute",
        "bhairavi": "🌅 Raga Bhairavi Morning Awakening Flute"
    }

    target_title = None
    cat_lower = (category_name or "").lower()
    for k, title in playlist_titles.items():
        if k in cat_lower:
            target_title = title
            break
            
    if not target_title:
        target_title = "🕉️ Divine Flute & Pure Meditation Music | Krishna Vibez"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        # 1. Search existing playlists on channel to find match
        playlist_id = None
        list_url = "https://www.googleapis.com/youtube/v3/playlists?part=snippet&mine=true&maxResults=50"
        resp = requests.get(list_url, headers=headers)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            for it in items:
                p_title = it.get("snippet", {}).get("title", "")
                if p_title.lower() == target_title.lower():
                    playlist_id = it.get("id")
                    break

        # 2. If playlist doesn't exist, create it legally via official API
        if not playlist_id:
            print(f"  -> 📂 Creating new dedicated Category Playlist: '{target_title}'...")
            create_url = "https://www.googleapis.com/youtube/v3/playlists?part=snippet,status"
            create_payload = {
                "snippet": {
                    "title": target_title,
                    "description": f"Listen to continuous {target_title} for deep relaxation, inner peace, meditation, study, and restful sleep. Official Krishna Vibez collection."
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
            c_resp = requests.post(create_url, headers=headers, json=create_payload)
            if c_resp.status_code in [200, 201]:
                playlist_id = c_resp.json().get("id")
                print(f"  -> ✅ Playlist created successfully (ID: {playlist_id})")
            else:
                print(f"  Notice creating playlist: {c_resp.status_code} - {c_resp.text}")

        # 3. Add the video to the playlist via official playlistItems.insert
        if playlist_id:
            item_url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet"
            item_payload = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
            i_resp = requests.post(item_url, headers=headers, json=item_payload)
            if i_resp.status_code in [200, 201]:
                print(f"  -> 🎯 SUCCESS! Video automatically added to Playlist: '{target_title}'")
            else:
                print(f"  Notice adding to playlist: {i_resp.status_code} - {i_resp.text}")

    except Exception as pl_err:
        print(f"  Notice in playlist auto-organizer: {pl_err}")
'''

# Check where to insert helper code
if "def add_video_to_category_playlist" not in content:
    # Insert before upload_to_youtube
    content = content.replace("def upload_to_youtube(", playlist_helper_code + "\ndef upload_to_youtube(")
    print("✅ Inserted add_video_to_category_playlist helper function!")

# Call this helper right after video upload and quarantine shield
old_trigger = '''        # Upload Custom Thumbnail
        if os.path.exists(TEMP_THUMBNAIL):'''

new_trigger = '''        # 🎯 Official Auto-Playlist Categorization:
        try:
            cat_target = theme.get("category", "") or track_name
            add_video_to_category_playlist(video_id, cat_target, access_token)
        except Exception as p_e:
            print(f"Playlist auto-organizer notice: {p_e}")

        # Upload Custom Thumbnail
        if os.path.exists(TEMP_THUMBNAIL):'''

if old_trigger in content and "add_video_to_category_playlist(video_id" not in content:
    content = content.replace(old_trigger, new_trigger)
    print("✅ Successfully hooked Auto-Playlist Categorization into upload_to_youtube workflow!")
else:
    print("Notice on trigger hook insertion.")

with open(pipeline_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("💾 Saved auto_music_video_pipeline.py with official Auto-Playlist integration!")
