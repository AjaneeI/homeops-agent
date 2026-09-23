const scenarios = {
  "all-clear": {
    "front-door": { name: "Front Door Lock", kind: "lock", status: "locked", safeActions: [] },
    "bedside-bulb": { name: "Govee Bedside Bulb", kind: "light", status: "dimmed to 20%", safeActions: ["dim_to_20"] },
    "switchbot-outlet": { name: "SwitchBot Outlet", kind: "outlet", status: "off", safeActions: ["turn_off"] },
    "fire-tv": { name: "Fire TV", kind: "media", status: "idle", safeActions: ["confirm_idle"] },
    "echo-group": { name: "Echo Surround Group", kind: "speaker_group", status: "quiet", safeActions: [] },
  },
  "fix-needed": {
    "front-door": { name: "Front Door Lock", kind: "lock", status: "locked", safeActions: [] },
    "bedside-bulb": { name: "Govee Bedside Bulb", kind: "light", status: "on at 80%", safeActions: ["dim_to_20"] },
    "switchbot-outlet": { name: "SwitchBot Outlet", kind: "outlet", status: "on", safeActions: ["turn_off"] },
    "fire-tv": { name: "Fire TV", kind: "media", status: "playing", safeActions: ["confirm_idle"] },
    "echo-group": { name: "Echo Surround Group", kind: "speaker_group", status: "quiet", safeActions: [] },
  },
  "lock-unknown": {
    "front-door": { name: "Front Door Lock", kind: "lock", status: "unknown", safeActions: [] },
    "bedside-bulb": { name: "Govee Bedside Bulb", kind: "light", status: "on at 60%", safeActions: ["dim_to_20"] },
    "switchbot-outlet": { name: "SwitchBot Outlet", kind: "outlet", status: "off", safeActions: ["turn_off"] },
    "fire-tv": { name: "Fire TV", kind: "media", status: "idle", safeActions: ["confirm_idle"] },
    "echo-group": { name: "Echo Surround Group", kind: "speaker_group", status: "quiet", safeActions: [] },
  },
  "device-failure": {
    "front-door": { name: "Front Door Lock", kind: "lock", status: "locked", safeActions: [] },
    "bedside-bulb": { name: "Govee Bedside Bulb", kind: "light", status: "unreachable", safeActions: ["dim_to_20"] },
    "switchbot-outlet": { name: "SwitchBot Outlet", kind: "outlet", status: "on", safeActions: ["turn_off"] },
    "fire-tv": { name: "Fire TV", kind: "media", status: "idle", safeActions: ["confirm_idle"] },
    "echo-group": { name: "Echo Surround Group", kind: "speaker_group", status: "quiet", safeActions: [] },
  },
};

const actionLabels = {
  dim_to_20: "Dimmed bedside bulb to 20%",
  turn_off: "Turned off SwitchBot outlet",
  confirm_idle: "Confirmed Fire TV is idle",
};

const deviceLabels = {
  lock: "Security",
  light: "Lighting",
  outlet: "Power",
  media: "Media",
  speaker_group: "Audio",
};

const devicesEl = document.querySelector("#devices");
const actionsEl = document.querySelector("#actions");
const approvalsEl = document.querySelector("#approvals");
const auditEl = document.querySelector("#audit");
const traceEl = document.querySelector("#trace");
const summaryEl = document.querySelector("#summary");
const scenarioEl = document.querySelector("#scenario");
const devicesCheckedEl = document.querySelector("#devices-checked");
const safeActionsEl = document.querySelector("#safe-actions");
const humanReviewEl = document.querySelector("#human-review");
const runCheckEl = document.querySelector("#run-check");
const flowEl = document.querySelector(".flow");
const agentCoreEl = document.querySelector(".agent-core strong");
const mapNodes = document.querySelectorAll(".node[data-device]");

function cloneScenario() {
  return JSON.parse(JSON.stringify(scenarios[scenarioEl.value]));
}

function audit(log, event) {
  log.push({ timestamp: new Date().toISOString(), ...event });
}

function recordTool(trace, name, input, result) {
  trace.push({ name, input, result });
}

function executeSafeAction(devices, id, action) {
  if (devices[id].status === "unreachable") {
    return { ok: false, device: devices[id].name, action, reason: "Device API is unavailable." };
  }
  if (!devices[id].safeActions.includes(action)) {
    return { ok: false, device: devices[id].name, action, reason: "Action is not low-risk." };
  }
  const nextStatus = { dim_to_20: "dimmed to 20%", turn_off: "off", confirm_idle: "idle" }[action];
  devices[id].status = nextStatus;
  return { ok: true, device: devices[id].name, action, status: nextStatus };
}

function runGoodNightCheck() {
  const devices = cloneScenario();
  const actions = [];
  const approvals = [];
  const log = [];
  const trace = [];

  Object.entries(devices).forEach(([id, device]) => {
    recordTool(trace, "get_device_state", { device_id: id }, { status: device.status, safe_actions: device.safeActions });
    const stateEvent = { type: "state_checked", device: device.name, status: device.status };
    audit(log, stateEvent);
    recordTool(trace, "write_audit_log", { event: stateEvent }, { stored: true });

    if (id === "front-door" && device.status !== "locked") {
      const approval = {
        action: "Verify front door lock",
        reason: "Door lock state is security-sensitive or uncertain, so the agent will not change it automatically.",
      };
      recordTool(trace, "request_human_approval", { action: approval.action }, { approval_status: "required" });
      approvals.push(approval);
      const approvalEvent = { type: "approval_requested", ...approval };
      audit(log, approvalEvent);
      recordTool(trace, "write_audit_log", { event: approvalEvent }, { stored: true });
      return;
    }

    if (id === "bedside-bulb" && device.status !== "dimmed to 20%") {
      const result = executeSafeAction(devices, id, "dim_to_20");
      recordTool(trace, "execute_safe_action", { device_id: id, action: "dim_to_20" }, result);
      actions.push(result);
    }
    if (id === "switchbot-outlet" && device.status === "on") {
      const result = executeSafeAction(devices, id, "turn_off");
      recordTool(trace, "execute_safe_action", { device_id: id, action: "turn_off" }, result);
      actions.push(result);
    }
    if (id === "fire-tv" && device.status !== "idle") {
      const result = executeSafeAction(devices, id, "confirm_idle");
      recordTool(trace, "execute_safe_action", { device_id: id, action: "confirm_idle" }, result);
      actions.push(result);
    }
  });

  actions.forEach((action) => {
    const actionEvent = { type: action.ok ? "safe_action_executed" : "safe_action_failed", ...action };
    audit(log, actionEvent);
    recordTool(trace, "write_audit_log", { event: actionEvent }, { stored: true });
  });
  render(devices, actions, approvals, log, trace);
}

function formatPayload(payload) {
  return JSON.stringify(payload).replaceAll('"', "");
}

function render(devices, actions = [], approvals = [], log = [], trace = []) {
  devicesEl.innerHTML = Object.values(devices)
    .map((device) => `<div class="card ${deviceClass(device.status)}">
      <span class="device-name">${device.name}</span>
      <span class="muted">${deviceLabels[device.kind]} · ${device.status}</span>
    </div>`)
    .join("");

  actionsEl.className = actions.length ? "stack" : "stack empty";
  actionsEl.innerHTML = actions.length
    ? actions.map((action) => {
      const title = action.ok ? actionLabels[action.action] : `Could not ${action.action.replaceAll("_", " ")}`;
      const detail = action.ok ? `${action.device} is now ${action.status}.` : `${action.device} was left unchanged: ${action.reason}`;
      return `<div class="item ${action.ok ? "" : "fail"}"><strong>${title}</strong><span class="muted">${detail}</span></div>`;
    }).join("")
    : "No automatic actions needed.";

  approvalsEl.className = approvals.length ? "stack" : "stack empty";
  approvalsEl.innerHTML = approvals.length
    ? approvals.map((approval) => `<div class="item warn"><strong>${approval.action}</strong><span class="muted">${approval.reason}</span></div>`).join("")
    : "No approvals required.";

  traceEl.className = trace.length ? "stack trace-list" : "stack empty";
  traceEl.innerHTML = trace.length
    ? trace.map((call) => `<div class="item trace-item"><strong>${call.name}</strong><span class="muted">Input ${formatPayload(call.input)}</span><span class="muted">Result ${formatPayload(call.result)}</span></div>`).join("")
    : "Tool calls will appear after a run.";

  auditEl.className = log.length ? "stack" : "stack empty";
  auditEl.innerHTML = log.length
    ? log.map((event) => `<div class="item"><strong>${event.type.replaceAll("_", " ")}</strong><span class="muted">${event.device || event.action || "HomeOps Agent"} · ${event.status || event.reason || event.timestamp}</span></div>`).join("")
    : "Audit events will appear here.";

  summaryEl.textContent = approvals.length ? "Good Night Check complete with human review required." : "Good Night Check complete.";
  devicesCheckedEl.textContent = `${Object.keys(devices).length} devices`;
  const successfulActions = actions.filter((action) => action.ok).length;
  safeActionsEl.textContent = `${successfulActions} safe ${successfulActions === 1 ? "action" : "actions"}`;
  humanReviewEl.textContent = approvals.length ? `${approvals.length} needed` : "None";
  agentCoreEl.textContent = approvals.length ? "Review" : actions.some((action) => !action.ok) ? "Degraded" : trace.length ? "Clear" : "Ready";
  renderMap(devices);
}

function deviceClass(status) {
  if (status === "unknown") return "warn";
  if (status === "unreachable") return "fail";
  return "";
}

function renderMap(devices) {
  mapNodes.forEach((node) => {
    const device = devices[node.dataset.device];
    node.classList.remove("warn", "fail");
    if (device) {
      const className = deviceClass(device.status);
      if (className) node.classList.add(className);
    }
  });
}

scenarioEl.addEventListener("change", () => {
  render(cloneScenario());
  summaryEl.textContent = "Ready to check the home.";
});
runCheckEl.addEventListener("click", () => {
  runCheckEl.classList.add("is-running");
  flowEl.classList.add("running");
  summaryEl.textContent = "Good Night Check running.";
  window.setTimeout(() => {
    runGoodNightCheck();
    runCheckEl.classList.remove("is-running");
    flowEl.classList.remove("running");
  }, 420);
});
render(cloneScenario());
