// content.js - Injected into Treblo AI pages (ISOLATED world)

let bridgeTracks = [];
const allDiscoveredMap = new Map();

// Helper to sanitize filenames
function sanitizeFilename(name) {
  if (!name) return "treblo_track";
  return name.replace(/[\\/:*?"<>|]/g, "_").trim().substring(0, 100);
}

// Listen for messages from page-bridge.js (MAIN world)
window.addEventListener("message", (event) => {
  if (event.data && event.data.type === "TREBLO_BRIDGE_TRACKS") {
    bridgeTracks = event.data.tracks || [];
    bridgeTracks.forEach(t => {
      if (t && t.url) {
        allDiscoveredMap.set(t.url, t);
      }
    });
    console.log(`[Treblo Content] Received ${bridgeTracks.length} tracks from page-bridge.`);
  }
});

// Comprehensive scanner across DOM, Network, Storage, and Bridge
async function scanAllTracks() {
  // 1. Trigger bridge scan in MAIN world
  window.postMessage({ type: "TREBLO_SCAN_NOW" }, "*");
  await new Promise(r => setTimeout(r, 400));

  // 2. Check Performance Resource Timings
  try {
    const resources = performance.getEntriesByType("resource");
    for (const res of resources) {
      const url = res.name;
      if (url.includes("cdn.treblo.com") || url.match(/\.(ogg|mp3|wav)(\?|$)/i)) {
        if (!allDiscoveredMap.has(url)) {
          const filename = url.split("/").pop().split("?")[0];
          allDiscoveredMap.set(url, {
            id: url,
            title: filename.replace(/\.(ogg|mp3|wav)$/i, ""),
            url: url
          });
        }
      }
    }
  } catch (err) {}

  // 3. Scan DOM for audio tags
  const audioElements = document.querySelectorAll("audio, audio source");
  audioElements.forEach((el, index) => {
    const src = el.src || el.getAttribute("src");
    if (src && (src.includes("cdn.treblo.com") || src.match(/\.(ogg|mp3|wav)/i))) {
      if (!allDiscoveredMap.has(src)) {
        allDiscoveredMap.set(src, {
          id: src,
          title: `Track_${index + 1}`,
          url: src
        });
      }
    }
  });

  // 4. Scan DOM for download or media links
  const links = document.querySelectorAll('a[href*=".ogg"], a[href*=".mp3"], a[href*="cdn.treblo.com"]');
  links.forEach((a, index) => {
    const href = a.href;
    if (href && !allDiscoveredMap.has(href)) {
      const title = a.innerText.trim() || a.getAttribute("download") || `Track_${index + 1}`;
      allDiscoveredMap.set(href, {
        id: href,
        title: sanitizeFilename(title),
        url: href
      });
    }
  });

  // Extract project ID from URL if present
  let projectId = null;
  const match = window.location.pathname.match(/\/editor\/([a-zA-Z0-9-]+)/);
  if (match) {
    projectId = match[1];
  }

  const trackList = Array.from(allDiscoveredMap.values());
  return {
    tracks: trackList,
    count: trackList.length,
    projectId: projectId,
    currentUrl: window.location.href
  };
}

// Listen for messages from popup.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "SCAN_TRACKS") {
    scanAllTracks().then(result => {
      sendResponse({ success: true, ...result });
    }).catch(err => {
      sendResponse({ success: false, error: err.message });
    });
    return true; // async
  }

  if (request.action === "IMPORT_JSON") {
    try {
      const data = typeof request.json === "string" ? JSON.parse(request.json) : request.json;
      let added = 0;

      // Extract entities.tracks
      if (data.entities && data.entities.tracks) {
        Object.values(data.entities.tracks).forEach(item => {
          const url = item.songPath || item.audioUrl || (item.generationId ? `https://cdn.treblo.com/generations3/audio_${item.generationId}_${item.index || 0}.ogg` : null);
          if (url) {
            allDiscoveredMap.set(url, {
              id: item.id || url,
              title: sanitizeFilename(item.title || "Track"),
              url: url
            });
            added++;
          }
        });
      }

      sendResponse({ success: true, count: allDiscoveredMap.size, added: added, tracks: Array.from(allDiscoveredMap.values()) });
    } catch (e) {
      sendResponse({ success: false, error: e.message });
    }
    return true;
  }
});
