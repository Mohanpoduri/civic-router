// Civic Complaint Router UI. All server text is inserted with textContent (never innerHTML) to avoid XSS.
const $ = (id) => document.getElementById(id);
const state = { filter: "" };

const LABELS = { critical: "Critical", high: "High", medium: "Medium", low: "Low" };
const LANG_NAMES = { en: "English", hi: "Hindi", te: "Telugu", "hi-latn": "Hinglish", "te-latn": "Tenglish" };

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

function formatTime(iso) {
  return new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function toast(message, isError = false) {
  const t = $("toast");
  t.textContent = message;
  t.className = "toast" + (isError ? " error" : "");
  t.hidden = false;
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => (t.hidden = true), 3200);
}

async function api(path, options) {
  const res = await fetch(path, options);
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch (_) {}
    throw new Error(detail);
  }
  return res.json();
}

/* ---------- Health ---------- */
async function checkHealth() {
  const status = $("status");
  try {
    await api("/health");
    status.textContent = "Service online";
    status.className = "status ok";
  } catch (_) {
    status.textContent = "Service offline";
    status.className = "status down";
  }
}

/* ---------- Result panel ---------- */
function renderResult(t) {
  $("result-empty").hidden = true;
  const box = $("result");
  box.replaceChildren();
  box.hidden = false;

  const head = el("div", "result-head");
  const titleWrap = el("div");
  titleWrap.append(el("p", "muted", `Ticket #${t.id}`), el("p", "dept", t.department_name));
  const badge = el("span", `badge u-${t.urgency.level}`, `${LABELS[t.urgency.level]} urgency`);
  head.append(titleWrap, badge);

  const text = el("div", "result-text", t.text);

  const meta = el("dl", "meta");
  const addMeta = (label, value) => {
    const wrap = el("div");
    wrap.append(el("dt", null, label));
    const dd = el("dd");
    if (value instanceof Node) dd.append(value); else dd.textContent = value;
    wrap.append(dd);
    meta.append(wrap);
  };

  const confPct = Math.round(t.confidence * 100);
  const bar = el("div", "bar");
  const fill = el("span");
  fill.style.width = `${confPct}%`;
  bar.append(fill);
  const confWrap = el("div");
  confWrap.append(el("span", null, `${confPct}%`), bar);
  addMeta("Confidence", confWrap);

  addMeta("Language", LANG_NAMES[t.language] || t.language);
  addMeta("SLA deadline", formatTime(t.sla_due) + ` (${t.urgency.sla_hours} h)`);
  addMeta("Ward", t.location.ward ? `Ward ${t.location.ward}` : "Not mentioned");
  if (t.location.landmark) addMeta("Landmark", t.location.landmark);
  if (t.location.known_places.length) addMeta("Places found", t.location.known_places.join(", "));
  addMeta("Why this urgency", t.urgency.reason);

  box.append(head, text, meta);

  if (t.needs_human) {
    box.append(el("div", "notice notice-warn",
      "The model is not confident enough. This ticket was sent to a human triage queue."));
  }
  if (t.duplicate_of) {
    box.append(el("div", "notice notice-info",
      `Looks like a duplicate of ticket #${t.duplicate_of} (${Math.round(t.duplicate_similarity * 100)}% similar).`));
  }
}

/* ---------- Ticket list and stats ---------- */
function renderTicket(t) {
  const row = el("article", "ticket");
  row.append(el("span", `badge u-${t.urgency.level}`, LABELS[t.urgency.level]));

  const main = el("div", "ticket-main");
  main.append(el("p", "ticket-text", t.text));
  const sub = el("div", "ticket-sub");
  sub.append(el("span", null, t.department_name));
  if (t.location.ward) sub.append(el("span", null, `Ward ${t.location.ward}`));
  sub.append(el("span", "lang", LANG_NAMES[t.language] || t.language));
  if (t.needs_human) sub.append(el("span", null, "Needs triage"));
  if (t.duplicate_of) sub.append(el("span", "dup-tag", `Duplicate of #${t.duplicate_of}`));
  main.append(sub);

  const side = el("div", "ticket-side");
  side.append(el("p", "ticket-id", `#${t.id}`), el("p", null, formatTime(t.created_at)));

  row.append(main, side);
  return row;
}

function renderStats(all) {
  $("stat-total").textContent = all.length;
  $("stat-critical").textContent = all.filter((t) => t.urgency.level === "critical").length;
  $("stat-triage").textContent = all.filter((t) => t.needs_human).length;
  $("stat-dup").textContent = all.filter((t) => t.duplicate_of).length;
}

async function loadTickets() {
  try {
    const query = state.filter ? `?urgency=${encodeURIComponent(state.filter)}` : "";
    const [filtered, everything] = await Promise.all([
      api(`/complaints${query}`),
      state.filter ? api("/complaints") : null,
    ]);
    renderStats(everything || filtered);

    const list = $("ticket-list");
    list.replaceChildren(...filtered.map(renderTicket));
    $("ticket-empty").hidden = filtered.length > 0;
  } catch (err) {
    toast(`Could not load tickets: ${err.message}`, true);
  }
}

/* ---------- Actions ---------- */
async function submitComplaint(event) {
  event.preventDefault();
  const textarea = $("text");
  const text = textarea.value.trim();
  if (text.length < 3) return toast("Please write at least 3 characters.", true);

  const btn = $("submit-btn");
  btn.disabled = true;
  btn.textContent = "Routing…";
  try {
    const ticket = await api("/complaints", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, source: "web" }),
    });
    renderResult(ticket);
    textarea.value = "";
    updateCounter();
    toast(`Ticket #${ticket.id} created`);
    await loadTickets();
  } catch (err) {
    toast(`Submission failed: ${err.message}`, true);
  } finally {
    btn.disabled = false;
    btn.textContent = "Submit complaint";
  }
}

function updateCounter() {
  $("counter").textContent = `${$("text").value.length} / 2000`;
}

function setupEvents() {
  $("complaint-form").addEventListener("submit", submitComplaint);
  $("text").addEventListener("input", updateCounter);

  document.querySelectorAll(".chip").forEach((chip) =>
    chip.addEventListener("click", () => {
      $("text").value = chip.dataset.example;
      updateCounter();
      $("text").focus();
    })
  );

  document.querySelectorAll(".filter").forEach((btn) =>
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.filter = btn.dataset.filter;
      loadTickets();
    })
  );
}

document.addEventListener("DOMContentLoaded", () => {
  setupEvents();
  checkHealth();
  loadTickets();
  setInterval(checkHealth, 15000);
});
