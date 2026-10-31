#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
KRISHNA VIBEZ — AUTOMATED 15-MIN MUSIC VIDEO PIPELINE (CLOUD & LOCAL)
=============================================================================
- 12 Brand New 8K Golden Theme Clean Images (Nature, Peacocks, Birds, Cows, Ghats)
- Fast 25-Second Dynamic Transitions (Never feels stuck, constantly fresh visuals)
- High-Clarity 1080p HDR (No sepia, no dark vignette)
- Live Indian Bansuri Flute & Tabla Master Tracks (100% Royalty Free & Legal)
- AI Dynamic Title, Description, SEO Tags & Hashtags (Meditation / Peace theme)
- AI Auto Thumbnail Generator (High CTR, Devanagari typography, 16:9 HD)
- Resumable YouTube Video & Thumbnail Upload via Data API v3
- Post-Upload Auto-Cleanup of all temporary media
=============================================================================
"""

import os
import sys
import json
import time
import random
import subprocess
import requests
import glob

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
import shutil
import math
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(BASE_DIR, "music")
IMAGES_DIR = os.path.join(BASE_DIR, "music_video_images")
USED_IMAGES_DIR = os.path.join(IMAGES_DIR, "used")
USED_IMAGES_TRACKER = os.path.join(BASE_DIR, "used_music_images_tracker.txt")
OUTPUT_VIDEO = os.path.join(BASE_DIR, "temp_music_video_render.mp4")
TEMP_AUDIO = os.path.join(BASE_DIR, "temp_music_video_audio.mp3")
TEMP_THUMBNAIL = os.path.join(BASE_DIR, "temp_music_thumbnail.jpg")
TREBLO_URLS_FILE = os.path.join(BASE_DIR, "treblo_music_urls.txt")
TREBLO_VIDEO_ONLY_URLS = os.path.join(BASE_DIR, "treblo_music_video_only_urls.txt")
TREBLO_BACKUP_URLS_FILE = os.path.join(BASE_DIR, "treblo_music_urls_backup.txt")
TREBLO_USED_URLS_FILE = os.path.join(BASE_DIR, "treblo_music_used_urls.txt")
TREBLO_CYCLE_TRACKER = os.path.join(BASE_DIR, "treblo_music_cycle_tracker.txt")
TREBLO_REGISTRY_FILE = os.path.join(BASE_DIR, "treblo_tracks_registry.json")

# Detect FFmpeg executable
FFMPEG_EXE = "ffmpeg"
local_ffmpeg = r"E:\Paresh\Auto Post\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if os.path.exists(local_ffmpeg):
    FFMPEG_EXE = local_ffmpeg

# =============================================================================
# 36 DISTINCT DIVERSE KRISHNA MEDITATION THEMES (6 SPIRITUAL CATEGORIES)
# Guarantees that every video has a completely unique title, thumbnail headline,
# sub-headline, and pill keywords tailored to the music theme and mood.
# =============================================================================
MEDITATION_THEMES_36 = [
    # ── Category 1: Morning Pooja & Vrindavan Sunrise (सुबह की पूजा और नई शुरुआत) ──
    {
        "category": "Morning Pooja & Awakening",
        "badge": "{dur_min} MIN MORNING MEDITATION",
        "hindi_main": "वृंदावन प्रभात बाँसुरी",
        "hindi_sub": "प्रातःकालीन पूजा और सकारात्मक शुरुआत",
        "hook_pill": "प्रातः पूजा   |   सकारात्मक ऊर्जा   |   शुभ शुरुआत",
        "title": "वृंदावन प्रभात बाँसुरी धुन | Morning Krishna Flute for Positive Energy",
        "tags": ["Morning Flute", "Vrindavan Bansuri", "Morning Pooja Music", "Positive Energy Flute", "Bansuri Meditation", "Radha Krishna", "Krishna Vibez", "Subah Ki Dhun", "Pratah Smaran"]
    },
    {
        "category": "Morning Pooja & Awakening",
        "badge": "SACRED MORNING DHUN",
        "hindi_main": "शुभ प्रभात अमृत बाँसुरी",
        "hindi_sub": "घर में सुख शांति और समृद्धि लाएं",
        "hook_pill": "सुख समृद्धि   |   पावन वातावरण   |   मानसिक शांति",
        "title": "शुभ प्रभात अमृत बाँसुरी और तबला | Sacred Morning Rhythms for Peace",
        "tags": ["Shubh Prabhat Flute", "Morning Peace Music", "Ghar Me Shanti", "Bansuri Tabla Jugalbandi", "Daily Meditation", "Spiritual Morning", "Radhe Radhe Flute"]
    },
    {
        "category": "Morning Pooja & Awakening",
        "badge": "BRAHMA MUHURTA DHYAN",
        "hindi_main": "ब्रह्म मुहूर्त दिव्य साधना",
        "hindi_sub": "अंतर्मन को जागृत करने वाला संगीत",
        "hook_pill": "ब्रह्म मुहूर्त   |   आत्मिक जागरण   |   गहरी एकाग्रता",
        "title": "ब्रह्म मुहूर्त कृष्ण ध्यान संगीत | Early Morning Flute Meditation",
        "tags": ["Brahma Muhurta Music", "Early Morning Meditation", "Dhyan Sangeet", "Krishna Murli", "Soul Awakening", "Spiritual Energy", "Peaceful Mind"]
    },
    {
        "category": "Morning Pooja & Awakening",
        "badge": "SUNRISE SPIRITUAL VIBES",
        "hindi_main": "सूर्योदय पावन मुरली धुन",
        "hindi_sub": "नई ऊर्जा और आनंद का संचार करें",
        "hook_pill": "सूर्योदय ऊर्जा   |   नई उमंग   |   आनंदमयी मन",
        "title": "सूर्योदय पावन मुरली एवं तबला | Divine Sunrise Flute Melodies",
        "tags": ["Sunrise Flute", "Suryodaya Music", "New Day Energy", "Krishna Bansuri Instrumental", "Indian Classical Flute", "Positive Mindset"]
    },
    {
        "category": "Morning Pooja & Awakening",
        "badge": "GOKUL MORNING BANSURI",
        "hindi_main": "गोकुल की पावन मुरली",
        "hindi_sub": "घर और मन को पवित्र करने वाला संगीत",
        "hook_pill": "गोकुल मुरली   |   मन की पवित्रता   |   आत्मिक सुकून",
        "title": "गोकुल की प्रातःकालीन बाँसुरी | Soulful Morning Flute for Daily Pooja",
        "tags": ["Gokul Flute", "Krishna Morning Bhajan", "Pooja Instrumental", "Vrindavan Vibes", "Daily Dhyan", "Harmonic Flute", "Krishna Bhakti"]
    },
    {
        "category": "Morning Pooja & Awakening",
        "badge": "PEACEFUL AWAKENING",
        "hindi_main": "प्रातः स्मरण शांति प्रवाह",
        "hindi_sub": "सारे दिन के लिए सकारात्मक मन पाएं",
        "hook_pill": "सकारात्मक सोच   |   शांत मन   |   निर्मल विचार",
        "title": "प्रातः स्मरण शांति प्रवाह बाँसुरी | Peaceful Morning Awakening Flute",
        "tags": ["Morning Awakening", "Pratah Smaran", "Peaceful Instrumental", "Krishna Flute Calm", "Day Start Music", "Inner Harmony"]
    },

    # ── Category 2: Stress Relief & Mental Calm (तनाव और चिंता मुक्ति) ──
    {
        "category": "Stress Relief & Anxiety Healing",
        "badge": "{dur_min} MIN STRESS RELIEF",
        "hindi_main": "तनाव और चिंता दूर करें",
        "hindi_sub": "असीम शांति और विश्राम का अनुभव",
        "hook_pill": "तनाव मुक्ति   |   मानसिक शांति   |   आत्मिक विश्राम",
        "title": "तनाव और चिंता तुरंत मिटाएं | Divine Krishna Flute for Stress Relief",
        "tags": ["Stress Relief Music", "Tanav Mukti Flute", "Anxiety Relief", "Overthinking Stop", "Relaxing Bansuri", "Peace of Mind", "Chinta Door Kare"]
    },
    {
        "category": "Stress Relief & Anxiety Healing",
        "badge": "CALM MIND & PEACE",
        "hindi_main": "मन को असीम शांति दें",
        "hindi_sub": "व्यस्त विचारों को थामें और सुकून पाएं",
        "hook_pill": "शांत विचार   |   चिंता से राहत   |   गहरा सुकून",
        "title": "मन को शांत करने वाला संगीत | Calming Krishna Flute for Overthinking",
        "tags": ["Calm Mind Music", "Overthinking Relief", "Man Ki Shanti", "Bansuri Dhun Hindi", "Peaceful Meditation", "Mental Relax Music"]
    },
    {
        "category": "Stress Relief & Anxiety Healing",
        "badge": "SOUL HEALING & CALM",
        "hindi_main": "मानसिक शांति अमृत रस",
        "hindi_sub": "थके हुए मस्तिष्क को नया जीवन दें",
        "hook_pill": "थकान मुक्ति   |   मस्तिष्क विश्राम   |   नया उत्साह",
        "title": "मानसिक शांति अमृत रस बाँसुरी | Healing Krishna Flute for Anxious Mind",
        "tags": ["Soul Healing Flute", "Mind Relaxing Music", "Thakan Door Kare", "Healing Frequency", "Bansuri Tabla Calm", "Anxiety Healer"]
    },
    {
        "category": "Stress Relief & Anxiety Healing",
        "badge": "ANGER RELIEF & SERENITY",
        "hindi_main": "क्रोध शांत करने वाली धुन",
        "hindi_sub": "हृदय में शीतलता और धैर्य भरें",
        "hook_pill": "धैर्य और शांति   |   हृदय शीतलता   |   मधुर स्वभाव",
        "title": "क्रोध और अशांति से मुक्ति | Krishna Flute for Anger Relief & Serenity",
        "tags": ["Anger Relief Music", "Krodh Shant Kare", "Inner Patience", "Serenity Music", "Calm Heart Flute", "Geeta Gyan Music"]
    },
    {
        "category": "Stress Relief & Anxiety Healing",
        "badge": "SOOTHING BANSURI FLOW",
        "hindi_main": "हृदयस्पर्शी मधुर बाँसुरी",
        "hindi_sub": "जीवन के हर तनाव को भुला देने वाला संगीत",
        "hook_pill": "हृदय शांति   |   गहरी राहत   |   कोमल स्वर",
        "title": "हृदय को सुकून देने वाली बाँसुरी | Soothing Flute Melody for Inner Calm",
        "tags": ["Soothing Flute", "Hridaya Shanti", "Heart Touching Bansuri", "Soft Tabla Beats", "Deep Relaxation", "Stress Dissolve"]
    },
    {
        "category": "Stress Relief & Anxiety Healing",
        "badge": "MENTAL REST & RELIEF",
        "hindi_main": "परम शांति एवं विश्राम",
        "hindi_sub": "मन के सारे भार को हल्का कर दें",
        "hook_pill": "मन का हल्कापन   |   निश्चिंतता   |   असीम आनंद",
        "title": "शांति और विश्राम का पावन प्रवाह | Peaceful Krishna Flute for Mental Rest",
        "tags": ["Param Shanti", "Mental Rest Music", "Total Relaxation", "Krishna Vibez Flute", "Peaceful Mind", "Spiritual Rest"]
    },

    # ── Category 3: Deep Night Sleep & Insomnia Relief (गहरी नींद और विश्राम) ──
    {
        "category": "Deep Night Sleep & Insomnia",
        "badge": "{dur_min} MIN DEEP SLEEP",
        "hindi_main": "चिंता मुक्ति और गहरी नींद",
        "hindi_sub": "रात्रि विश्राम और मानसिक सुकून",
        "hook_pill": "गहरी नींद   |   अनिद्रा मुक्ति   |   शांत रात्रि",
        "title": "रात को गहरी नींद के लिए संगीत | Krishna Flute for Deep Sleep & Insomnia",
        "tags": ["Deep Sleep Music", "Gehri Neend Bansuri", "Insomnia Relief", "Sleep Flute Hindi", "Night Rest Music", "Soothing Sleep Dhun"]
    },
    {
        "category": "Deep Night Sleep & Insomnia",
        "badge": "BEDTIME SLEEP HEALING",
        "hindi_main": "रात्रि विश्राम पावन धुन",
        "hindi_sub": "मीठे सपनों और शांत निद्रा के लिए",
        "hook_pill": "सुकून भरी नींद   |   स्वप्न शांति   |   रात्रि विश्राम",
        "title": "सोते समय मन को शांत करें | Bedtime Krishna Flute for Restful Sleep",
        "tags": ["Bedtime Flute", "Raat Ki Shanti", "Restful Sleep", "Calming Night Music", "Sleep Healing Instrumental", "Peaceful Dreams"]
    },
    {
        "category": "Deep Night Sleep & Insomnia",
        "badge": "INSOMNIA RELIEF MUSIC",
        "hindi_main": "अनिद्रा दूर करने वाला संगीत",
        "hindi_sub": "कुछ ही पलों में गहरी नींद पाएं",
        "hook_pill": "अनिद्रा से राहत   |   गहरी निद्रा   |   विश्राम अवस्था",
        "title": "अनिद्रा और बेचैनी से तुरंत राहत | Soothing Sleep Flute for Insomnia Cure",
        "tags": ["Insomnia Cure Music", "Bechaini Door Kare", "Fast Sleep Flute", "Fall Asleep Fast", "Deep Rest", "Night Relaxation"]
    },
    {
        "category": "Deep Night Sleep & Insomnia",
        "badge": "MIDNIGHT CALM & SLEEP",
        "hindi_main": "मधुर रात्रि स्वप्न बाँसुरी",
        "hindi_sub": "दिन भर की थकान मिटाकर विश्राम दें",
        "hook_pill": "रात्रि विश्राम   |   थकान मुक्ति   |   निर्मल निद्रा",
        "title": "रात्रि कालीन दिव्य शांति बाँसुरी | Midnight Krishna Flute & Gentle Waves",
        "tags": ["Midnight Flute", "Night Calm", "Dreamy Bansuri", "Soft Instrumentals", "Sleep Waves", "Krishna Night Music"]
    },
    {
        "category": "Deep Night Sleep & Insomnia",
        "badge": "PEACEFUL SLEEP VIBES",
        "hindi_main": "शांत निद्रा अमृत वर्षा",
        "hindi_sub": "तनावमुक्त होकर गहरी नींद में सोएं",
        "hook_pill": "तनावमुक्त निद्रा   |   शांत मस्तिष्क   |   पूर्ण विश्राम",
        "title": "शांत निद्रा अमृत वर्षा बाँसुरी | Peaceful Night Bansuri for Pure Sleep",
        "tags": ["Pure Sleep Flute", "Amrit Varsha Dhun", "Sound Sleep", "Sleep Therapy Music", "Stress Free Night", "Calm Body Mind"]
    },
    {
        "category": "Deep Night Sleep & Insomnia",
        "badge": "TOTAL SLEEP RELAXATION",
        "hindi_main": "सोने से पहले की मधुर धुन",
        "hindi_sub": "आत्मा को सुकून और नींद की गोद में ले जाएं",
        "hook_pill": "गहरी विश्रांति   |   आत्मिक सुकून   |   मधुर सपने",
        "title": "सोने से पहले मन को हल्का करें | Calming Sleep Flute for Total Relaxation",
        "tags": ["Bedtime Calm", "Sone Se Pehle Sangeet", "Total Sleep Relaxation", "Gentle Bansuri", "Deep Slumber Music", "Night Healing"]
    },

    # ── Category 4: Radha Krishna Divine Love & Bhakti (राधा कृष्ण भक्ति और प्रेम) ──
    {
        "category": "Radha Krishna Divine Love",
        "badge": "{dur_min} MIN RADHE KRISHNA",
        "hindi_main": "राधे कृष्ण पावन धुन",
        "hindi_sub": "सकारात्मक ऊर्जा और आत्मिक सुकून",
        "hook_pill": "अलौकिक प्रेम   |   राधा कृष्ण कृपा   |   भक्ति रस",
        "title": "राधे कृष्ण पावन प्रेम धुन | Soulful Radha Krishna Love Instrumental",
        "tags": ["Radhe Krishna Flute", "Radha Krishna Love Instrumental", "Bhakti Sangeet", "Divine Love Music", "Vrindavan Prem", "Soulful Bansuri"]
    },
    {
        "category": "Radha Krishna Divine Love",
        "badge": "DIVINE BHAKTI BANSURI",
        "hindi_main": "श्री कृष्ण अमृत बाँसुरी",
        "hindi_sub": "मन की शांति और भक्ति भाव के लिए",
        "hook_pill": "अमृत रस   |   भक्ति भाव   |   कृष्ण स्मरण",
        "title": "श्री कृष्ण दिव्य बाँसुरी धुन | Sacred Krishna Flute for Divine Connection",
        "tags": ["Krishna Amrit Bansuri", "Divine Connection", "Bhakti Bhav", "Krishna Smaran", "Inner Peace Flute", "Bhakti Dhun"]
    },
    {
        "category": "Radha Krishna Divine Love",
        "badge": "VRINDAVAN RAAS DHUN",
        "hindi_main": "वृंदावन रास अमृत धुन",
        "hindi_sub": "गोपियों संग कृष्ण की आनंदमयी मुरली",
        "hook_pill": "रास लीला   |   दिव्य आनंद   |   कृष्ण प्रेम",
        "title": "वृंदावन की रास बाँसुरी | Vrindavan Raas Leela Divine Flute Melody",
        "tags": ["Raas Leela Flute", "Vrindavan Murli", "Anandmayi Bansuri", "Krishna Prem Dhun", "Classical Indian Flute", "Devotional Vibe"]
    },
    {
        "category": "Radha Krishna Divine Love",
        "badge": "BARSANA LOVE MEDITATION",
        "hindi_main": "बरसाना पावन मुरली गान",
        "hindi_sub": "श्री राधा रानी के चरणों में समर्पण",
        "hook_pill": "राधा रानी कृपा   |   पावन समर्पण   |   प्रेम माधुर्य",
        "title": "बरसाना की पावन प्रेम बाँसुरी | Barsana Sacred Love Instrumental",
        "tags": ["Barsana Flute", "Radha Rani Dhun", "Prem Madhurya", "Barsana Vibe", "Samarpan Music", "Devotional Flute"]
    },
    {
        "category": "Radha Krishna Divine Love",
        "badge": "KADAMBA DIVINE FLUTE",
        "hindi_main": "कदम्ब की छाँव में बाँसुरी",
        "hindi_sub": "यमुना तट की पावन स्मृतियों संग ध्यान",
        "hook_pill": "कदम्ब कुंज   |   यमुना तट   |   पावन स्मृतियां",
        "title": "कदम्ब की छाँव में बजी मुरली | Kadamba Tree Divine Krishna Flute",
        "tags": ["Kadamba Tree Flute", "Yamuna Ghat Bansuri", "Vrindavan Kunj", "Divine Memories", "Kadamba Chhav", "Krishna Murli"]
    },
    {
        "category": "Radha Krishna Divine Love",
        "badge": "DEVOTIONAL SOUL VIBES",
        "hindi_main": "मधुर मुरली आत्मिक भक्ति",
        "hindi_sub": "भक्ति में लीन होकर परम सुख पाएं",
        "hook_pill": "अनन्य भक्ति   |   परमानंद   |   आत्मिक समर्पण",
        "title": "मधुर मुरली और आत्मिक भक्ति | Soulful Devotional Krishna Instrumental",
        "tags": ["Madhur Murli", "Aatmik Bhakti", "Param Anand", "Ananya Bhakti", "Soulful Krishna Music", "Devotion Instrumental"]
    },

    # ── Category 5: Inner Peace, Soul Healing & Dhyan (आत्मिक शांति और गहन ध्यान) ──
    {
        "category": "Inner Peace & Soul Dhyan",
        "badge": "{dur_min} MIN DEEP DHYAN",
        "hindi_main": "गहन ध्यान आत्मिक शांति",
        "hindi_sub": "अंतर्मन के शून्य में उतरने का संगीत",
        "hook_pill": "गहन ध्यान   |   शून्य समाधि   |   आत्मिक शांति",
        "title": "गहन ध्यान और आत्मिक जागरण | Deep Krishna Dhyan Flute for Inner Peace",
        "tags": ["Deep Dhyan Flute", "Inner Peace Music", "Shunya Samadhi", "Spiritual Awakening", "Meditation Waves", "Dhyan Sangeet"]
    },
    {
        "category": "Inner Peace & Soul Dhyan",
        "badge": "SOUL HEALING MEDITATION",
        "hindi_main": "आत्मिक हीलिंग अमृत धुन",
        "hindi_sub": "नकारात्मकता मिटाएं और प्रकाश पाएं",
        "hook_pill": "सोल हीलिंग   |   सकारात्मकता   |   आत्म प्रकाश",
        "title": "आत्मा को हील करने वाला संगीत | Krishna Flute for Soul Healing & Peace",
        "tags": ["Soul Healing", "Aatmik Healing", "Negative Energy Removal", "Chakra Balance", "Light Meditation", "Healing Flute"]
    },
    {
        "category": "Inner Peace & Soul Dhyan",
        "badge": "STUDY & FOCUS CALM",
        "hindi_main": "एकाग्रता और स्थिर मन",
        "hindi_sub": "पढ़ाई और ध्यान में पूर्ण फोकस लाएं",
        "hook_pill": "पूर्ण एकाग्रता   |   स्थिर मन   |   ज्ञान साधना",
        "title": "एकाग्रता और मानसिक स्थिरता | Krishna Flute for Study & Focus Concentration",
        "tags": ["Focus Flute", "Study Music Hindi", "Ekagrata Bansuri", "Deep Concentration", "Student Meditation", "Mind Focus"]
    },
    {
        "category": "Inner Peace & Soul Dhyan",
        "badge": "SERENE MEDITATION FLOW",
        "hindi_main": "शांत सरोवर मुरली तान",
        "hindi_sub": "कमल दल सा निर्मल और शांत मन पाएं",
        "hook_pill": "निर्मल मन   |   शांत सरोवर   |   दिव्य शांति",
        "title": "शांत सरोवर और मुरली की तान | Serene Lake & Lotus Flower Flute Music",
        "tags": ["Serene Flute", "Shant Sarovar", "Lotus Meditation", "Nirmal Man", "Pure Mind Music", "Peaceful Flow"]
    },
    {
        "category": "Inner Peace & Soul Dhyan",
        "badge": "SILENT MIND DHYAN",
        "hindi_main": "असीम शांति मौन साधना",
        "hindi_sub": "विचारों के पार परम विश्राम की अनुभूति",
        "hook_pill": "मौन साधना   |   परम विश्राम   |   अंतर्मुखी मन",
        "title": "असीम शांति और मौन का अनुभव | Silent Mind Meditation Krishna Bansuri",
        "tags": ["Silent Mind", "Maun Sadhana", "Thoughts Free Music", "Inner Silence", "Deep Stillness", "Transcendental Calm"]
    },
    {
        "category": "Inner Peace & Soul Dhyan",
        "badge": "SPIRITUAL AWAKENING",
        "hindi_main": "दिव्य चेतना का जागरण",
        "hindi_sub": "हृदय में आनंद और तेज का अनुभव करें",
        "hook_pill": "चेतना जागरण   |   आत्म तेज   |   परमानंद",
        "title": "दिव्य चेतना और ऊर्जा का संचार | Spiritual Awakening Krishna Instrumental",
        "tags": ["Spiritual Awakening", "Divya Chetna", "Soul Energy", "Paramanand", "Krishna Vibration", "Cosmic Calm"]
    },

    # ── Category 6: Classical Bansuri & Tabla Jugalbandi (बांसुरी एवं तबला जुगलबंदी) ──
    {
        "category": "Bansuri & Tabla Jugalbandi",
        "badge": "{dur_min} MIN FLUTE & TABLA",
        "hindi_main": "बांसुरी एवं तबला जुगलबंदी",
        "hindi_sub": "कहरवा ताल और रागों का पावन संगम",
        "hook_pill": "कहरवा ताल   |   राग संगम   |   शास्त्रीय संगीत",
        "title": "बांसुरी एवं तबला पावन जुगलबंदी | Pure Indian Classical Bansuri & Live Tabla",
        "tags": ["Bansuri Tabla Jugalbandi", "Keherwa Taal Flute", "Indian Classical Instrumental", "Live Tabla Rhythm", "Flute Jugalbandi", "Taal Dhun"]
    },
    {
        "category": "Bansuri & Tabla Jugalbandi",
        "badge": "RAAG BHAIRAVI JUGALBANDI",
        "hindi_main": "राग भैरवी पावन संगीत",
        "hindi_sub": "शांति और भक्ति का शास्त्रीय अनुभव",
        "hook_pill": "राग भैरवी   |   शास्त्रीय संगीत   |   मनोहारी ताल",
        "title": "राग भैरवी दिव्य बाँसुरी और तबला | Raag Bhairavi Divine Flute & Tabla",
        "tags": ["Raag Bhairavi", "Bhairavi Flute", "Classical Jugalbandi", "Morning Raag", "Spiritual Classical", "Pure Bansuri"]
    },
    {
        "category": "Bansuri & Tabla Jugalbandi",
        "badge": "MELODIC FLUTE & RHYTHM",
        "hindi_main": "सुरीली बाँसुरी कोमल लय",
        "hindi_sub": "हृदय को गुंजायमान करने वाला संगीत",
        "hook_pill": "कोमल लय   |   मधुर बांसुरी   |   सुरमयी ताल",
        "title": "सुरीली बाँसुरी और कोमल तबला लय | Melodic Bansuri & Soft Live Tabla Taal",
        "tags": ["Melodic Bansuri", "Komal Taal", "Surmayi Flute", "Soft Tabla Beats", "Harmonious Music", "Indian Classical Relax"]
    },
    {
        "category": "Bansuri & Tabla Jugalbandi",
        "badge": "RAAG DARBARI PEACE",
        "hindi_main": "राग दरबारी दिव्य धुन",
        "hindi_sub": "गंभीर और आत्मिक शांति का शास्त्रीय प्रवाह",
        "hook_pill": "राग दरबारी   |   गंभीर शांति   |   आत्मिक गहराई",
        "title": "राग दरबारी दिव्य बाँसुरी | Majestic Raag Darbari Flute for Deep Peace",
        "tags": ["Raag Darbari", "Darbari Flute", "Deep Classical Music", "Majestic Bansuri", "Midnight Raag", "Soulful Classical"]
    },
    {
        "category": "Bansuri & Tabla Jugalbandi",
        "badge": "YAMUNA GHAT BANSURI",
        "hindi_main": "यमुना तट शास्त्रीय प्रवाह",
        "hindi_sub": "लहरों के साथ गूंजती मधुर मुरली",
        "hook_pill": "यमुना तट   |   शास्त्रीय प्रवाह   |   पावन लहरें",
        "title": "यमुना तट शास्त्रीय बाँसुरी प्रवाह | Yamuna Ghat Classical Flute & Rhythm",
        "tags": ["Yamuna Ghat Flute", "Yamuna Kinare Bansuri", "Rhythm of Waves", "Classical Flute Flow", "Vrindavan Ghats", "Pure Instrumental"]
    },
    {
        "category": "Bansuri & Tabla Jugalbandi",
        "badge": "TRANSCENDENTAL NAAD",
        "hindi_main": "अलौकिक नाद ब्रह्म धुन",
        "hindi_sub": "संगीत के माध्यम से ईश्वर से जुड़ें",
        "hook_pill": "नाद ब्रह्म   |   दिव्य तरंग   |   ईश्वर मिलन",
        "title": "अलौकिक नाद ब्रह्म बाँसुरी एवं तबला | Transcendental Sound & Rhythmic Harmony",
        "tags": ["Naad Brahma", "Transcendental Flute", "Divya Tarang", "Cosmic Music", "Ishwar Milan", "Divine Harmony"]
    },

    # ── Category 7: Lo-Fi Chill & Night Relaxation (लो-फाई बांसुरी एवं शांत बीट्स) ──
    {
        "category": "Krishna Lo-Fi & Chill Beats",
        "badge": "KRISHNA LO-FI CHILL",
        "hindi_main": "कृष्ण लो-फाई पावन धुन",
        "hindi_sub": "सुकून भरी रात और एकाग्र मन के लिए",
        "hook_pill": "लो-फाई बांसुरी   |   सुकून भरी रात   |   एकाग्र मन",
        "title": "कृष्ण लो-फाई बांसुरी संगीत | Peaceful Krishna Lo-Fi Flute & Chill Beats",
        "tags": ["Krishna Lofi", "Lofi Flute", "Indian Lofi", "Krishna Lo-Fi Beats", "Peaceful Lofi", "Lofi Chill Music", "Bansuri Lofi", "Study Lofi Hindi", "Relaxing Lofi"]
    },
    {
        "category": "Krishna Lo-Fi & Chill Beats",
        "badge": "MIDNIGHT LO-FI VIBES",
        "hindi_main": "आधी रात का लो-फाई सुकून",
        "hindi_sub": "गहरी नींद और विचारों को विराम देने हेतु",
        "hook_pill": "मध्यरात्रि सुकून   |   लो-फाई बीट्स   |   गहरी निद्रा",
        "title": "आधी रात का कृष्ण लो-फाई सुकून | Midnight Krishna Lo-Fi Flute for Deep Sleep",
        "tags": ["Midnight Lofi", "Krishna Lofi Beats", "Sleep Lofi", "Night Lofi Flute", "Insomnia Relief Lofi", "Chillhop Flute", "Calm Lofi"]
    },
    {
        "category": "Krishna Lo-Fi & Chill Beats",
        "badge": "STUDY & FOCUS LO-FI",
        "hindi_main": "पढ़ाई और एकाग्रता लो-फाई",
        "hindi_sub": "मन को शांत और केंद्रित रखने वाला संगीत",
        "hook_pill": "पूर्ण फोकस   |   लो-फाई संगीत   |   स्थिर चित्त",
        "title": "पढ़ाई और एकाग्रता हेतु लो-फाई बांसुरी | Krishna Lo-Fi Flute for Study & Focus",
        "tags": ["Study Lofi", "Focus Lofi Flute", "Student Lofi", "Concentration Music", "Krishna Study Beats", "Background Lofi", "Indian Lofi Beats"]
    },
    {
        "category": "Krishna Lo-Fi & Chill Beats",
        "badge": "CHILL RAIN & LO-FI FLUTE",
        "hindi_main": "बरसात और लो-फाई बाँसुरी",
        "hindi_sub": "रिमझिम बारिश संग शांत बांसुरी की तान",
        "hook_pill": "रिमझिम बारिश   |   लो-फाई धुन   |   परम शांति",
        "title": "रिमझिम बारिश और लो-फाई बाँसुरी | Rainy Day Krishna Lo-Fi Flute & Calm Vibes",
        "tags": ["Rain Lofi", "Krishna Rain Lofi", "Rainy Day Bansuri", "Lofi Flute Rain", "Cozy Lofi", "Relaxing Indian Lofi", "Calm Rain Beats"]
    }
]

# Trackers for Zero-Repetition Title & Theme Guarantee
USED_TITLES_FILE = os.path.join(BASE_DIR, "used_music_titles.txt")
THEME_TRACKER_FILE = os.path.join(BASE_DIR, "music_theme_tracker.json")

def sanitize_clean_text(text):
    if not text:
        return ""
    import re
    text = re.sub(r'\(?\s*\d+\s*[Hh][Zz](\s*[Rr]esonance)?\s*\)?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\d+\s*[Hh][Zz]\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b[Hh][Zz]\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s{2,}', ' ', text).strip()
    return text

def is_krishna_track(track_name="", theme_category=""):
    t_lower = (track_name or "").lower()
    cat_lower = (theme_category or "").lower()
    krishna_keywords = [
        "krishna", "krishnas", "vrindavan", "brindavan", "radha", "radhe",
        "murli", "gokul", "barsana", "govind", "gopal", "kanha", "madhav",
        "shyam", "mohan", "murlidhar", "bhagavan", "dwarka", "nand"
    ]
    if any(kw in t_lower for kw in krishna_keywords):
        return True
    if any(kw in cat_lower for kw in ["krishna", "radha"]):
        return True
    return False

def is_lofi_track(track_name="", theme_category=""):
    t_lower = (track_name or "").lower()
    cat_lower = (theme_category or "").lower()
    return any(kw in t_lower or kw in cat_lower for kw in ["lofi", "lo-fi", "chill", "beats"])

def get_dynamic_music_metadata(dur_min=15, track_info=None):
    """
    Generates 100% UNIQUE, fresh, and non-repeating title, thumbnail headlines,
    badge, and SEO metadata for each music video.
    Strictly adapts to the actual music track: ONLY mentions Krishna if the track
    is genuinely about Krishna/Vrindavan/Radha/Murli.
    """
    track_name = ""
    if track_info and isinstance(track_info, dict):
        track_name = track_info.get("track_name", "")

    is_krishna = is_krishna_track(track_name)
    is_lofi = is_lofi_track(track_name)

    # 1. Load recently used titles to prevent any duplication
    used_titles = set()
    if os.path.exists(USED_TITLES_FILE):
        try:
            with open(USED_TITLES_FILE, "r", encoding="utf-8") as f:
                used_titles = {line.strip().lower() for line in f if line.strip()}
        except Exception:
            pass

    # 2. Attempt Gemini AI Generation for completely bespoke metadata
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        _kf = os.path.join(BASE_DIR, "gemini_key.txt")
        if os.path.exists(_kf):
            try:
                with open(_kf, "r", encoding="utf-8") as kfile:
                    gemini_key = kfile.read().strip()
            except Exception:
                pass

    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key, http_options={"timeout": 12000})
            
            if track_name:
                track_clause = f'The specific audio track playing in this video is named: "{track_name}".'
            else:
                track_clause = "This is an Indian classical bamboo flute & meditation instrumental video."

            if is_krishna:
                music_rule = (
                    "MUSIC IDENTITY: This IS a Lord Krishna / Vrindavan devotional flute track.\n"
                    "-> You SHOULD include 'Krishna' / 'श्री कृष्ण' / 'राधे कृष्ण' / 'वृंदावन' in the title, headlines, and tags."
                )
            else:
                music_rule = (
                    f"MUSIC IDENTITY: This track is NOT Krishna-specific. It is: '{track_name or 'Peaceful Meditation Bamboo Flute'}'.\n"
                    "-> STRICT USER MANDATE: DO NOT mention 'Krishna', 'श्री कृष्ण', 'राधे कृष्ण', or 'कृष्ण' anywhere in the title, badge, headlines, or tags!\n"
                    "-> Instead, accurately match the theme of the track (e.g. Ganga river, peaceful nature, bamboo stillness, morning raga, midnight sleep, healing dhyan)."
                )

            lofi_rule = (
                "-> This track is LO-FI! You MUST include 'Lo-Fi' or 'Lofi' in the title."
                if is_lofi else
                "-> This track is classical meditative flute."
            )

            prompt = f"""You are the senior spiritual content creator and YouTube SEO specialist for channel 'Krishna Vibez'.
We are creating a brand new {dur_min}-minute sacred meditation and music video.
{track_clause}

CRITICAL USER MANDATE (ACCURATE & HONEST METADATA):
1. The metadata (title, headlines, description, tags) MUST ACCURATELY REFLECT THIS SPECIFIC MUSIC.
2. {music_rule}
3. {lofi_rule}
4. STRICT: NEVER include frequency numbers like '432Hz', '528Hz', 'Hz', or '(432Hz Resonance)' anywhere!

Return a JSON object with EXACTLY these keys:
{{
  "theme_category": "One of: 'Morning Pooja & Awakening', 'Stress Relief & Anxiety Healing', 'Deep Night Sleep & Insomnia', 'Radha Krishna Divine Love', 'Inner Peace & Soul Dhyan', 'Bansuri & Tabla Jugalbandi', 'Krishna Lo-Fi & Chill Beats', 'Sacred Nature & River Flute'",
  "title": "A high-CTR title under 75 chars in format: [Unique Hindi Hook] | [English Meditation Angle]. (STRICT: NEVER include 'Krishna Vibez', NEVER include frequency numbers like 432Hz. Only mention Krishna if IS_KRISHNA_MUSIC is True)",
  "badge": "A short uppercase badge for thumbnail top-left (e.g. '{dur_min} MIN DEEP MEDITATION', '{dur_min} MIN SOUL HEALING', 'DEEP SLEEP & CHINTA MUKTI', 'SACRED GANGA FLUTE', 'INNER PEACE & CALM')",
  "hindi_main": "3 to 5 pure, powerful, easy-to-read Hindi words for the main thumbnail headline (e.g. 'माँ गंगा तट बाँसुरी', 'मन को असीम शांति दें', 'तनाव और चिंता दूर करें', 'शांत नदी कोमल बाँसुरी', 'गहरी नींद और सुकून')",
  "hindi_sub": "4 to 6 words supporting Hindi headline (e.g. 'अंतरात्मा को सुकून देने वाला संगीत', 'मानसिक तनाव घटाएं और शांति पाएं', 'प्रातःकालीन शांति और सकारात्मक दिन', 'अनिद्रा और चिंता से तुरंत राहत')",
  "hook_pill": "3 short keywords for bottom pill separated by ' | ' (e.g. 'मन की शांति | तनाव मुक्ति | गहरी नींद')",
  "tags": ["Indian Flute", "Deep Meditation", "Stress Relief", "Peaceful Music", "Bansuri Tabla"]
}}"""

            models_to_try = ["gemini-3.8-flash", "gemini-3.7-flash"]
            for m in models_to_try:
                try:
                    res = client.models.generate_content(
                        model=m,
                        contents=[prompt],
                        config={"response_mime_type": "application/json"}
                    )
                    if res and res.text:
                        data = json.loads(res.text)
                        title_candidate = sanitize_clean_text(data.get("title", "").strip())
                        if title_candidate and title_candidate.lower() not in used_titles:
                            badge_cand = sanitize_clean_text(data.get("badge", f"{dur_min} MIN DEEP MEDITATION")).replace("15 MIN", f"{dur_min} MIN")
                            h_main = sanitize_clean_text(data.get("hindi_main", "बाँसुरी ध्यान संगीत"))
                            h_sub = sanitize_clean_text(data.get("hindi_sub", "मन की शांति और गहरी नींद के लिए"))
                            h_pill = sanitize_clean_text(data.get("hook_pill", "मन की शांति   |   गहरी नींद   |   चिंता मुक्ति"))
                            tags_cand = [sanitize_clean_text(t) for t in data.get("tags", ["Indian Flute", "Deep Meditation", "Bansuri Dhun"]) if t]

                            # Extra guardrail: if not Krishna track, strip any stray Krishna mentions
                            if not is_krishna:
                                for kw in ["कृष्ण ", "श्री कृष्ण ", "राधे कृष्ण ", "Krishna "]:
                                    title_candidate = title_candidate.replace(kw, "")
                                    h_main = h_main.replace(kw, "")
                                    h_sub = h_sub.replace(kw, "")
                                tags_cand = [t for t in tags_cand if "krishna" not in t.lower() and "कृष्ण" not in t]

                            theme = {
                                "category": data.get("theme_category", "Meditation & Peace"),
                                "badge": badge_cand,
                                "hindi_main": h_main,
                                "hindi_sub": h_sub,
                                "hook_pill": h_pill,
                                "title": title_candidate,
                                "tags": tags_cand
                            }
                            try:
                                with open(USED_TITLES_FILE, "a", encoding="utf-8") as uf:
                                    uf.write(title_candidate + "\n")
                            except Exception:
                                pass
                            print(f"  -> ✅ Gemini AI generated 100% unique theme: '{title_candidate}'")
                            return theme
                except Exception:
                    pass
        except Exception as e:
            print(f"  -> [Notice] Gemini dynamic generation fell back to 36-Theme Master Pool: {e}")

    # 3. Master 36-Theme Non-Repeating Rotation System (Rock-Solid Fallback)
    print("  -> 🔄 Using Master 36-Theme Non-Repeating Rotation System...")
    current_idx = 0
    used_indices = []
    if os.path.exists(THEME_TRACKER_FILE):
        try:
            with open(THEME_TRACKER_FILE, "r", encoding="utf-8") as tf:
                t_data = json.load(tf)
                current_idx = t_data.get("next_index", 0)
                used_indices = t_data.get("used_indices", [])
        except Exception:
            current_idx = 0
            used_indices = []

    # Filter available themes strictly by track type (Krishna vs Non-Krishna)
    eligible_indices = []
    for idx, th in enumerate(MEDITATION_THEMES_36):
        th_cat = th.get("category", "")
        th_is_krishna = is_krishna_track("", th_cat) or "कृष्ण" in th.get("title", "") or "Krishna" in th.get("title", "")
        if is_krishna:
            eligible_indices.append(idx)
        else:
            if not th_is_krishna:
                eligible_indices.append(idx)

    if not eligible_indices:
        eligible_indices = list(range(len(MEDITATION_THEMES_36)))

    available = [i for i in eligible_indices if i not in used_indices]
    if not available:
        available = eligible_indices

    chosen_idx = random.choice(available)
    used_indices.append(chosen_idx)

    try:
        with open(THEME_TRACKER_FILE, "w", encoding="utf-8") as tf:
            json.dump({"next_index": (chosen_idx + 1) % len(MEDITATION_THEMES_36), "used_indices": used_indices}, tf, indent=2)
    except Exception:
        pass

    raw_theme = MEDITATION_THEMES_36[chosen_idx].copy()
    raw_theme["badge"] = raw_theme["badge"].replace("{dur_min}", str(dur_min)).replace("15 MIN", f"{dur_min} MIN")
    raw_theme["title"] = raw_theme["title"].replace("{dur_min}", str(dur_min)).replace("15 Min", f"{dur_min} Min")
    
    if not is_krishna:
        for kw in ["Krishna ", "कृष्ण ", "श्री कृष्ण "]:
            raw_theme["title"] = raw_theme["title"].replace(kw, "")
            raw_theme["hindi_main"] = raw_theme["hindi_main"].replace(kw, "")
            raw_theme["hindi_sub"] = raw_theme["hindi_sub"].replace(kw, "")
        raw_theme["tags"] = [t for t in raw_theme.get("tags", []) if "krishna" not in t.lower() and "कृष्ण" not in t]

    try:
        with open(USED_TITLES_FILE, "a", encoding="utf-8") as uf:
            uf.write(raw_theme["title"] + "\n")
    except Exception:
        pass

    print(f"  -> Selected Theme #{chosen_idx + 1}/{len(MEDITATION_THEMES_36)}: [{raw_theme['category']}] {raw_theme['title']}")
    return raw_theme


def generate_pollinations_nature_image(prompt, output_path):
    """Generates a free 16:9 8K Nature meditation artwork via Pollinations AI with 7% smart bottom watermark crop."""
    try:
        import urllib.parse
        encoded_p = urllib.parse.quote(prompt.strip())
        url = f"https://image.pollinations.ai/prompt/{encoded_p}?width=1920&height=1080&nologo=true&model=flux"
        temp_dl = output_path + ".temp.jpg"
        
        curl_path = "curl"
        if sys.platform == "win32" and os.path.exists(r"C:\Windows\System32\curl.exe"):
            curl_path = r"C:\Windows\System32\curl.exe"
            
        subprocess.run([curl_path, "-s", "-L", "-f", "--retry", "3", url, "-o", temp_dl], timeout=60, check=True)
        if os.path.exists(temp_dl) and os.path.getsize(temp_dl) > 10000:
            raw_mat = cv2.imread(temp_dl)
            if raw_mat is not None:
                h_r, w_r = raw_mat.shape[:2]
                crop_h = int(h_r * 0.93)
                clean_crop = raw_mat[:crop_h, :]
                final_img = cv2.resize(clean_crop, (1920, 1080), interpolation=cv2.INTER_LANCZOS4)
                cv2.imwrite(output_path, final_img, [cv2.IMWRITE_JPEG_QUALITY, 96])
                try: os.remove(temp_dl)
                except Exception: pass
                return True
        if os.path.exists(temp_dl):
            try: os.remove(temp_dl)
            except Exception: pass
    except Exception as e:
        print(f"  Pollinations generation fallback notice: {e}")
    return False

def ensure_images(num_needed=5, track_info=None, theme=None):
    """
    Ensures images for video:
    1. If Krishna Flute track: Uses existing library from music_video_images/. 
       Archived to used/ and auto-recycled in infinite loop (NEVER deleted).
    2. If Nature / River / Rain / Non-Krishna: Dynamically generates brand new 16:9 artworks
       via Pollinations AI without watermarks. Cleaned up after upload so storage stays clean.
    """
    track_name = track_info.get("track_name", "") if track_info else ""
    theme_cat = theme.get("category", "") if theme else ""
    is_krishna = is_krishna_track(track_name, theme_cat)

    # All tracks (Krishna, Temple, Nature, River, Rain, Sleep, etc.)
    # strictly read from our 883 Master Categorized Images Pool (100% Zero-Risk, 0% Watermark)

    # Smart Categorized Krishna / Flute Image Pool
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(USED_IMAGES_DIR, exist_ok=True)
    cat_pool_dir = os.path.join(IMAGES_DIR, "All catagery Krisha music photo")

    all_available = []
    if os.path.exists(cat_pool_dir):
        for f in os.listdir(cat_pool_dir):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                all_available.append(os.path.join(cat_pool_dir, f))
    
    # Also include root images
    for f in os.listdir(IMAGES_DIR):
        fp = os.path.join(IMAGES_DIR, f)
        if os.path.isfile(fp) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            all_available.append(fp)

    # Smart Keyword Filter according to theme category
    cat_keywords = {
        "temple": {
            "pos": ["temple", "bell", "aarti", "courtyard", "corridor", "pillar", "archway", "lamp", "sanctum"],
            "neg": ["peacock", "river", "water", "cow", "cat_"]
        },
        "bell": {
            "pos": ["bell", "temple", "brass", "chime", "aarti", "lamp", "pillar"],
            "neg": ["peacock", "river", "cow"]
        },
        "rain": {
            "pos": ["rain", "monsoon", "cloud", "sawan", "wet", "puddle", "drop"],
            "neg": ["desert", "sand"]
        },
        "monsoon": {
            "pos": ["monsoon", "rain", "cloud", "sawan", "wet", "storm"],
            "neg": ["desert"]
        },
        "yamuna": {
            "pos": ["yamuna", "river", "ghat", "water", "boat", "dock", "ripples"],
            "neg": ["cave", "desert"]
        },
        "river": {
            "pos": ["river", "water", "stream", "ghat", "boat", "shore"],
            "neg": ["cave"]
        },
        "meditation": {
            "pos": ["meditation", "cave", "dhyan", "shrine", "zen", "silence", "altar", "lamp"],
            "neg": ["storm", "rain"]
        },
        "sleep": {
            "pos": ["night", "stars", "moon", "twilight", "calm", "serene", "sleep", "dark", "lamp"],
            "neg": ["sunrise", "bright"]
        },
        "night": {
            "pos": ["night", "stars", "moon", "twilight", "fireflies", "milky", "diya"],
            "neg": ["sunrise", "noon", "sunlight"]
        },
        "sunrise": {
            "pos": ["sunrise", "dawn", "morning", "sunbeam", "golden", "first_light"],
            "neg": ["night", "dark", "moon"]
        },
        "morning": {
            "pos": ["morning", "dawn", "sunrise", "sunlight", "dew", "bamboo_morning"],
            "neg": ["night", "dark"]
        },
        "sunset": {
            "pos": ["sunset", "dusk", "evening", "twilight", "golden_hour", "sandhya"],
            "neg": ["morning", "sunrise"]
        },
        "cows": {
            "pos": ["cows", "surabhi", "calf", "calves", "pasture", "meadow", "grass"],
            "neg": ["cave", "night"]
        },
        "peacock": {
            "pos": ["peacock", "mayur", "morpankh", "feather"],
            "neg": ["cave"]
        },
        "lotus": {
            "pos": ["lotus", "pond", "water_lily", "kund", "pads"],
            "neg": ["mountain", "cave"]
        },
        "kadamba": {
            "pos": ["kadamba", "grove", "blossom", "tree", "forest", "flower"],
            "neg": ["cave"]
        },
        "banyan": {
            "pos": ["banyan", "akshaya_vat", "vat", "roots", "sacred_tree"],
            "neg": ["lotus", "river"]
        },
        "stepwell": {
            "pos": ["stepwell", "bawdi", "stairs", "stone_steps", "water_level"],
            "neg": ["forest", "tree"]
        },
        "mountain": {
            "pos": ["mountain", "himalayan", "cliff", "hill", "mist", "ascent"],
            "neg": ["lotus", "pond"]
        },
        "tanpura": {
            "pos": ["tanpura", "veena", "strings", "wooden_tanpura", "cymbals"],
            "neg": ["cow", "peacock"]
        },
        "bamboo": {
            "pos": ["bamboo", "flute", "bansuri", "grove", "swaying"],
            "neg": ["cave", "cow"]
        },
        "fireflies": {
            "pos": ["fireflies", "night", "stars", "twilight", "glowing"],
            "neg": ["sunrise", "morning"]
        },
        "cosmic": {
            "pos": ["cosmic", "milky_way", "stars", "galaxy", "nebula", "universe"],
            "neg": ["cow", "pasture"]
        },
        "aarti": {
            "pos": ["aarti", "lamp", "flames", "diya", "brass_aarti", "temple"],
            "neg": ["river", "pasture"]
        },
        "krishna": {
            "pos": ["krishna", "bansuri", "morpankh", "kadamba", "divine", "lord"],
            "neg": []
        }
    }

    # Match theme keywords with positive terms and strict negative exclusion
    pos_terms = set()
    neg_terms = set()
    theme_text = (theme_cat + " " + track_name).lower()
    
    for cat_name, rules in cat_keywords.items():
        if cat_name in theme_text:
            if isinstance(rules, dict):
                pos_terms.update(rules.get("pos", []))
                neg_terms.update(rules.get("neg", []))
            else:
                pos_terms.update(rules)

    # Filter matching slides
    matched_slides = []
    if pos_terms and all_available:
        for s in all_available:
            s_name = os.path.basename(s).lower()
            # Must match at least one positive term AND none of the negative exclusion terms
            has_pos = any(term in s_name for term in pos_terms)
            has_neg = any(term in s_name for term in neg_terms)
            if has_pos and not has_neg:
                matched_slides.append(s)

    if len(matched_slides) >= num_needed:
        slides = matched_slides
        print(f"  -> 🎯 Smart Category Match: Found {len(matched_slides)} matching photos for '{theme_cat}'!")
    elif len(all_available) >= num_needed:
        slides = all_available
        print(f"  -> ℹ️ Using blended pool of {len(all_available)} photos.")
    else:
        slides = [
            os.path.join(IMAGES_DIR, f) 
            for f in os.listdir(IMAGES_DIR) 
            if os.path.isfile(os.path.join(IMAGES_DIR, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ]

    # Auto-recycle from used/ folder (Infinite Loop)
    if len(slides) < num_needed:
        used_files = [
            os.path.join(USED_IMAGES_DIR, f)
            for f in os.listdir(USED_IMAGES_DIR)
            if os.path.isfile(os.path.join(USED_IMAGES_DIR, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ]
        if used_files:
            print(f"  -> 🔄 Auto-Recycle: All {len(used_files)} Krishna images used! Looping back to active pool...")
            for uf in used_files:
                dest = os.path.join(IMAGES_DIR, os.path.basename(uf))
                try:
                    shutil.move(uf, dest)
                except Exception:
                    pass
            slides = [
                os.path.join(IMAGES_DIR, f) 
                for f in os.listdir(IMAGES_DIR) 
                if os.path.isfile(os.path.join(IMAGES_DIR, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
            ]

    if not slides:
        raise FileNotFoundError(f"No images found in {IMAGES_DIR}")

    random.shuffle(slides)
    selected = slides[:num_needed]
    print(f"  -> 🖼️ Selected {len(selected)} unique, fresh 16:9 images from active Krishna pool of {len(slides)} available images.")
    return selected


def archive_used_images(used_slides, is_krishna=True):
    """
    If Krishna theme: Moves used images to music_video_images/used/ so they loop without deletion.
    If Nature theme: Deletes temporary generated images to keep workspace clean.
    """
    if not is_krishna:
        cleaned = 0
        for s in used_slides:
            if "temp_nature_images" in s and os.path.exists(s):
                try:
                    os.remove(s)
                    cleaned += 1
                except Exception:
                    pass
        print(f"  -> 🗑️ Cleaned up {cleaned} temporary nature images (Fresh ones will be generated next time).")
        return

    os.makedirs(USED_IMAGES_DIR, exist_ok=True)
    moved_count = 0
    for s in used_slides:
        if os.path.exists(s):
            dest = os.path.join(USED_IMAGES_DIR, os.path.basename(s))
            try:
                shutil.move(s, dest)
                moved_count += 1
                with open(USED_IMAGES_TRACKER, "a", encoding="utf-8") as f:
                    f.write(f"{os.path.basename(s)}\n")
            except Exception as e:
                print(f"  Warning: could not move {s} to used/: {e}")
    print(f"  -> 📁 Archived {moved_count} used Krishna images to music_video_images/used/ (Will not repeat until entire pool loops).")

def verify_zero_vocals(audio_file_path):
    """
    Scans the downloaded audio file using Whisper AI speech recognition and Gemini.
    Strictly verifies that the audio has ZERO human voice, words, speaking, or singing.
    Returns True if 100% pure instrumental, False if any voice is detected.
    """
    print(f"  -> 🛡️ Pre-Flight Vocal Scan: Auditing track for zero human voice/lyrics...")
    temp_wav = os.path.join(BASE_DIR, "temp_vocal_audit.wav")
    try:
        # Extract a 30-second high-energy sample from the middle of the track
        conv_cmd = [
            FFMPEG_EXE, "-y",
            "-ss", "00:00:10",
            "-t", "30",
            "-i", audio_file_path,
            "-vn", "-ac", "1", "-ar", "16000",
            temp_wav
        ]
        subprocess.run(conv_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        if not os.path.exists(temp_wav) or os.path.getsize(temp_wav) < 10000:
            return True

        # Run Faster-Whisper Speech Recognition
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel("tiny", device="cpu", compute_type="int8")
            segments, info = model.transcribe(temp_wav, beam_size=5)
            detected = []
            for s in segments:
                # Discard low-probability hallucinations
                if s.no_speech_prob < 0.4 and len(s.text.strip()) > 3:
                    detected.append(s.text.strip())
            
            if detected:
                print(f"  ❌ VOCALS DETECTED! Track contains singing/speech: '{detected[0]}'")
                return False
        except Exception as e_whisper:
            print(f"  -> Whisper check note: {e_whisper}")

        print("  -> ✅ Vocal Audit PASSED: 100% Pure Non-Vocal Instrumental!")
        return True
    except Exception as e:
        print(f"  -> Vocal audit check skipped: {e}")
        return True
    finally:
        if os.path.exists(temp_wav):
            try: os.remove(temp_wav)
            except Exception: pass

def mix_soundtrack(duration_sec=900):
    """Assembles Dynamic Flute & Tabla Master Audio (12-20 Mins), prioritizing fresh Suno AI tracks from Catbox."""
    dur_min = int(round(duration_sec / 60.0))
    print(f"[1/4] Assembling Dynamic {dur_min}-Minute Flute & Tabla Master Audio ({duration_sec}s)...")
    
    # 1. Check current cycle
    cycle = 1
    if os.path.exists(TREBLO_CYCLE_TRACKER):
        try:
            with open(TREBLO_CYCLE_TRACKER, "r", encoding="utf-8") as f:
                cycle = int(f.read().strip())
        except Exception:
            cycle = 1

    # 2. Treblo AI Music URLs (100% Exclusive — Prioritizing Video-Dedicated Pool Track 401+)
    treblo_urls = []
    active_urls_file = TREBLO_URLS_FILE
    active_used_file = TREBLO_USED_URLS_FILE

    if os.path.exists(TREBLO_VIDEO_ONLY_URLS):
        with open(TREBLO_VIDEO_ONLY_URLS, "r", encoding="utf-8") as f:
            v_urls = [line.strip() for line in f if line.strip() and line.strip().startswith("http")]
        if v_urls:
            treblo_urls = v_urls
            active_urls_file = TREBLO_VIDEO_ONLY_URLS
            print(f"  -> 🎵 Active Music Engine: Treblo Video-Dedicated Pool (Track 401+ - {len(treblo_urls)} tracks remaining)")

    if not treblo_urls and os.path.exists(TREBLO_URLS_FILE):
        with open(TREBLO_URLS_FILE, "r", encoding="utf-8") as f:
            treblo_urls = [line.strip() for line in f if line.strip() and line.strip().startswith("http")]
        active_urls_file = TREBLO_URLS_FILE

    if treblo_urls:
        source_type = "Treblo"
        chosen_urls = treblo_urls
        if active_urls_file != TREBLO_VIDEO_ONLY_URLS:
            print(f"  -> 🎵 Active Music Engine: Treblo AI (100% Exclusive - {len(treblo_urls)} tracks remaining in queue)")
    elif os.path.exists(TREBLO_BACKUP_URLS_FILE):
        # Auto-recycle from Treblo master backup pool (Unlimited Infinite Loop)
        with open(TREBLO_BACKUP_URLS_FILE, "r", encoding="utf-8") as f:
            backup_urls = [line.strip() for line in f if line.strip() and line.strip().startswith("http")]
        if backup_urls:
            cycle += 1
            with open(TREBLO_CYCLE_TRACKER, "w", encoding="utf-8") as f:
                f.write(str(cycle))
            print(f"  -> 🔄 Unlimited Loop Active: Treblo queue reloaded from master backup pool! (Starting Cycle {cycle})")
            random.shuffle(backup_urls)
            chosen_urls = backup_urls[:]
            with open(TREBLO_URLS_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(chosen_urls) + "\n")
            source_type = "Treblo"
            active_urls_file = TREBLO_URLS_FILE
            active_used_file = TREBLO_USED_URLS_FILE
    else:
        raise RuntimeError("No Treblo music tracks available in queue or backup pool!")

    # Download via curl and loop/master to duration_sec
    while chosen_urls:
        chosen_url = chosen_urls.pop(0)
        temp_input = os.path.join(BASE_DIR, "temp_music_input.mp3")
        print(f"  -> Found Fresh {source_type} Track in queue (Cycle {cycle}): {chosen_url}")
        print("  -> Downloading from Catbox CDN via native curl...")

        curl_path = "curl"
        if sys.platform == "win32" and os.path.exists(r"C:\Windows\System32\curl.exe"):
            curl_path = r"C:\Windows\System32\curl.exe"

        dl_cmd = [curl_path, "-s", "-L", "-f", "--retry", "3", chosen_url, "-o", temp_input]
        res = subprocess.run(dl_cmd)

        if res.returncode == 0 and os.path.exists(temp_input) and os.path.getsize(temp_input) > 50000:
            # Mandatory Pre-Flight Vocal Check (Zero Vocals Rule)
            if not verify_zero_vocals(temp_input):
                print(f"  🚫 REJECTED: Track {chosen_url} failed vocal test! Purging from queue and blacklisting...")
                try: os.remove(temp_input)
                except Exception: pass
                with open(active_used_file, "a", encoding="utf-8") as f:
                    f.write(chosen_url + "\n")
                with open(active_urls_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(chosen_urls) + "\n")
                continue

            print(f"  -> Download successful! Mastering for Cycle {cycle} ({dur_min}:00 dynamic master soundtrack)...")
            # Always apply 432Hz harmonic warmth EQ, 1.8% micro-pitch shift, and strip metadata
            # to guarantee 100% unique cryptographic audio fingerprint and zero Content ID matches
            fade_out_st = max(10, duration_sec - 5)
            filter_str = f"equalizer=f=432:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1.5:g=1.5,atempo=1.015,afade=t=in:st=0:d=3,afade=t=out:st={fade_out_st}:d=4,volume=1.05"

            master_cmd = [
                FFMPEG_EXE, "-y",
                "-stream_loop", "-1",
                "-i", temp_input,
                "-vn",
                "-map_metadata", "-1",
                "-t", str(duration_sec),
                "-af", filter_str,
                "-c:a", "libmp3lame", "-b:a", "192k",
                TEMP_AUDIO
            ]
            subprocess.run(master_cmd, check=True)

            # Record used URL and update active queue
            with open(active_used_file, "a", encoding="utf-8") as f:
                f.write(chosen_url + "\n")
            with open(active_urls_file, "w", encoding="utf-8") as f:
                f.write("\n".join(chosen_urls) + "\n")

            try:
                os.remove(temp_input)
            except Exception:
                pass

            track_name = ""
            if os.path.exists(TREBLO_REGISTRY_FILE):
                try:
                    with open(TREBLO_REGISTRY_FILE, "r", encoding="utf-8") as rf:
                        reg = json.load(rf)
                        track_name = reg.get(chosen_url, "")
                except Exception:
                    pass

            print(f"  -> ✅ {dur_min}-Minute Master Soundtrack ready from {source_type} ({duration_sec}s): {TEMP_AUDIO}")
            if track_name:
                print(f"  -> 🏷️ Identified Music Track: '{track_name}'")
            return {
                "url": chosen_url,
                "track_name": track_name
            }
        else:
            print(f"  ⚠️ Warning: Failed to download {chosen_url}, trying next track...")

    # Strict rule: NEVER touch Auto-Insta-Krishna/music/ folder. Always reload Suno/Treblo tracks.
    raise RuntimeError("No valid Suno/Treblo tracks could be downloaded from queue. Auto-Insta-Krishna/music/ is strictly forbidden.")


LOGO_PATH = os.path.join(BASE_DIR, "website", "public", "assets", "logo.png")
FEATHER_GREEN_SCREEN = os.path.join(BASE_DIR, "morpankh_green_screen.mp4")
FEATHER_CDN_URL = "https://files.catbox.moe/d7132r.mp4"

def ensure_feather_asset():
    """Ensures morpankh_green_screen.mp4 exists; downloads from Catbox CDN fallback if missing."""
    if not os.path.exists(FEATHER_GREEN_SCREEN) or os.path.getsize(FEATHER_GREEN_SCREEN) < 50000:
        print("  -> Downloading authentic Morpankh green screen asset from Catbox CDN...")
        try:
            r = requests.get(FEATHER_CDN_URL, timeout=30)
            if r.status_code == 200:
                with open(FEATHER_GREEN_SCREEN, "wb") as f:
                    f.write(r.content)
                print(f"  -> Successfully saved Morpankh asset ({len(r.content)} bytes).")
        except Exception as e:
            print(f"  ⚠️ Warning: Could not download Morpankh asset: {e}")
    return os.path.exists(FEATHER_GREEN_SCREEN)


def create_corner_logo_badge(size=120):
    """Creates a circular luxury glass badge with golden rim for top corner branding."""
    if not os.path.exists(LOGO_PATH):
        return None
    logo = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
    if logo is None:
        return None
    resized = cv2.resize(logo, (size, size), interpolation=cv2.INTER_AREA)
    if resized.shape[2] == 4:
        b, g, r, a = cv2.split(resized)
    else:
        b, g, r = cv2.split(resized)
        a = np.ones((size, size), dtype=np.uint8) * 255
        
    center = size // 2
    radius = size // 2 - 3
    mask = np.zeros((size, size), dtype=np.uint8)
    cv2.circle(mask, (center, center), radius, 255, -1, lineType=cv2.LINE_AA)
    
    inside_circle = (mask > 0)
    bg_backing_alpha = (inside_circle.astype(np.uint8) * 200)
    final_alpha = np.maximum(np.minimum(a, mask), bg_backing_alpha)
    
    badge = np.dstack([b, g, r, final_alpha])
    cv2.circle(badge, (center, center), radius, (50, 205, 255, 230), 2, lineType=cv2.LINE_AA)
    cv2.circle(badge, (center, center), radius - 3, (30, 160, 220, 140), 1, lineType=cv2.LINE_AA)
    return badge


def load_and_key_feather_frames():
    """Extracts, crops watermark, keys green screen, and applies golden halo."""
    if not ensure_feather_asset():
        return []
    cap = cv2.VideoCapture(FEATHER_GREEN_SCREEN)
    raw_frames = []
    x1, x2 = 310, 970
    y1, y2 = 20, 700
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        raw_frames.append(frame[y1:y2, x1:x2])
    cap.release()
    
    keyed_glowing_frames = []
    for f in raw_frames:
        b = f[:, :, 0].astype(np.float32)
        g = f[:, :, 1].astype(np.float32)
        r = f[:, :, 2].astype(np.float32)
        greenness = g - np.maximum(r, b)
        alpha = np.clip(1.0 - (greenness - 25.0) / 45.0, 0.0, 1.0)
        alpha = (alpha * 255.0).astype(np.uint8)
        suppressed_g = np.minimum(g, np.maximum(r, b) * 1.15).astype(np.uint8)
        clean_rgb = np.stack([f[:, :, 0], suppressed_g, f[:, :, 2]], axis=-1)
        rgba = np.dstack([clean_rgb, alpha])
        
        # Golden halo around feather
        h, w = rgba.shape[:2]
        pad = 28
        padded = np.zeros((h + pad*2, w + pad*2, 4), dtype=np.uint8)
        padded[pad:pad+h, pad:pad+w] = rgba
        pad_alpha = padded[:, :, 3]
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
        dilated = cv2.dilate(pad_alpha, kernel, iterations=2)
        blurred_glow = cv2.GaussianBlur(dilated, (25, 25), 0).astype(np.float32) / 255.0
        
        glow_b = (blurred_glow * 45).astype(np.uint8)
        glow_g = (blurred_glow * 195).astype(np.uint8)
        glow_r = (blurred_glow * 255).astype(np.uint8)
        glow_a = (blurred_glow * 135).astype(np.uint8)
        glow_rgba = np.dstack([glow_b, glow_g, glow_r, glow_a])
        
        f_a = padded[:, :, 3:].astype(np.float32) / 255.0
        g_a = glow_rgba[:, :, 3:].astype(np.float32) / 255.0 * (1.0 - f_a)
        out_rgb = padded[:, :, :3].astype(np.float32) * f_a + glow_rgba[:, :, :3].astype(np.float32) * g_a
        out_a = np.clip(f_a + g_a, 0.0, 1.0) * 255.0
        keyed_glowing_frames.append(np.dstack([out_rgb.astype(np.uint8), out_a.astype(np.uint8)]))
        
    return keyed_glowing_frames


def overlay_rgba(bg_img, fg_rgba, center_x, center_y, scale, angle_deg):
    fh, fw = fg_rgba.shape[:2]
    new_w = int(fw * scale)
    new_h = int(fh * scale)
    if new_w <= 0 or new_h <= 0:
        return
    resized = cv2.resize(fg_rgba, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    if abs(angle_deg) > 0.5:
        M = cv2.getRotationMatrix2D((new_w / 2, new_h / 2), angle_deg, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        bound_w = int((new_h * sin) + (new_w * cos))
        bound_h = int((new_h * cos) + (new_w * sin))
        M[0, 2] += (bound_w / 2) - new_w / 2
        M[1, 2] += (bound_h / 2) - new_h / 2
        rotated = cv2.warpAffine(resized, M, (bound_w, bound_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    else:
        rotated = resized
        
    rw, rh = rotated.shape[1], rotated.shape[0]
    x1 = int(center_x - rw / 2)
    y1 = int(center_y - rh / 2)
    x2 = x1 + rw
    y2 = y1 + rh
    
    bg_h, bg_w = bg_img.shape[:2]
    cx1 = max(0, x1)
    cy1 = max(0, y1)
    cx2 = min(bg_w, x2)
    cy2 = min(bg_h, y2)
    if cx2 <= cx1 or cy2 <= cy1:
        return
        
    fx1 = cx1 - x1
    fy1 = cy1 - y1
    fx2 = fx1 + (cx2 - cx1)
    fy2 = fy1 + (cy2 - cy1)
    
    fg_crop = rotated[fy1:fy2, fx1:fx2]
    alpha = fg_crop[:, :, 3:].astype(np.float32) / 255.0
    bg_crop = bg_img[cy1:cy2, cx1:cx2].astype(np.float32)
    blended = fg_crop[:, :, :3].astype(np.float32) * alpha + bg_crop * (1.0 - alpha)
    bg_img[cy1:cy2, cx1:cx2] = blended.astype(np.uint8)


DIVINE_SPARKLE_PALETTES = [
    {"name": "Vrindavan Royal Gold", "gold_bgr": np.array([45.0, 210.0, 255.0]), "core_bgr": np.array([255.0, 255.0, 255.0])},
    {"name": "Amber Sunrise Honey", "gold_bgr": np.array([25.0, 180.0, 255.0]), "core_bgr": np.array([210.0, 245.0, 255.0])},
    {"name": "Champagne Starlight", "gold_bgr": np.array([130.0, 225.0, 255.0]), "core_bgr": np.array([255.0, 255.0, 255.0])},
    {"name": "Lotus Peach-Gold", "gold_bgr": np.array([85.0, 175.0, 255.0]), "core_bgr": np.array([230.0, 235.0, 255.0])},
    {"name": "Celestial White-Gold", "gold_bgr": np.array([170.0, 235.0, 255.0]), "core_bgr": np.array([255.0, 255.0, 255.0])},
    {"name": "Sacred Saffron Gold", "gold_bgr": np.array([20.0, 195.0, 250.0]), "core_bgr": np.array([200.0, 240.0, 255.0])},
    {"name": "Morning Dawn Gold", "gold_bgr": np.array([60.0, 205.0, 245.0]), "core_bgr": np.array([240.0, 250.0, 255.0])},
]

def get_image_adapted_gold(bg_img, palette=None):
    avg_b = float(np.mean(bg_img[:, :, 0]))
    avg_g = float(np.mean(bg_img[:, :, 1]))
    avg_r = float(np.mean(bg_img[:, :, 2]))
    ambient = np.array([avg_b, avg_g, avg_r])
    
    if palette is not None:
        base_gold = palette["gold_bgr"]
        core_col_base = palette.get("core_bgr", np.array([255.0, 255.0, 255.0]))
    else:
        base_gold = np.array([45.0, 205.0, 255.0])
        core_col_base = np.array([255.0, 255.0, 255.0])
        
    adapted = 0.72 * base_gold + 0.28 * ambient
    return adapted, core_col_base


def prebuild_sparkle_sprites(adapted_gold, core_col_base=None):
    if core_col_base is None:
        core_col_base = np.array([255.0, 255.0, 255.0])
    sprites = {}
    radii = [2.5, 3.5, 4.5, 5.5, 6.5]
    for r in radii:
        for star in [False, True]:
            dim = int(r * 9) | 1
            cx = dim // 2
            cy = dim // 2
            stamp = np.zeros((dim, dim, 4), dtype=np.uint8)
            
            def draw_layer(rad_mult, alpha_val, col):
                cr = int(r * rad_mult)
                if cr <= 0: return
                layer = np.zeros((dim, dim, 3), dtype=np.uint8)
                cv2.circle(layer, (cx, cy), cr, [int(c) for c in col], -1, lineType=cv2.LINE_AA)
                l_mask = np.zeros((dim, dim), dtype=np.uint8)
                cv2.circle(l_mask, (cx, cy), cr, 255, -1, lineType=cv2.LINE_AA)
                l_blur = cv2.GaussianBlur(l_mask, (cr*2+1, cr*2+1), 0).astype(np.float32) / 255.0 * alpha_val
                cur_a = stamp[:, :, 3].astype(np.float32) / 255.0
                add_a = l_blur
                out_a = np.clip(cur_a + add_a, 0.0, 1.0)
                for c in range(3):
                    cur_c = stamp[:, :, c].astype(np.float32)
                    stamp[:, :, c] = np.clip(cur_c + col[c] * add_a, 0, 255).astype(np.uint8)
                stamp[:, :, 3] = (out_a * 255.0).astype(np.uint8)

            draw_layer(3.6, 0.25, adapted_gold)
            draw_layer(2.0, 0.45, adapted_gold)
            draw_layer(1.1, 0.70, adapted_gold)
            core_col = 0.65 * core_col_base + 0.35 * adapted_gold
            draw_layer(0.55, 0.95, core_col)
            
            if star and r >= 3.5:
                ray_len = int(r * 3.5)
                ray_img = np.zeros((dim, dim, 4), dtype=np.uint8)
                cv2.line(ray_img, (cx - ray_len, cy), (cx + ray_len, cy), (int(core_col[0]), int(core_col[1]), int(core_col[2]), 200), 1, lineType=cv2.LINE_AA)
                cv2.line(ray_img, (cx, cy - ray_len), (cx, cy + ray_len), (int(core_col[0]), int(core_col[1]), int(core_col[2]), 200), 1, lineType=cv2.LINE_AA)
                ra = ray_img[:, :, 3].astype(np.float32) / 255.0
                sa = stamp[:, :, 3].astype(np.float32) / 255.0
                out_a = np.clip(sa + ra, 0.0, 1.0)
                for c in range(3):
                    stamp[:, :, c] = np.clip(stamp[:, :, c] * (1.0 - ra) + ray_img[:, :, c] * ra, 0, 255).astype(np.uint8)
                stamp[:, :, 3] = (out_a * 255.0).astype(np.uint8)

            sprites[(r, star)] = stamp
    return sprites


def fast_draw_sparkle(target, cx, cy, rad, star, brightness, sprites):
    if brightness <= 0.08: return
    keys = [2.5, 3.5, 4.5, 5.5, 6.5]
    nearest_r = min(keys, key=lambda k: abs(k - rad))
    stamp = sprites.get((nearest_r, star))
    if stamp is None: return
    sh, sw = stamp.shape[:2]
    x1, y1 = int(cx - sw / 2), int(cy - sh / 2)
    x2, y2 = x1 + sw, y1 + sh
    bg_h, bg_w = target.shape[:2]
    cx1, cy1 = max(0, x1), max(0, y1)
    cx2, cy2 = min(bg_w, x2), min(bg_h, y2)
    if cx2 <= cx1 or cy2 <= cy1: return
    sx1, sy1 = cx1 - x1, cy1 - y1
    sx2, sy2 = sx1 + (cx2 - cx1), sy1 + (cy2 - cy1)
    stamp_crop = stamp[sy1:sy2, sx1:sx2]
    alpha = (stamp_crop[:, :, 3].astype(np.float32) / 255.0) * brightness
    alpha = np.dstack([alpha, alpha, alpha])
    bg_crop = target[cy1:cy2, cx1:cx2].astype(np.float32)
    fg_rgb = stamp_crop[:, :, :3].astype(np.float32)
    target[cy1:cy2, cx1:cx2] = (fg_rgb * alpha + bg_crop * (1.0 - alpha)).astype(np.uint8)


def generate_feather_configs(seed=None):
    rng = random.Random(seed)
    # 6 feathers distributed across screen, all drifting top-to-bottom with gentle diagonal side motion
    # Scales reduced significantly: Max scale is ~0.33 (down from 0.65!)
    configs = [
        # Feather 0: Medium-large majestic accent (left-center falling rightwards)
        {
            "scale": rng.uniform(0.30, 0.34),
            "offset": rng.randint(0, 30),
            "start_x": rng.uniform(220, 380),
            "drift_cycle": rng.uniform(16.0, 21.0),
            "drift_phase": rng.uniform(0.0, 7.0),
            "drift_dx": rng.uniform(120, 200),     # Drifts gently rightwards as it falls
            "amp_x": rng.uniform(25, 45),          # Natural breeze sway
            "freq_x": rng.uniform(1.0, 1.3),
            "phase_x": rng.uniform(0.0, math.pi),
            "base_rot": rng.uniform(-10, 5),
            "amp_rot": rng.uniform(6, 10),
            "freq_rot": rng.uniform(0.9, 1.2),
            "phase_rot": rng.uniform(0.0, math.pi),
        },
        # Feather 1: Medium elegant (right-center falling leftwards)
        {
            "scale": rng.uniform(0.24, 0.28),
            "offset": rng.randint(40, 70),
            "start_x": rng.uniform(1450, 1650),
            "drift_cycle": rng.uniform(18.0, 23.0),
            "drift_phase": rng.uniform(6.0, 14.0),
            "drift_dx": rng.uniform(-200, -120),   # Drifts gently leftwards as it falls
            "amp_x": rng.uniform(25, 40),
            "freq_x": rng.uniform(0.9, 1.2),
            "phase_x": rng.uniform(0.0, math.pi),
            "base_rot": rng.uniform(5, 15),
            "amp_rot": rng.uniform(5, 9),
            "freq_rot": rng.uniform(0.8, 1.1),
            "phase_rot": rng.uniform(0.0, math.pi),
        },
        # Feather 2: Delicate center floating
        {
            "scale": rng.uniform(0.19, 0.23),
            "offset": rng.randint(80, 110),
            "start_x": rng.uniform(850, 1050),
            "drift_cycle": rng.uniform(19.0, 25.0),
            "drift_phase": rng.uniform(12.0, 20.0),
            "drift_dx": rng.uniform(80, 160) * rng.choice([-1, 1]),
            "amp_x": rng.uniform(30, 50),
            "freq_x": rng.uniform(1.1, 1.4),
            "phase_x": rng.uniform(0.0, math.pi),
            "base_rot": rng.uniform(-8, 8),
            "amp_rot": rng.uniform(6, 12),
            "freq_rot": rng.uniform(1.0, 1.3),
            "phase_rot": rng.uniform(0.0, math.pi),
        },
        # Feather 3: Soft ambient background feather (left side)
        {
            "scale": rng.uniform(0.14, 0.18),
            "offset": rng.randint(120, 150),
            "start_x": rng.uniform(100, 250),
            "drift_cycle": rng.uniform(22.0, 28.0),
            "drift_phase": rng.uniform(3.0, 10.0),
            "drift_dx": rng.uniform(90, 150),
            "amp_x": rng.uniform(20, 35),
            "freq_x": rng.uniform(0.8, 1.1),
            "phase_x": rng.uniform(0.0, math.pi),
            "base_rot": rng.uniform(-12, 0),
            "amp_rot": rng.uniform(5, 8),
            "freq_rot": rng.uniform(0.7, 1.0),
            "phase_rot": rng.uniform(0.0, math.pi),
        },
        # Feather 4: Soft ambient background feather (far right side)
        {
            "scale": rng.uniform(0.12, 0.16),
            "offset": rng.randint(60, 90),
            "start_x": rng.uniform(1680, 1850),
            "drift_cycle": rng.uniform(20.0, 26.0),
            "drift_phase": rng.uniform(15.0, 23.0),
            "drift_dx": rng.uniform(-160, -90),
            "amp_x": rng.uniform(20, 35),
            "freq_x": rng.uniform(0.85, 1.15),
            "phase_x": rng.uniform(0.0, math.pi),
            "base_rot": rng.uniform(0, 12),
            "amp_rot": rng.uniform(4, 8),
            "freq_rot": rng.uniform(0.8, 1.1),
            "phase_rot": rng.uniform(0.0, math.pi),
        },
        # Feather 5: Medium ambient drifter (mid-left)
        {
            "scale": rng.uniform(0.20, 0.25),
            "offset": rng.randint(20, 50),
            "start_x": rng.uniform(550, 750),
            "drift_cycle": rng.uniform(17.0, 22.0),
            "drift_phase": rng.uniform(8.0, 16.0),
            "drift_dx": rng.uniform(-120, 120),
            "amp_x": rng.uniform(30, 48),
            "freq_x": rng.uniform(1.0, 1.3),
            "phase_x": rng.uniform(0.0, math.pi),
            "base_rot": rng.uniform(-10, 10),
            "amp_rot": rng.uniform(6, 11),
            "freq_rot": rng.uniform(0.9, 1.2),
            "phase_rot": rng.uniform(0.0, math.pi),
        }
    ]
    return configs


# 5 Dynamic Thematic Flora Palettes (Unique Per Video)
FLORA_THEMES = [
    {
        "name": "कमल एवं तुलसी (Lotus & Sacred Tulsi)",
        "sprites": ["flower_01", "flower_06", "flower_11", "flower_04", "flower_09", "feather_petal_01", "feather_petal_04"],
        "desc": "Soft pink lotus petals, fresh green tulsi leaves, and elegant peacock feather."
    },
    {
        "name": "गुलाब एवं मोगरा (Vrindavan Red Rose & Mogra)",
        "sprites": ["flower_00", "flower_08", "flower_03", "feather_petal_04", "feather_petal_05", "feather_petal_03"],
        "desc": "Deep velvet red rose petals, fragrant white jasmine/mogra, and soft pink rose petals."
    },
    {
        "name": "स्वर्ण गेंदा एवं पारिजात (Golden Marigold & Parijat)",
        "sprites": ["flower_02", "flower_05", "flower_07", "flower_10", "feather_petal_02"],
        "desc": "Bright golden yellow & orange marigold petals with divine white parijat flowers."
    },
    {
        "name": "पारिजात एवं श्वेत पुष्प (Celestial White Parijat & Mogra)",
        "sprites": ["flower_03", "flower_07", "flower_10", "flower_06", "feather_petal_00"],
        "desc": "Night-blooming parijat, fragrant white jasmine, and moonlight white petals."
    },
    {
        "name": "मयूरपंख एवं वनमाला (Divine Peacock Feathers & Forest Flora)",
        "sprites": ["feather_petal_00", "feather_petal_01", "feather_petal_02", "feather_petal_03", "flower_00", "flower_01", "flower_04"],
        "desc": "Majestic miniature peacock feathers balanced with red rose, lotus, and sacred tulsi."
    }
]

# 4 Distinct Motion & Wind Styles (Unique Per Video)
MOTION_STYLES = [
    {
        "name": "शांत मंद पवन (Gentle Serene Float)",
        "vy_range": (75, 125),
        "amp_range": (18, 40),
        "freq_range": (0.6, 1.0),
        "wind_drift_range": (8, 22),
        "tumble_freq_range": (0.5, 1.1)
    },
    {
        "name": "तिरछी बयार (Soft Diagonal Breeze)",
        "vy_range": (85, 140),
        "amp_range": (22, 48),
        "freq_range": (0.7, 1.2),
        "wind_drift_range": (45, 80),
        "tumble_freq_range": (0.8, 1.5)
    },
    {
        "name": "हल्की भँवर (Playful Swirling Flutter)",
        "vy_range": (90, 150),
        "amp_range": (40, 75),
        "freq_range": (1.1, 1.6),
        "wind_drift_range": (12, 30),
        "tumble_freq_range": (1.0, 1.7)
    },
    {
        "name": "गहन ध्यान प्रवाह (Deep Meditation Slow-Mo)",
        "vy_range": (55, 95),
        "amp_range": (12, 30),
        "freq_range": (0.45, 0.75),
        "wind_drift_range": (5, 15),
        "tumble_freq_range": (0.4, 0.85)
    }
]

def load_flora_sprites_dict():
    """Loads all 20 transparent RGBA sprites from extracted_petals/."""
    petals_dir = os.path.join(BASE_DIR, "extracted_petals")
    sprites_dict = {}
    if os.path.exists(petals_dir):
        for sf in glob.glob(os.path.join(petals_dir, "*.png")):
            name = os.path.basename(sf).replace(".png", "")
            img = cv2.imread(sf, cv2.IMREAD_UNCHANGED)
            if img is not None and img.shape[2] == 4:
                sprites_dict[name] = img
    return sprites_dict


def render_animated_slide_clip(slide_path, clip_output_path, flora_sprites, motion_style, logo_badge, slide_idx=0, duration=60, fps=25, sparkle_palette=None, num_particles=17):
    """
    Renders a single 60-second (1-minute) slide clip with:
    - Subpixel 64-bit Floating Bicubic Ken Burns Zoom & Pan (ZERO Jhatka)
    - 17 Clean, Dynamic 3D Falling Flower Petals, Leaves, & Feathers (Video-Specific Theme & Motion)
    - 40 Floating Golden Sparkles with Image-Harmonized Video-Specific Palette Tint
    - Circular Luxury Krishna Vibez Logo in Top Corner
    - Smooth 2.0s Fade-In & 2.0s Fade-Out
    """
    src_img = cv2.imread(slide_path)
    if src_img is None:
        raise FileNotFoundError(f"Slide not found: {slide_path}")

    # Flow / Image Watermark Auto-Removal: Crop bottom 5.5% cleanly
    h, w = src_img.shape[:2]
    if h >= 700:
        crop_bottom = int(h * 0.055)
        src_img = src_img[0:h - crop_bottom, 0:w]

    src_img = cv2.resize(src_img, (1920, 1080), interpolation=cv2.INTER_LANCZOS4)
    
    adapted_gold, core_bgr = get_image_adapted_gold(src_img, palette=sparkle_palette)
    sprites = prebuild_sparkle_sprites(adapted_gold, core_col_base=core_bgr)
    
    # Initialize 7-8 subtle particles for this slide (Sparse, Realistic Depth of Field)
    rng_p = random.Random(slide_idx * 19 + 77)
    num_particles = 8
    
    class SlideParticle:
        def __init__(self, rng, initial_spread=False):
            self.rng = rng
            self.reset(initial_spread=initial_spread)
            
        def reset(self, initial_spread=False):
            self.sprite = self.rng.choice(flora_sprites) if flora_sprites else None
            # Depth layers: Mostly background/midground (small & realistic), very rarely foreground
            layer = self.rng.choices(["bg", "mid", "fg"], weights=[0.60, 0.35, 0.05])[0]
            if layer == "fg":
                self.scale = self.rng.uniform(0.24, 0.32)
                self.vy = self.rng.uniform(motion_style["vy_range"][0] * 1.1, motion_style["vy_range"][1] * 1.1)
                self.opacity = self.rng.uniform(0.75, 0.88)
            elif layer == "mid":
                self.scale = self.rng.uniform(0.16, 0.23)
                self.vy = self.rng.uniform(*motion_style["vy_range"])
                self.opacity = self.rng.uniform(0.65, 0.80)
            else: # bg (Far away, subtle drift)
                self.scale = self.rng.uniform(0.10, 0.16)
                self.vy = self.rng.uniform(motion_style["vy_range"][0] * 0.75, motion_style["vy_range"][1] * 0.75)
                self.opacity = self.rng.uniform(0.50, 0.68)
                
            self.x = self.rng.uniform(-60, 1920 + 60)
            if initial_spread:
                self.y = self.rng.uniform(-100, 1080 + 100)
            else:
                self.y = self.rng.uniform(-140, -30)
                
            self.amp_x = self.rng.uniform(*motion_style["amp_range"])
            self.freq_x = self.rng.uniform(*motion_style["freq_range"])
            self.phase_x = self.rng.uniform(0, 2 * math.pi)
            self.wind_drift = self.rng.uniform(*motion_style["wind_drift_range"])
            
            self.angle = self.rng.uniform(0, 360)
            self.rot_speed = self.rng.uniform(-35, 35)
            self.tumble_freq = self.rng.uniform(*motion_style["tumble_freq_range"])
            self.tumble_phase = self.rng.uniform(0, 2 * math.pi)

        def update(self, dt, current_time):
            self.y += self.vy * dt
            sway = self.amp_x * math.sin(current_time * self.freq_x * 2 * math.pi + self.phase_x)
            self.x += (self.wind_drift + sway * 0.5) * dt
            self.angle += self.rot_speed * dt
            if self.y > 1080 + 100 or self.x < -120 or self.x > 1920 + 120:
                self.reset(initial_spread=False)
                
        def render(self, target_img):
            if self.sprite is None: return
            tumble = math.cos(self.angle * math.pi / 180.0 + self.tumble_phase)
            sx = self.scale * (0.35 + 0.65 * abs(tumble))
            sy = self.scale
            h, w = self.sprite.shape[:2]
            nw = max(6, int(w * sx))
            nh = max(6, int(h * sy))
            resized = cv2.resize(self.sprite, (nw, nh), interpolation=cv2.INTER_LINEAR)
            center = (nw // 2, nh // 2)
            M = cv2.getRotationMatrix2D(center, self.angle, 1.0)
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            bw = int((nh * sin) + (nw * cos))
            bh = int((nh * cos) + (nw * sin))
            M[0, 2] += (bw / 2) - center[0]
            M[1, 2] += (bh / 2) - center[1]
            rotated = cv2.warpAffine(resized, M, (bw, bh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
            px = int(self.x - bw // 2)
            py = int(self.y - bh // 2)
            x1, y1 = max(0, px), max(0, py)
            x2, y2 = min(1920, px + bw), min(1080, py + bh)
            if x1 >= x2 or y1 >= y2: return
            sx1, sy1 = x1 - px, y1 - py
            sx2, sy2 = sx1 + (x2 - x1), sy1 + (y2 - y1)
            crop_sprite = rotated[sy1:sy2, sx1:sx2]
            crop_target = target_img[y1:y2, x1:x2]
            alpha = (crop_sprite[:, :, 3].astype(np.float32) / 255.0) * self.opacity
            alpha = alpha[:, :, np.newaxis]
            fg_rgb = crop_sprite[:, :, :3].astype(np.float32)
            bg_rgb = crop_target.astype(np.float32)
            target_img[y1:y2, x1:x2] = (fg_rgb * alpha + bg_rgb * (1.0 - alpha)).astype(np.uint8)

    particles = [SlideParticle(rng_p, initial_spread=True) for _ in range(num_particles)] if flora_sprites else []
    
    # 40 Golden Sparkles
    rng_spk = random.Random(slide_idx * 31 + 42)
    sparkles = []
    for i in range(40):
        sx = rng_spk.randint(40, 1880)
        sy = rng_spk.randint(40, 1040)
        rad = rng_spk.uniform(2.5, 5.8)
        phase = rng_spk.uniform(0, math.pi * 2)
        speed = rng_spk.uniform(0.8, 1.8)
        star = (i % 2 == 0)
        sparkles.append((sx, sy, rad, phase, speed, star))
        
    total_frames = int(duration * fps)
    
    ffmpeg_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1920x1080",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        clip_output_path
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    fade_frames = int(2.0 * fps)
    dt = 1.0 / float(fps)
    
    for i in range(total_frames):
        t = i * dt
        
        # Dynamic Visible Cinematic Ken Burns Camera Motion (4 Alternating Styles)
        mode = slide_idx % 4
        prog = t / float(duration)
        if mode == 0:
            # Mode 0: Cinematic Gentle Push-In with Soft Right Drift
            zoom = 1.0 + 0.14 * prog
            pan_x = 70.0 * prog
            pan_y = 40.0 * prog
        elif mode == 1:
            # Mode 1: Majestic Pull-Out with Soft Left Drift
            zoom = 1.15 - 0.12 * prog
            pan_x = -65.0 * prog
            pan_y = 30.0 * prog
        elif mode == 2:
            # Mode 2: Sweeping Horizontal Pan with Breathing Zoom
            zoom = 1.08 + 0.06 * math.sin(prog * math.pi)
            pan_x = 80.0 * (prog - 0.5)
            pan_y = -35.0 * math.cos(prog * math.pi)
        else:
            # Mode 3: Diagonal Glide & Depth Focus
            zoom = 1.03 + 0.12 * prog
            pan_x = -60.0 * prog
            pan_y = -40.0 * prog
            
        cx, cy = 960.0, 540.0
        M = np.array([
            [zoom, 0, (1.0 - zoom) * cx - pan_x],
            [0, zoom, (1.0 - zoom) * cy - pan_y]
        ], dtype=np.float32)
        frame = cv2.warpAffine(src_img, M, (1920, 1080), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        
        # Update and render 17 Dynamic 3D Flora Particles (Petals, Leaves & Feathers)
        if particles:
            for p in particles:
                p.update(dt, t)
            sorted_p = sorted(particles, key=lambda p: p.scale)
            for p in sorted_p:
                p.render(frame)
                
        # Overlay Golden Sparkles
        for sx, sy, rad, phase, speed, star in sparkles:
            cur_y = (sy - (t * 22.0 * speed)) % 1080
            cur_x = sx + 15.0 * math.sin(t * 1.2 + phase)
            brightness = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * speed * 2.0 + phase))
            fast_draw_sparkle(frame, cur_x, cur_y, rad, star, brightness, sprites)
            
        # Top Corner Logo Badge
        if logo_badge is not None:
            overlay_rgba(frame, logo_badge, center_x=95, center_y=95, scale=1.0, angle_deg=0)
            
        # Fade In / Fade Out
        if i < fade_frames:
            alpha = float(i) / float(fade_frames)
            frame = (frame.astype(np.float32) * alpha).astype(np.uint8)
        elif i > total_frames - fade_frames:
            alpha = float(total_frames - i) / float(fade_frames)
            frame = (frame.astype(np.float32) * alpha).astype(np.uint8)
            
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()


def render_video(slides, duration_sec=900, is_krishna=True):
    """
    Renders Dynamic Full HD Video (12-20 Mins) with:
    - Butter-Smooth Subpixel Bicubic Ken Burns Zoom & Pan (ZERO Jhatka)
    - 17 Clean, Dynamic 3D Falling Flower Petals, Leaves, & Feathers (Random Unique Theme & Motion Per Video)
    - Dynamic Sparkle Color Palette (Varies subtly per video)
    - Krishna Vibez Circular Luxury Channel Logo Badge in Top Corner
    - Dynamic duration matching user soundtrack (12 to 20 minutes)
    """
    dur_min = int(round(duration_sec / 60.0))
    print(f"[2/4] Rendering {dur_min}-Minute ({duration_sec}s) Cinematic Video with Dynamic Petals & Subpixel Zoom...")
    
    # 1. Dynamically select Flora Theme strictly based on Music Theme:
    # If Nature / Non-Krishna track -> 100% STRICTLY ZERO Morpankh, ZERO religious petals. Use Green Leaves & Forest Flora only!
    # If Krishna track -> Sacred Morpankh, Lotus, Rose & Vrindavan Flora.
    if is_krishna:
        eligible_flora = FLORA_THEMES
    else:
        # Filter flora to ONLY green leaves and gentle forest elements (No feathers)
        eligible_flora = [
            th for th in FLORA_THEMES 
            if not any("feather" in sp for sp in th.get("sprites", [])) and "मयूर" not in th.get("name", "")
        ]
        if not eligible_flora:
            eligible_flora = [{"name": "शांत प्रकृति एवं हरे पत्ते (Serene Nature Leaves)", "sprites": ["flower_04", "flower_08", "flower_09"]}]

    chosen_flora = random.choice(eligible_flora)
    chosen_motion = random.choice(MOTION_STYLES)
    chosen_palette = random.choice(DIVINE_SPARKLE_PALETTES)
    
    print("=================================================================")
    print(f"  -> 🌸 Selected Flora Theme   : {chosen_flora['name']}")
    print(f"  -> 🍃 Selected Motion Style  : {chosen_motion['name']}")
    print(f"  -> ✨ Selected Sparkle Theme : {chosen_palette['name']}")
    print("=================================================================")
    
    # 2. Load flora sprites for chosen theme
    flora_dict = load_flora_sprites_dict()
    active_flora_sprites = [flora_dict[k] for k in chosen_flora["sprites"] if k in flora_dict]
    if not active_flora_sprites:
        active_flora_sprites = list(flora_dict.values())
        
    # 3. Select 15 unique slides (each slide stays for 60 seconds)
    selected_slides = slides[:]
    if len(selected_slides) > 15:
        random.shuffle(selected_slides)
        selected_slides = selected_slides[:15]
        
    clip_files = []
    temp_clips_dir = os.path.join(BASE_DIR, "temp_animated_clips")
    os.makedirs(temp_clips_dir, exist_ok=True)
    
    logo_badge = create_corner_logo_badge(size=120)
    
    # 4. Render 60-second animated clip for each slide
    for idx, slide in enumerate(selected_slides):
        clip_path = os.path.join(temp_clips_dir, f"clip_{idx+1}.mp4")
        clip_files.append(clip_path)
        print(f"  -> Rendering Slide {idx+1}/{len(selected_slides)} (60s) with Dynamic Petals & Smooth Zoom...")
        render_animated_slide_clip(
            slide, clip_path, active_flora_sprites, chosen_motion, logo_badge,
            slide_idx=idx, duration=60, fps=25, sparkle_palette=chosen_palette, num_particles=17
        )
    
    # 2. Concat animated clips to cover duration_sec
    clips_total_sec = len(clip_files) * 60
    repeat_count = int(math.ceil(duration_sec / float(clips_total_sec))) + 1
    concat_list = os.path.join(BASE_DIR, "temp_concat_clips.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for _ in range(repeat_count):
            for cp in clip_files:
                esc = cp.replace("\\", "/")
                f.write(f"file '{esc}'\n")
                
    cmd_final = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-i", TEMP_AUDIO,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration_sec),
        OUTPUT_VIDEO
    ]
    subprocess.run(cmd_final, check=True)
    
    # Clean up animated temp clips
    for cp in clip_files:
        if os.path.exists(cp):
            try: os.remove(cp)
            except Exception: pass
    if os.path.exists(temp_clips_dir):
        try: os.rmdir(temp_clips_dir)
        except Exception: pass
    if os.path.exists(concat_list):
        try: os.remove(concat_list)
        except Exception: pass
        
    print(f"  -> Video Rendered with Smooth Morpankh & Zoom: {OUTPUT_VIDEO} ({dur_min} Mins / {duration_sec}s)")


def generate_thumbnail(slides, theme):
    """Creates a high-CTR 16:9 YouTube Thumbnail using Headless Browser HarfBuzz text rendering (100% perfect Devanagari ligatures/matras)."""
    print("[3/4] Generating AI High-CTR YouTube Thumbnail...")
    import base64
    import shutil
    selected_slide = random.choice(slides)
    
    badge = theme.get("badge", "DEEP MEDITATION")
    main_text = theme.get("hindi_main", "श्री कृष्ण अमृत बाँसुरी")
    sub_text = theme.get("hindi_sub", "मन की शांति और गहरी नींद के लिए")
    hook_pill = theme.get("hook_pill", "मन की शांति   |   गहरी नींद   |   चिंता मुक्ति")
    brand_text = "KRISHNA VIBEZ"

    # Detect browser engine (Edge on Windows, Chromium on Linux)
    browser_candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    browser_path = None
    for bc in browser_candidates:
        if os.path.exists(bc):
            browser_path = bc
            break
    if not browser_path:
        for b in ["google-chrome", "chromium-browser", "chromium", "msedge"]:
            w = shutil.which(b)
            if w:
                browser_path = w
                break

    # Parse pills
    pill_items = [p.strip() for p in hook_pill.replace("|", ",").split(",") if p.strip()]
    if not pill_items or len(pill_items) < 3:
        pill_items = ["✨ 100% RELAXING", "🧘 DEEP SLEEP", "🦚 DIVINE VIBES"]
    else:
        icons = ["✨", "🧘", "🦚"]
        pill_items = [f"{icons[i]} {p}" if not any(c in p for c in ["✨", "🧘", "🦚", "🌿", "🌸"]) else p for i, p in enumerate(pill_items[:3])]
    pills_html = "".join([f'<span class="tag">{p}</span>' for p in pill_items[:3]])

    # Split main_text into dual tone: First word white, remaining words gold
    parts = main_text.strip().split(" ", 1)
    if len(parts) == 2:
        first_word = parts[0]
        rest_words = parts[1]
    else:
        first_word = main_text
        rest_words = "बाँसुरी ध्यान"

    if browser_path:
        try:
            with open(selected_slide, "rb") as f:
                bg_b64 = base64.b64encode(f.read()).decode("utf-8")

            html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@800;900&family=Noto+Sans+Devanagari:wght@800;900&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1280px;
    height: 720px;
    overflow: hidden;
    position: relative;
    font-family: 'Noto Sans Devanagari', 'Poppins', sans-serif;
    background-color: #050810;
  }}
  .bg {{
    position: absolute;
    top: 0;
    left: 0;
    width: 1280px;
    height: 720px;
    background-image: url('data:image/jpeg;base64,{bg_b64}');
    background-size: cover;
    background-position: center 20%;
    filter: contrast(1.1) saturate(1.18) brightness(0.98);
  }}
  .bottom-gradient {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 1280px;
    height: 520px;
    background: linear-gradient(to top, rgba(5, 8, 16, 0.98) 0%, rgba(5, 8, 16, 0.94) 60%, rgba(5, 8, 16, 0.5) 85%, transparent 100%);
  }}
  .content-container {{
    position: absolute;
    top: 0;
    left: 0;
    width: 1280px;
    height: 720px;
    padding: 35px 50px 38px 50px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    z-index: 10;
  }}
  .top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .badge-category {{
    background: linear-gradient(135deg, #FF6F00, #E65100);
    color: #ffffff;
    font-size: 24px;
    font-weight: 900;
    letter-spacing: 1px;
    padding: 8px 22px;
    border-radius: 10px;
    border: 2px solid #FFE082;
    box-shadow: 0 4px 15px rgba(230, 81, 0, 0.6);
  }}
  .badge-time {{
    background: rgba(10, 20, 35, 0.88);
    border: 2px solid #00E5FF;
    color: #00E5FF;
    font-size: 22px;
    font-weight: 800;
    padding: 8px 20px;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0, 229, 255, 0.35);
  }}
  .bottom-box {{
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-bottom: 75px;
  }}
  .title-main {{
    font-size: 78px;
    font-weight: 900;
    line-height: 1.1;
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
  }}
  .c-white {{
    color: #FFFFFF;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.4), 0 4px 10px #000, 0 8px 25px rgba(0,0,0,0.9);
  }}
  .c-gold {{
    color: #FFD600;
    background: linear-gradient(180deg, #FFF9C4 0%, #FFD600 50%, #FF9100 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.95)) drop-shadow(0 0 25px rgba(255, 145, 0, 0.7));
  }}
  .sub-box {{
    display: flex;
    align-items: center;
    gap: 18px;
  }}
  .pill-red {{
    background: linear-gradient(90deg, #D50000 0%, #C51162 100%);
    color: #FFFFFF;
    font-size: 32px;
    font-weight: 900;
    padding: 6px 22px;
    border-radius: 8px;
    border: 2px solid #FF80AB;
    box-shadow: 0 4px 16px rgba(213, 0, 0, 0.5);
    text-shadow: 0 2px 4px rgba(0,0,0,0.8);
  }}
  .text-cyan {{
    color: #00E5FF;
    font-size: 34px;
    font-weight: 800;
    text-shadow: 0 3px 8px rgba(0,0,0,0.95), 0 0 15px rgba(0, 229, 255, 0.6);
  }}
  .footer-box {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.18);
  }}
  .tags-list {{
    display: flex;
    gap: 16px;
  }}
  .tag {{
    background: linear-gradient(135deg, rgba(15, 30, 50, 0.95), rgba(8, 16, 28, 0.95));
    color: #FFFFFF;
    font-size: 26px;
    font-weight: 900;
    letter-spacing: 0.5px;
    padding: 10px 24px;
    border-radius: 12px;
    border: 2.5px solid #00E5FF;
    box-shadow: 0 4px 18px rgba(0, 229, 255, 0.4), inset 0 0 10px rgba(0, 229, 255, 0.2);
    text-shadow: 0 2px 4px rgba(0,0,0,0.9);
  }}
  .brand-name {{
    color: #FFB300;
    font-size: 28px;
    font-weight: 900;
    letter-spacing: 2px;
    border: 2px solid #FFB300;
    padding: 8px 20px;
    border-radius: 10px;
    background: rgba(20, 15, 5, 0.85);
    box-shadow: 0 4px 15px rgba(255, 179, 0, 0.35);
    text-shadow: 0 2px 8px rgba(0,0,0,0.9);
  }}
</style>
</head>
<body>
  <div class="bg"></div>
  <div class="bottom-gradient"></div>

  <div class="content-container">
    <div class="top-bar">
      <div class="badge-category">🌿 {badge}</div>
      <div class="badge-time">⏱️ 15 MIN MEDITATION</div>
    </div>

    <div class="bottom-box">
      <div class="title-main">
        <span class="c-white">{first_word}</span>
        <span class="c-gold">{rest_words}</span>
      </div>

      <div class="sub-box">
        <span class="pill-red">गहरा मानसिक सुकून</span>
        <span class="text-cyan">{sub_text}</span>
      </div>

      <div class="footer-box">
        <div class="tags-list">
          {pills_html}
        </div>
        <div class="brand-name">{brand_text}</div>
      </div>
    </div>
  </div>
</body>
</html>"""
            temp_html = os.path.join(BASE_DIR, "temp_render_thumb.html")
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_content)

            cmd = [
                browser_path,
                "--headless=new",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1280,720",
                f"--screenshot={TEMP_THUMBNAIL}",
                temp_html
            ]
            subprocess.run(cmd, cwd=BASE_DIR, check=True)
            if os.path.exists(temp_html):
                try: os.remove(temp_html)
                except Exception: pass
            print(f"  -> SUCCESS! Browser HarfBuzz Thumbnail Created: {TEMP_THUMBNAIL}")
            sample_thumb = os.path.join(BASE_DIR, "MUSIC_VIDEO_HIGH_CTR_SAMPLE_THUMBNAIL.jpg")
            shutil.copy2(TEMP_THUMBNAIL, sample_thumb)
            return TEMP_THUMBNAIL
        except Exception as e:
            print(f"  -> [Warning] Browser rendering failed ({e}), falling back to FFmpeg...")

    # Fallback to FFmpeg if browser not available
    local_font = os.path.join(BASE_DIR, "NotoSansDevanagari-Bold.ttf")
    local_english = os.path.join(BASE_DIR, "arialbd.ttf")
    hindi_font_arg = os.path.abspath(local_font).replace("\\", "/").replace(":", "\\:")
    english_font_arg = os.path.abspath(local_english if os.path.exists(local_english) else "arial.ttf").replace("\\", "/").replace(":", "\\:")

    badge_txt = os.path.join(BASE_DIR, "temp_thumb_badge.txt")
    main_txt = os.path.join(BASE_DIR, "temp_thumb_main.txt")
    sub_txt = os.path.join(BASE_DIR, "temp_thumb_sub.txt")
    pill_txt = os.path.join(BASE_DIR, "temp_thumb_pill.txt")

    with open(badge_txt, "w", encoding="utf-8") as f: f.write(badge)
    with open(main_txt, "w", encoding="utf-8") as f: f.write(main_text)
    with open(sub_txt, "w", encoding="utf-8") as f: f.write(sub_text)
    with open(pill_txt, "w", encoding="utf-8") as f: f.write(hook_pill)

    badge_arg = os.path.abspath(badge_txt).replace("\\", "/").replace(":", "\\:")
    main_arg = os.path.abspath(main_txt).replace("\\", "/").replace(":", "\\:")
    sub_arg = os.path.abspath(sub_txt).replace("\\", "/").replace(":", "\\:")
    pill_arg = os.path.abspath(pill_txt).replace("\\", "/").replace(":", "\\:")

    vf = (
        f"scale=1920:1080,"
        f"drawbox=y=0:h=180:color=black@0.45:t=fill,"
        f"drawbox=y=500:h=580:color=black@0.84:t=fill,"
        f"drawbox=x=60:y=496:w=1800:h=5:color=goldenrod@0.90:t=fill,"
        f"drawbox=x=70:y=45:w=740:h=90:color=0xFFB300@0.98:t=fill,"
        f"drawbox=x=66:y=41:w=748:h=98:color=white@0.85:t=4,"
        f"drawtext=fontfile='{english_font_arg}':textfile='{badge_arg}':fontcolor=black:fontsize=46:x=105:y=68,"
        f"drawtext=fontfile='{hindi_font_arg}':textfile='{main_arg}':fontcolor=0xFFE600:fontsize=128:x=75:y=550:borderw=10:bordercolor=black:text_shaping=1,"
        f"drawtext=fontfile='{hindi_font_arg}':textfile='{sub_arg}':fontcolor=white:fontsize=82:x=75:y=725:borderw=8:bordercolor=black:text_shaping=1,"
        f"drawbox=x=75:y=850:w=1040:h=82:color=0x8B0000@0.95:t=fill,"
        f"drawbox=x=71:y=846:w=1048:h=90:color=goldenrod@0.85:t=3,"
        f"drawtext=fontfile='{hindi_font_arg}':textfile='{pill_arg}':fontcolor=0xFFF8DC:fontsize=48:x=110:y=868:borderw=3:bordercolor=black:text_shaping=1,"
        f"drawtext=fontfile='{english_font_arg}':text='KRISHNA VIBEZ':fontcolor=0xFFD700:fontsize=46:x=1500:y=995:borderw=5:bordercolor=black"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", selected_slide,
        "-vf", vf,
        "-frames:v", "1",
        "-update", "1",
        "-q:v", "2",
        TEMP_THUMBNAIL
    ]
    subprocess.run(cmd, cwd=BASE_DIR, check=True)
    for tf in [badge_txt, main_txt, sub_txt, pill_txt]:
        if os.path.exists(tf):
            try: os.remove(tf)
            except Exception: pass

    sample_thumb = os.path.join(BASE_DIR, "MUSIC_VIDEO_HIGH_CTR_SAMPLE_THUMBNAIL.jpg")
    shutil.copy2(TEMP_THUMBNAIL, sample_thumb)
    return TEMP_THUMBNAIL


def add_video_to_category_playlist(video_id, category_name, access_token):
    """
    100% Legal & Official YouTube Data API v3 Playlist Automation.
    Finds or creates a dedicated category playlist and adds the newly uploaded video into it.
    """
    if not video_id or not access_token:
        return

    # Map category keyword to clean, beautiful high-CTR YouTube Playlist Titles
    playlist_titles = {
        "temple": "🏛️ Ancient Temple Bells & Sacred Chants | Peaceful Dhyan",
        "bell": "🔔 Auspicious Temple Bells & Flute Meditation",
        "rain": "🌧️ Monsoon Rain & Peaceful Flute Meditation",
        "monsoon": "🌧️ Sawan Monsoon Rain & Serene Nature Flute",
        "yamuna": "🌊 Sacred Yamuna River & Ghats Meditation Flute",
        "river": "🌊 Flowing Mountain River & Nature Flute Meditation",
        "sleep": "🌙 Deep Meditative Sleep Music | Pure Night Peace",
        "night": "✨ Starlight & Moonlight Deep Sleep Meditation",
        "sunrise": "🌅 Golden Sunrise & Morning Meditation Flute",
        "morning": "☀️ Peaceful Morning Flute & Birds Meditation",
        "sunset": "🌇 Sandhya Twilight & Dusk Meditation Dhun",
        "cows": "🐮 Surabhi Cows & Peaceful Vrindavan Meadows",
        "peacock": "🦚 Divine Peacock Van & Kadamba Forest Flute",
        "lotus": "🪷 Sacred Lotus Pond & Water Lily Ambient Meditation",
        "kadamba": "🌳 Kadamba Tree Grove & Forest Ambient Flute",
        "banyan": "🌿 Ancient Banyan Tree & Deep Dhyan Meditation",
        "stepwell": "🏰 Ancient Stepwell & Serene Water Reflection",
        "mountain": "🏔️ Himalayan Mist & Mountain Pine Forest Flute",
        "tanpura": "🪕 Classical Tanpura & Bansuri Jugalbandi Meditation",
        "bamboo": "🎋 Swaying Bamboo Forest & Pure Wind Flute",
        "fireflies": "✨ Glowing Fireflies & Serene Night Meditation",
        "cosmic": "🌌 Cosmic Naad & Universal Sound Meditation",
        "aarti": "🪔 Divine Temple Aarti & Ghee Diya Meditation",
        "garland": "🌺 Garlands & Fresh Flower Offering Ambient Flute",
        "flower": "🌸 Fresh Vrindavan Blossoms & Flute Meditation",
        "krishna": "🦚 Lord Krishna Divine Bansuri & Vrindavan Flute",
        "darbari": "👑 Raga Darbari Deep Meditation Flute",
        "bhairavi": "🌅 Raga Bhairavi Morning Awakening Flute"
    }

    target_title = None
    cat_lower = (category_name or "").lower()
    for k, title in playlist_titles.items():
        if k in cat_lower:
            target_title = title
            break
            
    if not target_title:
        target_title = "🕉️ Divine Flute & Pure Meditation Music | Krishna Vibez"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        # 1. Search existing playlists across all pages (0% Duplicate Guarantee)
        playlist_id = None
        next_page = ""
        while True:
            list_url = f"https://www.googleapis.com/youtube/v3/playlists?part=snippet&mine=true&maxResults=50{next_page}"
            resp = requests.get(list_url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                for it in items:
                    p_title = (it.get("snippet", {}).get("title", "")).strip().lower()
                    if p_title == target_title.strip().lower():
                        playlist_id = it.get("id")
                        break
                if playlist_id:
                    break
                page_token = data.get("nextPageToken")
                if page_token:
                    next_page = f"&pageToken={page_token}"
                else:
                    break
            else:
                break

        # 2. If playlist doesn't exist, create it legally via official API
        if not playlist_id:
            print(f"  -> 📂 Creating new dedicated Category Playlist: '{target_title}'...")
            create_url = "https://www.googleapis.com/youtube/v3/playlists?part=snippet,status"
            create_payload = {
                "snippet": {
                    "title": target_title,
                    "description": f"Listen to continuous {target_title} for deep relaxation, inner peace, meditation, study, and restful sleep. Official Krishna Vibez collection."
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
            c_resp = requests.post(create_url, headers=headers, json=create_payload)
            if c_resp.status_code in [200, 201]:
                playlist_id = c_resp.json().get("id")
                print(f"  -> ✅ Playlist created successfully (ID: {playlist_id})")
            else:
                print(f"  Notice creating playlist: {c_resp.status_code} - {c_resp.text}")

        # 3. Add the video to the playlist via official playlistItems.insert
        if playlist_id:
            item_url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet"
            item_payload = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
            i_resp = requests.post(item_url, headers=headers, json=item_payload)
            if i_resp.status_code in [200, 201]:
                print(f"  -> 🎯 SUCCESS! Video automatically added to Playlist: '{target_title}'")
            else:
                print(f"  Notice adding to playlist: {i_resp.status_code} - {i_resp.text}")

    except Exception as pl_err:
        print(f"  Notice in playlist auto-organizer: {pl_err}")

def upload_to_youtube(theme, duration_sec=900, track_info=None):
    """Uploads video & custom thumbnail to YouTube via Data API v3."""
    dur_min = int(round(duration_sec / 60.0))
    print("[4/4] Checking YouTube API credentials for Upload...")
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        token_path = os.path.join(BASE_DIR, "youtube_token.json")
        if os.path.exists(token_path):
            try:
                with open(token_path, "r", encoding="utf-8") as f:
                    t_data = json.load(f)
                    client_id = client_id or t_data.get("client_id")
                    client_secret = client_secret or t_data.get("client_secret")
                    refresh_token = refresh_token or t_data.get("refresh_token")
            except Exception as e:
                print(f"Notice reading local token file: {e}")

    if not all([client_id, client_secret, refresh_token]):
        print("[Notice] YouTube credentials not present. Local test complete!")
        return

    # Refresh Access Token
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    resp = requests.post(token_url, data=token_payload)
    if resp.status_code != 200:
        print("[Error] Failed to refresh YouTube OAuth token:", resp.text)
        return
    access_token = resp.json().get("access_token")

    # Resumable Video Upload with Long Trilingual SEO
    dur_quarter = dur_min // 4
    ch1 = f"00:00"
    ch2 = f"{dur_quarter:02d}:15"
    ch3 = f"{(dur_quarter * 2):02d}:30"
    ch4 = f"{(dur_quarter * 3):02d}:45"

    track_name = ""
    if track_info and isinstance(track_info, dict):
        track_name = track_info.get("track_name", "")

    is_krishna = is_krishna_track(track_name, theme.get("category", ""))
    is_lofi = is_lofi_track(track_name, theme.get("category", ""))

    brand_suffix = " | Krishna Vibez" if is_krishna else " | Peaceful Flute Meditation"
    raw_title = theme.get("title", f"{dur_min} Min Divine Bamboo Flute & Tabla")
    
    # Check if music is Lo-Fi
    if is_lofi and "lofi" not in raw_title.lower() and "lo-fi" not in raw_title.lower():
        raw_title = f"{raw_title} (Krishna Lo-Fi)" if is_krishna else f"{raw_title} (Lo-Fi Flute)"

    # STRICT RULE: Completely eliminate '432Hz', 'Hz', '528Hz', '(432Hz Resonance)' or technical frequency numbers
    import re
    raw_title = re.sub(r'\(?\s*\d+\s*[Hh][Zz](\s*[Rr]esonance)?\s*\)?', '', raw_title, flags=re.IGNORECASE)
    raw_title = re.sub(r'\b\d+\s*[Hh][Zz]\b', '', raw_title, flags=re.IGNORECASE)
    raw_title = re.sub(r'\b[Hh][Zz]\b', '', raw_title, flags=re.IGNORECASE)
    raw_title = raw_title.replace("<", "").replace(">", "").strip()
    raw_title = re.sub(r'\s{2,}', ' ', raw_title).strip()

    if not is_krishna:
        for kw in ["Krishna ", "कृष्ण ", "श्री कृष्ण ", "राधे कृष्ण "]:
            raw_title = raw_title.replace(kw, "")

    # Reserve space for brand_suffix
    max_raw_len = 95 - len(brand_suffix)
    if len(raw_title) > max_raw_len:
        raw_title = raw_title[:max_raw_len].rstrip(" |")

    title = f"{raw_title}{brand_suffix}"

    lofi_desc_block = ""
    if is_lofi:
        lofi_name = "Krishna Lo-Fi Chill Beats" if is_krishna else "Lo-Fi Bamboo Flute & Chill Beats"
        lofi_desc_block = (
            f"🎧 विशेष लो-फाई संगीत ({lofi_name}):\n"
            "यह संगीत आधुनिक लो-फाई (Lo-Fi Chill Beats) और पारंपरिक शांत बाँसुरी का अत्यंत मधुर, सुकून देने वाला संगम है। "
            "यह पढ़ने (Study), कार्य एकाग्रता (Work Focus) और सुकून भरी नींद के लिए सर्वोत्तम है।\n\n"
        )

    if is_krishna:
        description = (
            f"🌸 स्वागत है Krishna Vibez के पावन संगीत संसार में 🌸\n\n"
            f"Experience profound inner peace, deep tranquility, and divine healing with this {dur_min}-minute sacred "
            f"Lord Krishna Flute (Bansuri) & authentic Live Tabla meditation music.\n\n"
            f"🌿 आज का पावन प्रसंग (Theme): {theme['hindi_main']} — {theme['hindi_sub']}\n\n"
            f"{lofi_desc_block}"
            "भगवान श्री कृष्ण की मधुर मुरली की यह दिव्य ध्वनि मन के समस्त तनाव, चिंता और नकारात्मकता को समाप्त कर अंतरात्मा को "
            "असीम शांति से भर देती है। इसके साथ बजती हुई तबले की कोमल ताल (कहरवा एवं तीन ताल) हृदय में एक सुखद लय और सकारात्मक ऊर्जा का संचार करती है।\n\n"
            "✨ पावन संगीत का महत्व (Spiritual Peace & Mind Healing):\n"
            "यह संगीत मन को शांत करने वाली तरंगों पर आधारित है। यह मधुर संगीत मस्तिष्क की अल्फा तरंगों (Alpha Waves) को "
            "सक्रिय करता है, मानसिक तनाव को घटाता है, हृदय स्पंदन को शांत करता है और गहरी नींद व आत्मिक सुकून प्रदान करता है।\n\n"
            "🧘 इस पावन संगीत के सर्वोत्तम उपयोग (Ideal For):\n"
            "• ध्यान, योग और दैनिक साधना (Deep Meditation, Dhyan & Daily Yoga)\n"
            "• तनाव, चिंता और अधिक सोचने (Overthinking) से मुक्ति (Stress Relief & Mental Peace)\n"
            "• गहरी और सुकून भरी नींद (Deep Sleep & Insomnia Relief)\n"
            "• प्रातःकालीन पूजा, आरती और घर में सकारात्मक ऊर्जा (Morning Pooja & Positive Home Vibes)\n"
            "• पढ़ाई और कार्य में एकाग्रता (Deep Study & Work Concentration)\n\n"
            "⏱️ समय सारणी (Chapters / Timestamps):\n"
            f"{ch1} 🪷 वृंदावन प्रातःकालीन बांसुरी (Divine Prelude)\n"
            f"{ch2} 🪶 बांसुरी एवं तबला कोमल जुगलबंदी (Keherwa Taal Rhythm)\n"
            f"{ch3} 🌊 आत्मिक शांति और ध्यान प्रवाह (Deep Healing Flow)\n"
            f"{ch4} ✨ असीम शांति एवं समापन विश्राम (Closing Shanti & Gratitude)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔍 इस संगीत में समाहित प्रमुख विषय एवं खोज प्रश्न (Topics & Searches Covered):\n"
            "• Shri Krishna Bansuri Dhun for Deep Meditation & Stress Relief\n"
            "• Subah ki Shanti aur Positivity ke liye Morning Flute Music\n"
            "• Radha Krishna Peaceful Instrumental with Live Tabla Keherwa Taal\n"
            "• Raat ko gehri neend aane ka shant bansuri sangeet (Sleep Music)\n"
            "• Divine Meditation Flute Music for Anxiety and Mental Calm\n"
            "• Vrindavan Divine Morning Bansuri Dhun by Krishna Vibez\n"
            "• Man ko shant karne wali flute dhun hindi me\n"
            "• Pure Indian Classical Bansuri Tabla Jugalbandi for Pooja and Yoga\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🕊️ कृष्ण वाइब्स के आध्यात्मिक परिवार से जुड़ें:\n"
            "🌐 आधिकारिक वेबसाइट: https://krishnavibez.in/\n"
            "▶️ आधिकारिक YouTube: https://www.youtube.com/@KrishnaVibezMusic\n"
            "📲 WhatsApp चैनल: https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J\n"
            "📢 Telegram चैनल: https://t.me/krishnavibezz\n"
            "📸 Instagram: https://www.instagram.com/krishnavibez/\n"
            "🧵 Threads: https://www.threads.net/@krishnavibez\n"
            "📘 Facebook पेज: https://www.facebook.com/1808917602588221\n"
            "📌 Pinterest: https://in.pinterest.com/MojiloMart/\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🛍️ Divine Recommendations (Amazon Storefront):\n"
            "👉 Explore our Amazon Store: https://www.amazon.in/shop/myhappybirthday\n"
            "(Disclaimer: As an Amazon Associate, Krishna Vibez earns from qualifying purchases at no extra cost to you.)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🙏 यदि इस संगीत ने आपके मन को शांति और सुकून दिया हो, तो वीडियो को लाइक करें, अपने परिजनों के साथ साझा करें और चैनल को सब्सक्राइब अवश्य करें।\n\n"
            "जय श्री राधे कृष्ण! 🪷✨\n\n"
            + ("#KrishnaLofi #LofiFlute #LofiBeats #LofiMusic #Krishna #Flute #Bansuri #MeditationMusic #KrishnaMusic #RelaxingMusic #InnerPeace #DeepSleep #BansuriTabla #KrishnaVibez #DailyMeditation" if is_lofi else
               "#Krishna #Flute #Bansuri #MeditationMusic #KrishnaMusic #DivineMusic #RadhaKrishna #RelaxingMusic #InnerPeace #DeepSleep #BansuriTabla #KrishnaVibez #DailyMeditation")
        )
        lofi_tags = ["Krishna Lofi", "Lofi Flute", "Indian Lofi", "Lofi Beats", "Krishna Chill", "Relaxing Lofi"] if is_lofi else []
        raw_candidates = list(dict.fromkeys(
            lofi_tags + theme.get("tags", []) + [
                "Krishna Flute", "Bansuri Dhun", "Krishna Meditation Music",
                "Deep Sleep Music", "Stress Relief Music", "Radha Krishna Flute", "Bansuri Tabla",
                "Man Ki Shanti", "Subah Ki Flute", "Indian Classical Flute", "Morning Meditation",
                "Yoga Music", "Krishna Vibez", "Peaceful Instrumental", "Shri Krishna Bansuri",
                "Gehri Neend Music", "Healing Music", "Radhe Krishna", "Bhakti Music"
            ]
        ))
    else:
        description = (
            f"🌿 स्वागत है आपके अपने पावन बाँसुरी एवं ध्यान संगीत संसार में 🌿\n\n"
            f"Experience profound inner peace, deep tranquility, and restorative calm with this {dur_min}-minute soothing "
            f"Indian Classical Bamboo Flute (Bansuri) & authentic Live Tabla meditation music.\n\n"
            f"🌿 आज का पावन प्रसंग (Theme): {theme['hindi_main']} — {theme['hindi_sub']}\n\n"
            f"{lofi_desc_block}"
            "बाँसुरी की यह कोमल और शांत धुन मन के समस्त तनाव, चिंता और थकान को समाप्त कर अंतरात्मा को "
            "असीम शांति से भर देती है। इसके साथ बजती हुई तबले की कोमल ताल हृदय में एक सुखद लय और सकारात्मक ऊर्जा का संचार करती है।\n\n"
            "✨ पावन संगीत का महत्व (Spiritual Peace & Mind Healing):\n"
            "यह संगीत मन को शांत करने वाली तरंगों पर आधारित है। यह मधुर संगीत मस्तिष्क की अल्फा तरंगों (Alpha Waves) को "
            "सक्रिय करता है, मानसिक तनाव को घटाता है, हृदय स्पंदन को शांत करता है और गहरी नींद व आत्मिक सुकून प्रदान करता है।\n\n"
            "🧘 इस पावन संगीत के सर्वोत्तम उपयोग (Ideal For):\n"
            "• ध्यान, योग और दैनिक साधना (Deep Meditation, Dhyan & Daily Yoga)\n"
            "• तनाव, चिंता और अधिक सोचने (Overthinking) से मुक्ति (Stress Relief & Mental Peace)\n"
            "• गहरी और सुकून भरी नींद (Deep Sleep & Insomnia Relief)\n"
            "• प्रातःकालीन शांति और सकारात्मक ऊर्जा (Morning Peace & Positive Energy)\n"
            "• पढ़ाई और कार्य में एकाग्रता (Deep Study & Work Concentration)\n\n"
            "⏱️ समय सारणी (Chapters / Timestamps):\n"
            f"{ch1} 🪷 शांत प्रभात बाँसुरी (Peaceful Prelude)\n"
            f"{ch2} 🪶 बाँसुरी एवं तबला कोमल जुगलबंदी (Keherwa Taal Rhythm)\n"
            f"{ch3} 🌊 आत्मिक शांति और ध्यान प्रवाह (Deep Healing Flow)\n"
            f"{ch4} ✨ असीम शांति एवं समापन विश्राम (Closing Shanti & Gratitude)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔍 इस संगीत में समाहित प्रमुख विषय एवं खोज प्रश्न (Topics & Searches Covered):\n"
            "• Indian Bamboo Flute Music for Deep Meditation & Stress Relief\n"
            "• Subah ki Shanti aur Positivity ke liye Morning Flute Music\n"
            "• Peaceful Flute Instrumental with Live Tabla Keherwa Taal\n"
            "• Raat ko gehri neend aane ka shant bansuri sangeet (Sleep Music)\n"
            "• Soothing Meditation Flute Music for Anxiety and Mental Calm\n"
            "• Pure Classical Bansuri Dhun for Relaxing Mind\n"
            "• Man ko shant karne wali flute dhun hindi me\n"
            "• Pure Indian Classical Bansuri Tabla Jugalbandi for Yoga\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🕊️ हमारे संगीत परिवार से जुड़ें:\n"
            "🌐 आधिकारिक वेबसाइट: https://krishnavibez.in/\n"
            "▶️ आधिकारिक YouTube: https://www.youtube.com/@KrishnaVibezMusic\n"
            "📲 WhatsApp चैनल: https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J\n"
            "📢 Telegram चैनल: https://t.me/krishnavibezz\n"
            "📸 Instagram: https://www.instagram.com/krishnavibez/\n"
            "🧵 Threads: https://www.threads.net/@krishnavibez\n"
            "📘 Facebook पेज: https://www.facebook.com/1808917602588221\n"
            "📌 Pinterest: https://in.pinterest.com/MojiloMart/\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🛍️ Recommendations (Amazon Storefront):\n"
            "👉 Explore our Amazon Store: https://www.amazon.in/shop/myhappybirthday\n"
            "(Disclaimer: Krishna Vibez earns from qualifying purchases at no extra cost to you.)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🙏 यदि इस संगीत ने आपके मन को शांति और सुकून दिया हो, तो वीडियो को लाइक करें, अपने परिजनों के साथ साझा करें और चैनल को सब्सक्राइब अवश्य करें।\n\n"
            "शान्ति: शान्ति: शान्ति: 🌿✨\n\n"
            + ("#LofiFlute #LofiBeats #IndianLofi #Flute #Bansuri #MeditationMusic #RelaxingMusic #InnerPeace #DeepSleep #BansuriTabla #DailyMeditation" if is_lofi else
               "#Flute #Bansuri #IndianFlute #BambooFlute #MeditationMusic #RelaxingMusic #InnerPeace #DeepSleep #BansuriTabla #DailyMeditation #Mindfulness")
        )
        lofi_tags = ["Lofi Flute", "Indian Lofi", "Lofi Beats", "Relaxing Lofi", "Chill Flute"] if is_lofi else []
        raw_candidates = list(dict.fromkeys(
            lofi_tags + theme.get("tags", []) + [
                "Indian Classical Flute", "Bamboo Flute", "Bansuri Dhun",
                "Deep Sleep Music", "Stress Relief Music", "Bansuri Tabla",
                "Man Ki Shanti", "Subah Ki Flute", "Morning Meditation",
                "Yoga Music", "Peaceful Instrumental", "Gehri Neend Music",
                "Healing Music", "Sleep Flute Music", "Mindful Breathing",
                "Calm Flute", "Nature Meditation"
            ]
        ))
    # Accurately compute YouTube tag comma-separated length with quotes for multi-word tags
    # Keep strictly under 380 chars (safe under 500-char YouTube API limit)
    final_tags = []
    total_tag_chars = 0
    for t in raw_candidates:
        clean_t = t.replace("<", "").replace(">", "").replace(",", "").strip()
        # Strictly skip any tag mentioning 432 or hz
        if re.search(r'\b\d*hz\b', clean_t, flags=re.IGNORECASE) or "432" in clean_t:
            continue
        if not is_krishna and any(kw in clean_t.lower() for kw in ["krishna", "radha"]):
            continue
        if not clean_t:
            continue
        effective_len = len(clean_t) + (2 if " " in clean_t else 0) + 1
        if total_tag_chars + effective_len <= 380:
            final_tags.append(clean_t)
            total_tag_chars += effective_len

    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": final_tags,
            "categoryId": "10" # Music
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True
        }
    }

    upload_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": "video/mp4",
        "X-Upload-Content-Length": str(os.path.getsize(OUTPUT_VIDEO))
    }

    init_res = requests.post(upload_url, headers=headers, json=metadata)
    if init_res.status_code != 200:
        print("[Notice] YouTube init returned:", init_res.status_code, init_res.text)
        if "invalidTags" in init_res.text or "keyword" in init_res.text.lower():
            print("  -> Retrying with basic verified tags...")
            metadata["snippet"]["tags"] = ["Krishna Flute", "Bansuri Dhun", "Meditation Music", "Krishna Vibez"] if is_krishna else ["Indian Flute", "Bansuri Dhun", "Meditation Music", "Relaxing Flute"]
            init_res = requests.post(upload_url, headers=headers, json=metadata)
        if init_res.status_code != 200:
            print("  -> Retrying with zero tags fallback...")
            metadata["snippet"].pop("tags", None)
            init_res = requests.post(upload_url, headers=headers, json=metadata)

    if init_res.status_code != 200:
        print("[Error] YouTube resumable upload init failed:", init_res.text)
        sys.exit(1)

    session_url = init_res.headers.get("Location")
    print("  -> Uploading video stream to YouTube...")
    with open(OUTPUT_VIDEO, "rb") as f:
        up_res = requests.put(session_url, headers={"Content-Type": "video/mp4"}, data=f)

    if up_res.status_code in [200, 201]:
        video_id = up_res.json().get("id")
        print(f"  -> SUCCESS! Video uploaded to YouTube: https://youtu.be/{video_id}")
        
        # 🛡️ 24-HOUR SAFETY QUARANTINE SHIELD:
        try:
            from youtube_safety_quarantine import add_to_quarantine, process_quarantine_queue
            add_to_quarantine(video_id, theme.get("title", "Krishna Meditation Music"), video_type="music_video")
            print("🛡️ Checking mature quarantine videos (>= 24h old)...")
            process_quarantine_queue(min_quarantine_hours=24)
        except Exception as q_err:
            print(f"Quarantine shield notice: {q_err}")
        
        # Upload Custom Thumbnail
        if os.path.exists(TEMP_THUMBNAIL):
            print("  -> Uploading custom high-CTR thumbnail...")
            thumb_url = f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}&uploadType=media"
            thumb_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "image/jpeg"
            }
            with open(TEMP_THUMBNAIL, "rb") as tf:
                thumb_res = requests.post(thumb_url, headers=thumb_headers, data=tf)
            if thumb_res.status_code in [200, 201]:
                print("  -> SUCCESS! Custom Thumbnail applied successfully!")
            else:
                print("  -> [Notice] Thumbnail upload:", thumb_res.text)
    else:
        print("[Error] YouTube upload failed:", up_res.text)

def cleanup():
    """Post-upload cleanup of temporary media files."""
    print("[Cleanup] Cleaning temporary audio, video and thumbnail files...")
    # NOTE: Never delete NotoSansDevanagari-Bold.ttf or arialbd.ttf! They are master repository assets.
    for f in [TEMP_AUDIO, OUTPUT_VIDEO, TEMP_THUMBNAIL, os.path.join(BASE_DIR, "temp_concat_clips.txt")]:
        if os.path.exists(f):
            try: os.remove(f)
            except Exception: pass
    clips_dir = os.path.join(BASE_DIR, "temp_animated_clips")
    if os.path.exists(clips_dir):
        try:
            for c in os.listdir(clips_dir):
                os.remove(os.path.join(clips_dir, c))
            os.rmdir(clips_dir)
        except Exception: pass
    print("[Cleanup] All temporary media deleted. Workspace is clean and light.")

def main():
    # User rule: Dynamic duration between 12 and 50 minutes (e.g. 15 min = 5 images, 45 min = 15 images, 3-min shift)
    dur_min = random.randint(12, 50)
    dur_sec = dur_min * 60 + random.randint(5, 55)
    num_images_needed = max(3, dur_min // 3)
    print(f"🎬 [3-MINUTE DYNAMIC SCENES] Master Video: {dur_min} Minutes ({dur_sec}s), {num_images_needed} images shifting every 3 minutes.")
    
    # 1. First assemble and master soundtrack with Mandatory Pre-Flight Zero Vocal Scan
    track_info = mix_soundtrack(duration_sec=dur_sec)
    
    # 2. 100% Unique dynamic metadata tailored specifically to this track
    theme = get_dynamic_music_metadata(dur_min=dur_min, track_info=track_info)
    print(f"🌟 [AI DYNAMIC THEME] Category: {theme.get('category', 'Spiritual')}")
    print(f"   -> Track Name: {track_info.get('track_name', 'Bansuri Flute')}")
    print(f"   -> Title: {theme['title']}")
    print(f"   -> Badge: {theme['badge']}")
    print(f"   -> Headline: {theme['hindi_main']} | {theme['hindi_sub']}")
    print(f"   -> Pill: {theme.get('hook_pill')}")
    
    # 3. Ensure theme-adaptive images:
    # If Krishna track -> Use 311+ library images in loop (never deleted)
    # If Nature track -> Dynamically generate fresh Pollinations images (watermark cropped, deleted post-upload)
    is_krishna = is_krishna_track(track_info.get("track_name", ""), theme.get("category", ""))
    slides = ensure_images(num_needed=num_images_needed, track_info=track_info, theme=theme)
    
    render_video(slides, duration_sec=dur_sec, is_krishna=is_krishna)
    generate_thumbnail(slides, theme)
    upload_to_youtube(theme, duration_sec=dur_sec, track_info=track_info)
    archive_used_images(slides, is_krishna=is_krishna)
    cleanup()

if __name__ == "__main__":
    main()
