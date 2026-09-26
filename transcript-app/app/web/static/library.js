import { ACTIVE, api, formatDuration, toast } from "./common.js";

const list = document.getElementById("transcript-list");
const form = document.getElementById("import-form");
const pathInput = document.getElementById("path-input");
const titleInput = document.getElementById("title-input");
const errorLine = document.getElementById("import-error");
const browseButton = document.getElementById("browse-button");
const submitButton = form.querySelector("button[type=submit]");

function statusLine(item) {
  if (item.status === "running") return `Transcribing - ${Math.round(item.progress * 100)}%`;
  if (item.status === "queued") return "Waiting in queue";
  if (item.status === "completed") return `${item.segment_count ?? 0} segments - ${formatDuration(item.duration)}`;
  return item.error || item.status;
}

function render(items) {
  list.innerHTML = "";
  if (!items.length) {
    list.innerHTML = '<p class="muted empty">Nothing here yet.</p>';
    return;
  }
  for (const item of items) {
    const row = document.createElement("div");
    row.className = "item";

    const main = document.createElement("div");
    main.className = "item-main";
    main.innerHTML = `
      <div class="item-title"><a href="/transcripts/${item.id}"></a></div>
      <div class="item-sub"></div>`;
    main.querySelector("a").textContent = item.title;
    main.querySelector(".item-sub").textContent = statusLine(item);

    const actions = document.createElement("div");
    actions.className = "item-actions";

    const tag = document.createElement("span");
    tag.className = `tag ${item.status}`;
    tag.textContent = item.status;
    actions.appendChild(tag);

    if (ACTIVE.has(item.status)) {
      actions.appendChild(button("Cancel", "secondary", () => act(`/api/transcripts/${item.id}/cancel`)));
    } else {
      if (item.status !== "completed") {
        actions.appendChild(button("Retry", "secondary", () => act(`/api/transcripts/${item.id}/retry`)));
      }
      actions.appendChild(
        button("Delete", "danger", () => {
          if (confirm(`Delete "${item.title}"? The original file is not touched.`)) {
            act(`/api/transcripts/${item.id}`, "DELETE");
          }
        })
      );
    }

    row.append(main, actions);
    list.appendChild(row);
  }
}

function button(label, variant, onClick) {
  const el = document.createElement("button");
  el.type = "button";
  el.className = variant;
  el.textContent = label;
  el.addEventListener("click", onClick);
  return el;
}

async function act(url, method = "POST") {
  try {
    await api(url, { method });
    await refresh();
  } catch (err) {
    toast(err.message, true);
  }
}

async function refresh() {
  try {
    const data = await api("/api/transcripts");
    render(data.transcripts);
    return data.transcripts.some((item) => ACTIVE.has(item.status));
  } catch (err) {
    toast(err.message, true);
    return false;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorLine.hidden = true;
  submitButton.disabled = true;
  try {
    await api("/api/transcripts", {
      method: "POST",
      body: JSON.stringify({ path: pathInput.value, title: titleInput.value || null }),
    });
    pathInput.value = "";
    titleInput.value = "";
    toast("Queued.");
    await refresh();
  } catch (err) {
    errorLine.textContent = err.message;
    errorLine.hidden = false;
  } finally {
    submitButton.disabled = false;
  }
});

browseButton.addEventListener("click", async () => {
  browseButton.disabled = true;
  browseButton.textContent = "Choosing...";
  try {
    const data = await api("/api/browse", { method: "POST" });
    if (data.path) pathInput.value = data.path;
  } catch (err) {
    toast(`${err.message} Type or paste the full path instead.`, true);
  } finally {
    browseButton.disabled = false;
    browseButton.textContent = "Browse";
  }
});

let interval = null;
function schedule(active) {
  const wanted = active ? 1500 : 6000;
  clearInterval(interval);
  interval = setInterval(async () => {
    const stillActive = await refresh();
    if (stillActive !== active) schedule(stillActive);
  }, wanted);
}

refresh().then(schedule);
