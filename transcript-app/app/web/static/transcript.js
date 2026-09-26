import { ACTIVE, api, formatClock, formatDuration, toast } from "./common.js";

const root = document.getElementById("transcript-root");
const id = Number(root.dataset.transcriptId);
const segmentsBox = document.getElementById("segments");
const metaGrid = document.getElementById("meta-grid");
const progressWrap = document.getElementById("progress-wrap");
const progressFill = document.getElementById("progress-fill");
const progressLabel = document.getElementById("progress-label");
const errorLine = document.getElementById("transcript-error");
const cancelButton = document.getElementById("cancel-button");
const retryButton = document.getElementById("retry-button");
const saveState = document.getElementById("save-state");
const player = document.getElementById("player");

const rendered = new Map();
let pollTimer = null;

function meta(label, value) {
  const cell = document.createElement("div");
  const key = document.createElement("span");
  key.className = "muted";
  key.textContent = label;
  const val = document.createElement("strong");
  val.textContent = value;
  cell.append(key, val);
  return cell;
}

function renderHeader(t) {
  metaGrid.replaceChildren(
    meta("Status", t.status),
    meta("Length", formatDuration(t.duration)),
    meta("Model", t.model),
    meta("Engine", t.device ? `${t.device} / ${t.compute_type}` : "pending"),
    meta(
      "Language",
      t.detected_language
        ? `${t.detected_language}${t.language_probability ? ` (${Math.round(t.language_probability * 100)}%)` : ""}`
        : t.language
    )
  );

  const active = ACTIVE.has(t.status);
  progressWrap.hidden = !active;
  if (active) {
    progressFill.style.width = `${Math.round(t.progress * 100)}%`;
    progressLabel.textContent =
      t.status === "queued" ? "Waiting for the worker" : `${Math.round(t.progress * 100)}%`;
  }
  cancelButton.hidden = !active;
  retryButton.hidden = active || t.status === "completed";
  errorLine.hidden = !t.error;
  errorLine.textContent = t.error || "";
  return active;
}

function buildSegment(segment) {
  const row = document.createElement("div");
  row.className = "segment";
  row.dataset.id = segment.id;
  row.dataset.start = segment.start;
  row.dataset.end = segment.end;

  const time = document.createElement("button");
  time.type = "button";
  time.className = "segment-time";
  time.textContent = segment.start_label;
  time.title = "Play from here";
  time.addEventListener("click", () => {
    if (!player) return;
    player.currentTime = segment.start;
    player.play();
  });

  const text = document.createElement("div");
  text.className = "segment-text";
  text.contentEditable = "true";
  text.spellcheck = false;
  text.textContent = segment.text;
  text.addEventListener("blur", () => save(row, text, segment));
  text.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      text.blur();
    }
    if (event.key === "Escape") {
      text.textContent = segment.text;
      text.blur();
    }
  });

  row.append(time, text);
  row.classList.toggle("edited", segment.edited);
  return row;
}

async function save(row, textNode, segment) {
  const value = textNode.textContent.trim();
  if (value === segment.text) return;
  saveState.textContent = "Saving...";
  try {
    const updated = await api(`/api/segments/${segment.id}`, {
      method: "PATCH",
      body: JSON.stringify({ text: value }),
    });
    segment.text = updated.text;
    segment.edited = updated.edited;
    row.classList.toggle("edited", updated.edited);
    saveState.textContent = "Saved";
  } catch (err) {
    textNode.textContent = segment.text;
    saveState.textContent = "";
    toast(err.message, true);
  }
}

function renderSegments(segments) {
  document.getElementById("segments-empty")?.remove();
  for (const segment of segments) {
    const existing = rendered.get(segment.id);
    if (!existing) {
      const row = buildSegment({ ...segment });
      rendered.set(segment.id, row);
      segmentsBox.appendChild(row);
    }
  }
  if (!segments.length && !rendered.size) {
    segmentsBox.innerHTML = '<p class="muted empty" id="segments-empty">No text yet.</p>';
  }
}

async function refresh() {
  try {
    const data = await api(`/api/transcripts/${id}`);
    const active = renderHeader(data.transcript);
    renderSegments(data.segments || []);
    return active;
  } catch (err) {
    toast(err.message, true);
    return false;
  }
}

cancelButton.addEventListener("click", async () => {
  cancelButton.disabled = true;
  try {
    await api(`/api/transcripts/${id}/cancel`, { method: "POST" });
    toast("Canceling...");
  } catch (err) {
    toast(err.message, true);
  } finally {
    cancelButton.disabled = false;
  }
});

retryButton.addEventListener("click", async () => {
  retryButton.disabled = true;
  try {
    await api(`/api/transcripts/${id}/retry`, { method: "POST" });
    rendered.clear();
    segmentsBox.innerHTML = "";
    toast("Queued again.");
    poll(true);
  } catch (err) {
    toast(err.message, true);
  } finally {
    retryButton.disabled = false;
  }
});

if (player) {
  player.addEventListener("timeupdate", () => {
    const now = player.currentTime;
    for (const row of rendered.values()) {
      const on = now >= Number(row.dataset.start) && now < Number(row.dataset.end);
      row.classList.toggle("playing", on);
    }
  });
}

function poll(active) {
  clearInterval(pollTimer);
  if (!active) return;
  pollTimer = setInterval(async () => {
    const stillActive = await refresh();
    if (!stillActive) {
      clearInterval(pollTimer);
      // Pick up the final segments written after the last poll.
      refresh();
    }
  }, 1500);
}

refresh().then(poll);
