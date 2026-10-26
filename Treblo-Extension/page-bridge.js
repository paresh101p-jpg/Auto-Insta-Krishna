// page-bridge.js - Runs in MAIN world context (direct access to React & Treblo state)

(function() {
  console.log("[Treblo Bridge] Initialized in MAIN world context.");

  const capturedTracks = new Map();

  function parseTrackObject(obj) {
    if (!obj || typeof obj !== "object") return null;

    // Check for songPath or audioUrl or generationId
    const songPath = obj.songPath || obj.audioUrl || obj.audio_url || obj.url;
    let finalUrl = songPath;

    // If no direct songPath but generationId exists
    if (!finalUrl && obj.generationId) {
      const idx = typeof obj.index === "number" ? obj.index : 0;
      finalUrl = `https://cdn.treblo.com/generations3/audio_${obj.generationId}_${idx}.ogg`;
    }

    if (!finalUrl || typeof finalUrl !== "string") return null;
    if (!finalUrl.includes("cdn.treblo.com") && !finalUrl.match(/\.(ogg|mp3|wav)/i)) return null;

    const title = obj.title || obj.name || `Treblo_${obj.generationId || "Track"}`;
    const id = obj.id || obj.generationId || finalUrl;

    return {
      id: id,
      title: title,
      url: finalUrl,
      duration: obj.duration || null,
      status: obj.status || "SUCCESS"
    };
  }

  function extractTracksFromData(data, source) {
    if (!data) return;

    try {
      // 1. Structure: { entities: { tracks: { [id]: trackObj } } }
      if (data.entities && data.entities.tracks) {
        Object.values(data.entities.tracks).forEach(item => {
          const t = parseTrackObject(item);
          if (t && !capturedTracks.has(t.url)) {
            capturedTracks.set(t.url, t);
          }
        });
      }

      // 2. Structure: { data: { tracks: [...] } } or { tracks: [...] }
      const trackList = (data.data && (data.data.tracks || data.data.items)) || data.tracks || data.items;
      if (Array.isArray(trackList)) {
        trackList.forEach(item => {
          const t = parseTrackObject(item);
          if (t && !capturedTracks.has(t.url)) {
            capturedTracks.set(t.url, t);
          }
        });
      }

      // 3. Recursive search for any track objects in deeply nested json
      if (typeof data === "object") {
        function deepScan(obj, depth = 0) {
          if (!obj || depth > 5) return;
          if (typeof obj !== "object") return;

          if (obj.songPath || obj.generationId) {
            const t = parseTrackObject(obj);
            if (t && !capturedTracks.has(t.url)) {
              capturedTracks.set(t.url, t);
            }
          }

          if (Array.isArray(obj)) {
            obj.forEach(item => deepScan(item, depth + 1));
          } else {
            Object.values(obj).forEach(val => deepScan(val, depth + 1));
          }
        }
        deepScan(data);
      }

      notifyContentScript();
    } catch (e) {
      console.warn("[Treblo Bridge] Parse error:", e);
    }
  }

  // 1. Monkey-patch window.fetch to capture all network API responses
  const originalFetch = window.fetch;
  window.fetch = async function(...args) {
    const response = await originalFetch.apply(this, args);
    try {
      const url = typeof args[0] === "string" ? args[0] : (args[0] && args[0].url);
      const clone = response.clone();
      clone.json().then(data => {
        extractTracksFromData(data, url || "fetch");
      }).catch(() => {});
    } catch (e) {}
    return response;
  };

  // 2. Monkey-patch XMLHttpRequest
  const origOpen = XMLHttpRequest.prototype.open;
  const origSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function(method, url) {
    this._url = url;
    return origOpen.apply(this, arguments);
  };
  XMLHttpRequest.prototype.send = function() {
    this.addEventListener("load", function() {
      try {
        if (this.responseText && (this.responseText.includes("songPath") || this.responseText.includes("audio_"))) {
          const data = JSON.parse(this.responseText);
          extractTracksFromData(data, this._url || "xhr");
        }
      } catch (e) {}
    });
    return origSend.apply(this, arguments);
  };

  // 3. Scan React Fiber tree
  function scanReactFibers() {
    try {
      const rootEl = document.querySelector("#root, #__next, body > div");
      if (!rootEl) return;

      const fiberKey = Object.keys(rootEl).find(k => k.startsWith("__reactFiber") || k.startsWith("__reactContainer"));
      if (!fiberKey) return;

      const visited = new Set();
      function walkFiber(fiber, depth = 0) {
        if (!fiber || depth > 40 || visited.has(fiber)) return;
        visited.add(fiber);

        // Check memoizedProps
        if (fiber.memoizedProps) {
          extractTracksFromData(fiber.memoizedProps, "fiberProps");
        }
        // Check memoizedState
        if (fiber.memoizedState) {
          extractTracksFromData(fiber.memoizedState, "fiberState");
        }

        if (fiber.child) walkFiber(fiber.child, depth + 1);
        if (fiber.sibling) walkFiber(fiber.sibling, depth + 1);
      }

      walkFiber(rootEl[fiberKey]);
    } catch (err) {
      console.warn("[Treblo Bridge] Fiber scan err:", err);
    }
  }

  // 4. Scan LocalStorage & SessionStorage
  function scanStorage() {
    try {
      [localStorage, sessionStorage].forEach(store => {
        for (let i = 0; i < store.length; i++) {
          const key = store.key(i);
          const val = store.getItem(key);
          if (val && (val.includes("songPath") || val.includes("audio_") || val.includes("cdn.treblo.com"))) {
            try {
              const parsed = JSON.parse(val);
              extractTracksFromData(parsed, `storage_${key}`);
            } catch (e) {}
          }
        }
      });
    } catch (e) {}
  }

  function notifyContentScript() {
    const list = Array.from(capturedTracks.values());
    window.postMessage({
      type: "TREBLO_BRIDGE_TRACKS",
      tracks: list,
      count: list.length
    }, "*");
  }

  // Listen for scan requests from content.js
  window.addEventListener("message", (event) => {
    if (event.data && event.data.type === "TREBLO_SCAN_NOW") {
      scanStorage();
      scanReactFibers();
      notifyContentScript();
    }
  });

  // Initial scan after delay
  setTimeout(() => {
    scanStorage();
    scanReactFibers();
    notifyContentScript();
  }, 1000);

})();
