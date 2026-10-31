// offscreen.js - Runs in hidden offscreen DOM document with full AudioContext support

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
  view.setUint32(16, 16, true);
  view.setUint16(20, format, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitDepth, true);

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

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "CONVERT_TO_WAV_BLOB_URL") {
    fetch(request.url)
      .then(resp => {
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        return resp.arrayBuffer();
      })
      .then(arrayBuf => convertAudioBufferToWavBlob(arrayBuf))
      .then(wavBlob => {
        const blobUrl = URL.createObjectURL(wavBlob);
        sendResponse({ success: true, blobUrl: blobUrl });
      })
      .catch(err => {
        sendResponse({ success: false, error: err.message });
      });
    return true; // async
  }

  if (request.action === "REVOKE_BLOB_URL") {
    if (request.blobUrl) {
      URL.revokeObjectURL(request.blobUrl);
    }
    sendResponse({ success: true });
    return false;
  }
});
