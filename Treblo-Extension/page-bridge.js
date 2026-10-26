// page-bridge.js - Runs in MAIN world context (direct access to React & Treblo state)

(function() {
  console.log("[Treblo Bridge] Initialized in MAIN world context.");

  const capturedTracks = new Map();
  const sessionFetchTracks = new Map();

  function getActiveProjectId() {
    const match = window.location.pathname.match(/\/editor\/([a-zA-Z0-9-]+)/);
    return match ? match[1] : null;
  }

  function parseTrackObject(obj) {
    if (!obj || typeof obj !== "object") return null;

    // Filter out deleted tracks
    if (obj.isDeleted || obj.deleted || obj.status === "DELETED") return null;

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
      projectId: obj.projectId || obj.project_id || null,
      duration: obj.duration || null,
      status: obj.status || "SUCCESS"
    };
  }

  // Helper to extract tracks from any object
  function extractTracksGeneric(data, targetMap) {
    if (!data || typeof data !== "object") return;
    const activeProject = getActiveProjectId();

    function deep(obj, depth = 0) {
      if (!obj || depth > 6) return;
      if (typeof obj !== "object") return;

      if (obj.songPath || obj.generationId || (obj.audioUrl && typeof obj.audioUrl === "string")) {
        const t = parseTrackObject(obj);
        if (t && (!activeProject || !t.projectId || t.projectId === activeProject)) {
          if (!targetMap.has(t.url)) {
            targetMap.set(t.url, t);
          }
        }
      }

      if (Array.isArray(obj)) {
        obj.forEach(x => deep(x, depth + 1));
      } else {
        Object.values(obj).forEach(x => deep(x, depth + 1));
      }
    }

    deep(data);
  }

  // Priority 1: Scan DOM React Fibers of currently visible track cards on screen
  function scanDomReactFibers() {
    const found = new Map();
    try {
      const elements = document.querySelectorAll('button, [role="row"], [role="listitem"], div[class*="track"], div[class*="item"], div[class*="row"], div[class*="card"], li, div');
      for (const el of elements) {
        const fiberKey = Object.keys(el).find(k => k.startsWith("__reactFiber"));
        if (!fiberKey) continue;

        let fiber = el[fiberKey];
        let depth = 0;
        while (fiber && depth < 8) {
          const props = fiber.memoizedProps;
          if (props && typeof props === "object") {
            const candidates = [props.track, props.song, props.item, props.generation, props.data, props.entity];
            for (const cand of candidates) {
              if (cand && typeof cand === "object") {
                if (cand.songPath || cand.generationId || cand.audioUrl) {
                  const t = parseTrackObject(cand);
                  if (t && !found.has(t.url)) {
                    found.set(t.url, t);
                  }
                }
              }
            }
          }
          fiber = fiber.return;
          depth++;
        }
      }
    } catch (e) {
      console.warn("[Treblo Bridge] DOM fiber scan error:", e);
    }
    return found;
  }

  // Priority 2: Scan Storage STRICTLY for the active project
  function scanStorageForProject() {
    const activeProjectId = getActiveProjectId();
    const found = new Map();

    try {
      [localStorage, sessionStorage].forEach(store => {
        for (let i = 0; i < store.length; i++) {
          const key = store.key(i);
          const val = store.getItem(key);
          if (!val || (!val.includes("songPath") && !val.includes("audio_") && !val.includes("cdn.treblo.com"))) continue;

          try {
            const data = JSON.parse(val);

            // A. Check entities.projects[activeProjectId]
            if (activeProjectId && data.entities && data.entities.projects && data.entities.projects[activeProjectId]) {
              const proj = data.entities.projects[activeProjectId];
              const tIds = proj.tracks || proj.trackIds || proj.items;
              if (Array.isArray(tIds) && data.entities.tracks) {
                tIds.forEach(id => {
                  const item = data.entities.tracks[id] || (typeof id === "object" ? id : null);
                  if (item) {
                    const t = parseTrackObject(item);
                    if (t && !found.has(t.url)) found.set(t.url, t);
                  }
                });
                if (found.size > 0) return found;
              }
            }

            // B. Check if data is project object itself
            if (activeProjectId && (data.id === activeProjectId || data.projectId === activeProjectId)) {
              extractTracksGeneric(data, found);
              if (found.size > 0) return found;
            }

            // C. Filter by projectId on items
            if (activeProjectId && data.entities && data.entities.tracks) {
              Object.values(data.entities.tracks).forEach(item => {
                if (item && (item.projectId === activeProjectId || item.project_id === activeProjectId)) {
                  const t = parseTrackObject(item);
                  if (t && !found.has(t.url)) found.set(t.url, t);
                }
              });
              if (found.size > 0) return found;
            }

          } catch (e) {}
        }
      });
    } catch (e) {}
    return found;
  }

  // 1. Monkey-patch window.fetch to capture live network API responses
  const originalFetch = window.fetch;
  window.fetch = async function(...args) {
    const response = await originalFetch.apply(this, args);
    try {
      const clone = response.clone();
      clone.json().then(data => {
        extractTracksGeneric(data, sessionFetchTracks);
        // Also update capturedTracks if matching project
        sessionFetchTracks.forEach((t, url) => {
          capturedTracks.set(url, t);
        });
        notifyContentScript();
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
          extractTracksGeneric(data, sessionFetchTracks);
          sessionFetchTracks.forEach((t, url) => {
            capturedTracks.set(url, t);
          });
          notifyContentScript();
        }
      } catch (e) {}
    });
    return origSend.apply(this, arguments);
  };

  function notifyContentScript() {
    const list = Array.from(capturedTracks.values());
    window.postMessage({
      type: "TREBLO_BRIDGE_TRACKS",
      tracks: list,
      count: list.length
    }, "*");
  }

  function doFullScan() {
    capturedTracks.clear();

    // 1. Try DOM React Fibers of currently visible track cards
    const domMap = scanDomReactFibers();
    if (domMap.size > 0) {
      console.log(`[Treblo Bridge] Found ${domMap.size} tracks from DOM cards.`);
      domMap.forEach((t, url) => capturedTracks.set(url, t));
    }

    // 2. Try Storage strictly for active project
    if (capturedTracks.size === 0) {
      const storageMap = scanStorageForProject();
      if (storageMap.size > 0) {
        console.log(`[Treblo Bridge] Found ${storageMap.size} tracks from Project Storage.`);
        storageMap.forEach((t, url) => capturedTracks.set(url, t));
      }
    }

    // 3. Try session network fetches
    if (capturedTracks.size === 0 && sessionFetchTracks.size > 0) {
      console.log(`[Treblo Bridge] Found ${sessionFetchTracks.size} tracks from live session API.`);
      sessionFetchTracks.forEach((t, url) => capturedTracks.set(url, t));
    }

    // 4. Fallback: If still 0, extract all tracks from storage as last resort
    if (capturedTracks.size === 0) {
      console.log("[Treblo Bridge] Fallback storage scan...");
      try {
        [localStorage, sessionStorage].forEach(store => {
          for (let i = 0; i < store.length; i++) {
            const val = store.getItem(store.key(i));
            if (val && (val.includes("songPath") || val.includes("audio_"))) {
              try { extractTracksGeneric(JSON.parse(val), capturedTracks); } catch (e) {}
            }
          }
        });
      } catch (e) {}
    }

    notifyContentScript();
  }

  // Listen for scan & reset requests from content.js
  window.addEventListener("message", (event) => {
    if (event.data && event.data.type === "TREBLO_SCAN_NOW") {
      doFullScan();
    } else if (event.data && event.data.type === "TREBLO_RESET_CACHE") {
      capturedTracks.clear();
      sessionFetchTracks.clear();
      notifyContentScript();
    }
  });

  // Initial scan after page load
  setTimeout(() => {
    doFullScan();
  }, 1000);

})();
