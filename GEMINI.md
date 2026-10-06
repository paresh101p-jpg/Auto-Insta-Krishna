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

# ?? NEW ARCHITECTURE: Catbox URL Queue System (Active)
Auto-Insta-Krishna has been upgraded to match Auto-Insta-Pooja's robust URL-based queue system.
- **Workflow:** 
  1. User generates images in images/ locally.
  2. Runs create_reels.ps1 to convert them into cinematic Reels with music and blurred backgrounds in new_video/.
  3. Uploads both images and reels to Catbox.moe.
  4. Appends the URLs to images_urls.txt and reels_urls.txt.
- **Alternating Posts:** The bot automatically alternates between IMAGE and REEL every time it posts.
- **Backup:** After posting, the bot removes the URL from the active text file and appends it to used_urls.txt for backup.
- **NEVER** delete local files from the user's PC (they are the user's permanent backup).

