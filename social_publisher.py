# -*- coding: utf-8 -*-
"""
Multi-Channel Social Publisher for Krishna Vibez
Publishes newly created quotes, 4K wallpapers, and reels across multiple free platforms:
1. Telegram Channel (100% Free Telegram Bot API, Instant)
2. Pinterest (Pinterest API v5 and Native RSS Feed Auto-Publish)
3. Meta Threads (Meta Threads Graph API)
4. Reddit (Reddit OAuth API)

Designed for 100% reliability with zero errors:
If any platform credentials are not provided or an individual API fails,
it will log a clean notice and NEVER crash the main publishing flow.
"""

import os
import sys
import json
import time
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def publish_to_telegram(media_url, caption, post_url, is_video=False, youtube_url=None):
    """
    Publishes the image or reel with clean short thought and interactive buttons to Telegram Channel.
    Uses official Telegram Bot API (100% Free, No Token Expiration).
    """
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    admin_chat_id = os.environ.get("TELEGRAM_ADMIN_CHAT_ID")

    token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telegram_token.txt")
    if os.path.exists(token_file):
        try:
            with open(token_file, "r", encoding="utf-8") as tf:
                for line in tf:
                    if not bot_token and line.startswith("TELEGRAM_BOT_TOKEN="):
                        bot_token = line.split("=", 1)[1].strip()
                    elif not chat_id and line.startswith("TELEGRAM_CHAT_ID="):
                        chat_id = line.split("=", 1)[1].strip()
                    elif not admin_chat_id and line.startswith("TELEGRAM_ADMIN_CHAT_ID="):
                        admin_chat_id = line.split("=", 1)[1].strip()
        except Exception:
            pass

    admin_chat_id = admin_chat_id or "753762808"

    if not bot_token or not chat_id:
        print("[Telegram] ℹ️ Skipped: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured.")
        return False

    try:
        # Extract clean thought for clean, uncluttered caption (ZERO URLs in text as requested)
        clean_lines = [l.strip() for l in caption.split("\n") if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("http")]
        quote_text = clean_lines[0] if clean_lines else "तुम्हारा केवल कर्म है, बाक़ी सब मुझ पर छोड़ दो।"
        quote_text = quote_text.replace("- राधे कृष्ण", "").replace("- श्री कृष्ण", "").strip()

        # 🛡️ ANTI-DUPLICATE SAFETY LOCK (Prevents duplicate posts on Telegram)
        lock_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_telegram_post.json")
        now_ts = time.time()
        if os.path.exists(lock_file):
            try:
                with open(lock_file, "r", encoding="utf-8") as lf:
                    lock_data = json.load(lf)
                last_ts = lock_data.get("timestamp", 0)
                last_quote = lock_data.get("quote", "")
                elapsed = now_ts - last_ts

                # If exact same quote was published within 24 hours -> Block duplicate!
                if quote_text == last_quote and elapsed < 86400:
                    print(f"[Telegram] 🛡️ Duplicate Post Blocked: Exact same thought was already published {int(elapsed//60)} minutes ago!")
                    return True

                # If ANY post was published within 25 minutes -> Block simultaneous double runs!
                if elapsed < 1500: # 25 minutes
                    print(f"[Telegram] 🛡️ Double-Post Blocked: A post was already published {int(elapsed//60)} minutes ago (minimum interval is 25 minutes)!")
                    return True
            except Exception as lock_err:
                print(f"[Telegram] Notice (lock check): {lock_err}")

        # Clean short caption: Only thought and 2-4 keywords, strictly ZERO URLs (No forced Krishna header)
        formatted_caption = (
            f"\"{quote_text}\"\n\n"
            f"#सुविचार #प्रेरणा #सकारात्मक_सोच #जीवन"
        )

        import urllib.parse
        target_web_url = post_url or "https://krishnavibez.in/"
        target_yt_url = youtube_url or "https://www.youtube.com/@KrishnaVibezMusic"
        target_wa_url = "https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J"

        share_text = urllib.parse.quote(f"\"{quote_text}\"")
        share_url = f"https://t.me/share/url?url={urllib.parse.quote(target_web_url)}&text={share_text}"

        # Clean 4-button layout: Website, YouTube, WhatsApp, and Share
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "🌐 Visit Website", "url": target_web_url},
                    {"text": "▶️ Watch YouTube", "url": target_yt_url}
                ],
                [
                    {"text": "💬 WhatsApp Channel", "url": target_wa_url},
                    {"text": "↗️ Share Thought", "url": share_url}
                ]
            ]
        }

        endpoint = "sendVideo" if is_video else "sendPhoto"
        param_name = "video" if is_video else "photo"

        payload = {
            "chat_id": chat_id,
            "caption": formatted_caption,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(reply_markup)
        }
        api_url = f"https://api.telegram.org/bot{bot_token}/{endpoint}"

        if os.path.exists(str(media_url)):
            filename = os.path.basename(str(media_url))
            mime = "video/mp4" if is_video else "image/jpeg"
            with open(media_url, "rb") as mf:
                response = requests.post(api_url, data=payload, files={param_name: (filename, mf, mime)}, timeout=75)
                res_data = response.json()
        else:
            payload[param_name] = media_url
            response = requests.post(api_url, data=payload, timeout=30)
            res_data = response.json()

        if res_data.get("ok"):
            message_id = res_data.get("result", {}).get("message_id")
            print(f"[Telegram] ✅ Successfully published to Telegram Channel ({chat_id})! Message ID: {message_id}")

            # Automatically activate reactions on post so live reaction bar is ready
            if message_id:
                try:
                    react_url = f"https://api.telegram.org/bot{bot_token}/setMessageReaction"
                    react_payload = {
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "reaction": json.dumps([{"type": "emoji", "emoji": "🙏"}])
                    }
                    requests.post(react_url, data=react_payload, timeout=10)
                except Exception:
                    pass

            # Record successful post to lock file to permanently prevent double-posts
            try:
                with open(lock_file, "w", encoding="utf-8") as lf:
                    json.dump({"timestamp": now_ts, "quote": quote_text, "message_id": message_id}, lf)
            except Exception:
                pass

            # Also send personal reminder to Paresh bhai (ONLY if admin_chat_id is a private user ID, NEVER if channel)
            admin_str = str(admin_chat_id).strip()
            chat_str = str(chat_id).strip()
            is_channel_target = admin_str.startswith("@") or admin_str.startswith("-100") or admin_str == chat_str
            if admin_chat_id and not is_channel_target:
                try:
                    reflection = caption.strip()
                    whatsapp_channel = "https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J"
                    admin_caption = (
                        f"🔔 <b>परेश भाई, आज का नया पोस्ट तैयार है!</b>\n"
                        f"👉 <i>इस फ़ोटो/रील को अपने WhatsApp Channel और YouTube पर शेयर कर दीजिए:</i>\n\n"
                        f"{formatted_caption}"
                    )
                    admin_reply_markup = {
                        "inline_keyboard": [
                            [
                                {"text": "🟢 WhatsApp चैनल खोलें", "url": whatsapp_channel},
                                {"text": "▶️ YouTube Community खोलें", "url": "https://youtube.com/@krishnavibezofficial/community"}
                            ],
                            [
                                {"text": "🌸 4K दर्शन वेबसाइट पर देखें", "url": post_url}
                            ]
                        ]
                    }
                    admin_payload = {
                        "chat_id": admin_chat_id,
                        "caption": admin_caption[:1024],
                        "parse_mode": "HTML",
                        "reply_markup": json.dumps(admin_reply_markup)
                    }
                    if os.path.exists(str(media_url)):
                        with open(media_url, "rb") as mf:
                            requests.post(api_url, data=admin_payload, files={param_name: (filename, mf, mime)}, timeout=60)
                    else:
                        admin_payload[param_name] = media_url
                        requests.post(api_url, data=admin_payload, timeout=20)

                    # Send 1-tap instant copy message so Paresh bhai never has to manually select text
                    clean_wa_caption = (
                        f"✨ श्री कृष्ण पावन अमृत विचार ✨\n\n"
                        f"\"{quote_text}\"\n\n"
                        f"📖 पावन भावार्थ:\n"
                        f"{reflection[:300]}\n\n"
                        f"🌸 4K दर्शन व डाउनलोड:\n{post_url}\n\n"
                        f"🕊️ Krishna Vibez Official:\n"
                        f"🟢 WhatsApp: {whatsapp_channel}\n"
                        f"▶️ YouTube: https://youtube.com/@krishnavibezofficial\n\n"
                        f"जय श्री राधे कृष्ण! 🙏✨\n\n"
                        f"#Krishna #RadheKrishna #BhagavadGita #KrishnaQuotes"
                    )
                    copy_text_payload = {
                        "chat_id": admin_chat_id,
                        "text": f"📋 <b>नीचे दिए गए बॉक्स पर सिर्फ 1 बार टैप (Click) करें — पूरा Caption तुरंत Copy हो जाएगा:</b>\n\n<code>{clean_wa_caption}</code>",
                        "parse_mode": "HTML"
                    }
                    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data=copy_text_payload, timeout=15)
                    print(f"[Telegram] 🔔 Personal reminder & 1-tap copy box sent to Paresh bhai ({admin_chat_id})!")
                except Exception as admin_err:
                    print(f"[Telegram] Notice (Admin reminder): {admin_err}")

            return True
        else:
            print(f"[Telegram] ⚠️ API response error: {res_data.get('description')}")
            return False

    except Exception as e:
        print(f"[Telegram] ⚠️ Notice (non-fatal error): {e}")
        return False


def publish_to_pinterest(media_url, title, description, post_url, is_video=False):
    """
    Publishes a Pin with direct website destination link to a Pinterest Board.
    Required Secrets:
      - PINTEREST_ACCESS_TOKEN: Pinterest API v5 Bearer Token
      - PINTEREST_BOARD_ID: Target Board ID
    """
    access_token = os.environ.get("PINTEREST_ACCESS_TOKEN")
    board_id = os.environ.get("PINTEREST_BOARD_ID")

    if not access_token or not board_id:
        print("[Pinterest] ℹ️ Skipped direct API: PINTEREST_ACCESS_TOKEN or PINTEREST_BOARD_ID not set. (Note: Pinterest will still auto-publish via RSS Feed https://krishnavibez.in/rss.xml)")
        return False

    try:
        api_url = "https://api.pinterest.com/v5/pins"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        wa_link = "https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J"
        clean_title = (title[:95] + "…") if len(title) > 95 else title
        base_desc = description[:380].strip()
        clean_desc = f"{base_desc}\n\n🟢 WhatsApp Channel: {wa_link}"
        if len(clean_desc) > 495:
            clean_desc = clean_desc[:490] + "…"

        payload = {
            "link": post_url,
            "title": clean_title,
            "description": clean_desc,
            "board_id": board_id,
            "media_source": {
                "source_type": "image_url",
                "url": media_url
            }
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        if response.status_code in [200, 201]:
            print(f"[Pinterest] ✅ Successfully published Pin with direct link to Board ({board_id})!")
            return True
        else:
            print(f"[Pinterest] ⚠️ API response {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"[Pinterest] ⚠️ Notice (non-fatal error): {e}")
        return False


def publish_to_threads(media_url, caption, post_url, is_video=False):
    """
    Publishes post to Meta Threads via the official Meta Threads API.
    Required Secrets:
      - THREADS_ACCESS_TOKEN: Threads user access token
      - THREADS_USER_ID: Threads user profile ID
    """
    access_token = os.environ.get("THREADS_ACCESS_TOKEN")
    user_id = os.environ.get("THREADS_USER_ID")

    if not access_token or not user_id:
        token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "threads_token.txt")
        if os.path.exists(token_file):
            try:
                with open(token_file, "r", encoding="utf-8") as tf:
                    for line in tf:
                        if line.startswith("THREADS_ACCESS_TOKEN="):
                            access_token = line.split("=", 1)[1].strip()
                        elif line.startswith("THREADS_USER_ID="):
                            user_id = line.split("=", 1)[1].strip()
            except Exception:
                pass

    if not access_token or not user_id:
        print("[Threads] ℹ️ Skipped: THREADS_ACCESS_TOKEN or THREADS_USER_ID not configured.")
        return False

    try:
        # Step 1: Create Rich Devotional Caption (FB/Insta style, strictly under 490 chars)
        clean_lines = [l.strip() for l in caption.split("\n") if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("http")]
        quote_text = clean_lines[0] if clean_lines else "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।"

        if len(clean_lines) > 1:
            reflection = " ".join(clean_lines[1:])
        else:
            reflection = "जब जीवन में चिंता या संशय घेरे, तब गोविंद के इन वचनों को हृदय में धारण करें। निष्काम कर्म ही ईश्वर की सच्ची पूजा है।"

        wa_channel = "https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J"
        header = "✨ श्री कृष्ण अमृत विचार ✨\n\n"
        cta = f"\n\n🌸 4K दर्शन: {post_url}\n🟢 WhatsApp Channel:\n👉 {wa_channel}\n\n#RadhaKrishna #KrishnaVibez"

        max_allowed_body = 485 - len(header) - len(cta)
        body = f'"{quote_text}"\n\n{reflection}'
        if len(body) > max_allowed_body:
            allowed_ref = max_allowed_body - len(quote_text) - 8
            if allowed_ref > 30:
                reflection_cut = reflection[:allowed_ref].rsplit(" ", 1)[0] + "…"
                body = f'"{quote_text}"\n\n{reflection_cut}'
            else:
                body = f'"{quote_text[:max_allowed_body]}"'

        thread_text = f"{header}{body}{cta}"

        container_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
        media_type = "VIDEO" if is_video else "IMAGE"
        media_field = "video_url" if is_video else "image_url"

        create_payload = {
            "media_type": media_type,
            media_field: media_url,
            "text": thread_text,
            "access_token": access_token
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        res_create = requests.post(container_url, data=create_payload, headers=headers, timeout=20)
        create_data = res_create.json()
        creation_id = create_data.get("id")

        if not creation_id:
            print(f"[Threads] ⚠️ Failed to create {media_type} container: {create_data}. Retrying as TEXT thread...")
            text_payload = {
                "media_type": "TEXT",
                "text": thread_text,
                "access_token": access_token
            }
            res_create = requests.post(container_url, data=text_payload, headers=headers, timeout=20)
            create_data = res_create.json()
            creation_id = create_data.get("id")
            if not creation_id:
                print(f"[Threads] ⚠️ Text fallback also failed: {create_data}")
                return False

        # For video: poll container status until Meta Threads finishes transcoding
        if is_video and create_payload.get("media_type") == "VIDEO":
            status_url = f"https://graph.threads.net/v1.0/{creation_id}?fields=status,error_message&access_token={access_token}"
            video_ok = False
            for _ in range(12):  # Poll up to 60s
                time.sleep(5)
                try:
                    s_res = requests.get(status_url, timeout=10).json()
                    st = s_res.get("status")
                    if st == "FINISHED":
                        video_ok = True
                        break
                    elif st == "ERROR":
                        print(f"[Threads] Video processing failed: {s_res}")
                        break
                except Exception:
                    pass
            if not video_ok:
                print("[Threads] Video failed on Threads. Publishing as TEXT thread with direct link instead...")
                text_payload = {
                    "media_type": "TEXT",
                    "text": thread_text,
                    "access_token": access_token
                }
                res_create = requests.post(container_url, data=text_payload, headers=headers, timeout=20)
                creation_id = res_create.json().get("id")
                if not creation_id:
                    return False

        # Step 2: Publish Container
        publish_url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": access_token
        }

        res_pub = requests.post(publish_url, data=publish_payload, headers=headers, timeout=20)
        pub_data = res_pub.json()

        if pub_data.get("id"):
            print("[Threads] ✅ Successfully published to Meta Threads!")
            return True
        else:
            print(f"[Threads] ⚠️ Publish error: {pub_data}")
            return False

    except Exception as e:
        print(f"[Threads] ⚠️ Notice (non-fatal error): {e}")
        return False


def publish_to_reddit(title, post_url, media_url, is_video=False):
    """
    Submits link and wallpaper to Reddit via Reddit API.
    Required Secrets:
      - REDDIT_CLIENT_ID
      - REDDIT_CLIENT_SECRET
      - REDDIT_USERNAME
      - REDDIT_PASSWORD
      - REDDIT_SUBREDDIT (e.g. 'KrishnaVibez')
    """
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    username = os.environ.get("REDDIT_USERNAME")
    password = os.environ.get("REDDIT_PASSWORD")
    subreddit = os.environ.get("REDDIT_SUBREDDIT")

    if not all([client_id, client_secret, username, password, subreddit]):
        print("[Reddit] ℹ️ Skipped: Reddit credentials not fully configured.")
        return False

    try:
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        token_data = {
            "grant_type": "password",
            "username": username,
            "password": password
        }
        headers = {"User-Agent": "KrishnaVibezBot/1.0"}

        res_token = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data=token_data,
            headers=headers,
            timeout=15
        )
        token_json = res_token.json()
        oauth_token = token_json.get("access_token")

        if not oauth_token:
            print(f"[Reddit] ⚠️ Token acquisition failed: {token_json}")
            return False

        oauth_headers = {
            "Authorization": f"bearer {oauth_token}",
            "User-Agent": "KrishnaVibezBot/1.0"
        }

        submit_payload = {
            "sr": subreddit,
            "kind": "link",
            "title": title[:290],
            "url": post_url,
            "resubmit": "true",
            "sendreplies": False
        }

        res_sub = requests.post(
            "https://oauth.reddit.com/api/submit",
            headers=oauth_headers,
            data=submit_payload,
            timeout=20
        )
        sub_json = res_sub.json()

        if sub_json.get("success"):
            print(f"[Reddit] ✅ Successfully posted to r/{subreddit}!")
            return True
        else:
            print(f"[Reddit] ⚠️ Submission notice: {sub_json}")
            return False

    except Exception as e:
        print(f"[Reddit] ⚠️ Notice (non-fatal error): {e}")
        return False


def publish_all_channels(media_url, caption, title, post_url, is_video=False, youtube_url=None):
    """
    Master function that runs all multi-platform publishers in parallel or sequence.
    Guaranteed to never raise an exception, preventing any failure in main.py.
    """
    print("\n--- [Social Publisher] Starting Multi-Channel Broadcast ---")
    results = {}

    # 1. Telegram Channel
    results["telegram"] = publish_to_telegram(
        media_url=media_url,
        caption=caption,
        post_url=post_url,
        is_video=is_video,
        youtube_url=youtube_url
    )

    # 2. Pinterest API
    results["pinterest"] = publish_to_pinterest(
        media_url=media_url,
        title=title,
        description=caption,
        post_url=post_url,
        is_video=is_video
    )

    # 3. Meta Threads
    results["threads"] = publish_to_threads(
        media_url=media_url,
        caption=caption,
        post_url=post_url,
        is_video=is_video
    )

    # 4. Reddit
    results["reddit"] = publish_to_reddit(
        title=title,
        post_url=post_url,
        media_url=media_url,
        is_video=is_video
    )

    print("--- [Social Publisher] Broadcast Complete ---\n")
    return results

if __name__ == "__main__":
    # Self-test when executed directly
    print("Self-testing social_publisher.py...")
    test_results = publish_all_channels(
        media_url="https://krishnavibez.in/assets/logo.png",
        caption="कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
        title="कर्म करो, फल की चिंता मत करो",
        post_url="https://krishnavibez.in/",
        is_video=False
    )
    print("Test finished cleanly with results:", test_results)
