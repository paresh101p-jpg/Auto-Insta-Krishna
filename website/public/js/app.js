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

// Hover video preview helpers for cards (RAM-optimized: loads video only on hover)
function previewCardVideo(wrap) {
  const video = wrap.querySelector('.video-hover-element');
  if (video) {
    if (!video.src && video.dataset.src) {
      video.src = video.dataset.src;
    }
    video.style.display = 'block';
    video.play().catch(() => {});
  }
}

function stopCardVideo(wrap) {
  const video = wrap.querySelector('.video-hover-element');
  if (video) {
    video.pause();
    video.style.display = 'none';
  }
}

// Progressive 60-FPS Feed Engine (Zero Lag, Fast Progressive Chunking)
let currentFilteredList = [];
let currentRenderedIndex = 0;
const FEED_BATCH_SIZE = 12;
let feedScrollObserver = null;

function extractYouTubeId(url) {
  if (!url) return null;
  const m = String(url).match(/(?:shorts\/|v=|youtu\.be\/|\/v\/|\/embed\/)([a-zA-Z0-9_-]{11})/);
  return m ? m[1] : null;
}

function renderSinglePostCard(post) {
  const stats = StatsManager.getStats(post.id);
  const ytId = extractYouTubeId(post.videoUrl) || extractYouTubeId(post.imageUrl);
  const isVideo = (post.mediaType === 'video') || Boolean(post.videoUrl) || (post.imageUrl && post.imageUrl.endsWith('.mp4')) || Boolean(ytId);
  const videoUrl = post.videoUrl || (post.imageUrl && post.imageUrl.endsWith('.mp4') ? post.imageUrl : null);
  const isDirectMp4 = Boolean(videoUrl && videoUrl.endsWith('.mp4'));

  let posterImg = 'https://files.catbox.moe/yt84ra.jpg';
  if (ytId) {
    posterImg = `https://i.ytimg.com/vi/${ytId}/hqdefault.jpg`;
  } else if (post.imageUrl && !post.imageUrl.endsWith('.mp4') && !post.imageUrl.includes('youtube')) {
    posterImg = post.imageUrl;
  }

  const seoAlt = getSeoAltText(post, isVideo);
  const targetUrl = post.articleUrl || `/post/${post.id}`;

  const mediaHtml = isVideo ? `
    <div class="video-card-thumb-wrap" onmouseenter="previewCardVideo(this)" onmouseleave="stopCardVideo(this)">
      <img class="card-img video-poster-img" src="${posterImg}" alt="${escapeHtml(seoAlt)}" title="${escapeHtml(seoAlt)}" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.onerror=null;this.src='https://files.catbox.moe/yt84ra.jpg';">
      <video class="card-img video-hover-element" data-src="${isDirectMp4 ? videoUrl : ''}" preload="none" muted playsinline loop style="display:none;position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;z-index:1;"></video>
      <div class="video-play-overlay">▶</div>
      <span class="video-reel-pill">4K REEL</span>
    </div>
  ` : `
    <img class="card-img" src="${post.imageUrl}" alt="${escapeHtml(seoAlt)}" title="${escapeHtml(seoAlt)}" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.onerror=null;this.src='https://files.catbox.moe/yt84ra.jpg';">
  `;

  return `
    <article class="post-card" id="card-${post.id}">
      <div class="card-img-wrap">
        <a href="${targetUrl}" class="card-media-link" style="display:block;width:100%;height:100%;text-decoration:none;color:inherit;">
          ${mediaHtml}
        </a>
        <span class="card-overlay-badge">${isVideo ? '🎬' : '🪷'} ${escapeHtml(post.category)}</span>
        <span class="card-stats-badge">👁️ <span class="view-num-${post.id}">${stats.views.toLocaleString('en-IN')}</span></span>
      </div>
      <div class="card-body">
        <div class="card-date-row">
          <span>📅 ${post.date}</span>
          <span>⏱️ ${post.readTime || '3 min read'}</span>
        </div>
        <h2 class="card-title">
          <a href="${targetUrl}" style="color:inherit;text-decoration:none;">
            ${escapeHtml(post.title)}
          </a>
        </h2>
        <div class="card-quote-box">
          "${escapeHtml(post.quote)}"
        </div>
        <p class="card-desc">${escapeHtml(post.shortDesc || '')}</p>

        <!-- Interactive Real Metrics Strip -->
        <div class="card-metrics-strip">
          <span class="metric-item" title="कुल दर्शन (Views)">
            👁️ <strong class="view-num-${post.id}">${stats.views.toLocaleString('en-IN')}</strong>
          </span>
          
          <span class="metric-item interactive ${stats.isLiked ? 'like-active' : ''}" 
                id="card-like-${post.id}" 
                onclick="toggleFeedLike('${post.id}', event)" 
                title="${stats.isLiked ? 'पसंद हटाएँ' : 'पसंद करें (Like)'}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="${stats.isLiked ? '#FF4757' : 'none'}" stroke="currentColor" stroke-width="2">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
            <strong class="like-num-${post.id}">${stats.likes.toLocaleString('en-IN')}</strong>
          </span>

          <a href="/post/${post.id}#commentsSection" class="metric-item interactive" style="color:inherit;text-decoration:none;" title="भक्त टिप्पणियाँ">
            💬 <strong class="comment-num-${post.id}">${stats.commentsCount}</strong>
          </a>

          <span class="metric-item" title="कुल शेयर (Shares)">
            📲 <strong class="share-num-${post.id}">${stats.shares.toLocaleString('en-IN')}</strong>
          </span>

          <span class="metric-item" title="वॉलपेपर / रील डाउनलोड">
            ⬇️ <strong class="dl-num-${post.id}">${stats.downloads.toLocaleString('en-IN')}</strong>
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
            ${isVideo ? '⬇️ 4K Reel' : '⬇️ HD Wallpaper'}
          </button>
          <a href="${targetUrl}" class="btn-read-full">
            पूरा दर्शन एवं भावार्थ पढ़ें →
          </a>
        </div>
      </div>
    </article>
  `;
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

  currentFilteredList = filtered;
  currentRenderedIndex = 0;

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

  // Blazing Fast Initial Batch (12 Cards Instant Render)
  const initialBatch = filtered.slice(0, FEED_BATCH_SIZE);
  currentRenderedIndex = initialBatch.length;
  grid.innerHTML = initialBatch.map(renderSinglePostCard).join('');

  updateLoadMoreControls();
  setupFeedInfiniteScroll();
}

function loadNextBatch() {
  const grid = document.getElementById('postsGrid');
  if (!grid || currentRenderedIndex >= currentFilteredList.length) return;

  const nextBatch = currentFilteredList.slice(currentRenderedIndex, currentRenderedIndex + FEED_BATCH_SIZE);
  currentRenderedIndex += nextBatch.length;

  const existingBtn = document.getElementById('feedLoadMoreWrap');
  if (existingBtn) existingBtn.remove();

  const newHtml = nextBatch.map(renderSinglePostCard).join('');
  grid.insertAdjacentHTML('beforeend', newHtml);

  updateLoadMoreControls();
}
window.loadNextBatch = loadNextBatch;

function updateLoadMoreControls() {
  const grid = document.getElementById('postsGrid');
  if (!grid) return;

  const existingBtn = document.getElementById('feedLoadMoreWrap');
  if (existingBtn) existingBtn.remove();

  if (currentRenderedIndex < currentFilteredList.length) {
    const remaining = currentFilteredList.length - currentRenderedIndex;
    const loadWrap = document.createElement('div');
    loadWrap.id = 'feedLoadMoreWrap';
    loadWrap.className = 'feed-load-more-wrap';
    loadWrap.innerHTML = `
      <button class="btn-load-more" onclick="loadNextBatch()" title="और दिव्य दर्शन देखें">
        <span>✨ और दर्शन देखें (${remaining} और विचार)</span>
      </button>
    `;
    grid.appendChild(loadWrap);

    // Attach IntersectionObserver to trigger automatically when user scrolls near the button
    if (feedScrollObserver) {
      feedScrollObserver.disconnect();
      feedScrollObserver.observe(loadWrap);
    }
  } else if (currentFilteredList.length > FEED_BATCH_SIZE) {
    const endWrap = document.createElement('div');
    endWrap.id = 'feedLoadMoreWrap';
    endWrap.className = 'feed-load-more-wrap';
    endWrap.innerHTML = `
      <div class="feed-end-badge">
        🌸 आपने सभी ${currentFilteredList.length} दिव्य दर्शन देख लिए हैं। जय श्री कृष्णा! 🌸
      </div>
    `;
    grid.appendChild(endWrap);
  }
}

function setupFeedInfiniteScroll() {
  if ('IntersectionObserver' in window) {
    if (feedScrollObserver) feedScrollObserver.disconnect();
    feedScrollObserver = new IntersectionObserver((entries) => {
      if (entries[0] && entries[0].isIntersecting) {
        loadNextBatch();
      }
    }, { rootMargin: '350px' });
  }
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
    el.textContent = result.stats.likes.toLocaleString('en-IN');
  });

  const cardBtn = document.getElementById(`card-like-${postId}`);
  if (cardBtn) {
    if (result.isLiked) {
      cardBtn.classList.add('like-active');
      cardBtn.querySelector('svg').setAttribute('fill', '#FF4757');
      showToast('❤️ आपने यह दिव्य विचार पसंद किया! जय श्री कृष्णा');
    } else {
      cardBtn.classList.remove('like-active');
      cardBtn.querySelector('svg').setAttribute('fill', 'none');
      showToast('🤍 पसंद हटा दी गई');
    }
  }
}

// Category Icons Mapping (Expanded for All 33+ Spiritual Categories)
const CATEGORY_ICONS = {
  'all': '🌸',
  'दिव्य रील्स (Reels)': '🎬',
  'भगवद्गीता ज्ञान': '📖',
  'भगवद्गीता सार (Gita Essence)': '📜',
  'दैनिक दर्शन': '🪷',
  'राधे कृष्ण प्रेम': '💖',
  'राधे कृष्ण प्रेम (Divine Love)': '💖',
  'प्रेरणादायक सीख': '✨',
  'विद्यार्थी प्रेरणा (Study)': '📚',
  'विद्यार्थी प्रेरणा (Youth & Students)': '📚',
  'युवा प्रेरणा (Motivation)': '🔥',
  'युवा मार्गदर्शन (Youth & Career)': '🚀',
  'सफलता के सूत्र': '🏆',
  'लक्ष्य एवं एकाग्रता': '🎯',
  'श्री कृष्ण लीला': '🦚',
  'भक्ति रस': '📿',
  'भक्ति योग (Bhakti Yoga)': '📿',
  'भक्ति एवं शरणागति (Surrender & Grace)': '🙏',
  'भक्ति एवं विश्वास (Faith & Devotion)': '🌺',
  'सुप्रभात दर्शन': '🌄',
  'कर्म योग': '⚖️',
  'कर्म योग (Karma Yoga)': '⚖️',
  'कर्म फल सिद्धांत (Law of Karma)': '🪐',
  'शांति एवं ध्यान': '🧘',
  'मानसिक शांति (Mind Control)': '🧘',
  'ध्यान योग (Meditation Yoga)': '🧘',
  'आत्म-संयम (Self-Discipline)': '🛡️',
  'स्थितप्रज्ञ दर्शन (Mastery of Mind)': '💎',
  'आध्यात्मिक ज्ञान (Spiritual Purpose)': '🌌',
  'ब्रह्म ज्ञान (Higher Wisdom)': '☀️',
  'धर्म एवं कर्तव्य (Dharma & Duty)': '🏹',
  'विश्वरूप दर्शन (Cosmic Vision & Time)': '👁️',
  'प्रकृति के तीन गुण (Three Gunas)': '🌿',
  'चरित्र एवं गुण (Virtues & Character)': '🌟',
  'मित्रता एवं संबंध (Friendship & Relationships)': '🤝',
  'आहार एवं जीवनशैली (Food & Lifestyle)': '🍃',
  'समत्व योग (Equanimity & Balance)': '☯️',
  'आत्मा का ज्ञान (Soul & Immortality)': '✨',
  'अवसाद मुक्ति (Stress & Depression Relief)': '🕊️',
  'अहंकार मुक्ति (Ego Freedom)': '🍃',
  'क्रोध नियंत्रण (Anger Management)': '💧'
};

// 2. Dynamic Category Ribbon & Modal Generator
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

  // Sort categories descending by post count (Most popular first)
  const uniqueCategories = Object.keys(categoryCounts).sort((a, b) => categoryCounts[b] - categoryCounts[a]);

  // Update total count badges
  const totalCountEl = document.getElementById('catTotalCount');
  if (totalCountEl) {
    totalCountEl.textContent = `${uniqueCategories.length}+`;
  }
  const modalSubEl = document.getElementById('catModalSubtitle');
  if (modalSubEl) {
    modalSubEl.textContent = `${uniqueCategories.length} विशेष श्रेणियाँ · तुरंत खोजें व चुनें`;
  }

  // Generate HTML for Horizontal Ribbon Pills
  let pillsHtml = `
    <button class="cat-pill ${activeCategory === 'all' ? 'active' : ''}" data-cat="all" onclick="selectCategory('all', this)">
      <span class="cat-pill-icon">🌸</span>
      <span class="cat-pill-label">सभी दर्शन</span>
      <span class="cat-pill-count">${allPosts.length}</span>
    </button>
  `;

  uniqueCategories.forEach(cat => {
    const icon = CATEGORY_ICONS[cat] || '🪷';
    const isActive = activeCategory === cat ? 'active' : '';
    const count = categoryCounts[cat];
    pillsHtml += `
      <button class="cat-pill ${isActive}" data-cat="${escapeHtml(cat)}" onclick="selectCategory('${escapeHtml(cat)}', this)">
        <span class="cat-pill-icon">${icon}</span>
        <span class="cat-pill-label">${escapeHtml(cat)}</span>
        <span class="cat-pill-count">${count}</span>
      </button>
    `;
  });

  container.innerHTML = pillsHtml;

  // Generate HTML for Modal Grid Tiles
  const modalGrid = document.getElementById('catModalGrid');
  if (modalGrid) {
    let modalHtml = `
      <div class="cat-modal-card ${activeCategory === 'all' ? 'active' : ''}" data-cat="all" onclick="selectCategory('all', null, true)">
        <span class="cat-modal-card-icon">🌸</span>
        <div class="cat-modal-card-info">
          <div class="cat-modal-card-name">सभी दर्शन (All)</div>
          <div class="cat-modal-card-count">${allPosts.length} संपूर्ण दर्शन संग्रह</div>
        </div>
        <span class="cat-modal-check">✓</span>
      </div>
    `;

    uniqueCategories.forEach(cat => {
      const icon = CATEGORY_ICONS[cat] || '🪷';
      const isActive = activeCategory === cat ? 'active' : '';
      const count = categoryCounts[cat];
      modalHtml += `
        <div class="cat-modal-card ${isActive}" data-cat="${escapeHtml(cat)}" onclick="selectCategory('${escapeHtml(cat)}', null, true)">
          <span class="cat-modal-card-icon">${icon}</span>
          <div class="cat-modal-card-info">
            <div class="cat-modal-card-name">${escapeHtml(cat)}</div>
            <div class="cat-modal-card-count">${count} दर्शन पोस्ट</div>
          </div>
          <span class="cat-modal-check">✓</span>
        </div>
      `;
    });

    modalGrid.innerHTML = modalHtml;
  }

  // Setup scroll listeners for navigation chevrons
  container.addEventListener('scroll', updateRibbonNavButtons, { passive: true });
  setTimeout(updateRibbonNavButtons, 200);
}

// Ribbon Scroll Handler (Smooth left/right scroll)
window.scrollCatRibbon = function(direction) {
  const track = document.getElementById('categoryFilterWrap');
  if (!track) return;
  const amount = (track.clientWidth * 0.65) || 300;
  track.scrollBy({ left: direction * amount, behavior: 'smooth' });
};

// Ribbon Chevrons Visibility Helper
window.updateRibbonNavButtons = function() {
  const track = document.getElementById('categoryFilterWrap');
  const prevBtn = document.getElementById('catNavPrev');
  const nextBtn = document.getElementById('catNavNext');
  if (!track || !prevBtn || !nextBtn) return;

  const atStart = track.scrollLeft <= 5;
  const atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 5;

  prevBtn.disabled = atStart;
  prevBtn.style.opacity = atStart ? '0.2' : '1';
  prevBtn.style.pointerEvents = atStart ? 'none' : 'auto';

  nextBtn.disabled = atEnd;
  nextBtn.style.opacity = atEnd ? '0.2' : '1';
  nextBtn.style.pointerEvents = atEnd ? 'none' : 'auto';
};

// Open All Categories Modal
window.openCategoryModal = function() {
  const modal = document.getElementById('catModalOverlay');
  if (modal) {
    modal.classList.add('open');
    document.body.classList.add('cat-modal-lock');
    const inp = document.getElementById('catModalSearchInput');
    if (inp) {
      inp.value = '';
      filterModalCategories('');
      setTimeout(() => inp.focus(), 150);
    }
  }
};

// Close All Categories Modal
window.closeCategoryModal = function(e) {
  if (e && e.target && e.target.closest('.cat-modal') && !e.target.closest('.cat-modal-close')) {
    return;
  }
  const modal = document.getElementById('catModalOverlay');
  if (modal) {
    modal.classList.remove('open');
    document.body.classList.remove('cat-modal-lock');
  }
};

// Filter Categories in Modal via Live Search
window.filterModalCategories = function(query) {
  const q = (query || '').toLowerCase().trim();
  const cards = document.querySelectorAll('#catModalGrid .cat-modal-card');
  cards.forEach(card => {
    const name = (card.querySelector('.cat-modal-card-name')?.textContent || '').toLowerCase();
    const matches = !q || name.includes(q);
    card.style.display = matches ? 'flex' : 'none';
  });
};

// Unified Category Selection Handler
window.selectCategory = function(cat, pillEl, fromModal = false) {
  activeCategory = cat || 'all';

  // Sync ribbon pills
  document.querySelectorAll('#categoryFilterWrap .cat-pill').forEach(p => {
    if (p.getAttribute('data-cat') === activeCategory) {
      p.classList.add('active');
      p.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    } else {
      p.classList.remove('active');
    }
  });

  // Sync modal cards
  document.querySelectorAll('#catModalGrid .cat-modal-card').forEach(c => {
    if (c.getAttribute('data-cat') === activeCategory) {
      c.classList.add('active');
    } else {
      c.classList.remove('active');
    }
  });

  if (fromModal) {
    closeCategoryModal();
  }

  // Render filtered posts
  renderFilteredPosts(window.KRISHNA_POSTS || []);

  const label = activeCategory === 'all' ? 'सभी दर्शन' : activeCategory;
  showToast(`✨ श्रेणी: ${label}`);
};

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeCategoryModal();
});

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
    el.textContent = updatedStats.shares.toLocaleString('en-IN');
  });

  const detailShares = document.getElementById('dShares');
  if (detailShares) {
    detailShares.textContent = updatedStats.shares.toLocaleString('en-IN');
  }

  const currentUrl = `${window.location.origin}/post/${encodeURIComponent(post.id)}`;
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
    el.textContent = updatedStats.downloads.toLocaleString('en-IN');
  });
  const detailDls = document.getElementById('dDownloads');
  if (detailDls) {
    detailDls.textContent = updatedStats.downloads.toLocaleString('en-IN');
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
function copyQuote(postId) {
  const post = getPostById(postId);
  if (!post) return;

  const textToCopy = `"${post.quote}" — श्री कृष्ण (via krishnavibez.in)`;
  navigator.clipboard.writeText(textToCopy).then(() => {
    showToast('✨ सुविचार कॉपी हो गया!');
  }).catch(() => {
    showToast('⚠️ कॉपी नहीं हो सका');
  });
}

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

// 10. Universal Hash Router & Smooth Feed Scroll
function handleHashScroll() {
  const hash = (window.location.hash || '').toLowerCase();
  if (hash === '#feed') {
    const feed = document.getElementById('feed');
    if (feed) {
      setTimeout(() => {
        feed.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    }
  } else if (hash === '#latest' || hash === '#views' || hash === '#likes' || hash === '#reels') {
    const sortKey = hash.replace('#', '');
    if (typeof handleSortChange === 'function') {
      handleSortChange(sortKey);
    }
    const feed = document.getElementById('feed');
    if (feed) {
      setTimeout(() => {
        feed.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    }
  }
}

window.addEventListener('DOMContentLoaded', handleHashScroll);
window.addEventListener('hashchange', handleHashScroll);

document.addEventListener('click', (e) => {
  const a = e.target.closest('a[href="/#feed"], a[href="#feed"]');
  if (a && (window.location.pathname === '/' || window.location.pathname === '/index.html')) {
    e.preventDefault();
    const feed = document.getElementById('feed');
    if (feed) {
      feed.scrollIntoView({ behavior: 'smooth' });
      history.pushState(null, '', '/#feed');
    }
  }
});

