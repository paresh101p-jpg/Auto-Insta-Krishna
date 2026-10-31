// background.js - Service worker to run downloads persistently in background
// Keeps downloading even if popup closes, another tab is active, or browser is minimized.

let downloadQueue = [];
let isDownloading = false;
let currentProgress = {
  active: false,
  total: 0,
  current: 0,
  downloaded: 0,
  failed: 0,
  currentTitle: "",
  isWav: false,
  status: "idle",
  error: null
};

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

function getCleanTitle(title, index) {
  let clean = (title || `Track_${index + 1}`).replace(/[\\/:*?"<>|]/g, "_").trim();
  clean = clean.replace(/\.(ogg|mp3|wav)$/i, "");
  return clean || `Track_${index + 1}`;
}

// Ensure offscreen document exists for WAV audio conversion
async function ensureOffscreenDocument() {
  const existingContexts = await chrome.runtime.getContexts({
    contextTypes: ["OFFSCREEN_DOCUMENT"]
  });
  if (existingContexts.length > 0) {
    return;
  }

  await chrome.offscreen.createDocument({
    url: "offscreen.html",
    reasons: ["AUDIO_PLAYBACK", "BLOBS"],
    justification: "Convert audio formats to 16-bit PCM WAV in background"
  });
}

async function closeOffscreenDocument() {
  const existingContexts = await chrome.runtime.getContexts({
    contextTypes: ["OFFSCREEN_DOCUMENT"]
  });
  if (existingContexts.length > 0) {
    await chrome.offscreen.closeDocument();
  }
}

// Broadcast status to popup or storage
function updateStatus(patch) {
  Object.assign(currentProgress, patch);
  chrome.storage.local.set({ treblo_download_progress: currentProgress });
  chrome.runtime.sendMessage({ action: "DOWNLOAD_PROGRESS_UPDATE", progress: currentProgress }).catch(() => {
    // Popup might be closed, which is totally normal!
  });
}

// Process the download queue
async function processQueue() {
  if (isDownloading) return;
  isDownloading = true;

  const total = downloadQueue.length;
  let downloadedCount = 0;
  let failedCount = 0;
  const isWav = currentProgress.isWav;

  updateStatus({
    active: true,
    total: total,
    current: 0,
    downloaded: 0,
    failed: 0,
    status: "downloading"
  });

  if (isWav) {
    try {
      await ensureOffscreenDocument();
    } catch (e) {
      console.warn("Offscreen creation notice:", e);
    }
  }

  for (let i = 0; i < total; i++) {
    const track = downloadQueue[i];
    const cleanTitle = getCleanTitle(track.title, i);

    updateStatus({
      current: i + 1,
      currentTitle: track.title
    });

    try {
      if (isWav) {
        // Request offscreen document to fetch & convert to WAV blob URL
        const convertRes = await chrome.runtime.sendMessage({
          action: "CONVERT_TO_WAV_BLOB_URL",
          url: track.url
        });

        if (!convertRes || !convertRes.success || !convertRes.blobUrl) {
          throw new Error(convertRes ? convertRes.error : "Conversion failed");
        }

        const blobUrl = convertRes.blobUrl;
        const destPath = `Treblo_Music/${cleanTitle}.wav`;

        await new Promise((resolve) => {
          chrome.downloads.download({
            url: blobUrl,
            filename: destPath,
            conflictAction: "uniquify",
            saveAs: false
          }, (downloadId) => {
            setTimeout(() => {
              chrome.runtime.sendMessage({ action: "REVOKE_BLOB_URL", blobUrl }).catch(() => {});
            }, 20000);

            if (chrome.runtime.lastError || !downloadId) {
              failedCount++;
            } else {
              downloadedCount++;
            }
            resolve();
          });
        });

      } else {
        // Fast direct OGG download
        const destPath = `Treblo_Music/${cleanTitle}.ogg`;

        await new Promise((resolve) => {
          chrome.downloads.download({
            url: track.url,
            filename: destPath,
            conflictAction: "uniquify",
            saveAs: false
          }, (downloadId) => {
            if (chrome.runtime.lastError || !downloadId) {
              failedCount++;
            } else {
              downloadedCount++;
            }
            resolve();
          });
        });
      }

    } catch (err) {
      console.warn(`Download error on ${track.title}:`, err);
      failedCount++;
    }

    updateStatus({
      downloaded: downloadedCount,
      failed: failedCount
    });

    // Gentle pacing (1.1s)
    if (i < total - 1) {
      await sleep(1100);
    }
  }

  isDownloading = false;
  downloadQueue = [];

  if (isWav) {
    try {
      await closeOffscreenDocument();
    } catch (e) {}
  }

  updateStatus({
    active: false,
    status: "completed",
    current: total,
    downloaded: downloadedCount,
    failed: failedCount
  });

  // Notify user via Chrome notification when batch finishes
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icons/icon128.png",
    title: "Treblo Music Downloader",
    message: `✅ Complete! ${downloadedCount} tracks have been downloaded to Treblo_Music/ folder.`,
    priority: 2
  });
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "START_DOWNLOAD_ALL") {
    if (isDownloading) {
      sendResponse({ success: false, error: "Download already in progress in background." });
      return false;
    }

    downloadQueue = request.tracks || [];
    currentProgress.isWav = !!request.isWav;

    if (downloadQueue.length === 0) {
      sendResponse({ success: false, error: "No tracks to download." });
      return false;
    }

    // Start background download loop
    processQueue();
    sendResponse({ success: true, count: downloadQueue.length });
    return false;
  }

  if (request.action === "GET_DOWNLOAD_STATUS") {
    sendResponse({ progress: currentProgress, isDownloading });
    return false;
  }
});

