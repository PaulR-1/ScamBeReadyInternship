import { api, toast } from "./common.js";

const form = document.getElementById("settings-form");
const state = document.getElementById("settings-state");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {};
  for (const field of form.elements) {
    if (!field.name) continue;
    payload[field.name] = field.type === "checkbox" ? (field.checked ? "1" : "0") : field.value;
  }
  state.textContent = "Saving...";
  try {
    await api("/api/settings", { method: "PUT", body: JSON.stringify(payload) });
    state.textContent = "Saved. Applies to the next transcription.";
    toast("Settings saved.");
  } catch (err) {
    state.textContent = "";
    toast(err.message, true);
  }
});
