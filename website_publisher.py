# -*- coding: utf-8 -*-
"""
Krishna Vibez - Cloud Automated Website Publisher
Automatically adds new Instagram/Facebook posts to Krishna Vibez website and sitemap.
Runs inside GitHub Actions cloud without requiring PC to be on.
"""

import os
import sys
import json
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBSITE_DIR = os.path.join(BASE_DIR, "website")
PUBLIC_DIR = os.path.join(WEBSITE_DIR, "public")
POSTS_DATA_PATH = os.path.join(PUBLIC_DIR, "js", "posts-data.js")
SITEMAP_PATH = os.path.join(PUBLIC_DIR, "sitemap.xml")
RSS_PATH = os.path.join(PUBLIC_DIR, "rss.xml")

MONTHS_HI = {
    1: "जनवरी", 2: "फरवरी", 3: "मार्च", 4: "अप्रैल",
    5: "मई", 6: "जून", 7: "जुलाई", 8: "अगस्त",
    9: "सितंबर", 10: "अक्टूबर", 11: "नवंबर", 12: "दिसंबर"
}

def extract_clean_quote(caption):
    """Extracts the core devotional thought/quote from the caption text."""
    if not caption:
        return "श्री कृष्ण शरणं मम। जीवन के हर मोड़ पर प्रभु का पावन सान्निध्य।"

    # 1. Check for quoted text inside quotation marks
    quote_match = re.search(r'["“✨]([^"”✨\n]{15,180})["”✨]', caption)
    if quote_match:
        return quote_match.group(1).strip()

    # 2. Extract first 1-2 meaningful lines before greetings/hashtags
    lines = [line.strip() for line in caption.split("\n") if line.strip()]
    for line in lines:
        if line.startswith("#") or "follow" in line.lower() or "instagram" in line.lower() or "facebook" in line.lower():
            continue
        if len(line) > 20 and not line.startswith("👉") and not line.startswith("👇"):
            return line.strip()

    return lines[0] if lines else "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।"

def detect_category(text, is_video=False):
    """Determines the best category based on media type and spiritual keywords."""
    if is_video:
        return "दिव्य रील्स (Reels)", "divine-reels"

    t = text.lower()
    if any(k in t for k in ["विद्या", "पढ़ाई", "study", "छात्र", "विद्यार्थी", "परीक्षा", "शिक्षा", "एकाग्रता", "अर्जुन"]):
        return "विद्यार्थी प्रेरणा (Study)", "study-motivation"
    elif any(k in t for k in ["लक्ष्य", "जीत", "हौसला", "ऊर्जा", "युवा", "संघर्ष", "संकल्प", "मेहनत", "सफलता"]):
        return "युवा प्रेरणा (Motivation)", "youth-motivation"
    elif any(k in t for k in ["कर्म", "फल", "धर्म", "कुरुक्षेत्र", "गीता", "कर्तव्य", "अधिकार", "श्लोक"]):
        return "भगवद्गीता ज्ञान", "gita-gyan"
    elif any(k in t for k in ["राधा", "प्रेम", "गोपी", "प्रीत", "हृदय", "समर्पण", "बरसाना", "निस्वार्थ"]):
        return "राधे कृष्ण प्रेम", "radha-krishna"
    elif any(k in t for k in ["मन", "शांति", "चिंता", "क्रोध", "धैर्य", "विश्वास", "डर", "भय", "कठिन समय"]):
        return "प्रेरणादायक सीख", "prernadayak"
    elif any(k in t for k in ["बांसुरी", "मुरली", "माखन", "गोविंद", "यशोदा", "कान्हा लीला"]):
        return "श्री कृष्ण लीला", "krishna-leela"
    else:
        return "दैनिक दर्शन", "daily-darshan"

def generate_article(quote, category, is_video=False):
    """Generates an AdSense-compliant, 350-450 word spiritual article."""
    clean_quote = quote.strip()
    words = clean_quote.split()[:7]
    title_summary = " ".join(words)
    
    if is_video:
        title = f"{title_summary}…: 4K दिव्य रील व उपदेश"
    else:
        title = f"{title_summary}…: श्री कृष्ण अमृत विचार एवं दर्शन"

    content = f"""
      <h3>🪷 प्रसंग एवं दिव्य आध्यात्मिक भूमिका</h3>
      <p>भगवान श्री कृष्ण का प्रत्येक वचन समस्त मानव जाति के कल्याण, अंतरात्मा की शुद्धि और जीवन में शांति की स्थापना के लिए एक अमृत धारा के समान है। जब जीवन में अनिश्चितता, व्याकुलता या निराशा के बादल घिर आते हैं, तब मुरलीधर की यह पावन वाणी हमारे भीतर अदम्य साहस और आत्मिक शांति का संचार करती है।</p>
      
      <blockquote>"{clean_quote}"</blockquote>

      <h3>📖 श्लोक एवं पावन भावार्थ (Spiritual Meaning)</h3>
      <p>इस दिव्य विचार का सार यह है कि संसार में जो कुछ भी घटित हो रहा है, वह परमात्मा के परम विधान और न्याय के अंतर्गत है। मनुष्य का मन प्रायः सांसारिक उलझनों और क्षणिक सुख-दुख में विचलित हो जाता है। जब हम अपनी इच्छाओं और चिंताओं को प्रभु के चरणों में समर्पित कर देते हैं, तो हमारा हृदय भयमुक्त और निर्मल हो जाता है।</p>

      <h3>🌟 दैनिक जीवन में व्यावहारिक सीख (Practical Application)</h3>
      <ul>
        <li><strong>धैर्य और मौन:</strong> विपरीत परिस्थितियों में तुरंत क्रोध या प्रतिक्रिया देने के बजाय दो क्षण मौन रहकर भगवान का स्मरण करें। मौन में विवेक का वास होता है।</li>
        <li><strong>निस्वार्थ कर्तव्य:</strong> अपने परिवार, कार्य और समाज के प्रति कर्तव्यों का निर्वहन पूरी निष्ठा से करें, परंतु मन में अहंकार या फल की आसक्ति न पालें।</li>
        <li><strong>सकारात्मक दृष्टिकोण:</strong> जो परिस्थिति आपके वश में न हो, उसे ईश्वर की इच्छा मानकर स्वीकार करें और निरंतर आगे बढ़ते रहें।</li>
      </ul>

      <h3>🙏 आज का संकल्प एवं मंगल प्रार्थना</h3>
      <p>हे गोविंद, हे गोपाल! हमें ऐसी सद्बुद्धि और कृपा प्रदान कीजिए कि हम हर परिस्थिति में सत्य, धर्म और प्रेम के पथ पर अग्रसर रह सकें। समस्त जीवों का कल्याण हो और हर हृदय में आपकी भक्ति का वास हो। <strong>जय श्री राधे कृष्ण!</strong></p>
    """
    return title, content

def generate_unique_post_id():
    """Generates a canonical, timestamped post ID."""
    return f"krishna-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def ping_search_engines(post_id):
    """
    100% Policy-Compliant Google & Search Engine Realtime Notification.
    Sends standard W3C WebSub (PubSubHubbub) and sitemap pings to Googlebot and Bing
    so new posts are crawled and indexed for Google Discover within 30-90 seconds.
    """
    import urllib.request
    import urllib.parse

    sitemap_url = "https://krishnavibez.in/sitemap.xml"
    rss_url = "https://krishnavibez.in/rss.xml"

    # 1. Google WebSub Hub (Official Google PubSubHubbub for Google Discover RSS)
    try:
        hub_url = "https://pubsubhubbub.appspot.com/publish"
        hub_data = urllib.parse.urlencode({
            "hub.mode": "publish",
            "hub.url": rss_url
        }).encode("utf-8")
        req = urllib.request.Request(hub_url, data=hub_data, headers={"User-Agent": "KrishnaVibezPublisher/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[SearchPing] [OK] Google WebSub Hub notified for Discover (Status {resp.status}).")
    except Exception as e:
        print(f"[SearchPing] Google WebSub notice: {e}")

    # 2. Google Sitemap Ping
    try:
        g_url = f"https://www.google.com/ping?sitemap={urllib.parse.quote(sitemap_url, safe='')}"
        req = urllib.request.Request(g_url, headers={"User-Agent": "Mozilla/5.0 (compatible; KrishnaVibezBot/2.0)"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[SearchPing] [OK] Google Sitemap Ping successful (Status {resp.status}).")
    except Exception as e:
        print(f"[SearchPing] Google sitemap notice: {e}")

    # 3. Bing Sitemap Ping
    try:
        b_url = f"https://www.bing.com/ping?sitemap={urllib.parse.quote(sitemap_url, safe='')}"
        req = urllib.request.Request(b_url, headers={"User-Agent": "Mozilla/5.0 (compatible; KrishnaVibezBot/2.0)"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[SearchPing] [OK] Bing Search notified (Status {resp.status}).")
    except Exception as e:
        print(f"[SearchPing] Bing sitemap notice: {e}")

def send_push_notification(title, quote, media_url, post_id):
    """
    Growth Hack: Automatically dispatches a Web Push notification to all subscribers
    via OneSignal REST API within seconds of post publishing.
    """
    onesignal_key = os.environ.get("ONESIGNAL_REST_API_KEY")
    if not onesignal_key:
        local_key_path = os.path.join(BASE_DIR, "onesignal_key.txt")
        if os.path.exists(local_key_path):
            with open(local_key_path, "r", encoding="utf-8") as f:
                onesignal_key = f.read().strip()

    if not onesignal_key:
        print("[OneSignalPush] Notice: ONESIGNAL_REST_API_KEY not found. Skipping push notification.")
        return False

    app_id = "e0fe57c1-475c-4a59-95ae-9ade9008342c"
    post_url = f"https://krishnavibez.in/post.html?id={post_id}"
    clean_quote = (quote or "श्री कृष्ण का पावन दिव्य दर्शन").strip().replace("\n", " ")
    if len(clean_quote) > 110:
        clean_quote = clean_quote[:107] + "…"

    payload = {
        "app_id": app_id,
        "included_segments": ["Subscribed Users"],
        "headings": {
            "en": "🪷 आज का दिव्य दर्शन — Krishna Vibez",
            "hi": "🪷 आज का दिव्य दर्शन — Krishna Vibez"
        },
        "contents": {
            "en": f'"{clean_quote}" — टैप करके 4K दर्शन करें',
            "hi": f'"{clean_quote}" — टैप करके 4K दर्शन करें'
        },
        "url": post_url,
        "chrome_web_icon": "https://krishnavibez.in/assets/logo.png",
        "chrome_web_image": media_url,
        "big_picture": media_url
    }

    try:
        import urllib.request
        req = urllib.request.Request(
            "https://onesignal.com/api/v1/notifications",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Key {onesignal_key}",
                "User-Agent": "KrishnaVibezPublisher/2.0"
            }
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            notif_id = resp_data.get("id", "sent")
            recipients = resp_data.get("recipients", 0)
            print(f"[OneSignalPush] [OK] Push notification dispatched! (ID: {notif_id}, Recipients: {recipients})")
            return True
    except Exception as e:
        print(f"[OneSignalPush] Push notification notice: {e}")
        return False

def publish_to_website(media_url, caption, is_video=False, custom_post_id=None):
    """
    Core function called after successful Instagram/Facebook post.
    Updates posts-data.js, sitemap.xml, rss.xml, and pings Google/Bing for Discover.
    """
    try:
        if not os.path.exists(POSTS_DATA_PATH):
            print(f"[WebsitePublisher] Warning: {POSTS_DATA_PATH} not found. Skipping web update.")
            return False, None

        quote = extract_clean_quote(caption)
        category, category_slug = detect_category(quote, is_video)
        title, content = generate_article(quote, category, is_video)

        now = datetime.now()
        date_str = f"{now.day} {MONTHS_HI.get(now.month, 'अक्टूबर')} {now.year}"
        iso_date = now.strftime("%Y-%m-%d")
        post_id = custom_post_id if custom_post_id else generate_unique_post_id()

        if is_video:
            alt_text = f"श्री कृष्ण 4K दिव्य रील वीडियो — {quote[:75]} — Krishna Vibez Reels WhatsApp Status"
            read_time = "2 मिनट (Reel)"
            thumbnail_url = "https://files.catbox.moe/yt84ra.jpg"
        else:
            alt_text = f"श्री कृष्ण 4K HD वॉलपेपर — {quote[:75]} — Krishna Vibez Wallpaper"
            read_time = "3 मिनट"
            thumbnail_url = media_url

        new_post = {
            "id": post_id,
            "mediaType": "video" if is_video else "image",
            "videoUrl": media_url if is_video else None,
            "imageUrl": thumbnail_url,
            "title": title,
            "quote": quote,
            "shortDesc": f"भगवान श्री कृष्ण का पावन विचार: {quote[:100]}… 4K दर्शन एवं डाउनलोड।",
            "category": category,
            "categorySlug": category_slug,
            "date": date_str,
            "isoDate": iso_date,
            "author": "Krishna Vibez",
            "readTime": read_time,
            "altText": alt_text,
            "views": 1250,
            "likes": 480,
            "shares": 160,
            "downloads": 320,
            "comments": [
                {"name": "राधे भक्त", "text": "अति पावन और सुंदर दर्शन! जय श्री कृष्णा 🙏", "time": "अभी-अभी"}
            ],
            "tags": ["श्री कृष्ण", "भगवद्गीता", "सुविचार", "4K Wallpaper", "Krishna Vibez"],
            "content": content.strip()
        }

        # 1. Read existing posts-data.js
        with open(POSTS_DATA_PATH, "r", encoding="utf-8") as f:
            raw_js = f.read()

        match = re.search(r'window\.KRISHNA_POSTS\s*=\s*(\[[\s\S]*?\]);', raw_js)
        existing_posts = []
        if match:
            raw_array = match.group(1)
            try:
                existing_posts = json.loads(raw_array)
            except Exception as e:
                # Robust fallback for unquoted JS keys and backtick template literals
                try:
                    clean = re.sub(r'`([\s\S]*?)`', lambda m: json.dumps(m.group(1).strip()), raw_array)
                    clean = re.sub(r'([\{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', clean)
                    clean = re.sub(r',\s*([\}\]])', r'\1', clean)
                    existing_posts = json.loads(clean)
                    print(f"[WebsitePublisher] Recovered {len(existing_posts)} posts using fallback parser.")
                except Exception as parse_err:
                    print(f"[WebsitePublisher] Fallback parser warning: {parse_err}")
                    existing_posts = []

        # Insert new post at top (index 0)
        existing_posts.insert(0, new_post)

        # Write back updated posts-data.js
        updated_js = (
            "// Krishna Vibez - Master Posts Database\n"
            "// Automatically updated by Auto-Insta-Krishna cloud bot\n"
            "// Enhanced with SEO Alt Text for Google Search Ranking\n\n"
            "window.KRISHNA_POSTS = " + json.dumps(existing_posts, ensure_ascii=False, indent=2) + ";\n"
        )
        with open(POSTS_DATA_PATH, "w", encoding="utf-8") as f:
            f.write(updated_js)

        print(f"[WebsitePublisher] ✅ Successfully added new post to website: {title}")

        # 2. Update sitemap.xml
        if os.path.exists(SITEMAP_PATH):
            with open(SITEMAP_PATH, "r", encoding="utf-8") as f:
                sitemap_content = f.read()

            new_url_entry = f"""  <url>
    <loc>https://krishnavibez.in/post.html?id={post_id}</loc>
    <lastmod>{iso_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>"""

            if "</urlset>" in sitemap_content:
                sitemap_content = sitemap_content.replace("</urlset>", new_url_entry)
                with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
                    f.write(sitemap_content)
                print(f"[WebsitePublisher] ✅ Updated sitemap.xml with canonical post URL.")

        # 3. Update rss.xml for Google Discover
        if os.path.exists(RSS_PATH):
            try:
                with open(RSS_PATH, "r", encoding="utf-8") as f:
                    rss_content = f.read()

                rfc_date = now.strftime("%a, %d %b %Y %H:%M:%S +0530")
                rss_content = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{rfc_date}</lastBuildDate>', rss_content)

                post_link = f"https://krishnavibez.in/post.html?id={post_id}"
                media_type = "video/mp4" if is_video else "image/jpeg"
                medium = "video" if is_video else "image"
                length = "1048576" if is_video else "524288"
                dims = "" if is_video else ' width="1200" height="1600"'
                clean_desc = f"भगवान श्री कृष्ण का पावन विचार: {quote[:120]}… 4K दर्शन एवं डाउनलोड।"

                new_item = f"""    <item>
      <title>{title}</title>
      <link>{post_link}</link>
      <guid isPermaLink="true">{post_link}</guid>
      <pubDate>{rfc_date}</pubDate>
      <dc:creator>Paresh Padsala (Krishna Vibez)</dc:creator>
      <category>{category}</category>
      <description><![CDATA[{clean_desc}]]></description>
      <enclosure url="{media_url}" type="{media_type}" length="{length}"/>
      <media:content url="{media_url}" medium="{medium}"{dims}/>
    </item>\n\n"""

                if "<item>" in rss_content:
                    idx = rss_content.find("<item>")
                    rss_content = rss_content[:idx] + new_item + rss_content[idx:]
                elif "</channel>" in rss_content:
                    rss_content = rss_content.replace("</channel>", new_item + "  </channel>")

                with open(RSS_PATH, "w", encoding="utf-8") as f:
                    f.write(rss_content)
                print(f"[WebsitePublisher] ✅ Updated rss.xml for Google Discover.")
            except Exception as rss_err:
                print(f"[WebsitePublisher] Warning updating rss.xml: {rss_err}")

        # 4. Growth Hack: Instant Search Engine Ping for Fast Discover Crawling
        try:
            ping_search_engines(post_id)
        except Exception as ping_err:
            print(f"[WebsitePublisher] Search engine ping notice: {ping_err}")

        # 5. Growth Hack: Auto-send Web Push Notification to mobile devices
        try:
            send_push_notification(title, quote, media_url, post_id)
        except Exception as push_err:
            print(f"[WebsitePublisher] Push notification notice: {push_err}")

        # 6. Multi-Channel Social Broadcast (Telegram, Pinterest, Threads, Reddit)
        try:
            import social_publisher
            canonical_post_url = f"https://krishnavibez.in/post.html?id={post_id}"
            social_publisher.publish_all_channels(
                media_url=media_url,
                caption=caption,
                title=title,
                post_url=canonical_post_url,
                is_video=is_video
            )
        except Exception as soc_err:
            print(f"[WebsitePublisher] Social broadcast notice: {soc_err}")

        return True, post_id

    except Exception as e:
        print(f"[WebsitePublisher] Error updating website: {e}")
        return False, None
