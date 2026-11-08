# -*- coding: utf-8 -*-
"""
Multi-Platform Kinetic Reels Syndicator for Krishna Vibez
=========================================================
Automatically syndicates the freshly generated 1080x1920 Kinetic Short to:
1. Website (krishnavibez.in) -> updates website/posts-data.js
2. Instagram Reels -> Meta Graph API Direct Resumable Upload
3. Facebook Video / Reels -> Meta Graph API
4. Telegram Channel -> Clean short thought caption + 4 buttons (Website, YouTube, WhatsApp, Share)
5. Meta Threads -> Video / Thought via official Threads API
6. Pinterest -> Pin with direct destination link to website
"""

import os
import sys
import time
import json
import requests
import subprocess
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def upload_to_catbox(file_path):
    """Uploads media to Catbox to obtain a fast, public HTTPS URL for website & social syndication."""
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "rb") as f:
            res = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": f},
                timeout=35
            )
        if res.status_code == 200 and res.text.strip().startswith("http"):
            return res.text.strip()
    except Exception as e:
        print(f"[Syndicator] Catbox upload note: {e}")
    return None

def post_ig_reel(ig_account_id, caption, local_video_path, fb_token, fallback_video_url=None):
    """Uploads video to Instagram as a 9:16 Reel using Meta Direct Resumable Upload."""
    try:
        media_endpoint = f"https://graph.facebook.com/v20.0/{ig_account_id}/media"
        file_size = os.path.getsize(local_video_path)
        print(f"[Instagram Reel] Initializing resumable upload ({file_size / (1024*1024):.2f} MB)...")

        init_payload = {
            "upload_type": "resumable",
            "media_type": "REELS",
            "caption": caption,
            "access_token": fb_token
        }
        init_res = requests.post(media_endpoint, data=init_payload, timeout=20).json()

        if "id" in init_res and "uri" in init_res:
            container_id = init_res["id"]
            upload_uri = init_res["uri"]

            with open(local_video_path, "rb") as vf:
                video_bytes = vf.read()

            upload_headers = {
                "Authorization": f"OAuth {fb_token}",
                "offset": "0",
                "file_size": str(file_size)
            }
            up_res = requests.post(upload_uri, data=video_bytes, headers=upload_headers, timeout=90)
            print(f"[Instagram Reel] Binary stream uploaded (HTTP {up_res.status_code}). Waiting for Meta transcoding...")

            status = "IN_PROGRESS"
            wait_count = 0
            while status != "FINISHED" and wait_count < 25:
                time.sleep(5)
                wait_count += 1
                status_res = requests.get(
                    f"https://graph.facebook.com/v20.0/{container_id}?fields=status_code&access_token={fb_token}",
                    timeout=15
                ).json()
                status = status_res.get("status_code", "ERROR")
                if status == "FINISHED":
                    break
                if status in ["ERROR", "EXPIRED"]:
                    print(f"[Instagram Reel] Processing error: {status_res}")
                    break

            if status == "FINISHED":
                publish_url = f"https://graph.facebook.com/v20.0/{ig_account_id}/media_publish"
                pub_res = requests.post(
                    publish_url,
                    data={"creation_id": container_id, "access_token": fb_token},
                    timeout=30
                ).json()
                if "id" in pub_res:
                    print(f"[Instagram Reel] ✅ Published Successfully! (ID: {pub_res['id']})")
                    return True
                else:
                    print(f"[Instagram Reel] Publish response: {pub_res}")

        # Fallback to URL method
        if fallback_video_url:
            print("[Instagram Reel] Attempting URL container fallback...")
            res = requests.post(media_endpoint, data={
                "video_url": fallback_video_url,
                "media_type": "REELS",
                "caption": caption,
                "access_token": fb_token
            }, timeout=25).json()
            if "id" in res:
                cid = res["id"]
                for _ in range(20):
                    time.sleep(5)
                    st = requests.get(f"https://graph.facebook.com/v20.0/{cid}?fields=status_code&access_token={fb_token}").json()
                    if st.get("status_code") == "FINISHED":
                        requests.post(f"https://graph.facebook.com/v20.0/{ig_account_id}/media_publish", data={"creation_id": cid, "access_token": fb_token})
                        print(f"[Instagram Reel] ✅ Published via URL fallback! (ID: {cid})")
                        return True
    except Exception as e:
        print(f"[Instagram Reel] ⚠️ Notice: {e}")
    return False

def post_fb_video(fb_page_id, caption, local_video_path, fb_token):
    """Uploads video to Facebook Page as a Reel / Video."""
    try:
        url = f"https://graph.facebook.com/v20.0/{fb_page_id}/videos"
        with open(local_video_path, "rb") as vf:
            payload = {"description": caption, "access_token": fb_token}
            files = {"source": vf}
            res = requests.post(url, data=payload, files=files, timeout=75).json()
            if "id" in res:
                print(f"[Facebook Video] ✅ Published Successfully! (ID: {res['id']})")
                return True
            else:
                print(f"[Facebook Video] Response: {res}")
    except Exception as e:
        print(f"[Facebook Video] ⚠️ Notice: {e}")
    return False

def syndicate_kinetic_reel(video_path, spoken_thought, title, youtube_video_id, image_path=None):
    """
    Syndicates the newly generated kinetic short across Website, Telegram, Instagram, FB, Threads & Pinterest.
    """
    print("\n" + "=" * 65)
    print("🚀 [Multi-Platform Syndicator] Starting Broadcast of Kinetic Reel...")
    print(f"📖 Thought: \"{spoken_thought}\"")
    print(f"▶️ YouTube Short: https://youtube.com/shorts/{youtube_video_id}")
    print("=" * 65)

    yt_short_url = f"https://youtube.com/shorts/{youtube_video_id}"
    results = {}

    # 1. Upload to Catbox for high-speed CDN public URLs
    public_video_url = upload_to_catbox(video_path) or yt_short_url
    public_img_url = upload_to_catbox(image_path) if image_path and os.path.exists(image_path) else f"https://img.youtube.com/vi/{youtube_video_id}/maxresdefault.jpg"
    print(f"[Syndicator] Public Video CDN URL: {public_video_url}")

    # 2. Publish to Website (krishnavibez.in)
    post_url = "https://krishnavibez.in/"
    try:
        import website_publisher
        caption_for_web = f"{spoken_thought}\n\n#Krishna #RadheKrishna #DailySuvichar #KrishnaVibez"
        web_ok, post_id = website_publisher.publish_to_website(
            media_url=public_video_url,
            caption=caption_for_web,
            is_video=True
        )
        if post_id:
            post_url = f"https://krishnavibez.in/post.html?id={post_id}"
            print(f"[Website] ✅ Published to Website: {post_url}")
            results["website"] = True
    except Exception as e:
        print(f"[Website] ⚠️ Notice: {e}")

    # 3. Publish to Telegram Channel (Clean Short Thought + 4 Buttons: Website, YouTube, WhatsApp, Share)
    try:
        from social_publisher import publish_to_telegram
        tg_ok = publish_to_telegram(
            media_url=video_path,
            caption=spoken_thought,
            post_url=post_url,
            is_video=True,
            youtube_url=yt_short_url
        )
        results["telegram"] = tg_ok
    except Exception as e:
        print(f"[Telegram] ⚠️ Notice: {e}")

    # 4. Meta Credentials for Instagram & Facebook
    fb_page_id = os.environ.get("FB_PAGE_ID") or "1808917602588221"
    fb_token = os.environ.get("FB_ACCESS_TOKEN")

    if fb_token:
        # A. Instagram Reel
        try:
            ig_url = f"https://graph.facebook.com/v20.0/{fb_page_id}?fields=instagram_business_account&access_token={fb_token}"
            ig_res = requests.get(ig_url, timeout=15).json()
            ig_acc_id = ig_res.get("instagram_business_account", {}).get("id")

            if ig_acc_id:
                ig_caption = (
                    f"✨ श्री कृष्ण अमृत वचन ✨\n\n"
                    f"\"{spoken_thought}\"\n\n"
                    f"🌸 4K दर्शन व संपूर्ण विचार पढ़ने के लिए Bio में दी गई लिंक पर क्लिक करें!\n"
                    f"🙏 जय श्री राधे कृष्ण! अधिक पावन विचारों के लिए पेज को फॉलो करें।\n\n"
                    f"#Krishna #RadheKrishna #KrishnaVibez #DailySuvichar #BhagavadGita #Reels #Devotional"
                )
                results["instagram"] = post_ig_reel(ig_acc_id, ig_caption, video_path, fb_token, public_video_url)
            else:
                print("[Instagram Reel] Notice: No instagram_business_account linked to page.")
        except Exception as e:
            print(f"[Instagram Reel] ⚠️ Notice: {e}")

        # B. Facebook Video / Reel
        try:
            fb_caption = (
                f"✨ श्री कृष्ण अमृत वचन ✨\n\n"
                f"\"{spoken_thought}\"\n\n"
                f"📖 4K HD दर्शन एवं वॉलपेपर फ्री डाउनलोड करें:\n👉 {post_url}\n\n"
                f"🙏 जय श्री राधे कृष्ण! अधिक पावन विचारों के लिए पेज को फॉलो करें।\n\n"
                f"#Krishna #RadheKrishna #KrishnaVibez #DailySuvichar #BhagavadGita"
            )
            results["facebook"] = post_fb_video(fb_page_id, fb_caption, video_path, fb_token)
        except Exception as e:
            print(f"[Facebook Video] ⚠️ Notice: {e}")

    # 5. Meta Threads
    try:
        from social_publisher import publish_to_threads
        results["threads"] = publish_to_threads(
            media_url=public_video_url,
            caption=spoken_thought,
            post_url=post_url,
            is_video=True
        )
    except Exception as e:
        print(f"[Threads] ⚠️ Notice: {e}")

    # 6. Pinterest
    try:
        from social_publisher import publish_to_pinterest
        results["pinterest"] = publish_to_pinterest(
            media_url=public_img_url,
            title=f"श्री कृष्ण अमृत वचन: {spoken_thought[:60]}",
            description=spoken_thought,
            post_url=post_url,
            is_video=False
        )
    except Exception as e:
        print(f"[Pinterest] ⚠️ Notice: {e}")

    print("=" * 65)
    print(f"🎉 [Multi-Platform Syndicator] Completed Broadcast: {results}")
    print("=" * 65 + "\n")
    return results

