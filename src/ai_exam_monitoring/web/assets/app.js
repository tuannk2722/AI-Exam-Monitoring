"use strict";
const $ = (id) => document.getElementById(id);
const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const labels = { phone_use: "Điện thoại", looking_around: "Nhìn quanh" };
const statuses = {
  candidate: "Chưa duyệt",
  confirmed: "Xác nhận",
  dismissed: "Bác bỏ FP",
  uncertain: "Chưa rõ",
};
const reasons = [
  "Tay/bàn bị che khuất",
  "Vật khác, không phải phone",
  "Cúi đọc/viết bài",
  "Hướng nhìn chưa rõ",
  "Box trùng",
  "Context chồng lấn",
  "Đứt/nhảy track",
  "Classifier báo nhầm",
];
const state = {
  data: null,
  review: null,
  sessionList: [],
  view: "hub",
  tab: "events",
  selected: null,
  frame: 0,
  anchor: null,
  playing: null,
  frameToken: 0,
  saveQueue: Promise.resolve(),
  editVersion: 0,
  dirty: false,
};
let toastTimer,
  saveTimer,
  sourceImage = null;
const time = (ms) => `${(ms / 1000).toFixed(1)}s`;
const score = (n) => (Number.isFinite(n) ? n.toFixed(4) : "—");
const date = (value) =>
  value
    ? new Date(value).toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" })
    : "—";
const shortId = (value) => String(value).split("-").at(-1);
const badge = (status) =>
  `<span class="badge ${esc(status)}">${esc(statuses[status] || status)}</span>`;
const decision = (item) =>
  state.review?.decisions[item?.event?.event_id] || {
    status: "candidate",
    note: "",
    reasons: [],
    flagged: false,
  };
const current = () => state.selected;
function toast(message, error = false) {
  clearTimeout(toastTimer);
  $("notice").textContent = message;
  $("notice").className = `toast${error ? " error" : ""}`;
  toastTimer = setTimeout(() => $("notice").classList.add("hidden"), 6000);
}
async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!response.ok) {
    let body;
    try {
      body = await response.json();
    } catch {
      body = { detail: `HTTP ${response.status}` };
    }
    throw new Error(body.detail || "Không thể hoàn tất yêu cầu");
  }
  return response.json();
}
const query = () => `identity=${encodeURIComponent(state.data.id)}`;
const imageURL = (frame, anchor = null, kind = "crop") =>
  `/api/image?${query()}&frame=${frame}${anchor ? `&anchor=${encodeURIComponent(anchor)}&kind=${kind}` : ""}`;
function setTheme(value) {
  document.documentElement.dataset.theme = value;
  try {
    localStorage.setItem("exam-review-theme", value);
  } catch {}
  $("theme").innerHTML =
    value === "dark"
      ? "☀ <span>Giao diện sáng</span>"
      : "☾ <span>Giao diện tối</span>";
  if (sourceImage) drawFrame();
}
try {
  setTheme(
    localStorage.getItem("exam-review-theme") ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"),
  );
} catch {
  setTheme("dark");
}
$("theme").onclick = () =>
  setTheme(
    document.documentElement.dataset.theme === "dark" ? "light" : "dark",
  );
function showView(view) {
  if (view !== "hub" && !state.data) return;
  stopPlayback();
  state.view = view;
  for (const id of ["hub", "work", "summary"])
    $(id).classList.toggle("hidden", id !== view);
  document
    .querySelectorAll("[data-view]")
    .forEach((b) => b.classList.toggle("active", b.dataset.view === view));
  if (view === "summary") renderSummary();
  if (view === "hub") loadHub();
  location.hash = view;
}
document
  .querySelectorAll("[data-view]")
  .forEach((b) => (b.onclick = () => showView(b.dataset.view)));
document.querySelector(".brand").onclick = (e) => {
  e.preventDefault();
  showView("hub");
};
window.addEventListener("hashchange", () => {
  const v = location.hash.slice(1);
  if (["hub", "work", "summary"].includes(v) && v !== state.view) showView(v);
});
async function loadHub() {
  try {
    state.sessionList = await api("/api/sessions");
    renderSessions();
    await loadJobs();
  } catch (e) {
    $("sessions").innerHTML =
      `<div class="empty error-text">${esc(e.message)}</div>`;
  }
}
function renderSessions() {
  const filter = $("session-filter").value;
  const sessions = state.sessionList.filter(
    (s) => filter === "all" || s.status === filter,
  );
  $("session-count").textContent = state.sessionList.length;
  $("sessions").innerHTML =
    sessions
      .map(
        (s) =>
          `<article class="session-card ${s.reviewable ? "reviewable" : ""}"><div class="card-top"><h3>${esc(s.event_run_id || s.runtime_id || s.id.split("/").at(-1))}</h3>${badge(s.status)}</div><div class="muted small mono">${esc(s.id)}</div>${s.reviewable ? `<div class="session-metrics"><div><strong>${s.event_count ?? "—"}</strong><small>Event candidates</small></div><div><strong>${s.counts_by_behavior?.phone_use ?? "—"}</strong><small>Điện thoại</small></div><div><strong>${s.counts_by_behavior?.looking_around ?? "—"}</strong><small>Nhìn quanh</small></div></div><div class="pipeline"><span>V8S → context-v1</span><span>G0 · 1 Hz</span><span>C10 · 10 Hz</span></div>` : `<p class="muted small" style="margin-top:12px">${esc(s.error_type || `${s.frames ?? 0} mẫu đã xử lý · ${s.observations ?? 0} observations`)}${s.status === "failed" ? " · Không dùng làm phiên nghiệm thu" : ""}</p>`}<div class="card-bottom"><span class="muted">Hạn media: ${date(s.media_delete_by)} VN</span>${s.reviewable ? `<button class="primary" data-open="${esc(s.id)}">Mở bàn duyệt →</button>` : `<button data-session-detail="${esc(s.id)}">Chi tiết phiên</button>`}</div></article>`,
      )
      .join("") || '<div class="empty">Không có phiên ở trạng thái này.</div>';
  $("sessions")
    .querySelectorAll(".session-card")
    .forEach((card, index) => {
      const session = sessions[index];
      if (!session.source_sha256) return;
      const info = document.createElement("p");
      info.className = "muted small mono";
      info.style.marginTop = "10px";
      info.title = session.source_sha256;
      info.textContent = `Source SHA ${session.source_sha256.slice(0, 12)}…${session.source_sha256.slice(-8)}${session.reviewable ? ` · Đã duyệt ${session.reviewed_count ?? 0}/${session.event_count}` : ""}`;
      card.querySelector(".card-bottom").before(info);
    });
  $("sessions")
    .querySelectorAll("[data-open]")
    .forEach((b) => (b.onclick = () => openSession(b.dataset.open)));
  $("sessions")
    .querySelectorAll("[data-session-detail]")
    .forEach(
      (b) =>
        (b.onclick = () =>
          openModal(
            "Chi tiết phiên",
            `<pre>${esc(
              JSON.stringify(
                state.sessionList.find((s) => s.id === b.dataset.sessionDetail),
                null,
                2,
              ),
            )}</pre>`,
          )),
    );
}
$("session-filter").onchange = renderSessions;
$("refresh").onclick = loadHub;
async function loadJobs() {
  const jobs = await api("/api/jobs");
  $("jobs").innerHTML = jobs
    .filter((j) => j.status !== "completed")
    .map(
      (j) =>
        `<div class="job-card"><div class="section-top"><strong>${esc(j.id)}</strong>${badge(j.status)}</div><p class="small">${esc(j.stage)} · ${j.stage === "runtime" ? `${j.runtime_frames_written ?? 0} mẫu G0 đã ghi` : `${j.completed_samples ?? 0} mẫu tracker`}</p>${j.status === "failed" ? `<p class="error-text small">${esc(j.error_type)} · ${esc(j.error)}</p>` : `<progress ${j.stage === "tracking" ? `value="${j.current_frame ?? 0}" max="${j.frames}"` : ""}></progress>`}</div>`,
    )
    .join("");
}
const jobInput = () => ({
  source: $("source").value.trim(),
  receipt: $("receipt").value.trim(),
});
$("preflight").onclick = async () => {
  const b = $("preflight");
  b.disabled = true;
  $("preflight-result").textContent = "Đang kiểm tra SHA256, video và receipt…";
  try {
    const r = await api("/api/preflight", {
      method: "POST",
      body: JSON.stringify(jobInput()),
    });
    $("preflight-result").innerHTML =
      `<p class="confirmed">✓ ${r.frames} frames · ${r.fps} FPS · ${r.duration_seconds.toFixed(1)} giây<br>✓ Quyền media & model pins hợp lệ<br>Hạn: ${date(r.media_delete_by)}</p>`;
  } catch (e) {
    $("preflight-result").innerHTML =
      `<p class="error-text">${esc(e.message)}</p>`;
  } finally {
    b.disabled = false;
  }
};
$("job-form").onsubmit = async (e) => {
  e.preventDefault();
  const b = e.submitter;
  b.disabled = true;
  try {
    await api("/api/jobs", {
      method: "POST",
      body: JSON.stringify(jobInput()),
    });
    toast("Đã xếp hàng xử lý trên máy này.");
    await loadHub();
  } catch (error) {
    toast(error.message, true);
  } finally {
    b.disabled = false;
  }
};
async function openSession(identity) {
  try {
    if (state.dirty) await flushSave();
    toast("Đang kiểm tra evidence và ghép frame/track…");
    const [data, review] = await Promise.all([
      api(`/api/session?identity=${encodeURIComponent(identity)}`),
      api(`/api/review?identity=${encodeURIComponent(identity)}`),
    ]);
    state.data = data;
    state.review = review;
    state.selected = null;
    state.anchor = null;
    state.tab = "events";
    state.frame = data.frames[0]?.frame_index ?? 0;
    state.dirty = false;
    state.editVersion = 0;
    document
      .querySelectorAll("[data-view]")
      .forEach((b) => (b.disabled = false));
    $("session-name").textContent = data.session.event_run_id;
    $("summary-name").textContent = data.id;
    $("acceptance").textContent = data.acceptance
      ? "✓ Batch accepted cho prototype · Từng event vẫn cần review"
      : "Chưa có batch acceptance";
    $("cadence").value = "1";
    $("search").value = "";
    $("status").value = "all";
    $("behavior").value = "all";
    setTab("events");
    updateProgress();
    updateRetention();
    showView("work");
    if (data.events.length) selectItem(data.events[0]);
    else {
      renderQueue();
      renderFrame();
      renderInspector();
      renderFilmstrip();
    }
    toast("Đã mở phiên. Quyết định review lưu riêng trong SQLite.");
  } catch (e) {
    toast(e.message, true);
  }
}
function updateRetention() {
  if (!state.data) return;
  const expired =
    Date.now() >= new Date(state.data.session.media_delete_by).getTime();
  $("retention").textContent =
    `${expired ? "Media đã hết hạn" : "Hạn lưu trữ media"}: ${date(state.data.session.media_delete_by)} VN · Owner-only`;
  $("retention").classList.toggle("error-text", expired);
  if (expired) {
    stopPlayback();
    sourceImage = null;
    $("canvas").getContext("2d").clearRect(0, 0, 1280, 720);
    $("media-state").textContent =
      "Đã quá hạn lưu trữ media. Chỉ hiển thị metadata và provenance.";
    $("media-state").classList.remove("hidden");
    $("input-image").removeAttribute("src");
    $("crop-canvas").getContext("2d").clearRect(0, 0, 336, 336);
    document
      .querySelectorAll("#filmstrip img")
      .forEach((i) => i.removeAttribute("src"));
  }
  return expired;
}
function updateProgress() {
  if (!state.data) return;
  const total = state.data.events.length;
  const count = state.data.events.filter(
    (e) => decision(e).status !== "candidate",
  ).length;
  $("progress-text").textContent = `${count} / ${total} sự kiện đã duyệt`;
  $("progress").value = total ? (count / total) * 100 : 0;
}
function shortItems() {
  return state.data.accounting.short_sequences.map((s, i) => ({
    ...s,
    event: {
      event_id: `short-${i}`,
      track_id: s.track_id,
      behavior: s.behavior,
      start_frame: s.support[0].frame_index,
      end_frame: s.support.at(-1).frame_index,
      start_time_ms: s.support[0].video_time_ms,
      end_time_ms: s.support.at(-1).video_time_ms,
      aggregated_confidence:
        s.support.reduce((a, b) => a + b.score, 0) / s.support.length,
    },
    support_count: s.support.length,
    short: true,
  }));
}
function filteredItems() {
  if (!state.data) return [];
  let items = state.tab === "short" ? shortItems() : state.data.events;
  const needle = $("search").value.toLowerCase().trim(),
    behavior = $("behavior").value,
    status = $("status").value;
  items = items.filter((item) => {
    const e = item.event,
      d = decision(item);
    return (
      (behavior === "all" || e.behavior === behavior) &&
      (state.tab === "short" ||
        status === "all" ||
        (status === "flagged" ? d.flagged : d.status === status)) &&
      (!needle ||
        `${e.event_id} T${e.track_id} ${d.note} ${d.reasons.join(" ")}`
          .toLowerCase()
          .includes(needle))
    );
  });
  return items.toSorted
    ? items.toSorted(sortItems)
    : [...items].sort(sortItems);
}
function sortItems(a, b) {
  const x = a.event,
    y = b.event;
  switch ($("sort").value) {
    case "score":
      return y.aggregated_confidence - x.aggregated_confidence;
    case "duration":
      return (
        y.end_time_ms - y.start_time_ms - (x.end_time_ms - x.start_time_ms)
      );
    case "track":
      return x.track_id - y.track_id;
    default:
      return (
        x.start_time_ms - y.start_time_ms ||
        x.event_id.localeCompare(y.event_id)
      );
  }
}
function setTab(tab) {
  state.tab = tab;
  document
    .querySelectorAll("[data-tab]")
    .forEach((b) => b.classList.toggle("active", b.dataset.tab === tab));
  $("status").disabled = tab !== "events";
  renderQueue();
}
document
  .querySelectorAll("[data-tab]")
  .forEach((b) => (b.onclick = () => setTab(b.dataset.tab)));
for (const id of ["search", "behavior", "status", "sort"])
  $(id).addEventListener(id === "search" ? "input" : "change", renderQueue);
function renderQueue() {
  if (!state.data) return;
  const list = $("queue-list");
  if (state.tab === "tracks") {
    const tracks = new Map();
    for (const row of state.data.assignments)
      for (const a of row.assignments) {
        const key = a.track_id ?? "null";
        if (!tracks.has(key)) tracks.set(key, []);
        tracks.get(key).push({
          frame: row.frame_index,
          time: row.video_time_ms,
          anchor: a.anchor_id,
        });
      }
    const needle = $("search").value.toLowerCase();
    const groups = [...tracks].filter(
      ([id]) => !needle || `t${id}`.includes(needle),
    );
    $("queue-count").textContent = groups.length;
    list.innerHTML = groups
      .map(
        ([id, samples]) =>
          `<button class="event-card" data-track="${id}"><div class="event-top"><strong>${id === "null" ? "? · Không có track" : `Track T${id}`}</strong><span class="badge">${samples.length} obs</span></div><div class="event-time">${time(samples[0].time)} → ${time(samples.at(-1).time)}</div><div class="details">${state.data.events.filter((e) => e.event.track_id === id).length} candidates · mã tạm thời</div></button>`,
      )
      .join("");
    list.querySelectorAll("[data-track]").forEach(
      (b) =>
        (b.onclick = () => {
          const id =
            b.dataset.track === "null" ? null : Number(b.dataset.track);
          const event = state.data.events.find((e) => e.event.track_id === id);
          if (event) {
            selectItem(event);
          } else {
            const sample = tracks.get(id ?? "null")[0];
            state.selected = null;
            state.frame = sample.frame;
            state.anchor = sample.anchor;
            renderFrame();
            renderInspector();
            renderFilmstrip();
          }
        }),
    );
    return;
  }
  const items = filteredItems();
  $("queue-count").textContent = items.length;
  list.innerHTML =
    items
      .map((item) => {
        const e = item.event,
          d = decision(item);
        return `<button class="event-card ${state.selected?.event.event_id === e.event_id ? "selected" : ""}" data-event="${esc(e.event_id)}"><div class="event-top"><span class="mono">${esc(shortId(e.event_id))} · T${e.track_id}</span>${item.short ? '<span class="badge">Chưa đủ rule</span>' : badge(d.status)}</div><div class="behavior ${e.behavior}">${labels[e.behavior]}${d.flagged ? " ⚑" : ""}</div><div class="event-time">${time(e.start_time_ms)} <span class="muted">→</span> ${time(e.end_time_ms)}</div><div class="details">${item.support_count} mẫu · span ${time(e.end_time_ms - e.start_time_ms)} · mean ${score(e.aggregated_confidence)}</div></button>`;
      })
      .join("") || '<div class="empty">Không có kết quả khớp bộ lọc.</div>';
  list
    .querySelectorAll("[data-event]")
    .forEach(
      (b) =>
        (b.onclick = () =>
          selectItem(items.find((i) => i.event.event_id === b.dataset.event))),
    );
}
function selectItem(item) {
  if (!item) return;
  stopPlayback();
  state.selected = item;
  state.frame = item.event.start_frame;
  state.anchor = item.support[0].anchor_id;
  renderQueue();
  renderInspector();
  renderFilmstrip();
  renderFrame();
}
function frameRows() {
  return $("cadence").value === "10"
    ? state.data.assignments
    : state.data.frames;
}
function frameData() {
  return state.data.frames.find((f) => f.frame_index === state.frame);
}
function assignmentData() {
  return state.data.assignments.find((f) => f.frame_index === state.frame);
}
function selectedObs() {
  const f = frameData();
  if (!f) return null;
  return (
    f.observations.find((o) => o.anchor_id === state.anchor) ||
    f.observations.find((o) => o.track_id === current()?.event.track_id) ||
    null
  );
}
function syncAnchor() {
  const row = assignmentData();
  const support = current()?.support.find((s) => s.frame_index === state.frame);
  state.anchor =
    support?.anchor_id ||
    row?.assignments.find((a) => a.track_id === current()?.event.track_id)
      ?.anchor_id ||
    null;
}
async function renderFrame() {
  if (!state.data) return;
  const token = ++state.frameToken;
  sourceImage?.close();
  sourceImage = null;
  const canvas = $("canvas");
  canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
  const f = frameData(),
    r = assignmentData();
  const stamp = r?.video_time_ms ?? 0;
  $("frame-info").textContent =
    `Frame #${String(state.frame).padStart(8, "0")} · ${stamp.toFixed(0)} ms · ${f ? "G0 1 Hz" : "C10 10 Hz"}`;
  $("cadence-info").textContent = f
    ? "Có điểm classifier"
    : "Chỉ detector / tracker";
  $("clock").textContent = time(stamp);
  const samples = frameRows();
  $("scrubber").max = Math.max(0, samples.length - 1);
  $("scrubber").value = Math.max(
    0,
    samples.findIndex((s) => s.frame_index === state.frame),
  );
  renderTimeline();
  renderEvidence();
  if (updateRetention()) return;
  $("media-state").textContent = "Đang tải frame nguồn…";
  $("media-state").classList.remove("hidden");
  try {
    const res = await fetch(imageURL(state.frame));
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail);
    }
    const blob = await res.blob();
    const image = await createImageBitmap(blob);
    if (token !== state.frameToken) {
      image.close();
      return;
    }
    if (updateRetention()) {
      image.close();
      return;
    }
    sourceImage = image;
    canvas.width = image.width;
    canvas.height = image.height;
    $("media-state").classList.add("hidden");
    drawFrame();
  } catch (e) {
    if (token !== state.frameToken) return;
    $("media-state").textContent = e.message;
    $("media-state").classList.remove("hidden");
  }
  renderFilmstripSelection();
}
function drawFrame() {
  if (!sourceImage) return;
  const canvas = $("canvas"),
    ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(sourceImage, 0, 0);
  const r = assignmentData(),
    f = frameData();
  const selected = r?.assignments.find((a) => a.anchor_id === state.anchor);
  if ($("spotlight").checked && selected) {
    ctx.fillStyle = "#07101ba6";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    const [x, y, x2, y2] = selected.person_box;
    const margin = 25;
    const sx = Math.max(0, x - margin),
      sy = Math.max(0, y - margin),
      w = Math.min(canvas.width - sx, x2 - x + margin * 2),
      h = Math.min(canvas.height - sy, y2 - y + margin * 2);
    ctx.drawImage(sourceImage, sx, sy, w, h, sx, sy, w, h);
  }
  for (const a of r?.assignments || []) {
    const obs = f?.observations.find((o) => o.anchor_id === a.anchor_id);
    const active = a.anchor_id === state.anchor;
    const color =
      a.track_id === null
        ? "#ff4f58"
        : `hsl(${(a.track_id * 137.5) % 360},85%,65%)`;
    ctx.globalAlpha = active ? 1 : $("spotlight").checked ? 0.42 : 0.9;
    if ($("person-overlay").checked) {
      const [x, y, x2, y2] = a.person_box;
      ctx.strokeStyle = color;
      ctx.lineWidth = active ? 4 : 2;
      ctx.setLineDash([]);
      ctx.strokeRect(x, y, x2 - x, y2 - y);
      let caption = `${a.track_id === null ? "?" : `T${a.track_id}`} / ${a.anchor_id.split("-").at(-1)}`;
      if (obs && $("scores-overlay").checked)
        caption += ` P ${obs.scores[0].toFixed(2)} · L ${obs.scores[1].toFixed(2)}`;
      ctx.font = `${active ? "bold " : ""}13px Consolas`;
      const width = ctx.measureText(caption).width + 8;
      ctx.fillStyle = "#08121ee6";
      ctx.fillRect(x, Math.max(0, y - 20), width, 19);
      ctx.fillStyle = color;
      ctx.fillText(caption, x + 4, Math.max(14, y - 6));
    }
    if (
      $("context-overlay").checked &&
      obs &&
      (active || !$("spotlight").checked)
    ) {
      const [x, y, x2, y2] = obs.context_box;
      ctx.setLineDash([7, 5]);
      ctx.strokeStyle = "#ffb65c";
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, x2 - x, y2 - y);
    }
  }
  ctx.globalAlpha = 1;
  ctx.setLineDash([]);
}
for (const id of [
  "person-overlay",
  "context-overlay",
  "spotlight",
  "scores-overlay",
])
  $(id).onchange = drawFrame;
$("canvas").onclick = (e) => {
  const rect = e.currentTarget.getBoundingClientRect(),
    x = ((e.clientX - rect.left) / rect.width) * e.currentTarget.width,
    y = ((e.clientY - rect.top) / rect.height) * e.currentTarget.height;
  const hits = (assignmentData()?.assignments || [])
    .filter(
      (a) =>
        x >= a.person_box[0] &&
        x <= a.person_box[2] &&
        y >= a.person_box[1] &&
        y <= a.person_box[3],
    )
    .sort(
      (a, b) =>
        (a.person_box[2] - a.person_box[0]) *
          (a.person_box[3] - a.person_box[1]) -
        (b.person_box[2] - b.person_box[0]) *
          (b.person_box[3] - b.person_box[1]),
    );
  if (hits.length) {
    state.anchor = hits[0].anchor_id;
    drawFrame();
    renderEvidence();
    toast(
      `Đang xem ${state.anchor} · ${hits[0].track_id === null ? "Không có track" : `T${hits[0].track_id}`}`,
    );
  }
};
$("zoom").onclick = () => $("canvas-wrap").classList.toggle("zoomed");
function seek(frame) {
  state.frame = frame;
  syncAnchor();
  renderFrame();
}
function step(delta) {
  const samples = frameRows(),
    i = samples.findIndex((s) => s.frame_index === state.frame);
  seek(
    samples[Math.min(samples.length - 1, Math.max(0, i + delta))].frame_index,
  );
}
$("prev").onclick = () => step(-1);
$("next").onclick = () => step(1);
$("first").onclick = () =>
  seek(current()?.event.start_frame ?? frameRows()[0].frame_index);
$("last").onclick = () =>
  seek(current()?.event.end_frame ?? frameRows().at(-1).frame_index);
$("scrubber").oninput = () =>
  seek(frameRows()[Number($("scrubber").value)].frame_index);
$("cadence").onchange = () => {
  stopPlayback();
  const samples = frameRows();
  seek(
    samples.reduce((a, b) =>
      Math.abs(b.frame_index - state.frame) <
      Math.abs(a.frame_index - state.frame)
        ? b
        : a,
    ).frame_index,
  );
};
function stopPlayback() {
  if (state.playing) {
    clearInterval(state.playing);
    state.playing = null;
  }
  $("play").textContent = "▶ Phát đoạn";
}
function togglePlayback() {
  if (state.playing) {
    stopPlayback();
    return;
  }
  if (updateRetention()) return;
  $("play").textContent = "Ⅱ Tạm dừng";
  const hz = Number($("cadence").value);
  state.playing = setInterval(() => {
    const end = current()?.event.end_frame ?? frameRows().at(-1).frame_index;
    if (state.frame >= end)
      seek(current()?.event.start_frame ?? frameRows()[0].frame_index);
    else step(1);
  }, 1000 / hz);
}
$("play").onclick = togglePlayback;
function renderInspector() {
  const item = current(),
    d = decision(item);
  $("event-title").textContent = item
    ? `${labels[item.event.behavior]} · T${item.event.track_id}`
    : "Quan sát frame";
  $("event-meta").textContent = item
    ? `${shortId(item.event.event_id)} · ${time(item.event.start_time_ms)} — ${time(item.event.end_time_ms)} · ${item.support_count} mẫu${item.short ? " · Chuỗi chưa đủ rule" : ""}`
    : "Chọn một candidate để ghi quyết định";
  if (item) {
    $("event-meta").textContent +=
      ` · Mean ${score(item.event.aggregated_confidence)} · min ${score(Math.min(...item.support.map((s) => s.score)))} / max ${score(Math.max(...item.support.map((s) => s.score)))}`;
  }
  $("decision-status").textContent = statuses[d.status];
  $("decision-status").className = `badge ${d.status}`;
  $("note").value = d.note;
  $("flag").checked = d.flagged;
  $("reasons").innerHTML = reasons
    .map(
      (reason) =>
        `<button class="${d.reasons.includes(reason) ? "active" : ""}" data-reason="${esc(reason)}">${esc(reason)}</button>`,
    )
    .join("");
  const disabled = !item || item.short;
  document
    .querySelectorAll(".decisions button,.decisions input,.decisions textarea")
    .forEach((e) => (e.disabled = !!disabled));
  document.querySelectorAll("[data-decision]").forEach((b) => {
    b.classList.toggle("active", b.dataset.decision === d.status);
  });
  $("reasons")
    .querySelectorAll("button")
    .forEach(
      (b) =>
        (b.onclick = () => {
          editDecision((d) => {
            d.reasons = d.reasons.includes(b.dataset.reason)
              ? d.reasons.filter((r) => r !== b.dataset.reason)
              : [...d.reasons, b.dataset.reason];
          });
          renderInspector();
        }),
    );
}
async function renderEvidence() {
  const token = state.frameToken,
    obs = selectedObs();
  $("crop-canvas").getContext("2d").clearRect(0, 0, 336, 336);
  $("input-image").removeAttribute("src");
  $("crop-state").textContent = obs
    ? "Đang tải…"
    : "Không có crop G0 tại mốc này";
  $("input-state").textContent = obs ? "Đang tải…" : "Không có input G0";
  $("anchor-info").textContent = obs
    ? `${obs.anchor_id} · T${obs.track_id ?? "?"} · det ${score(obs.detector_confidence)}\nBox [${obs.person_box.join(", ")}]`
    : "Không có observation classifier cho target tại frame này.";
  $("scores").innerHTML = obs
    ? state.data.metadata.target_order
        .map(
          (label, i) =>
            `<div class="score-row ${label}"><div>${labels[label]}<div class="score-bar"><i style="width:${obs.scores[i] * 100}%"></i></div></div><span class="mono">${score(obs.scores[i])}</span><span class="mono muted" title="Ngưỡng">${score(state.data.metadata.thresholds[i])}</span><span class="${obs.above_threshold[i] ? "confirmed" : "muted"}">${obs.above_threshold[i] ? "＋" : "−"}</span></div>`,
        )
        .join("")
    : "";
  if (!obs || updateRetention()) return;
  try {
    const res = await fetch(imageURL(state.frame, obs.anchor_id));
    if (!res.ok) {
      const e = await res.json();
      throw new Error(e.detail);
    }
    const image = await createImageBitmap(await res.blob());
    if (
      token !== state.frameToken ||
      obs.anchor_id !== selectedObs()?.anchor_id
    ) {
      image.close();
      return;
    }
    const canvas = $("crop-canvas"),
      ctx = canvas.getContext("2d");
    const scale = 336 / Math.max(image.width, image.height),
      w = image.width * scale,
      h = image.height * scale,
      x = (336 - w) / 2,
      y = (336 - h) / 2;
    ctx.drawImage(image, x, y, w, h);
    ctx.strokeStyle = "#ffb65c";
    ctx.lineWidth = 2;
    const b = obs.person_box,
      c = obs.context_box;
    ctx.strokeRect(
      x + (b[0] - c[0]) * scale,
      y + (b[1] - c[1]) * scale,
      (b[2] - b[0]) * scale,
      (b[3] - b[1]) * scale,
    );
    image.close();
    $("crop-state").textContent = "";
    const input = $("input-image");
    input.onload = () => {
      if (token === state.frameToken) $("input-state").textContent = "";
    };
    input.onerror = () => {
      if (token === state.frameToken)
        $("input-state").textContent = "Không tải được input";
    };
    input.src = imageURL(state.frame, obs.anchor_id, "input");
  } catch (e) {
    if (token === state.frameToken) {
      $("crop-state").textContent = e.message;
      $("input-state").textContent = "Evidence chưa có ảnh";
    }
  }
}
function renderFilmstrip() {
  const item = current();
  $("support-count").textContent = item?.support.length ?? 0;
  if (updateRetention()) {
    $("filmstrip").replaceChildren();
    return;
  }
  $("filmstrip").innerHTML = (item?.support || [])
    .map(
      (s) =>
        `<button data-frame="${s.frame_index}" title="${esc(s.anchor_id)}"><img loading="lazy" src="${imageURL(s.frame_index, s.anchor_id)}" alt="Crop ${s.frame_index}">${time(s.video_time_ms)}<small>${s.anchor_id.split("-").at(-1)}</small>${s.score.toFixed(3)}</button>`,
    )
    .join("");
  $("filmstrip")
    .querySelectorAll("button")
    .forEach((b) => (b.onclick = () => seek(Number(b.dataset.frame))));
  $("filmstrip")
    .querySelectorAll("img")
    .forEach(
      (i) =>
        (i.onerror = () => {
          i.removeAttribute("src");
          i.alt = "Thiếu ảnh";
        }),
    );
  renderFilmstripSelection();
}
function renderFilmstripSelection() {
  $("filmstrip")
    .querySelectorAll("button")
    .forEach((b) =>
      b.classList.toggle("active", Number(b.dataset.frame) === state.frame),
    );
}
function renderTimeline() {
  const data = state.data,
    max = Math.max(1, data.frames.at(-1)?.video_time_ms ?? 1),
    stamp = assignmentData()?.video_time_ms ?? 0;
  let html = `<div class="axis"><span>0s</span><span>${time(max / 2)}</span><span>${time(max)}</span></div>`;
  html += `<div class="timeline-lane"><span class="lane-label">Mẫu 1 Hz</span><div class="sample-ticks">${data.frames.map((frame) => `<button data-sample="${frame.frame_index}" class="${data.metadata.qa_frame_indices?.includes(frame.frame_index) ? "qa" : ""}" title="${time(frame.video_time_ms)}${data.metadata.qa_frame_indices?.includes(frame.frame_index) ? " · QA tĩnh" : ""}"></button>`).join("")}</div></div>`;
  for (const label of data.metadata.target_order) {
    const events = data.events.filter((i) => i.event.behavior === label);
    const lanes = [];
    const positioned = events.map((item) => {
      let lane = lanes.findIndex((end) => end < item.event.start_time_ms);
      if (lane < 0) lane = lanes.length;
      lanes[lane] = item.event.end_time_ms;
      return { item, lane };
    });
    html += `<div class="timeline-lane"><span class="lane-label behavior ${label}">${labels[label]}</span><div class="lane-content" style="height:${Math.max(25, lanes.length * 8 + 4)}px">${positioned
      .map(({ item, lane }) => {
        const e = item.event;
        return `<button title="${shortId(e.event_id)} · T${e.track_id} · ${time(e.start_time_ms)}–${time(e.end_time_ms)}" class="timeline-event ${label} ${decision(item).status} ${current()?.event.event_id === e.event_id ? "selected" : ""}" data-timeline="${esc(e.event_id)}" style="left:${(e.start_time_ms / max) * 100}%;width:${Math.max(0.8, ((e.end_time_ms - e.start_time_ms) / max) * 100)}%;top:${lane * 8 + 3}px"></button>`;
      })
      .join(
        "",
      )}<i class="playhead" style="left:${Math.min(100, (stamp / max) * 100)}%"></i></div></div>`;
  }
  $("timeline").innerHTML = html;
  $("timeline")
    .querySelectorAll("[data-sample]")
    .forEach((button) => {
      button.onclick = () => seek(Number(button.dataset.sample));
    });
  $("timeline")
    .querySelectorAll("[data-timeline]")
    .forEach(
      (b) =>
        (b.onclick = () => {
          setTab("events");
          selectItem(
            data.events.find((e) => e.event.event_id === b.dataset.timeline),
          );
        }),
    );
  const item = current();
  if (!item) {
    $("track-strip").innerHTML = "";
    return;
  }
  const target = data.metadata.target_order.indexOf(item.event.behavior),
    threshold = data.metadata.thresholds[target];
  const values = data.frames.map((f) => {
    const o = f.observations.find((o) => o.track_id === item.event.track_id);
    return {
      frame: f.frame_index,
      score: o?.scores?.[target],
      positive: o?.above_threshold?.[target],
      support: item.support.some((s) => s.frame_index === f.frame_index),
    };
  });
  const lines = values
    .slice(1)
    .map((v, i) =>
      values[i].score != null && v.score != null
        ? `<line x1="${(i / (values.length - 1)) * 1000}" y1="${36 - values[i].score * 32}" x2="${((i + 1) / (values.length - 1)) * 1000}" y2="${36 - v.score * 32}" stroke="var(--accent)" stroke-width="2"/>`
        : "",
    )
    .join("");
  $("track-strip").innerHTML =
    `<div class="section-top small" style="margin:14px 0 2px"><span>Track T${item.event.track_id} · ${labels[item.event.behavior]}</span><span class="muted">Ngưỡng ${score(threshold)}</span></div><svg class="sparkline" viewBox="0 0 1000 40" preserveAspectRatio="none"><line x1="0" x2="1000" y1="${36 - threshold * 32}" y2="${36 - threshold * 32}" stroke="var(--muted)" stroke-dasharray="5 5"/>${lines}</svg><div class="track-cells">${values.map((v) => `<button data-frame="${v.frame}" title="Frame ${v.frame} · ${score(v.score)}" class="${v.score == null ? "missing" : v.positive ? `positive ${item.event.behavior} ${v.support ? "" : "short"}` : ""}">${v.support ? "★" : ""}</button>`).join("")}</div>`;
  $("track-strip")
    .querySelectorAll("button")
    .forEach((b) => (b.onclick = () => seek(Number(b.dataset.frame))));
}
function editDecision(change) {
  const item = current();
  if (!item || item.short) return;
  const d = structuredClone(decision(item));
  change(d);
  state.review.decisions[item.event.event_id] = d;
  markDirty();
  updateProgress();
  renderQueue();
  renderTimeline();
}
function markDirty() {
  state.dirty = true;
  state.editVersion++;
  $("save-status").textContent = "Đang lưu…";
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => flushSave().catch(() => {}), 400);
}
function flushSave() {
  clearTimeout(saveTimer);
  const identity = state.data?.id;
  if (!identity || !state.dirty) return state.saveQueue;
  state.saveQueue = state.saveQueue
    .catch(() => {})
    .then(async () => {
      if (!state.dirty || state.data.id !== identity) return;
      const version = state.editVersion,
        payload = structuredClone(state.review);
      try {
        const saved = await api(
          `/api/review?identity=${encodeURIComponent(identity)}`,
          { method: "PUT", body: JSON.stringify(payload) },
        );
        state.review.revision = saved.revision;
        state.review.updated_at = saved.updated_at;
        if (version === state.editVersion) state.dirty = false;
        $("save-status").textContent =
          `Đã lưu ${new Date(saved.updated_at).toLocaleTimeString("vi-VN")}`;
      } catch (e) {
        $("save-status").textContent =
          "Chưa lưu · thử lại bằng Lưu & tiếp theo";
        toast(e.message, true);
        throw e;
      }
    });
  return state.saveQueue;
}
document.querySelectorAll("[data-decision]").forEach(
  (b) =>
    (b.onclick = () => {
      editDecision((d) => (d.status = b.dataset.decision));
      renderInspector();
    }),
);
$("note").oninput = () => editDecision((d) => (d.note = $("note").value));
$("flag").onchange = () => editDecision((d) => (d.flagged = $("flag").checked));
$("reset").onclick = () => {
  editDecision((d) => {
    d.status = "candidate";
  });
  renderInspector();
};
$("save-next").onclick = async () => {
  try {
    await flushSave();
    const all = state.data.events;
    const i = all.findIndex(
      (e) => e.event.event_id === current()?.event.event_id,
    );
    const next = [...all.slice(i + 1), ...all.slice(0, i)].find(
      (e) => decision(e).status === "candidate",
    );
    if (next) {
      $("status").value = "all";
      $("search").value = "";
      $("behavior").value = "all";
      setTab("events");
      selectItem(next);
    } else toast("Không còn candidate chưa duyệt. Bạn có thể xem Tổng kết.");
  } catch {}
};
window.addEventListener("beforeunload", (e) => {
  if (state.dirty) {
    e.preventDefault();
    e.returnValue = "";
  }
});
function download(name, content, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
async function exportReview() {
  try {
    await flushSave();
    download(
      "event-review.json",
      JSON.stringify(state.review, null, 2),
      "application/json",
    );
    toast("Đã xuất quyết định review kèm SHA256 evidence.");
  } catch {}
}
$("export").onclick = exportReview;
$("summary-export").onclick = exportReview;
$("import").onclick = () => $("import-file").click();
$("import-file").onchange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  try {
    const imported = JSON.parse(await file.text());
    if (
      imported.schema_version !== "event-human-review-v1" ||
      imported.events_sha256 !== state.data.events_sha256
    )
      throw new Error("JSON khác schema hoặc SHA256 phiên. Không nhập.");
    const ids = new Set(state.data.events.map((e) => e.event.event_id));
    if (
      !imported.decisions ||
      Object.keys(imported.decisions).some((id) => !ids.has(id))
    )
      throw new Error("Có event không thuộc phiên.");
    openModal(
      "Nhập quyết định review",
      `<p>File có <strong>${Object.keys(imported.decisions).length}</strong> quyết định, cùng SHA256 evidence. Nhập sẽ thay bản review hiện tại; artifacts AI giữ nguyên.</p><button id="confirm-import" class="primary">Nhập bản review này</button>`,
    );
    $("confirm-import").onclick = async () => {
      try {
        await flushSave();
        const saved = await api(`/api/review?${query()}`, {
          method: "PUT",
          body: JSON.stringify({
            ...imported,
            revision: state.review.revision,
          }),
        });
        state.review = saved;
        state.dirty = false;
        renderInspector();
        renderQueue();
        renderTimeline();
        updateProgress();
        $("modal").close();
        toast("Đã nhập và lưu vào SQLite.");
      } catch (error) {
        toast(error.message, true);
      }
    };
  } catch (error) {
    toast(error.message, true);
  } finally {
    e.target.value = "";
  }
};
function renderSummary() {
  const data = state.data,
    all = data.events;
  const counts = Object.fromEntries(
    Object.keys(statuses).map((s) => [
      s,
      all.filter((e) => decision(e).status === s).length,
    ]),
  );
  $("summary-stats").innerHTML = Object.entries(counts)
    .map(
      ([s, n]) =>
        `<div class="stat"><small>${statuses[s]}</small><strong class="${s}">${n}</strong></div>`,
    )
    .join("");
  $("summary-table").innerHTML =
    `<table><thead><tr><th>Hành vi</th><th>Tổng</th>${Object.values(statuses)
      .map((s) => `<th>${s}</th>`)
      .join("")}</tr></thead><tbody>${data.metadata.target_order
      .map((b) => {
        const items = all.filter((e) => e.event.behavior === b);
        return `<tr><td><span class="behavior ${b}">${labels[b]}</span></td><td>${items.length}</td>${Object.keys(
          statuses,
        )
          .map(
            (s) =>
              `<td>${items.filter((e) => decision(e).status === s).length}</td>`,
          )
          .join("")}</tr>`;
      })
      .join("")}</tbody></table>`;
  const keys = [
    "positive_assigned",
    "event_support",
    "short_support",
    "negative_assigned",
    "unknown_assigned",
    "null_track",
  ];
  const names = [
    "Dương có ID",
    "Hỗ trợ event",
    "Dương chuỗi ngắn",
    "Âm có ID",
    "Unknown",
    "Null ID",
  ];
  const pass = Object.values(data.accounting.behaviors).every(
    (v) =>
      v.positive_assigned === v.event_support + v.short_support &&
      v.positive_assigned +
        v.negative_assigned +
        v.unknown_assigned +
        v.null_track ===
        data.accounting.observations,
  );
  $("accounting-pass").textContent = pass
    ? "✓ Đối soát khớp"
    : "✕ Đối soát không khớp";
  $("accounting-pass").className = `badge ${pass ? "confirmed" : "dismissed"}`;
  $("accounting").innerHTML =
    `<p class="muted small" style="margin-bottom:12px">${data.accounting.frames} frames · ${data.accounting.observations} observations · Dương có ID = support event + support chuỗi ngắn</p><table><thead><tr><th>Hành vi</th>${names.map((n) => `<th>${n}</th>`).join("")}</tr></thead><tbody>${Object.entries(
      data.accounting.behaviors,
    )
      .map(
        ([b, v]) =>
          `<tr><td>${labels[b]}</td>${keys.map((k) => `<td class="mono">${v[k]}</td>`).join("")}</tr>`,
      )
      .join("")}</tbody></table>`;
  const flags = all.filter((e) => decision(e).flagged);
  $("flagged-list").innerHTML =
    flags
      .map((item) => {
        const e = item.event,
          d = decision(item);
        return `<div class="flagged-row"><div><strong class="small">${shortId(e.event_id)} · T${e.track_id} · ${labels[e.behavior]}</strong><p>${esc(d.note || "Chưa có ghi chú")}</p>${badge(d.status)}</div><button data-revisit="${esc(e.event_id)}">Xem lại ↗</button></div>`;
      })
      .join("") || '<div class="empty">Chưa có ca được đánh dấu.</div>';
  $("flagged-list")
    .querySelectorAll("button")
    .forEach(
      (b) =>
        (b.onclick = () => {
          showView("work");
          setTab("events");
          selectItem(all.find((e) => e.event.event_id === b.dataset.revisit));
        }),
    );
  $("summary-note").value = state.review.summary;
  $("disposition").value = state.review.disposition;
}
$("back-work").onclick = () => showView("work");
$("summary-note").oninput = () => {
  state.review.summary = $("summary-note").value;
  markDirty();
};
$("disposition").onchange = () => {
  state.review.disposition = $("disposition").value;
  markDirty();
};
$("markdown").onclick = async () => {
  try {
    await flushSave();
    const data = state.data;
    const text =
      `# Tổng kết human review\n\nPhiên: ${data.session.event_run_id}\n\nEvidence SHA256: ${data.events_sha256}\n\nHạn media: ${date(data.session.media_delete_by)} VN\n\n` +
      Object.keys(statuses)
        .map(
          (s) =>
            `- ${statuses[s]}: ${data.events.filter((e) => decision(e).status === s).length}`,
        )
        .join("\n") +
      `\n\nĐánh giá phiên: ${state.review.disposition}\n\n${state.review.summary}\n\n## Ca đánh dấu\n\n` +
      data.events
        .filter((e) => decision(e).flagged)
        .map(
          (e) =>
            `- ${e.event.event_id} · T${e.event.track_id} · ${statuses[decision(e).status]}: ${decision(e).note}`,
        )
        .join("\n") +
      "\n\nTrack là mã tạm thời. Kết quả mô tả hành vi, không kết luận gian lận. Điểm classifier không phải risk.\n";
    download("review-summary.md", text, "text/markdown;charset=utf-8");
  } catch {}
};
function openModal(title, body) {
  $("modal-title").textContent = title;
  $("modal-body").innerHTML = body;
  $("modal").showModal();
}
$("close-modal").onclick = () => $("modal").close();
$("modal").onclick = (e) => {
  if (e.target === $("modal")) {
    const r = $("modal").getBoundingClientRect();
    if (
      e.clientX < r.left ||
      e.clientX > r.right ||
      e.clientY < r.top ||
      e.clientY > r.bottom
    )
      $("modal").close();
  }
};
$("pins").onclick = () => {
  const d = state.data;
  openModal(
    "Nguồn dữ liệu & provenance",
    `<p><strong>Source SHA256</strong></p><pre>${esc(d.provenance.source_sha256)}</pre><p>${d.metadata.fps} FPS · ${d.metadata.source_frame_count} source frames · Hạn media ${date(d.session.media_delete_by)} VN</p><p>G0 thresholds: ${d.metadata.thresholds.map(score).join(" / ")} · Crop ${esc(d.metadata.crop_policy.version)}</p><details open><summary>Event / tracker / runtime pins</summary><pre>${esc(JSON.stringify(d.provenance, null, 2))}</pre></details><p>Đã đối chiếu SHA của artifacts đọc và ghép frame/time/anchor/box. Model pins là provenance của inference, không phải một lần chạy model mới.</p>`,
  );
};
$("connect").onclick = () => {
  openModal(
    "Kết nối video gốc",
    `<p>Chỉ đọc MP4 local khớp SHA256 của phiên. Dùng để giải mã đúng frame chưa có ảnh cache.</p><label>Đường dẫn MP4<input id="connect-path" placeholder="D:\videos\clip.mp4"></label><button id="connect-submit" class="primary">Kiểm SHA256 & kết nối</button>`,
  );
  $("connect-submit").onclick = async () => {
    const b = $("connect-submit");
    b.disabled = true;
    try {
      await api("/api/source", {
        method: "POST",
        body: JSON.stringify({
          identity: state.data.id,
          source: $("connect-path").value,
        }),
      });
      $("modal").close();
      toast("Đã kết nối đúng video nguồn.");
      renderFrame();
      renderFilmstrip();
    } catch (e) {
      toast(e.message, true);
    } finally {
      b.disabled = false;
    }
  };
};
$("help").onclick = () =>
  openModal(
    "Quy tắc review & phím tắt",
    `<p><strong>Điện thoại:</strong> Thấy điện thoại di động đang được cầm/tương tác hoặc đặt trên bàn/sách gắn đúng người trong anchor. Máy tính cầm tay, bút, thước và điện thoại bàn không tính. Vật nhìn thấy nhưng chưa phân biệt được: chọn Chưa rõ.</p><p><strong>Nhìn quanh:</strong> Đầu/hướng nhìn quay rõ sang bên/sau hoặc sang vùng bài người khác. Cúi đọc/viết bài của mình không tính.</p><p>Batch accepted không tự xác nhận từng event. Chuỗi ngắn chưa đủ rule không được duyệt như một candidate. Không gộp track ID hoặc tự điền điểm ở mốc không có G0.</p><table><tr><td><kbd>←</kbd> <kbd>→</kbd></td><td>Mẫu trước / sau theo nhịp đang xem</td></tr><tr><td><kbd>↑</kbd> <kbd>↓</kbd></td><td>Candidate trước / sau</td></tr><tr><td><kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd></td><td>Xác nhận / bác bỏ / chưa rõ</td></tr><tr><td><kbd>F</kbd></td><td>Bật/tắt focus</td></tr><tr><td><kbd>Space</kbd></td><td>Phát / tạm dừng đoạn</td></tr><tr><td><kbd>Enter</kbd></td><td>Lưu & đến candidate chưa duyệt tiếp theo</td></tr></table><p class="muted">Phím tắt không chạy khi đang nhập nội dung hoặc mở hộp thoại.</p>`,
  );
document.addEventListener("keydown", (e) => {
  if (
    state.view !== "work" ||
    $("modal").open ||
    e.ctrlKey ||
    e.altKey ||
    e.metaKey ||
    ["INPUT", "TEXTAREA", "SELECT"].includes(e.target.tagName)
  )
    return;
  const actions = {
    ArrowLeft: () => step(-1),
    ArrowRight: () => step(1),
    " ": togglePlayback,
    f: () => {
      $("spotlight").checked = !$("spotlight").checked;
      drawFrame();
    },
    Enter: () => $("save-next").click(),
    1: () => document.querySelector('[data-decision="confirmed"]').click(),
    2: () => document.querySelector('[data-decision="dismissed"]').click(),
    3: () => document.querySelector('[data-decision="uncertain"]').click(),
  };
  if (e.key === "ArrowUp" || e.key === "ArrowDown") {
    e.preventDefault();
    const items = filteredItems(),
      i = items.findIndex(
        (x) => x.event.event_id === current()?.event.event_id,
      );
    selectItem(
      items[
        Math.max(
          0,
          Math.min(items.length - 1, i + (e.key === "ArrowDown" ? 1 : -1)),
        )
      ],
    );
  } else if (actions[e.key]) {
    e.preventDefault();
    actions[e.key]();
  }
});
setInterval(() => {
  if (state.view === "hub") loadHub();
  updateRetention();
}, 5000);
loadHub();
