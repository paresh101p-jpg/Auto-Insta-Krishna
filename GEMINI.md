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
1. NEVER use generic prompts for the text (e.g., "Add a nice quote").
2. ALWAYS read the file `e:\Paresh\Auto Post\Auto-Insta-Krishna\used_quotes.txt` first to see which quotes have already been used in the past.
3. Generate completely unique, fresh Hindi/Sanskrit thoughts that are NOT in that file. Include a wide variety of topics such as: motivational life lessons, Krishna bhakti, love, success, garibi (poverty), daya (kindness), paisa (money), riste (relationships), etc. **CRITICAL:** DO NOT append "- राधे कृष्ण" or any other signature at the end of the quotes. Only write the core quote.
4. **Varied Backgrounds (Unlimited Creativity):** Do not always use a simple wooden board. You can write the text on almost ANY realistic surface! Rotate between hyper-realistic backgrounds like: vintage book pages, old weathered wooden door, stone wall, boat wood, raste (roads), pani (water surface), glass, diwaar (walls), kapde (cloth/fabric), leaves, etc. The text must look naturally integrated (painted, carved, or reflected) into whatever surface you choose.
5. Explicitly pass the specific thought into the image generation prompt.
6. AFTER generating the image, ALWAYS append the newly used quote(s) to `e:\Paresh\Auto Post\Auto-Insta-Krishna\used_quotes.txt` so they are never repeated in the future.

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

