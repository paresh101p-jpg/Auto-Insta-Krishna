import os
import json
import random

BASE_DIR = r"E:\Paresh\Auto Post\Auto-Insta-Krishna"
CAT_JSON = os.path.join(BASE_DIR, "categorized_image_urls.json")

with open(CAT_JSON, "r", encoding="utf-8") as f:
    cat_data = json.load(f)

# Mapping of the 17 micro-categories into the 7 Parent Categories
# Notice multi-category cross-listing: an image group is included in ALL matching parent categories!
PARENT_MAP = {
    "morning_pooja": ["temple", "aarti", "sunrise_morning", "cows", "kadamba"],
    "stress_relief": ["meditation", "mountain", "bamboo", "peacock"],
    "sleep_insomnia": ["sleep_night", "rain_monsoon", "sunset_evening"],
    "bansuri_tabla": ["tanpura_instruments", "bamboo", "stepwell"],
    "raag_darbari": ["raas_celebration", "stepwell", "tanpura_instruments"],
    "lotus_lake": ["lotus", "yamuna_river", "meditation"],
    "lofi_beats": ["sunset_evening", "sleep_night", "bamboo", "rain_monsoon"]
}

print("Building 7 Parent Category Queues for Music Video Slides...")
counts = {}

for parent_cat, micro_cats in PARENT_MAP.items():
    pool_urls = []
    for mc in micro_cats:
        urls = cat_data.get(mc, [])
        pool_urls.extend(urls)
    
    # Deduplicate while preserving order
    unique_urls = list(dict.fromkeys(pool_urls))
    random.seed(42)
    random.shuffle(unique_urls)
    counts[parent_cat] = len(unique_urls)

    queue_path = os.path.join(BASE_DIR, f"music_slide_urls_{parent_cat}.txt")
    backup_path = os.path.join(BASE_DIR, f"music_slide_urls_{parent_cat}_backup.txt")

    with open(queue_path, "w", encoding="utf-8") as qf:
        qf.write("\n".join(unique_urls) + "\n")

    with open(backup_path, "w", encoding="utf-8") as bf:
        bf.write("\n".join(unique_urls) + "\n")

print("\n7 Parent Category Queues Created Successfully:")
for cat, count in counts.items():
    print(f"  • {cat}: {count} Catbox URLs")
