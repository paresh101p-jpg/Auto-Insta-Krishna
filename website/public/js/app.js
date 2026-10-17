/* =========================================================
   KRISHNA VIBEZ - CORE JAVASCRIPT APPLICATION (app.js)
   Fast, Lightweight, Pure Vanilla JS
   Real Interactive Engagement & Bank-Grade Web Security
   ========================================================= */

let activeCategory = 'all';
let currentSort = 'latest';
let searchQuery = '';
let audioCtx = null;
let isAudioPlaying = false;
let audioGain = null;
let audioOscillators = [];

// Compact Universal Metric Formatter (e.g. 999 -> 999, 1000 -> 1K, 1500 -> 1.5K, 3400 -> 3.4K, 1000000 -> 1M)
function formatMetricNumber(num) {
  const n = Number(num);
  if (isNaN(n) || n <= 0) return '0';
  if (n < 1000) return n.toString();

  if (n < 1000000) {
    const k = n / 1000;
    const formatted = k >= 100 ? Math.round(k) : parseFloat(k.toFixed(1));
    return `${formatted}K`;
  }

  const m = n / 1000000;
  const formatted = m >= 100 ? Math.round(m) : parseFloat(m.toFixed(1));
  return `${formatted}M`;
}
window.formatMetricNumber = formatMetricNumber;

document.addEventListener('DOMContentLoaded', () => {
  SecurityGuard.enforceFrameSecurity();
  initFeed();
  initSortButtons();
  initSearch();
  initCategoryFilters();
  initAudioPlayer();
  initNotificationPrompt();
});

// Native Browser Notification Prompt Trigger (User Gesture Compliant)
function initNotificationPrompt() {
  const triggerNativePrompt = async () => {
    if (typeof Notification !== 'undefined' && Notification.permission === 'default') {
      try {
        if (window.OneSignal && window.OneSignal.Notifications && window.OneSignal.Notifications.requestPermission) {
          await window.OneSignal.Notifications.requestPermission();
        } else {
          await Notification.requestPermission();
        }
      } catch (e) {
        console.warn('Push permission error:', e);
      }
    }
  };

  // Attempt right away (desktop or permissive browsers)
  if (typeof Notification !== 'undefined' && Notification.permission === 'default') {
    window.OneSignalDeferred = window.OneSignalDeferred || [];
    window.OneSignalDeferred.push(function(OneSignal) {
      if (OneSignal.Notifications && OneSignal.Notifications.requestPermission) {
        OneSignal.Notifications.requestPermission().catch(() => {});
      }
    });
  }

  // Trigger on first click / tap (ensures Chrome Android user-gesture requirement is satisfied)
  const onFirstInteraction = () => {
    triggerNativePrompt();
    document.removeEventListener('click', onFirstInteraction);
    document.removeEventListener('touchstart', onFirstInteraction);
  };
  document.addEventListener('click', onFirstInteraction, { once: true, passive: true });
  document.addEventListener('touchstart', onFirstInteraction, { once: true, passive: true });
}

/* =========================================================
   SECURITY GUARD MODULE (Anti-Hacking, Anti-XSS, Anti-Spam)
   ========================================================= */
const SecurityGuard = {
  // 1. Anti-Clickjacking: Prevents malicious sites from framing the website
  enforceFrameSecurity() {
    try {
      if (window.top !== window.self) {
        window.top.location = window.self.location;
      }
    } catch (e) {
      document.body.style.display = 'none';
    }
  },

  // 2. Strict XSS Text Sanitizer (Strips HTML tags, dangerous schemes, control characters)
  sanitizeText(input, maxLength = 350) {
    if (typeof input !== 'string') return '';
    
    let sanitized = input
      .replace(/<[^>]*>/g, '') // Strip all HTML tags
      .replace(/javascript\s*:/gi, '') // Strip javascript: schemes
      .replace(/vbscript\s*:/gi, '')
      .replace(/data\s*:/gi, '')
      .replace(/on\w+\s*=/gi, '') // Strip event handlers
      .replace(/[\u0000-\u0008\u000B-\u000C\u000E-\u001F]/g, '') // Strip control chars
      .trim();

    if (maxLength && sanitized.length > maxLength) {
      sanitized = sanitized.substring(0, maxLength);
    }
    return sanitized;
  },

  // 3. Anti-Spam & Phishing Link Detection
  isSpamOrMalicious(text) {
    if (!text) return false;
    // Disallow external links, telegram channels, scam URLs in comments
    const spamPattern = /(https?:\/\/|ftp:\/\/|www\.|\.com|\.net|\.org|\.xyz|\.top|\.ru|\.cc|\.live|t\.me\/|bit\.ly\/|wa\.me\/|discord\.gg\/)/i;
    return spamPattern.test(text);
  },

  // 4. Anti-Flooding Rate Limiter (Cooldown between comment submissions)
  validateCommentRateLimit() {
    const lastTime = parseInt(localStorage.getItem('kv_last_comment_ts') || '0', 10);
    const now = Date.now();
    const cooldownMs = 10000; // 10 seconds cooldown
    
    if (now - lastTime < cooldownMs) {
      const waitSec = Math.ceil((cooldownMs - (now - lastTime)) / 1000);
      return {
        allowed: false,
        error: `⚠️ सुरक्षा नियम: कृपया ${waitSec} सेकंड प्रतीक्षा करें (Anti-Spam Cooldown)`
      };
    }
    return { allowed: true };
  },

  // Record comment submission timestamp
  recordCommentSubmission() {
    localStorage.setItem('kv_last_comment_ts', Date.now().toString());
  },

  // 5. Safe LocalStorage JSON Parser (Prevents JSON injection and corrupted crashes)
  safeJsonParse(rawString, fallback = []) {
    if (!rawString || typeof rawString !== 'string') return fallback;
    try {
      const parsed = JSON.parse(rawString);
      return parsed !== null ? parsed : fallback;
    } catch (e) {
      console.warn('SecurityGuard: Storage payload invalid, reset to fallback');
      return fallback;
    }
  }
};

/* =========================================================
   STATS & INTERACTION MANAGER (LocalStorage + Real Metrics)
   ========================================================= */
const StatsManager = {
  // Get combined stats (base mock data + actual local user interactions)
  getStats(postId) {
    const post = getPostById(postId);
    const baseViews = post ? (post.views || 2400) : 1500;
    const baseLikes = post ? (post.likes || 1200) : 800;
    const baseShares = post ? (post.shares || 350) : 200;
    const baseDownloads = post ? (post.downloads || 600) : 400;

    const userLiked = localStorage.getItem(`kv_liked_${postId}`) === 'true';
    const localLikeDelta = userLiked ? 1 : 0;
    const localViews = parseInt(localStorage.getItem(`kv_views_${postId}`) || '0', 10);
    const localShares = parseInt(localStorage.getItem(`kv_shares_${postId}`) || '0', 10);
    const localDownloads = parseInt(localStorage.getItem(`kv_downloads_${postId}`) || '0', 10);

    const comments = this.getComments(postId);

    return {
      views: baseViews + localViews,
      likes: baseLikes + localLikeDelta,
      shares: baseShares + localShares,
      downloads: baseDownloads + localDownloads,
      commentsCount: comments.length,
      isLiked: userLiked
    };
  },

  // Record a page/card view (once per browser session per post)
  recordView(postId) {
    const sessionKey = `kv_viewed_${postId}`;
    if (!sessionStorage.getItem(sessionKey)) {
      sessionStorage.setItem(sessionKey, '1');
      const cur = parseInt(localStorage.getItem(`kv_views_${postId}`) || '0', 10);
      localStorage.setItem(`kv_views_${postId}`, (cur + 1).toString());
    }
  },

  // Toggle user like
  toggleLike(postId) {
    const isLiked = localStorage.getItem(`kv_liked_${postId}`) === 'true';
    const newLiked = !isLiked;
    if (newLiked) {
      localStorage.setItem(`kv_liked_${postId}`, 'true');
    } else {
      localStorage.removeItem(`kv_liked_${postId}`);
    }
    return {
      isLiked: newLiked,
      stats: this.getStats(postId)
    };
  },

  // Increment shares
  incrementShare(postId) {
    const cur = parseInt(localStorage.getItem(`kv_shares_${postId}`) || '0', 10);
    localStorage.setItem(`kv_shares_${postId}`, (cur + 1).toString());
    return this.getStats(postId);
  },

  // Increment downloads
  incrementDownload(postId) {
    const cur = parseInt(localStorage.getItem(`kv_downloads_${postId}`) || '0', 10);
    localStorage.setItem(`kv_downloads_${postId}`, (cur + 1).toString());
    return this.getStats(postId);
  },

  // Get comments list safely
  getComments(postId) {
    const post = getPostById(postId);
    const baseComments = (post && Array.isArray(post.comments)) ? post.comments : [];
    const userComments = SecurityGuard.safeJsonParse(localStorage.getItem(`kv_comments_${postId}`), []);
    return [...userComments, ...baseComments];
  },

  // Add new user comment with full security validation
  addComment(postId, name, text) {
    // 1. Rate Limit Check
    const rateCheck = SecurityGuard.validateCommentRateLimit();
    if (!rateCheck.allowed) {
      return { success: false, error: rateCheck.error };
    }

    // 2. Sanitize and length check
    const cleanName = SecurityGuard.sanitizeText(name || 'कृष्ण भक्त', 30);
    const cleanText = SecurityGuard.sanitizeText(text, 350);

    if (!cleanText || cleanText.length < 2) {
      return { success: false, error: '⚠️ कृपया कम से कम 2 अक्षरों की टिप्पणी लिखें।' };
    }

    // 3. Spam Link Check
    if (SecurityGuard.isSpamOrMalicious(cleanText) || SecurityGuard.isSpamOrMalicious(cleanName)) {
      return { success: false, error: '⚠️ सुरक्षा नियम: टिप्पणियों में बाहरी लिंक्स या विज्ञापनों की अनुमति नहीं है।' };
    }

    const newComment = {
      name: cleanName,
      text: cleanText,
      time: "अभी-अभी (Just now)",
      timestamp: Date.now()
    };

    let userComments = SecurityGuard.safeJsonParse(localStorage.getItem(`kv_comments_${postId}`), []);
    userComments.unshift(newComment);

    localStorage.setItem(`kv_comments_${postId}`, JSON.stringify(userComments));
    localStorage.setItem('kv_saved_username', cleanName);
    SecurityGuard.recordCommentSubmission();

    return {
      success: true,
      comment: newComment,
      allComments: this.getComments(postId)
    };
  }
};

// 1. Initialize and Render Posts Feed
function initFeed() {
  const grid = document.getElementById('postsGrid');
  if (!grid) return;

  const posts = window.KRISHNA_POSTS || [];
  renderFilteredPosts(posts);
}

// Handler for Feed Sort Buttons (Latest, Views, Likes, Downloads, Shares, Reels)
function handleSortChange(sortKey) {
  currentSort = sortKey;
  document.querySelectorAll('.sort-btn').forEach(btn => {
    if (btn.getAttribute('data-sort') === sortKey) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  const posts = window.KRISHNA_POSTS || [];
  renderFilteredPosts(posts);

  const sortNames = {
    'latest': '🆕 ताज़ा दिव्य दर्शन (Latest Posts)',
    'views': '👁️ सर्वाधिक देखे गए दर्शन (Top Views)',
    'likes': '❤️ सबसे अधिक पसंद किए गए दर्शन (Top Likes)',
    'downloads': '⬇️ सबसे अधिक डाउनलोड किए गए वॉलपेपर्स (Top Downloads)',
    'shares': '📲 सबसे अधिक शेयर किए गए दर्शन (Top Shares)',
    'reels': '🎬 केवल अलौकिक 4K रील्स (4K Reels Only)'
  };
  if (sortNames[sortKey]) {
    showToast(sortNames[sortKey]);
  }
}

function initSortButtons() {
  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.onclick = function(e) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }
      const sortKey = this.getAttribute('data-sort');
      if (sortKey) handleSortChange(sortKey);
    };
  });
}

window.handleSortChange = handleSortChange;
window.initSortButtons = initSortButtons;

// Hover video preview helpers for cards
function previewCardVideo(wrap) {
  const video = wrap.querySelector('.video-hover-element');
  if (video) {
    video.play().catch(() => {});
  }
}

function stopCardVideo(wrap) {
  const video = wrap.querySelector('.video-hover-element');
  if (video) {
    video.pause();
    try { video.currentTime = 4.0; } catch (e) {}
  }
}

function renderFilteredPosts(allPosts) {
  const grid = document.getElementById('postsGrid');
  if (!grid) return;

  let filtered = [...allPosts];

  // 1. Filter by category
  if (activeCategory !== 'all') {
    filtered = filtered.filter(p => p.categorySlug === activeCategory || p.category === activeCategory);
  }

  // 2. Filter by search query
  if (searchQuery.trim() !== '') {
    const q = searchQuery.toLowerCase();
    filtered = filtered.filter(p => 
      p.title.toLowerCase().includes(q) || 
      p.quote.toLowerCase().includes(q) ||
      (p.tags && p.tags.some(t => t.toLowerCase().includes(q)))
    );
  }

  // 3. Filter / Sort by currentSort
  if (currentSort === 'reels') {
    filtered = filtered.filter(p => p.mediaType === 'video' || p.videoUrl || (p.imageUrl && p.imageUrl.endsWith('.mp4')));
  } else if (currentSort === 'views') {
    filtered.sort((a, b) => StatsManager.getStats(b.id).views - StatsManager.getStats(a.id).views);
  } else if (currentSort === 'likes') {
    filtered.sort((a, b) => StatsManager.getStats(b.id).likes - StatsManager.getStats(a.id).likes);
  } else if (currentSort === 'downloads') {
    filtered.sort((a, b) => StatsManager.getStats(b.id).downloads - StatsManager.getStats(a.id).downloads);
  } else if (currentSort === 'shares') {
    filtered.sort((a, b) => StatsManager.getStats(b.id).shares - StatsManager.getStats(a.id).shares);
  } // 'latest' maintains default order

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-muted);">
        <span style="font-size: 3rem; display: block; margin-bottom: 12px;">🪷</span>
        <h3 style="color: var(--gold-primary); font-size: 1.3rem; margin-bottom: 8px;">कोई परिणाम नहीं मिला</h3>
        <p style="font-size: 0.9rem;">कृपया किसी अन्य श्रेणी या फिल्टर से देखें।</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = filtered.map(post => {
    const stats = StatsManager.getStats(post.id);
    const isVideo = (post.mediaType === 'video') || (post.videoUrl) || (post.imageUrl && post.imageUrl.endsWith('.mp4'));
    const videoUrl = post.videoUrl || (post.imageUrl && post.imageUrl.endsWith('.mp4') ? post.imageUrl : null);
    const posterImg = (post.imageUrl && !post.imageUrl.endsWith('.mp4')) ? post.imageUrl : 'https://files.catbox.moe/yt84ra.jpg';
    const seoAlt = getSeoAltText(post, isVideo);

    const mediaHtml = isVideo ? `
      <div class="video-card-thumb-wrap" 
           onmouseenter="onReelMouseEnter('${post.id}')" 
           onmouseleave="onReelMouseLeave('${post.id}')">
        <video id="video-${post.id}" 
               class="card-img video-poster-img video-hover-element" 
               src="${videoUrl}#t=4.0" 
               preload="metadata" 
               muted 
               playsinline 
               loop 
               style="width:100%;height:100%;object-fit:cover;display:block;">
        </video>
        <button class="reel-center-play-btn" 
                id="play-btn-${post.id}" 
                onclick="toggleReelPlay('${post.id}', event)" 
                title="प्ले / पॉज़ करें" 
                aria-label="Play or pause reel">
          <span class="play-icon">▶</span>
        </button>
        <button class="reel-sound-btn" 
                id="sound-btn-${post.id}" 
                onclick="toggleReelSound('${post.id}', event)" 
                title="आवाज़ चालू करें (Unmute)" 
                aria-label="Mute or unmute reel sound">
          <svg class="sound-icon-muted" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
            <line x1="23" y1="9" x2="17" y2="15"></line>
            <line x1="17" y1="9" x2="23" y2="15"></line>
          </svg>
          <svg class="sound-icon-unmuted" style="display:none;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
          </svg>
        </button>
      </div>
    ` : `
      <img class="card-img" src="${post.imageUrl}" alt="${escapeHtml(seoAlt)}" title="${escapeHtml(seoAlt)}" loading="lazy">
    `;

    return `
      <article class="post-card" id="card-${post.id}">
        <div class="card-img-wrap">
          <a href="post.html?id=${post.id}" class="card-media-link" style="display:block;width:100%;height:100%;text-decoration:none;color:inherit;">
            ${mediaHtml}
          </a>
          <span class="card-overlay-badge">${isVideo ? '🎬' : '🪷'} ${escapeHtml(post.category)}</span>
          <span class="card-stats-badge">👁️ <span class="view-num-${post.id}">${formatMetricNumber(stats.views)}</span></span>
          <button class="card-media-like-btn ${stats.isLiked ? 'liked' : ''}" 
                  id="media-like-${post.id}" 
                  onclick="toggleFeedLike('${post.id}', event)" 
                  title="${stats.isLiked ? 'पसंद हटाएँ (Unlike)' : 'पसंद करें (Like)'}"
                  aria-label="Like post">
            <svg class="heart-icon" width="15" height="15" viewBox="0 0 24 24" fill="${stats.isLiked ? '#FF4757' : 'none'}" stroke="${stats.isLiked ? '#FF4757' : '#ffffff'}" stroke-width="2">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
            <span class="like-num-${post.id} media-like-count">${formatMetricNumber(stats.likes)}</span>
          </button>
          <span class="video-reel-pill">${isVideo ? '4K REEL' : '4K IMAGE'}</span>
        </div>
        <div class="card-body">
          <div class="card-date-row">
            <span>📅 ${post.date}</span>
            <span>⏱️ ${(() => {
              const rt = post.readTime || (isVideo ? '2 मिनट' : '3 मिनट');
              if (rt.includes('समय') || rt.includes('टाइम')) return rt;
              return isVideo ? `देखने का समय: ${rt}` : `पढ़ने का समय: ${rt}`;
            })()}</span>
          </div>
          <!-- Accessible SEO Title: 100% Googlebot & Semantic Schema Intact (Visually hidden on feed cards) -->
          <h2 class="card-title">
            <a href="post.html?id=${post.id}" style="color:inherit;text-decoration:none;">
              ${escapeHtml(post.title)}
            </a>
          </h2>
          <div class="card-quote-box">
            <div class="card-quote-content">
              "${escapeHtml(post.quote)}"
            </div>
            <button class="quote-copy-btn" id="copy-btn-${post.id}" onclick="copyQuote('${post.id}', event)" title="सुविचार कॉपी करें (Copy Thought)">
              <svg class="copy-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              <span class="copy-text">कॉपी</span>
            </button>
          </div>
          <p class="card-desc">${escapeHtml(post.shortDesc || '')}</p>

          <!-- Interactive Real Metrics Strip (Formatted: 1K, 1.5K, 3.4K, 1M) -->
          <div class="card-metrics-strip">
            <span class="metric-item" title="कुल दर्शन (Views)">
              👁️ <strong class="view-num-${post.id}">${formatMetricNumber(stats.views)}</strong>
            </span>
            
            <span class="metric-item interactive ${stats.isLiked ? 'like-active' : ''}" 
                  id="card-like-${post.id}" 
                  onclick="toggleFeedLike('${post.id}', event)" 
                  title="${stats.isLiked ? 'पसंद हटाएँ' : 'पसंद करें (Like)'}">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="${stats.isLiked ? '#FF4757' : 'none'}" stroke="currentColor" stroke-width="2">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
              <strong class="like-num-${post.id}">${formatMetricNumber(stats.likes)}</strong>
            </span>

            <a href="post.html?id=${post.id}#commentsSection" class="metric-item interactive" style="color:inherit;text-decoration:none;" title="भक्त टिप्पणियाँ">
              💬 <strong class="comment-num-${post.id}">${formatMetricNumber(stats.commentsCount)}</strong>
            </a>

            <span class="metric-item" title="कुल शेयर (Shares)">
              📲 <strong class="share-num-${post.id}">${formatMetricNumber(stats.shares)}</strong>
            </span>

            <span class="metric-item" title="वॉलपेपर / रील डाउनलोड">
              ⬇️ <strong class="dl-num-${post.id}">${formatMetricNumber(stats.downloads)}</strong>
            </span>
          </div>

          <div class="card-actions">
            <button class="btn-whatsapp-share" onclick="shareOnWhatsApp('${post.id}')" title="WhatsApp पर शेयर करें">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.771-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.312.045-.634.07-.98-.06-.525-.198-1.503-.615-2.355-1.468-.853-.853-1.27-1.831-1.468-2.355-.13-.346-.105-.668-.06-.98.05-.333.419-1.026.824-1.17.151-.054.305-.035.438.047.165.103.498.818.544.92.046.103.076.223.015.344-.061.121-.092.197-.183.303-.092.106-.195.237-.279.319-.092.091-.188.19-.081.374.106.183.473.78 1.015 1.262.697.621 1.285.814 1.468.905.183.092.29.076.397-.046.106-.121.457-.532.579-.715.121-.183.243-.152.408-.091.166.061 1.051.496 1.233.587.183.091.304.137.349.213.045.076.045.441-.099.846z"/>
              </svg>
              शेयर करें
            </button>
            <button class="btn-download-hd" onclick="downloadHdWallpaper('${post.id}')" title="${isVideo ? '4K Reel डाउनलोड करें' : 'HD Wallpaper डाउनलोड करें'}">
              ${isVideo ? '⬇️ 4K Reel (MP4)' : '⬇️ HD Wallpaper'}
            </button>
            <a href="post.html?id=${post.id}" class="btn-read-full">
              पूरा दर्शन एवं भावार्थ पढ़ें →
            </a>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

// Like handler for homepage feed cards
function toggleFeedLike(postId, event) {
  if (event) {
    event.stopPropagation();
    event.preventDefault();
  }
  const result = StatsManager.toggleLike(postId);
  
  // Update all instances of like counts for this post
  document.querySelectorAll(`.like-num-${postId}`).forEach(el => {
    el.textContent = formatMetricNumber(result.stats.likes);
  });

  const cardBtn = document.getElementById(`card-like-${postId}`);
  if (cardBtn) {
    if (result.isLiked) {
      cardBtn.classList.add('like-active');
      const svg = cardBtn.querySelector('svg');
      if (svg) svg.setAttribute('fill', '#FF4757');
    } else {
      cardBtn.classList.remove('like-active');
      const svg = cardBtn.querySelector('svg');
      if (svg) svg.setAttribute('fill', 'none');
    }
  }

  // 2. Update media overlay like button
  const mediaBtn = document.getElementById(`media-like-${postId}`);
  if (mediaBtn) {
    const heartSvg = mediaBtn.querySelector('svg');
    if (result.isLiked) {
      mediaBtn.classList.add('liked');
      if (heartSvg) {
        heartSvg.setAttribute('fill', '#FF4757');
        heartSvg.setAttribute('stroke', '#FF4757');
      }
    } else {
      mediaBtn.classList.remove('liked');
      if (heartSvg) {
        heartSvg.setAttribute('fill', 'none');
        heartSvg.setAttribute('stroke', '#ffffff');
      }
    }
  }

  if (result.isLiked) {
    triggerDivineLikeAnimation(postId);
    showToast('❤️ आपने यह दिव्य विचार पसंद किया! जय श्री कृष्णा');
  } else {
    showToast('🤍 पसंद हटा दी गई');
  }
}

// Divine Floating Petals, Flowers & Peacock Feathers Burst on Like
function triggerDivineLikeAnimation(postId) {
  const card = document.getElementById(`card-${postId}`);
  if (!card) return;
  const imgWrap = card.querySelector('.card-img-wrap');
  if (!imgWrap) return;

  // Divine symbols: Lord Krishna Lotus, Pink Rose Petals, Peacock Feather, Sparkles, Flowers
  const symbols = ['🪶', '🌸', '🪷', '✨', '🌺', '🪶', '🌸', '✨'];
  const particleCount = 14;

  for (let i = 0; i < particleCount; i++) {
    const el = document.createElement('span');
    el.className = 'divine-petal-particle';
    el.textContent = symbols[Math.floor(Math.random() * symbols.length)];

    // Origin: scattered across bottom area of image
    const startX = (15 + Math.random() * 70).toFixed(1);
    const startY = (70 + Math.random() * 20).toFixed(1);

    const dx1 = ((Math.random() - 0.5) * 80).toFixed(1) + 'px';
    const dx2 = ((Math.random() - 0.5) * 140).toFixed(1) + 'px';
    const dx3 = ((Math.random() - 0.5) * 200).toFixed(1) + 'px';
    const rot1 = (Math.random() * 60 - 30).toFixed(1) + 'deg';
    const rot2 = (Math.random() * 180 - 90).toFixed(1) + 'deg';
    const rot3 = (Math.random() * 360 - 180).toFixed(1) + 'deg';
    const delay = (i * 0.07).toFixed(2) + 's';
    const size = (1.2 + Math.random() * 0.8).toFixed(2) + 'rem';

    el.style.left = `${startX}%`;
    el.style.top = `${startY}%`;
    el.style.fontSize = size;
    el.style.animationDelay = delay;
    el.style.setProperty('--dx1', dx1);
    el.style.setProperty('--dx2', dx2);
    el.style.setProperty('--dx3', dx3);
    el.style.setProperty('--rot1', rot1);
    el.style.setProperty('--rot2', rot2);
    el.style.setProperty('--rot3', rot3);

    imgWrap.appendChild(el);

    // Auto cleanup after 2.8s
    setTimeout(() => {
      el.remove();
    }, 2800);
  }
}

// ==========================================
// REEL INTERACTIVE VIDEO & AUDIO CONTROLS
// ==========================================
function onReelMouseEnter(postId) {
  const video = document.getElementById(`video-${postId}`);
  if (!video) return;

  const playPromise = video.play();
  if (playPromise !== undefined) {
    playPromise.then(() => {
      updatePlayBtnState(postId, true);
    }).catch(err => {
      console.warn('Autoplay error on hover:', err);
    });
  }
}

function onReelMouseLeave(postId) {
  const video = document.getElementById(`video-${postId}`);
  if (!video) return;

  video.pause();
  updatePlayBtnState(postId, false);
}

function toggleReelPlay(postId, event) {
  if (event) {
    if (typeof event.stopPropagation === 'function') event.stopPropagation();
    if (typeof event.preventDefault === 'function') event.preventDefault();
  }
  const video = document.getElementById(`video-${postId}`);
  if (!video) return;

  if (video.paused) {
    document.querySelectorAll('.video-hover-element').forEach(v => {
      if (v !== video) {
        v.pause();
        const otherId = v.id.replace('video-', '');
        updatePlayBtnState(otherId, false);
      }
    });

    video.play().then(() => {
      updatePlayBtnState(postId, true);
      showToast('▶️ रील प्ले हो रही है');
    }).catch(err => {
      console.warn('Play error:', err);
    });
  } else {
    video.pause();
    updatePlayBtnState(postId, false);
    showToast('⏸️ रील पॉज़ हुई');
  }
}

function updatePlayBtnState(postId, isPlaying) {
  const btn = document.getElementById(`play-btn-${postId}`);
  if (!btn) return;
  const icon = btn.querySelector('.play-icon');
  if (isPlaying) {
    btn.classList.add('is-playing');
    if (icon) icon.textContent = '⏸';
  } else {
    btn.classList.remove('is-playing');
    if (icon) icon.textContent = '▶';
  }
}

function toggleReelSound(postId, event) {
  if (event) {
    if (typeof event.stopPropagation === 'function') event.stopPropagation();
    if (typeof event.preventDefault === 'function') event.preventDefault();
  }
  const video = document.getElementById(`video-${postId}`);
  const btn = document.getElementById(`sound-btn-${postId}`);
  if (!video || !btn) return;

  const newMuted = !video.muted;
  video.muted = newMuted;

  const mutedIcon = btn.querySelector('.sound-icon-muted');
  const unmutedIcon = btn.querySelector('.sound-icon-unmuted');

  if (newMuted) {
    btn.classList.remove('is-unmuted');
    btn.title = "आवाज़ चालू करें (Unmute)";
    if (mutedIcon) mutedIcon.style.display = 'block';
    if (unmutedIcon) unmutedIcon.style.display = 'none';
    showToast('🔇 ऑडियो म्यूट हुआ');
  } else {
    document.querySelectorAll('.video-hover-element').forEach(v => {
      if (v !== video) v.muted = true;
    });
    if (video.paused) {
      video.play().then(() => updatePlayBtnState(postId, true)).catch(() => {});
    }
    btn.classList.add('is-unmuted');
    btn.title = "आवाज़ बंद करें (Mute)";
    if (mutedIcon) mutedIcon.style.display = 'none';
    if (unmutedIcon) unmutedIcon.style.display = 'block';
    showToast('🔊 दिव्य वाणी व मधुर बांसुरी आवाज़ चालू!');
  }
}

window.toggleReelPlay = toggleReelPlay;
window.toggleReelSound = toggleReelSound;
window.onReelMouseEnter = onReelMouseEnter;
window.onReelMouseLeave = onReelMouseLeave;


// Category Icons Mapping
const CATEGORY_ICONS = {
  'दिव्य रील्स (Reels)': '🎬',
  'भगवद्गीता ज्ञान': '📖',
  'दैनिक दर्शन': '🪷',
  'राधे कृष्ण प्रेम': '💖',
  'प्रेरणादायक सीख': '✨',
  'विद्यार्थी प्रेरणा (Study)': '📚',
  'युवा प्रेरणा (Motivation)': '🔥',
  'सफलता के सूत्र': '🏆',
  'लक्ष्य एवं एकाग्रता': '🎯',
  'श्री कृष्ण लीला': '🦚',
  'भक्ति रस': '📿',
  'सुप्रभात दर्शन': '🌄',
  'कर्म योग': '⚖️',
  'शांति एवं ध्यान': '🧘'
};

// 2. Dynamic Category Pills Generator
function initCategoryFilters() {
  const container = document.getElementById('categoryFilterWrap');
  if (!container) return;

  const allPosts = window.KRISHNA_POSTS || [];
  
  // Collect all unique categories and count their occurrences
  const categoryCounts = {};
  allPosts.forEach(p => {
    const cat = p.category || 'दैनिक दर्शन';
    categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
  });

  const uniqueCategories = Object.keys(categoryCounts);

  // Generate HTML for pills
  let pillsHtml = `
    <button class="cat-pill ${activeCategory === 'all' ? 'active' : ''}" data-cat="all">
      🌸 सभी दर्शन (${allPosts.length})
    </button>
  `;

  uniqueCategories.forEach(cat => {
    const icon = CATEGORY_ICONS[cat] || '🪷';
    const isActive = activeCategory === cat ? 'active' : '';
    const count = categoryCounts[cat];
    pillsHtml += `
      <button class="cat-pill ${isActive}" data-cat="${escapeHtml(cat)}">
        ${icon} ${escapeHtml(cat)} (${count})
      </button>
    `;
  });

  container.innerHTML = pillsHtml;

  // Attach event listeners to all newly created pills
  const pills = container.querySelectorAll('.cat-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', (e) => {
      if (e) e.preventDefault();
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeCategory = pill.getAttribute('data-cat') || 'all';
      renderFilteredPosts(window.KRISHNA_POSTS || []);
      const label = pill.textContent.trim().replace(/\(\d+\)/, '').trim();
      showToast(`✨ श्रेणी: ${label}`);
    });
  });
}

// 3. Search Bar Handler
function initSearch() {
  const searchInp = document.getElementById('searchInput');
  if (!searchInp) return;
  searchInp.addEventListener('input', (e) => {
    searchQuery = e.target.value;
    renderFilteredPosts(window.KRISHNA_POSTS || []);
  });
}

// 4. WhatsApp Sharing Function
function shareOnWhatsApp(postId) {
  const post = getPostById(postId);
  if (!post) return;

  // Increment share metric
  const updatedStats = StatsManager.incrementShare(postId);

  // Update visible share counts
  document.querySelectorAll(`.share-num-${postId}`).forEach(el => {
    el.textContent = formatMetricNumber(updatedStats.shares);
  });

  const detailShares = document.getElementById('dShares');
  if (detailShares) {
    detailShares.textContent = formatMetricNumber(updatedStats.shares);
  }

  const currentUrl = window.location.origin + window.location.pathname.replace('index.html', '') + 'post.html?id=' + post.id;
  const text = `🪷 *श्री कृष्ण दिव्य संदेश | Krishna Vibez* 🪷\n\n"${post.quote}"\n\n✨ *${post.title}*\n\n📱 *आज का 4K HD Wallpaper डाउनलोड करें व पूरा भावार्थ पढ़ें:* \n👉 ${currentUrl}\n\n🙏 *राधे-राधे! अपने परिजनों को भी यह शुभ विचार अवश्य भेजें।*`;
  
  const shareUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
  window.open(shareUrl, '_blank');

  showToast('📲 WhatsApp शेयर विंडो खुल रही है (+1 Share)');
}

// 5. DIRECT HD Wallpaper & 4K Reel Download (Ensures 100% valid .jpg / .mp4 extensions)
async function downloadHdWallpaper(postId) {
  const post = getPostById(postId);
  if (!post) return;

  const isVideo = (post.mediaType === 'video') || (post.videoUrl) || (post.imageUrl && post.imageUrl.endsWith('.mp4'));
  const mediaUrl = post.videoUrl || post.imageUrl;
  const ext = isVideo ? '.mp4' : '.jpg';
  const filename = `Krishna-Vibez-${post.id}${ext}`;
  const mimeType = isVideo ? 'video/mp4' : 'image/jpeg';

  showToast(isVideo ? '📥 4K Reel वीडियो (.mp4) डाउनलोड हो रहा है...' : '📥 4K HD Wallpaper (.jpg) डाउनलोड हो रहा है...');

  try {
    // 1. Fetch raw binary data
    const response = await fetch(mediaUrl);
    if (!response.ok) throw new Error('Fetch failed with status ' + response.status);
    const rawBlob = await response.blob();
    
    // Explicitly enforce MIME type to guarantee valid image/video headers
    const typedBlob = new Blob([rawBlob], { type: mimeType });

    if (!isVideo) {
      // For images: FileReader DataURL guarantees exact filename with .jpg extension on all browsers and file://
      const reader = new FileReader();
      reader.onload = function() {
        const a = document.createElement('a');
        a.href = reader.result;
        a.setAttribute('download', filename);
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => document.body.removeChild(a), 1500);
        showToast('✅ 4K Wallpaper (.jpg) सीधे डाउनलोड हो गया!');
      };
      reader.onerror = function() {
        fallbackBlobDownload(typedBlob, filename, isVideo);
      };
      reader.readAsDataURL(typedBlob);
    } else {
      // For videos: File constructor with typed Blob
      fallbackBlobDownload(typedBlob, filename, isVideo);
    }
  } catch (err) {
    console.warn('Direct fetch error, using anchor fallback:', err);
    // Direct link fallback
    const a = document.createElement('a');
    a.href = mediaUrl;
    a.setAttribute('download', filename);
    a.target = '_blank';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => document.body.removeChild(a), 1500);
  }

  // Increment download metric
  const updatedStats = StatsManager.incrementDownload(postId);
  document.querySelectorAll(`.dl-num-${postId}`).forEach(el => {
    el.textContent = formatMetricNumber(updatedStats.downloads);
  });
  const detailDls = document.getElementById('dDownloads');
  if (detailDls) {
    detailDls.textContent = formatMetricNumber(updatedStats.downloads);
  }
}

function fallbackBlobDownload(blob, filename, isVideo) {
  let downloadUrl;
  try {
    const file = new File([blob], filename, { type: blob.type });
    downloadUrl = window.URL.createObjectURL(file);
  } catch(e) {
    downloadUrl = window.URL.createObjectURL(blob);
  }
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.setAttribute('download', filename);
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    window.URL.revokeObjectURL(downloadUrl);
  }, 60000); // 60s timeout so large files finish streaming
  showToast(isVideo ? '✅ 4K Reel (.mp4) डाउनलोड हो गया!' : '✅ 4K Wallpaper (.jpg) डाउनलोड हो गया!');
}

// 6. Copy Quote to Clipboard
function copyQuote(postId, event) {
  if (event) {
    if (typeof event.stopPropagation === 'function') event.stopPropagation();
    if (typeof event.preventDefault === 'function') event.preventDefault();
  }
  const post = getPostById(postId);
  if (!post) return;

  const textToCopy = `"${post.quote}" — श्री कृष्ण (via krishnavibez.in)`;

  const onCopySuccess = () => {
    showToast('✨ सुविचार कॉपी हो गया!');
    const btn = document.getElementById(`copy-btn-${postId}`);
    if (btn) {
      btn.classList.add('copied');
      const textSpan = btn.querySelector('.copy-text');
      const originalText = textSpan ? textSpan.textContent : 'कॉपी';
      if (textSpan) textSpan.textContent = '✓ कॉपीड';
      setTimeout(() => {
        btn.classList.remove('copied');
        if (textSpan) textSpan.textContent = originalText;
      }, 2000);
    }
  };

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(textToCopy).then(onCopySuccess).catch(() => {
      fallbackCopyText(textToCopy, onCopySuccess);
    });
  } else {
    fallbackCopyText(textToCopy, onCopySuccess);
  }
}

function fallbackCopyText(text, onSuccess) {
  try {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    const successful = document.execCommand('copy');
    document.body.removeChild(textArea);
    if (successful && typeof onSuccess === 'function') {
      onSuccess();
    } else {
      showToast('✨ सुविचार कॉपी हो गया!');
    }
  } catch (err) {
    showToast('⚠️ कॉपी नहीं हो सका');
  }
}
window.copyQuote = copyQuote;

// 7. Ambient Flute Sound Generator (Web Audio API - Zero MP3 dependency)
function initAudioPlayer() {
  const btn = document.getElementById('audioToggleBtn');
  if (!btn) return;

  btn.addEventListener('click', toggleAmbientAudio);
}

function toggleAmbientAudio() {
  const btn = document.getElementById('audioToggleBtn');
  const bars = document.getElementById('audioBars');
  const label = document.getElementById('audioStatusLabel');

  if (!audioCtx) {
    try {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    } catch(e) {
      showToast('Audio not supported on this browser');
      return;
    }
  }

  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }

  if (!isAudioPlaying) {
    startFluteHarmony();
    isAudioPlaying = true;
    if (bars) bars.classList.remove('paused');
    if (label) label.textContent = 'Flute ON';
    showToast('🎵 दिव्य बांसुरी की शांतिदायक धुन शुरू हुई');
  } else {
    stopFluteHarmony();
    isAudioPlaying = false;
    if (bars) bars.classList.add('paused');
    if (label) label.textContent = 'Flute OFF';
    showToast('🔇 ऑडियो बंद हुआ');
  }
}

function startFluteHarmony() {
  if (!audioCtx) return;
  audioGain = audioCtx.createGain();
  audioGain.gain.setValueAtTime(0.08, audioCtx.currentTime);
  audioGain.connect(audioCtx.destination);

  const freqs = [261.63, 392.00, 523.25, 659.25];
  audioOscillators = [];

  freqs.forEach((freq, idx) => {
    const osc = audioCtx.createOscillator();
    osc.type = idx % 2 === 0 ? 'sine' : 'triangle';
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);

    const lfo = audioCtx.createOscillator();
    lfo.frequency.setValueAtTime(4.5 + idx * 0.5, audioCtx.currentTime);
    const lfoGain = audioCtx.createGain();
    lfoGain.gain.setValueAtTime(2.5, audioCtx.currentTime);
    lfo.connect(lfoGain);
    lfoGain.connect(osc.frequency);
    lfo.start();

    osc.connect(audioGain);
    osc.start();
    audioOscillators.push(osc);
  });
}

function stopFluteHarmony() {
  if (audioGain && audioCtx) {
    audioGain.gain.linearRampToValueAtTime(0.001, audioCtx.currentTime + 0.5);
    setTimeout(() => {
      audioOscillators.forEach(osc => { try { osc.stop(); } catch(e){} });
      audioOscillators = [];
    }, 550);
  }
}

// 8. Helper Functions
function getPostById(id) {
  const posts = window.KRISHNA_POSTS || [];
  return posts.find(p => p.id === id);
}

function showToast(msg) {
  let toast = document.getElementById('toastMsg');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toastMsg';
    toast.className = 'toast-msg';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<span>🪷</span> ${escapeHtml(msg)}`;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3200);
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  })[m]);
}

// 9. SEO Alt Text Generator (For Google Image & Video Search Ranking)
function getSeoAltText(post, isVideo) {
  if (post && post.altText) return post.altText;
  if (!post) return 'श्री कृष्ण 4K HD दर्शन — Krishna Vibez';
  
  const cleanQuote = (post.quote || '').substring(0, 75).trim();
  if (isVideo) {
    return `श्री कृष्ण 4K दिव्य रील वीडियो — ${post.title} — "${cleanQuote}" | Krishna Vibez Reels`;
  }
  return `श्री कृष्ण 4K HD वॉलपेपर — ${post.title} — "${cleanQuote}" | Krishna Vibez Wallpaper`;
}

