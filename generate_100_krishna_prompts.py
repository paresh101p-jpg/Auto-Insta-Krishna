#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates 100+ Master 16:9 Cinematic Krishna Image Prompts (1-Click Copy Ready)
Outputs:
1. KRISHNA_100_PROMPTS_ONE_CLICK.html (Interactive web app with 1-click clipboard copy)
2. KRISHNA_100_CINEMATIC_PROMPTS.txt (Plain text list formatted with clear numbered blocks)
"""

import os
import sys
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"E:\Paresh\Auto Post\Auto-Insta-Krishna"

categories = {
    "flute_kadamba": [
        "under a sacred blooming Kadamba tree on the tranquil banks of river Yamuna during magical golden hour sunset, soft sunbeams filtering through leaves",
        "seated gracefully on ancient mossy carved stone stairs under a grand Kadamba tree, playing golden bansuri as gentle breeze sways divine floral garlands",
        "leaning serenely against a giant flowering Kadamba tree, soft afternoon sunlight casting golden dappled shadows over his radiant face",
        "playing bansuri beneath Kadamba branches laden with fragrant orange blossoms, divine butterflies fluttering in the warm golden mist",
        "resting peacefully on a velvet royal chawki under the Kadamba canopy, divine flute melodies echoing across the serene waters at twilight",
        "playing bansuri under Kadamba tree as glowing fireflies gently illuminate the peaceful twilight ambiance",
        "seated cross-legged in deep meditation with bansuri held gently, under majestic ancient Kadamba branches by the river edge",
        "playing the flute at sunrise under Kadamba tree, misty pink and golden sky creating heavenly ethereal reflections on the calm waters",
        "under a blossoming Kadamba tree with vibrant yellow flowers raining gently down around him as he plays the divine bansuri",
        "standing gracefully in tribhanga posture playing bansuri under the shade of a sacred Kadamba tree overlooking rolling green Vrindavan pastures"
    ],
    "yamuna_ghats": [
        "sitting on ancient Keshi Ghat stone steps at dusk, hundreds of tiny glowing clay diyas floating gently on the sacred Yamuna river",
        "walking barefoot on the pristine white sands of Yamuna river at dawn, early morning golden fog rising softly from the calm waters",
        "playing bansuri on an ornate marble Yamuna pavilion at sunset, golden water ripples reflecting deep orange and violet twilight skies",
        "sitting on stone steps of Vrindavan ghat surrounded by blooming pink water lilies, holy Yamuna river glistening like molten gold",
        "standing on a rustic wooden boat floating peacefully on the sacred Yamuna river, distant temple shikhara silhouetted in the sunset haze",
        "playing flute at the edge of the sacred river as gentle water waves lap softly against his lotus feet",
        "seated on a carved sandstone ghat platform at sunrise, flock of white cranes flying across the golden Yamuna horizon",
        "playing bansuri by the Yamuna at golden hour, traditional river ghats and ornate stone chattris glowing in warm amber light",
        "standing on the peaceful riverbank as the evening twilight paints the water with shades of purple, indigo, and gold",
        "sitting on a ghat bench under a canopy of jasmine flowers overlooking the vast tranquil Yamuna river at sunset"
    ],
    "gau_seva": [
        "surrounded by gentle white Surabhi cows resting peacefully in lush green meadows, caressing a baby calf with divine maternal love",
        "playing sweet bansuri melodies for a herd of sacred white cows adorned with brass bells and flower garlands under a banyan tree",
        "sitting in a lush Vrindavan pasture, an affectionate white calf resting its head softly in his lap as he plays the flute",
        "walking through flowering Vrindavan pastures at Godhuli Bela (cow dust hour) with gentle cows walking beside him in golden sunset glow",
        "playing bansuri atop a gentle grassy hill surrounded by serene cows and playful calves grazing peacefully in the golden light",
        "embracing a loving white Kamadhenu cow with painted blue horns and fragrant marigold garland in a traditional Vrindavan goshala",
        "playing flute in an open meadow as gentle cows listen intently with closed eyes in deep spiritual trance",
        "sitting on a rustic wooden cart surrounded by grazing cows in lush tall green grass sprinkled with wild yellow flowers",
        "resting by a peaceful lotus pond with friendly white cows drinking crystal clear water beside him in early morning golden light",
        "walking through a mist-covered pasture at dawn playing sweet flute notes as calves run joyfully in the morning dew"
    ],
    "peacocks": [
        "sitting under a flowering tree while two majestic Vrindavan peacocks dance joyfully with fully spread iridescent feathers",
        "playing bansuri on a mossy stone platform with a colorful peacock perched lovingly on a Kadamba branch above him",
        "standing gracefully as a majestic peacock displays its emerald and sapphire fan of feathers in the soft evening golden sunlight",
        "playing the flute in a forest clearing while a circle of wild peacocks listen peacefully with divine devotion",
        "sitting on an ornate stone bench, gently feeding wild peacocks with a peacock feather gracefully adorning his golden crown",
        "walking through a forest path surrounded by flying and dancing peacocks, their iridescent feathers catching the twilight glow",
        "seated beside a calm river with a pair of royal peacocks drinking water near his lotus feet while he plays sweet melodies",
        "playing bansuri on a terrace garden overlooking Vrindavan forest, with wild peacocks calling in the golden sunset distance",
        "standing by a tranquil water fountain in a divine palace courtyard surrounded by radiant peacocks resting on stone railings",
        "playing flute in rain-drenched Vrindavan forest while peacocks dance ecstatically in the gentle mist and falling droplets"
    ],
    "lotus_ponds": [
        "sitting on a carved marble step by a vast pond covered with hundreds of blooming sacred pink lotuses and floating lily pads",
        "standing on a wooden bridge arching over a tranquil lotus pond, golden sunset reflections shining between large green leaves",
        "playing bansuri in the center of a calm lake filled with glowing white and pink lotuses, water as smooth as glass",
        "resting gracefully on a stone ghat overlooking a sacred lotus sarovar, divine golden light piercing through morning mist",
        "playing flute while seated on a giant green lotus leaf platform in the middle of a divine Vrindavan lake",
        "standing beside a serene mountain pond filled with radiant blue and purple lotuses, gentle mountain breeze swaying his pitamber",
        "sitting on the edge of sacred Radha Kund filled with blooming lotuses, soft temple bells chiming in the quiet sunset breeze",
        "playing bansuri on a stone pavilion surrounded on all four sides by tranquil lotus waters and gentle water ripples",
        "seated peacefully near a natural lotus spring, crystal clear water trickling between smooth river stones and water lilies",
        "playing flute at twilight by an ancient temple pond where floating lotus flowers glow softly in the evening shadows"
    ],
    "nidhivan_forest": [
        "walking through the mystical, twisted ancient tulsi and kadamba groves of sacred Nidhivan under soft ethereal moonlight",
        "playing bansuri in a secluded Vrindavan grove surrounded by fragrant white night-blooming jasmine and blooming parijat trees",
        "sitting beneath intertwining sacred trees in Nidhivan, divine soft blue and golden luminescence glowing softly in the quiet night",
        "playing flute in an enchanted dense forest clearing where rays of golden sunset light pierce dramatically through tall tree trunks",
        "seated on a stone bench in a serene bamboo grove in Vrindavan, bamboo leaves rustling gently in the divine evening breeze",
        "walking along a quiet moss-covered forest trail surrounded by wild deer and gentle rabbits listening to the flute melody",
        "playing bansuri deep inside the sacred forest, ancient banyan tree roots hanging gracefully in the ethereal mist",
        "sitting beside a sparkling forest brook, crystal clear water cascading over smooth pebbles beneath a canopy of green leaves",
        "resting peacefully against a mossy boulder in Vrindavan forest, golden autumn leaves drifting softly through the air",
        "playing flute at the edge of the sacred woods overlooking distant glowing temple spires at twilight"
    ],
    "govardhan_hill": [
        "sitting atop the sacred rocks of Govardhan hill at sunrise, overlooking the vast green plains and lakes of Braj in morning mist",
        "playing bansuri on a scenic sandstone cliff of Govardhan, golden morning light illuminating the rocky landscape and wild peacock paths",
        "walking along the sacred Govardhan parikrama path surrounded by ancient trees, flowering shrubs, and peaceful pilgrims path",
        "seated near the sacred waters of Mansi Ganga at Govardhan, stone steps and ornate chattris glowing in warm twilight",
        "playing flute on a rocky plateau of Govardhan hill with divine white cows grazing peacefully on the green terraces below",
        "sitting by sacred Kusum Sarovar at Govardhan, magnificent Rajasthani sandstone pavilions reflected in the tranquil water",
        "playing bansuri beside a natural rock cave on Govardhan hill surrounded by wild blooming yellow and red forest flowers",
        "standing on the heights of Govardhan hill as dramatic golden sunset clouds roll across the sacred Braj sky",
        "resting beneath a shaded tree on Govardhan slopes, gentle mountain breeze blowing through his yellow silk garments",
        "playing flute near the sacred rock carvings of Govardhan, peaceful deer and birds gathered around in tranquil harmony"
    ],
    "night_moonlight": [
        "sitting on the Yamuna riverbank under the radiant full moon of Sharad Purnima, moonlight creating a shimmering silver path on the water",
        "playing bansuri on a white marble terrace at midnight, billions of brilliant stars and the Milky Way shining brightly in the deep blue sky",
        "seated peacefully beneath a grand banyan tree under a starlit night sky, glowing fireflies dancing in the serene darkness",
        "playing flute on a stone ghat at midnight, cool silver moonlight bathing the tranquil temple waters and blooming night lotuses",
        "walking along the calm Yamuna shore beneath the glowing crescent moon, soft ripples reflecting stars like scattered diamonds",
        "playing bansuri in a moonlit forest grove where cool blue mist and silvery beams of light create an ethereal divine dreamscape",
        "sitting on a carved boat floating quietly on river Yamuna under the vast starry night, glowing oil lamps reflecting softly",
        "playing flute beside a sacred temple pond at night, illuminated oil lamps and cool moonlight blending in mystical harmony",
        "resting gracefully on a stone bridge beneath the full moon, silhouetted kadamba trees framing the peaceful nocturnal scene",
        "playing sweet bansuri melodies under a starry Vrindavan sky, soft silver luminescence illuminating his peaceful divine face"
    ],
    "aarti_devotion": [
        "sitting on an ornate Vrindavan ghat while hundreds of golden brass oil lamps and aarti diyas glow warmly around him in the twilight",
        "playing bansuri beside a divine temple altar adorned with fresh red roses, white jasmine garlands, and fragrant sandalwood paste",
        "seated gracefully on a carved teakwood jhula (swing) decorated with thick garlands of fragrant flowers, swaying gently in the breeze",
        "playing flute in an open-air temple courtyard as fragrant dhoop and incense smoke rises gracefully into the warm evening sky",
        "standing on the grand steps of a sacred Vrindavan temple at Sandhya Aarti, temple bells softly chiming and brass lamps glowing",
        "seated near floating river diyas carrying golden flames across the dark Yamuna water, creating a river of light and devotion",
        "playing bansuri surrounded by offerings of fresh seasonal fruits, sacred tulsi leaves, and golden marigold petals",
        "sitting in a peaceful temple verandah overlooking the sanctum, glowing ghee lamps creating warm golden bokeh in the background",
        "playing flute during festive Diwali twilight in Vrindavan, thousands of tiny oil lamps outlining every ghat, terrace, and step",
        "standing gracefully beside a sacred stone shrine draped in fresh flower malas, soft golden illumination radiating all around"
    ],
    "monsoon_rain": [
        "sitting peacefully under the shelter of an ornate stone chattri pavilion while gentle monsoon rain falls on the lush green gardens outside",
        "playing bansuri on a wooden veranda as refreshing rain showers create dancing ripples across the Yamuna river, sweet petrichor mist",
        "standing gracefully under a wide Kadamba tree whose broad green leaves provide natural shelter from gentle tropical rain showers",
        "playing flute while warm monsoon raindrops glisten like pearls on lotus leaves and pink flowers in a peaceful pond",
        "sitting on the dry steps of a temple porch watching monsoon clouds and a vibrant rainbow arch gracefully over Vrindavan",
        "playing bansuri as soft rain mist rolls gently over the river, water droplets glistening on his peacock feather and golden crown",
        "seated beside a cascading fresh monsoon stream flowing through the sacred forest, cool rain breeze swaying the trees",
        "playing flute on a covered balcony overlooking rain-swept Vrindavan pastures, cattle sheltering peacefully under banyan trees",
        "standing beside a calm rain-drenched lotus pool, raindrops falling softly through the golden afternoon light",
        "playing sweet melodies as gentle monsoon showers subside, revealing brilliant golden sunlight breaking through retreating clouds"
    ]
}

def generate():
    total_count = 0
    all_prompts = []

    base_prefix = "Ultra-realistic cinematic 16:9 landscape photography of divine Lord Krishna "
    base_suffix = ", peaceful meditative atmosphere, sharp focus, 8k resolution, photorealistic masterpiece, cinematic lighting, ultra-detailed, depth of field, National Geographic editorial look. Clean visual, absolutely zero text, no quotes, no watermarks, no typography, 16:9 aspect ratio."

    for cat_name, scenarios in categories.items():
        for sc in scenarios:
            total_count += 1
            prompt_text = f"{base_prefix}{sc}{base_suffix}"
            all_prompts.append({
                "id": total_count,
                "category": cat_name,
                "scenario": sc[:60] + "...",
                "prompt": prompt_text
            })

    # 1. Write Text file
    txt_path = os.path.join(BASE_DIR, "KRISHNA_100_CINEMATIC_PROMPTS.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("===============================================================================\n")
        f.write("  KRISHNA VIBEZ — 100+ MASTER 16:9 CINEMATIC IMAGE PROMPTS (1-CLICK READY)\n")
        f.write("===============================================================================\n")
        f.write("Rules: 16:9 Landscape, 100% Clean (Zero Text / Zero Quotes / Zero Watermarks)\n")
        f.write("Usage: Copy any prompt below and paste into Midjourney, Fooocus, DALL-E, etc.\n")
        f.write("===============================================================================\n\n")
        for p in all_prompts:
            f.write(f"PROMPT #{p['id']:03d} [{p['category'].upper()}]:\n")
            f.write(f"{p['prompt']}\n\n")

    print(f"✅ Saved TXT file with {len(all_prompts)} prompts: {txt_path}")

    # 2. Write 1-Click Interactive HTML
    html_path = os.path.join(BASE_DIR, "KRISHNA_100_PROMPTS_ONE_CLICK.html")
    escaped_json = json.dumps(all_prompts).replace("</script>", "<\\/script>")

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Krishna Vibez — 100+ Master Cinematic 16:9 Prompts (1-Click Copy)</title>
    <style>
        :root {
            --bg-dark: #0a0e17;
            --card-bg: #111827;
            --accent-gold: #f59e0b;
            --accent-cyan: #38bdf8;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg-dark);
            color: var(--text-main);
            padding: 30px 20px;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            max-width: 900px;
            margin: 0 auto 30px auto;
        }
        h1 {
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, #fbbf24, #f59e0b, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        p.subtitle {
            color: var(--text-muted);
            font-size: 16px;
            margin-bottom: 20px;
        }
        .stats-badge {
            display: inline-block;
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.4);
            color: #fbbf24;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
        }
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #10b981;
            color: white;
            padding: 14px 24px;
            border-radius: 12px;
            font-weight: 700;
            box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        .toast.show {
            opacity: 1;
            transform: translateY(0);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 20px;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, border-color 0.2s;
        }
        .card:hover {
            transform: translateY(-4px);
            border-color: rgba(245, 158, 11, 0.5);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .card-num {
            font-size: 14px;
            font-weight: 800;
            color: var(--accent-gold);
            background: rgba(245, 158, 11, 0.1);
            padding: 4px 10px;
            border-radius: 8px;
        }
        .card-cat {
            font-size: 12px;
            text-transform: uppercase;
            font-weight: 600;
            color: var(--accent-cyan);
            letter-spacing: 0.5px;
        }
        .prompt-box {
            background: #090d16;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 14px;
            font-size: 13.5px;
            line-height: 1.5;
            color: #d1d5db;
            margin-bottom: 16px;
            max-height: 150px;
            overflow-y: auto;
            word-break: break-word;
        }
        .copy-btn {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: #fff;
            border: none;
            padding: 12px 18px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s;
        }
        .copy-btn:hover {
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
        }
        .copy-btn.copied {
            background: #10b981 !important;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🪷 100+ Krishna Cinematic 16:9 Master Prompts</h1>
        <p class="subtitle">1-Click Copy Ready • 16:9 Ultra HD • Zero Text • 100% Clean Visuals</p>
        <span class="stats-badge">✨ 100 Divine Scenarios Generated</span>
    </div>

    <div class="container" id="cardsGrid"></div>
    <div class="toast" id="toast">✅ Prompt Copied to Clipboard!</div>

    <script>
        const prompts = __PROMPTS_JSON__;
        const grid = document.getElementById('cardsGrid');
        const toast = document.getElementById('toast');

        function showToast(msg) {
            toast.textContent = msg;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2000);
        }

        prompts.forEach(p => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <div>
                    <div class="card-header">
                        <span class="card-num">#` + String(p.id).padStart(3, '0') + `</span>
                        <span class="card-cat">` + p.category.replace('_', ' ') + `</span>
                    </div>
                    <div class="prompt-box">` + p.prompt + `</div>
                </div>
                <button class="copy-btn" onclick="copyPrompt(this, ` + p.id + `)">
                    📋 1-Click Copy Prompt
                </button>
            `;
            grid.appendChild(card);
        });

        function copyPrompt(btn, id) {
            const item = prompts.find(x => x.id === id);
            if (!item) return;
            navigator.clipboard.writeText(item.prompt).then(() => {
                btn.textContent = '✅ Copied to Clipboard!';
                btn.classList.add('copied');
                showToast('✅ Prompt #' + String(id).padStart(3, '0') + ' Copied!');
                setTimeout(() => {
                    btn.textContent = '📋 1-Click Copy Prompt';
                    btn.classList.remove('copied');
                }, 2200);
            });
        }
    </script>
</body>
</html>"""

    final_html = html_template.replace("__PROMPTS_JSON__", escaped_json)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✅ Saved HTML 1-Click tool: {html_path}")

if __name__ == "__main__":
    generate()
