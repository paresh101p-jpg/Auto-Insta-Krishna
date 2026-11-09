# -*- coding: utf-8 -*-
"""
Master Thumbnail Prompt Engine for YouTube Playlists & 15-Minute Music Videos
- 100% EXCLUSIVE PURE ONE-SHOT AI PROMPT ARCHITECTURE (ZERO HTML, ZERO CROP/PASTE).
- MANDATORY ATTRIBUTES:
  * Extreme Macro Focus on Face, Slender Neck, Collarbones & Décolletage.
  * Always Beautiful Smiling Madhosh / Trance Pose (Candid, 60-degree angled, NEVER looking at camera).
  * Traditional Red Bindi, Winged Kajal, Layered Gold Choker, Drop-Shoulder Designer Choli with Transparent One-Shoulder Net Dupatta.
  * Single Continuous Unified Scene (Zero split lines, Zero divider borders).
  * Pure 3D Embossed Gleaming Gold Letters floating naturally (Zero black boxes, Zero translucent strips).
  * Classical Instrument placed below floating text (Bansuri ALWAYS with vibrant iridescent Morpankh).
"""

import re
import random

CATEGORY_CONFIGS = [
    {
        "id": "stress_relief",
        "keywords": ["stress", "relief", "tanav", "chinta", "mental", "peace", "calm", "overthinking"],
        "hook_title": "तनाव और चिंता तुरंत दूर करें",
        "hook_sub": "STRESS RELIEF FLUTE - 15 MIN",
        "choli": "deep emerald-green velvet with intricate gold mirror-work and zardozi detailing",
        "dupatta": "sheer transparent olive-green net dupatta draped loosely over one shoulder",
        "pose": "Her torso is physically angled sideways at a 60-degree diagonal away from the camera. Her head is tilted backwards with blissful feminine grace, her captivating almond eyes softly closed with an enchanting, sweet serene smile on her parted glossy pink lips, completely lost in soothing peaceful melody, NEVER facing or looking towards the camera.",
        "instrument": "An authentic handcrafted golden bamboo bansuri flute adorned with a vibrant iridescent peacock feather (morpankh) resting on an ancient mossy boulder beside crystal-clear flowing turquoise water.",
        "background": "a breathtaking misty emerald alpine lake at golden sunrise with warm sunbeams piercing through pine trees and floating magical amber bokeh motes"
    },
    {
        "id": "deep_sleep",
        "keywords": ["sleep", "night", "neend", "insomnia", "soye", "soyein", "lullaby"],
        "hook_title": "सोने से पहले 10 मिनट सुनें",
        "hook_sub": "गहरी नींद और मानसिक शांति",
        "choli": "deep midnight sapphire-blue velvet with delicate silver zardozi and pearl cutwork",
        "dupatta": "ultra-sheer transparent navy-blue net dupatta draped loosely over one shoulder",
        "pose": "Her torso is physically angled sideways at a 60-degree diagonal away from the camera. Her head is tilted backwards against a soft velvet headrest in deep musical ecstasy and trance, her enchanting almond eyes softly closed with a blissful, sweet relaxed smile on her parted glossy pink lips, completely lost in soothing peaceful melody, NEVER looking or facing towards the camera.",
        "instrument": "An authentic handcrafted bamboo flute adorned with a vibrant iridescent peacock feather (morpankh) resting on a polished dark wood pedestal beside a warm glowing brass diya.",
        "background": "a seamless, misty ancient royal pavilion at starry midnight, with soft silver moonlight filtering through enchanted bamboo trees, glowing fireflies floating in the air, and magical ambient bokeh"
    },
    {
        "id": "morning_awakening",
        "keywords": ["morning", "awakening", "sunrise", "dawn", "prabhat", "subah", "positivity", "positive"],
        "hook_title": "सुबह उठते ही 10 मिनट सुनें",
        "hook_sub": "दिन भर सकारात्मक ऊर्जा",
        "choli": "vibrant sunrise saffron-marigold silk with heavy gold mirror-work and zardozi embroidery",
        "dupatta": "ultra-sheer transparent saffron net dupatta draped loosely over one shoulder",
        "pose": "Her torso is physically angled sideways at a 60-degree diagonal away from the camera. Her head is tilted backwards with blissful feminine grace, absorbing the warm morning dawn rays, her enchanting almond eyes softly closed with a serene, radiant smile on her parted glossy pink lips, completely lost in divine morning serenity, NEVER looking or facing towards the camera.",
        "instrument": "An authentic handcrafted golden bamboo bansuri flute adorned with a vibrant iridescent peacock feather (morpankh) resting on an ornate carved brass thali with scattered fresh yellow marigold and orange flower petals.",
        "background": "an ancient Vrindavan marble temple ghat at golden sunrise, with glorious warm sunbeams cutting through morning haze, Yamuna river shimmering in the distance, and dreamy floating golden dust motes"
    },
    {
        "id": "lotus_lake",
        "keywords": ["lotus", "lake", "sarovar", "kamal", "pond", "water", "lily"],
        "hook_title": "मन की सारी अशांति दूर करें",
        "hook_sub": "PEACEFUL LOTUS FLUTE - 15 MIN",
        "choli": "elegant blush rose-pink silk with intricate gold zardozi cutwork and pearl borders",
        "dupatta": "ultra-sheer transparent rose-gold net dupatta draped loosely over one shoulder",
        "pose": "Her torso is physically angled sideways at a 60-degree diagonal away from the camera. Her head is tilted backwards with sublime feminine grace, her captivating almond eyes softly closed with a blissful, sweet sensual smile on her parted glossy pink lips, lost in deep musical trance and peace, NEVER facing or looking towards the camera.",
        "instrument": "An authentic handcrafted golden bamboo bansuri flute adorned with a vibrant iridescent peacock feather (morpankh) resting gracefully across a giant blooming pink lotus flower on calm reflective morning water.",
        "background": "a sacred Vrindavan lotus pond at sunrise with blooming pink water lilies, morning mist, warm golden god rays, and floating magical amber bokeh motes"
    },
    {
        "id": "bansuri_tabla",
        "keywords": ["tabla", "jugalbandi", "taal", "rhythm", "classical"],
        "hook_title": "सुरीली बाँसुरी और कोमल तबला",
        "hook_sub": "15 MIN RELAXING JUGALBANDI",
        "choli": "royal crimson red velvet with heavy gold zardozi embroidery and pearl cutwork",
        "dupatta": "ultra-sheer transparent crimson net dupatta with shimmering gold borders draped over one shoulder",
        "pose": "Her torso is physically turned at a 60-degree angle away from the camera, swaying gently in musical rhythm. Her head is tilted with alluring charm, her deep almond eyes half-closed with a captivating, joyous smile on her glossy lips, completely enchanted by the classical Indian melody, NEVER looking at the camera.",
        "instrument": "An authentic Indian classical dark rosewood Tabla pair (bayan and dayan) and a golden bansuri flute with an iridescent peacock feather, resting elegantly on crimson velvet with scattered fresh red rose petals.",
        "background": "an ancient Rajasthani white marble palace courtyard at golden sunrise with soft morning sunbeams and floating magical warm amber bokeh"
    },
    {
        "id": "raga_darbari",
        "keywords": ["darbari", "raga", "raag", "royal", "sitar", "tanpura"],
        "hook_title": "जब दिमाग बहुत थक जाए",
        "hook_sub": "गहरा ध्यान और सुकून - 15 MIN",
        "choli": "rich royal wine-burgundy velvet with heavy antique gold zardozi and pearl cutwork",
        "dupatta": "ultra-sheer transparent wine-red net dupatta draped loosely over one shoulder",
        "pose": "Her torso is physically angled sideways at a 60-degree diagonal away from the camera. Her head is tilted backwards with royal poise, her enchanting almond eyes softly closed with a blissful, meditative smile on her parted glossy lips, completely entranced by deep royal classical music, NEVER looking towards the camera.",
        "instrument": "An authentic, exquisitely hand-carved Indian classical Sitar with delicate mother-of-pearl floral inlays, resting gracefully on red velvet beside warm flickering brass deepam oil lamps with floating jasmine petals.",
        "background": "a majestic ancient royal Indian palace stepwell courtyard at twilight, with hundreds of warm glowing clay diyas, ancient carved sandstone arches, gentle incense mist, and magical warm amber bokeh"
    },
    {
        "id": "yamuna_ghats",
        "keywords": ["yamuna", "ghat", "river", "nadi", "dusk", "sandhya", "evening"],
        "hook_title": "शाम को 15 मिनट सुनें",
        "hook_sub": "दिन भर की थकान गायब",
        "choli": "royal teal-peacock blue velvet with intricate gold threadwork and delicate border trim",
        "dupatta": "ultra-sheer transparent teal net dupatta draped loosely over one shoulder",
        "pose": "She is reclined sideways, resting her upper back and fair bare shoulder gently against an ornate carved marble pillar in total languid relaxation. Her chin is delicately rested sideways, her captivating deep almond eyes looking dreamily into the distance with a wistful, enchanting smile on her glossy pink lips, completely lost in evening river twilight, NEVER looking towards the camera.",
        "instrument": "An authentic handcrafted golden bamboo bansuri flute adorned with a vibrant iridescent peacock feather (morpankh) resting on an ancient sandstone river step beside floating glowing clay diyas on tranquil water.",
        "background": "an atmospheric Yamuna river stone ghat at twilight, with hundreds of floating golden oil lamps reflecting in the calm river, soft evening mist, temple bells in the distance, and magical amber bokeh"
    },
    {
        "id": "soul_healing",
        "keywords": ["soul", "healing", "divine", "dhyan", "meditation", "peaceful", "inner"],
        "hook_title": "आत्मा को मिले असीम शांति",
        "hook_sub": "DIVINE HEALING FLUTE - 15 MIN",
        "choli": "opulent ivory-gold raw silk with intricate antique gold filigree and sparkling crystal cutwork",
        "dupatta": "ultra-sheer transparent ivory-gold net dupatta draped loosely over one shoulder",
        "pose": "Her torso is angled diagonally at 60-degrees. Her head is tilted gently back in spiritual transcendence, a luminous, serene smile adorning her lips, eyes closed in divine meditation, exuding boundless calm and grace, NEVER facing the camera.",
        "instrument": "An authentic handcrafted golden bansuri flute with an iridescent peacock feather resting on a ceremonial gold thali beside sacred white lotus blossoms and a gentle curling ribbon of incense smoke.",
        "background": "a celestial ancient temple sanctum with hanging brass bells, glowing carved pillars bathed in divine golden volumetric light, and soft ethereal floating particles"
    }
]

DEFAULT_CONFIG = CATEGORY_CONFIGS[0]

def match_category(title, description=""):
    text = f"{title} {description}".lower()
    for cfg in CATEGORY_CONFIGS:
        for kw in cfg["keywords"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", text):
                return cfg
    return DEFAULT_CONFIG

def build_master_thumbnail_prompt(title, description=""):
    cfg = match_category(title, description)
    
    prompt = (
        f"A viral high-CTR 16:9 cinematic YouTube meditation thumbnail. "
        f"A single continuous, unified cinematic wide scene with ZERO split lines, ZERO divider borders, and ZERO partitions. "
        f"Framed prominently on the right side of the environment in an intense, maximum tight macro close-up—with extreme sharp focus "
        f"centered directly on her face, soft smiling lips, and fair glowing complexion—is an extraordinarily gorgeous, fair-skinned Indian woman "
        f"with a voluptuous feminine silhouette and radiant glowing porcelain skin. "
        f"{cfg['pose']} "
        f"On her smooth fair forehead sits a delicate, vibrant red traditional Indian bindi. "
        f"Razor-sharp macro focus captures her soft parted glossy pink lips with a gentle captivating smile, glowing jawline, slender neck adorned "
        f"with a royal gold choker, prominent collarbones, and sculpted décolletage. "
        f"She wears an ultra-luxury designer couture sweetheart drop-shoulder choli in {cfg['choli']}, "
        f"with an {cfg['dupatta']}, leaving the opposite shoulder completely bare and glowing. Hands are off-frame. "
        f"On the left side of the SAME continuous environment: "
        f"In the upper area, floating naturally and cleanly directly in the open air with ZERO background box, ZERO black banner strip, "
        f"ZERO dark backing rectangle, and ZERO drop-shadow bar, are massive individual 3D embossed gleaming polished metallic gold luxury letters "
        f"reading \"{cfg['hook_title']}\" with a glowing subtitle \"{cfg['hook_sub']}\". "
        f"Directly below the floating letters: {cfg['instrument']} "
        f"The entire environment is a seamless, {cfg['background']}. "
        f"8K commercial fashion portrait photography, extreme shallow depth of field, dramatic cinematic rim lighting, pure single-shot unified scene, "
        f"award-winning viral YouTube cover."
    )
    return prompt, cfg

if __name__ == "__main__":
    test_title = "Stress Relief & Mental Peace | Flute Meditation"
    p, c = build_master_thumbnail_prompt(test_title)
    print("Detected Category:", c["id"])
    print("Prompt length:", len(p))
    print("\nPROMPT:\n", p)
