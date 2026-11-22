# -*- coding: utf-8 -*-
"""
Posts the deferred Krishna Vibez article link to Facebook AFTER the article
has been deployed to Firebase Hosting, so the link preview is never a 404.
Reads pending_fb_post.json produced by daily_trending_article_engine.py when
SKIP_FB_POST is set.
"""
import os
import sys
import json

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PENDING_FILE = os.path.join(REPO_ROOT, "pending_fb_post.json")

# Import the posting helper from the main engine
sys.path.insert(0, REPO_ROOT)
from daily_trending_article_engine import post_to_facebook

def main():
    if not os.path.exists(PENDING_FILE):
        print("No pending_fb_post.json found. Nothing to post.")
        return 0

    with open(PENDING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    topic_meta = data["topic_meta"]
    hero_img = data["hero_img"]

    print(f"Posting deferred article to Facebook: {topic_meta.get('title')}")
    success, res = post_to_facebook(topic_meta, hero_img)

    if success:
        try:
            os.remove(PENDING_FILE)
            print("Removed pending_fb_post.json after successful post.")
        except Exception as e:
            print(f"Notice removing pending file: {e}")
        return 0
    else:
        print(f"Facebook post failed: {res}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
