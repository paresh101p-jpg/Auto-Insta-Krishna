// popup.js - Controller for Treblo Downloader Popup with Studio-Quality WAV conversion

let currentTracks = [];
let isDownloading = false;
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

// Format title to safe filename
function getCleanTitle(title, index) {
  let clean = (title || `Track_${index + 1}`).replace(/[\\/:*?"<>|]/g, "_").trim();
  clean = clean.replace(/\.(ogg|mp3|wav)$/i, "");
  return clean || `Track_${index + 1}`;
}

// Convert ArrayBuffer audio (OGG/MP3) to standard 16-bit PCM WAV Blob
async function convertAudioBufferToWavBlob(arrayBuffer) {
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  let audioBuffer;
  try {
    audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
  } finally {
    try { audioCtx.close(); } catch(e) {}
  }

  const numChannels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const format = 1; // PCM
  const bitDepth = 16;

  // Interleave channels
  let interleaved;
  if (numChannels === 2) {
    const left = audioBuffer.getChannelData(0);
    const right = audioBuffer.getChannelData(1);
    interleaved = new Float32Array(left.length + right.length);
    let index = 0;
    for (let i = 0; i < left.length; i++) {
      interleaved[index++] = left[i];
      interleaved[index++] = right[i];
    }
  } else {
    interleaved = audioBuffer.getChannelData(0);
  }

  const byteRate = (sampleRate * numChannels * bitDepth) / 8;
  const blockAlign = (numChannels * bitDepth) / 8;
  const dataSize = interleaved.length * 2;
  const bufferLength = 44 + dataSize;
  const wavBuffer = new ArrayBuffer(bufferLength);
  const view = new DataView(wavBuffer);

  function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  // RIFF chunk descriptor
  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + dataSize, true);
  writeString(view, 8, "WAVE");

  // fmt sub-chunk
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true); // SubChunk1Size (16 for PCM)
  view.setUint16(20, format, true); // AudioFormat (1 = PCM)
  view.setUint16(22, numChannels, true); // NumChannels
  view.setUint32(24, sampleRate, true); // SampleRate
  view.setUint32(28, byteRate, true); // ByteRate
  view.setUint16(32, blockAlign, true); // BlockAlign
  view.setUint16(34, bitDepth, true); // BitsPerSample

  // data sub-chunk
  writeString(view, 36, "data");
  view.setUint32(40, dataSize, true);

  // Write 16-bit PCM samples
  let offset = 44;
  for (let i = 0; i < interleaved.length; i++) {
    let s = Math.max(-1, Math.min(1, interleaved[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    offset += 2;
  }

  return new Blob([wavBuffer], { type: "audio/wav" });
}

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
        <small style="color:#94a3b8;">Page reload hote hi sabhi 31 tracks apne aap load ho jayenge.</small>
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
      <span class="track-item-idx">WAV</span>
    `;
    trackListEl.appendChild(item);
  });
}

// Initialize & Scan current active tab
async function initTab() {
  statusBadge.className = "badge checking";
  statusBadge.textContent = "Scanning...";

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

// Button 1: Download All Music with Safe Pacing + WAV Conversion
btnDownloadAll.addEventListener("click", async () => {
  if (isDownloading || currentTracks.length === 0) return;

  const isWav = fmtWav && fmtWav.checked;
  const targetFormat = isWav ? "WAV (Studio Quality)" : "OGG (Original)";
  const total = currentTracks.length;

  const userConfirmed = confirm(`Aapke paas total ${total} music tracks hain.\nFormat: ${targetFormat}\n\nKya aap sabhi ${total} tracks ko seedhe:\nE:\\Paresh\\Auto Post\\Auto-Insta-Krishna\\Treblo Music\nme download karna chahte hain?`);
  if (!userConfirmed) return;

  isDownloading = true;
  btnDownloadAll.disabled = true;
  btnReloadTab.disabled = true;
  progressContainer.classList.remove("hidden");

  let downloadedCount = 0;
  let failedCount = 0;

  for (let i = 0; i < total; i++) {
    const track = currentTracks[i];
    const cleanTitle = getCleanTitle(track.title, i);

    progressBar.style.width = `${Math.round(((i + 1) / total) * 100)}%`;

    try {
      if (isWav) {
        progressText.textContent = `[${i + 1}/${total}] Fetching & Converting to WAV: ${track.title}...`;
        
        // 1. Fetch raw audio
        const resp = await fetch(track.url);
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        const arrayBuf = await resp.arrayBuffer();

        // 2. Convert to uncompressed 16-bit PCM WAV
        const wavBlob = await convertAudioBufferToWavBlob(arrayBuf);
        const blobUrl = URL.createObjectURL(wavBlob);
        const destPath = `Treblo_Music/${cleanTitle}.wav`;

        // 3. Trigger download
        await new Promise((resolve) => {
          chrome.downloads.download({
            url: blobUrl,
            filename: destPath,
            conflictAction: "uniquify",
            saveAs: false
          }, (downloadId) => {
            setTimeout(() => URL.revokeObjectURL(blobUrl), 15000);
            if (chrome.runtime.lastError || !downloadId) {
              console.warn("Download error:", chrome.runtime.lastError);
              failedCount++;
            } else {
              downloadedCount++;
            }
            resolve();
          });
        });

      } else {
        // Fast direct OGG download
        progressText.textContent = `[${i + 1}/${total}] Downloading: ${track.title}...`;
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

    } catch (e) {
      console.warn("Track download error:", e);
      failedCount++;
    }

    // Safe delay (1.2s) between downloads to respect browser and memory
    if (i < total - 1) {
      await sleep(1200);
    }
  }

  isDownloading = false;
  btnDownloadAll.disabled = false;
  btnReloadTab.disabled = false;
  const extLabel = isWav ? ".WAV" : ".OGG";
  progressText.textContent = `✅ Completed: ${downloadedCount} ${extLabel} downloaded (${failedCount} failed). Saved to Downloads/Treblo_Music/`;
  alert(`✅ Done! ${downloadedCount} music tracks successfully ${extLabel} format me download ho gaye hain!\n\nAapke computer ke 'Downloads/Treblo_Music/' folder me check karein.`);
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
