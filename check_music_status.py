#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Music Queue Status Checker for Krishna Vibez
Displays live counts of Suno AI and Treblo AI music pools
"""

import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_track_count(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
    return len(lines)

def print_status():
    suno_active = get_track_count("suno_music_urls.txt")
    suno_backup = get_track_count("suno_music_urls_backup.txt")
    suno_used = get_track_count("suno_music_used_urls.txt")

    treblo_active = get_track_count("treblo_music_urls.txt")
    treblo_backup = get_track_count("treblo_music_urls_backup.txt")
    treblo_used = get_track_count("treblo_music_used_urls.txt")

    total_active = suno_active + treblo_active
    total_backup = suno_backup + treblo_backup

    print("=" * 65)
    print("        KRISHNA VIBEZ — MASTER AI MUSIC INVENTORY STATUS")
    print("=" * 65)
    print("\n  [1] SUNO AI MUSIC STATUS:")
    print(f"      • Active Queue (Ready to use) : {suno_active} tracks")
    print(f"      • Master Backup Pool          : {suno_backup} tracks")
    print(f"      • Already Used / Uploaded     : {suno_used} tracks")
    
    print("\n  [2] TREBLO AI MUSIC STATUS:")
    print(f"      • Active Queue (Fallback)     : {treblo_active} tracks")
    print(f"      • Master Backup Pool          : {treblo_backup} tracks")
    print(f"      • Already Used / Uploaded     : {treblo_used} tracks")

    print("\n  " + "-" * 50)
    print(f"    TOTAL ACTIVE QUEUE (Combined) : {total_active} tracks")
    print(f"    TOTAL MASTER BACKUP POOL      : {total_backup} tracks")
    print("  " + "-" * 50)
    print("=" * 65)

if __name__ == "__main__":
    print_status()
