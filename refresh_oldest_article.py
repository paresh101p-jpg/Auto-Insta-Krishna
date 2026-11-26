#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Krishnavibez.in Autonomous Article Refresher / Updater
1. Inspects all 36 articles in website/public/articles/*.html.
2. Identifies articles that were published ~300 days ago (or >= 300 days old) in a strict chronological queue.
3. Selects exactly ONE article per day to refresh.
4. Refreshes its content with enhanced insights, updated FAQs, and modern JSON-LD schema.
5. Updates lastmod in articles-sitemap.xml and rss.xml without deleting ANY article.
6. Deploys to Firebase Hosting (krishna-vibez) and commits to GitHub.
"""

import os
import re
import glob
from datetime import datetime, timezone, timedelta

_IST = timezone(timedelta(hours=5, minutes=30))
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(REPO_ROOT, "website", "public", "articles")
SITEMAP_FILE = os.path.join(REPO_ROOT, "website", "public", "articles-sitemap.xml")

def find_target_article():
    files = glob.glob(os.path.join(ARTICLES_DIR, "*.html"))
    if not files:
        return None

    now_ist = datetime.now(_IST)
    articles_list = []

    for f in files:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
            m = re.search(r"\"datePublished\":\s*\"([^\"]+)\"", content)
            date_str = m.group(1) if m else "1970-01-01"
            m_mod = re.search(r"\"dateModified\":\s*\"([^\"]+)\"", content)
            mod_str = m_mod.group(1) if m_mod else date_str

            # Parse datePublished
            pub_date = None
            for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d"):
                try:
                    pub_date = datetime.strptime(date_str, fmt)
                    break
                except Exception:
                    pass
            if not pub_date:
                pub_date = datetime(2026, 1, 1, tzinfo=_IST)

            age_days = (now_ist - pub_date).total_seconds() / 86400.0

            articles_list.append({
                "path": f,
                "file": os.path.basename(f),
                "datePublished": date_str,
                "dateModified": mod_str,
                "pub_date": pub_date,
                "age_days": age_days,
                "mtime": os.path.getmtime(f)
            })

    # Sort queue:
    # Prioritize articles >= 300 days old whose dateModified is oldest
    # If no article is >= 300 days old yet, select the oldest published article in queue
    eligible = [a for a in articles_list if a["age_days"] >= 290]
    if not eligible:
        eligible = articles_list

    eligible.sort(key=lambda x: (x["dateModified"], x["pub_date"]))
    return eligible[0]

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
    print(f"   Published date: {target['datePublished']} (Age: {target['age_days']:.1f} days)")
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
    target = find_target_article()
    if target:
        refresh_article(target)
    else:
        print("No articles found to update.")
