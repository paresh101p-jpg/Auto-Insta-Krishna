# -*- coding: utf-8 -*-
"""
Master SSG, Sitemap & RSS Engine for Krishna Vibez
1. Pre-renders all 95 automated posts from posts-data.js into public/post/<id>.html
2. Generates 100% valid XML sitemap.xml with 134 URLs (7 core + 32 articles + 95 posts)
3. Generates 100% valid XML rss.xml with proper XML entity escaping (& -> &amp;)
4. Validates all outputs with xml.etree.ElementTree
"""

import os
import sys
import json
import re
import html
import glob
from datetime import datetime
import xml.etree.ElementTree as ET

BASE_DIR = r"e:\Paresh\Auto Post\Krishna Vibez"
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
POSTS_DATA_PATH = os.path.join(PUBLIC_DIR, "js", "posts-data.js")
POST_TEMPLATE_PATH = os.path.join(PUBLIC_DIR, "post.html")
ARTICLES_DIR = os.path.join(PUBLIC_DIR, "articles")
OUTPUT_POST_DIR = os.path.join(PUBLIC_DIR, "post")
SITEMAP_PATH = os.path.join(PUBLIC_DIR, "sitemap.xml")
RSS_PATH = os.path.join(PUBLIC_DIR, "rss.xml")

def escape_xml(s):
    if not s:
        return ""
    return html.escape(str(s), quote=True)

def load_posts():
    with open(POSTS_DATA_PATH, "r", encoding="utf-8") as f:
        raw = f.read()
    m = re.search(r'window\.KRISHNA_POSTS\s*=\s*(\[[\s\S]*?\]);', raw)
    if not m:
        raise ValueError("Could not find window.KRISHNA_POSTS in posts-data.js")
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
    iso_date = post.get("isoDate") or "2026-11-14"
    date_str = post.get("date") or "दैनिक दर्शन"
    category = post.get("category") or "भगवद्गीता ज्ञान"
    author = post.get("author") or "Krishna Vibez"
    read_time = post.get("readTime") or ("देखने का समय: 2 मिनट (Reel)" if is_video else "पढ़ने का समय: 3 मिनट")
    views = post.get("views", 1250)
    likes = post.get("likes", 480)
    shares = post.get("shares", 160)
    downloads = post.get("downloads", 320)
    comments = post.get("comments") or []
    tags = post.get("tags") or ["श्री कृष्ण", "भगवद्गीता", "सुविचार", "4K Wallpaper", "Krishna Vibez"]
    seo_alt = post.get("altText") or f"श्री कृष्ण 4K HD दर्शन — {quote[:70]} — Krishna Vibez"

    html_out = template_html

    # Fix relative paths to absolute
    html_out = re.sub(r'href="css/', 'href="/css/', html_out)
    html_out = re.sub(r'src="assets/', 'src="/assets/', html_out)
    html_out = re.sub(r'href="assets/', 'href="/assets/', html_out)
    html_out = re.sub(r'src="js/', 'src="/js/', html_out)

    # Replace Title, Description, Canonical
    html_out = re.sub(r'<title[^>]*>.*?</title>', f'<title>{html.escape(full_title)}</title>', html_out, count=1)
    html_out = re.sub(r'<meta\s+name="description"[^>]*>', f'<meta name="description" id="postMetaDesc" content="{html.escape(clean_desc, quote=True)}">', html_out, count=1)
    html_out = re.sub(r'<link\s+rel="canonical"[^>]*>', f'<link rel="canonical" id="postCanonical" href="{post_url}">', html_out, count=1)

    # Social Meta Tags
    og_block = f"""  <!-- Open Graph / Social Rich Previews -->
  <meta property="og:site_name" content="Krishna Vibez">
  <meta property="og:type" id="ogType" content="article">
  <meta property="og:url" id="ogUrl" content="{post_url}">
  <meta property="og:title" id="ogTitle" content="{html.escape(full_title, quote=True)}">
  <meta property="og:description" id="ogDesc" content="{html.escape(clean_desc, quote=True)}">
  <meta property="og:image" id="ogImage" content="{html.escape(thumb_url, quote=True)}">
  <meta property="og:image:secure_url" id="ogImageSecure" content="{html.escape(thumb_url, quote=True)}">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" id="ogImageAlt" content="{html.escape(seo_alt, quote=True)}">

  <!-- Twitter Cards -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" id="twTitle" content="{html.escape(full_title, quote=True)}">
  <meta name="twitter:description" id="twDesc" content="{html.escape(clean_desc, quote=True)}">
  <meta name="twitter:image" id="twImage" content="{html.escape(thumb_url, quote=True)}">
  <meta name="thumbnail" id="metaThumbnail" content="{html.escape(thumb_url, quote=True)}">

  <!-- Article Meta -->
  <meta property="article:published_time" id="articlePubTime" content="{iso_date}T06:00:00+05:30">
  <meta property="article:modified_time" id="articleModTime" content="{iso_date}T10:00:00+05:30">
  <meta property="article:author" content="https://www.instagram.com/krishnavibez/">
  <meta property="article:section" id="articleSection" content="{html.escape(category, quote=True)}">
  <meta property="article:publisher" content="https://krishnavibez.in/">"""

    html_out = re.sub(
        r'<!-- Open Graph / Facebook / WhatsApp Rich Preview -->[\s\S]*?<!-- Pinterest Domain Verification -->',
        f'{og_block}\n\n  <!-- Pinterest Domain Verification -->',
        html_out,
        count=1
    )

    # Schema JSON-LD
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
                "thumbnailUrl": thumb_url
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
                        "item": "https://krishnavibez.in/#feed"
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

    # Remove loading indicator and show article body statically
    html_out = re.sub(r'<div id="postLoading"[^>]*>[\s\S]*?</div>', '', html_out, count=1)
    html_out = html_out.replace('<article id="postContentArea" style="display: none;">', '<article id="postContentArea" style="display: block;">')

    # Populate Header
    html_out = re.sub(r'<span class="post-detail-cat" id="dCategory">.*?</span>', f'<span class="post-detail-cat" id="dCategory">{html.escape(category)}</span>', html_out, count=1)
    html_out = re.sub(r'<h1 class="post-detail-title" id="dTitle">.*?</h1>', f'<h1 class="post-detail-title" id="dTitle">{html.escape(title)}</h1>', html_out, count=1)
    html_out = re.sub(r'<span id="dDate">.*?</span>', f'<span id="dDate">{html.escape(date_str)}</span>', html_out, count=1)
    html_out = re.sub(r'<span id="dAuthor">.*?</span>', f'<span id="dAuthor">{html.escape(author)}</span>', html_out, count=1)
    html_out = re.sub(r'<span id="dReadTime">.*?</span>', f'<span id="dReadTime">{html.escape(read_time)}</span>', html_out, count=1)

    # Populate Media
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
        <video src="{html.escape(media_url, quote=True)}" class="post-detail-img" controls autoplay loop playsinline title="{html.escape(seo_alt, quote=True)}" aria-label="{html.escape(seo_alt, quote=True)}" style="width:100%;max-height:680px;background:#000;display:block;"></video>
        {media_overlay}"""
    else:
        media_inner = f"""
        <img id="dImage" src="{html.escape(media_url, quote=True)}" alt="{html.escape(seo_alt, quote=True)}" title="{html.escape(seo_alt, quote=True)}" class="post-detail-img" loading="eager" decoding="async">
        {media_overlay}"""

    html_out = re.sub(
        r'<div class="post-detail-img-wrap" id="dMediaWrap">[\s\S]*?</div>\s*<!-- Stats Bar -->',
        f'<div class="post-detail-img-wrap" id="dMediaWrap">\n{media_inner}\n      </div>\n      <!-- Stats Bar -->',
        html_out,
        count=1
    )

    # Populate Quote and Explanation Text
    html_out = re.sub(r'<div class="post-detail-quote" id="dQuote">.*?</div>', f'<div class="post-detail-quote" id="dQuote">"{html.escape(quote)}"</div>', html_out, count=1)
    
    # Detailed Explanation
    explanation_html = f"""
    <div class="spiritual-commentary" style="margin-top: 24px; line-height: 1.8; color: var(--text-main); font-size: 1.05rem;">
      <h3 style="color: var(--gold-primary); margin-bottom: 12px; font-size: 1.25rem;">🌸 आध्यात्मिक भावार्थ एवं जीवन सीख</h3>
      <p>{html.escape(clean_desc)}</p>
      <p style="margin-top: 14px;">भगवान श्री कृष्ण हमें स्मरण कराते हैं कि मन की स्थिरता और निष्काम कर्म ही जीवन के हर संकट का सर्वोत्तम समाधान है। जब हम अपने कर्मों को प्रभु चरणों में समर्पित कर देते हैं, तो चित्त से भय और चिंता का स्वतः निवारण हो जाता है।</p>
    </div>
    """
    html_out = re.sub(r'<div class="post-detail-desc" id="dDesc">.*?</div>', f'<div class="post-detail-desc" id="dDesc">{explanation_html}</div>', html_out, count=1)

    # Metrics
    html_out = re.sub(r'<strong id="dViews">.*?</strong>', f'<strong id="dViews">{format_metric(views)}</strong>', html_out, count=1)
    html_out = re.sub(r'<strong id="dLikes">.*?</strong>', f'<strong id="dLikes">{format_metric(likes)}</strong>', html_out, count=1)
    html_out = re.sub(r'<strong id="dShares">.*?</strong>', f'<strong id="dShares">{format_metric(shares)}</strong>', html_out, count=1)
    html_out = re.sub(r'<strong id="dDownloads">.*?</strong>', f'<strong id="dDownloads">{format_metric(downloads)}</strong>', html_out, count=1)

    # Comments
    comments_html = ""
    for c in comments:
        initial = c.get("name", "भ")[0] if c.get("name") else "🪷"
        comments_html += f"""
          <div class="comment-item">
            <div class="comment-author-row">
              <div class="comment-avatar">{html.escape(initial)}</div>
              <span class="comment-author-name">{html.escape(c.get('name', 'कृष्ण भक्त'))}</span>
              <span class="comment-date">🕒 {html.escape(c.get('time', 'हाल ही में'))}</span>
            </div>
            <div class="comment-text">
              {html.escape(c.get('text', ''))}
            </div>
          </div>
        """
    if comments_html:
        html_out = re.sub(r'<div class="comments-list" id="commentsList">[\s\S]*?</div>\s*</div>\s*<!-- Navigation Prev / Next -->', f'<div class="comments-list" id="commentsList">\n{comments_html}\n        </div>\n      </div>\n      <!-- Navigation Prev / Next -->', html_out, count=1)

    return html_out

def main():
    print("=" * 60)
    print("🪷 KRISHNA VIBEZ — MASTER STATIC SITE GENERATOR")
    print("=" * 60)

    # 1. Load posts
    posts = load_posts()
    print(f"Loaded {len(posts)} automated posts from posts-data.js")

    # 2. Load post template
    with open(POST_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_html = f.read()

    # 3. Create public/post directory
    os.makedirs(OUTPUT_POST_DIR, exist_ok=True)

    # 4. Generate all post HTML files
    print("Generating static HTML pages in public/post/...")
    for p in posts:
        post_id = p["id"]
        post_html = build_post_html(p, template_html)
        file_path = os.path.join(OUTPUT_POST_DIR, f"{post_id}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(post_html)
    print(f"✅ Pre-rendered {len(posts)} static post HTML files in public/post/")

    # 5. Get 32 article slugs
    article_files = glob.glob(os.path.join(ARTICLES_DIR, "*.html"))
    article_slugs = [os.path.splitext(os.path.basename(a))[0] for a in article_files]
    print(f"Found {len(article_slugs)} master articles in public/articles/")

    # 6. Generate Master Sitemap.xml (7 Core + 32 Articles + 95 Posts = 134 URLs)
    today = datetime.now().strftime("%Y-%m-%d")
    sitemap_entries = []

    # 7 Core Pages
    core_pages = [
        ("/", "daily", "1.0"),
        ("/articles", "daily", "0.95"),
        ("/about", "monthly", "0.8"),
        ("/contact", "monthly", "0.8"),
        ("/privacy-policy", "monthly", "0.6"),
        ("/terms", "monthly", "0.6"),
        ("/disclaimer", "monthly", "0.6"),
    ]
    for path, freq, prio in core_pages:
        sitemap_entries.append(f"""  <url>
    <loc>https://krishnavibez.in{path}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>""")

    # 32 Articles
    for slug in sorted(article_slugs):
        sitemap_entries.append(f"""  <url>
    <loc>https://krishnavibez.in/articles/{slug}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>""")

    # 95 Automated Posts
    for p in posts:
        post_id = p["id"]
        lastmod = p.get("isoDate") or today
        sitemap_entries.append(f"""  <url>
    <loc>https://krishnavibez.in/post/{post_id}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.85</priority>
  </url>""")

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(sitemap_entries) + '\n</urlset>\n'
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
    print(f"✅ Generated sitemap.xml with {len(sitemap_entries)} total URLs (7 Core + {len(article_slugs)} Articles + {len(posts)} Posts)")

    # Validate sitemap XML syntax
    try:
        ET.fromstring(sitemap_xml.encode('utf-8'))
        print("🟢 SITEMAP XML VALIDATION: 100% PERFECT SYNTAX (0 errors)")
    except Exception as e:
        print("❌ SITEMAP XML SYNTAX ERROR:", e)

    # 7. Generate Master RSS.xml (with 100% safe XML escaping)
    rfc_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0530")
    rss_items = []

    # Add 32 Articles to RSS
    for slug in sorted(article_slugs):
        art_path = os.path.join(ARTICLES_DIR, f"{slug}.html")
        with open(art_path, "r", encoding="utf-8") as f:
            art_content = f.read()
        
        title_m = re.search(r'<title>(.*?)</title>', art_content)
        title = title_m.group(1).replace(" — Krishna Vibez", "").strip() if title_m else slug
        
        desc_m = re.search(r'<meta\s+name="description"\s+content="(.*?)"', art_content)
        desc = desc_m.group(1).strip() if desc_m else title
        
        url = f"https://krishnavibez.in/articles/{slug}"
        img_url = "https://files.catbox.moe/x9e87u.jpg"
        img_m = re.search(r'<meta\s+property="og:image"\s+content="(.*?)"', art_content)
        if img_m:
            img_url = img_m.group(1)

        cat = "श्रीमद्भगवद्गीता ज्ञान"

        item = f"""    <item>
      <title>{html.escape(title)}</title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{rfc_date}</pubDate>
      <dc:creator>Paresh Padsala (Krishna Vibez)</dc:creator>
      <category>{html.escape(cat)}</category>
      <description><![CDATA[{desc}]]></description>
      <media:content url="{html.escape(img_url, quote=True)}" medium="image"/>
      <media:thumbnail url="{html.escape(img_url, quote=True)}"/>
    </item>"""
        rss_items.append(item)

    # Add Top 20 Automated Posts to RSS
    for p in posts[:20]:
        post_id = p["id"]
        title = p.get("title", "श्री कृष्ण अमृत विचार")
        desc = p.get("shortDesc") or p.get("quote") or ""
        cat = p.get("category", "दैनिक दर्शन")
        url = f"https://krishnavibez.in/post/{post_id}"
        is_video = (p.get("mediaType") == "video") or bool(p.get("videoUrl"))
        media_url = p.get("videoUrl") or p.get("imageUrl") or "https://krishnavibez.in/assets/krishna-og.jpg"
        media_type = "video/mp4" if is_video else "image/jpeg"
        medium = "video" if is_video else "image"

        item = f"""    <item>
      <title>{html.escape(title)}</title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{rfc_date}</pubDate>
      <dc:creator>Paresh Padsala (Krishna Vibez)</dc:creator>
      <category>{html.escape(cat)}</category>
      <description><![CDATA[{desc}]]></description>
      <enclosure url="{html.escape(media_url, quote=True)}" type="{media_type}" length="1048576"/>
      <media:content url="{html.escape(media_url, quote=True)}" medium="{medium}"/>
    </item>"""
        rss_items.append(item)

    rss_items_str = "\n".join(rss_items)
    full_rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>Krishna Vibez — दैनिक दिव्य दर्शन, भगवद्गीता सार एवं आध्यात्मिक लेख</title>
    <link>https://krishnavibez.in/</link>
    <description>भगवान श्री कृष्ण के अनमोल विचार, श्रीमद्भगवद्गीता उपदेश, 32+ प्रामाणिक आध्यात्मिक लेख एवं 4K HD दर्शन।</description>
    <language>hi-IN</language>
    <lastBuildDate>{rfc_date}</lastBuildDate>
    <atom:link href="https://krishnavibez.in/rss.xml" rel="self" type="application/rss+xml"/>
    <image>
      <url>https://krishnavibez.in/assets/logo.png</url>
      <title>Krishna Vibez</title>
      <link>https://krishnavibez.in/</link>
    </image>
{rss_items_str}
  </channel>
</rss>
"""
    with open(RSS_PATH, "w", encoding="utf-8") as f:
        f.write(full_rss)
    print(f"✅ Generated rss.xml with {len(rss_items)} items ({len(article_slugs)} Articles + 20 Posts)")

    # Validate RSS XML syntax
    try:
        ET.fromstring(full_rss.encode('utf-8'))
        print("🟢 RSS XML VALIDATION: 100% PERFECT SYNTAX (0 errors, ZERO unescaped ampersands)")
    except Exception as e:
        print("❌ RSS XML SYNTAX ERROR:", e)

if __name__ == "__main__":
    main()

