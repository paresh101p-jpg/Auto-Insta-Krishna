import json, os

QUEUE_FILE = "Auto-Insta-Krishna/channel_music_videos_oldest_first.json"
REGISTRY_FILE = "Auto-Insta-Krishna/completed_music_video_thumbnails.json"

# Videos that already have master thumbnails applied:
ALREADY_COMPLETED = {
    "X0EMsuBBhr4": "Playlist 1 Lead",
    "Zb9E7V9LiVM": "Playlist 2 Lead",
    "VDEvUok3pT8": "Playlist 3 Lead",
    "aOMg-IAezXY": "Playlist 4 Lead",
    "sUctWLbOpmY": "Playlist 5 Lead",
    "PZes6Z-cU8s": "Playlist 6 Lead",
    "CJF8tZpJI8Y": "Playlist 7 Lead",
    "InfDz_ftdGE": "Playlist 8 Lead",
    "_65f6xs_WUk": "Playlist 9 Lead",
    "vuoOW98h96c": "Playlist 10 Lead",
    "lElWf0LSl_I": "Manual master thumb test",
    "QoY31E1kRi4": "Manual master thumb test"
}

if os.path.exists(REGISTRY_FILE):
    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        registry = json.load(f)
else:
    registry = ALREADY_COMPLETED

with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

with open(QUEUE_FILE, "r", encoding="utf-8") as f:
    raw_videos = json.load(f)

# Deduplicate and filter out 24/7 multi-day streams
filtered = []
seen_ids = set()

for v in raw_videos:
    vid = v["id"]
    if vid in seen_ids:
        continue
    seen_ids.add(vid)
    
    title = v["title"]
    dur = v["duration"]
    
    # Skip live streams lasting days (e.g. P1D, P2D, P3D, P4D)
    if "D" in dur or "24/7" in title or "LIVE" in title:
        continue
        
    filtered.append(v)

print(f"Total Standalone Long-Form Music Videos: {len(filtered)}")

pending = [v for v in filtered if v["id"] not in registry]
print(f"Pending Videos to Process: {len(pending)}")

print("\n--- NEXT 5 PENDING VIDEOS (Oldest First) ---")
for idx, v in enumerate(pending[:5]):
    print(f"{idx+1}. [{v['published']}] ID: {v['id']} | Title: {v['title']}")

