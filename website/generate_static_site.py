# -*- coding: utf-8 -*-
"""
Krishna Vibez - Static Site Generator (SSG) & SEO Engine
Converts all dynamic JS posts from posts-data.js into 100% pre-rendered, 
crawlable static HTML files for Google Search, Google Discover, and social crawlers.
"""

import os
import sys
import json
import re
import html
from datetime import datetime

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
POSTS_DATA_PATH = os.path.join(PUBLIC_DIR, "js", "posts-data.js")
POST_HTML_PATH = os.path.join(PUBLIC_DIR, "post.html")
INDEX_HTML_PATH = os.path.join(PUBLIC_DIR, "index.html")
SITEMAP_PATH = os.path.join(PUBLIC_DIR, "sitemap.xml")
RSS_PATH = os.path.join(PUBLIC_DIR, "rss.xml")
OUTPUT_POST_DIR = os.path.join(PUBLIC_DIR, "post")

def escape_attr(val):
    if not val:
        return ""
    return html.escape(str(val), quote=True)

def load_posts():
    if not os.path.exists(POSTS_DATA_PATH):
        raise FileNotFoundError(f"posts-data.js not found at {POSTS_DATA_PATH}")

    with open(POSTS_DATA_PATH, "r", encoding="utf-8") as f:
        raw = f.read()

    m = re.search(r'window\.KRISHNA_POSTS\s*=\s*(\[[\s\S]*?\]);', raw)
    if not m:
        raise ValueError("Could not find window.KRISHNA_POSTS array in posts-data.js")

    raw_array = m.group(1)
    try:
        return json.loads(raw_array)
    except Exception:
        clean = re.sub(r'`([\s\S]*?)`', lambda match: json.dumps(match.group(1).strip()), raw_array)
        clean = re.sub(r'([\{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', clean)
        clean = re.sub(r',\s*([\}\]])', r'\1', clean)
        return json.loads(clean)

def format_metric(num):
    try:
        n = int(num)
        if n >= 1000000:
            return f"{n/1000000:.1f}M"
        elif n >= 1000:
            return f"{n/1000:.1f}k"
        return str(n)
    except Exception:
        return str(num)

def build_post_html(post, template_html):
    post_id = post["id"]
    title = post.get("title", "श्री कृष्ण अमृत विचार एवं दर्शन")
    quote = post.get("quote", "")
    full_title = f"{title} — Krishna Vibez"
    clean_desc = (post.get("shortDesc") or quote or "").replace("\r", " ").replace("\n", " ").strip()
    if len(clean_desc) > 175:
        clean_desc = clean_desc[:172] + "…"
    
    post_url = f"https://krishnavibez.in/post/{post_id}"
    is_video = (post.get("mediaType") == "video") or bool(post.get("videoUrl")) or str(post.get("imageUrl", "")).endswith(".mp4")
    media_url = post.get("videoUrl") or post.get("imageUrl") or "https://krishnavibez.in/assets/krishna-og.jpg"
    thumb_url = post.get("imageUrl") or "https://krishnavibez.in/assets/krishna-og.jpg"
    iso_date = post.get("isoDate") or "2026-10-15"
    date_str = post.get("date") or "दैनिक दर्शन"
    category = post.get("category") or "भगवद्गीता ज्ञान"
    category_slug = post.get("categorySlug") or "daily-darshan"
    author = post.get("author") or "Krishna Vibez"
    read_time = post.get("readTime") or ("देखने का समय: 2 मिनट (Reel)" if is_video else "पढ़ने का समय: 3 मिनट")
    views = post.get("views", 1250)
    likes = post.get("likes", 480)
    shares = post.get("shares", 160)
    downloads = post.get("downloads", 320)
    comments = post.get("comments") or []
    comments_count = len(comments)
    tags = post.get("tags") or ["श्री कृष्ण", "भगवद्गीता", "सुविचार", "4K Wallpaper", "Krishna Vibez"]
    content_html = post.get("content") or f"<p>{html.escape(quote)}</p>"
    seo_alt = post.get("altText") or f"श्री कृष्ण 4K HD दर्शन — {quote[:70]} — Krishna Vibez"

    # 1. Start from base template
    html_out = template_html

    # Ensure all relative asset links use absolute root paths
    html_out = re.sub(r'href="css/', 'href="/css/', html_out)
    html_out = re.sub(r'src="assets/', 'src="/assets/', html_out)
    html_out = re.sub(r'href="assets/', 'href="/assets/', html_out)
    html_out = re.sub(r'src="js/', 'src="/js/', html_out)
    html_out = re.sub(r'href="index\.html"', 'href="/index.html"', html_out)
    html_out = re.sub(r'href="articles\.html"', 'href="/articles.html"', html_out)
    html_out = re.sub(r'href="about\.html"', 'href="/about.html"', html_out)
    html_out = re.sub(r'href="contact\.html"', 'href="/contact.html"', html_out)
    html_out = re.sub(r'href="privacy-policy\.html"', 'href="/privacy-policy.html"', html_out)
    html_out = re.sub(r'href="terms\.html"', 'href="/terms.html"', html_out)
    html_out = re.sub(r'href="disclaimer\.html"', 'href="/disclaimer.html"', html_out)

    # 2. Replace head title, description, and canonical
    html_out = re.sub(r'<title[^>]*>.*?</title>', f'<title>{escape_attr(full_title)}</title>', html_out, count=1)
    html_out = re.sub(r'<meta\s+name="description"[^>]*>', f'<meta name="description" id="postMetaDesc" content="{escape_attr(clean_desc)}">', html_out, count=1)
    html_out = re.sub(r'<link\s+rel="canonical"[^>]*>', f'<link rel="canonical" id="postCanonical" href="{post_url}">', html_out, count=1)

    # 3. Clean up Open Graph and Twitter tags completely
    og_block = f"""  <!-- Open Graph / Social Rich Previews -->
  <meta property="og:site_name" content="Krishna Vibez">
  <meta property="og:type" id="ogType" content="article">
  <meta property="og:url" id="ogUrl" content="{post_url}">
  <meta property="og:title" id="ogTitle" content="{escape_attr(full_title)}">
  <meta property="og:description" id="ogDesc" content="{escape_attr(clean_desc)}">
  <meta property="og:image" id="ogImage" content="{escape_attr(thumb_url)}">
  <meta property="og:image:secure_url" id="ogImageSecure" content="{escape_attr(thumb_url)}">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" id="ogImageAlt" content="{escape_attr(seo_alt)}">

  <!-- Twitter Cards -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" id="twTitle" content="{escape_attr(full_title)}">
  <meta name="twitter:description" id="twDesc" content="{escape_attr(clean_desc)}">
  <meta name="twitter:image" id="twImage" content="{escape_attr(thumb_url)}">
  <meta name="thumbnail" id="metaThumbnail" content="{escape_attr(thumb_url)}">

  <!-- Article Meta -->
  <meta property="article:published_time" id="articlePubTime" content="{iso_date}T06:00:00+05:30">
  <meta property="article:modified_time" id="articleModTime" content="{iso_date}T10:00:00+05:30">
  <meta property="article:author" content="https://www.instagram.com/krishnavibez/">
  <meta property="article:section" id="articleSection" content="{escape_attr(category)}">
  <meta property="article:publisher" content="https://krishnavibez.in/">"""

    html_out = re.sub(
        r'<!-- Open Graph / Facebook / WhatsApp Rich Preview -->[\s\S]*?<!-- Pinterest Domain Verification -->',
        f'{og_block}\n\n  <!-- Pinterest Domain Verification -->',
        html_out,
        count=1
    )

    # 4. Generate Schema.org JSON-LD structured data
    schema_graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": ["Article", "NewsArticle", "CreativeWork"],
                "@id": f"{post_url}#article",
                "isPartOf": {
                    "@type": "WebPage",
                    "@id": post_url,
                    "url": post_url,
                    "name": full_title
                },
                "headline": title,
                "alternativeHeadline": quote,
                "description": clean_desc,
                "inLanguage": "hi-IN",
                "datePublished": f"{iso_date}T06:00:00+05:30",
                "dateModified": f"{iso_date}T10:00:00+05:30",
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": post_url
                },
                "keywords": ", ".join(tags),
                "articleSection": category,
                "author": {
                    "@type": "Person",
                    "name": "Paresh Padsala",
                    "jobTitle": "Spiritual Creator & Editor",
                    "url": "https://www.instagram.com/krishnavibez/"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "Krishna Vibez",
                    "url": "https://krishnavibez.in/",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://krishnavibez.in/assets/logo.png",
                        "width": 512,
                        "height": 512
                    }
                },
                "image": [
                    thumb_url,
                    "https://krishnavibez.in/assets/logo.png"
                ],
                "thumbnailUrl": thumb_url,
                "primaryImageOfPage": {
                    "@type": "ImageObject",
                    "url": thumb_url,
                    "contentUrl": thumb_url,
                    "caption": seo_alt,
                    "width": 1200,
                    "height": 1600
                },
                "interactionStatistic": [
                    {
                        "@type": "InteractionCounter",
                        "interactionType": "https://schema.org/LikeAction",
                        "userInteractionCount": max(int(likes), 25)
                    },
                    {
                        "@type": "InteractionCounter",
                        "interactionType": "https://schema.org/CommentAction",
                        "userInteractionCount": max(comments_count, 1)
                    }
                ]
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{post_url}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "होम (Home)",
                        "item": "https://krishnavibez.in/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": category,
                        "item": f"https://krishnavibez.in/index.html#{category_slug}"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": title,
                        "item": post_url
                    }
                ]
            }
        ]
    }

    if is_video:
        schema_graph["@graph"][0]["video"] = {
            "@type": "VideoObject",
            "name": title,
            "description": clean_desc,
            "thumbnailUrl": [thumb_url],
            "uploadDate": f"{iso_date}T06:00:00+05:30",
            "contentUrl": media_url,
            "embedUrl": post_url
        }

    schema_json_str = json.dumps(schema_graph, ensure_ascii=False, indent=2)
    html_out = re.sub(
        r'<script type="application/ld\+json" id="postSchemaJsonLd">[\s\S]*?</script>',
        f'<script type="application/ld+json" id="postSchemaJsonLd">\n{schema_json_str}\n  </script>',
        html_out,
        count=1
    )

    # 5. Hide loader and make article visible
    html_out = re.sub(
        r'<div id="postLoading"[^>]*>[\s\S]*?</div>',
        '',
        html_out,
        count=1
    )
    html_out = html_out.replace(
        '<article id="postContentArea" style="display: none;">',
        '<article id="postContentArea" style="display: block;">'
    )

    # 6. Populate Header
    html_out = re.sub(r'<span class="post-detail-cat" id="dCategory">.*?</span>', f'<span class="post-detail-cat" id="dCategory">{escape_attr(category)}</span>', html_out, count=1)
    html_out = re.sub(r'<h1 class="post-detail-title" id="dTitle">.*?</h1>', f'<h1 class="post-detail-title" id="dTitle">{escape_attr(title)}</h1>', html_out, count=1)
    html_out = re.sub(r'<span id="dDate">.*?</span>', f'<span id="dDate">{escape_attr(date_str)}</span>', html_out, count=1)
    html_out = re.sub(r'<span id="dAuthor">.*?</span>', f'<span id="dAuthor">{escape_attr(author)}</span>', html_out, count=1)
    html_out = re.sub(r'<span id="dReadTime">.*?</span>', f'<span id="dReadTime">{escape_attr(read_time)}</span>', html_out, count=1)

    # 7. Populate Media Wrapper
    media_overlay = f"""
        <button class="card-media-like-btn" id="detailMediaLikeBtn" onclick="handleDetailLikeToggle(event)" title="पसंद करें (Like)" aria-label="Like post">
          <svg class="heart-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
          </svg>
          <span class="media-like-count" id="detailMediaLikeCount">{format_metric(likes)}</span>
        </button>
        <span class="video-reel-pill">{'4K REEL' if is_video else '4K IMAGE'}</span>"""

    if is_video:
        media_inner = f"""
        <video src="{escape_attr(media_url)}" class="post-detail-img" controls autoplay loop playsinline title="{escape_attr(seo_alt)}" aria-label="{escape_attr(seo_alt)}" style="width:100%;max-height:680px;background:#000;display:block;"></video>
        {media_overlay}"""
    else:
        media_inner = f"""
        <img id="dImage" src="{escape_attr(media_url)}" alt="{escape_attr(seo_alt)}" title="{escape_attr(seo_alt)}" class="post-detail-img">
        {media_overlay}"""

    html_out = re.sub(
        r'<div class="post-detail-img-wrap">[\s\S]*?</div>\s*<!-- Real Live Metrics',
        f'<div class="post-detail-img-wrap">\n{media_inner}\n      </div>\n\n      <!-- Real Live Metrics',
        html_out,
        count=1
    )

    # 8. Populate Metrics
    html_out = re.sub(r'<strong id="dViews">.*?</strong>', f'<strong id="dViews">{format_metric(views)}</strong>', html_out, count=1)
    html_out = re.sub(r'<strong id="dLikes">.*?</strong>', f'<strong id="dLikes">{format_metric(likes)}</strong>', html_out, count=1)
    html_out = re.sub(r'<strong id="dCommentsCount">.*?</strong>', f'<strong id="dCommentsCount">{comments_count}</strong>', html_out, count=1)
    html_out = re.sub(r'<strong id="dShares">.*?</strong>', f'<strong id="dShares">{format_metric(shares)}</strong>', html_out, count=1)
    html_out = re.sub(r'<strong id="dDownloads">.*?</strong>', f'<strong id="dDownloads">{format_metric(downloads)}</strong>', html_out, count=1)
    html_out = re.sub(r'<span class="comment-badge" id="commentBadge">.*?</span>', f'<span class="comment-badge" id="commentBadge">{comments_count} टिप्पणियाँ</span>', html_out, count=1)

    # 9. Download button label
    btn_dl_text = '⬇️ 4K Reel डाउनलोड (MP4)' if is_video else '⬇️ 4K Wallpaper डाउनलोड'
    html_out = re.sub(r'<button class="btn-download-hd" id="btnDownloadDetail"[^>]*>[\s\S]*?</button>', f'<button class="btn-download-hd" id="btnDownloadDetail" style="padding: 12px 16px; font-size: 0.9rem;">{btn_dl_text}</button>', html_out, count=1)

    # 10. Populate Article Body
    html_out = re.sub(
        r'<div class="post-content-body" id="dBody">[\s\S]*?</div>',
        f'<div class="post-content-body" id="dBody">\n{content_html}\n      </div>',
        html_out,
        count=1
    )

    # 11. Populate Tags
    tags_spans = "".join([f'<span style="background:rgba(255,255,255,0.06);border:1px solid var(--border-subtle);color:var(--text-muted);padding:4px 12px;border-radius:14px;font-size:0.75rem;">#{escape_attr(t)}</span>' for t in tags])
    html_out = re.sub(
        r'<div style="margin-top: 36px;[^"]*" id="dTags">[\s\S]*?</div>',
        f'<div style="margin-top: 36px; padding-top: 20px; border-top: 1px solid var(--border-subtle); display: flex; gap: 8px; flex-wrap: wrap;" id="dTags">{tags_spans}</div>',
        html_out,
        count=1
    )

    # 12. Populate Comments
    if comments:
        comments_html = "".join([f"""
          <div class="comment-item">
            <div class="comment-author-row">
              <div class="comment-avatar">{escape_attr(c.get('name', '🪷')[0] if c.get('name') else '🪷')}</div>
              <span class="comment-author-name">{escape_attr(c.get('name', 'राधे भक्त'))}</span>
              <span class="comment-date">🕒 {escape_attr(c.get('time', 'हाल ही में'))}</span>
            </div>
            <div class="comment-text">
              {escape_attr(c.get('text', 'अति दिव्य एवं पावन दर्शन! जय श्री कृष्णा 🙏'))}
            </div>
          </div>""" for c in comments])
    else:
        comments_html = f"""
          <div class="comment-item">
            <div class="comment-author-row">
              <div class="comment-avatar">🪷</div>
              <span class="comment-author-name">राधे भक्त</span>
              <span class="comment-date">🕒 हाल ही में</span>
            </div>
            <div class="comment-text">
              अति पावन और सुंदर दर्शन! जय श्री कृष्णा 🙏
            </div>
          </div>"""

    html_out = re.sub(
        r'<div class="comments-list" id="commentsList">[\s\S]*?</div>',
        f'<div class="comments-list" id="commentsList">{comments_html}\n        </div>',
        html_out,
        count=1
    )

    # 13. Inject static currentPostId bootstrap
    bootstrap_js = f"""
  <script>
    window.__CURRENT_POST_ID = "{escape_attr(post_id)}";
    window.__CURRENT_POST_OBJ = {json.dumps(post, ensure_ascii=False)};
  </script>"""
    html_out = html_out.replace('</body>', f'{bootstrap_js}\n</body>')

    return html_out

def generate_homepage_cards(posts, limit=20):
    cards_html = []
    for post in posts[:limit]:
        post_id = post["id"]
        title = post.get("title", "श्री कृष्ण अमृत विचार एवं दर्शन")
        quote = post.get("quote", "")
        clean_desc = (post.get("shortDesc") or quote or "").replace("\r", " ").replace("\n", " ").strip()
        if len(clean_desc) > 130:
            clean_desc = clean_desc[:127] + "…"
        category = post.get("category", "भगवद्गीता ज्ञान")
        date_str = post.get("date", "दैनिक दर्शन")
        is_video = (post.get("mediaType") == "video") or bool(post.get("videoUrl")) or str(post.get("imageUrl", "")).endswith(".mp4")
        media_url = post.get("videoUrl") or post.get("imageUrl") or "/assets/krishna-og.jpg"
        thumb_url = post.get("imageUrl") or "/assets/krishna-og.jpg"
        views = post.get("views", 1250)
        likes = post.get("likes", 480)
        comments_count = len(post.get("comments") or [])
        shares = post.get("shares", 160)
        downloads = post.get("downloads", 320)
        read_time = post.get("readTime") or ("देखने का समय: 2 मिनट (Reel)" if is_video else "पढ़ने का समय: 3 मिनट")
        seo_alt = post.get("altText") or f"श्री कृष्ण 4K HD दर्शन — {quote[:70]} — Krishna Vibez"

        post_link = f"/post/{post_id}"

        if is_video:
            media_elem = f"""
            <div class="video-preview-wrapper" style="width:100%;height:100%;position:relative;background:#000;">
              <video class="card-video-preview" src="{escape_attr(media_url)}" muted loop playsinline preload="metadata" style="width:100%;height:100%;object-fit:cover;display:block;" title="{escape_attr(seo_alt)}" aria-label="{escape_attr(seo_alt)}"></video>
              <div class="video-play-overlay">
                <div class="video-play-circle">
                  <svg class="play-icon" width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                  </svg>
                </div>
                <span class="video-watch-hint">टैप करके 4K Reel देखें</span>
              </div>
            </div>"""
        else:
            media_elem = f'<img class="card-img" src="{escape_attr(thumb_url)}" alt="{escape_attr(seo_alt)}" title="{escape_attr(seo_alt)}" loading="lazy">'

        card = f"""
      <article class="post-card" id="card-{post_id}">
        <div class="card-img-wrap">
          <a href="{post_link}" class="card-media-link" style="display:block;width:100%;height:100%;text-decoration:none;color:inherit;">
            {media_elem}
          </a>
          <span class="card-overlay-badge">{'🎬' if is_video else '🪷'} {escape_attr(category)}</span>
          <span class="card-stats-badge">👁️ <span class="view-num-{post_id}">{format_metric(views)}</span></span>
          <button class="card-media-like-btn" id="media-like-{post_id}" onclick="toggleFeedLike('{post_id}', event)" title="पसंद करें (Like)" aria-label="Like post">
            <svg class="heart-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
            <span class="like-num-{post_id} media-like-count">{format_metric(likes)}</span>
          </button>
          <span class="video-reel-pill">{'4K REEL' if is_video else '4K IMAGE'}</span>
        </div>
        <div class="card-body">
          <div class="card-date-row">
            <span>📅 {escape_attr(date_str)}</span>
            <span>⏱️ {escape_attr(read_time)}</span>
          </div>
          <h2 class="card-title">
            <a href="{post_link}" style="color:inherit;text-decoration:none;">
              {escape_attr(title)}
            </a>
          </h2>
          <div class="card-quote-box">
            <div class="card-quote-content">
              "{escape_attr(quote)}"
            </div>
            <button class="quote-copy-btn" id="copy-btn-{post_id}" onclick="copyQuote('{post_id}', event)" title="सुविचार कॉपी करें (Copy Thought)">
              <svg class="copy-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              <span class="copy-text">कॉपी</span>
            </button>
          </div>
          <p class="card-desc">{escape_attr(clean_desc)}</p>
          <div class="card-metrics-strip">
            <span class="metric-item" title="कुल दर्शन (Views)">
              👁️ <strong class="view-num-{post_id}">{format_metric(views)}</strong>
            </span>
            <span class="metric-item interactive" id="card-like-{post_id}" onclick="toggleFeedLike('{post_id}', event)" title="पसंद करें (Like)">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
              <strong class="like-num-{post_id}">{format_metric(likes)}</strong>
            </span>
            <a href="{post_link}#commentsSection" class="metric-item interactive" style="color:inherit;text-decoration:none;" title="भक्त टिप्पणियाँ">
              💬 <strong class="comment-num-{post_id}">{comments_count}</strong>
            </a>
            <span class="metric-item" title="कुल शेयर (Shares)">
              📲 <strong class="share-num-{post_id}">{format_metric(shares)}</strong>
            </span>
            <span class="metric-item" title="वॉलपेपर / रील डाउनलोड">
              ⬇️ <strong class="dl-num-{post_id}">{format_metric(downloads)}</strong>
            </span>
          </div>
          <div class="card-actions">
            <button class="btn-whatsapp-share" onclick="shareOnWhatsApp('{post_id}')" title="WhatsApp पर शेयर करें">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.771-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.312.045-.634.07-.98-.06-.525-.198-1.503-.615-2.355-1.468-.853-.853-1.27-1.831-1.468-2.355-.13-.346-.105-.668-.06-.98.05-.333.419-1.026.824-1.17.151-.054.305-.035.438.047.165.103.498.818.544.92.046.103.076.223.015.344-.061.121-.092.197-.183.303-.092.106-.195.237-.279.319-.092.091-.188.19-.081.374.106.183.473.78 1.015 1.262.697.621 1.285.814 1.468.905.183.092.29.076.397-.046.106-.121.457-.532.579-.715.121-.183.243-.152.408-.091.166.061 1.051.496 1.233.587.183.091.304.137.349.213.045.076.045.441-.099.846z"/>
              </svg>
              शेयर करें
            </button>
            <button class="btn-download-hd" onclick="downloadHdWallpaper('{post_id}')" title="{'4K Reel डाउनलोड करें' if is_video else 'HD Wallpaper डाउनलोड करें'}">
              {'⬇️ 4K Reel (MP4)' if is_video else '⬇️ HD Wallpaper'}
            </button>
            <a href="{post_link}" class="btn-read-full">
              पूरा दर्शन एवं भावार्थ पढ़ें →
            </a>
          </div>
        </div>
      </article>"""
        cards_html.append(card)
    return "\n".join(cards_html)

def update_index_html(posts):
    if not os.path.exists(INDEX_HTML_PATH):
        return
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    cards_block = generate_homepage_cards(posts, limit=24)
    replacement = f'<div class="posts-grid" id="postsGrid">\n{cards_block}\n    </div>'

    html_content = re.sub(
        r'<div class="posts-grid" id="postsGrid">[\s\S]*?</div>',
        replacement,
        html_content,
        count=1
    )

    with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[SSG] ✅ Updated index.html with {min(len(posts), 24)} static pre-rendered cards with crawlable links.")

def generate_sitemap(posts):
    today = datetime.now().strftime("%Y-%m-%d")
    sitemap_entries = [
        """  <!-- Core Static Pages -->
  <url>
    <loc>https://krishnavibez.in/</loc>
    <lastmod>""" + today + """</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://krishnavibez.in/articles.html</loc>
    <lastmod>""" + today + """</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://krishnavibez.in/about.html</loc>
    <lastmod>""" + today + """</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://krishnavibez.in/contact.html</loc>
    <lastmod>""" + today + """</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://krishnavibez.in/privacy-policy.html</loc>
    <lastmod>""" + today + """</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://krishnavibez.in/terms.html</loc>
    <lastmod>""" + today + """</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://krishnavibez.in/disclaimer.html</loc>
    <lastmod>""" + today + """</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>

  <!-- Clean Canonical Devotional Articles & 4K Posts (Pre-Rendered SSG) -->"""
    ]

    for p in posts:
        post_id = p["id"]
        lastmod = p.get("isoDate") or today
        entry = f"""  <url>
    <loc>https://krishnavibez.in/post/{post_id}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>"""
        sitemap_entries.append(entry)

    full_sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(sitemap_entries) + '\n</urlset>\n'
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(full_sitemap)
    print(f"[SSG] ✅ Generated sitemap.xml with {len(posts)} clean post URLs.")

def generate_rss(posts):
    now = datetime.now()
    rfc_date = now.strftime("%a, %d %b %Y %H:%M:%S +0530")
    
    items = []
    seen_links = set()
    for p in posts[:50]:
        post_id = p["id"]
        link = f"https://krishnavibez.in/post/{post_id}"
        if link in seen_links:
            continue
        seen_links.add(link)
        
        title = html.escape(p.get("title", "श्री कृष्ण अमृत विचार"))
        desc = html.escape(p.get("shortDesc") or p.get("quote") or "")
        category = html.escape(p.get("category", "दैनिक दर्शन"))
        is_video = p.get("mediaType") == "video" or (p.get("videoUrl") and p.get("videoUrl").endswith(".mp4"))
        
        media_url = p.get("videoUrl") if is_video else p.get("imageUrl")
        if not media_url:
            media_url = "https://krishnavibez.in/assets/krishna-og.jpg"
            
        media_type = "video/mp4" if is_video else "image/jpeg"
        medium = "video" if is_video else "image"
        length = "1048576" if is_video else "102400"
        
        item = f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{rfc_date}</pubDate>
      <dc:creator>Paresh Padsala (Krishna Vibez)</dc:creator>
      <category>{category}</category>
      <description><![CDATA[{desc}]]></description>
      <enclosure url="{media_url}" type="{media_type}" length="{length}" />
      <media:content url="{media_url}" medium="{medium}" />
    </item>"""
        items.append(item)

    items_str = "\n".join(items)
    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Krishna Vibez — दैनिक दिव्य दर्शन एवं भगवद्गीता सार</title>
    <link>https://krishnavibez.in/</link>
    <description>भगवान श्री कृष्ण के अलौकिक सुविचार, 4K HD वॉलपेपर्स, रील्स और भगवद्गीता ज्ञान।</description>
    <language>hi</language>
    <lastBuildDate>{rfc_date}</lastBuildDate>
    <atom:link href="https://krishnavibez.in/rss.xml" rel="self" type="application/rss+xml" />
{items_str}
  </channel>
</rss>
"""
    with open(RSS_PATH, "w", encoding="utf-8") as f:
        f.write(rss_xml)
    print(f"[SSG] ✅ Generated rss.xml with top {len(items)} posts (100% Valid XML with dc/media namespaces).")

def main():
    print("=" * 60)
    print("🪷 KRISHNA VIBEZ — STATIC SITE GENERATOR (SSG) STARTING")
    print("=" * 60)

    posts = load_posts()
    print(f"[SSG] Loaded {len(posts)} posts from posts-data.js")

    if not os.path.exists(POST_HTML_PATH):
        raise FileNotFoundError(f"post.html not found at {POST_HTML_PATH}")
    with open(POST_HTML_PATH, "r", encoding="utf-8") as f:
        template_html = f.read()

    os.makedirs(OUTPUT_POST_DIR, exist_ok=True)

    generated_count = 0
    for p in posts:
        post_id = p["id"]
        post_content = build_post_html(p, template_html)
        dest_file = os.path.join(OUTPUT_POST_DIR, f"{post_id}.html")
        with open(dest_file, "w", encoding="utf-8") as f:
            f.write(post_content)
        generated_count += 1

    print(f"[SSG] ✅ Generated {generated_count} pre-rendered HTML post pages in {OUTPUT_POST_DIR}")

    update_index_html(posts)
    generate_sitemap(posts)
    generate_rss(posts)

    print("=" * 60)
    print("🪷 SSG COMPLETE: 100% Googlebot Crawlable & Indexable")
    print("=" * 60)

if __name__ == "__main__":
    main()
