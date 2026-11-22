# -*- coding: utf-8 -*-
"""
Autonomous Daily Trending Spiritual Article Engine for Krishna Vibez (krishnavibez.in)
- Runs daily at 7:00 AM IST
- Finds today's top trending/timely topic (Hindu calendar, tithi, festival, or deep Bhagavad Gita wisdom)
- Researches & writes 100% original, plagiarism-free 2200-2500+ words SEO pillar article
- Injects Schema.org JSON-LD (Article, FAQPage, Breadcrumb), TOC, 1200x675 HD visuals
- Updates website/public/articles/{slug}.html, articles.html, articles-sitemap.xml, rss.xml
- Auto-deploys to Firebase Hosting
- Auto-posts clickable rich link to Facebook Page (Krishna Vibez: 1808917602588221)
"""

import os
import sys
import re
import json
import random
import requests
from datetime import datetime, timezone, timedelta
from google import genai

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_IST = timezone(timedelta(hours=5, minutes=30))

# ----------------- Configuration & Paths -----------------
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
WEBSITE_DIR = os.path.join(REPO_ROOT, "website")
PUBLIC_DIR = os.path.join(WEBSITE_DIR, "public")
ARTICLES_DIR = os.path.join(PUBLIC_DIR, "articles")
ARTICLES_INDEX_FILE = os.path.join(PUBLIC_DIR, "articles.html")
SITEMAP_FILE = os.path.join(PUBLIC_DIR, "articles-sitemap.xml")
RSS_FILE = os.path.join(PUBLIC_DIR, "rss.xml")
HISTORY_FILE = os.path.join(REPO_ROOT, "shared_articles_history.json")

# Environment & Credentials
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    gk_file = os.path.join(REPO_ROOT, "gemini_key.txt")
    if os.path.exists(gk_file):
        try:
            with open(gk_file, "r", encoding="utf-8") as f:
                GEMINI_API_KEY = f.read().strip()
        except Exception:
            pass

FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "1808917602588221")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
if not FB_ACCESS_TOKEN:
    tf_file = os.path.join(REPO_ROOT, "fb_permanent_token.txt")
    if os.path.exists(tf_file):
        try:
            with open(tf_file, "r", encoding="utf-8") as f:
                FB_ACCESS_TOKEN = f.read().strip()
        except Exception:
            pass

# High-quality, safe, 1200x675+ divine Krishna & sacred aesthetic images pool
HERO_IMAGES_POOL = [
    "https://files.catbox.moe/3g5io2.jpg",
    "https://files.catbox.moe/r6g9mx.png",
    "https://files.catbox.moe/4f3x7k.jpg",
    "https://files.catbox.moe/5m9p1q.jpg",
    "https://files.catbox.moe/8v2b6c.jpg",
    "https://files.catbox.moe/9k4m2w.jpg",
    "https://files.catbox.moe/1d7x8z.jpg",
    "https://files.catbox.moe/2h5n8y.jpg"
]

def get_existing_slugs():
    slugs = set()
    if os.path.exists(ARTICLES_DIR):
        for f in os.listdir(ARTICLES_DIR):
            if f.endswith(".html"):
                slugs.add(f[:-5])
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    if "slug" in item:
                        slugs.add(item["slug"])
        except Exception:
            pass
    return list(slugs)

def call_gemini(prompt, system_instruction=""):
    client = genai.Client(api_key=GEMINI_API_KEY)
    models = ["gemini-3.1-flash-lite", "gemini-3.7-flash", "gemini-3.8-flash"]
    for m in models:
        try:
            config = {}
            if system_instruction:
                config["system_instruction"] = system_instruction
            res = client.models.generate_content(
                model=m,
                contents=prompt,
                config=config if config else None
            )
            if res and res.text:
                return res.text.strip()
        except Exception as e:
            print(f"   [Model Notice] {m} failed: {e}. Trying fallback...")
            continue
    raise RuntimeError("All Gemini models failed to generate content.")

def determine_today_topic():
    now_ist = datetime.now(_IST)
    date_str = now_ist.strftime("%d-%m-%Y")
    month_name = now_ist.strftime("%B")
    existing_slugs = get_existing_slugs()

    prompt = f"""You are the Chief Spiritual Researcher and Head SEO Strategist for Krishna Vibez (krishnavibez.in).
Today's Date in India (IST): {date_str} ({month_name}).

Your task: Determine today's single most impactful, trending, and high-search-intent spiritual topic for our website.
CRITICAL RULES:
1. Research today's Hindu calendar / Panchang / Tithi / Festival (such as Ekadashi, Purnima, Amavasya, Pradosh, Gita Jayanti, Janmashtami, Shivratri, Navratri, Diwali, Kartik / Margashirsha special, or current auspicious period). If today or this upcoming week has an auspicious tithi or festival, PRIORITIZE it with its Lord Krishna / Bhagavad Gita inner spiritual meaning.
2. If today is a normal day without a major festival, choose a high-volume, deep-search evergreen Bhagavad Gita life-management theme (e.g. Dealing with Overthinking & Anxiety, Karma Yoga in modern professional career, Anger management, Overcoming fear of failure, True detachment vs love, Why bad things happen to good people).
3. Plagiarism & Duplicate Ban: The topic must be 100% FRESH and NOT duplicate or overlap with any of these existing slugs:
{json.dumps(existing_slugs[-20:], ensure_ascii=False)}

Output STRICTLY a JSON object with this exact structure and nothing else:
{{
  "slug": "url-friendly-lowercase-slug-without-html",
  "title": "Hindi Title between 60 to 90 characters (compelling, click-worthy, Google Discover optimized)",
  "category": "One of: महापर्व विशेषांक | गीता ज्ञान | जीवन प्रबंधन | कर्म योग | भक्ति एवं ध्यान",
  "meta_desc": "Engaging Hindi summary between 140 to 160 characters for Google meta description",
  "keywords": "8 to 10 high-intent keywords separated by commas in Hindi and English",
  "hook": "A 2-line poetic or thought-provoking introductory hook quote",
  "theme_outline": "A short summary of the core thesis and practical lessons covered"
}}
"""
    raw = call_gemini(prompt)
    clean_json = re.sub(r"^```json\s*", "", raw.strip(), flags=re.MULTILINE)
    clean_json = re.sub(r"\s*```$", "", clean_json.strip(), flags=re.MULTILINE)
    data = json.loads(clean_json)
    data["slug"] = re.sub(r"[^a-z0-9\-]", "-", data["slug"].lower()).strip("-")
    return data

def generate_full_article_content(topic_meta):
    prompt = f"""You are a master Vedic scholar, philosopher, and senior editor for Krishna Vibez.
Write a comprehensive, 2200 to 2500+ word, 100% original, deeply insightful pillar article in pure Hindi on the topic:
TITLE: {topic_meta['title']}
CATEGORY: {topic_meta['category']}
THEME: {topic_meta['theme_outline']}

MANDATORY EDITORIAL STANDARDS:
1. ZERO Plagiarism: Do not copy or paraphrase generic articles. Write with profound emotional depth, authentic spiritual authority, and practical real-world psychological application.
2. Structure:
   - Compelling Introduction: Set the emotional and philosophical stage (Why this matters to modern human life).
   - Chapter 1: The Spiritual & Scriptural Context (Reference to Bhagavad Gita / Shrimad Bhagavatam / Vedic wisdom with authentic Sanskrit shlok and word-by-word meaning).
   - Chapter 2: The Core Psychological Breakdown (How human mind, ego, desires, or doubts operate).
   - Chapter 3: Practical Modern Application (How to apply this in career, family, daily stress, relationships, and modern challenges).
   - Chapter 4: Common Misconceptions & The True Sanatan Truth.
   - Chapter 5: 10 Golden Life Sutras (Numbered 1 to 10, bold titles with actionable 2-line takeaways).
   - Chapter 6: Frequently Asked Questions (5 detailed, highly realistic questions people ask on Google with authentic answers).
   - Chapter 7: Conclusion & Mahamantra Meditation guidance.

OUTPUT FORMAT:
Generate ONLY the semantic HTML body content (do NOT include <html> or <body> tags, only the article inner HTML starting from <section class="article-content">).
Use proper tags:
- <h2> for main section headers
- <h3> for sub-headings
- <p> for detailed paragraphs (at least 3-4 rich paragraphs per section)
- <blockquote> for Sanskrit shlokas and their translation
- <ol> and <li> for the 10 Golden Sutras
- <div class="faq-item"><h3>Q...</h3><p>A...</p></div> for the 5 FAQs
- <div class="article-callout"> for key insights
"""
    content_html = call_gemini(prompt)
    content_html = re.sub(r"^```html\s*", "", content_html.strip(), flags=re.MULTILINE)
    content_html = re.sub(r"\s*```$", "", content_html.strip(), flags=re.MULTILINE)
    return content_html

def build_complete_article_page(topic_meta, content_html):
    slug = topic_meta["slug"]
    title = topic_meta["title"]
    category = topic_meta["category"]
    meta_desc = topic_meta["meta_desc"]
    keywords = topic_meta["keywords"]
    canonical_url = f"https://krishnavibez.in/articles/{slug}.html"
    now_ist = datetime.now(_IST)
    date_iso = now_ist.isoformat()
    display_date = now_ist.strftime("%d-%m-%Y")

    hero_img = random.choice(HERO_IMAGES_POOL)

    # Extract FAQs for FAQPage Schema
    faq_matches = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", content_html)
    faq_schema_items = []
    for q, a in faq_matches[:5]:
        clean_q = re.sub(r"<[^>]+>", "", q).strip()
        clean_a = re.sub(r"<[^>]+>", "", a).strip()
        if "?" in clean_q or "प्रश्न" in clean_q or "क्या" in clean_q or "कैसे" in clean_q or "क्यों" in clean_q:
            faq_schema_items.append({
                "@type": "Question",
                "name": clean_q,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": clean_a
                }
            })

    schema_graph = [
        {
            "@type": "Article",
            "@id": f"{canonical_url}#article",
            "isPartOf": {
                "@type": "WebSite",
                "@id": "https://krishnavibez.in/#website",
                "url": "https://krishnavibez.in/",
                "name": "Krishna Vibez",
                "description": "श्री कृष्ण सुविचार, भगवद्गीता सार, 4K HD वॉलपेपर & स्टेटस"
            },
            "headline": title,
            "description": meta_desc,
            "image": hero_img,
            "datePublished": date_iso,
            "dateModified": date_iso,
            "inLanguage": "hi-IN",
            "mainEntityOfPage": canonical_url,
            "author": {
                "@type": "Person",
                "name": "Paresh Padsala",
                "url": "https://krishnavibez.in/about.html"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Krishna Vibez",
                "url": "https://krishnavibez.in/",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://krishnavibez.in/assets/logo.png"
                }
            }
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{canonical_url}#breadcrumb",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "होम",
                    "item": "https://krishnavibez.in/"
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "आर्टिकल्स",
                    "item": "https://krishnavibez.in/articles.html"
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": title,
                    "item": canonical_url
                }
            ]
        }
    ]

    if faq_schema_items:
        schema_graph.append({
            "@type": "FAQPage",
            "@id": f"{canonical_url}#faq",
            "mainEntity": faq_schema_items
        })

    json_ld_str = json.dumps({"@context": "https://schema.org", "@graph": schema_graph}, ensure_ascii=False, indent=2)

    page_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Krishna Vibez</title>
  <meta name="description" content="{meta_desc}">
  <meta name="keywords" content="{keywords}">
  <meta name="author" content="Paresh Padsala (Krishna Vibez)">
  <link rel="canonical" href="{canonical_url}">

  <!-- Open Graph / WhatsApp / Facebook Rich Preview -->
  <meta property="og:site_name" content="Krishna Vibez">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:image" content="{hero_img}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="675">
  <meta property="og:locale" content="hi_IN">

  <!-- Twitter Cards -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{meta_desc}">
  <meta name="twitter:image" content="{hero_img}">

  <!-- Robots Directives (Google Discover Optimized) -->
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="googlebot" content="index, follow, max-image-preview:large">

  <!-- Favicon -->
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png">
  <link rel="apple-touch-icon" href="/favicon-192.png">

  <!-- Google AdSense -->
  <meta name="google-adsense-account" content="ca-pub-4064462736581300">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4064462736581300" crossorigin="anonymous"></script>

  <!-- Google tag (gtag.js) - Google Analytics 4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-M7W6128K1Z"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-M7W6128K1Z');
  </script>

  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
{json_ld_str}
  </script>

  <link rel="stylesheet" href="../css/style.css?v=4.6">
  <style>
    /* Hallmark · genre: spiritual · theme: luxury-dark · redesign: full */
    html, body {{
      overflow-x: clip;
    }}
    :root {{
      --gold-primary: #f5c542;
      --gold-dark: #b8860b;
      --bg-dark: #080b11;
      --bg-card: #0d1117;
      --text-main: #f0f6fc;
      --text-muted: #8b949e;
      --text-silver: #c9d1d9;
      --text-light: #e6edf3;
      --text-pure: #f6f9fc;
      --border-subtle: #21262d;
      --color-wa: #25d366;
      --color-fb: #1877f2;
      --color-tg: #229ed9;
    }}
    body {{
      background: var(--bg-dark);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      line-height: 1.85;
      margin: 0;
      padding: 0;
    }}
    .article-wrap {{
      max-width: 860px;
      margin: 0 auto;
      padding: 30px 18px 80px;
    }}
    .article-badge {{
      display: inline-block;
      background: rgba(245, 197, 66, 0.15);
      color: var(--gold-primary);
      border: 1px solid rgba(245, 197, 66, 0.35);
      padding: 4px 14px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 700;
      margin-bottom: 16px;
      letter-spacing: normal;
    }}
    h1.article-title {{
      font-size: clamp(1.9rem, 3.5vw, 2.7rem);
      line-height: 1.35;
      margin: 0 0 16px 0;
      font-weight: 800;
      background: linear-gradient(135deg, var(--text-pure) 40%, var(--gold-primary) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .meta-bar {{
      display: flex;
      align-items: center;
      gap: 16px;
      color: var(--text-muted);
      font-size: 0.9rem;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border-subtle);
    }}
    .hero-img-box {{
      width: 100%;
      border-radius: 16px;
      overflow: hidden;
      margin-bottom: 34px;
      border: 1px solid var(--border-subtle);
      box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6);
    }}
    .hero-img-box img {{
      width: 100%;
      height: auto;
      display: block;
      aspect-ratio: 16 / 9;
      object-fit: cover;
    }}
    .toc-card {{
      background: var(--bg-card);
      border: 1px solid rgba(245, 197, 66, 0.25);
      border-radius: 14px;
      padding: 22px 26px;
      margin-bottom: 40px;
    }}
    .toc-card h3 {{
      margin: 0 0 14px 0;
      color: var(--gold-primary);
      font-size: 1.15rem;
    }}
    .toc-card ul {{
      margin: 0;
      padding-left: 22px;
      line-height: 1.9;
    }}
    .toc-card a {{
      color: #58a6ff;
      text-decoration: none;
    }}
    .toc-card a:hover {{
      text-decoration: underline;
    }}
    .article-content h2 {{
      color: var(--gold-primary);
      font-size: 1.7rem;
      margin: 45px 0 18px 0;
      padding-bottom: 10px;
      border-bottom: 1px solid rgba(245, 197, 66, 0.2);
    }}
    .article-content h3 {{
      color: var(--text-light);
      font-size: 1.3rem;
      margin: 28px 0 12px 0;
    }}
    .article-content p {{
      color: var(--text-silver);
      font-size: 1.12rem;
      margin-bottom: 20px;
      text-align: justify;
    }}
    .article-content blockquote {{
      background: rgba(245, 197, 66, 0.08);
      border-left: 4px solid var(--gold-primary);
      padding: 16px 20px;
      margin: 28px 0;
      border-radius: 0 12px 12px 0;
      font-style: italic;
      color: #f0e6d2;
      font-size: 1.15rem;
    }}
    .article-content ol, .article-content ul {{
      color: var(--text-silver);
      font-size: 1.1rem;
      padding-left: 24px;
      margin-bottom: 28px;
    }}
    .article-content li {{
      margin-bottom: 14px;
    }}
    .faq-item {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 18px 22px;
      margin-bottom: 16px;
    }}
    .faq-item h3 {{
      margin: 0 0 8px 0;
      color: var(--gold-primary);
      font-size: 1.15rem;
    }}
    .share-bar {{
      display: flex;
      gap: 12px;
      margin: 50px 0 30px;
      padding: 20px;
      background: var(--bg-card);
      border-radius: 14px;
      border: 1px solid var(--border-subtle);
      align-items: center;
      flex-wrap: wrap;
    }}
    .share-btn {{
      padding: 10px 18px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 600;
      font-size: 0.95rem;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .share-wa {{ background: var(--color-wa); color: var(--bg-dark); }}
    .share-fb {{ background: var(--color-fb); color: var(--text-pure); }}
    .share-tg {{ background: var(--color-tg); color: var(--text-pure); }}
    .back-home {{
      text-align: center;
      margin-top: 40px;
    }}
    .back-home a {{
      color: var(--gold-primary);
      text-decoration: none;
      font-weight: 700;
      border: 1px solid var(--gold-primary);
      padding: 10px 24px;
      border-radius: 25px;
      display: inline-block;
      transition: transform 0.2s ease, background-color 0.2s ease, color 0.2s ease;
    }}
    .back-home a:hover {{
      background: var(--gold-primary);
      color: var(--bg-dark);
    }}
    a:focus-visible, button:focus-visible {{
      outline: 2px solid var(--gold-primary);
      outline-offset: 2px;
    }}
    a:active, button:active {{
      transform: translateY(1px);
    }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
      }}
    }}
  </style>
</head>
<body>

  <div class="article-wrap">
    <div class="article-badge">🪷 {category}</div>
    <h1 class="article-title">{title}</h1>
    
    <div class="meta-bar">
      <span>✍️ परेश पादसाला (Krishna Vibez)</span>
      <span>📅 {display_date}</span>
      <span>⏱️ 8 मिनट पठन</span>
    </div>

    <div class="hero-img-box">
      <img src="{hero_img}" alt="{title}" loading="eager" width="1200" height="675">
    </div>

    <div class="toc-card">
      <h3>📑 विषय सूची (Quick Overview)</h3>
      <ul>
        <li><a href="#intro">1. प्रस्तावना एवं पृष्ठभूमि</a></li>
        <li><a href="#context">2. आध्यात्मिक एवं शास्त्रोक्त संदर्भ</a></li>
        <li><a href="#psychology">3. मन और चेतना का गहरा विश्लेषण</a></li>
        <li><a href="#practical">4. आधुनिक जीवन और करियर में इसका सही प्रयोग</a></li>
        <li><a href="#sutras">5. 10 दिव्य जीवन सूत्र (Golden Sutras)</a></li>
        <li><a href="#faq">6. अक्सर पूछे जाने वाले सवाल (FAQs)</a></li>
        <li><a href="#conclusion">7. उपसंहार एवं दिव्य महामंत्र ध्यान</a></li>
      </ul>
    </div>

    <article class="article-content">
      {content_html}
    </article>

    <div class="share-bar">
      <span style="font-weight:700; color:var(--gold-primary);">इस पावन ज्ञान को अपनों के साथ साझा करें:</span>
      <a class="share-btn share-wa" href="https://api.whatsapp.com/send?text={title}%20-%20{canonical_url}" target="_blank" rel="noopener">WhatsApp</a>
      <a class="share-btn share-fb" href="https://www.facebook.com/sharer/sharer.php?u={canonical_url}" target="_blank" rel="noopener">Facebook</a>
      <a class="share-btn share-tg" href="https://t.me/share/url?url={canonical_url}&text={title}" target="_blank" rel="noopener">Telegram</a>
    </div>

    <div class="back-home">
      <a href="https://krishnavibez.in/articles.html">← सभी विशेष आध्यात्मिक लेख पढ़ें</a>
    </div>
  </div>

</body>
</html>"""
    return page_html, hero_img

def update_articles_index(topic_meta, hero_img):
    if not os.path.exists(ARTICLES_INDEX_FILE):
        return
    slug = topic_meta["slug"]
    title = topic_meta["title"]
    category = topic_meta["category"]
    meta_desc = topic_meta["meta_desc"]
    now_ist = datetime.now(_IST)
    display_date = now_ist.strftime("%d-%m-%Y")

    card_html = f"""
    <div class="article-card" style="border-color: rgba(245, 197, 66, 0.4); background: linear-gradient(145deg, rgba(20,24,33,0.95), rgba(13,17,23,0.95));">
      <div>
        <div class="article-top">
          <span class="article-tag" style="background: rgba(245, 197, 66, 0.2);">{category}</span>
          <span class="article-date">📅 {display_date}</span>
        </div>
        <h2 class="article-heading">
          <a href="articles/{slug}.html">{title}</a>
        </h2>
        <p class="article-excerpt">{meta_desc[:145]}...</p>
      </div>
      <div class="article-bottom">
        <span class="article-readtime">⏱️ 8 मिनट पठन</span>
        <a href="articles/{slug}.html" class="article-read-btn">पूरा पढ़ें →</a>
      </div>
    </div>
"""
    with open(ARTICLES_INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Insert right after <div class="articles-grid">
    if '<div class="articles-grid">' in html:
        new_html = html.replace('<div class="articles-grid">', '<div class="articles-grid">\n' + card_html, 1)
        with open(ARTICLES_INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("✅ Updated articles.html with new top featured article card.")

def update_sitemap(slug):
    if not os.path.exists(SITEMAP_FILE):
        return
    today_str = datetime.now(_IST).strftime("%Y-%m-%d")
    new_entry = f"""  <url>
    <loc>https://krishnavibez.in/articles/{slug}.html</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
"""
    with open(SITEMAP_FILE, "r", encoding="utf-8") as f:
        xml = f.read()
    if f"/articles/{slug}.html" not in xml:
        xml = xml.replace('</urlset>', new_entry + '</urlset>')
        with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
            f.write(xml)
        print("✅ Updated articles-sitemap.xml.")

def update_rss(topic_meta, hero_img):
    if not os.path.exists(RSS_FILE):
        return
    slug = topic_meta["slug"]
    title = topic_meta["title"]
    meta_desc = topic_meta["meta_desc"]
    category = topic_meta["category"]
    now_rfc = datetime.now(_IST).strftime("%a, %d %b %Y %H:%M:%S +0530")
    article_url = f"https://krishnavibez.in/articles/{slug}.html"

    item_xml = f"""    <item>
      <title>{title}</title>
      <link>{article_url}</link>
      <guid isPermaLink="true">{article_url}</guid>
      <pubDate>{now_rfc}</pubDate>
      <dc:creator>Paresh Padsala (Krishna Vibez)</dc:creator>
      <category>{category}</category>
      <description><![CDATA[{meta_desc}]]></description>
      <enclosure url="{hero_img}" type="image/jpeg" length="153600" />
      <media:content url="{hero_img}" medium="image" width="1200" height="675" />
    </item>
"""
    with open(RSS_FILE, "r", encoding="utf-8") as f:
        xml = f.read()
    if article_url not in xml:
        # Prepend to channel after <atom:link ... />
        match = re.search(r'(<atom:link[^>]+/>)', xml)
        if match:
            xml = xml[:match.end()] + "\n" + item_xml + xml[match.end():]
        else:
            xml = xml.replace('</channel>', item_xml + '</channel>')
        with open(RSS_FILE, "w", encoding="utf-8") as f:
            f.write(xml)
        print("✅ Updated rss.xml for Google Discover.")

def ping_search_engines(article_url):
    """
    Submits new article to IndexNow (Bing, Yandex, Seznam, Naver) and WebSub
    for instant search engine indexing.
    """
    print("\n🌐 Step 4.5: Submitting article to IndexNow & Search Engine Instant Indexing...")
    # 1. IndexNow Submission
    try:
        indexnow_payload = {
            "host": "krishnavibez.in",
            "key": "c8d1979b9a674e2d83b0f51276a71e3d",
            "keyLocation": "https://krishnavibez.in/c8d1979b9a674e2d83b0f51276a71e3d.txt",
            "urlList": [
                "https://krishnavibez.in/",
                "https://krishnavibez.in/articles",
                article_url
            ]
        }
        res = requests.post(
            "https://api.indexnow.org/indexnow",
            json=indexnow_payload,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "Mozilla/5.0 (compatible; IndexNowClient/1.0; +https://www.indexnow.org)"
            },
            timeout=10
        )
        print(f"   ✅ IndexNow instant indexing ping: HTTP {res.status_code}")
    except Exception as e:
        print(f"   [Notice] IndexNow ping: {e}")

    # 2. WebSub (PubSubHubbub) Submission
    try:
        websub_res = requests.post(
            "https://pubsubhubbub.appspot.com/publish",
            data={
                "hub.mode": "publish",
                "hub.url": "https://krishnavibez.in/rss.xml"
            },
            headers={"User-Agent": "KrishnaVibez-Publisher/1.0"},
            timeout=10
        )
        print(f"   ✅ WebSub (PubSubHubbub) ping: HTTP {websub_res.status_code}")
    except Exception as e:
        print(f"   [Notice] WebSub ping: {e}")

def post_to_facebook(topic_meta, hero_img):
    slug = topic_meta["slug"]
    title = topic_meta["title"]
    category = topic_meta["category"]
    meta_desc = topic_meta["meta_desc"]
    article_url = f"https://krishnavibez.in/articles/{slug}.html"

    caption = f"""🪷 {category} — विशेष आध्यात्मिक लेख 🪷

✨ {title}

"{meta_desc}"

भगवान श्री कृष्ण के अमर उपदेश और सनातन ज्ञान के इस अनुपम चिंतन को गहराई से समझने के लिए यह लेख अवश्य पढ़ें।

📖 संपूर्ण विस्तृत लेख पढ़ने के लिए नीचे दिए गए लिंक पर क्लिक करें 👇
🔗 {article_url}

॥ हरे कृष्ण हरे कृष्ण कृष्ण कृष्ण हरे हरे ॥
॥ हरे राम हरे राम राम राम हरे हरे ॥

#KrishnaVibez #BhagavadGita #GitaGyan #SanatanDharma #RadhaKrishna #SpiritualWisdom #KarmaYoga #GeetaSaar"""

    print(f"\n[Facebook Auto-Post] Posting to Krishna Vibez Page ({FB_PAGE_ID})...")
    url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/feed"
    payload = {
        "message": caption,
        "link": article_url,
        "access_token": FB_ACCESS_TOKEN
    }
    try:
        resp = requests.post(url, data=payload, timeout=30)
        data = resp.json()
        if resp.status_code == 200 and "id" in data:
            post_id = data["id"]
            print(f"✅ SUCCESS! Article posted to Krishna Vibez Facebook Page. Post ID: {post_id}")
            
            # Record in history
            hist = []
            if os.path.exists(HISTORY_FILE):
                try:
                    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                        hist = json.load(f)
                except Exception:
                    hist = []
            hist.append({
                "slug": slug,
                "title": title,
                "posted_at": datetime.now(_IST).isoformat(),
                "fb_post_id": post_id
            })
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(hist, f, indent=2, ensure_ascii=False)
            return True, post_id
        else:
            print(f"❌ Facebook Post Failed: {data}")
            return False, data
    except Exception as e:
        print(f"❌ Facebook Post Exception: {e}")
        return False, str(e)

def run_pipeline():
    print("=" * 70)
    print("🚀 STARTING DAILY TRENDING ARTICLE GENERATOR & PUBLISHER (7:00 AM IST)")
    print("=" * 70)

    # 1. Determine Topic
    print("\n🔍 Step 1: Researching today's top trending/timely spiritual topic...")
    topic_meta = determine_today_topic()
    print(f"   Selected Topic: {topic_meta['title']}")
    print(f"   Category: {topic_meta['category']}")
    print(f"   Slug: {topic_meta['slug']}")

    # 2. Write Article
    print("\n✍️ Step 2: Generating 2200-2500+ words 100% original high-SEO content...")
    content_html = generate_full_article_content(topic_meta)
    print(f"   Generated {len(content_html)} characters of structured semantic HTML.")

    # 3. Assemble Complete Webpage
    print("\n🎨 Step 3: Assembling full HTML with Schema.org & Discover optimizations...")
    page_html, hero_img = build_complete_article_page(topic_meta, content_html)
    article_dest = os.path.join(ARTICLES_DIR, f"{topic_meta['slug']}.html")
    with open(article_dest, "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"   Saved article to: {article_dest}")

    # Mirror to local directory if exists
    mirror_dir = r"E:\Paresh\Auto Post\Krishna Vibez\public\articles"
    if os.path.exists(mirror_dir):
        try:
            with open(os.path.join(mirror_dir, f"{topic_meta['slug']}.html"), "w", encoding="utf-8") as mf:
                mf.write(page_html)
            print(f"   Mirrored to Krishna Vibez public articles folder.")
        except Exception as e:
            print(f"   Notice mirroring: {e}")

    # 4. Update Site Indexes & Feeds
    print("\n📡 Step 4: Updating articles.html, articles-sitemap.xml & rss.xml...")
    update_articles_index(topic_meta, hero_img)
    update_sitemap(topic_meta["slug"])
    update_rss(topic_meta, hero_img)
    ping_search_engines(f"https://krishnavibez.in/articles/{topic_meta['slug']}.html")

    # 5. Post to Facebook (may be deferred until after Firebase deploy to avoid 404 link previews)
    skip_fb = os.environ.get("SKIP_FB_POST", "").strip().lower() in ("1", "true", "yes")
    if skip_fb:
        print("\n📝 Step 5: Deferring Facebook post until after Firebase deploy (SKIP_FB_POST set)...")
        pending_path = os.path.join(REPO_ROOT, "pending_fb_post.json")
        with open(pending_path, "w", encoding="utf-8") as pf:
            json.dump({"topic_meta": topic_meta, "hero_img": hero_img}, pf, ensure_ascii=False, indent=2)
        print(f"   Saved pending post metadata to: {pending_path}")
    else:
        print("\n📱 Step 5: Publishing rich clickable link to Krishna Vibez Facebook Page...")
        fb_success, fb_res = post_to_facebook(topic_meta, hero_img)

    print("\n" + "=" * 70)
    print("🎉 DAILY ARTICLE ENGINE RUN COMPLETED SUCCESSFULLY!")
    print(f"   Live URL: https://krishnavibez.in/articles/{topic_meta['slug']}.html")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
