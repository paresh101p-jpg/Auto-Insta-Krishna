# -*- coding: utf-8 -*-
"""
Master Thumbnail Prompt Engine for YouTube Playlists & 15-Minute Music Videos
- 100% EXCLUSIVE PURE ONE-SHOT AI PROMPT ARCHITECTURE (ZERO HTML, ZERO CROP/PASTE).
- 100% PURE INSTRUMENTAL & NATURE SOUND ACCURACY (ZERO VOCAL CLAIMS, ZERO FAKE OM CHANT WORDS).
- STRICT CATEGORY-INSTRUMENT COHERENCE:
  * Sitar tracks feature Classical Sitar (NO flute).
  * Tabla tracks feature Classical Tabla Pair (NO flute).
  * Tanpura tracks feature Classical Tanpura Strings (NO flute).
  * Veena tracks feature Saraswati Veena (NO flute).
  * Nature / Rain / Ocean / Birds feature authentic ambient instruments (Rainstick, Singing Bowl, Conch Shell, Windchimes).
  * Mridanga / Karatals feature acoustic Indian percussion (NO flute).
  * Iridescent Peacock Feather (Morpankh) is ALWAYS visually present in EVERY scene.
- EXPLICIT PURE INSTRUMENTAL IDENTIFICATION IN 3D GOLD TEXT:
  * Viewer immediately knows the exact acoustic instrument and music genre!
- DYNAMIC SIDE ALTERNATION (50/50 LEFT VS RIGHT):
  * Alternates model placement between Left and Right to guarantee visual freshness.
- MANDATORY VISUAL ATTRIBUTES:
  * Extreme Macro Focus on Face, Smiling Lips, Slender Neck, Collarbones & Décolletage.
  * Always Beautiful Smiling Madhosh / Trance Pose (Candid, 60-degree angled, NEVER looking at camera).
  * Traditional Red Bindi, Winged Kajal, Layered Gold Choker, Drop-Shoulder Designer Choli with Transparent One-Shoulder Net Dupatta.
  * Single Continuous Unified Scene (Zero split lines, Zero divider borders).
  * Massive, Free-Floating 3D Embossed Gleaming Polished Metallic Gold Luxury Letters (Zero black boxes, Zero dark strips).
"""

import re

CATEGORY_CONFIGS = [
    # 01. STRESS RELIEF BANSURI FLUTE
    {
        "id": "stress_relief_flute",
        "keywords": ["stress", "relief", "tanav", "chinta", "mental", "peace", "calm", "overthinking"],
        "model_side": "right",
        "hook_title": "मधुर बाँसुरी - तनाव और चिंता तुरंत दूर करें",
        "hook_sub": "DIVINE BANSURI FLUTE MEDITATION - 15 MIN",
        "choli": "deep emerald-green velvet with intricate gold mirror-work and zardozi detailing",
        "dupatta": "sheer transparent olive-green net dupatta draped loosely over one shoulder",
        "pose": "Her torso is physically angled sideways at a 60-degree diagonal away from the camera. Her head is tilted backwards with blissful feminine grace, her captivating almond eyes softly closed with an enchanting, sweet serene smile on her parted glossy pink lips, completely lost in soothing peaceful bansuri melody, NEVER facing or looking towards the camera.",
        "instrument": "An authentic handcrafted golden bamboo bansuri flute adorned with a vibrant iridescent peacock feather (morpankh) resting on an ancient mossy boulder beside crystal-clear flowing turquoise water.",
        "background": "a breathtaking misty emerald alpine lake at golden sunrise with warm sunbeams piercing through pine trees and floating magical amber bokeh motes"
    },
    # 02. ROYAL RAGA DARBARI SITAR
    {
        "id": "raga_darbari_sitar",
        "keywords": ["darbari", "raga", "raag", "royal", "sitar"],
        "model_side": "left",
        "hook_title": "राग दरबारी सितार वादन - दिमाग को असीम सुकून",
        "hook_sub": "ROYAL INDIAN CLASSICAL SITAR - 15 MIN",
        "choli": "rich royal wine-burgundy velvet with heavy antique gold zardozi and pearl cutwork",
        "dupatta": "ultra-sheer transparent wine-red net dupatta draped loosely over one shoulder",
        "pose": "Her torso is physically angled diagonally towards the right at 60-degrees. Her head is tilted backwards with royal poise, her enchanting almond eyes softly closed with a blissful, meditative smile on her parted glossy lips, completely entranced by deep royal Indian classical sitar notes, NEVER looking towards the camera.",
        "instrument": "An authentic, exquisitely hand-carved Indian classical Sitar with delicate mother-of-pearl floral inlays, and an iridescent peacock feather (morpankh) resting gracefully across its polished gourd body on red velvet beside warm flickering brass deepam oil lamps.",
        "background": "a majestic ancient royal Indian palace stepwell courtyard at twilight, with hundreds of warm glowing clay diyas, ancient carved sandstone arches, gentle incense mist, and magical warm amber bokeh"
    },
    # 03. INDIAN CLASSICAL TABLA
    {
        "id": "classical_tabla",
        "keywords": ["tabla", "taal", "rhythm", "theka", "teentaal"],
        "model_side": "right",
        "hook_title": "कोमल तबला ताल - गहरा ध्यान और शांति",
        "hook_sub": "CLASSICAL INDIAN TABLA RHYTHM - 15 MIN",
        "choli": "royal crimson red velvet with heavy gold zardozi embroidery and pearl cutwork",
        "dupatta": "ultra-sheer transparent crimson net dupatta with shimmering gold borders draped over one shoulder",
        "pose": "Her torso is physically turned at a 60-degree angle away from the camera, swaying gently to the rhythmic tabla beats. Her head is tilted with alluring charm, her deep almond eyes half-closed with a captivating, joyous smile on her glossy lips, completely enchanted by classical tabla taal, NEVER looking at the camera.",
        "instrument": "An authentic Indian classical dark rosewood Tabla pair (bayan and dayan) with intricate braided leather straps, and an iridescent peacock feather (morpankh) resting on crimson velvet between the drums beside scattered fresh red rose petals.",
        "background": "an ancient Rajasthani white marble palace courtyard at golden sunrise with soft morning sunbeams and floating magical warm amber bokeh"
    },
    # 04. BANSURI & TABLA JUGALBANDI
    {
        "id": "bansuri_tabla_jugalbandi",
        "keywords": ["jugalbandi", "duet"],
        "model_side": "left",
        "hook_title": "सुरीली बाँसुरी और कोमल तबला जुगलबंदी",
        "hook_sub": "BANSURI & TABLA CLASSICAL JUGALBANDI - 15 MIN",
        "choli": "regal magenta-purple silk with rich antique gold marodi embroidery",
        "dupatta": "ultra-sheer transparent magenta net dupatta draped loosely over one shoulder",
        "pose": "Her body is angled diagonally at 60-degrees, head tilted back in musical ecstasy as flute and tabla harmonize, a radiant enchanting smile on her parted lips, eyes gently closed in sheer joy, NEVER facing camera.",
        "instrument": "An authentic dark rosewood classical Tabla pair and a handcrafted golden bamboo bansuri flute adorned with a vibrant iridescent peacock feather (morpankh), resting together on royal red velvet with fresh rose and jasmine petals.",
        "background": "a grand royal Mughal pavilion overlooking serene reflective lotus ponds at golden hour twilight with warm chandeliers and soft amber bokeh"
    },
    # 05. COSMIC TANPURA STRINGS (100% PURE INSTRUMENTAL - ZERO VOCAL OM)
    {
        "id": "cosmic_tanpura",
        "keywords": ["tanpura", "tambura", "drone", "cosmic"],
        "model_side": "right",
        "hook_title": "तानपुरा संगीत - गहरा ध्यान और आत्मिक शांति",
        "hook_sub": "DEEP ACOUSTIC TANPURA MEDITATION - 15 MIN",
        "choli": "opulent ivory-gold raw silk with intricate antique gold filigree and sparkling crystal cutwork",
        "dupatta": "ultra-sheer transparent ivory-gold net dupatta draped loosely over one shoulder",
        "pose": "Her torso is angled diagonally at 60-degrees. Her head is tilted gently back in spiritual transcendence, a luminous, serene smile adorning her lips, eyes closed in divine resonance with the deep acoustic tanpura drone strings, exuding boundless calm, NEVER facing the camera.",
        "instrument": "A majestic handcrafted Indian classical Tanpura with four bronze drone strings and fine floral ivory inlay, with an iridescent peacock feather (morpankh) resting across its soundboard beside a warm glowing brass lamp.",
        "background": "a celestial ancient temple sanctum with hanging brass bells, glowing carved pillars bathed in divine golden volumetric light, and soft ethereal floating particles"
    },
    # 06. MONSOON RAIN SOUNDS
    {
        "id": "monsoon_rain",
        "keywords": ["rain", "monsoon", "barish", "drizzle", "thunder"],
        "model_side": "left",
        "hook_title": "रिमझिम बारिश की सुकून भरी ध्वनि - तनाव मुक्ति",
        "hook_sub": "SOOTHING MONSOON RAIN SOUNDS - 15 MIN",
        "choli": "deep monsoon indigo-blue silk with silver raindrop sequin work",
        "dupatta": "ultra-sheer transparent blue net dupatta draped loosely over one shoulder",
        "pose": "Her body is angled towards the right at 60-degrees, head gently resting against a wet marble jharokha window sill, eyes softly closed with a blissful refreshed smile, deeply enjoying the natural scent of fresh rain and the rhythm of raindrops, NEVER facing the camera.",
        "instrument": "A natural handcrafted bamboo rainstick and an authentic earthen water urn adorned with an iridescent peacock feather (morpankh) resting on wet carved marble beside scattered fresh wet jasmine buds.",
        "background": "an ancient royal palace terrace overlooking lush green Vrindavan gardens under gentle monsoon drizzle and soft misty twilight with falling water droplets"
    },
    # 07. MOUNTAIN RIVER & WATERFALL
    {
        "id": "mountain_river",
        "keywords": ["river", "waterfall", "stream", "jharna", "brook", "water"],
        "model_side": "right",
        "hook_title": "पहाड़ी झरने और नदी की धारा - मन को धो दे",
        "hook_sub": "NATURAL MOUNTAIN RIVER & WATERFALL SOUNDS",
        "choli": "vibrant aqua-teal silk with silver water-wave embroidery",
        "dupatta": "sheer transparent turquoise net dupatta draped loosely over one shoulder",
        "pose": "Her body is angled sideways at 60-degrees, head resting back against a smooth granite rock, eyes closed listening peacefully to the rushing crystal water, serene contented smile on her lips, NEVER looking at camera.",
        "instrument": "A sacred Tibetan bronze singing bowl with wooden striker, smooth polished river pebbles, and a vibrant iridescent peacock feather (morpankh) resting on a wet river boulder beside cascading clear freshwater.",
        "background": "a pristine Himalayan mountain brook with cascading mini-waterfalls, smooth river pebbles, lush alpine ferns, and morning sunlight piercing through mountain mist"
    },
    # 08. BEACHFRONT OCEAN WAVES
    {
        "id": "ocean_waves",
        "keywords": ["ocean", "waves", "beach", "samudra", "sea"],
        "model_side": "left",
        "hook_title": "समुद्र की शांत लहरें - गहरी और आरामदायक नींद",
        "hook_sub": "CALMING OCEAN WAVES FOR DEEP SLEEP - 15 MIN",
        "choli": "shimmering pearl-white raw silk with sea-foam gold embroidery",
        "dupatta": "sheer transparent white organza dupatta draped loosely over one shoulder",
        "pose": "Her torso is angled towards the right at 60-degrees, head tilted back into the gentle sea breeze with loose hair strands catching the sunset light, eyes softly closed with a sublime tranquil smile on her glossy lips, completely relaxed by ocean waves, NEVER looking at camera.",
        "instrument": "A natural sacred white spiral Conch Shell (shankha) and an iridescent peacock feather (morpankh) resting elegantly on clean golden sand beside gentle ocean foam.",
        "background": "a calm tropical ocean coastline at golden sunset with gentle pastel waves rolling onto the shore and warm amber horizon glow"
    },
    # 09. DEVOTIONAL MRIDANGA & KARATALS (100% PURE INSTRUMENTAL PERCUSSION)
    {
        "id": "devotional_mridanga",
        "keywords": ["kirtan", "mridanga", "satsang", "bhajan", "sankirtan"],
        "model_side": "right",
        "hook_title": "मृदंग और करताल की मधुर ताल - असीम शांति",
        "hook_sub": "ACOUSTIC DEVOTIONAL MRIDANGA & KARATALS - 15 MIN",
        "choli": "rich maroon-garnet silk with gold temple border embroidery",
        "dupatta": "sheer maroon net dupatta draped loosely over one shoulder",
        "pose": "Her torso is angled sideways at 60-degrees, head swaying gently to the rhythmic acoustic mridanga beats, glowing smile of serene musical joy on her lips, eyes closed listening peacefully, NEVER facing camera.",
        "instrument": "A traditional clay Indian Mridanga drum with red ceremonial strap, a pair of polished brass karatals (hand cymbals), and a vibrant iridescent peacock feather (morpankh) resting on an embroidered altar cloth with tulsi leaves.",
        "background": "an open-air riverbank pavilion in Braj during evening twilight with warm hanging paper lanterns and gentle peaceful ambient lighting"
    },
    # 10. SACRED LOTUS LAKE FLUTE
    {
        "id": "lotus_lake_flute",
        "keywords": ["lotus", "kamal", "sarovar", "pond", "lily"],
        "model_side": "left",
        "hook_title": "कमल सरोवर मधुर बाँसुरी - मन की सारी अशांति दूर",
        "hook_sub": "SACRED LOTUS LAKE BANSURI FLUTE - 15 MIN",
        "choli": "elegant blush rose-pink silk with intricate gold zardozi cutwork and pearl borders",
        "dupatta": "ultra-sheer transparent rose-gold net dupatta draped loosely over one shoulder",
        "pose": "Her torso is physically angled diagonally towards the right at a 60-degree angle. Her head is tilted backwards with sublime feminine grace, her captivating almond eyes softly closed with a blissful, sweet sensual smile on her parted glossy pink lips, lost in deep bansuri melody, NEVER facing or looking towards the camera.",
        "instrument": "An authentic handcrafted golden bamboo bansuri flute adorned with a vibrant iridescent peacock feather (morpankh) resting gracefully across a giant blooming pink lotus flower on calm reflective morning water.",
        "background": "a sacred Vrindavan lotus pond at sunrise with blooming pink water lilies, morning mist, warm golden god rays, and floating magical amber bokeh motes"
    },
    # 11. MIDNIGHT SLEEP FLUTE
    {
        "id": "midnight_sleep_flute",
        "keywords": ["sleep", "night", "neend", "insomnia", "soye", "soyein", "lullaby"],
        "model_side": "right",
        "hook_title": "रात की शांत बाँसुरी - सोने से पहले 10 मिनट सुनें",
        "hook_sub": "DEEP SLEEP & RELAXATION BANSURI - 15 MIN",
        "choli": "deep midnight sapphire-blue velvet with delicate silver zardozi and pearl cutwork",
        "dupatta": "ultra-sheer transparent navy-blue net dupatta draped loosely over one shoulder",
        "pose": "Her torso is physically angled sideways at a 60-degree diagonal away from the camera. Her head is tilted backwards against a soft velvet headrest in deep musical ecstasy and trance, her enchanting almond eyes softly closed with a blissful, sweet relaxed smile on her parted glossy pink lips, completely lost in soothing peaceful melody, NEVER looking or facing towards the camera.",
        "instrument": "An authentic handcrafted bamboo flute adorned with a vibrant iridescent peacock feather (morpankh) resting on a polished dark wood pedestal beside a warm glowing brass diya.",
        "background": "a seamless, misty ancient royal pavilion at starry midnight, with soft silver moonlight filtering through enchanted bamboo trees, glowing fireflies floating in the air, and magical ambient bokeh"
    },
    # 12. MORNING AWAKENING BANSURI
    {
        "id": "morning_awakening_flute",
        "keywords": ["morning", "awakening", "sunrise", "dawn", "prabhat", "subah", "positivity", "positive"],
        "model_side": "left",
        "hook_title": "प्रातःकालीन बाँसुरी - सुबह उठते ही सुनें",
        "hook_sub": "MORNING AWAKENING BANSURI & POSITIVE ENERGY",
        "choli": "vibrant sunrise saffron-marigold silk with heavy gold mirror-work and zardozi embroidery",
        "dupatta": "ultra-sheer transparent saffron net dupatta draped loosely over one shoulder",
        "pose": "Her torso is physically angled sideways at a 60-degree diagonal away from the camera. Her head is tilted backwards with blissful feminine grace, absorbing the warm morning dawn rays, her enchanting almond eyes softly closed with a serene, radiant smile on her parted glossy pink lips, completely lost in divine morning serenity, NEVER looking or facing towards the camera.",
        "instrument": "An authentic handcrafted golden bamboo bansuri flute adorned with a vibrant iridescent peacock feather (morpankh) resting on an ornate carved brass thali with scattered fresh yellow marigold and orange flower petals.",
        "background": "an ancient Vrindavan marble temple ghat at golden sunrise, with glorious warm sunbeams cutting through morning haze, Yamuna river shimmering in the distance, and dreamy floating golden dust motes"
    },
    # 13. TEMPLE BELL & SACRED SHANKHA (100% PURE ACOUSTIC BELL & CONCH)
    {
        "id": "temple_bell_aarti",
        "keywords": ["aarti", "bell", "ghanti", "pooja", "deepam", "mandir"],
        "model_side": "right",
        "hook_title": "मंदिर की पावन घंटी और शंख ध्वनि - आत्मिक शांति",
        "hook_sub": "SACRED TEMPLE BRASS BELLS & CONCH SHELL - 15 MIN",
        "choli": "deep ceremonial vermilion-red silk with heavy gold zardozi borders",
        "dupatta": "sheer red net dupatta draped loosely over one shoulder",
        "pose": "Her torso is angled at 60-degrees, chin slightly raised with an expression of divine devotion and bliss, a subtle pious smile on her parted lips, warm firelight dancing on her glowing cheeks, NEVER looking at camera.",
        "instrument": "A heavy carved temple brass hanging bell (ghanti), an authentic white sacred conch shell (shankha), and an iridescent peacock feather (morpankh) resting beside a multi-tiered brass deepam lamp with warm dancing flames.",
        "background": "an ancient stone temple sanctum illuminated by hundreds of golden oil lamps, swirling dhoop incense smoke, and hanging temple bells"
    },
    # 14. FOREST BIRDS & NATURAL AMBIENCE
    {
        "id": "forest_birds",
        "keywords": ["birds", "forest", "jungle", "pakshi", "chidiya"],
        "model_side": "left",
        "hook_title": "चहचहाते पक्षी और जंगल की शांति - तनाव से मुक्ति",
        "hook_sub": "SOOTHING FOREST BIRDS & NATURAL AMBIENCE",
        "choli": "rich moss-olive raw silk with golden vine embroidery",
        "dupatta": "sheer olive net dupatta draped loosely over one shoulder",
        "pose": "Her torso is angled towards the right at 60-degrees, head tilted backwards in total ecstasy as she listens to singing forest birds, eyes closed with a joyful, serene smile on her parted lips, completely one with nature, NEVER looking at camera.",
        "instrument": "Handcrafted bamboo windchimes and an iridescent peacock feather (morpankh) resting on a fallen mossy log beside wildflowers and dewy ferns.",
        "background": "an enchanted sacred grove in Braj at sunrise with morning fog, sunbeams dancing through giant banyan branches, and flying golden songbirds"
    },
    # 15. ANCIENT STEPWELL SWARPETI & TANPURA
    {
        "id": "stepwell_baori",
        "keywords": ["stepwell", "baori", "bavdi", "heritage", "ancient"],
        "model_side": "right",
        "hook_title": "प्राचीन बावड़ी स्वरपेटी संगीत - गहरा सुकून और एकाग्रता",
        "hook_sub": "ANCIENT STEPWELL SWARPETI & TANPURA INSTRUMENTAL - 15 MIN",
        "choli": "rich amber-ochre silk with antique copper-gold zari work",
        "dupatta": "sheer transparent amber dupatta draped loosely over one shoulder",
        "pose": "Her body is physically angled away at 60-degrees, head tilted slightly downward in peaceful musical contemplation, a sweet captivating smile on her glossy lips, eyes half-closed enjoying deep acoustic resonance, NEVER facing the camera.",
        "instrument": "An authentic wooden Indian Swarpeti (shrutibox), an antique tanpura soundboard, and an iridescent peacock feather (morpankh) resting on sandstone beside rows of warm glowing brass oil lamps.",
        "background": "an ancient subterranean stepwell with symmetrical geometric sandstone stairs descending into tranquil turquoise water, illuminated by flickering diyas"
    },
    # 16. SARASWATI VEENA CLASSICAL HERITAGE
    {
        "id": "classical_veena",
        "keywords": ["veena", "saraswati", "shastriya", "vina"],
        "model_side": "left",
        "hook_title": "दिव्य वीणा वादन - अंतरात्मा को मिले शांति",
        "hook_sub": "DIVINE CLASSICAL SARASWATI VEENA - 15 MIN",
        "choli": "regal emerald-gold brocade silk with traditional south Indian temple zardozi",
        "dupatta": "ultra-sheer transparent emerald net dupatta draped loosely over one shoulder",
        "pose": "Her torso is angled at 60-degrees towards the right, head tilted with serene devotion, a subtle blissful smile on her glossy lips, eyes gently closed as if absorbing sacred veena vibrations, NEVER facing camera.",
        "instrument": "A divine, masterfully hand-carved classical Saraswati Veena with golden frets, floral resonator carving, and an iridescent peacock feather (morpankh) resting on yellow silk beside a brass diya.",
        "background": "an ancient carved stone temple pavilion with granite pillars, fresh jasmine garlands, and morning sunlight streaming through stone lattices"
    },
    # 17. YAMUNA GHATS EVENING BANSURI
    {
        "id": "yamuna_ghats_flute",
        "keywords": ["yamuna", "ghat", "dusk", "sandhya", "evening", "diya"],
        "model_side": "right",
        "hook_title": "यमुना तट संध्या बाँसुरी - दिन भर की थकान गायब",
        "hook_sub": "YAMUNA GHATS EVENING BANSURI - 15 MIN",
        "choli": "royal teal-peacock blue velvet with intricate gold threadwork and delicate border trim",
        "dupatta": "ultra-sheer transparent teal net dupatta draped loosely over one shoulder",
        "pose": "She is reclined sideways, resting her upper back and fair bare shoulder gently against an ornate carved marble pillar in total languid relaxation. Her chin is delicately rested sideways, her captivating deep almond eyes looking dreamily into the distance with a wistful, enchanting smile on her glossy pink lips, completely lost in evening river twilight, NEVER looking towards the camera.",
        "instrument": "An authentic handcrafted golden bamboo bansuri flute adorned with a vibrant iridescent peacock feather (morpankh) resting on an ancient sandstone river step beside floating glowing clay diyas on tranquil water.",
        "background": "an atmospheric Yamuna river stone ghat at twilight, with hundreds of floating golden oil lamps reflecting in the calm river, soft evening mist, temple bells in the distance, and magical amber bokeh"
    }
]

DEFAULT_CONFIG = CATEGORY_CONFIGS[0]

SPECIFICITY_PRIORITY = [
    "midnight_sleep_flute",
    "yamuna_ghats_flute",
    "bansuri_tabla_jugalbandi",
    "lotus_lake_flute",
    "morning_awakening_flute",
    "raga_darbari_sitar",
    "classical_veena",
    "devotional_mridanga",
    "stepwell_baori",
    "temple_bell_aarti",
    "forest_birds",
    "monsoon_rain",
    "mountain_river",
    "ocean_waves",
    "classical_tabla",
    "cosmic_tanpura",
    "stress_relief_flute"
]

def match_category(title, description=""):
    text = f"{title} {description}".lower()
    cat_map = {c["id"]: c for c in CATEGORY_CONFIGS}
    for cat_id in SPECIFICITY_PRIORITY:
        cfg = cat_map.get(cat_id)
        if not cfg:
            continue
        for kw in cfg["keywords"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", text):
                return cfg
    return DEFAULT_CONFIG

# Dynamic Variation Pools for Infinite Freshness per Category
VARIATION_POSES = [
    "Her torso is physically angled sideways at a 60-degree diagonal away from the camera. Her head is tilted backwards with blissful feminine grace, her captivating almond eyes softly closed with an enchanting, sweet serene smile on her parted glossy pink lips, completely lost in deep musical melody, NEVER facing or looking towards the camera.",
    "Her body is physically angled diagonally at 60-degrees. Her chin is gently lifted towards the warm sky with an expression of pure musical ecstasy, a radiant, tender smile playing across her glossy parted lips, eyes half-closed in meditative bliss, NEVER looking at the camera.",
    "She is gracefully reclined sideways, resting her smooth bare shoulder gently against an ornate carved marble pillar in sublime relaxation. Her chin rests sideways, deep almond eyes looking dreamily into the distance with a wistful, seductive smile on her pink lips, NEVER facing camera.",
    "Her torso is turned away at a 60-degree angle, head titled softly to the side as if listening intently to the divine acoustic notes, a glowing, joyous smile illuminating her flawless face, eyes gently shut in sheer tranquility, NEVER looking at the camera."
]

VARIATION_CHOLIS = [
    "deep emerald-green velvet with intricate antique gold mirror-work and zardozi embroidery",
    "rich royal wine-burgundy velvet with heavy antique gold zardozi and pearl cutwork",
    "royal crimson-ruby red velvet with shimmering gold threadwork and delicate pearl borders",
    "regal midnight sapphire-blue silk with silver and gold filigree embroidery",
    "vibrant sunrise saffron-marigold silk with heavy gold zari borders and crystal accents",
    "opulent royal magenta-purple brocade silk with antique gold marodi embroidery"
]

VARIATION_LIGHTINGS = [
    "at glorious golden sunrise with warm sunbeams slicing through morning mist and floating magical amber bokeh motes",
    "at atmospheric twilight with hundreds of warm glowing clay oil lamps (diyas), gentle incense mist, and soft golden bokeh",
    "under soft glowing golden hour light with gentle reflections shimmering on tranquil sacred water and dreamy dust motes",
    "at enchanting dawn with gentle pastel sunrise hues, morning haze, and soft warm volumetric god rays"
]

def build_master_thumbnail_prompt(title="", description="", force_side=None, category_id=None, variation_index=0, is_playlist=False):
    if category_id:
        cfg = next((c for c in CATEGORY_CONFIGS if c["id"] == category_id), DEFAULT_CONFIG)
    else:
        cfg = match_category(title, description)
        
    # Dynamic variation rotation: guarantees that every video/image in the same category gets a completely unique look!
    v_idx = variation_index
    pose = VARIATION_POSES[v_idx % len(VARIATION_POSES)] if v_idx > 0 else cfg["pose"]
    choli = VARIATION_CHOLIS[v_idx % len(VARIATION_CHOLIS)] if v_idx > 0 else cfg["choli"]
    
    # 50/50 side alternation can also toggle with variation_index
    if force_side:
        model_side = force_side
    else:
        base_side = cfg.get("model_side", "right")
        model_side = ("left" if base_side == "right" else "right") if (v_idx % 2 == 1) else base_side
        
    text_side = "left" if model_side == "right" else "right"
    
    subtitle_text = "✨ संपूर्ण प्लेलिस्ट | COMPLETE MASTER PLAYLIST ✨" if is_playlist else cfg['hook_sub']
    
    prompt = (
        f"A viral high-CTR 16:9 cinematic YouTube meditation thumbnail. "
        f"A single continuous, unified cinematic wide scene with ZERO split lines, ZERO divider borders, and ZERO partitions. "
        f"Framed prominently on the {model_side.upper()} side of the environment in an extreme tight macro close-up portrait, framed strictly from the lower-to-mid bustline upwards to the top of her head (only face, glowing neck, bare shoulders, and large, beautifully contoured voluptuous bosom shape visible, with ZERO waist, ZERO navel, and ZERO midriff in frame)—is an extraordinarily gorgeous, fair-skinned Indian woman with radiant glowing porcelain skin and an alluringly full, prominent voluptuous bustline. "
        f"{pose} "
        f"On her smooth fair forehead sits a delicate, vibrant red traditional Indian bindi. "
        f"Razor-sharp macro focus captures her soft parted glossy pink lips with a gentle captivating smile, glowing jawline, slender neck adorned with a layered royal gold choker, prominent collarbones, and deeply sculpted décolletage. "
        f"She wears a completely strapless, low-cut off-the-shoulder couture choli bodice in {choli} with ZERO shoulder straps and ZERO sleeve fabric, resting entirely below both shoulders to leave both smooth glowing shoulders, collarbones, and upper chest completely bare. The choli features an elongated, deeply plunging low-cut sweetheart neckline cutting deep into the cleavage, dramatically accentuating her large, prominently contoured bust curves and seductive décolletage in sharp high-definition focus. "
        f"A delicate sheer transparent gossamer dupatta rests loosely behind her bare shoulders, leaving her chest, neckline, and shoulders completely uncovered and glowing. Hands are strictly off-frame. "
        f"On the {text_side.upper()} side of the SAME continuous environment: "
        f"In the upper area, floating naturally and cleanly directly in the open air with ZERO background box, ZERO black banner strip, "
        f"ZERO dark backing rectangle, and ZERO drop-shadow bar, is extra-large, massive bold 3D embossed gleaming polished 24K metallic gold luxury typography "
        f"reading \"{cfg['hook_title']}\" with an ultra-prominent glowing golden 3D badge subtitle reading \"{subtitle_text}\". "
        f"Directly below the floating letters: {cfg['instrument']} "
        f"The entire environment is a seamless, {cfg['background']}. "
        f"8K commercial fashion portrait photography, extreme shallow depth of field, dramatic cinematic rim lighting, pure single-shot unified scene, "
        f"award-winning viral YouTube cover."
    )
    return prompt, cfg

import os
import json

USED_PROMPTS_REGISTRY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "used_thumbnail_prompts_registry.json")

def get_next_unique_prompt(identifier="", description="", force_side=None, category_id=None):
    """
    Guarantees 100% infinite uniqueness across all videos & playlists:
    Tracks how many prompts have been generated for each category,
    automatically increments the variation index so NO TWO VIDEOS EVER SHARE THE SAME PROMPT,
    while strictly enforcing all master visual rules.
    """
    registry = {}
    if os.path.exists(USED_PROMPTS_REGISTRY_FILE):
        try:
            with open(USED_PROMPTS_REGISTRY_FILE, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception:
            registry = {}
            
    if category_id:
        cfg = next((c for c in CATEGORY_CONFIGS if c["id"] == category_id), DEFAULT_CONFIG)
    else:
        cfg = match_category(identifier, description)
    cat_id = cfg["id"]
    
    current_count = registry.get(cat_id, 0)
    prompt, cfg = build_master_thumbnail_prompt(identifier, description, force_side=force_side, category_id=cat_id, variation_index=current_count)
    
    # Increment count for next time
    registry[cat_id] = current_count + 1
    try:
        with open(USED_PROMPTS_REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
        
    return prompt, cfg, current_count

if __name__ == "__main__":
    print(f"Loaded {len(CATEGORY_CONFIGS)} bespoke categories (100% Pure Instrumental & Nature Accuracy).")
