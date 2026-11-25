#!/usr/bin/env python3
import os
import re
import json
import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build

try:
    from youtube_auth_manager import get_authenticated_service
except ImportError:
    def get_authenticated_service():
        from google.oauth2.credentials import Credentials
        client_id = os.environ.get("YOUTUBE_CLIENT_ID")
        client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
        refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
        if client_id and client_secret and refresh_token:
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=["https://www.googleapis.com/auth/youtube"]
            )
            return build("youtube", "v3", credentials=creds)
        return None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Configuration
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "UC_x5XG1OV2P6uZZ5FSM9Ttw")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Initialize Gemini models cascade
MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"GenAI configure error: {e}")

def get_channel_videos(youtube, max_results=50):
    """Fetch latest videos from channel uploads playlist."""
    uploads_playlist_id = None
    if CHANNEL_ID:
        try:
            res = youtube.channels().list(part="contentDetails", id=CHANNEL_ID).execute()
            if res.get("items"):
                uploads_playlist_id = res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except Exception as e:
            print(f"Error fetching channel by ID {CHANNEL_ID}: {e}")

    if not uploads_playlist_id:
        try:
            res = youtube.channels().list(part="contentDetails", mine=True).execute()
            if res.get("items"):
                uploads_playlist_id = res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except Exception as e:
            print(f"Error fetching channel by mine=True: {e}")

    if not uploads_playlist_id:
        print("Could not locate channel uploads playlist.")
        return []
    
    videos = []
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=uploads_playlist_id,
        maxResults=max_results
    )
    while request:
        response = request.execute()
        for item in response.get("items", []):
            videos.append({
                "id": item["contentDetails"]["videoId"],
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"]
            })
        request = youtube.playlistItems().list_next(request, response)
        if len(videos) >= max_results:
            break
    return videos

def get_video_stats(youtube, video_ids):
    """Fetch statistics for videos."""
    stats = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        res = youtube.videos().list(
            part="statistics,snippet",
            id=",".join(batch)
        ).execute()
        for item in res.get("items", []):
            stats[item["id"]] = {
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "title": item["snippet"]["title"],
                "description": item["snippet"].get("description", ""),
                "tags": item["snippet"].get("tags", [])
            }
    return stats

def sanitize_seo_title(title):
    """Zero frequency numbers rule compliance (no 432Hz, 528Hz, Solfeggio, or Hz)."""
    if not title:
        return title
    # Remove 432Hz, 528Hz, Solfeggio, Hz
    cleaned = re.sub(r'\b(432|528)\s*hz\b', '', title, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b(solfeggio|frequency)\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip()
    return cleaned

def suggest_new_seo(old_title, old_description, views):
    """Gemini se SEO title suggestion lein (sirf title, description URLs nahi chhuhenge)."""
    if not GEMINI_API_KEY:
        if "Krishna" not in old_title and "krishna" not in old_title.lower():
            return sanitize_seo_title(f"Lord Krishna | {old_title} | Krishna Vibez")
        return sanitize_seo_title(old_title)

    prompt = f"""
    You are a YouTube SEO expert for 'Krishna Vibez' devotional channel.
    Current Title: {old_title}
    Views: {views}
    
    Suggest ONE high-CTR, SEO-optimized title (max 90 characters).
    Add keywords like: Krishna Bhajan, Radha Krishna, Meditation, Peace, Bhakti, Devotional, Bansuri.
    IMPORTANT RULES:
    1. NEVER mention frequency numbers (NO 432Hz, 528Hz, Solfeggio, or Hz).
    2. Maintain divine Krishna and spiritual devotional essence.
    
    Return ONLY valid JSON: {{"new_title": "..."}}
    """
    for model_name in MODELS:
        try:
            m = genai.GenerativeModel(model_name)
            response = m.generate_content(prompt)
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            data = json.loads(text)
            new_title = data.get("new_title", old_title)
            return sanitize_seo_title(new_title)
        except Exception as e:
            print(f"Gemini {model_name} error: {e}")
            continue

    return sanitize_seo_title(old_title)

def main():
    print(f"--- Starting Daily SEO Optimization at {datetime.now()} ---")
    youtube = get_authenticated_service()
    if not youtube:
        print("Auth failed.")
        return

    videos = get_channel_videos(youtube)
    if not videos:
        print("No videos found.")
        return

    video_ids = [v["id"] for v in videos]
    stats = get_video_stats(youtube, video_ids)
    
    all_views = [s["views"] for s in stats.values()]
    avg_views = sum(all_views) / len(all_views) if all_views else 0
    print(f"Average Views: {avg_views:.0f}")

    updated_count = 0
    max_updates = 3

    for vid, data in stats.items():
        if updated_count >= max_updates:
            break
        
        v_info = next(v for v in videos if v["id"] == vid)
        pub_date = datetime.strptime(v_info["published_at"], "%Y-%m-%dT%H:%M:%SZ")
        if (datetime.utcnow() - pub_date).days < 3:
            continue

        # Sirf kam views wale videos ko update karein (Average se 60% kam)
        if data["views"] < avg_views * 0.4:
            print(f"Optimizing: {data['title']} (Views: {data['views']})")
            new_title = suggest_new_seo(data["title"], data["description"], data["views"])
            
            if new_title != data["title"]:
                try:
                    # SIRF TITLE change karein, description ya URLs nahi chhuhenge
                    youtube.videos().update(
                        part="snippet",
                        body={
                            "id": vid,
                            "snippet": {
                                "title": new_title,
                                "description": data["description"],  # Original description (links intact)
                                "categoryId": "10",
                                "tags": data.get("tags", [])
                            }
                        }
                    ).execute()
                    print(f"✅ Title Updated: {new_title}")
                    updated_count += 1
                except Exception as e:
                    print(f"Update failed for {vid}: {e}")

    print(f"Optimization complete. Total updated: {updated_count}")

if __name__ == "__main__":
    main()
