import json
import os

transcript_path = r"C:\Users\Admin\.gemini\antigravity-ide\brain\19740b44-94df-459e-92f8-b6789d7693f7\.system_generated\logs\transcript_full.jsonl"
out_dir = r"e:\Paresh\Auto Post\Auto-Insta-Krishna"

print("Reading transcript...")
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        if '"trackIds"' in line and '"entities"' in line:
            data = json.loads(line)
            content = data.get("content", "")
            # Locate {"data":
            idx = content.find('{"data":')
            if idx != -1:
                json_str = content[idx:].strip()
                # If content was wrapped or truncated
                print("Found JSON string! Length:", len(json_str))
                try:
                    parsed = json.loads(json_str)
                    tracks = parsed.get("entities", {}).get("tracks", {})
                    print(f"Extracted {len(tracks)} tracks successfully!")
                    with open(os.path.join(out_dir, "treblo_tracks_parsed.json"), "w", encoding="utf-8") as out:
                        json.dump(tracks, out, indent=2)
                except Exception as e:
                    print("JSON parse error:", e)
                    # Let's use regex to find all songPath and titles
                    import re
                    song_matches = re.findall(r'"title":"([^"]+)".*?"songPath":"([^"]+)"', json_str)
                    print(f"Regex found {len(song_matches)} tracks!")
                    track_list = []
                    for t, s in song_matches:
                        track_list.append({"title": t, "songPath": s})
                    with open(os.path.join(out_dir, "treblo_tracks_parsed.json"), "w", encoding="utf-8") as out:
                        json.dump(track_list, out, indent=2)
