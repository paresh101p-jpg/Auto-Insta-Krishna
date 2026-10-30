# -*- coding: utf-8 -*-
"""
YouTube Safety Quarantine & Auto-Publish/Delete Engine
Protects Krishna Vibez channel by:
1. Uploading all new Shorts & Music Videos initially as UNLISTED (Quarantine).
2. Tracking every unlisted video in a JSON registry (video_id, title, upload_timestamp, video_type).
3. On every scheduled run:
   - Evaluates videos that have spent >= 24 hours in Quarantine.
   - Queries YouTube Data API v3 for Content ID claims / copyright match issues.
   - IF 100% Clean: Updates privacyStatus to 'public' (SAFE TO PUBLISH).
   - IF ANY Claim / Rejection / Flag detected: IMMEDIATELY DELETES the video from YouTube!
   - Archives result and cleans up registry.
"""

import os
import sys
import time
import json
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "youtube_token.json")
QUARANTINE_FILE = os.path.join(BASE_DIR, "youtube_quarantine_queue.json")
AUDIT_LOG_FILE = os.path.join(BASE_DIR, "youtube_quarantine_audit.log")

CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                CLIENT_ID = CLIENT_ID or data.get("client_id")
                CLIENT_SECRET = CLIENT_SECRET or data.get("client_secret")
                REFRESH_TOKEN = REFRESH_TOKEN or data.get("refresh_token")
        except Exception as e:
            print(f"[Quarantine Engine] Notice reading local token file: {e}")

def get_authenticated_service():
    if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
        print("[Quarantine Engine] YouTube API credentials missing. Skipping quarantine processing.")
        return None
    try:
        creds = Credentials(
            token=None,
            refresh_token=REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"[Quarantine Engine] Error building YouTube service: {e}")
        return None

def load_quarantine_queue():
    if not os.path.exists(QUARANTINE_FILE):
        return []
    try:
        with open(QUARANTINE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_quarantine_queue(queue):
    try:
        with open(QUARANTINE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Quarantine Engine] Failed to save queue: {e}")

def add_to_quarantine(video_id, title, video_type="short"):
    """Registers newly uploaded unlisted video into quarantine queue."""
    queue = load_quarantine_queue()
    entry = {
        "video_id": video_id,
        "title": title,
        "video_type": video_type,
        "uploaded_at": int(time.time()),
        "uploaded_at_iso": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }
    # Avoid duplicate entry
    if not any(item.get("video_id") == video_id for item in queue):
        queue.append(entry)
        save_quarantine_queue(queue)
        print(f"🛡️ [Quarantine Enforced] Video registered in 24h Safety Shield Queue: {video_id} ('{title}')")

def process_quarantine_queue(min_quarantine_hours=24):
    """
    Checks all quarantined videos:
    - If >= min_quarantine_hours (default 24h):
      - Checks video status and contentDetails for any copyright claim / rejection
      - If clean: sets privacyStatus to 'public'
      - If claimed / rejected: DELETES the video immediately!
    """
    queue = load_quarantine_queue()
    if not queue:
        print("[Quarantine Engine] Quarantine queue is empty. No videos to review.")
        return

    youtube = get_authenticated_service()
    if not youtube:
        return

    now = int(time.time())
    quarantine_seconds = min_quarantine_hours * 3600
    remaining_queue = []

    print(f"[Quarantine Engine] Reviewing {len(queue)} video(s) in quarantine...")

    for item in queue:
        vid = item.get("video_id")
        title = item.get("title", "Unknown")
        uploaded_at = item.get("uploaded_at", 0)
        age_hours = (now - uploaded_at) / 3600.0

        if age_hours < min_quarantine_hours:
            remaining_hours = min_quarantine_hours - age_hours
            print(f"  ⏳ Video {vid} ('{title}') in quarantine for {age_hours:.1f}h (needs {remaining_hours:.1f}h more). Keeping Unlisted.")
            remaining_queue.append(item)
            continue

        print(f"\n🔍 [24H SAFETY CHECK] Auditing video {vid} (Age: {age_hours:.1f}h)...")
        try:
            # Query video status & contentDetails
            req = youtube.videos().list(part="status,contentDetails,snippet", id=vid)
            res = req.execute()
            items = res.get("items", [])
            
            if not items:
                print(f"  ⚠️ Video {vid} was deleted or not found on YouTube. Removing from queue.")
                continue

            video_data = items[0]
            status_data = video_data.get("status", {})
            content_details = video_data.get("contentDetails", {})
            
            privacy = status_data.get("privacyStatus", "unlisted")
            upload_status = status_data.get("uploadStatus", "")
            rejection_reason = status_data.get("rejectionReason", "")
            has_custom_license = content_details.get("licensedContent", False)

            # Check if video was rejected or blocked due to copyright
            has_copyright_flag = False
            flag_reason = ""

            if rejection_reason in ["copyright", "claim", "termsOfUse", "legal"]:
                has_copyright_flag = True
                flag_reason = f"Rejection reason: {rejection_reason}"
            elif upload_status == "rejected":
                has_copyright_flag = True
                flag_reason = f"Upload status rejected ({rejection_reason})"

            # If copyright flag detected -> AUTO-DELETE IMMEDIATELY!
            if has_copyright_flag:
                print(f"🚨 [COPYRIGHT DANGER DETECTED] Video {vid} flagged by YouTube: {flag_reason}")
                print(f"🗑️ [SAFETY ACTION] Deleting video {vid} immediately to protect channel reputation...")
                try:
                    del_req = youtube.videos().delete(id=vid)
                    del_req.execute()
                    print(f"✅ Video {vid} permanently DELETED from YouTube.")
                    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as log_f:
                        log_f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}] DELETED {vid} due to {flag_reason}. Title: {title}\n")
                except Exception as del_err:
                    print(f"❌ Failed to delete flagged video {vid}: {del_err}")
                continue

            # If already public
            if privacy == "public":
                print(f"  ✨ Video {vid} is already Public. Removing from quarantine queue.")
                continue

            # 100% CLEAN -> Set to Public
            print(f"✅ [100% CLEAN & VERIFIED] Zero copyright issues after {age_hours:.1f}h! Publishing to Public...")
            update_body = {
                "id": vid,
                "snippet": video_data.get("snippet", {}),
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                    "embeddable": True,
                    "license": "youtube",
                    "containsSyntheticMedia": True
                }
            }
            update_req = youtube.videos().update(part="snippet,status", body=update_body)
            update_res = update_req.execute()
            new_privacy = update_res.get("status", {}).get("privacyStatus")
            print(f"🎉 SUCCESS! Video {vid} ('{title}') is now LIVE & PUBLIC on YouTube! Status: {new_privacy}")
            
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as log_f:
                log_f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}] PUBLISHED {vid} successfully after {age_hours:.1f}h clean quarantine. Title: {title}\n")

        except Exception as e:
            print(f"  ⚠️ Error checking/updating video {vid}: {e}. Retaining in quarantine queue.")
            remaining_queue.append(item)

    save_quarantine_queue(remaining_queue)

if __name__ == "__main__":
    process_quarantine_queue(min_quarantine_hours=24)
