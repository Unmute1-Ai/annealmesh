const form = document.querySelector("#ask-form");
const prompt = document.querySelector("#prompt");
const recordButton = document.querySelector("#record");
const recordLabel = document.querySelector("#record-label");
const result = document.querySelector("#result");
const answer = document.querySelector("#answer");
const loading = document.querySelector("#loading");
const copyButton = document.querySelector("#copy");
const listenButton = document.querySelector("#listen");
const audio = document.querySelector("#audio");
const toast = document.querySelector("#toast");
const submitButton = form.querySelector('button[type="submit"]');

let recorder;
let toastTimer;

function notify(message) {
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.hidden = false;
  toastTimer = setTimeout(() => {
    toast.hidden = true;
  }, 2600);
}

async function request(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {}
    throw new Error(message);
  }
  return response;
}

async function runTask(task) {
  loading.hidden = false;
  result.hidden = true;
  submitButton.disabled = true;
  try {
    const response = await request("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task }),
    });
    const data = await response.json();
    answer.textContent = data.answer;
    result.hidden = false;
    result.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (error) {
    notify(error.message);
  } finally {
    loading.hidden = true;
    submitButton.disabled = false;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const task = prompt.value.trim();
  if (task) runTask(task);
});

copyButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(answer.textContent);
  notify("Copied");
});

listenButton.addEventListener("click", async () => {
  listenButton.disabled = true;
  listenButton.textContent = "Preparing...";
  try {
    const response = await request("/api/speech", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task: answer.textContent }),
    });
    const blob = await response.blob();
    if (audio.src) URL.revokeObjectURL(audio.src);
    audio.src = URL.createObjectURL(blob);
    audio.hidden = false;
    await audio.play();
  } catch (error) {
    notify(error.message);
  } finally {
    listenButton.disabled = false;
    listenButton.textContent = "Listen";
  }
});

recordButton.addEventListener("click", async () => {
  if (recorder?.recording) {
    const wav = await recorder.stop();
    setRecordingState(false);
    await transcribe(wav);
    return;
  }
  try {
    recorder = await createRecorder();
    setRecordingState(true);
  } catch (error) {
    notify(error.message || "Microphone access failed");
  }
});

function setRecordingState(active) {
  recordButton.classList.toggle("recording", active);
  recordButton.setAttribute("aria-label", active ? "Stop recording" : "Record voice");
  recordLabel.textContent = active ? "Tap to stop" : "Voice";
}

async function transcribe(blob) {
  recordButton.disabled = true;
  recordLabel.textContent = "Transcribing";
  const data = new FormData();
  data.append("audio", blob, "recording.wav");
  try {
    const response = await request("/api/transcribe", { method: "POST", body: data });
    const body = await response.json();
    prompt.value = body.transcript;
    prompt.focus();
  } catch (error) {
    notify(error.message);
  } finally {
    recordButton.disabled = false;
    recordLabel.textContent = "Voice";
  }
}

async function createRecorder() {
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
  });
  const context = new AudioContext();
  await context.audioWorklet.addModule("/recorder-worklet.js");
  const source = context.createMediaStreamSource(stream);
  const node = new AudioWorkletNode(context, "pcm-recorder");
  source.connect(node);
  node.connect(context.destination);
  const chunks = [];
  node.port.onmessage = (event) => chunks.push(event.data);

  return {
    recording: true,
    async stop() {
      node.port.postMessage("stop");
      await new Promise((resolve) => setTimeout(resolve, 80));
      this.recording = false;
      source.disconnect();
      node.disconnect();
      stream.getTracks().forEach((track) => track.stop());
      await context.close();
      return encodeWav(chunks, context.sampleRate);
    },
  };
}

function encodeWav(chunks, sampleRate) {
  const length = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
  const samples = new Float32Array(length);
  let offset = 0;
  chunks.forEach((chunk) => {
    samples.set(chunk, offset);
    offset += chunk.length;
  });

  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);
  write(view, 0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  write(view, 8, "WAVEfmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  write(view, 36, "data");
  view.setUint32(40, samples.length * 2, true);
  samples.forEach((sample, index) => {
    const value = Math.max(-1, Math.min(1, sample));
    view.setInt16(44 + index * 2, value < 0 ? value * 32768 : value * 32767, true);
  });
  return new Blob([buffer], { type: "audio/wav" });
}

function write(view, offset, value) {
  for (let i = 0; i < value.length; i += 1) {
    view.setUint8(offset + i, value.charCodeAt(i));
  }
}

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js");
}
