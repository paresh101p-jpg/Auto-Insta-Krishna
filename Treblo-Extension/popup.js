// popup.js - Controller for Treblo Downloader Popup with Background Downloader

let currentTracks = [];
let activeTabId = null;

// DOM Elements
const statusBadge = document.getElementById("statusBadge");
const trackCountEl = document.getElementById("trackCount");
const summaryNote = document.getElementById("summaryNote");
const projectIdRow = document.getElementById("projectIdRow");
const projectIdText = document.getElementById("projectIdText");

const fmtWav = document.getElementById("fmtWav");
const fmtOgg = document.getElementById("fmtOgg");

const btnDownloadAll = document.getElementById("btnDownloadAll");
const btnCountBadge = document.getElementById("btnCountBadge");
const btnDeleteList = document.getElementById("btnDeleteList");
const btnReloadTab = document.getElementById("btnReloadTab");
const btnCopyLinks = document.getElementById("btnCopyLinks");
const btnToggleImport = document.getElementById("btnToggleImport");
const importBox = document.getElementById("importBox");
const jsonInput = document.getElementById("jsonInput");
const btnImportJsonSubmit = document.getElementById("btnImportJsonSubmit");

const trackListEl = document.getElementById("trackList");
const listCounter = document.getElementById("listCounter");

const progressContainer = document.getElementById("progressContainer");
const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");

const deleteModal = document.getElementById("deleteModal");
const modalTrackCount = document.getElementById("modalTrackCount");
const btnConfirmClearLocal = document.getElementById("btnConfirmClearLocal");
const btnCancelModal = document.getElementById("btnCancelModal");

// Sleep helper
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Update UI based on background progress
function updateProgressUI(progress) {
  if (!progress) return;

  if (progress.active || progress.status === "downloading") {
    progressContainer.classList.remove("hidden");
    btnDownloadAll.disabled = true;
    btnReloadTab.disabled = true;

    const total = progress.total || 1;
    const current = progress.current || 0;
    const percent = Math.min(100, Math.round((current / total) * 100));

    progressBar.style.width = `${percent}%`;
    const formatLabel = progress.isWav ? "WAV" : "OGG";
    progressText.innerHTML = `⏳ [${current}/${total}] Downloading & Converting ${formatLabel}: <strong>${progress.currentTitle || "Track"}</strong>... <br><small style="color:#38bdf8;">(Aap dusra tab use kar sakte hain ya browser minimize kar sakte hain)</small>`;
  } else if (progress.status === "completed") {
    progressContainer.classList.remove("hidden");
    progressBar.style.width = "100%";
    btnDownloadAll.disabled = false;
    btnReloadTab.disabled = false;
    const formatLabel = progress.isWav ? "WAV" : "OGG";
    progressText.innerHTML = `✅ <strong>Completed!</strong> ${progress.downloaded} ${formatLabel} tracks downloaded (${progress.failed} failed).<br><small style="color:#94a3b8;">Downloads/Treblo_Music/ folder me saved hain.</small>`;
  } else {
    // idle
    btnDownloadAll.disabled = currentTracks.length === 0;
    btnReloadTab.disabled = false;
  }
}

// Listen for real-time progress updates from background.js
chrome.runtime.onMessage.addListener((request) => {
  if (request.action === "DOWNLOAD_PROGRESS_UPDATE" && request.progress) {
    updateProgressUI(request.progress);
  }
});

// Update Download Button Label based on format radio
function updateDownloadButtonLabel() {
  const isWav = fmtWav && fmtWav.checked;
  const titleSpan = btnDownloadAll.querySelector(".btn-title");
  if (titleSpan) {
    titleSpan.textContent = isWav ? "Download All (.WAV)" : "Download All (.OGG)";
  }
}

if (fmtWav && fmtOgg) {
  fmtWav.addEventListener("change", updateDownloadButtonLabel);
  fmtOgg.addEventListener("change", updateDownloadButtonLabel);
}

// Render Track List
function renderTrackList(tracks) {
  currentTracks = tracks || [];
  const count = currentTracks.length;
  
  trackCountEl.textContent = count;
  btnCountBadge.textContent = count;
  listCounter.textContent = `${count} items`;

  if (count === 0) {
    trackListEl.innerHTML = `
      <div class="empty-state">
        No tracks detected yet.<br>
        <span style="color:#38bdf8; font-weight:600;">👉 Click "Reload & Scan" button above</span><br>
        <small style="color:#94a3b8;">Page reload hote hi sabhi tracks apne aap load ho jayenge.</small>
      </div>
    `;
    btnDownloadAll.disabled = true;
    btnDeleteList.disabled = true;
    btnCopyLinks.disabled = true;
    summaryNote.textContent = "0 tracks detected on current page.";
    return;
  }

  summaryNote.innerHTML = `✅ <strong>${count} songs</strong> ready for download!`;
  btnDownloadAll.disabled = false;
  btnDeleteList.disabled = false;
  btnCopyLinks.disabled = false;
  updateDownloadButtonLabel();

  trackListEl.innerHTML = "";
  currentTracks.forEach((t, i) => {
    const item = document.createElement("div");
    item.className = "track-item";
    item.innerHTML = `
      <span class="track-item-title" title="${t.title}">${i + 1}. ${t.title}</span>
      <span class="track-item-idx">AUDIO</span>
    `;
    trackListEl.appendChild(item);
  });
}

// Initialize & Scan current active tab
async function initTab() {
  statusBadge.className = "badge checking";
  statusBadge.textContent = "Scanning...";

  // Check background download status first
  chrome.runtime.sendMessage({ action: "GET_DOWNLOAD_STATUS" }, (response) => {
    if (response && response.progress && response.progress.active) {
      updateProgressUI(response.progress);
    }
  });

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.url) {
      setDisconnected("No active tab found.");
      return;
    }

    activeTabId = tab.id;

    if (!tab.url.includes("treblo.com")) {
      setDisconnected("Not on treblo.com");
      return;
    }

    // Check project ID in URL
    const match = tab.url.match(/\/editor\/([a-zA-Z0-9-]+)/);
    if (match) {
      projectIdRow.classList.remove("hidden");
      projectIdText.textContent = match[1];
    } else {
      projectIdRow.classList.add("hidden");
    }

    // Try sending message to content script
    chrome.tabs.sendMessage(tab.id, { action: "SCAN_TRACKS" }, async (response) => {
      if (chrome.runtime.lastError || !response) {
        try {
          await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ["content.js"]
          });
          await sleep(400);
          
          chrome.tabs.sendMessage(tab.id, { action: "SCAN_TRACKS" }, (retryResponse) => {
            if (retryResponse && retryResponse.success) {
              setConnected(retryResponse.tracks);
            } else {
              setConnected([]);
            }
          });
        } catch (err) {
          setDisconnected("Please click 'Reload & Scan'");
        }
      } else if (response && response.success) {
        setConnected(response.tracks);
      } else {
        setConnected([]);
      }
    });

  } catch (err) {
    setDisconnected(err.message);
  }
}

function setConnected(tracks) {
  statusBadge.className = "badge connected";
  statusBadge.textContent = "Connected";
  renderTrackList(tracks);
}

function setDisconnected(msg) {
  statusBadge.className = "badge disconnected";
  statusBadge.textContent = "Offline";
  summaryNote.innerHTML = `<span style="color:#f87171">${msg}</span> Please open <a href="https://treblo.com" target="_blank">treblo.com</a>`;
  renderTrackList([]);
}

// Reload active tab and rescan
btnReloadTab.addEventListener("click", async () => {
  if (!activeTabId) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) activeTabId = tab.id;
  }

  if (activeTabId) {
    chrome.tabs.sendMessage(activeTabId, { action: "RESET_CACHE" }, () => {});
    renderTrackList([]);
    statusBadge.className = "badge checking";
    statusBadge.textContent = "Reloading...";
    summaryNote.textContent = "Page reload ho raha hai, fresh tracks capture kiye ja rahe hain...";

    chrome.tabs.reload(activeTabId, {}, async () => {
      await sleep(2500);
      initTab();
    });
  }
});

// Button 1: Download All Music (Runs in Background Service Worker)
btnDownloadAll.addEventListener("click", () => {
  if (currentTracks.length === 0) return;

  const isWav = fmtWav && fmtWav.checked;
  const targetFormat = isWav ? "WAV (Studio Quality)" : "OGG (Original)";
  const total = currentTracks.length;

  const userConfirmed = confirm(`Aapke paas total ${total} music tracks hain.\nFormat: ${targetFormat}\n\nKya aap download shuru karna chahte hain?\n\n(Download background me chalta rahega - chahe aap dusra tab kholein ya browser minimize karein!)`);
  if (!userConfirmed) return;

  // Send to background service worker
  chrome.runtime.sendMessage({
    action: "START_DOWNLOAD_ALL",
    tracks: currentTracks,
    isWav: isWav
  }, (response) => {
    if (response && response.success) {
      updateProgressUI({
        active: true,
        total: total,
        current: 0,
        currentTitle: "Starting background download...",
        isWav: isWav,
        status: "downloading"
      });
    } else {
      alert("Notice: " + (response ? response.error : "Failed to start background download."));
    }
  });
});

// Button 2: Delete List (Safety Confirmation)
btnDeleteList.addEventListener("click", () => {
  if (currentTracks.length === 0) return;
  modalTrackCount.textContent = currentTracks.length;
  deleteModal.classList.remove("hidden");
});

btnConfirmClearLocal.addEventListener("click", () => {
  renderTrackList([]);
  deleteModal.classList.add("hidden");
  if (activeTabId) {
    chrome.tabs.sendMessage(activeTabId, { action: "RESET_CACHE" }, () => {});
  }
  summaryNote.innerHTML = `List clear kar di gayi hai. Naye tracks dekhne ke liye <strong>Reload & Scan</strong> dabayein.`;
});

btnCancelModal.addEventListener("click", () => {
  deleteModal.classList.add("hidden");
});

// Toggle Import Box
btnToggleImport.addEventListener("click", () => {
  importBox.classList.toggle("hidden");
});

// Load Pasted JSON
btnImportJsonSubmit.addEventListener("click", () => {
  const raw = jsonInput.value.trim();
  if (!raw) {
    alert("Kripya Treblo ka JSON paste karein.");
    return;
  }

  try {
    const data = JSON.parse(raw);
    const parsedTracks = [];

    if (data.entities && data.entities.tracks) {
      Object.values(data.entities.tracks).forEach((t, idx) => {
        const url = t.songPath || t.audioUrl || (t.generationId ? `https://cdn.treblo.com/generations3/audio_${t.generationId}_${t.index || 0}.ogg` : null);
        if (url) {
          parsedTracks.push({
            id: t.id || `track_${idx}`,
            title: t.title || `Track_${idx + 1}`,
            url: url
          });
        }
      });
    } else if (Array.isArray(data)) {
      data.forEach((t, idx) => {
        const url = t.songPath || t.audioUrl || t.url;
        if (url) {
          parsedTracks.push({
            id: t.id || `track_${idx}`,
            title: t.title || `Track_${idx + 1}`,
            url: url
          });
        }
      });
    }

    if (parsedTracks.length > 0) {
      renderTrackList(parsedTracks);
      importBox.classList.add("hidden");
      jsonInput.value = "";
      alert(`✅ Success! ${parsedTracks.length} tracks load ho gaye hain! Ab aap 'Download All (.WAV)' daba sakte hain.`);
    } else {
      alert("JSON me koi valid songPath ya tracks nahi mile.");
    }
  } catch (err) {
    alert("JSON parse error: " + err.message);
  }
});

// Extra Action: Copy Links
btnCopyLinks.addEventListener("click", () => {
  if (currentTracks.length === 0) return;
  const urls = currentTracks.map(t => t.url).join("\n");
  navigator.clipboard.writeText(urls).then(() => {
    alert(`📋 ${currentTracks.length} Direct CDN Links clipboard me copy ho gaye hain!`);
  }).catch(() => {
    alert("Clipboard permission error.");
  });
});

// Run on load
document.addEventListener("DOMContentLoaded", () => {
  initTab();
});
