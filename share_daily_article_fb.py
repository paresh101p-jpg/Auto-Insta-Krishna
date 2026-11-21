# -*- coding: utf-8 -*-
"""
Automated Daily Article Sharer for Krishna Vibez Facebook Page
Selects upcoming festival / timely devotional articles and posts rich clickable links to Facebook.
"""

import os
import sys
import json
import random
import requests
from datetime import datetime, timezone, timedelta

_IST = timezone(timedelta(hours=5, minutes=30))

FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "1808917602588221")

token_file = os.path.join(os.path.dirname(__file__), "fb_permanent_token.txt")
if os.path.exists(token_file):
    try:
        with open(token_file, "r", encoding="utf-8") as tf:
            FB_ACCESS_TOKEN = tf.read().strip()
    except Exception:
        FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN", "")
else:
    FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN", "")

# Curated library of 33+ high-impact articles with festival calendar logic
ARTICLES_POOL = [
    {
        "slug": "gita-jayanti-mokshada-ekadashi-bhagavad-gita-sar",
        "title": "गीता जयंती 2026 और मोक्षदा एकादशी: कुरुक्षेत्र में श्री कृष्ण का अमर उपदेश, सम्पूर्ण गीता सार एवं 10 दिव्य सूत्र",
        "highlight": "कुरुक्षेत्र के रणक्षेत्र में अर्जुन को दिए गए अमर गीता ज्ञान, 18 अध्यायों का संपूर्ण सार, मोक्षदा एकादशी का महत्व और जीवन को बदलने वाले 10 व्यावहारिक सूत्र।",
        "season_months": [11, 12], # November / December special
        "is_festival": True
    },
    {
        "slug": "karmanye-vadhikaraste-ma-phaleshu-kadachana-meaning-in-hindi",
        "title": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन का वास्तविक अर्थ: जीवन और करियर में इसका सही प्रयोग",
        "highlight": "क्यों इंसान फल की चिंता में अपने वर्तमान कर्म को बिगाड़ बैठता है? जानिए श्री कृष्ण का वह सूत्र जो आपको कर्म करते हुए भी तनावमुक्त और विजयी बनाता है।",
        "is_festival": False
    },
    {
        "slug": "overthinking-aur-chinta-se-mukti-shree-krishna-updesh",
        "title": "ओवरथिंकिंग और चिंता से मुक्ति: श्री कृष्ण के 5 अचूक उपदेश",
        "highlight": "दिमाग में विचारों का निरंतर तूफान कैसे शांत करें? भगवान श्री कृष्ण के बताए अभ्यास और वैराग्य के व्यावहारिक नियम जो मन को तत्काल स्थिर करते हैं।",
        "is_festival": False
    },
    {
        "slug": "mann-ko-vash-me-kaise-kare-gita-abhyas-vairagya",
        "title": "मन को वश में कैसे करें: गीता अभ्यास और वैराग्य सूत्र",
        "highlight": "चंचलं हि मनः कृष्ण प्रमाथि बलवद्दृढम्। मन हवा की तरह चंचल है, इसे वश में करना कठिन अवश्य है लेकिन असंभव नहीं। जानिए श्री कृष्ण का सरल समाधान।",
        "is_festival": False
    },
    {
        "slug": "krodh-se-bhram-aur-buddhi-vinash-gita-shlok-meaning",
        "title": "क्रोध से भ्रम और बुद्धि नाश: क्रोध को शांत करने के 5 अचूक नियम",
        "highlight": "क्रोधाद्भवति संमोहः संमोहात्स्मृतिविभ्रमः। जब गुस्सा आता है तो सबसे पहले अपनी ही सोचने-समझने की शक्ति क्यों खो जाती है? श्री कृष्ण का आत्म-नियंत्रण सूत्र।",
        "is_festival": False
    },
    {
        "slug": "arjun-ka-vishad-depression-aur-stress-se-mukti-ke-upay",
        "title": "अर्जुन का विषाद: जब जीवन में सब कुछ व्यर्थ और कठिन लगने लगे तो क्या करें?",
        "highlight": "अवसाद, निराशा और मानसिक तनाव से मुक्ति का आध्यात्मिक विज्ञान। गीता के प्रथम अध्याय से सीखें विषम परिस्थितियों में सही निर्णय लेने की कला।",
        "is_festival": False
    },
    {
        "slug": "bhagavad-gita-quotes-for-students-padhai-me-ekagrata",
        "title": "विद्यार्थियों के लिए भगवद्गीता के अनमोल सूत्र: पढ़ाई में एकाग्रता और परीक्षा के डर से मुक्ति",
        "highlight": "पढ़ाई में मन न लगना, एकाग्रता की कमी और असफलता का डर? जानिए श्री कृष्ण के वे नियम जो छात्रों को मानसिक रूप से मजबूत और सफल बनाते हैं।",
        "is_festival": False
    },
    {
        "slug": "radha-krishna-ka-prem-kya-sikhata-hai-divine-love-meaning",
        "title": "सच्चे प्रेम की पराकाष्ठा: श्री राधा-कृष्ण का दिव्य प्रेम और पवित्र रिश्तों का रहस्य",
        "highlight": "प्रेम अधिकार नहीं, समर्पण है। जानिए भगवान श्री कृष्ण और राधा रानी के निस्वार्थ प्रेम की वह गहराइयां जो आज के रिश्तों को अटूट और पवित्र बना सकती हैं।",
        "is_festival": False
    },
    {
        "slug": "bhagavad-gita-ke-18-adhyaya-ka-sampurna-sar-hindi-me",
        "title": "श्रीमद्भगवद्गीता के 18 अध्यायों का संपूर्ण सार सरल हिंदी में",
        "highlight": "कर्म योग, भक्ति योग और ज्ञान योग का समन्वय। जानिए जीवन के हर पहलू को संतुलित और सफल बनाने वाले गीता के 18 अध्यायों का सार।",
        "is_festival": False
    }
]

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "shared_articles_history.json")

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(slug):
    hist = load_history()
    hist.append({"slug": slug, "posted_at": datetime.now(_IST).isoformat()})
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=2)

def pick_article_for_today():
    now = datetime.now(_IST)
    current_month = now.month
    hist = [x["slug"] for x in load_history()]

    # Priority 1: Festival / Timely articles matching the current season/month
    seasonal = [a for a in ARTICLES_POOL if a.get("is_festival") and current_month in a.get("season_months", [])]
    for s in seasonal:
        # If not posted in the last 7 days, prioritize it
        recent = [x["slug"] for x in load_history()[-7:]]
        if s["slug"] not in recent:
            return s

    # Priority 2: Unposted or least recently posted evergreen articles
    unposted = [a for a in ARTICLES_POOL if a["slug"] not in hist]
    if unposted:
        return random.choice(unposted)

    # Priority 3: Rotate through articles not in the last 15 posts
    recent_slugs = [x["slug"] for x in load_history()[-15:]]
    candidates = [a for a in ARTICLES_POOL if a["slug"] not in recent_slugs]
    if candidates:
        return random.choice(candidates)
    
    return random.choice(ARTICLES_POOL)

def post_article_to_facebook(article=None):
    if not article:
        article = pick_article_for_today()

    slug = article["slug"]
    title = article["title"]
    highlight = article["highlight"]
    article_url = f"https://krishnavibez.in/articles/{slug}.html"

    # Construct engaging, high-CTR Facebook post caption
    caption = f"""🪷 श्रीमद्भगवद्गीता ज्ञान एवं विशेष पर्व विशेषांक 🪷

✨ {title}

"{highlight}"

भगवान श्री कृष्ण के अमर उपदेश और जीवन की हर उलझन को सुलझाने वाले दिव्य सूत्रों को गहराई से समझने के लिए यह लेख अवश्य पढ़ें।

📖 संपूर्ण विस्तृत लेख पढ़ने के लिए नीचे दिए गए लिंक पर क्लिक करें 👇
🔗 {article_url}

॥ हरे कृष्ण हरे कृष्ण कृष्ण कृष्ण हरे हरे ॥
॥ हरे राम हरे राम राम राम हरे हरे ॥

#KrishnaVibez #BhagavadGita #GitaJayanti #ShriKrishna #RadhaKrishna #GitaGyan #SpiritualWisdom #SanatanDharma #KarmaYoga #GeetaSaar"""

    print(f"Sharing article to Facebook Page ({FB_PAGE_ID})...")
    print(f"Article: {title}")
    print(f"URL: {article_url}")

    endpoint = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/feed"
    payload = {
        "message": caption,
        "link": article_url,
        "access_token": FB_ACCESS_TOKEN
    }

    resp = requests.post(endpoint, data=payload, timeout=30)
    data = resp.json()

    if resp.status_code == 200 and "id" in data:
        post_id = data["id"]
        print(f"✅ SUCCESS! Article posted to Facebook Page. Post ID: {post_id}")
        save_history(slug)
        return True, post_id
    else:
        print(f"❌ FAILED to post to Facebook: {data}")
        return False, data

if __name__ == "__main__":
    success, res = post_article_to_facebook()
    sys.exit(0 if success else 1)
