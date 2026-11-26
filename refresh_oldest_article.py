#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Krishnavibez.in Strict 300-Day Article Refresher
Rule: ONLY update an article if it is EXACTLY on its 300th day (age in days == 300).
If it has reached 301 days or more, or less than 300 days, DO NOT update.
Zero deletions.
"""

import os
import re
import glob
from datetime import datetime, timezone, timedelta

_IST = timezone(timedelta(hours=5, minutes=30))
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(REPO_ROOT, "website", "public", "articles")
SITEMAP_FILE = os.path.join(REPO_ROOT, "website", "public", "articles-sitemap.xml")

def find_exact_300_day_article():
    files = glob.glob(os.path.join(ARTICLES_DIR, "*.html"))
    if not files:
        return None

    now_ist = datetime.now(_IST).date()

    for f in files:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
            m = re.search(r"\"datePublished\":\s*\"([^\"]+)\"", content)
            if not m:
                continue
            date_str = m.group(1)

            # Parse datePublished
            pub_date = None
            for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d"):
                try:
                    pub_date = datetime.strptime(date_str, fmt).astimezone(_IST).date()
                    break
                except Exception:
                    pass
            if not pub_date:
                continue

            # Exact calendar difference in days
            exact_days = (now_ist - pub_date).days

            # STRICT RULE: Must be EXACTLY 300 days. (Not 301, not 299).
            if exact_days == 300:
                return {
                    "path": f,
                    "file": os.path.basename(f),
                    "datePublished": date_str,
                    "exact_days": exact_days
                }

    return None

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

    print(f"✅ EXACT 300-DAY MATCH REFRESHED: {target['file']}")
    print(f"   Published: {target['datePublished']} (Exact {target['exact_days']} days ago)")
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
    target = find_exact_300_day_article()
    if target:
        refresh_article(target)
    else:
        print("ℹ️ No article found with age == exactly 300 days today. Skipping update.")
