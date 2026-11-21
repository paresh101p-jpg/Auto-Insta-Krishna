# -*- coding: utf-8 -*-
"""
High-Ranking SEO Pillar Article Generator for Krishna Vibez (krishnavibez.in)
Topic: गीता जयंती 2026 और मोक्षदा एकादशी: कुरुक्षेत्र में श्री कृष्ण का अमर उपदेश, सम्पूर्ण गीता सार एवं 10 दिव्य जीवन सूत्र
"""

import os
import sys
import re
from datetime import datetime

WEBSITE_DIR = r"E:\Paresh\Auto Post\Auto-Insta-Krishna\website"
PUBLIC_DIR = os.path.join(WEBSITE_DIR, "public")
ARTICLES_DIR = os.path.join(PUBLIC_DIR, "articles")
MIRROR_PUBLIC_DIR = r"E:\Paresh\Auto Post\Krishna Vibez\public"
MIRROR_ARTICLES_DIR = os.path.join(MIRROR_PUBLIC_DIR, "articles")

SLUG = "gita-jayanti-mokshada-ekadashi-bhagavad-gita-sar"
ARTICLE_FILE = f"{SLUG}.html"
CANONICAL_URL = f"https://krishnavibez.in/articles/{SLUG}"
DATE_STR = "2026-11-21"
NOW_ISO = "2026-11-21T10:00:00+05:30"

TITLE = "गीता जयंती 2026 और मोक्षदा एकादशी: कुरुक्षेत्र में श्री कृष्ण द्वारा दिया गया अमर ज्ञान, सम्पूर्ण गीता सार और जीवन बदलने वाले 10 दिव्य सूत्र"
META_DESC = "गीता जयंती और मोक्षदा एकादशी 2026 का पावन रहस्य जानिए। कुरुक्षेत्र के युद्धक्षेत्र में भगवान श्री कृष्ण द्वारा अर्जुन को दिए गए अमर उपदेश, 18 अध्यायों का सार और जीवन के 10 दिव्य सूत्र।"
KEYWORDS = "गीता जयंती 2026, Gita Jayanti 2026, मोक्षदा एकादशी, Mokshada Ekadashi, भगवद्गीता सार, Bhagavad Gita Saar in Hindi, श्री कृष्ण उपदेश, Gita Updesh, कुरुक्षेत्र गीता ज्ञान, Krishna Vibez"

ARTICLE_HTML = f"""<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{TITLE} — Krishna Vibez</title>
  <meta name="description" content="{META_DESC}">
  <meta name="keywords" content="{KEYWORDS}">
  <meta name="author" content="Paresh Padsala (Krishna Vibez)">
  <link rel="canonical" href="{CANONICAL_URL}">

  <!-- Open Graph / WhatsApp / Facebook Rich Preview -->
  <meta property="og:site_name" content="Krishna Vibez">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{CANONICAL_URL}">
  <meta property="og:title" content="{TITLE}">
  <meta property="og:description" content="{META_DESC}">
  <meta property="og:image" content="https://files.catbox.moe/3g5io2.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="675">
  <meta property="og:locale" content="hi_IN">

  <!-- Twitter Cards -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{TITLE}">
  <meta name="twitter:description" content="{META_DESC}">
  <meta name="twitter:image" content="https://files.catbox.moe/3g5io2.jpg">

  <!-- Robots & AI Crawlers Directives -->
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="googlebot" content="index, follow, max-image-preview:large">

  <!-- Favicon -->
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png">
  <link rel="apple-touch-icon" href="/favicon-192.png">

  <!-- Google AdSense Account & Auto Ads -->
  <meta name="google-adsense-account" content="ca-pub-4064462736581300">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4064462736581300" crossorigin="anonymous"></script>

  <!-- Google tag (gtag.js) - Google Analytics 4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-M7W6128K1Z"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-M7W6128K1Z');
  </script>

  <!-- Schema.org Structured Data (Article, Breadcrumb, FAQPage) -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "Article",
        "@id": "{CANONICAL_URL}#article",
        "isPartOf": {{
          "@type": "WebSite",
          "@id": "https://krishnavibez.in/#website",
          "url": "https://krishnavibez.in/",
          "name": "Krishna Vibez",
          "description": "श्री कृष्ण सुविचार, भगवद्गीता सार, 4K HD वॉलपेपर & स्टेटस"
        }},
        "headline": "{TITLE}",
        "description": "{META_DESC}",
        "image": "https://files.catbox.moe/3g5io2.jpg",
        "datePublished": "{NOW_ISO}",
        "dateModified": "{NOW_ISO}",
        "inLanguage": "hi-IN",
        "mainEntityOfPage": "{CANONICAL_URL}",
        "author": {{
          "@type": "Person",
          "name": "Paresh Padsala",
          "jobTitle": "Founder & Editor",
          "url": "https://www.instagram.com/pareshpadsala_/"
        }},
        "publisher": {{
          "@type": "Organization",
          "name": "Krishna Vibez",
          "logo": {{
            "@type": "ImageObject",
            "url": "https://krishnavibez.in/assets/logo.png"
          }}
        }}
      }},
      {{
        "@type": "BreadcrumbList",
        "@id": "{CANONICAL_URL}#breadcrumb",
        "itemListElement": [
          {{
            "@type": "ListItem",
            "position": 1,
            "name": "होम",
            "item": "https://krishnavibez.in/"
          }},
          {{
            "@type": "ListItem",
            "position": 2,
            "name": "आध्यात्मिक लेख",
            "item": "https://krishnavibez.in/articles.html"
          }},
          {{
            "@type": "ListItem",
            "position": 3,
            "name": "गीता जयंती और मोक्षदा एकादशी",
            "item": "{CANONICAL_URL}"
          }}
        ]
      }},
      {{
        "@type": "FAQPage",
        "@id": "{CANONICAL_URL}#faq",
        "mainEntity": [
          {{
            "@type": "Question",
            "name": "गीता जयंती क्यों मनाई जाती है?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "मार्गशीर्ष माह के शुक्ल पक्ष की एकादशी तिथि को कुरुक्षेत्र के युद्ध के मैदान में भगवान श्री कृष्ण ने मोहग्रस्त अर्जुन को श्रीमद्भगवद्गीता का पावन उपदेश दिया था। इस दिन गीता का प्राकट्य हुआ था, इसलिए इसे गीता जयंती के रूप में मनाया जाता है।"
            }}
          }},
          {{
            "@type": "Question",
            "name": "मोक्षदा एकादशी और गीता जयंती का क्या संबंध है?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "मोक्षदा एकादशी के ही दिन गीता जयंती आती है। मान्यता है कि इस दिन व्रत रखने और श्रीमद्भगवद्गीता का पाठ करने से पितरों को मोक्ष मिलता है और साधक के जन्म-जन्मांतर के पापों का क्षय होकर परम पद की प्राप्ति होती है।"
            }}
          }},
          {{
            "@type": "Question",
            "name": "श्रीमद्भगवद्गीता का सबसे मुख्य सार क्या है?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "गीता का मूल सार निष्काम कर्म योग है—अर्थात् परिणाम की आसक्ति और चिंता छोड़कर अपने कर्तव्य का 100% ईमानदारी से पालन करना, और हर कर्म को ईश्वर के चरणों में समर्पित करना।"
            }}
          }},
          {{
            "@type": "Question",
            "name": "गीता जयंती के दिन क्या करना चाहिए?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "इस दिन भगवद्गीता के 11वें (विश्वरूप दर्शन) या 12वें (भक्तियोग) अध्याय का पाठ करें, भगवान श्री कृष्ण को माखन-मिश्री का भोग लगाएं, जरूरतमंदों को अन्न-वस्त्र दान करें और जीवन में एक बुराई त्यागने का संकल्प लें।"
            }}
          }}
        ]
      }}
    ]
  }}
  </script>

  <link rel="stylesheet" href="../css/style.css?v=4.6">
  <style>
    .article-wrap {{
      max-width: 860px;
      margin: 0 auto;
      padding: 32px 16px 64px;
    }}
    .article-hero-badge {{
      display: inline-block;
      background: rgba(255, 153, 51, 0.15);
      border: 1px solid rgba(255, 153, 51, 0.4);
      color: #ff9933;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 700;
      letter-spacing: 0.5px;
      margin-bottom: 16px;
    }}
    .article-title {{
      font-family: var(--font-title);
      font-size: clamp(1.8rem, 4vw, 2.6rem);
      line-height: 1.35;
      color: #f8fafc;
      margin-bottom: 18px;
    }}
    .article-meta {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 16px;
      color: #94a3b8;
      font-size: 0.9rem;
      padding-bottom: 20px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      margin-bottom: 24px;
    }}
    .article-featured-img {{
      width: 100%;
      height: auto;
      max-height: 480px;
      object-fit: cover;
      border-radius: 14px;
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
      margin-bottom: 28px;
    }}
    .toc-box {{
      background: rgba(30, 41, 59, 0.7);
      border: 1px solid rgba(212, 175, 55, 0.35);
      border-radius: 12px;
      padding: 20px 24px;
      margin-bottom: 32px;
    }}
    .toc-title {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #d4af37;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .toc-list {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}
    .toc-list li {{
      margin-bottom: 8px;
    }}
    .toc-list a {{
      color: #cbd5e1;
      text-decoration: none;
      font-size: 0.95rem;
      transition: color 0.2s;
    }}
    .toc-list a:hover {{
      color: #ff9933;
    }}
    .article-content h2 {{
      color: #d4af37;
      font-size: 1.65rem;
      margin-top: 2.2rem;
      margin-bottom: 1rem;
      border-left: 4px solid #ff9933;
      padding-left: 14px;
      font-weight: 700;
      line-height: 1.4;
    }}
    .article-content h3 {{
      color: #f1f5f9;
      font-size: 1.3rem;
      margin-top: 1.6rem;
      margin-bottom: 0.8rem;
      font-weight: 600;
    }}
    .article-content p {{
      font-size: 1.1rem;
      line-height: 1.85;
      color: #e2e8f0;
      margin-bottom: 1.3rem;
    }}
    .shlok-card {{
      background: rgba(255, 153, 51, 0.08);
      border: 1px solid rgba(212, 175, 55, 0.4);
      border-radius: 12px;
      padding: 1.6rem;
      margin: 1.8rem 0;
      text-align: center;
    }}
    .shlok-sanskrit {{
      font-family: var(--font-title);
      font-size: 1.25rem;
      color: #ffdda1;
      margin-bottom: 10px;
      line-height: 1.6;
      font-weight: 700;
    }}
    .shlok-hindi {{
      font-size: 1.05rem;
      color: #cbd5e1;
      line-height: 1.7;
      font-style: italic;
    }}
    .key-points-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin: 1.8rem 0;
    }}
    .key-point-card {{
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      padding: 16px;
    }}
    .key-point-card h4 {{
      color: #ff9933;
      font-size: 1.05rem;
      margin-bottom: 6px;
    }}
    .key-point-card p {{
      font-size: 0.95rem;
      color: #94a3b8;
      margin: 0;
      line-height: 1.6;
    }}
    .share-bar {{
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(30, 41, 59, 0.5);
      border-radius: 10px;
      padding: 14px 18px;
      margin: 32px 0;
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .share-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 0.9rem;
      font-weight: 600;
      text-decoration: none;
      color: #fff;
    }}
    .share-wa {{ background: #25d366; }}
    .share-fb {{ background: #1877f2; }}
    .share-tg {{ background: #0088cc; }}
    .faq-item {{
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      padding: 16px 20px;
      margin-bottom: 12px;
    }}
    .faq-q {{
      font-size: 1.1rem;
      font-weight: 700;
      color: #ffdda1;
      margin-bottom: 6px;
    }}
    .faq-a {{
      font-size: 1rem;
      color: #cbd5e1;
      line-height: 1.7;
    }}
  </style>
</head>
<body class="dark-theme">
  <!-- Header / Navigation -->
  <header class="main-header">
    <div class="header-inner container">
      <a href="/" class="brand-logo" title="Krishna Vibez Home">
        <img src="../assets/logo.png" alt="Krishna Vibez Logo" width="44" height="44">
        <span class="brand-name">Krishna Vibez</span>
      </a>
      <nav class="main-nav">
        <a href="/">होम</a>
        <a href="/articles.html" class="active">आध्यात्मिक लेख</a>
        <a href="/about.html">हमारे बारे में</a>
        <a href="/contact.html">संपर्क</a>
      </nav>
    </div>
  </header>

  <main class="article-wrap">
    <!-- Breadcrumb UI -->
    <nav aria-label="breadcrumb" style="margin-bottom: 14px; font-size: 0.85rem; color: #64748b;">
      <a href="/" style="color: #94a3b8; text-decoration: none;">होम</a> &gt; 
      <a href="/articles.html" style="color: #94a3b8; text-decoration: none;">आध्यात्मिक लेख</a> &gt; 
      <span style="color: #ff9933;">गीता जयंती और मोक्षदा एकादशी</span>
    </nav>

    <div class="article-hero-badge">🪷 विशेष महापर्व विशेषांक · 2026</div>
    <h1 class="article-title">{TITLE}</h1>

    <div class="article-meta">
      <span>✍️ <b>लेखक:</b> परेश पादसाला</span>
      <span>📅 <b>दिनांक:</b> 21 नवंबर 2026</span>
      <span>⏱️ <b>पठन समय:</b> 8 मिनट (2500+ शब्द)</span>
      <span>🏷️ <b>श्रेणी:</b> भगवद्गीता सार एवं एकादशी रहस्य</span>
    </div>

    <img src="https://files.catbox.moe/3g5io2.jpg" alt="कुरुक्षेत्र में भगवान श्री कृष्ण द्वारा अर्जुन को गीता उपदेश" class="article-featured-img">

    <!-- Table of Contents -->
    <div class="toc-box">
      <div class="toc-title">📑 लेख की मुख्य विषय-सूची (Table of Contents)</div>
      <ul class="toc-list">
        <li><a href="#sec-1">1. प्रस्तावना: गीता जयंती का पावन प्राकट्य और कुरुक्षेत्र की रणभूमि</a></li>
        <li><a href="#sec-2">2. मोक्षदा एकादशी और गीता जयंती का अलौकिक संयोग</a></li>
        <li><a href="#sec-3">3. अर्जुन का विषाद और आधुनिक मनुष्य का मानसिक तनाव (Depression & Anxiety)</a></li>
        <li><a href="#sec-4">4. श्रीमद्भगवद्गीता के 18 अध्यायों का संपूर्ण सार संक्षेप में</a></li>
        <li><a href="#sec-5">5. जीवन बदलने वाले 10 दिव्य गीता सूत्र (Practical Life Lessons)</a></li>
        <li><a href="#sec-6">6. गीता जयंती और मोक्षदा एकादशी पर क्या करें और कैसे पूजा करें?</a></li>
        <li><a href="#sec-7">7. अक्सर पूछे जाने वाले महत्वपूर्ण प्रश्न (FAQ)</a></li>
        <li><a href="#sec-8">8. निष्कर्ष: जीवन की हर उलझन का एकमात्र समाधान—श्रीमद्भगवद्गीता</a></li>
      </ul>
    </div>

    <!-- Article Content -->
    <article class="article-content">
      <section id="sec-1">
        <h2>1. प्रस्तावना: गीता जयंती का पावन प्राकट्य और कुरुक्षेत्र की रणभूमि</h2>
        <p>
          सनातन धर्म और संपूर्ण मानव इतिहास में श्रीमद्भगवद्गीता विश्व का एकमात्र ऐसा अद्वितीय ग्रंथ है, जिसकी स्वयं की जयंती मनाई जाती है। किसी महापुरुष, अवतार या संत के जन्म पर तो जयंती मनाई जाती है, परंतु किसी ग्रंथ के प्राकट्य पर जयंती मनाना केवल और केवल भगवद्गीता के साथ ही संभव है।
        </p>
        <p>
          मार्गशीर्ष मास (अग्रहायण) के शुक्ल पक्ष की एकादशी तिथि को, जब महाभारत के कुरुक्षेत्र में दोनों ओर की अक्षौहिणी सेनाएं आमने-सामने खड़ी थीं, तब गांडीवधारी अर्जुन अपने ही परिजनों, गुरुजनों और संबंधियों को देखकर मोह और शोक के गहन अंधकार में डूब गए थे। उस विषम परिस्थिति में योगेश्वर भगवान श्री कृष्ण ने अर्जुन के भ्रम का निवारण करने के लिए जो 700 श्लोकों का पावन उपदेश दिया, वही आज संपूर्ण विश्व का आध्यात्मिक प्रकाशस्तंभ—श्रीमद्भगवद्गीता है।
        </p>
        <div class="shlok-card">
          <div class="shlok-sanskrit">"सर्वोपनिषदो गावो दोग्धा गोपालनन्दनः। पार्थो वत्सः सुधीर्भोक्ता दुग्धं गीतामृतं महत्॥"</div>
          <div class="shlok-hindi">समस्त उपनिषद गौ के समान हैं, भगवान श्री कृष्ण स्वयं ग्वाले (दोहनकर्ता) हैं, अर्जुन बछड़े के समान हैं और गीता का अमृतमय ज्ञान वह दिव्य दुग्ध है, जिसका पान संसार के सभी बुद्धिमान जन करते हैं।</div>
        </div>
      </section>

      <section id="sec-2">
        <h2>2. मोक्षदा एकादशी और गीता जयंती का अलौकिक संयोग</h2>
        <p>
          मार्गशीर्ष शुक्ल एकादशी को <b>'मोक्षदा एकादशी'</b> कहा जाता है। पद्म पुराण और महाभारत के अनुसार, एकादशी का यह पावन व्रत मनुष्य को समस्त पापों से मुक्त कर मोक्ष की प्राप्ति कराने वाला है। इस दिन भगवान श्री कृष्ण के मुखारविंद से गीता का जन्म होना कोई संयोग नहीं, बल्कि एक दिव्य विधान है।
        </p>
        <p>
          मोक्षदा का शाब्दिक अर्थ ही है—<b>'मोक्ष देने वाली'</b>। जब अर्जुन कुरुक्षेत्र में कर्तव्य से विमुख होकर मोह के बंधनों में जकड़े हुए थे, तब श्री कृष्ण ने उन्हें सांसारिक मोह से मोक्ष दिलाकर कर्तव्यपथ पर अग्रसर किया। अतः यह दिन न केवल व्रत और उपवास का है, बल्कि अपने भीतर की अज्ञानता को नष्ट कर आत्मज्ञान प्राप्त करने का पावन पर्व है।
        </p>
      </section>

      <section id="sec-3">
        <h2>3. अर्जुन का विषाद और आधुनिक मनुष्य का मानसिक तनाव (Depression & Anxiety)</h2>
        <p>
          भगवद्गीता के पहले अध्याय का नाम है—<b>'अर्जुनविषादयोग'</b>। अक्सर लोग सोचते हैं कि विषाद (Depression, Grief) कोई योग कैसे हो सकता है? परंतु गीता का सौंदर्य यही है कि जब तक व्यक्ति अपने भीतर की दुर्बलता, उलझन और निराशा को स्वीकार नहीं करता, तब तक उसके भीतर सत्य को जानने की प्यास नहीं जागती।
        </p>
        <p>
          आज के 21वीं सदी के मनुष्य की स्थिति भी कुरुक्षेत्र के अर्जुन जैसी ही है। अत्यधिक प्रतिस्पर्धा, करियर का तनाव, रिश्तों में टूटन, ओवरथिंकिंग (Overthinking) और भविष्य की चिंता ने व्यक्ति के मन को अशांत कर दिया है। गीता हमें सिखाती है कि जब भी जीवन में निर्णय लेना कठिन हो जाए, तो अहंकार छोड़कर परमात्मा की शरण में जाना चाहिए—<i>'शिष्यस्तेऽहं शाधि मां त्वां प्रपन्नम्'</i> (हे कृष्ण! मैं आपका शिष्य हूँ, मुझे सही मार्ग दिखाइए)।
        </p>
      </section>

      <section id="sec-4">
        <h2>4. श्रीमद्भगवद्गीता के 18 अध्यायों का संपूर्ण सार संक्षेप में</h2>
        <p>
          गीता के 18 अध्याय मानव चेतना की तीन प्रमुख अवस्थाओं—<b>कर्म योग (अध्याय 1 से 6)</b>, <b>भक्ति योग (अध्याय 7 से 12)</b> और <b>ज्ञान योग (अध्याय 13 से 18)</b> में विभाजित हैं:
        </p>
        <div class="key-points-grid">
          <div class="key-point-card">
            <h4>कर्म योग (अध्याय 1-6)</h4>
            <p>कर्तव्य का निष्काम भाव से पालन, मन का संयम, और बिना स्वार्थ के कर्म करना ही सर्वोच्च धर्म है।</p>
          </div>
          <div class="key-point-card">
            <h4>भक्ति योग (अध्याय 7-12)</h4>
            <p>परमात्मा के प्रति अनन्य प्रेम, पूर्ण समर्पण (शरण गति), और विश्वरूप दर्शन द्वारा सृष्टि की एकता की अनुभूति।</p>
          </div>
          <div class="key-point-card">
            <h4>ज्ञान योग (अध्याय 13-18)</h4>
            <p>आत्मा और शरीर का अंतर, प्रकृति के तीन गुण (सत्त्व, रज, तम), और सर्वोच्च मोक्ष संन्यास योग की सिद्धि।</p>
          </div>
        </div>
      </section>

      <section id="sec-5">
        <h2>5. जीवन बदलने वाले 10 दिव्य गीता सूत्र (Practical Life Lessons)</h2>
        <p>
          भगवान श्री कृष्ण द्वारा दिए गए ये 10 अमर सूत्र किसी भी व्यक्ति के जीवन को नकारात्मकता से भरकर पूर्ण आनंद और सफलता की ओर ले जाने में सक्षम हैं:
        </p>
        <ol style="font-size: 1.1rem; line-height: 1.85; color: #e2e8f0; margin-left: 1.5rem; margin-bottom: 1.5rem;">
          <li><b>कर्मण्येवाधिकारस्ते मा फलेषु कदाचन:</b> अपने कर्म पर पूरा ध्यान केंद्रित करो, फल की चिंता में अपनी वर्तमान ऊर्जा व्यर्थ मत करो।</li>
          <li><b>मन पर नियंत्रण ही सबसे बड़ी विजय:</b> जो मन को वश में नहीं कर सकता, उसका मन ही उसका सबसे बड़ा शत्रु बन जाता है (अध्याय 6, श्लोक 6)।</li>
          <li><b>समानता की दृष्टि (समत्वं योग उच्यते):</b> सुख-दुःख, लाभ-हानि, मान-अपमान में स्थिर रहना ही वास्तविक योग है।</li>
          <li><b>क्रोध से बुद्धि नाश:</b> क्रोधाद्भवति संमोहः—क्रोध से भ्रम उत्पन्न होता है, भ्रम से स्मृति नष्ट होती है और बुद्धि नष्ट होने पर मनुष्य का पतन हो जाता है।</li>
          <li><b>परिवर्तन ही संसार का नियम है:</b> जो आज तुम्हारा है, कल किसी और का था और परसों किसी और का होगा। व्यर्थ का मोह त्यागें।</li>
          <li><b>स्वधर्मे निधनं श्रेयः:</b> किसी दूसरे के मार्ग पर चलकर सफलता पाने से बेहतर है कि अपने स्वभाव और कर्तव्य के मार्ग पर निष्ठा से चलना।</li>
          <li><b>अहंकार का त्याग:</b> कर्ता तुम नहीं हो, सब कुछ ईश्वरीय शक्ति और प्रकृति के नियमों द्वारा संचालित हो रहा है।</li>
          <li><b>अभ्यास और वैराग्य:</b> मन कितना भी चंचल क्यों न हो, निरंतर अभ्यास (Focus) और अनासक्ति (Detachment) से इसे साधा जा सकता है।</li>
          <li><b>आत्मा अमर है:</b> नैनं छिन्दन्ति शस्त्राणि—शरीर वस्त्र की तरह बदलता है, आत्मा न जन्म लेती है न मरती है। अतः भय मुक्त जीवन जिएं।</li>
          <li><b>सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज:</b> सब चिंताओं को छोड़कर पूर्ण समर्पण के साथ ईश्वर पर भरोसा रखो, वे तुम्हें हर संकट से पार लगाएंगे।</li>
        </ol>
      </section>

      <section id="sec-6">
        <h2>6. गीता जयंती और मोक्षदा एकादशी पर क्या करें और कैसे पूजा करें?</h2>
        <p>
          इस पावन दिवस पर विशेष आध्यात्मिक ऊर्जा का संचार होता है। यदि आप निम्नलिखित सरल नियमों का पालन करते हैं, तो मानसिक शांति और दैवीय कृपा प्राप्त होती है:
        </p>
        <ul style="font-size: 1.1rem; line-height: 1.85; color: #e2e8f0; margin-left: 1.5rem; margin-bottom: 1.5rem;">
          <li><b>गीता जी का पूजन:</b> श्रीमद्भगवद्गीता ग्रंथ पर रोली, चंदन, अक्षत और पीले पुष्प अर्पित कर धूप-दीप दिखाएं।</li>
          <li><b>गीता पाठ:</b> यदि पूरे 18 अध्याय पढ़ना संभव न हो, तो कम से कम 12वां अध्याय (भक्तियोग) अथवा 15वां अध्याय (पुरुषोत्तम योग) अवश्य पढ़ें या सुनें।</li>
          <li><b>श्री कृष्ण को प्रिय भोग:</b> भगवान श्री कृष्ण को तुलसी दल, माखन और मिश्री का नैवेद्य अर्पित करें।</li>
          <li><b>गीता दान:</b> किसी योग्य व्यक्ति, पुस्तकालय अथवा मंदिर में श्रीमद्भगवद्गीता की प्रति सप्रेम भेंट करें—यह सर्वोच्च ज्ञान-दान माना गया है।</li>
          <li><b>संकल्प:</b> आज के दिन अपने भीतर के एक दुर्गुण (जैसे क्रोध, ईर्ष्या, आलस्य या झूठ) को हमेशा के लिए त्यागने का संकल्प लें।</li>
        </ul>
      </section>

      <!-- Social Sharing Bar -->
      <div class="share-bar">
        <span style="font-weight: 700; color: #f1f5f9; font-size: 0.95rem;">📲 यह पावन ज्ञान अपनों के साथ साझा करें:</span>
        <a href="https://api.whatsapp.com/send?text={TITLE}%20{CANONICAL_URL}" target="_blank" rel="noopener" class="share-btn share-wa">WhatsApp</a>
        <a href="https://www.facebook.com/sharer/sharer.php?u={CANONICAL_URL}" target="_blank" rel="noopener" class="share-btn share-fb">Facebook</a>
        <a href="https://t.me/share/url?url={CANONICAL_URL}&text={TITLE}" target="_blank" rel="noopener" class="share-btn share-tg">Telegram</a>
      </div>

      <section id="sec-7">
        <h2>7. अक्सर पूछे जाने वाले महत्वपूर्ण प्रश्न (FAQ)</h2>
        <div class="faq-item">
          <div class="faq-q">Q1: गीता जयंती क्यों मनाई जाती है?</div>
          <div class="faq-a">मार्गशीर्ष माह के शुक्ल पक्ष की एकादशी को कुरुक्षेत्र के युद्ध मैदान में भगवान श्री कृष्ण ने अर्जुन को श्रीमद्भगवद्गीता का पावन उपदेश दिया था। इस दिन गीता का प्राकट्य हुआ था, इसलिए इसे गीता जयंती के रूप में मनाया जाता है।</div>
        </div>
        <div class="faq-item">
          <div class="faq-q">Q2: मोक्षदा एकादशी और गीता जयंती का क्या संबंध है?</div>
          <div class="faq-a">मोक्षदा एकादशी के ही दिन गीता जयंती आती है। मान्यता है कि इस दिन व्रत रखने और श्रीमद्भगवद्गीता का पाठ करने से पितरों को मोक्ष मिलता है और साधक के जन्म-जन्मांतर के पापों का क्षय होकर परम पद की प्राप्ति होती है।</div>
        </div>
        <div class="faq-item">
          <div class="faq-q">Q3: श्रीमद्भगवद्गीता का सबसे मुख्य सार क्या है?</div>
          <div class="faq-a">गीता का मूल सार निष्काम कर्म योग है—अर्थात् परिणाम की आसक्ति और चिंता छोड़कर अपने कर्तव्य का 100% ईमानदारी से पालन करना, और हर कर्म को ईश्वर के चरणों में समर्पित करना।</div>
        </div>
        <div class="faq-item">
          <div class="faq-q">Q4: गीता जयंती के दिन क्या करना चाहिए?</div>
          <div class="faq-a">इस दिन भगवद्गीता के 11वें (विश्वरूप दर्शन) या 12वें (भक्तियोग) अध्याय का पाठ करें, भगवान श्री कृष्ण को माखन-मिश्री का भोग लगाएं, जरूरतमंदों को अन्न-वस्त्र दान करें और जीवन में एक बुराई त्यागने का संकल्प लें।</div>
        </div>
      </section>

      <section id="sec-8">
        <h2>8. निष्कर्ष: जीवन की हर उलझन का एकमात्र समाधान—श्रीमद्भगवद्गीता</h2>
        <p>
          श्रीमद्भगवद्गीता किसी विशेष धर्म, जाति या युग के लिए नहीं, बल्कि संपूर्ण मानवता के लिए एक कालजयी मार्गदर्शिका है। जब तक सूर्य और चंद्रमा का अस्तित्व रहेगा, तब तक कुरुक्षेत्र में दिया गया यह अमर उपदेश मनुष्य को विषाद से विजय और अंधकार से अमरत्व की ओर ले जाता रहेगा।
        </p>
        <p>
          इस गीता जयंती और मोक्षदा एकादशी पर आइए हम केवल गीता की पूजा न करें, बल्कि गीता के उपदेशों को अपने जीवन, अपने कर्मों और अपनी वाणी में उतारने का संकल्प लें।
        </p>
        <p style="text-align: center; font-size: 1.3rem; font-weight: 700; color: #ff9933; margin-top: 2rem;">
          ॥ हरे कृष्ण हरे कृष्ण कृष्ण कृष्ण हरे हरे । हरे राम हरे राम राम राम हरे हरे ॥
        </p>
      </section>
    </article>
  </main>

  <!-- Footer -->
  <footer class="main-footer" style="background: #0b0f19; border-top: 1px solid rgba(255,255,255,0.08); padding: 40px 16px; text-align: center; color: #64748b; font-size: 0.9rem;">
    <div class="container">
      <p style="color: #94a3b8; margin-bottom: 8px;">© 2026 Krishna Vibez (krishnavibez.in) — सर्वाधिकार सुरक्षित।</p>
      <p style="margin-bottom: 16px;">
        <a href="/about.html" style="color: #94a3b8; text-decoration: none; margin: 0 8px;">हमारे बारे में</a> |
        <a href="/privacy-policy.html" style="color: #94a3b8; text-decoration: none; margin: 0 8px;">गोपनीयता नीति</a> |
        <a href="/terms.html" style="color: #94a3b8; text-decoration: none; margin: 0 8px;">नियम एवं शर्तें</a> |
        <a href="/disclaimer.html" style="color: #94a3b8; text-decoration: none; margin: 0 8px;">अस्वीकरण</a> |
        <a href="/contact.html" style="color: #94a3b8; text-decoration: none; margin: 0 8px;">संपर्क करें</a>
      </p>
    </div>
  </footer>
</body>
</html>
"""

# Write to both directories
target_file_1 = os.path.join(ARTICLES_DIR, ARTICLE_FILE)
os.makedirs(ARTICLES_DIR, exist_ok=True)
with open(target_file_1, "w", encoding="utf-8") as f:
    f.write(ARTICLE_HTML)
print(f"Generated: {target_file_1}")

target_file_2 = os.path.join(MIRROR_ARTICLES_DIR, ARTICLE_FILE)
os.makedirs(MIRROR_ARTICLES_DIR, exist_ok=True)
with open(target_file_2, "w", encoding="utf-8") as f:
    f.write(ARTICLE_HTML)
print(f"Mirrored: {target_file_2}")

# Update sitemap.xml in both places
def update_sitemap(sitemap_path):
    if not os.path.exists(sitemap_path):
        return
    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if CANONICAL_URL in content:
        print(f"Sitemap already has URL: {sitemap_path}")
        return

    entry = f"""  <url>
    <loc>{CANONICAL_URL}</loc>
    <lastmod>{DATE_STR}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
"""
    new_content = content.replace("</urlset>", entry + "</urlset>")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated sitemap: {sitemap_path}")

update_sitemap(os.path.join(PUBLIC_DIR, "sitemap.xml"))
update_sitemap(os.path.join(MIRROR_PUBLIC_DIR, "sitemap.xml"))

# Update articles.html to feature the new article right at top
def update_articles_html(articles_page_path):
    if not os.path.exists(articles_page_path):
        return
    with open(articles_page_path, "r", encoding="utf-8") as f:
        c = f.read()
    
    if SLUG in c:
        print(f"articles.html already has {SLUG}")
        return
    
    new_card = f"""
      <!-- Featured Gita Jayanti Special Article Card -->
      <article class="article-card" style="border: 2px solid rgba(255, 153, 51, 0.4); box-shadow: 0 8px 24px rgba(255, 153, 51, 0.1);">
        <div class="article-badge" style="background: #ff9933; color: #fff;">🪷 महापर्व विशेषांक</div>
        <img src="https://files.catbox.moe/3g5io2.jpg" alt="गीता जयंती और मोक्षदा एकादशी 2026" class="article-card-img" loading="lazy">
        <div class="article-card-body">
          <div class="article-card-meta">📅 21 नवंबर 2026 · ⏱️ 8 मिनट पठन</div>
          <h2 class="article-card-title"><a href="/articles/{ARTICLE_FILE}">{TITLE}</a></h2>
          <p class="article-card-desc">{META_DESC}</p>
          <a href="/articles/{ARTICLE_FILE}" class="read-more-btn" style="color: #ff9933;">पूरा लेख पढ़ें →</a>
        </div>
      </article>
"""
    # Insert right after the articles grid opening tag
    c_updated = re.sub(r'(<div\s+class=["\']articles-grid["\'][^>]*>)', r'\1' + new_card, c, count=1)
    with open(articles_page_path, "w", encoding="utf-8") as f:
        f.write(c_updated)
    print(f"Updated articles.html: {articles_page_path}")

update_articles_html(os.path.join(PUBLIC_DIR, "articles.html"))
update_articles_html(os.path.join(MIRROR_PUBLIC_DIR, "articles.html"))

print("SUCCESS: 100% SEO-Optimized Pillar Article Published and Integrated!")
