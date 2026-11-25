# 🎵 KRISHNA & DEVOTIONAL SONG VIDEO 2-PIPELINE ARCHITECTURE (100% GITHUB ACTIONS & ZERO-PC)

> **MANDATORY & UNBREAKABLE LIFETIME RULE FOR ALL AGENTS / AI ASSISTANTS / GITHUB ACTIONS**:
> - **ZERO LOCAL PC RELIANCE**: PC se live streaming ya heavy rendering kabhi nahi hogi. Sab kuch 100% GitHub Actions aur Cloud (Catbox CDN / YouTube API) par chalega.
> - **TWO CLEAR ISOLATED PIPELINES**:
>   - **Pipeline 1 (Ingestion & Registration)**: Song ko sunna, synced SRT lyrics nikalna, matching thumbnail & clean slide cloud par daalna, aur registry me register karke GitHub par push karna.
>   - **Pipeline 2 (Render & YouTube Upload)**: GitHub Actions par chalna, cloud se audio/images uthana, anti-copyright audio shield lagana, synced lyric badge render karna, aur YouTube par Unlisted upload karna.

---

## 🌟 PIPELINE 1: SONG INGESTION, AUDIT & CLOUD REGISTRATION
- **Script**: `song_ingest_pipeline.py`
- **GitHub Workflow**: `.github/workflows/song-ingest.yml` (can be triggered from GitHub web, mobile, or API)
- **Role**: Whenever a new song is provided (by the user, an AI agent, or inbox):
  1. **Audio Ingestion**: Audio file ko Catbox CDN par upload karke permanent `AUDIO_URL` banaya jata hai.
  2. **Voice-Synchronized Lyrics (Gemini Audio AI)**:
     - Song ko Gemini Audio AI (`gemini-3.5-flash`) se end-to-end sunaya jata hai.
     - Singer ki aawaz ke second-to-second singing timing ke mutabik standard `.srt` subtitle file banti hai.
     - File `Songs/<Song Name>.srt` me save hoti hai aur registry me `lyrics` field me lock ho jati hai.
  3. **16:9 Image Pair Rule (Zero-Mismatch Guarantee)**:
     - **Thumbnail (`thumb_url`)**: 16:9 landscape image with high-CTR 3D Devanagari title typography, glowing borders, and divine badges.
     - **Inside Video Slide (`image_urls[0]`)**: The EXACT SAME scene/artwork, but 100% CLEAN (zero text, zero titles, zero badges, zero watermarks).
     - Both images are uploaded to Catbox CDN so they are accessible by GitHub Actions.
  4. **Registry & Queue**:
     - Song is saved in `song_tracks_registry.json` under its `AUDIO_URL` with `thumb_url`, `image_urls`, `lyrics` (full SRT), and `status: "pending"`.
     - `AUDIO_URL` is appended to `song_urls.txt`.
     - Committed and pushed directly to `origin master`.

---

## 🌟 PIPELINE 2: RENDER & YOUTUBE UPLOAD (100% CLOUD RUNNER)
- **Script**: `song_full_pipeline.py`
- **GitHub Workflow**: `.github/workflows/song-auto.yml` (Scheduled Sunday 4 AM / 9 AM IST or manual trigger)
- **Role**:
  1. Reads next song from `song_urls.txt` and `song_tracks_registry.json`.
  2. Downloads clean `AUDIO_URL`, `thumb_url`, and `image_urls[0]` directly from Catbox CDN (Zero local cache mismatch).
  3. **Anti-Copyright Audio Shield & Studio Mastering**:
     - 100% metadata stripped (`-map_metadata -1`).
     - 1.5% micro-tempo acoustic shift (`atempo=1.015`) to create a 100% unique digital fingerprint.
     - Deva vocal warmth & presence EQ (`equalizer=f=220`, `equalizer=f=3200`).
     - Divine subtle temple ambiance (`aecho=0.75:0.5:28:0.10`).
     - Stereo soundstage widening (`extrastereo=m=1.15`).
     - YouTube broadcast standard loudness normalization (`loudnorm=I=-14:TP=-1.0:LRA=11`).
     - Renders pristine 320k high fidelity stereo audio.
  4. **1080p Animated Video Generation**:
     - Visuals: Uses the clean slide (no text) with gentle, slow Ken Burns zoom (1.00 -> 1.08x) + drifting sacred flora petals (morpankh, lotus) + diamond star sparkles.
     - Synchronized Lyrics: Uses the exact `.srt` subtitles to render luxury glassmorphic golden pill badges at the bottom-center of the screen that appear and fade smoothly as each line is sung.
  5. **YouTube Upload & SEO**:
     - Uploads to YouTube Unlisted with AI-generated title, description, and tags.
     - Sets the custom master thumbnail via YouTube Data API (`thumbnails().set`).
     - Moves URL from `song_urls.txt` to `song_used_urls.txt`, logs upload in `song_uploaded_tracker.txt`, updates status to `uploaded` in `song_tracks_registry.json`, and commits back to GitHub.

---

## 📋 CURRENT ACTIVE PENDING SONG CATALOG

| # | Deity | Song Name | Audio URL | Thumbnail (With Text) | Clean Slide (No Text) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Lord Krishna | *Mere Shyam - मेरे हर गीत में तू* | `https://files.catbox.moe/lqr2zr.mp3` | `https://files.catbox.moe/js8nno.png` | `https://files.catbox.moe/n6qo8o.png` |
| **2** | Lord Krishna | *Krishna Sada Sahayate - Govind Damodar* | `https://files.catbox.moe/1fg4a9.mp3` | `https://files.catbox.moe/szpuog.png` | `https://files.catbox.moe/azmkd3.png` |
| **3** | Lord Hanuman | *Hanuman Ji - Sankat Mochan Hey Anjanilala* | `https://files.catbox.moe/j44adr.mp3` | `https://files.catbox.moe/r55plj.png` | `https://files.catbox.moe/wb2eer.png` |
| **4** | Lord Hanuman | *Hanuman Ji - Bajrangi Mere Bajrangi* | `https://files.catbox.moe/087dwy.mp3` | `https://files.catbox.moe/ntohhe.png` | `https://files.catbox.moe/huhs3o.png` |
| **5** | Lord Ram | *Mere Ghar Ram Padhare Hain - कुटिया में उजाला* | `https://files.catbox.moe/1h27ej.mp3` | `https://files.catbox.moe/pz4uxc.jpg` | `https://files.catbox.moe/tj3yi9.jpg` |
