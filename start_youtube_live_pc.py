#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — 24/7 YOUTUBE LIVE STREAMING LAUNCHER (AUTO-RECONNECT)
=============================================================================
- Video: 1080p Full HD Base Loop (Floating Morpankh + Sparkles + Ken Burns)
- Audio: 64 Authentic Treblo AI Flute Tracks (3,200 Looped Entries)
- CPU Usage: < 1% (Direct Stream Copy -c:v copy)
- Auto-Reconnect: Infinitely re-establishes connection on any network drop
=============================================================================
"""

import os
import sys
import time
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_EXE = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG_EXE):
    FFMPEG_EXE = "ffmpeg"

BASE_VIDEO = os.path.join(BASE_DIR, "live_base_video.mp4")
AUDIO_PLAYLIST = os.path.join(BASE_DIR, "live_audio_playlist.txt")
STREAM_KEY = "9zzv-8p2v-7gdx-8kbx-b2kj"
RTMP_URL = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"

def run_stream():
    print("=================================================================")
    print("KRISHNA VIBEZ — 24/7 YOUTUBE LIVE MEDITATION STREAM")
    print("=================================================================")
    print(f"🎬 Video Source  : {os.path.basename(BASE_VIDEO)} (1080p Animated Loop)")
    print(f"🎵 Audio Source  : 64 Treblo AI Bansuri Flute Tracks")
    print(f"📡 Target Ingest : rtmp://a.rtmp.youtube.com/live2/••••{STREAM_KEY[-4:]}")
    print("⚙️ Video Mode    : -c:v copy (ZERO CPU load)")
    print("⚙️ Audio Mode    : AAC 192k 44.1kHz Studio Quality")
    print("=================================================================")

    stream_cmd = [
        FFMPEG_EXE,
        "-re",
        "-stream_loop", "-1",
        "-i", BASE_VIDEO,
        "-stream_loop", "-1",
        "-f", "concat", "-safe", "0",
        "-i", AUDIO_PLAYLIST,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-flvflags", "no_duration_filesize",
        "-f", "flv",
        RTMP_URL
    ]

    reconnect_count = 0
    while True:
        try:
            print(f"\n🚀 [Active] Broadcasting live stream to YouTube... (Session #{reconnect_count + 1})")
            p = subprocess.Popen(stream_cmd)
            p.wait()
            reconnect_count += 1
            print(f"⚠️ Stream disconnected (code {p.returncode}). Auto-reconnecting in 3 seconds...")
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n🛑 Stream manually stopped by user.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    run_stream()
