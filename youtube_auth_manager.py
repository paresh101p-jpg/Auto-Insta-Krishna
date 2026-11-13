# -*- coding: utf-8 -*-
"""
DUAL-ENGINE YOUTUBE AUTHENTICATION MANAGER (AUTO-FAILOVER)
=========================================================
Automatically fails over between:
1. Engine 1 (Primary: 859501505546 - 10,000 Quota Units)
2. Engine 2 (Secondary Lifetime: 536337501439 - 10,000 Quota Units)

When Engine 1 exceeds quota (403 quotaExceeded), it instantly switches
to Engine 2 without failing the script or task.
"""
import os
import sys
import json
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_ENGINE1 = os.path.join(BASE_DIR, "youtube_token_engine1.json")
TOKEN_ENGINE2 = os.path.join(BASE_DIR, "youtube_token_engine2.json")
ACTIVE_TOKEN = os.path.join(BASE_DIR, "youtube_token.json")

def load_engine_token(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def get_valid_access_token(token_data):
    if not token_data or not token_data.get("refresh_token"):
        return None
    try:
        resp = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": token_data["client_id"],
            "client_secret": token_data["client_secret"],
            "refresh_token": token_data["refresh_token"],
            "grant_type": "refresh_token"
        }, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("access_token")
    except Exception as e:
        print(f"Error refreshing token: {e}")
    return None

def test_engine_quota(access_token):
    """Checks if the quota is active with a 1-unit call."""
    if not access_token:
        return False
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/channels?part=id&mine=true",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        if r.status_code == 200:
            return True
        elif r.status_code == 403 and "quotaExceeded" in r.text:
            return False
    except Exception:
        pass
    return False

def get_active_youtube_service():
    """
    Returns (youtube_service, engine_name).
    Checks Engine 1 first; if quota exceeded, automatically uses Engine 2.
    """
    e1_data = load_engine_token(TOKEN_ENGINE1)
    e2_data = load_engine_token(TOKEN_ENGINE2)

    # 1. Try Engine 2 (Lifetime Production) first if currently active
    tok2 = get_valid_access_token(e2_data)
    if tok2 and test_engine_quota(tok2):
        creds = Credentials(
            token=tok2,
            refresh_token=e2_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=e2_data.get("client_id"),
            client_secret=e2_data.get("client_secret")
        )
        return build("youtube", "v3", credentials=creds), "Engine 2 (Lifetime Production)"

    # 2. Fallback to Engine 1
    tok1 = get_valid_access_token(e1_data)
    if tok1 and test_engine_quota(tok1):
        creds = Credentials(
            token=tok1,
            refresh_token=e1_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=e1_data.get("client_id"),
            client_secret=e1_data.get("client_secret")
        )
        return build("youtube", "v3", credentials=creds), "Engine 1 (Primary)"

    # If neither passes test_engine_quota, return Engine 2 credentials anyway (may reset soon)
    if tok2:
        creds = Credentials(token=tok2, refresh_token=e2_data.get("refresh_token"),
                            token_uri="https://oauth2.googleapis.com/token",
                            client_id=e2_data.get("client_id"), client_secret=e2_data.get("client_secret"))
        return build("youtube", "v3", credentials=creds), "Engine 2 (Forced)"

    raise Exception("No valid YouTube tokens found!")

if __name__ == "__main__":
    service, engine = get_active_youtube_service()
    print(f"SUCCESS: Active YouTube Engine: {engine}")
