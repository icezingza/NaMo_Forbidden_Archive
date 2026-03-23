const CLOUD_RUN_URL = "https://namo-forbidden-archive-185116032835.asia-southeast1.run.app";
const DEFAULT_BASE_URL = (() => {
  const origin = window.location.origin;
  if (origin && origin !== "null" && window.location.pathname.startsWith("/ui")) {
    return origin;
  }
  return CLOUD_RUN_URL;
})();
const STORAGE_KEYS = {
  baseUrl: "namo_base_url",
  sessionId: "namo_session_id",
  messages: "namo_messages",
  streamMode: "namo_stream_mode",
};

const state = {
  baseUrl: "",
  sessionId: "",
  messages: [],
  loading: false,
  streamMode: true,
};

const dom = {
  chat: document.getElementById("chat"),
  emptyState: document.getElementById("empty-state"),
  errorState: document.getElementById("error-state"),
  errorMessage: document.getElementById("error-message"),
  messageInput: document.getElementById("message-input"),
  chatForm: document.getElementById("chat-form"),
  sendButton: document.getElementById("send-button"),
  settingsButton: document.getElementById("settings-button"),
  pingButton: document.getElementById("ping-button"),
  newSessionBtn: document.getElementById("new-session-btn"),
  settingsModal: document.getElementById("settings-modal"),
  confirmModal: document.getElementById("confirm-modal"),
  confirmNewSession: document.getElementById("confirm-new-session"),
  baseUrlInput: document.getElementById("base-url-input"),
  saveSettings: document.getElementById("save-settings"),
  baseUrlLabel: document.getElementById("base-url-label"),
  sessionIdLabel: document.getElementById("session-id-label"),
  statusEngine: document.getElementById("status-engine"),
  statusSin: document.getElementById("status-sin"),
  statusArousal: document.getElementById("status-arousal"),
  statusPersonas: document.getElementById("status-personas"),
  arousalBar: document.getElementById("arousal-bar"),
  statusStage: document.getElementById("status-stage"),
  statusStageDesc: document.getElementById("status-stage-desc"),
  emotionProse: document.getElementById("emotion-prose"),
  streamToggle: document.getElementById("stream-toggle"),
  ebarJoy: document.getElementById("ebar-joy"),
  ebarArousal: document.getElementById("ebar-arousal"),
  ebarTrust: document.getElementById("ebar-trust"),
  ebarAnger: document.getElementById("ebar-anger"),
  ebarDesire: document.getElementById("ebar-desire"),
  ebarJoyNum: document.getElementById("ebar-joy-num"),
  ebarArousalNum: document.getElementById("ebar-arousal-num"),
  ebarTrustNum: document.getElementById("ebar-trust-num"),
  ebarAngerNum: document.getElementById("ebar-anger-num"),
  ebarDesireNum: document.getElementById("ebar-desire-num"),
};

// ---------------------------------------------------------------------------
// Stage metadata
// ---------------------------------------------------------------------------
const STAGE_META = {
  Stranger: { key: "stranger", desc: "Just met. Guarded but polite." },
  Plaything: { key: "plaything", desc: "User is testing boundaries." },
  Lover: { key: "lover", desc: "Deeply intimate." },
  "Dark Obsession": { key: "obsession", desc: "Completely unhinged and possessive." },
};

// ---------------------------------------------------------------------------
// Persistence helpers
// ---------------------------------------------------------------------------
function normalizeBaseUrl(value) {
  return value.trim().replace(/\/+$/, "");
}

function generateSessionId() {
  if (window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID();
  }
  return `session-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
}

function loadState() {
  const storedBaseUrl = localStorage.getItem(STORAGE_KEYS.baseUrl);
  state.baseUrl = normalizeBaseUrl(storedBaseUrl || DEFAULT_BASE_URL);

  const storedSession = localStorage.getItem(STORAGE_KEYS.sessionId);
  state.sessionId = storedSession || generateSessionId();
  localStorage.setItem(STORAGE_KEYS.sessionId, state.sessionId);

  const storedMessages = localStorage.getItem(STORAGE_KEYS.messages);
  if (storedMessages) {
    try {
      state.messages = JSON.parse(storedMessages);
    } catch {
      state.messages = [];
    }
  }

  const storedStream = localStorage.getItem(STORAGE_KEYS.streamMode);
  state.streamMode = storedStream === null ? true : storedStream === "1";
}

function saveMessages() {
  localStorage.setItem(STORAGE_KEYS.messages, JSON.stringify(state.messages.slice(-80)));
}

function setBaseUrl(value) {
  state.baseUrl = normalizeBaseUrl(value);
  localStorage.setItem(STORAGE_KEYS.baseUrl, state.baseUrl);
  updateSessionUI();
}

// ---------------------------------------------------------------------------
// UI updates
// ---------------------------------------------------------------------------
function updateSessionUI() {
  dom.baseUrlLabel.textContent = state.baseUrl;
  const sid = state.sessionId;
  dom.sessionIdLabel.textContent = sid.length > 20 ? `${sid.slice(0, 8)}…${sid.slice(-6)}` : sid;
}

function updateStreamToggleUI() {
  dom.streamToggle.setAttribute("aria-pressed", state.streamMode ? "true" : "false");
  dom.streamToggle.textContent = state.streamMode ? "Stream ◈" : "Stream ○";
}

function setStatusFromRoot(payload) {
  if (!payload) return;
  if (payload.engine) {
    dom.statusEngine.textContent = payload.engine;
  }
  if (payload.sin) {
    dom.statusSin.textContent = payload.sin;
  }
}

function setStatusFromChat(payload) {
  if (!payload || !payload.status) return;
  const status = payload.status;

  if (status.sin_status) {
    dom.statusSin.textContent = status.sin_status;
  }
  if (status.arousal) {
    dom.statusArousal.textContent = status.arousal;
    const match = String(status.arousal).match(/(\d+)/);
    const pct = match ? Math.min(100, Number(match[1])) : 0;
    dom.arousalBar.style.width = `${pct}%`;
  }
  if (Array.isArray(status.active_personas)) {
    dom.statusPersonas.textContent = status.active_personas.join(", ") || "NaMo";
  }
  if (status.relationship) {
    updateRelationshipStage(status.relationship);
  }
  if (status.emotion) {
    updateEmotionBars(status.emotion);
  }
  if (payload.engine) {
    dom.statusEngine.textContent = payload.engine;
  }
}

function updateRelationshipStage(rel) {
  if (!rel || !rel.stage) return;
  const stageName = rel.stage;
  const meta = STAGE_META[stageName] || { key: "stranger", desc: rel.description || "" };
  dom.statusStage.textContent = stageName;
  dom.statusStage.dataset.stage = meta.key;
  dom.statusStageDesc.textContent = meta.desc || rel.description || "";
}

function updateEmotionBars(emotion) {
  if (!emotion) return;
  const bars = [
    { key: "joy", el: dom.ebarJoy, num: dom.ebarJoyNum },
    { key: "arousal", el: dom.ebarArousal, num: dom.ebarArousalNum },
    { key: "trust", el: dom.ebarTrust, num: dom.ebarTrustNum },
    { key: "anger", el: dom.ebarAnger, num: dom.ebarAngerNum },
    { key: "desire", el: dom.ebarDesire, num: dom.ebarDesireNum },
  ];
  for (const bar of bars) {
    const raw = emotion[bar.key];
    if (typeof raw !== "number") continue;
    const pct = Math.round(Math.min(1, Math.max(0, raw)) * 100);
    bar.el.style.width = `${pct}%`;
    bar.num.textContent = raw.toFixed(2);
  }
  if (emotion.prose) {
    dom.emotionProse.textContent = emotion.prose;
  }
}

// Called after a stream completes — refreshes emotion from the global status endpoint.
async function fetchAndApplyStatus() {
  try {
    const res = await fetch(`${state.baseUrl}/v1/status`);
    if (!res.ok) return;
    const payload = await res.json();
    // payload shape: { EngineName: { emotion, traits, ... } }
    const engineData = Object.values(payload)[0];
    if (!engineData) return;
    if (engineData.emotion) updateEmotionBars(engineData.emotion);
    if (engineData.engine) dom.statusEngine.textContent = engineData.engine;
  } catch {
    // silent
  }
}

function resolveMediaUrl(path) {
  if (!path) return null;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  if (path.startsWith("/")) return `${state.baseUrl}${path}`;
  return `${state.baseUrl}/${path}`;
}

function setLoading(isLoading) {
  state.loading = isLoading;
  dom.sendButton.disabled = isLoading;
  dom.sendButton.textContent = isLoading ? "…" : "Send";
  dom.messageInput.disabled = isLoading;
}

function setError(message) {
  if (message) {
    dom.errorMessage.textContent = message;
    dom.errorState.classList.add("state--visible");
  } else {
    dom.errorState.classList.remove("state--visible");
  }
}

function updateEmptyState() {
  if (state.messages.length === 0) {
    dom.emptyState.classList.add("state--visible");
  } else {
    dom.emptyState.classList.remove("state--visible");
  }
}

// ---------------------------------------------------------------------------
// Message rendering
// ---------------------------------------------------------------------------
function renderMessages() {
  dom.chat.innerHTML = "";
  state.messages.forEach((message) => {
    dom.chat.appendChild(renderMessage(message));
  });
  updateEmptyState();
  dom.chat.scrollTop = dom.chat.scrollHeight;
}

function renderMessage(message) {
  const wrapper = document.createElement("div");
  wrapper.className = `message message--${message.role}`;

  const bubble = document.createElement("div");
  bubble.className = `bubble bubble--${message.role}`;
  bubble.textContent = message.text;
  wrapper.appendChild(bubble);

  if (message.media) {
    const mediaSection = renderMedia(message.media);
    if (mediaSection) {
      wrapper.appendChild(mediaSection);
    }
  }

  const meta = document.createElement("div");
  meta.className = "message__meta";
  const stamp = new Date(message.timestamp || Date.now());
  meta.textContent = stamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  wrapper.appendChild(meta);

  return wrapper;
}

function renderMedia(media) {
  const entries = [];

  if (media.image) {
    entries.push({ type: "image", url: resolveMediaUrl(media.image), label: "Image" });
  }
  if (media.audio) {
    entries.push({ type: "audio", url: resolveMediaUrl(media.audio), label: "Audio" });
  }
  if (media.tts && media.tts !== media.audio) {
    entries.push({ type: "audio", url: resolveMediaUrl(media.tts), label: "TTS" });
  }

  if (entries.length === 0) return null;

  const container = document.createElement("div");
  container.className = "message__media";

  entries.forEach((entry) => {
    const label = document.createElement("div");
    label.className = "media-label";
    label.textContent = entry.label;
    container.appendChild(label);

    if (entry.type === "image") {
      const img = document.createElement("img");
      img.alt = "Media output";
      img.src = entry.url;
      container.appendChild(img);
    } else if (entry.type === "audio") {
      const audio = document.createElement("audio");
      audio.controls = true;
      audio.src = entry.url;
      container.appendChild(audio);
    }
  });

  return container;
}

function addMessage(message) {
  state.messages.push(message);
  if (state.messages.length > 120) {
    state.messages = state.messages.slice(-120);
  }
  saveMessages();
  dom.chat.appendChild(renderMessage(message));
  updateEmptyState();
  dom.chat.scrollTop = dom.chat.scrollHeight;
}

// ---------------------------------------------------------------------------
// Non-streaming send (uses /chat, returns full status)
// ---------------------------------------------------------------------------
async function sendMessagePlain(text) {
  if (!text || state.loading) return;
  setError("");
  addMessage({ role: "user", text, timestamp: Date.now() });
  dom.messageInput.value = "";
  setLoading(true);

  try {
    const response = await fetch(`${state.baseUrl}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, session_id: state.sessionId }),
    });

    if (!response.ok) throw new Error(`API error: ${response.status}`);

    const payload = await response.json();
    if (payload.session_id) {
      state.sessionId = payload.session_id;
      localStorage.setItem(STORAGE_KEYS.sessionId, state.sessionId);
    }

    addMessage({
      role: "assistant",
      text: payload.response || "No response",
      media: payload.media || null,
      timestamp: Date.now(),
    });
    setStatusFromChat(payload);
  } catch (error) {
    setError(error.message || "Request failed.");
  } finally {
    setLoading(false);
    updateSessionUI();
  }
}

// ---------------------------------------------------------------------------
// Streaming send (uses /v1/chat/stream SSE, updates emotion after)
// ---------------------------------------------------------------------------
async function sendMessageStream(text) {
  if (!text || state.loading) return;
  setError("");
  addMessage({ role: "user", text, timestamp: Date.now() });
  dom.messageInput.value = "";
  setLoading(true);

  // Create assistant message placeholder
  const assistantMsg = { role: "assistant", text: "", timestamp: Date.now() };
  state.messages.push(assistantMsg);
  if (state.messages.length > 120) state.messages = state.messages.slice(-120);
  const wrapper = renderMessage(assistantMsg);
  dom.chat.appendChild(wrapper);
  updateEmptyState();
  dom.chat.scrollTop = dom.chat.scrollHeight;
  const bubble = wrapper.querySelector(".bubble--assistant");

  try {
    const response = await fetch(`${state.baseUrl}/v1/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, session_id: state.sessionId }),
    });

    if (!response.ok) throw new Error(`API error: ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const raw = line.slice(6).trim();
        if (!raw) continue;
        let event;
        try {
          event = JSON.parse(raw);
        } catch {
          continue;
        }

        if (event.error) {
          throw new Error(event.error);
        }
        if (event.chunk) {
          assistantMsg.text += event.chunk;
          bubble.textContent = assistantMsg.text;
          dom.chat.scrollTop = dom.chat.scrollHeight;
        }
        if (event.session_id) {
          state.sessionId = event.session_id;
          localStorage.setItem(STORAGE_KEYS.sessionId, state.sessionId);
        }
        if (event.engine) {
          dom.statusEngine.textContent = event.engine;
        }
      }
    }

    saveMessages();
    await fetchAndApplyStatus();
  } catch (error) {
    if (assistantMsg.text === "") {
      // Stream failed before any content — remove placeholder and fall back
      dom.chat.removeChild(wrapper);
      state.messages.pop();
      setError(error.message || "Stream failed.");
    }
  } finally {
    setLoading(false);
    updateSessionUI();
  }
}

function sendMessage(text) {
  if (state.streamMode) {
    return sendMessageStream(text);
  }
  return sendMessagePlain(text);
}

// ---------------------------------------------------------------------------
// Ping / status
// ---------------------------------------------------------------------------
async function pingServer() {
  setError("");
  try {
    const response = await fetch(`${state.baseUrl}/`, { method: "GET" });
    if (!response.ok) throw new Error(`Ping failed: ${response.status}`);
    const payload = await response.json();
    setStatusFromRoot(payload);
  } catch (error) {
    setError(error.message || "Unable to reach API.");
  }
}

// ---------------------------------------------------------------------------
// New session
// ---------------------------------------------------------------------------
function startNewSession() {
  state.sessionId = generateSessionId();
  localStorage.setItem(STORAGE_KEYS.sessionId, state.sessionId);
  state.messages = [];
  localStorage.removeItem(STORAGE_KEYS.messages);
  renderMessages();
  updateSessionUI();
}

// ---------------------------------------------------------------------------
// Settings modal
// ---------------------------------------------------------------------------
function openSettings() {
  dom.baseUrlInput.value = state.baseUrl;
  dom.settingsModal.classList.remove("hidden");
  dom.settingsModal.setAttribute("aria-hidden", "false");
}

function closeSettings() {
  dom.settingsModal.classList.add("hidden");
  dom.settingsModal.setAttribute("aria-hidden", "true");
}

function openConfirmModal() {
  dom.confirmModal.classList.remove("hidden");
  dom.confirmModal.setAttribute("aria-hidden", "false");
}

function closeConfirmModal() {
  dom.confirmModal.classList.add("hidden");
  dom.confirmModal.setAttribute("aria-hidden", "true");
}

// ---------------------------------------------------------------------------
// Event binding
// ---------------------------------------------------------------------------
function bindEvents() {
  dom.chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage(dom.messageInput.value.trim());
  });

  dom.messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage(dom.messageInput.value.trim());
    }
  });

  dom.settingsButton.addEventListener("click", openSettings);
  dom.pingButton.addEventListener("click", pingServer);

  dom.newSessionBtn.addEventListener("click", openConfirmModal);
  dom.confirmNewSession.addEventListener("click", () => {
    closeConfirmModal();
    startNewSession();
  });
  dom.confirmModal.addEventListener("click", (event) => {
    if (event.target.dataset.closeConfirm === "true") closeConfirmModal();
  });

  dom.streamToggle.addEventListener("click", () => {
    state.streamMode = !state.streamMode;
    localStorage.setItem(STORAGE_KEYS.streamMode, state.streamMode ? "1" : "0");
    updateStreamToggleUI();
  });

  dom.saveSettings.addEventListener("click", () => {
    const value = dom.baseUrlInput.value.trim();
    if (value) {
      setBaseUrl(value);
      pingServer();
    }
    closeSettings();
  });

  dom.settingsModal.addEventListener("click", (event) => {
    if (event.target.dataset.close === "true") closeSettings();
  });
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
function init() {
  loadState();
  updateSessionUI();
  updateStreamToggleUI();
  renderMessages();
  bindEvents();
  pingServer();
}

init();
