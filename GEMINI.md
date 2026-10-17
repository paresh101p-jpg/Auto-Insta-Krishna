# Image Generation Strategy for Krishna & Pooja

Whenever you are instructed to generate images for "Pooja" or "Krishna", ALWAYS perform this check first:
1. Count the number of images currently in the GitHub `images/` folder (local repo folder) for `Auto-Insta-Krishna` and `Auto-Insta-Pooja`.
2. Compare the counts. 
3. Whichever account has FEWER images at the START of the generation process, generate the ENTIRE batch of images for THAT specific account until the daily/session limit is reached.
   - Example: If Krishna has 5 and Pooja has 6, the entire batch for today will be for Krishna because he started with fewer images.
4. If they have the exact same number of images at the start, generate images equally for both.
5. After generating, always compress them, apply necessary watermarks, and save them in the correct repository's `images/` folder, then upload to GitHub.

This rule is mandatory and must be strictly followed to keep the post backlog balanced between the two bots.

# Unique Quotes for Krishna Images
Whenever you generate AI images for Krishna that include text/quotes:
1. ALWAYS read the file `e:\Paresh\Auto Post\Auto-Insta-Krishna\quotes.txt`.
2. NEVER generate your own quotes. ONLY use the exact quotes provided in `quotes.txt`. Pick quotes from this file RANDOMLY (not sequentially) to use in the images.
3. **CRITICAL:** DO NOT append Sandeep Maheshwari's name, "- राधे कृष्ण", or any other signature at the end of the quotes. Only write the core quote exactly as it is in the file.
4. **Varied Backgrounds (Unlimited Creativity):** Do not always use a simple wooden board. You can write the text on almost ANY realistic surface! Rotate between hyper-realistic backgrounds like: vintage book pages, old weathered wooden door, stone wall, boat wood, raste (roads), pani (water surface), glass, diwaar (walls), kapde (cloth/fabric), leaves, etc. The text must look naturally integrated (painted, carved, or reflected) into whatever surface you choose.
5. Explicitly pass the specific thought into the image generation prompt.
6. AFTER generating the image successfully, ALWAYS MOVE the used quote(s) from `quotes.txt` to `e:\Paresh\Auto Post\Auto-Insta-Krishna\used_quotes.txt` (backup). This means you must delete the quote from `quotes.txt` and append it to `used_quotes.txt`. This ensures the quote is permanently preserved as a backup but never repeated, preventing duplicate images.

# 🚀 NEW ARCHITECTURE: Catbox URL Queue System (Active & Mandatory)
Auto-Insta-Krishna and Auto-Insta-Pooja both use a robust URL-based queue system for posting.

### Rule 1: Post via URLs ONLY
- The bots read strictly from `images_urls.txt` and `reels_urls.txt`.
- They **do not** pull local files from the `images/` or `new_video/` folders to post.
- This bypasses Catbox's IP blocking by passing direct raw links to Graph API.
- After a successful post, the URL is removed from the active file and saved in `used_urls.txt`.

### Rule 2: NEVER Delete User Files (Permanent Backup)
- **CRITICAL:** Do NOT write scripts that delete local `.jpg`, `.png`, or `.mp4` files from the user's PC after they are uploaded or posted.
- The `images/` and `new_video/` folders serve as the user's permanent local and GitHub backup.
- Always use `-lt` filters (e.g. `(Get-Date).AddMinutes(-2)`) in PowerShell when uploading to ensure old files are skipped instead of deleted.

### Rule 3: File Type Handling (.JPG vs .PNG)
- When writing scripts to upload or process images, always check for BOTH `.jpg` and `.png` files.
- Example: `Get-ChildItem -Path "images" -Include *.jpg, *.png`
- If you forget `.png`, half the user's images (e.g. from older screenshot generations) will be skipped.

### Rule 4: Amazon Affiliate Splitting (Pooja Bot)
- Auto-Insta-Pooja uses a split logic for captions to comply with Amazon Affiliate rules.
- **Instagram:** Appends `🛒 Check out the link in my Bio! #ad #CommissionsEarned` (No clickable links allowed).
- **Facebook:** Appends `🛒 Buy my favorite product here: https://link.amazon/A02oaFqo9 #ad #CommissionsEarned` (Direct clickable link).
- **Self-Referral Rule:** The user is aware that linking their own brand (Mojilo) via the same affiliate ID is a violation and has opted not to do it. Only promote products officially using this split-caption method.

### Rule 5: Facebook Video Story Upload Fix (CRITICAL)
- When uploading a Video Story to Facebook via the Graph API (`post_fb_video_story`), Meta's servers require time to process the video chunk in the `transfer` phase before the `finish` phase.
- **NEVER** reduce the `time.sleep(35)` after the chunk upload. 
- If reduced, Meta's API will return a false `Video Upload Is Missing` error, crashing the Facebook Story post. This has been permanently fixed and must remain exactly as is.

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

### 4. Background Music (Flute / Bansuri)
- ALWAYS use Lord Krishna devotional flute/bansuri tracks from the project's music library (`Auto-Insta-Krishna/music/`).
- Flute volume MUST be softly balanced at **14% - 15%** so the voice is crystal clear and prominent (voice at 115% volume).
- BGM MUST have a smooth **1.2 to 1.5-second fade-out** at the end.
- Voice delay: Start the voice 0.6 to 0.7 seconds after video begins, allowing the viewer to first hear the flute music and experience the unblur transition.

### 5. Video Technical Specifications
- Resolution: **1080 × 1920 (9:16 Full HD Vertical)**.
- Frame Rate: **25 fps**, Codec: **libx264** (CRF 18), Audio: **AAC 192k**.
- Total Duration: Matches voice length + ~2 seconds padding (typically 15 to 20 seconds).

### 6. YouTube Partner Program (YPP) Monetization & Metadata Rules
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
4. **Description & Cross-Promotion:**
   - Include a concise 2-3 line spiritual summary of the thought.
   - Include direct links to the website (`https://krishnavibez.in/`), WhatsApp Channel (`https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J`), and Telegram (`https://t.me/krishnavibezz`).
   - Relevant hashtags: `#KrishnaVibez #BhagavadGita #DailySuvichar #SpiritualShorts #KrishnaQuotes`.

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



