"use strict";
const $ = (id) => document.getElementById(id);
const states = { uploading: "Đang nhận video", ready: "Video sẵn sàng", starting: "Đang khởi tạo AI", running: "Đang phát & phân tích", paused: "Đã tạm dừng", stopping: "Đang dừng, chờ AI giải phóng", stopped: "Phiên đã dừng", completed: "Video đã kết thúc", failed: "Không hoàn tất phiên" };
const labels = { phone_use: "Dùng điện thoại", looking_around: "Nhìn quanh" };
let snapshot = { session: null }, events = null, eventSession = null, imageKey = null;
let pending = false, dragging = false, receivedAt = performance.now(), ageAtReceive = null;
let expiryChecked = null;
const terminal = (status) => ["completed", "stopped", "failed"].includes(status);
const seconds = (ms) => Number.isFinite(ms) ? `${(ms / 1000).toFixed(1)} s` : "—";

function notice(message) { $("notice").textContent = message; $("notice").hidden = !message; }
async function api(path, options = {}) {
  const response = await fetch(`/api/monitor/${path}`, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Không hoàn tất yêu cầu (HTTP ${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}
const post = (path, value = {}) => api(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(value) });
function clearPreview() {
  imageKey = null;
  $("preview").removeAttribute("src");
  $("preview").hidden = true;
  $("preview-placeholder").hidden = false;
}
function controls() {
  const session = snapshot.session, status = session?.status;
  $("upload").disabled = pending || (session && !terminal(status));
  $("start").disabled = pending || status !== "ready";
  $("pause").disabled = pending || !["running", "paused"].includes(status);
  $("pause").textContent = status === "paused" ? "Tiếp tục" : "Tạm dừng";
  $("stop").disabled = pending || !["starting", "running", "paused"].includes(status);
  $("delete").disabled = pending || snapshot.receiving || !session || !["uploading", "ready", "failed", "completed", "stopped"].includes(status);
  $("seek").disabled = pending || !["running", "paused"].includes(status);
}
function render(value) {
  if (value.session && Date.parse(value.session.media_delete_by) <= Date.now()) {
    value = { ...value, session: { ...value.session, status: "failed", error_type: "MediaExpired" }, observations: null, result_age_ms: null };
  }
  const previous = snapshot.session;
  const previousFrame = snapshot.observations?.frame_index;
  snapshot = value;
  const session = value.session;
  if (!session || previous?.id !== session.id || previous?.epoch !== session.epoch || ["stopped", "stopping", "failed"].includes(session.status)) clearPreview();
  receivedAt = performance.now();
  ageAtReceive = value.result_age_ms;
  updateAge();
  $("session-state").textContent = session ? states[session.status] || session.status : "Chưa có nguồn";
  $("upload-limit").textContent = `${Math.round((value.limits?.upload_bytes || 536870912) / 1048576)} MiB`;
  $("source-time").textContent = `Nguồn ${seconds(session?.source_time_ms)}`;
  $("result-time").textContent = `Ảnh phân tích ${seconds(value.observations?.video_time_ms)}`;
  $("processed").textContent = session?.processed || 0;
  $("dropped").textContent = session?.dropped || 0;
  $("ai-state").textContent = session?.dropped ? "AI xử lý chậm · có mẫu bị bỏ qua" : session?.processed ? "Kết quả đúng frame nguồn" : "Chưa có mẫu phân tích";
  $("retention").textContent = session ? `Bản upload giữ local đến ${new Date(session.media_delete_by).toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" })}, hoặc khi bạn xóa phiên.` : "";
  $("seek").max = Math.max(0, (session?.frame_count || 1) - 1);
  if (!dragging) $("seek").value = session?.source_frame_index || 0;
  if (previous?.id !== session?.id || previous?.epoch !== session?.epoch || previousFrame !== value.observations?.frame_index) {
    $("observations").replaceChildren();
    for (const [index, observation] of (value.observations?.observations || []).entries()) {
      const row = document.createElement("div"); row.className = "observation";
      const title = document.createElement("strong"); title.textContent = `Vị trí ${index + 1} trong ảnh`; row.append(title);
      const found = Object.keys(labels).filter((_, i) => observation.above_threshold[i]);
      const text = document.createElement("span"); text.textContent = found.length ? found.map((key) => labels[key]).join(" · ") : "Chưa có nhãn hành vi vượt ngưỡng";
      row.append(text); $("observations").append(row);
    }
    if (!$("observations").children.length) $("observations").textContent = value.observations ? "Không có detection trong mẫu này." : "Chưa có kết quả.";
  }
  if (session && value.observations && !["stopped", "stopping", "failed"].includes(session.status)) {
    const key = `${session.id}:${session.epoch}`;
    if (key !== imageKey) {
      imageKey = key;
      $("preview").src = `/api/monitor/sessions/${encodeURIComponent(session.id)}/preview?epoch=${session.epoch}`;
      $("preview").hidden = false; $("preview-placeholder").hidden = true;
    }
  }
  if (session?.status === "failed") notice(session.error_type === "MediaExpired" ? "Quyền sử dụng media đã hết hạn. Bản upload không còn được phục vụ." : `Phiên dừng do lỗi ${session.error_type || "input"}. Kiểm tra video, receipt và cấu hình trước khi tạo phiên mới.`);
  controls();
  if (session && !terminal(session.status) && eventSession !== session.id) connect(session.id);
  if (!session || terminal(session.status)) disconnect();
}
function disconnect() { events?.close(); events = null; eventSession = null; }
function connect(id) {
  disconnect(); eventSession = id;
  events = new EventSource(`/api/monitor/sessions/${encodeURIComponent(id)}/events`);
  events.addEventListener("snapshot", (event) => { $("connection-state").textContent = "Đã kết nối"; render(JSON.parse(event.data)); });
  events.onerror = () => { $("connection-state").textContent = "Mất kết nối · đang nối lại"; };
}
async function refresh() { render(await api("state")); }
async function perform(action) {
  pending = true; controls(); notice("");
  try { await action(); }
  catch (error) { notice(error.message); await refresh().catch(() => {}); }
  finally { pending = false; controls(); }
}
async function command(action, extra = {}) {
  const session = snapshot.session;
  if (!session) return;
  if (["seek", "stop"].includes(action)) clearPreview();
  render(await post(`sessions/${session.id}/command`, { command_id: session.command_id + 1, epoch: session.epoch, action, ...extra }));
}
$("upload-form").onsubmit = (event) => {
  event.preventDefault();
  perform(async () => {
    const video = $("video-file").files[0], receipt = $("receipt-file").files[0];
    if (!video || !receipt) throw new Error("Chọn video và receipt quyền sử dụng.");
    if (video.size > snapshot.limits.upload_bytes || receipt.size > snapshot.limits.receipt_bytes) throw new Error("File vượt giới hạn dung lượng.");
    render(await post("uploads", { receipt: JSON.parse(await receipt.text()), size: video.size }));
    const identity = snapshot.session.id;
    render(await api(`uploads/${identity}`, { method: "PUT", headers: { "Content-Type": "video/mp4" }, body: video }));
  });
};
$("start").onclick = () => perform(async () => render(await post(`sessions/${snapshot.session.id}/start`)));
$("pause").onclick = () => perform(() => command(snapshot.session.status === "paused" ? "resume" : "pause"));
$("stop").onclick = () => perform(() => command("stop"));
$("delete").onclick = () => perform(async () => { await api(`sessions/${snapshot.session.id}`, { method: "DELETE" }); clearPreview(); await refresh(); });
$("seek").oninput = () => { dragging = true; $("seek-time").textContent = `${(Number($("seek").value) / snapshot.session.fps).toFixed(1)} s (ước tính)`; };
$("seek").onchange = () => { const index = Number($("seek").value); dragging = false; perform(() => command("seek", { frame_index: index })); };
function theme(value) { document.documentElement.dataset.theme = value; $("theme").textContent = value === "dark" ? "Giao diện sáng" : "Giao diện tối"; try { localStorage.setItem("exam-review-theme", value); } catch {} }
try { theme(localStorage.getItem("exam-review-theme") || "dark"); } catch { theme("dark"); }
$("theme").onclick = () => theme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
function updateAge() { $("age").textContent = `Tuổi ảnh ${ageAtReceive == null ? "—" : seconds(ageAtReceive + performance.now() - receivedAt)}`; }
setInterval(() => {
  updateAge();
  const session = snapshot.session;
  if (session && Date.parse(session.media_delete_by) <= Date.now() && expiryChecked !== session.id) {
    expiryChecked = session.id;
    render(snapshot);
    refresh().catch((error) => notice(error.message));
  }
}, 250);
window.addEventListener("pagehide", disconnect);
refresh().catch((error) => notice(error.message));
