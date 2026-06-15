let cases = [
  { id: "C-74218", merchant: "EL ARADO", issue: "Menu not syncing to KDS", status: "active", sla: "2h 15m", update: "10:21 AM", risk: "ok" },
  { id: "C-74207", merchant: "TAQUERIA LA GLORIA", issue: "Payments failing on check close", status: "active", sla: "4h 05m", update: "9:58 AM", risk: "ok" },
  { id: "C-74191", merchant: "MAISON DE CREPES", issue: "Gift card balance issue", status: "follow-ups", sla: "1h 20m", update: "9:12 AM", risk: "warn" },
  { id: "C-74174", merchant: "KATFISH KASTLE", issue: "Printer offline intermittently", status: "callback", sla: "30m", update: "8:47 AM", risk: "danger" },
  { id: "C-74163", merchant: "EL ARADO", issue: "Modifier not applying in POS", status: "escalation", sla: "Overdue", update: "8:15 AM", risk: "danger" },
  { id: "C-74150", merchant: "TAQUERIA LA GLORIA", issue: "Time zone incorrect in reports", status: "needs-tz", sla: "3h 40m", update: "7:52 AM", risk: "ok" },
  { id: "C-74138", merchant: "MAISON DE CREPES", issue: "Menu upload error", status: "read-only", sla: "—", update: "Yesterday", risk: "none" },
  { id: "C-74122", merchant: "KATFISH KASTLE", issue: "Tax not calculating correctly", status: "confirmation", sla: "1h 05m", update: "Yesterday", risk: "warn" }
];

let actions = [
  { title: "Follow up with TAQUERIA LA GLORIA", detail: "Payments failing on check close", status: "follow-ups", time: "15m" },
  { title: "Call back KATFISH KASTLE", detail: "Printer offline intermittently", status: "callback", time: "30m", urgent: true },
  { title: "Escalate EL ARADO to Engineering", detail: "Modifier not applying in POS", status: "escalation", time: "1h" },
  { title: "Request time zone from TAQUERIA LA GLORIA", detail: "Time zone incorrect in reports", status: "needs-tz", time: "1h 25m" },
  { title: "Confirm workaround with MAISON DE CREPES", detail: "Gift card balance issue", status: "confirmation", time: "2h" }
];

let signals = [
  { icon: "S", label: "Slack", detail: "#support-dine", count: 3, color: "#dc2626" },
  { icon: "E", label: "Email", detail: "New case emails", count: 7, color: "#1d64d8" },
  { icon: "M", label: "Merchant", detail: "Merchant replies", count: 5, color: "#078747" },
  { icon: "!", label: "Escalations", detail: "Escalation pings", count: 1, color: "#dc2626" }
];

let memory = [
  { merchant: "EL ARADO", detail: "2 open cases · last modifier issue on 6/12", tag: "Repeat merchant" },
  { merchant: "TAQUERIA LA GLORIA", detail: "3 open cases · busy after 11am local time", tag: "Repeat merchant" },
  { merchant: "MAISON DE CREPES", detail: "1 open case · uses multiple locations", tag: "Known setup" },
  { merchant: "KATFISH KASTLE", detail: "2 open cases · prefers callback before email", tag: "Callback first" }
];

let calendar = [
  { time: "11:00 AM", title: "Standup", duration: "30m" },
  { time: "1:00 PM", title: "Sync: Escalations Review", duration: "45m" },
  { time: "3:30 PM", title: "1:1", duration: "30m" },
  { time: "Tomorrow", title: "Dine Ops Huddle", duration: "60m" }
];

let kpis = [
  { label: "Active Cases", value: 34, note: "+6 vs yesterday", tone: "teal" },
  { label: "Follow-ups", value: 17, note: "Due today", tone: "amber" },
  { label: "Callback", value: 6, note: "Due today", tone: "blue" },
  { label: "Escalation", value: 3, note: "Overdue", tone: "red" },
  { label: "Needs TZ", value: 4, note: "Waiting on info", tone: "teal" },
  { label: "Read-only", value: 8, note: "No action", tone: "muted" },
  { label: "Confirmation required", value: 5, note: "Awaiting response", tone: "amber" }
];

let currentFilter = "all";
let confirmationOnly = false;
let learningData = [
  ["Cases Closed", "28", "+12%"],
  ["First Contact Res.", "64%", "+8%"],
  ["Avg. Handle Time", "31m", "-5m"],
  ["Reopen Rate", "7%", "-2%"]
];
let nextDeadlineText = "Callback: KATFISH KASTLE · 30m";
let launchGates = [
  { id: "github_global_repo", label: "GitHub", target: "pending", gate: "github_publish", status: "pending", detail: "Repo and branch need confirmation" },
  { id: "icloud_destination", label: "iCloud Drive", target: "pending", gate: "icloud_artifact_export", status: "pending", detail: "Local path or upload route needs confirmation" },
  { id: "notion_live_launch_team", label: "Notion", target: "collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45", gate: "notion_status_update", status: "pending", detail: "Live row method not confirmed" }
];
let packageStatus = {
  repo: "maverick-cockpit",
  sourceArtifacts: 0,
  assembledFiles: 0,
  publishStatus: "prepared_local_only",
  externalMutationAllowed: false,
  githubOrigin: "pending",
  icloudPath: "pending"
};
let canvases = [];
let botDispatch = {};
let priorityEngine = [];
let operatingLoop = {
  mission: {},
  dailyCadence: [],
  todayObjectives: [],
  caseLanes: [],
  pendingConfirmations: []
};
let commsOutbox = {
  slackApp: {},
  deliveryRules: [],
  drafts: []
};
let activationChecklist = {
  summary: {},
  lanes: []
};
let learningLedger = {
  summary: {},
  events: [],
  rejectedMemory: []
};
let slackBridge = {
  app: {},
  requiredBeforeSend: [],
  messageEnvelopes: [],
  dryRun: {}
};
let githubBridge = {
  repository: {},
  packageEvidence: {},
  publishEnvelope: {},
  requiredBeforePublish: [],
  dryRun: {}
};
let notionBridge = {
  target: {},
  readModel: {},
  updateEnvelopes: [],
  requiredBeforeUpdate: [],
  dryRun: {}
};
let deviceAccess = {
  hard_rule: "Maverick must work from every Edwin device through a stable device-safe URL; localhost is never the user-facing answer.",
  primary_access: { mode: "always_on_static_https", status: "pending_public_publish_target" },
  fallback_access: { mode: "same_wifi_lan", url_template: "http://<mac-lan-ip>:4181/" },
  installable_app: { status: "ready_for_https_hosts" }
};

function statusLabel(status) {
  const labels = {
    active: "Active",
    "follow-ups": "Follow-ups",
    callback: "Callback",
    escalation: "Escalation",
    "needs-tz": "Needs TZ",
    "read-only": "Read-only",
    confirmation: "Confirmation required"
  };
  return labels[status] || status;
}

function breakable(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll("/", "/<wbr>")
    .replaceAll("~", "~<wbr>")
    .replaceAll("-", "-<wbr>");
}

function compact(value, max = 44) {
  const text = String(value || "pending");
  if (text.length <= max) return text;
  return `${text.slice(0, 22)}...${text.slice(-14)}`;
}

function renderKpis() {
  document.querySelector("#kpiGrid").innerHTML = kpis.map((item) => `
    <div class="kpi">
      <label>${item.label}</label>
      <strong class="${item.tone}">${item.value}</strong>
      <span>${item.note}</span>
    </div>
  `).join("");
}

function filteredCases() {
  if (currentFilter === "all") return cases;
  return cases.filter((item) => item.status === currentFilter);
}

function filteredActions() {
  if (confirmationOnly) return actions.filter((item) => item.status === "confirmation");
  if (currentFilter === "all") return actions;
  return actions.filter((item) => item.status === currentFilter);
}

function renderCases() {
  document.querySelector("#caseRows").innerHTML = filteredCases().map((item) => `
    <tr>
      <td class="case-id">${item.id}</td>
      <td>${item.merchant}</td>
      <td>${item.issue}</td>
      <td><span class="chip ${item.status}">${statusLabel(item.status)}</span></td>
      <td><span class="sla"><span class="dot ${item.risk}"></span>${item.sla}</span></td>
      <td>${item.update}</td>
    </tr>
  `).join("");
}

function renderActions() {
  const rows = filteredActions();
  document.querySelector("#actionQueue").innerHTML = rows.map((item, index) => `
    <label class="queue-item">
      <input type="checkbox" data-action-index="${index}">
      <span>
        <span class="queue-title">${item.title}</span>
        <span class="queue-detail">${item.detail}</span>
      </span>
      <span class="chip ${item.status}">${statusLabel(item.status)}</span>
      <span class="queue-time ${item.urgent ? "danger" : ""}">${item.time}</span>
    </label>
  `).join("") || `<div class="queue-item"><span></span><span class="queue-title">No actions in this filter</span></div>`;
}

function renderSignals() {
  document.querySelector("#signalList").innerHTML = signals.map((item) => `
    <div class="signal-row">
      <span class="signal-icon" style="background:${item.color}">${item.icon}</span>
      <span><strong>${item.label}</strong><br><span class="muted">${item.detail}</span></span>
      <span class="count-pill" style="background:${item.color}">${item.count}</span>
    </div>
  `).join("");
}

function renderMemory() {
  document.querySelector("#memoryList").innerHTML = memory.map((item) => `
    <div class="memory-row">
      <span class="merchant-icon">▣</span>
      <span>
        <span class="memory-title">${item.merchant}</span>
        <span class="memory-detail">${item.detail}</span>
      </span>
      <span class="chip active">${item.tag}</span>
    </div>
  `).join("");
}

function renderCalendar() {
  document.querySelector("#calendarList").innerHTML = calendar.map((item) => `
    <div class="calendar-row">
      <span class="blue">${item.time}</span>
      <span class="calendar-title">${item.title}</span>
      <span class="muted">${item.duration}</span>
    </div>
  `).join("");
  document.querySelector("#nextDeadline").innerHTML = `<span>Next deadline</span><span>${nextDeadlineText}</span>`;
}

function renderLearning() {
  document.querySelector("#learningStats").innerHTML = learningData.map(([label, value, delta]) => `
    <div class="learning-stat">
      <label>${label}</label>
      <strong>${value}</strong><span>${delta}</span>
    </div>
  `).join("");
}

function renderLearningLedger() {
  const summary = learningLedger.summary || {};
  const events = Array.isArray(learningLedger.events) ? learningLedger.events : [];
  const rejected = Array.isArray(learningLedger.rejectedMemory) ? learningLedger.rejectedMemory : [];
  document.querySelector("#learningLedger").innerHTML = `
    <div class="ledger-summary">
      <span><b>${breakable(summary.promoted_events || events.length)}</b> promoted</span>
      <span><b>${breakable(summary.rejected_memory || rejected.length)}</b> rejected</span>
      <span><b>${breakable(summary.confidence || "local")}</b> confidence</span>
    </div>
    <div class="ledger-list">
      ${events.map((item) => `
        <div class="ledger-row">
          <span class="canvas-type">${breakable(item.kind || "learned")}</span>
          <span>
            <span class="memory-title">${breakable(item.id || "learning")}</span>
            <span class="memory-detail">${breakable(item.next_action || item.lesson || "Review next action")}</span>
          </span>
        </div>
      `).join("")}
    </div>
  `;
}

function renderCanvases() {
  document.querySelector("#canvasList").innerHTML = canvases.map((item) => `
    <div class="canvas-row">
      <span class="canvas-type">${breakable(item.type || "view")}</span>
      <span>
        <span class="memory-title">${breakable(item.name)}</span>
        <span class="memory-detail">${breakable(item.purpose)}</span>
      </span>
    </div>
  `).join("") || `<div class="canvas-row"><span></span><span class="memory-detail">No Notion canvases mapped yet</span></div>`;
}

function renderOperatingLoop() {
  const mission = operatingLoop.mission || {};
  const objectives = Array.isArray(operatingLoop.todayObjectives) ? operatingLoop.todayObjectives : [];
  const cadence = Array.isArray(operatingLoop.dailyCadence) ? operatingLoop.dailyCadence : [];
  const pending = Array.isArray(operatingLoop.pendingConfirmations) ? operatingLoop.pendingConfirmations : [];
  document.querySelector("#operatingLoop").innerHTML = `
    <strong>${breakable(mission.target || "Keep the Shift4 Dine work visible and inside the handling window")}</strong>
    <div class="loop-metrics">
      <span><b>${breakable(mission.active_cases || 0)}</b> active</span>
      <span><b>${breakable(mission.desired_active_cases || 50)}</b> target</span>
      <span><b>${breakable(mission.window_days || 14)}</b> day rule</span>
    </div>
    <div class="loop-list">
      ${objectives.slice(0, 4).map((item) => `
        <div class="loop-row">
          <span>${breakable(item.priority || "Priority")}</span>
          <span>
            <span class="memory-title">${breakable(item.metric || item.id)}</span>
            <span class="memory-detail">${breakable(item.action || "Review next action")}</span>
          </span>
        </div>
      `).join("")}
    </div>
    <div class="loop-footer">
      <span>${cadence.length} cadence steps</span>
      <span>${pending.length} gated lanes</span>
    </div>
  `;
}

function renderBotDispatch() {
  const replies = Array.isArray(botDispatch.quick_replies) ? botDispatch.quick_replies : [];
  const lanes = Array.isArray(priorityEngine) ? priorityEngine : [];
  document.querySelector("#botDispatch").innerHTML = `
    <strong>${breakable(botDispatch.name || "Argo / Buddy dispatch")}</strong>
    <span>${breakable(botDispatch.target || "Awaiting bot target")}</span>
    <div class="reply-cloud">
      ${replies.map((reply) => `<span>${breakable(reply)}</span>`).join("")}
    </div>
    <div class="priority-stack">
      ${lanes.slice(0, 5).map((lane) => `
        <span><b>${breakable(lane.level)}</b> ${breakable(lane.name)}</span>
      `).join("")}
    </div>
  `;
}

function renderCommsOutbox() {
  const drafts = Array.isArray(commsOutbox.drafts) ? commsOutbox.drafts : [];
  const slackApp = commsOutbox.slackApp || {};
  document.querySelector("#commsOutbox").innerHTML = `
    <div class="outbox-app">
      <span>Slack app</span>
      <strong>${breakable(slackApp.app_id || "pending")}</strong>
      <span>${breakable(slackApp.target_status || "pending")}</span>
    </div>
    ${drafts.slice(0, 4).map((item) => `
      <div class="outbox-row">
        <span class="canvas-type">${breakable(item.lane || "draft")}</span>
        <span>
          <span class="memory-title">${breakable(item.title || item.id)}</span>
          <span class="memory-detail">${breakable(item.status || "draft")}</span>
        </span>
        <span class="gate-code">${breakable(item.gate || "gate")}</span>
      </div>
    `).join("")}
  `;
}

function renderSlackBridge() {
  const app = slackBridge.app || {};
  const requirements = Array.isArray(slackBridge.requiredBeforeSend) ? slackBridge.requiredBeforeSend : [];
  const envelopes = Array.isArray(slackBridge.messageEnvelopes) ? slackBridge.messageEnvelopes : [];
  const dryRun = slackBridge.dryRun || {};
  document.querySelector("#slackBridge").innerHTML = `
    <div class="bridge-summary">
      <span><b>${breakable(app.id || "A0BALRB6CNQ")}</b> app</span>
      <span><b>${breakable(envelopes.length)}</b> envelopes</span>
      <span><b>${dryRun.send_allowed ? "ready" : "blocked"}</b> send</span>
    </div>
    <div class="bridge-list">
      ${requirements.slice(0, 4).map((item) => `
        <div class="bridge-row">
          <span class="gate-status"></span>
          <span>${breakable(item)}</span>
        </div>
      `).join("")}
    </div>
  `;
}

function renderGithubBridge() {
  const repository = githubBridge.repository || {};
  const evidence = githubBridge.packageEvidence || {};
  const requirements = Array.isArray(githubBridge.requiredBeforePublish) ? githubBridge.requiredBeforePublish : [];
  const dryRun = githubBridge.dryRun || {};
  document.querySelector("#githubBridge").innerHTML = `
    <div class="github-summary">
      <span><b>${breakable(compact(repository.candidate_repo || "pending", 32))}</b> repo</span>
      <span><b>${breakable(evidence.assembled_file_count || 0)}</b> files</span>
      <span><b>${dryRun.publish_allowed ? "ready" : "blocked"}</b> publish</span>
    </div>
    <div class="github-list">
      ${requirements.slice(0, 4).map((item) => `
        <div class="github-row">
          <span class="gate-status"></span>
          <span>${breakable(item)}</span>
        </div>
      `).join("")}
    </div>
  `;
}

function renderNotionBridge() {
  const target = notionBridge.target || {};
  const readModel = notionBridge.readModel || {};
  const requirements = Array.isArray(notionBridge.requiredBeforeUpdate) ? notionBridge.requiredBeforeUpdate : [];
  const dryRun = notionBridge.dryRun || {};
  document.querySelector("#notionBridge").innerHTML = `
    <div class="notion-summary">
      <span><b>${breakable(readModel.active_cases || 0)}</b> cases</span>
      <span><b>${breakable(readModel.canvas_count || 0)}</b> views</span>
      <span><b>${dryRun.update_allowed ? "ready" : "blocked"}</b> update</span>
    </div>
    <div class="notion-target">${breakable(compact(target.known_target || "pending", 68))}</div>
    <div class="notion-list">
      ${requirements.slice(0, 4).map((item) => `
        <div class="notion-row">
          <span class="gate-status"></span>
          <span>${breakable(item)}</span>
        </div>
      `).join("")}
    </div>
  `;
}

function renderDeviceAccess() {
  const primary = deviceAccess.primary_access || {};
  const fallback = deviceAccess.fallback_access || {};
  const app = deviceAccess.installable_app || {};
  document.querySelector("#deviceAccess").innerHTML = `
    <div class="device-rule">${breakable(deviceAccess.hard_rule || "Every device needs a stable access path.")}</div>
    <div class="device-grid">
      <span><b>${breakable(primary.mode || "https")}</b> ${breakable(primary.status || "pending")}</span>
      <span><b>${breakable(fallback.mode || "lan")}</b> ${breakable(fallback.url_template || "pending")}</span>
      <span><b>PWA</b> ${breakable(app.status || "pending")}</span>
    </div>
  `;
}

function renderActivationChecklist() {
  const summary = activationChecklist.summary || {};
  const lanes = Array.isArray(activationChecklist.lanes) ? activationChecklist.lanes : [];
  document.querySelector("#activationChecklist").innerHTML = `
    <div class="activation-summary">
      <span><b>${breakable(summary.total_targets || 0)}</b> targets</span>
      <span><b>${breakable(summary.ready_with_confirmation_token || 0)}</b> ready</span>
      <span><b>${breakable(summary.pending_targets || 0)}</b> pending</span>
    </div>
    <div class="activation-rows">
      ${lanes.map((lane) => `
        <div class="activation-row">
          <span class="gate-status ${lane.activation_status === "ready_with_confirmation_token" ? "confirmed" : ""}"></span>
          <span>
            <span class="gate-title">${breakable(lane.target_id)}</span>
            <span class="gate-detail">${breakable(compact(lane.known_target || lane.system, 62))}</span>
          </span>
          <span class="chip ${lane.activation_status === "ready_with_confirmation_token" ? "active" : "confirmation"}">${breakable(lane.activation_status)}</span>
          <span class="gate-code">${breakable(lane.gate)}</span>
        </div>
      `).join("")}
    </div>
  `;
}

function renderLaunchGates() {
  document.querySelector("#packageStatus").innerHTML = `
    <div>
      <label>Package</label>
      <strong>${packageStatus.repo}</strong>
      <span>${packageStatus.assembledFiles} files · ${packageStatus.publishStatus}</span>
    </div>
    <div>
      <label>GitHub origin</label>
      <strong>${breakable(compact(packageStatus.githubOrigin))}</strong>
      <span>${packageStatus.externalMutationAllowed ? "writes enabled" : "writes blocked"}</span>
    </div>
    <div>
      <label>iCloud path</label>
      <strong>${breakable(compact(packageStatus.icloudPath))}</strong>
      <span>export gate required</span>
    </div>
  `;

  document.querySelector("#launchGates").innerHTML = launchGates.map((item) => `
    <div class="gate-row">
      <span class="gate-status ${item.status}"></span>
      <span>
        <span class="gate-title">${item.label}</span>
        <span class="gate-detail">${breakable(compact(item.target, 56))}</span>
      </span>
      <span class="chip ${item.status === "confirmed" ? "active" : "confirmation"}">${statusLabel(item.status)}</span>
      <span class="gate-code">${breakable(item.gate)}</span>
    </div>
  `).join("");
}

function setFilter(filter) {
  currentFilter = filter;
  confirmationOnly = false;
  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.classList.toggle("active", button.dataset.filter === filter);
  });
  document.querySelectorAll(".segment").forEach((button) => {
    button.classList.toggle("active", button.dataset.filter === filter);
  });
  renderCases();
  renderActions();
}

document.addEventListener("click", (event) => {
  const filterButton = event.target.closest("[data-filter]");
  if (filterButton) {
    setFilter(filterButton.dataset.filter);
  }
});

document.querySelector("#onlyConfirmations").addEventListener("click", () => {
  confirmationOnly = !confirmationOnly;
  renderActions();
});

document.querySelector("#resetFilters").addEventListener("click", () => setFilter("all"));

document.querySelector("#actionQueue").addEventListener("change", (event) => {
  if (event.target.matches("input[type='checkbox']")) {
    event.target.closest(".queue-item").classList.toggle("done", event.target.checked);
  }
});

document.querySelector("#addReviewAction").addEventListener("click", () => {
  actions.unshift({
    title: "Review source-map migration roles",
    detail: "Confirm copy_now vs copy_later before adapter import",
    status: "confirmation",
    time: "New"
  });
  renderActions();
});

function applyDashboardData(data) {
  if (!data || typeof data !== "object") return;
  if (Array.isArray(data.kpis)) kpis = data.kpis;
  if (Array.isArray(data.cases)) cases = data.cases;
  if (Array.isArray(data.actions)) actions = data.actions;
  if (Array.isArray(data.signals)) signals = data.signals;
  if (Array.isArray(data.memory)) memory = data.memory;
  if (Array.isArray(data.calendar)) calendar = data.calendar;
  if (Array.isArray(data.learning)) learningData = data.learning;
  if (Array.isArray(data.canvases)) canvases = data.canvases;
  if (data.botDispatch && typeof data.botDispatch === "object") botDispatch = data.botDispatch;
  if (Array.isArray(data.priorityEngine)) priorityEngine = data.priorityEngine;
  if (data.operatingLoop && typeof data.operatingLoop === "object") operatingLoop = data.operatingLoop;
  if (data.commsOutbox && typeof data.commsOutbox === "object") commsOutbox = data.commsOutbox;
  if (data.activationChecklist && typeof data.activationChecklist === "object") activationChecklist = data.activationChecklist;
  if (data.learningLedger && typeof data.learningLedger === "object") learningLedger = data.learningLedger;
  if (data.slackBridge && typeof data.slackBridge === "object") slackBridge = data.slackBridge;
  if (data.githubBridge && typeof data.githubBridge === "object") githubBridge = data.githubBridge;
  if (data.notionBridge && typeof data.notionBridge === "object") notionBridge = data.notionBridge;
  if (data.deviceAccess && typeof data.deviceAccess === "object") deviceAccess = data.deviceAccess;
  if (Array.isArray(data.launchGates)) launchGates = data.launchGates;
  if (data.packageStatus && typeof data.packageStatus === "object") packageStatus = data.packageStatus;
  if (typeof data.nextDeadline === "string") nextDeadlineText = data.nextDeadline;
}

function renderAll() {
  renderKpis();
  renderCases();
  renderActions();
  renderSignals();
  renderMemory();
  renderCalendar();
  renderLearning();
  renderLearningLedger();
  renderOperatingLoop();
  renderCanvases();
  renderBotDispatch();
  renderCommsOutbox();
  renderSlackBridge();
  renderGithubBridge();
  renderNotionBridge();
  renderDeviceAccess();
  renderActivationChecklist();
  renderLaunchGates();
}

async function boot() {
  try {
    const response = await fetch("./data/maverick-dashboard-data.json", { cache: "no-store" });
    if (response.ok) {
      applyDashboardData(await response.json());
    }
  } catch {
    // file:// browsing and offline use keep the built-in fallback dataset.
  }
  try {
    const response = await fetch("./data/maverick-device-access.json", { cache: "no-store" });
    if (response.ok) {
      deviceAccess = await response.json();
    }
  } catch {
    // Public HTTPS hosts and same-Wi-Fi fallback use cached data when offline.
  }
  renderAll();
}

boot();

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./service-worker.js").catch(() => {
    // Non-HTTPS LAN browsing can render the cockpit without offline install.
  });
}
