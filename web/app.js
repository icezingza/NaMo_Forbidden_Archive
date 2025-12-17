const DEFAULT_BASE_URL = "https://namo-forbidden-archive0-185116032835.asia-southeast1.run.app";
const STORAGE_KEYS = {
  baseUrl: "namo_base_url",
  sessionId: "namo_session_id",
  messages: "namo_messages",
};

const state = {
  baseUrl: "",
  sessionId: "",
  messages: [],
  loading: false,
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
  settingsModal: document.getElementById("settings-modal"),
  baseUrlInput: document.getElementById("base-url-input"),
  saveSettings: document.getElementById("save-settings"),
  baseUrlLabel: document.getElementById("base-url-label"),
  sessionIdLabel: document.getElementById("session-id-label"),
  statusEngine: document.getElementById("status-engine"),
  statusSin: document.getElementById("status-sin"),
  statusArousal: document.getElementById("status-arousal"),
  statusPersonas: document.getElementById("status-personas"),
  arousalBar: document.getElementById("arousal-bar"),
};

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
    } catch (error) {
      state.messages = [];
    }
  }
}

function saveMessages() {
  localStorage.setItem(STORAGE_KEYS.messages, JSON.stringify(state.messages.slice(-80)));
}

function setBaseUrl(value) {
  state.baseUrl = normalizeBaseUrl(value);
  localStorage.setItem(STORAGE_KEYS.baseUrl, state.baseUrl);
  updateSessionUI();
}

function updateSessionUI() {
  dom.baseUrlLabel.textContent = state.baseUrl;
  dom.sessionIdLabel.textContent = state.sessionId;
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
  dom.sendButton.textContent = isLoading ? "Sending..." : "Send";
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

  if (entries.length === 0) {
    return null;
  }

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

async function sendMessage(text) {
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

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

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
  }
}

async function pingServer() {
  setError("");
  try {
    const response = await fetch(`${state.baseUrl}/`, { method: "GET" });
    if (!response.ok) {
      throw new Error(`Ping failed: ${response.status}`);
    }
    const payload = await response.json();
    setStatusFromRoot(payload);
  } catch (error) {
    setError(error.message || "Unable to reach API.");
  }
}

function openSettings() {
  dom.baseUrlInput.value = state.baseUrl;
  dom.settingsModal.classList.remove("hidden");
  dom.settingsModal.setAttribute("aria-hidden", "false");
}

function closeSettings() {
  dom.settingsModal.classList.add("hidden");
  dom.settingsModal.setAttribute("aria-hidden", "true");
}

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
  dom.saveSettings.addEventListener("click", () => {
    const value = dom.baseUrlInput.value.trim();
    if (value) {
      setBaseUrl(value);
      pingServer();
    }
    closeSettings();
  });

  dom.settingsModal.addEventListener("click", (event) => {
    if (event.target.dataset.close === "true") {
      closeSettings();
    }
  });
}

function init() {
  loadState();
  updateSessionUI();
  renderMessages();
  bindEvents();
  pingServer();
}

init();
