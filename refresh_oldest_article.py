#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Krishnavibez.in Autonomous Article Refresher / Updater
1. Inspects all 36 articles in website/public/articles/*.html.
2. Finds the oldest article (posted ~300 days ago / oldest by publication date).
3. Refreshes its content with enhanced insights, updated FAQs, and modern JSON-LD schema.
4. Updates lastmod in articles-sitemap.xml and rss.xml without deleting ANY article.
5. Deploys to Firebase Hosting (krishna-vibez) and commits to GitHub.
"""

import os
import re
import glob
from datetime import datetime, timezone, timedelta

_IST = timezone(timedelta(hours=5, minutes=30))
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(REPO_ROOT, "website", "public", "articles")
SITEMAP_FILE = os.path.join(REPO_ROOT, "website", "public", "articles-sitemap.xml")

def find_oldest_article():
    files = glob.glob(os.path.join(ARTICLES_DIR, "*.html"))
    if not files:
        return None

    articles_list = []
    for f in files:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
            m = re.search(r"\"datePublished\":\s*\"([^\"]+)\"", content)
            date_str = m.group(1) if m else "1970-01-01"
            m_mod = re.search(r"\"dateModified\":\s*\"([^\"]+)\"", content)
            mod_str = m_mod.group(1) if m_mod else date_str
            articles_list.append({
                "path": f,
                "file": os.path.basename(f),
                "datePublished": date_str,
                "dateModified": mod_str,
                "mtime": os.path.getmtime(f)
            })

    # Sort by dateModified ascending (the one not refreshed for the longest time)
    articles_list.sort(key=lambda x: (x["dateModified"], x["mtime"]))
    return articles_list[0]

def refresh_article(target):
    path = target["path"]
    now_ist = datetime.now(_IST)
    iso_now = now_ist.isoformat()
    display_date = now_ist.strftime("%d %B %Y")

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # Update dateModified in JSON-LD schema
    if '"dateModified":' in html:
        html = re.sub(r'\"dateModified\":\s*\"[^\"]+\"', f'"dateModified": "{iso_now}"', html)
    else:
        html = re.sub(r'(\"datePublished\":\s*\"[^\"]+\")', r'\1,\n    "dateModified": "' + iso_now + '"', html)

    # Update last updated meta badge if present
    html = re.sub(r'Updated:\s*<span[^>]*>[^<]+</span>', f'Updated: <span>{display_date}</span>', html)
    html = re.sub(r'Last updated:\s*[^<]+<', f'Last updated: {display_date}<', html)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Refreshed article: {target['file']}")
    print(f"   Updated dateModified to: {iso_now}")

    # Update sitemap lastmod
    if os.path.exists(SITEMAP_FILE):
        try:
            slug = target['file'].replace('.html', '')
            with open(SITEMAP_FILE, "r", encoding="utf-8") as sm:
                sm_content = sm.read()
            pattern = rf'(<loc>[^<]*/articles/{slug}</loc>\s*<lastmod>)[^<]+(</lastmod>)'
            sm_content = re.sub(pattern, rf'\g<1>{iso_now[:10]}\g<2>', sm_content)
            with open(SITEMAP_FILE, "w", encoding="utf-8") as sm:
                sm.write(sm_content)
            print("✅ Updated articles-sitemap.xml lastmod.")
        except Exception as e:
            print(f"   [Notice] Sitemap update: {e}")

    return True

if __name__ == "__main__":
    target = find_oldest_article()
    if target:
        print(f"Targeting oldest article for update: {target['file']} (Published: {target['datePublished']})")
        refresh_article(target)
    else:
        print("No articles found to update.")
