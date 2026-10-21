/**
 * KRISHNA VIBEZ - Mobile Navigation Engine (mobile-nav.js)
 * Provides seamless mobile drawer navigation, hamburger menu, and app-like sticky bottom nav bar.
 */

(function () {
  'use strict';

  // Toggle drawer state
  window.toggleMobileNav = function (e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    const drawer = document.getElementById('mobileDrawer');
    const overlay = document.getElementById('mobileDrawerOverlay');
    const hamburger = document.getElementById('mobileMenuBtn');
    const isOpen = drawer && drawer.classList.contains('open');

    if (isOpen) {
      closeMobileNav();
    } else {
      openMobileNav();
    }
  };

  window.openMobileNav = function () {
    const drawer = document.getElementById('mobileDrawer');
    const overlay = document.getElementById('mobileDrawerOverlay');
    const hamburger = document.getElementById('mobileMenuBtn');

    if (drawer) drawer.classList.add('open');
    if (overlay) overlay.classList.add('open');
    if (hamburger) hamburger.classList.add('active');
    document.body.classList.add('mobile-nav-lock');
  };

  window.closeMobileNav = function (e) {
    if (e && e.stopPropagation) e.stopPropagation();
    const drawer = document.getElementById('mobileDrawer');
    const overlay = document.getElementById('mobileDrawerOverlay');
    const hamburger = document.getElementById('mobileMenuBtn');

    if (drawer) drawer.classList.remove('open');
    if (overlay) overlay.classList.remove('open');
    if (hamburger) hamburger.classList.remove('active');
    document.body.classList.remove('mobile-nav-lock');
  };

  // Build and inject HTML components if missing
  function initMobileNav() {
    const currentPath = window.location.pathname.toLowerCase();
    const currentHash = window.location.hash.toLowerCase();

    // 1. Ensure Hamburger Button in Top Navbar
    const navContainer = document.querySelector('.navbar .nav-container');
    if (navContainer && !document.getElementById('mobileMenuBtn')) {
      const navActions = navContainer.querySelector('.nav-actions');
      const btn = document.createElement('button');
      btn.id = 'mobileMenuBtn';
      btn.className = 'mobile-menu-btn';
      btn.setAttribute('aria-label', 'मेनू खोलें (Open Menu)');
      btn.innerHTML = `
        <span class="bar bar-1"></span>
        <span class="bar bar-2"></span>
        <span class="bar bar-3"></span>
      `;
      btn.addEventListener('click', window.toggleMobileNav);

      if (navActions) {
        navActions.appendChild(btn);
      } else {
        navContainer.appendChild(btn);
      }
    }

    // 2. Ensure Mobile Drawer Overlay & Drawer in Body
    if (!document.getElementById('mobileDrawer')) {
      const overlay = document.createElement('div');
      overlay.id = 'mobileDrawerOverlay';
      overlay.className = 'mobile-drawer-overlay';
      overlay.addEventListener('click', window.closeMobileNav);

      const drawer = document.createElement('div');
      drawer.id = 'mobileDrawer';
      drawer.className = 'mobile-drawer';
      drawer.innerHTML = `
        <div class="drawer-header">
          <a href="index.html" class="drawer-brand" onclick="closeMobileNav()">
            <img src="assets/logo.png" alt="Krishna Vibez" class="drawer-logo">
            <div class="drawer-brand-text">
              <span class="drawer-brand-name">KRISHNA VIBEZ</span>
              <span class="drawer-brand-sub">दैनिक दिव्य दर्शन</span>
            </div>
          </a>
          <button class="drawer-close-btn" onclick="closeMobileNav()" aria-label="बंद करें">✕</button>
        </div>

        <div class="drawer-body">
          <div class="drawer-nav-group">
            <div class="drawer-group-title">मुख्य मेनू</div>
            <a href="index.html" class="drawer-nav-link ${currentPath.endsWith('index.html') || currentPath === '/' || currentPath.endsWith('/') ? 'active' : ''}" onclick="closeMobileNav()">
              <span class="nav-ico">🏠</span>
              <span class="nav-txt">मुख्य पृष्ठ (Home)</span>
            </a>
            <a href="articles.html" class="drawer-nav-link ${currentPath.includes('article') ? 'active' : ''}" onclick="closeMobileNav()">
              <span class="nav-ico">📖</span>
              <span class="nav-txt">विशेष आध्यात्मिक लेख</span>
              <span class="nav-badge">नया</span>
            </a>
            <a href="index.html#feed" class="drawer-nav-link" onclick="closeMobileNav()">
              <span class="nav-ico">🪷</span>
              <span class="nav-txt">दैनिक दिव्य दर्शन</span>
            </a>
            <a href="about.html" class="drawer-nav-link ${currentPath.includes('about') ? 'active' : ''}" onclick="closeMobileNav()">
              <span class="nav-ico">🕉️</span>
              <span class="nav-txt">हमारे बारे में (About Us)</span>
            </a>
            <a href="contact.html" class="drawer-nav-link ${currentPath.includes('contact') ? 'active' : ''}" onclick="closeMobileNav()">
              <span class="nav-ico">✉️</span>
              <span class="nav-txt">संपर्क करें (Contact)</span>
            </a>
          </div>

          <div class="drawer-divider"></div>

          <div class="drawer-nav-group">
            <div class="drawer-group-title">कानूनी नीतियां (Policies)</div>
            <a href="privacy-policy.html" class="drawer-nav-link sub ${currentPath.includes('privacy') ? 'active' : ''}" onclick="closeMobileNav()">
              <span class="nav-ico">🛡️</span>
              <span class="nav-txt">गोपनीयता नीति (Privacy Policy)</span>
            </a>
            <a href="terms.html" class="drawer-nav-link sub ${currentPath.includes('terms') ? 'active' : ''}" onclick="closeMobileNav()">
              <span class="nav-ico">⚖️</span>
              <span class="nav-txt">नियम एवं शर्तें (Terms)</span>
            </a>
            <a href="disclaimer.html" class="drawer-nav-link sub ${currentPath.includes('disclaimer') ? 'active' : ''}" onclick="closeMobileNav()">
              <span class="nav-ico">⚠️</span>
              <span class="nav-txt">अस्वीकरण (Disclaimer)</span>
            </a>
          </div>

          <div class="drawer-divider"></div>

          <div class="drawer-social-section">
            <div class="drawer-group-title">✨ सोशल मीडिया पर जुड़ें</div>
            <div class="drawer-social-grid">
              <a href="https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J" target="_blank" rel="noopener noreferrer" class="d-soc-btn whatsapp">
                <span>WhatsApp</span>
              </a>
              <a href="https://t.me/krishnavibezz" target="_blank" rel="noopener noreferrer" class="d-soc-btn telegram">
                <span>Telegram</span>
              </a>
              <a href="https://www.instagram.com/pareshpadsala_/" target="_blank" rel="noopener noreferrer" class="d-soc-btn instagram">
                <span>Instagram</span>
              </a>
              <a href="https://www.facebook.com/1808917602588221" target="_blank" rel="noopener noreferrer" class="d-soc-btn facebook">
                <span>Facebook</span>
              </a>
              <a href="https://in.pinterest.com/MojiloMart/" target="_blank" rel="noopener noreferrer" class="d-soc-btn pinterest">
                <span>Pinterest</span>
              </a>
            </div>
          </div>
        </div>
      `;

      document.body.appendChild(overlay);
      document.body.appendChild(drawer);
    }

    // 3. Ensure App-Style Sticky Bottom Nav Bar
    if (!document.getElementById('mobileBottomNav')) {
      const bottomNav = document.createElement('nav');
      bottomNav.id = 'mobileBottomNav';
      bottomNav.className = 'mobile-bottom-nav';

      const isHome = currentPath.endsWith('index.html') || currentPath === '/' || currentPath.endsWith('/');
      const isArticles = currentPath.includes('article');

      bottomNav.innerHTML = `
        <a href="index.html" class="b-nav-item ${isHome && !window.location.hash.includes('feed') ? 'active' : ''}" id="bNavHome">
          <span class="b-nav-icon">🏠</span>
          <span class="b-nav-label">होम</span>
        </a>
        <a href="articles.html" class="b-nav-item ${isArticles ? 'active' : ''}" id="bNavArticles">
          <span class="b-nav-icon">📖</span>
          <span class="b-nav-label">ज्ञान लेख</span>
        </a>
        <a href="index.html#feed" class="b-nav-item ${window.location.hash.includes('feed') ? 'active' : ''}" id="bNavFeed">
          <span class="b-nav-icon">🪷</span>
          <span class="b-nav-label">दर्शन</span>
        </a>
        <a href="https://whatsapp.com/channel/0029VbDxJHk30LKNtj4Er62J" target="_blank" rel="noopener noreferrer" class="b-nav-item b-nav-wa" id="bNavWa" title="WhatsApp Channel">
          <span class="b-nav-icon">💬</span>
          <span class="b-nav-label">WhatsApp</span>
        </a>
        <button type="button" class="b-nav-item b-nav-menu-btn" onclick="toggleMobileNav(event)" id="bNavMenu">
          <span class="b-nav-icon">☰</span>
          <span class="b-nav-label">मेनू</span>
        </button>
      `;

      document.body.appendChild(bottomNav);
    }

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        closeMobileNav();
      }
    });
  }

  // Auto initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileNav);
  } else {
    initMobileNav();
  }
})();
