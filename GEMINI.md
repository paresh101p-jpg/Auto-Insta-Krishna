# Image Generation Strategy for Krishna Music Videos (50+ Images)

**NOTE (User Instruction)**: Instagram quote/text images for Pooja and Krishna are discontinued.
All future image generation is dedicated strictly to **Krishna 16:9 Cinematic Music Video Images (`Auto-Insta-Krishna/music_video_images/`)**.

1. **Aspect Ratio**: Always 16:9 Landscape (1920x1080 / 4K / 8K cinematic).
2. **Clean Visuals (No Text / No Quotes)**: Absolutely ZERO quotes, text, watermarks, or typography on the images.
3. **Themes**: Ultra-realistic cinematic Lord Krishna in Vrindavan, playing flute under Kadamba tree, divine cows, Yamuna river ghats, sunrise/sunset golden hour lighting, peacocks, lotus ponds, and majestic divine scenery.
4. **Target Pool**: Minimum 50+ high-quality images stored in `Auto-Insta-Krishna/music_video_images/` for the automated 15-minute music video pipeline.


# Strict Account Separation & Content Segregation Rule (Krishna vs Pooja)
1. **100% Zero-Leak Isolation**:
   - Lord Krishna content (images, reels, audio, quotes, and URLs) MUST NEVER enter `Auto-Insta-Pooja`.
   - Pooja content (images, reels, URLs) MUST NEVER enter `Auto-Insta-Krishna`.
   - Both repositories, bots, image folders, and URL queues are 100% isolated and independent.
2. **Dedicated Queues & Scripts**:
   - `Auto-Insta-Krishna` strictly reads and writes to its own folders (`Auto-Insta-Krishna/Images/`, `Auto-Insta-Krishna/music_video_images/`) and its own URL queues (`images_urls.txt`, `reels_urls.txt`, `youtube_reels_urls.txt`, `suno_music_urls.txt`).
   - `Auto-Insta-Pooja` strictly reads and writes to its own folders (`Auto-Insta-Pooja/images/`) and its own URL queues (`images_urls.txt`, `reels_urls.txt`).
   - NEVER copy, move, mix, or cross-reference any file between these two directories under any circumstance.


# Unique Quotes for Krishna Images
Whenever you generate AI images for Krishna that include text/quotes:
1. ALWAYS read the file `e:\Paresh\Auto Post\Auto-Insta-Krishna\quotes.txt` to get the next available Hindi/Sanskrit spiritual thought. (Take quotes starting from the top of the file).
2. NEVER generate your own quotes. ONLY use the exact quotes provided in `quotes.txt`.
3. Explicitly pass the specific thought into the image generation prompt.
4. AFTER generating the image successfully, ALWAYS MOVE the used quote(s) from `quotes.txt` to `e:\Paresh\Auto Post\Auto-Insta-Krishna\used_quotes.txt`. This means you must delete the quote from `quotes.txt` and append it to `used_quotes.txt`. This ensures the quote is preserved as a backup but never repeated.

# Image Persistence and Addition Rule
Whenever new AI images are generated, they MUST be ADDED to the existing GitHub repository pool. You MUST NEVER delete, replace, or overwrite existing images when pushing new ones.

# Failed Posts Rule
If a post fails (e.g. due to an API error), the image MUST NOT be deleted. The image should be returned to the images/ folder so it can be picked up and tried again on the next run. Only images that successfully post to all platforms should be permanently removed on the subsequent run.

# User Uploaded Images Sync Rule
Whenever the USER manually adds new images to the local PC's images/ folder, DO NOT automatically push them to GitHub. Only push these manually added images to GitHub if the USER explicitly instructs you to do so (e.g., "images folder ki images github me send karo").

# Krishna Image Generation Prompt Template
Whenever you generate AI images for Krishna, you MUST use the following exact prompt structure:

Create a premium, ultra-realistic Instagram photograph.
TEXT + LOCATION:
"[WRITE YOUR TEXT] — physically written/printed/painted on [WRITE YOUR LOCATION]"
Make the text look 100% REAL and physically present on the specified location, like a professionally photographed real-world mockup — never like a digital overlay, pasted PNG, sticker, floating text or Photoshop layer.
Automatically adapt the typography to the exact surface: perspective, curves, folds, texture, grain, depth, shadows, highlights, reflections, lighting and imperfections. The text must naturally follow the surface and look as if it existed there before the photograph was taken.
Create artistic typography with BIG + small words, different premium fonts, slightly tilted/rotated/curved words, dynamic spacing, controlled overlap and 3–6 beautiful complementary colors. Keep everything stylish, balanced and highly readable.
Automatically choose the most realistic physical application method for the specified location.
Ultra-realistic commercial photography, cinematic lighting, realistic materials, professional composition, HDR, sharp details, premium editorial look.
Preserve the exact text spelling. No extra words, logos, watermark, gibberish or cropped letters.
The final image must look like a genuine real-life photograph with authentic physical typography integrated into the scene.

Notes:
1. Replace [WRITE YOUR TEXT] with a unique, trending Hindi spiritual thought. **CRITICAL: NEVER include "- राधे कृष्ण" or any other name at the end of the quote.**
2. Replace [WRITE YOUR LOCATION] with a creative physical location (e.g., old rustic wooden door, ancient stone wall, vintage diary, temple pillars, etc.).
3. ALWAYS include a beautiful flute (banshuri) and 2 peacock feathers (morpankh) placed beautifully in the scene.
4. ALWAYS write "PareshPadsala_" clearly visible at the bottom center of the image.

5. ALWAYS use a 3:4 Aspect Ratio for ALL generated images (Instagram Portrait). DO NOT use 1:1 or any other ratio.

# YouTube Shorts & Video Reel Generation Rules

Whenever you are generating video reels or YouTube Shorts from images (whether batch processing 2000+ images or single reels), you MUST ALWAYS strictly follow these rules:

### 1. Anti-Cropping & Aspect Ratio Rule (Blurred Ambient Background)
- Input images may be 4:5, 3:4, or other ratios.
- **NEVER crop or stretch the main image** when converting to 9:16 vertical (1080x1920). All text, quotes, signatures, and borders MUST be 100% visible.
- **ALWAYS use the Blurred Ambient Background method**:
  - Background: The original image scaled to fill 1080x1920 with heavy box blur (`boxblur=25:5`) and slight darkening (`eq=brightness=-0.09:saturation=1.15`).
  - Foreground: The uncropped main image fitted nicely in the center (`scale=1040:1750:force_original_aspect_ratio=decrease`) with a subtle elegant border/shadow (`pad=w=1044:h=ih+4:x=2:y=2:color=black@0.4`).

### 2. Dynamic Unblur Hook (Focus-Reveal Transition)
- Every reel MUST start with the foreground image blurred at Second 0.
- Between **Second 0 and Second 3.5 - 4.0**, the foreground MUST smoothly dissolve/transition from blurred to 100% crystal clear sharp focus (`blend=all_expr='if(lte(T,3.5), A*(1-T/3.5) + B*(T/3.5), B)'`).
- From Second 4 onwards until the end, it stays completely sharp.
- This creates an irresistible viewer retention hook that stops viewers from swiping away on YouTube Shorts & Instagram Reels.

### 3. Voiceover & Human Soul (Emotion-Adaptive Delivery)
- **Voice Gender**: ALWAYS use a **Male / Boy voice**. Never use female voice for Krishna quotes.
- **Voice Model**: Microsoft Madhur Neural (`hi-IN-MadhurNeural`).
- **Dynamic Emotion Adaptation (विचार के भाव के अनुसार आवाज़ बदलना)**:
  Every quote is unique, so the script MUST automatically detect the mood/emotion of the thought and adapt its vocal parameters:
  1. **संघर्ष से सफलता / सीख (Struggle to Victory - e.g., बदलाव, शुरुआत, कठिन, अंत):**
     - Phase 1 (कठिन शुरुआत): Slower, deeper empathetic tone (`rate="-12%", pitch="-2Hz"`).
     - Phase 2 (उलझन/मंथन): Thoughtful pause and steady pace (`rate="-10%", pitch="-1Hz"`).
     - Phase 3 (सुखद अंत/जीत): Uplifting, joyful, serene tone (`rate="-6%", pitch="+1Hz"`).
  2. **गंभीर / कर्म / कर्तव्य (Karma / Duty / Strength - e.g., कर्म, साहस, लक्ष्य, समय):**
     - Firm, confident, grounded guru delivery (`rate="-9%", pitch="-1Hz"`).
  3. **शांत / मौन / आत्मा / ध्यान (Peace / Meditation - e.g., शांति, मौन, क्रोध, आत्मा, ईश्वर):**
     - Ultra-calm, meditative, whisper-gentle cadence (`rate="-13%", pitch="-2Hz"`).
  4. **प्रेम / भक्ति / विश्वास (Devotion / Love / Faith - e.g., प्रेम, विश्वास, भक्ति, समर्पण):**
     - Warm, gentle, affectionate, soulful cadence (`rate="-8%", pitch="0Hz"`).
- **Human Emotion & Pauses (No Robotic AI Feel)**:
  - DO NOT read raw plain text in a single rush.
  - MUST split into natural breathing clauses at conjunctions (`जब... तब...`, `लेकिन...`, `क्योंकि...`, `और...`, commas) with `...` and 350ms–500ms pauses between thoughts.
  - Audio Mastering: Apply studio warmth (`bass=g=3:f=160,treble=g=2:f=3200`) and subtle divine room ambiance (`aecho=0.8:0.7:30:0.10`).

### 4. Background Music & AI Music Generation Rules (Treblo AI First & Live Stream Rule)
- **TREBLO AI MUSIC FIRST (Tier 1 Primary)**: All standalone 15-minute Krishna music videos strictly prioritize Treblo AI music (`treblo_music_urls.txt`) first. Only when the Treblo queue is 100% finished will it fall back to Suno AI music (`suno_music_urls.txt`). When both queues finish, it auto-recycles from Treblo backup pool.
- **24/7 YOUTUBE LIVE STREAM (100% TREBLO ONLY)**: The 24/7 YouTube live meditation stream on Oracle Cloud VPS strictly uses 100% Treblo AI music in an infinite seamless loop (`-stream_loop -1`). All Suno AI tracks are completely removed from the live stream playlist.
- **STRICT PROHIBITION ON `Auto-Insta-Krishna/music/`**: NEVER use, pick, copy, or read any music files from `Auto-Insta-Krishna/music/` under ANY circumstance. Using pre-existing tracks from this folder is 100% STRICTLY FORBIDDEN.
- **SINGLE TRACK PER MUSIC VIDEO RULE**: In every standalone 15-minute Krishna music video, strictly use **1 unique track** looped seamlessly with `-stream_loop -1` and smooth fade-in/fade-out to maintain deep meditative focus. Never mix or mash up different tracks within the same video.
- **True Melody & Rhythm (Taal & Dhun)**: AI music must have authentic Indian classical Bansuri flute melody and real Tabla beats/rhythm. Never produce empty or robotic monotone beeps.
- **Clean Visuals (No Quotes/Thoughts)**: For dedicated music videos and live streams, NEVER use Instagram quote/thought images. Always use clean, 100% text-free, 16:9 cinematic Lord Krishna images without any written text, quotes, or thoughts.
- Flute volume MUST be softly balanced at **14% - 15%** for voice reels, and 100% full master for music videos and live stream.
- BGM MUST have a smooth **1.2 to 1.5-second fade-out** at the end.
- Voice delay: Start the voice 0.6 to 0.7 seconds after video begins, allowing the viewer to first hear the flute music and experience the unblur transition.

### 5. Video Technical Specifications
- Resolution: **1080 × 1920 (9:16 Full HD Vertical)**.
- Frame Rate: **25 fps**, Codec: **libx264** (CRF 18), Audio: **AAC 192k**.
- Total Duration: Matches voice length + ~2 seconds padding (typically 15 to 20 seconds).

### 6. YouTube Partner Program (YPP) Monetization & Upload Automation Rules
Whenever uploading or generating metadata for YouTube Shorts:
1. **Meaningful Title Structure (Never post bare hashtags):**
   - Title MUST have the core wisdom/hook followed by hashtags.
   - Pattern: `[विचार का मुख्य सार/सीख] | श्री कृष्ण अमृत वचन #Shorts #Krishna #RadheKrishna`
   - Example: `बदलाव से कभी मत घबराओ | श्री कृष्ण अमृत वचन #Shorts #Krishna #RadheKrishna`
2. **Transparent AI Content Disclosure (Mandatory for Fast Approval):**
   - ALWAYS enable the `Altered or Synthetic Content` declaration in upload settings/API parameters (`hasCustomThumbnail=False`, `selfDeclaredMadeForKids=False`, synthetic media disclosure = true).
   - This complies with YouTube's 2024-2026 AI transparency policy and prevents any demonetization flags.
3. **Original Value Addition Guarantee:**
   - Every reel must incorporate the 4-layer signature: (a) Emotion-Adaptive Voiceover with pauses, (b) 0 to 3.5s Focus-Reveal Unblur Hook, (c) Studio-mastered Flute BGM, and (d) Visible creator brand watermark (`@PareshPadsala_` / `Krishna Vibez`).
4. **Description & Cross-Promotion (100% Thought-Adaptive Keywords & Hashtags):**
   - Include a concise 2-3 line spiritual summary of the thought + 3 practical life lessons + English wisdom summary.
   - **Reel-Specific Searches & Topics Block**: Dynamically generated `🔍 Searches & Topics Covered` block containing 6-8 search queries specifically matching what the reel is about (e.g., patience, anger, karma, hard times, faith) in Hindi and Hinglish.
   - **Reel-Specific Hashtags**: Base platform tags (`#Shorts #Krishna #RadheKrishna #KrishnaVibez #DailySuvichar`) followed by 5-8 hashtags that directly reflect the core topic of the reel (e.g. `#Dhairya #Patience #BuraWaqt #Samay` or `#Karma #KarmFal #Duty`).
   - **Thought-First Backend Tags**: YouTube API backend `tags` prioritizes the reel's specific search tags first, followed by anchor tags, capped at 480 chars.
   - Include direct links to the website (`https://krishnavibez.in/`), WhatsApp Channel (`https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J`), and Telegram (`https://t.me/krishnavibezz`).
5. **Multi-Candidate Auto-Recovery Loop (Crash-Proof Queue):**
   - NEVER crash the workflow if a single video URL fails download or video integrity check (e.g., missing `moov atom` or truncated upload).
   - Distinguish between Corrupted/404 files vs temporary network drops:
     - If confirmed corrupt (failed `verify_video_integrity()` due to truncated upload/missing `moov atom`) or HTTP 404: automatically prune and discard from `youtube_reels_urls.txt`.
     - If temporary network drop: preserve URL in queue and immediately attempt the next candidate reel.
   - The script attempts up to 5 distinct candidate reels per run, ensuring 99.9% uptime even if a few uploaded files in the queue were truncated.
6. **Native `curl` (HTTP/2 & TLS 1.3) Primary Download Engine:**
   - Always prioritize native `curl -s -L -f --retry 3` over Python's `requests`/`urllib3`.
   - **Root Cause & Reason**: Cloudflare and Catbox anti-bot firewall aggressively drop Python HTTP/1.1 socket connections from Microsoft Azure / GitHub Actions runner IPs (`Remote end closed connection without response`), while native `curl` negotiates HTTP/2 and modern TLS 1.3 smoothly in < 1 second.
   - Fallback chain: Primary `curl` ➔ Secondary `urllib.request` ➔ Tertiary `requests` (with `Connection: close`).
   - NEVER wrap video downloads with free web HTML proxies (e.g. `allorigins.win` or `corsproxy.io`) as they truncate binary streams and strip the `moov atom`.
7. **CI/CD System Dependencies (FFmpeg):**
   - In `.github/workflows/youtube_schedule.yml`, ALWAYS include `sudo apt-get update && sudo apt-get install -y ffmpeg` before running the Python script.
   - Required for OpenCV video reading, 4.0s sharp frame extraction, and anti-duplicate audio-visual variations.
8. **Gemini Vision Model & Active Discovery:**
   - Always use `gemini-3.8-flash`, `gemini-3.8-pro`, `gemini-3.7-flash` with dynamic `client.models.list()` fallback to ensure prompt metadata generation never fails due to deprecated models.
9. **Anti-Duplicate Fingerprint & Auto-Recycle Loop:**
   - Cycle 1: Upload pristine original voice reels without modifications from the master 2,000+ backlog.
   - Cycle 2+ (Looping): When `youtube_reels_urls.txt` runs out, it auto-reloads from `youtube_reels_urls_backup.txt`, shuffles them, and applies micro-speed/color grading variations via FFmpeg to guarantee 100% unique cryptographic file hash and pixel matrix.
10. **Automated Publishing Schedule & Queue Archiving:**
   - 3 Daily automated scheduled slots: `02:30 UTC` (08:00 AM IST), `08:30 UTC` (02:00 PM IST), `14:30 UTC` (08:00 PM IST) via GitHub Actions `youtube_schedule.yml` (`cron: '30 2,8,14 * * *'`).
   - Resumable YouTube Data API v3 upload (`insert(part="snippet,status", body=body, media_body=media)`).
   - Once uploaded successfully, URL is archived to `youtube_used_urls.txt`, removed from `youtube_reels_urls.txt`, and committed to GitHub `master` with automatic rebase retry.

### 6.1 YouTube Community Tab Image Post Automation Rules
1. **Strict Pipeline Separation**:
   - YouTube Shorts/Reels pipeline (`youtube_uploader.py`, `youtube_reels_urls.txt`, `.github/workflows/youtube_schedule.yml`) is 100% INDEPENDENT and MUST NEVER be touched or modified for community image posts.
2. **Dedicated Cloud URL Queue**:
   - Community posts strictly use `youtube_community_urls.txt` and archive used URLs to `youtube_community_used_urls.txt`.
   - Images are downloaded on-the-fly (`temp_community_image.jpg`) from Cloud CDN and deleted immediately upon post completion (0% disk space waste).
3. **Safety & Rate Limit Guards**:
   - Strictly maximum 2 community posts per day.
   - Enforce a minimum 4-hour gap between posts (timestamped in `youtube_community_history.json`).
4. **Image-Specific Thought Matching & SEO**:
   - Gemini Vision reads the exact thought from the image (or falls back to `quotes.txt`).
   - Generates thought-matched divine hook, spiritual meaning, 3 practical lessons, topic-specific search queries, and specific hashtags.
   - Moves used thoughts from `quotes.txt` to `used_quotes.txt`.
5. **Local Stealth Execution**:
   - Run exclusively via local Playwright with dedicated browser profile (`.youtube_community_profile/`) to eliminate datacenter IP blocks and protect the channel from any suspension or security challenges.
6. **Infinite Auto-Recycle Loop**:
   - When `youtube_community_urls.txt` runs out of URLs, the script automatically reloads all 2,000+ image URLs from `youtube_community_urls_backup.txt`, shuffles them randomly, increments the cycle in `youtube_community_cycle_tracker.txt`, and continues posting indefinitely without ever stopping.

### 7. Power Cut & System Restart Auto-Recovery Architecture (Crash-Proof)
Whenever power cuts, system reboots, or execution stops, the entire pipeline is designed to resume seamlessly without any data loss or duplicate work:
1. **Image Upload Auto-Resume**:
   - `uploaded_images_tracker.txt` permanently records every uploaded filename.
   - Upon restart, `catbox_uploader.py` reads this file, skips all completed images, and resumes immediately with the next pending image.
2. **Reel Generation Auto-Resume**:
   - Each reel `.mp4` is verified (>500 KB) before the corresponding source image in `new_video/` is deleted.
   - Upon restart, `batch_create_reels.py` only processes images that still exist in `new_video/`. Completed reels are untouched, ensuring zero wasted computation.
3. **Reel Upload Auto-Resume**:
   - `uploaded_reels_tracker.txt` tracks all uploaded reels.
   - `watch_and_upload_reels.py` automatically detects when `Images/` upload finishes and uploads pending reels.
4. **Single-Click Master Launch Script**:
   - Run `START_ALL_AUTOMATION.bat` from `Auto-Insta-Krishna/` to restart all workers in a single click after any reboot.
5. **Zero Interference with Scheduled Posts**:
   - Scheduled posting runs in GitHub Actions cloud.
   - All git sync scripts use `git pull --rebase origin master` so that cloud posts and local uploads never create merge conflicts.
### 8. Multi-Channel Social Syndication & Dailyhunt Ecosystem Rules

1. **WhatsApp Share & Telegram Button 512-Byte Bypass**:
   - **Pinterest Exclusion**: Pinterest links MUST NEVER be included in WhatsApp share text. Keep Pinterest only on the website and YouTube descriptions.
   - **Share Bridge**: Telegram `InlineKeyboardButton.url` strictly truncates links at 512 bytes. To prevent truncation of Devanagari Hindi thoughts and social links, ALWAYS use the smart website bridge URL: `https://krishnavibez.in/share.html?id=[POST_ID]&q=[ENCODED_QUOTE]`. This forwards the 100% complete, unclipped text with all official social links directly into WhatsApp.
   - **Open Graph (OG) Thumbnail Card**: WhatsApp crawler strictly rejects `og:image` files > 300 KB or non-image formats. ALWAYS use the optimized JPEG `https://krishnavibez.in/assets/krishna-og.jpg` (1200x630, ~100 KB) in `post.html` and `share.html`. Never set `og:image` to `.mp4` video files.

2. **Meta Threads Automated Broadcasting**:
   - Meta Threads API is 100% active and integrated under `@pareshpadsala_` (Threads User ID: `29921796124076935`).
   - Every daily scheduled post and reel automatically broadcasts simultaneously to Meta Threads via GitHub Actions (`schedule.yml`) without manual intervention.

3. **Dailyhunt (DH Creator) Syndication & Monetization**:
   - Account: Approved Creator with 18,600+ followers.
   - Creator Handle: `@KrishnaVibez`
   - Creator Profile: `Krishna Vibez` / Paresh Padsala (`paresh101p@gmail.com`).
   - Public Profile Link: `https://m.dailyhunt.in/profile/KrishnaVibez`
   - DH Creator Dashboard: `https://dhcreator.dailyhunt.in/app/profile`
   - Current Status: On Hold by Dailyhunt Support (Ticket `#36815474`, 17 Oct 2026: "Bank approval and RSS Feed process is now on hold, will reach out once requirements arise"). Creator account `@KrishnaVibez` remains active and safe.
   - KYC & Banking: Axis Bank (A/C `915010046668776`, IFSC `UTIB0002083`, PAN `AVKPP7401M`), Signature & KYC documents uploaded.
   - Automated Content Ingestion: Syndicated via Media RSS (MRSS) feed at `https://krishnavibez.in/rss.xml`.
   - Both 4K Images (`type="image/jpeg"`) and Video Reels (`type="video/mp4"`) are automatically generated and looped continuously from the master 2,000+ backlog.

### 8.1 WhatsApp Channel Post Automation Rules
1. **100% Ban-Proof Architecture**:
   - Uses real local Chromium via Playwright on residential IP (`.whatsapp_channel_profile/`).
   - Meta Multi-Device authorized: acts as official secondary linked device (never conflicts with personal phone or personal browser WhatsApp).
2. **Alternating Reel & Image Engine**:
   - Alternates strictly every post: **Reel ➔ Image ➔ Reel ➔ Image** (tracked via `whatsapp_last_post_type.txt`).
3. **Dedicated Independent Queues & Auto-Recycle**:
   - Dedicated `whatsapp_images_urls.txt` (2,009 items) + `whatsapp_images_urls_backup.txt`.
   - Dedicated `whatsapp_reels_urls.txt` (2,080 items) + `whatsapp_reels_urls_backup.txt`.
   - Infinite Auto-Recycle Loop restores and shuffles URLs independently whenever either queue finishes.
4. **Publishing Schedule, Gap & Auto-Catchup Policy**:
   - 3 Daily Target Slots: **09:00 AM IST**, **01:00 PM IST**, and **05:00 PM IST** (Task Scheduler tasks `WhatsApp_Channel_Poster_Slot1`, `Slot2`, `Slot3`).
   - Enforce a minimum **3-hour gap** between posts (timestamped in `whatsapp_history.json`).
   - **PC Power Cut / Boot Catchup**: Configured with `StartWhenAvailable = True`. If PC was turned off during scheduled time or for days, upon PC boot the task automatically fires, verifies >= 3 hours have passed since the last post, and immediately posts the next alternating item!
5. **AI Vision Thought-Matching**:
   - Gemini Vision reads the exact thought from the image or reel's 4.0s video frame, formats divine hook, spiritual meaning, and practical lessons using WhatsApp typography (`*bold*` & bullet points `•`).

### 9. Website UI/UX, SEO & Engagement Engine Rules (`krishnavibez.in`)

1. **Floating Like Button & Divine Petal Burst (`🪶`, `🌸`, `🪷`, `✨`)**:
   - **Locations**: Present on both Homepage feed cards (`.card-img-wrap`) and Post Detail page (`.post-detail-img-wrap`) at `bottom: 12px; left: 14px;`.
   - **Interaction**: Real-time counter toggle, saved to `localStorage` via `StatsManager`.
   - **Divine Burst Animation**: Clicking like triggers 14 animated particles (pink rose petals, lotus petals, peacock feathers, and divine sparkles) that float upward across the media for 2.6 seconds.
   - **Post Detail Sync**: Floating media like button and metrics strip like button (`#dLikeBox`) stay 100% in sync.

2. **Dedicated Quote Copy Buttons**:
   - **Feed Cards**: Sleek `[📋 कॉपी]` button inside `.card-quote-box`.
   - **Post Detail Page Quote Callouts**: Any `<blockquote>` inside `.post-content-body` automatically receives a `[📋 कॉपी]` button at the right end.
   - **Behavior**: Copies clean Hindi quote formatted as `"[QUOTE]" — श्री कृष्ण (via krishnavibez.in)`, turns button green with `✓ कॉपीड` for 2 seconds, and displays toast feedback.

3. **Instagram-Style Reels Engine (Global Sync & Audio Isolation)**:
   - **Hover Auto-Play**: Mouse enter starts reel; mouse leave pauses and resets.
   - **Global Pause Lock**: If user clicks center pause on any reel, auto-play is locked off globally until explicitly re-enabled.
   - **Global Sound Synchronization**: Unmuting/muting one reel updates the sound state across all reels. Only the hovered/active reel outputs audio.

4. **Hero Daily Divine Thought Rotation & Shuffle**:
   - **Automatic Daily Rotation**: Deterministic day-of-year calculation (`dayOfYear % DAILY_DIVINE_THOUGHTS.length`) ensures every single calendar day displays a fresh divine thought without manual updates.
   - **Instant Shuffle**: `[🔄 नया विचार]` button in the hero pill allows visitors to shuffle thoughts with a smooth fade-in/fade-out transition.

5. **SEO & Clean Typography Compliance**:
   - **Feed Card Titles**: Semantic `<h2>` preserved in DOM for Googlebot / JSON-LD schema crawling, visually hidden with `clip: rect(0,0,0,0)` to avoid duplicating the quote display on feed cards.
   - **Metric Numbers**: Universal compact formatting (`>= 1000 -> 1K, 1.2K, 1.5K, 3.4K, 1M`).
   - **4K Badges**: Every card displays `4K IMAGE` or `4K REEL` pill in bottom-right corner.

### 10. Contact Form & Delivery Architecture

1. **FormSubmit.co AJAX Integration**:
   - Form endpoint: `https://formsubmit.co/ajax/paresh101p@gmail.com`.
   - Permanently activated and whitelisted for `https://krishnavibez.in`.
   - Content-Security-Policy (CSP) in `website/firebase.json` explicitly whitelists `https://formsubmit.co` in `connect-src`.
   - Honeypot and custom subject configured (`🙏 [Krishna Vibez] नई इंक्वायरी: ...`).
   - Submissions show loading state (`⏳ संदेश भेजा जा रहा है...`) and return green success toast without page reloads.
   - Fail-safe fallback: If network blocks AJAX or ad-blocker interferes, automatically triggers pre-filled `mailto:support@krishnavibez.in` link.

2. **Clickable Contact Details**:
   - Support Email: `mailto:support@krishnavibez.in` (opens mail client).
   - Website: `https://krishnavibez.in` (opens in new tab).
   - Instagram: direct link to `https://www.instagram.com/pareshpadsala_/`.
   - Facebook: direct link to `https://www.facebook.com/1808917602588221`.
   - Styled with gold hover highlights and smooth transitions.

### 11. Zero-Cost & Strict Free-Tier Quota Guard Rule (बिल 0 रहना चाहिए - Zero Bill Policy)
1. **Absolute Zero Bill Policy**: Under NO circumstances should any paid bill, card debit, or fee ever be incurred from Google Cloud, ElevenLabs, Sarvam AI, or any other API.
2. **Local Character Tracker (`gcloud_usage_tracker.json`)**: Every single character synthesized must be counted and recorded with month/year.
3. **Strict Safety Ceiling (800,000 chars)**: Google Cloud TTS offers 1,000,000 characters free per month. A hard cut-off is strictly locked at 800,000 characters (leaving a massive 200,000 character safety buffer).
4. **Auto-Stop & Fallback**: If the safety ceiling is reached or free tier expires, the system MUST IMMEDIATELY STOP making API requests, notify Paresh bhai, and switch automatically to the 100% free offline engine (Edge-TTS). Never proceed with paid calls once free limits are reached.

### 12. Anchor Aadhya — AI & Future Tech News Channel Rules
1. **Absolute Standalone Independence**:
   - Location: `E:\Paresh\Auto Post\AI News Channel`.
   - Must NEVER be mixed, linked, or merged with `Auto-Insta-Krishna`, `Auto-Insta-Mojilo`, or `Auto-Insta-Pooja`.
2. **Daily 4:30 PM Research -> 5:00 PM YouTube Upload**:
   - 04:30 PM (16:30 IST): Automatic research fetches today's latest real AI & tech news, sources real photojournalism photos, renders full 1080p video (3.5 to 5 min), generates 1280x720 high-CTR thumbnail, and full Hinglish metadata (`RUN_DAILY_430PM.bat`).
   - 05:00 PM (17:00 IST): Automatic upload engine publishes video, thumbnail, and metadata directly to YouTube (`RUN_DAILY_5PM_UPLOAD.bat`).
3. **Anchor Aadhya Visual & Character Identity**:
   - Name: **आध्या** / **Anchor Aadhya** (Channel: **AI Aadhya**).
   - Voice: Microsoft Swara Neural (`hi-IN-SwaraNeural`).
   - Visuals: Gorgeous, glamorous Indian female news anchor with radiant glowing skin, expressive eyes, dazzling confident smile, and modern fitted crimson red/navy broadcast blazer with asymmetrical cuts.
   - Studio Branding: Digital studio monitors and desk plates must prominently display **"AI Aadhya"**.
   - Thumbnail Aspect Ratio: STRICT mathematical aspect ratio preservation `(crop_w/crop_h == target_w/target_h)`. Never stretch or distort facial features.
4. **YouTube Policy & YPP Compliance**:
   - Strict Anti-Tag-Stuffing Rule: NEVER put comma-separated lists of tags inside the description. Comma tags belong strictly in YouTube's backend `tags` field.
   - Description must contain engaging Hinglish narrative, exact timestamps/chapters, question of the day, channel mission, mandatory synthetic media disclosure, and 6-10 `#Hashtags`.
5. **100% Autonomous Broadcast TV Outro Architecture**:
   - Duration: Last 15–20 seconds of the video (Scene 6 Outro).
   - Zero Manual Studio Touch: The creator NEVER needs to open YouTube Studio to manually add end screen elements.
   - Autonomous Visual & Audio Sign-off:
     - Anchor Aadhya (`anchor_aadhya_outro.jpg`) warmly smiles on full broadcast studio frame.
     - Professional Animated Lower-Third Plate: `DAILY 5PM BULLETIN | ROZ SHAAM 5 BAJE NAYA VIDEO!`.
     - Animated Bullets: `• Like karo, doston ko share karo aur bell icon dabao` and `• Kal shaam 5 baje milte hain ek aur naye dhamake ke saath!`.
     - Scrolling Bottom Ticker Tape with daily 5 PM schedule and subscribe callout.
     - Audio: Natural, engaging sign-off inviting viewers to like, share, subscribe, and meet tomorrow at 5:00 PM.

### 13. Suno AI Music & 15-Minute Lord Krishna Flute Video Pipeline Rules

1. **User Suno Music Ingestion & Zero-Refusal Extraction Protocol**:
   - **Never Refuse Any Suno Link ("MP3 Nahi Hogi" is Strictly Forbidden)**: Whenever the USER provides any Suno share URLs (`https://suno.com/s/...` or `https://suno.com/song/...`) or files:
     - Automatically extract pristine, high-fidelity MP3 audio using the automated extractor engine (`resolve_suno_urls.py` / `batch_process_all_suno_urls.py`) via `api.sunodown.com` with dynamic rotating `Fingerprint-Id: str(uuid.uuid4())` to completely bypass daily download limits.
     - Strip all Suno metadata (`-map_metadata -1`) and apply 432Hz harmonic warmth EQ + subtle atempo normalization (`equalizer=f=432:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1.5:g=1.5,atempo=1.015,volume=1.05`).
     - Upload the mastered track to Catbox CDN (`https://catbox.moe/user/api.php`).
     - Append the direct Catbox URL to `suno_music_urls.txt` (active queue) and `suno_music_urls_backup.txt` (master backup pool).
     - **0% Local PC Disk Waste**: Immediately delete all temporary audio files (`.mp3`, `.m4a`) from local PC storage once uploaded to Catbox and synced to Oracle VPS. Local PC storage must remain clean and uncluttered.
     - Automatically commit and push `suno_music_urls.txt` and `suno_music_urls_backup.txt` to GitHub remote `origin master`.

2. **Unified Suno Auto-Sync (Music Videos + 24/7 Live Stream)**:
   - Every single Suno track added MUST automatically and simultaneously be synced to BOTH:
     1. Standalone full-length 15-minute Krishna Music Videos (`suno_music_urls.txt`).
     2. 24/7 YouTube Live Meditation Stream on Oracle Cloud VPS (`/home/ubuntu/krishna-live/music/` and `audio_playlist.txt`).
   - The user does NOT need to ask or say "live me add karo" — it must happen simultaneously and automatically every time.

3. **Single Track Per Music Video Rule**:
   - In every standalone 15-minute Krishna music video, strictly use **1 unique track** looped seamlessly with `-stream_loop -1` and smooth fade-in (3s) and fade-out (4s) to maintain deep meditative trance.
   - NEVER mix, mash up, or stitch different tracks within the same video.

4. **Channel Branding & Public Title Standards**:
   - **Mandatory Channel Signature**: Every title across Shorts, 15-Minute Music Videos, and Live Stream MUST end with `| Krishna Vibez`.
   - **Zero Technical Frequency Numbers**: NEVER write `432Hz` or technical frequency numbers in public video titles or thumbnail badges. Titles must remain purely devotional, spiritual, and meditative (e.g., `श्री कृष्ण बाँसुरी ध्यान संगीत | Deep Meditation & Inner Peace Flute Music | Krishna Vibez`).

5. **Strict Prohibition on Old Local Audio (`Auto-Insta-Krishna/music/`)**:
   - NEVER use, pick, copy, or read any music files from `Auto-Insta-Krishna/music/` under ANY circumstance. Pre-existing tracks from this folder are 100% strictly forbidden. Every single track must be pure Suno AI flute dhun.

6. **Thrice-Daily (07:00 AM, 01:00 PM & 07:00 PM IST) Automated Cloud Publishing**:
   - Runs 3 times daily at 07:00 AM IST (01:30 UTC), 01:00 PM IST (07:30 UTC), and 07:00 PM IST (13:30 UTC) via GitHub Actions (`krishna_music_video.yml`) and `cron-job.org` (`Krishna Music Video 1`, `Krishna Music Video 2`, and `Krishna Music Video 3`).
   - Reads the top URL from `suno_music_urls.txt` (or fallback `treblo_music_urls.txt`) via native `curl`.
   - Loops and masters audio seamlessly to exact 15:00.00 flat duration with 3s fade-in, 4s fade-out, and 432 Hz harmonic warmth EQ.
   - Selects 12 random slides from the 50+ master clean image pool (`music_video_images/`), applying alternating Ken Burns Zoom-In, Pan, and Zoom-Out with 1.5s crossfades and floating golden sparkles (`golden_sparkles_loop.mp4`).
   - Generates high-CTR Devanagari AI thumbnail, dynamic meditation title (<= 95 chars), and publishes directly to YouTube channel `Krishna Vibez`.
   - Moves used URL to `suno_music_used_urls.txt`, updates `suno_music_urls.txt`, and commits changes with `[skip ci]`.
   - **Infinite Auto-Recycle Loop**: When `suno_music_urls.txt` is exhausted, auto-reloads from `suno_music_urls_backup.txt`, shuffles them, increments `suno_music_cycle_tracker.txt`, and applies 432Hz anti-duplicate remastering to ensure 100% unique cryptographic file hash.
   - **NEVER manually run the workflow**: Runs strictly on schedule or when explicitly instructed by the user.

### 14. YouTube 24/7 Live Stream Description & SEO Standards
1. **Description Length & Completeness**:
   - The 24/7 Live Stream description (`update_live_stream_seo.py`) must NEVER be a short stub. It must always be comprehensive (~1,800 to 2,000 chars) with:
     - Divine Hook & spiritual meditation narrative.
     - Comprehensive "Ideal For" points (Deep Meditation, Dhyan, Yoga, Stress Relief, Deep Sleep, Insomnia, Work/Study Focus).
     - Full official ecosystem links: Website (`https://krishnavibez.in/`), YouTube (`@KrishnaVibezofficial`), WhatsApp Channel, Telegram, Instagram (`@pareshpadsala_`), Facebook Page (`1808917602588221`), Threads (`@pareshpadsala_`), and Pinterest (`MojiloMart`).
     - Amazon Storefront section: `https://www.amazon.in/shop/myhappybirthday` with official Amazon Associate legal disclosure.
     - Long-tail search keywords block & top devotional hashtags.
2. **Weekly Rotation**: Rotates through 4 weekly theme hooks and titles automatically via `update_live_stream_seo.py` without stopping or interrupting the stream.

### 15. YouTube Thumbnail Dual-Font Standard (Zero Tofu Box Rule) & Typography
1. **Root Cause Prevention**:
   - Standard English fonts (`arial.ttf`, `DejaVuSans`) do NOT contain Devanagari Hindi glyphs and result in square/tofu box (`□`) rendering artifacts in FFmpeg drawtext.
   - ALWAYS enforce **Dual-Font Rendering**:
     - English badges & branding: `arialbd.ttf` (or system English bold font).
     - Hindi Title & Subtitle: Dedicated Unicode font `NotoSansDevanagari-Bold.ttf` (stored locally in `Auto-Insta-Krishna/`).
2. **High-CTR Visibility Font Sizes**:
   - Main Hindi Title: **100px** font size (`#FFDF00` bright gold) with 6px solid black outline.
   - Hindi Subtitle: **62px** font size (pure white) with 4px black outline.
   - Category Badge: **42px** font size on goldenrod badge.
   - Bottom Contrast Gradient: Deep 450px solid/gradient dark overlay (`black@0.75`) to guarantee maximum contrast and readability across all mobile and TV screens.

### 16. Mojilo Shorts & Reels Generation Engine
1. **Technical Specifications**:
   - Location: `E:\Paresh\Auto Post\Auto-Insta-Mojilo`.
   - Script: `batch_create_mojilo_reels.py`.
   - Resolution: 1080x1920 (9:16 vertical full HD).
   - Duration: ~55 to 58 seconds (strict <60s Shorts limit).
   - Structure: 0–5s viral flash cut hook (15 rapid cuts), 5–52s cinematic smooth model pans/zooms into cotton fabric/collar/fit, last 6s flat t-shirt mockup hero frame + Call To Action.
   - Voiceover: `hi-IN-SwaraNeural` (+8% speed).
   - Audio Mix: Voiceover delayed by 5s (after viral hook), background music softly mixed with 1.5s fade-out at end.
2. **Crash-Proof Resume Tracker**:
   - Completed folders are logged into `uploaded_mojilo_reels_tracker.txt`.
### 17. Master AI Music Inventory & Treblo Sequential Queue Architecture (Permanent Lifetime Record)
1. **Permanent Suno AI Music Inventory Count (Lifetime Record - Even After 2+ Years)**:
   - **Total Master Backup Tracks**: Exactly **751 Unique Suno Tracks** (`suno_music_urls_backup.txt`).
   - **Active Pending Queue (Current)**: **743 Tracks** (`suno_music_urls.txt`).
   - **Initial Uploaded/Used**: **7 Tracks** (`suno_music_used_urls.txt`).
   - **User Shared Backlog Pool**: **461 Tracks** (`ALL_USER_SUNO_TRACKS_300_PLUS.txt`).
2. **Treblo AI Music Inventory (Sequential Fallback & 24/7 Live Stream)**:
   - Folder: `Auto-Insta-Krishna/Treblo Music/` (0 loose files in inbox) and `Auto-Insta-Krishna/Treblo Music/uploaded/` (Archived).
   - Dedicated Queues: `treblo_music_urls.txt` (Active: **208 Tracks**), `treblo_music_urls_backup.txt` (Master Pool: **208 Tracks**), `treblo_music_used_urls.txt`.
   - **Sequential Priority Rule**:
     - **Tier 1 (Primary)**: Always prioritize and play through Suno AI tracks (`suno_music_urls.txt`).
     - **Tier 2 (Treblo Takeover)**: When Suno music queue runs out / is depleted (`not suno_urls`), the pipeline automatically transitions seamlessly to Treblo music tracks (`treblo_music_urls.txt`).
     - **Tier 3 (Infinite Loop)**: When both queues run out, it increments cycle, shuffles backup pools, and restarts seamlessly.
   - **Treblo Processing & Mastering Standards**:
     - All tracks undergo automated cleaning via `process_treblo_music.py`:
       - 100% metadata stripped (`-map_metadata -1`).
       - 432Hz harmonic meditation EQ applied.
       - Mastered to 320kbps MP3 and uploaded to Catbox CDN (`files.catbox.moe`).
       - Original files archived to `Treblo Music/uploaded/` so local disk remains light and clean.
     - Also synced to Oracle Cloud VPS 24/7 Live Stream (`/home/ubuntu/krishna-live/music/`).
3. **Automated AI Content Disclosure (`containsSyntheticMedia = True`)**:
   - Every video upload across all channels (Krishna music videos, Krishna shorts, Anchor Aadhya news) automatically passes `"containsSyntheticMedia": True` in the YouTube Data API `status` object and includes the full legal disclosure in the description.

### 18. Oracle Cloud VPS 24/7 Live Stream Permanent Engine (`krishna-live.service`)
1. **Host & Connection Specifications**:
   - Server: Oracle Cloud Always-Free Enterprise VPS (`bharatflow-ubuntu`, IP: `92.4.66.182`, User: `ubuntu`).
   - Authentication: SSH Key `e:\Paresh\Auto Post\ssh_oracle.key` (`-o BatchMode=yes -o StrictHostKeyChecking=no`).
   - Service Daemon: `sudo systemctl status/restart krishna-live.service` (`/etc/systemd/system/krishna-live.service`, `Restart=always`).
   - Python Engine: `/home/ubuntu/krishna-live/venv/bin/python3 -u /home/ubuntu/krishna-live/live_stream_server.py`.
2. **Zero-CPU Streaming & Keyframe Standards**:
   - Video Codec: `-c:v copy` streaming directly from pre-rendered base loop (`live_base_video.mp4`, 2.0s GOP keyframes).
   - CPU Load: **< 1% CPU** (Zero encoding strain, eliminating buffering and preventing server crash).
   - Ingestion Health: YouTube Data API status strictly **Good (Green)** with `configurationIssues: []`.
   - Streaming Target: YouTube RTMP (`rtmp://a.rtmp.youtube.com/live2/9zzv-8p2v-7gdx-8kbx-b2kj`).
3. **100% Treblo Audio Infinite Loop Architecture**:
   - Audio Directory: `/home/ubuntu/krishna-live/music/treblo/` (119+ unique Treblo tracks, strictly 0 Suno).
   - Playlist File: `/home/ubuntu/krishna-live/audio_playlist.txt` (5,950+ loop entries = 119 tracks × 50 repetitions, 350 KB text file).
   - Infinite Playback: Wrapped with `-stream_loop -1` in FFmpeg, ensuring that when entry 5,950 finishes (~17 days of non-stop playback), it seamlessly loops back to entry 1 without 1 second of pause.
   - Storage Capacity: VPS has 26 GB free disk space (only 880 MB used by music), easily accommodating 2,500+ additional tracks.
4. **Local PC Freedom**:
   - PC streaming (`start_youtube_live_pc.py`, `task-2036`) is permanently turned off.
   - Live stream runs 24/7/365 entirely in the cloud, allowing the user to turn off or reboot their local PC anytime without impacting the stream.

### 19. YouTube Partner Program (YPP) Monetization & Policy Compliance Matrix (2024–2026 Guidelines)
To guarantee 100% approval for YouTube monetization across **LIVE Streams**, **15-Min Music Videos**, and **YouTube Shorts**, every automated pipeline strictly complies with YouTube's core policies:

1. **YouTube "Reused Content" & "Repetitive Content" Policy Compliance**:
   - **Why Content Gets Flagged (What NOT to do)**: Channels that upload raw static image + unedited stock music without transformation or branding are rejected under "Reused Content".
   - **How Our Content Guarantees Monetization**:
     - **Original Value Addition**: 
       * (a) Custom-rendered 1080p base loop with dynamic 3D Morpankh fluttering, image-adapted golden sparkles, subpixel Ken Burns motion, and permanent creator watermark/logo (`@PareshPadsala_` / `Krishna Vibez`).
       * (b) Custom-mastered 432 Hz harmonic tuning + 1.5% micro-speed shift, creating a unique cryptographic audio matrix distinct from raw AI outputs.
       * (c) High-CTR bilingual dual-font thumbnails (`arialbd.ttf` + `NotoSansDevanagari-Bold.ttf`).
2. **YouTube Shorts Monetization Standards**:
   - **4-Layer Human Soul Signature**:
     1. Emotion-Adaptive Voiceover with human breathing pauses (Microsoft Madhur Neural) matching the mood of the thought.
     2. Dynamic 0 to 3.5s Focus-Reveal Unblur Hook that maximizes initial 3-second retention (stops swipe-away).
     3. Classical Flute BGM balanced at 14–15% volume with gentle 1.5s fade-out.
     4. Blurred ambient background with uncropped central image, preserving 100% text readability.
   - **Metadata & YPP Discovery**:
     - Meaningful titles (`[विचार का मुख्य सार] | श्री कृष्ण अमृत वचन #Shorts`).
     - Thought-adaptive descriptions with 3 practical life lessons + specific search tags.
3. **15-Minute Standalone Music Videos Monetization Standards**:
   - 60+ Clean 16:9 8K Cinematic Krishna Images (slide-by-slide transitions, no repetitive single image).
   - Single unique Treblo AI flute composition per video for pure meditative relaxation (no erratic audio changes).
   - In-depth descriptions outlining meditation, sleep benefits, and frequency explanations.
4. **YouTube AI & Synthetic Media Transparency (2024–2026 Policy)**:
   - Mandatory AI Content Disclosure: All uploads declare `containsSyntheticMedia = True` in YouTube API parameters.
   - Disclosing AI-generated media under YouTube's guidelines protects the channel from algorithmic suppression, demonetization, or copyright flags.

### 20. CorelDRAW & Design Explorer Freeze Troubleshooting Protocol
- **Issue Tracked (27 Oct 2026)**: CorelDRAW freezing/jamming on Save, Close, and `D:\Design\DTF Sticker PNG` folder freezing/jamming during file search.
- **Root Causes**:
  1. Windows File Dialog attempting to render metadata/thumbnails for thousands of high-res PNG files optimized as "Pictures".
  2. Windows `%temp%` clutter with orphaned Corel lock files (`cor*.tmp`, `@backup_*.cdr`).
  3. Corrupted CorelDRAW Workspace cache (persists even after reinstallation).
  4. Corel Graphics - Windows Shell Extension (`CdrShellExt.dll`) hanging Explorer preview handlers.
  5. Windows Default Printer query hang on GDI calls during Save/Close.
- **Resolution Steps Active After PC Reboot**:
  1. **F8 Reset on Launch**: Hold `F8` key while launching CorelDRAW -> Click "Yes" to restore clean factory workspace.
  2. **Folder Template**: `D:\Design\DTF Sticker PNG` Properties -> Customize -> Set "Optimize for General items" + apply to all subfolders.
  3. **Temp Clean**: Clear `%temp%` folder periodically.
  4. **Printer Setting**: Keep "Microsoft Print to PDF" as default Windows printer.
  5. **Shell Extension**: Uninstall "Corel Graphics - Windows Shell Extension" from `appwiz.cpl` if preview hang persists.

