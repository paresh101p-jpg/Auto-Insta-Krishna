#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from youtube_auth_manager import get_authenticated_service
import google.generativeai as genai

# Configuration
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "UC_x5XG1OV2P6uZZ5FSM9Ttw")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Initialize Gemini (sirf SEO suggestions ke liye)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
else:
    model = None

def get_channel_videos(youtube, max_results=50):
    """Fetch latest videos from channel uploads playlist."""
    res = youtube.channels().list(part="contentDetails", id=CHANNEL_ID).execute()
    uploads_playlist_id = res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    videos = []
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=uploads_playlist_id,
        maxResults=max_results
    )
    while request:
        response = request.execute()
        for item in response["items"]:
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
        for item in res["items"]:
            stats[item["id"]] = {
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "title": item["snippet"]["title"],
                "description": item["snippet"].get("description", ""),
                "tags": item["snippet"].get("tags", [])
            }
    return stats

def suggest_new_seo(old_title, old_description, views):
    """Gemini se SEO title suggestion lein (sirf title, description URLs nahi chhuhenge)."""
    if not model:
        if "Krishna" not in old_title and "krishna" not in old_title.lower():
            return f"Lord Krishna | {old_title} | Krishna Vibez"
        return old_title

    prompt = f"""
    You are a YouTube SEO expert for 'Krishna Vibez' devotional channel.
    Current Title: {old_title}
    Views: {views}
    
    Suggest ONE high-CTR, SEO-optimized title (max 90 characters).
    Add keywords like: Krishna Bhajan, Radha Krishna, Meditation, Peace, Bhakti, Devotional.
    Return ONLY valid JSON: {{"new_title": "..."}}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        data = json.loads(text)
        return data.get("new_title", old_title)
    except Exception as e:
        print(f"Gemini error: {e}")
        return old_title

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
