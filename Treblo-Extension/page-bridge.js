// page-bridge.js - Runs in MAIN world context (direct access to React & Treblo state)

(function() {
  console.log("[Treblo Bridge] Initialized in MAIN world context.");

  const capturedTracks = new Map();

  function getActiveProjectId() {
    const match = window.location.pathname.match(/\/editor\/([a-zA-Z0-9-]+)/);
    return match ? match[1] : null;
  }

  function parseTrackObject(obj) {
    if (!obj || typeof obj !== "object") return null;

    // Filter out deleted tracks
    if (obj.isDeleted || obj.deleted || obj.status === "DELETED") return null;

    // Filter by project ID if present
    const activeProject = getActiveProjectId();
    if (activeProject && obj.projectId && obj.projectId !== activeProject) {
      return null;
    }

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
      projectId: obj.projectId || null,
      duration: obj.duration || null,
      status: obj.status || "SUCCESS"
    };
  }

  function extractTracksFromData(data, source) {
    if (!data) return;
    const activeProject = getActiveProjectId();

    try {
      // 1. Structure: { entities: { tracks: { [id]: trackObj } } }
      if (data.entities && data.entities.tracks) {
        Object.values(data.entities.tracks).forEach(item => {
          if (activeProject && item.projectId && item.projectId !== activeProject) return;
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
          if (activeProject && item.projectId && item.projectId !== activeProject) return;
          const t = parseTrackObject(item);
          if (t && !capturedTracks.has(t.url)) {
            capturedTracks.set(t.url, t);
          }
        });
      }

      // 3. Scan for any generation objects matching current active project
      if (typeof data === "object") {
        function deepScan(obj, depth = 0) {
          if (!obj || depth > 5) return;
          if (typeof obj !== "object") return;

          if (obj.songPath || obj.generationId) {
            if (!activeProject || !obj.projectId || obj.projectId === activeProject) {
              const t = parseTrackObject(obj);
              if (t && !capturedTracks.has(t.url)) {
                capturedTracks.set(t.url, t);
              }
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

  // 1. Monkey-patch window.fetch to capture active project network API responses
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

  // 3. Scan React Fiber tree of active page
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

        if (fiber.memoizedProps) {
          extractTracksFromData(fiber.memoizedProps, "fiberProps");
        }
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

  function notifyContentScript() {
    const list = Array.from(capturedTracks.values());
    window.postMessage({
      type: "TREBLO_BRIDGE_TRACKS",
      tracks: list,
      count: list.length
    }, "*");
  }

  // Listen for scan & reset requests from content.js
  window.addEventListener("message", (event) => {
    if (event.data && event.data.type === "TREBLO_SCAN_NOW") {
      capturedTracks.clear(); // Always start fresh on scan
      scanReactFibers();
      notifyContentScript();
    } else if (event.data && event.data.type === "TREBLO_RESET_CACHE") {
      capturedTracks.clear();
      notifyContentScript();
    }
  });

  // Initial scan after page load
  setTimeout(() => {
    scanReactFibers();
    notifyContentScript();
  }, 1000);

})();
