#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from youtube_auth_manager import get_authenticated_service
import google.generativeai as genai

# Configuration
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "UC_x5XG1OV2P6uZZ5FSM9Ttw") # Krishna Vibez Default
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
else:
    model = None

def get_channel_videos(youtube, max_results=50):
    """Fetch the latest videos from the channel."""
    # Get the uploads playlist ID
    res = youtube.channels().list(part="contentDetails", id=CHANNEL_ID).execute()
    uploads_playlist_id = res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    # Fetch videos from the playlist
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
    """Fetch statistics for a batch of videos."""
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
    """Use Gemini to suggest better SEO if available."""
    if not model:
        # Fallback basic optimization
        if "Krishna" not in old_title:
            return f"Lord Krishna | {old_title} | Krishna Vibez", old_description
        return old_title, old_description

    prompt = f"""
    Analyze this YouTube video for a Krishna devotional channel called 'Krishna Vibez'.
    Current Title: {old_title}
    Views: {views}
    
    The video is performing low. Suggest a high-CTR, SEO-optimized Title (max 90 chars) 
    and a short enriched Description (first 2 lines only).
    Focus on keywords like: Krishna Bhajan, Radha Krishna, Meditation, Peace, Bhakti.
    Return ONLY a JSON object: {{"new_title": "...", "new_description_snippet": "..."}}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean potential markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        data = json.loads(text)
        return data.get("new_title", old_title), data.get("new_description_snippet", "")
    except Exception as e:
        print(f"Gemini error: {e}")
        return old_title, ""

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
    
    # Calculate average views to find outliers
    all_views = [s["views"] for s in stats.values()]
    avg_views = sum(all_views) / len(all_views) if all_views else 0
    print(f"Average Views: {avg_views}")

    updated_count = 0
    max_updates = 3 # Safety limit: don't change too many at once

    for vid, data in stats.items():
        if updated_count >= max_updates:
            break
        
        # Criteria: Less than 30% of average views AND at least 3 days old
        # (Assuming videos are newest first, we check published_at from 'videos' list)
        v_info = next(v for v in videos if v["id"] == vid)
        pub_date = datetime.strptime(v_info["published_at"], "%Y-%m-%dT%H:%M:%SZ")
        if (datetime.utcnow() - pub_date).days < 3:
            continue

        if data["views"] < avg_views * 0.4:
            print(f"Optimizing low-performer: {data['title']} (Views: {data['views']})")
            new_title, new_desc_snippet = suggest_new_seo(data["title"], data["description"], data["views"])
            
            if new_title != data["title"]:
                try:
                    # Update Title and append snippet to description
                    full_desc = f"{new_desc_snippet}\n\n{data['description']}"[:4500]
                    youtube.videos().update(
                        part="snippet",
                        body={
                            "id": vid,
                            "snippet": {
                                "title": new_title,
                                "description": full_desc,
                                "categoryId": "10" # Music
                            }
                        }
                    ).execute()
                    print(f"✅ Updated: {new_title}")
                    updated_count += 1
                except Exception as e:
                    print(f"Update failed for {vid}: {e}")

    print(f"Optimization complete. Total updated: {updated_count}")

if __name__ == "__main__":
    main()
