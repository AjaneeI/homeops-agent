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
const summaryEl = document.querySelector("#summary");
const scenarioEl = document.querySelector("#scenario");
const auditCountEl = document.querySelector("#audit-count");

function cloneScenario() {
  return JSON.parse(JSON.stringify(scenarios[scenarioEl.value]));
}

function audit(log, event) {
  log.push({ timestamp: new Date().toISOString(), ...event });
}

function executeSafeAction(devices, id, action) {
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

  Object.entries(devices).forEach(([id, device]) => {
    audit(log, { type: "state_checked", device: device.name, status: device.status });

    if (id === "front-door" && device.status !== "locked") {
      const approval = {
        action: "Verify front door lock",
        reason: "Door lock state is security-sensitive or uncertain, so the agent will not change it automatically.",
      };
      approvals.push(approval);
      audit(log, { type: "approval_requested", ...approval });
      return;
    }

    if (id === "bedside-bulb" && device.status !== "dimmed to 20%") {
      actions.push(executeSafeAction(devices, id, "dim_to_20"));
    }
    if (id === "switchbot-outlet" && device.status === "on") {
      actions.push(executeSafeAction(devices, id, "turn_off"));
    }
    if (id === "fire-tv" && device.status !== "idle") {
      actions.push(executeSafeAction(devices, id, "confirm_idle"));
    }
  });

  actions.forEach((action) => audit(log, { type: "safe_action_executed", ...action }));
  render(devices, actions, approvals, log);
}

function render(devices, actions = [], approvals = [], log = []) {
  devicesEl.innerHTML = Object.values(devices)
    .map((device) => `<div class="card ${device.status === "unknown" ? "warn" : ""}">
      <span class="device-name">${device.name}</span>
      <span class="muted">${deviceLabels[device.kind]} · ${device.status}</span>
    </div>`)
    .join("");

  actionsEl.className = actions.length ? "stack" : "stack empty";
  actionsEl.innerHTML = actions.length
    ? actions.map((action) => `<div class="item"><strong>${actionLabels[action.action]}</strong><span class="muted">${action.device} is now ${action.status}.</span></div>`).join("")
    : "No automatic actions needed.";

  approvalsEl.className = approvals.length ? "stack" : "stack empty";
  approvalsEl.innerHTML = approvals.length
    ? approvals.map((approval) => `<div class="item warn"><strong>${approval.action}</strong><span class="muted">${approval.reason}</span></div>`).join("")
    : "No approvals required.";

  auditEl.className = log.length ? "stack" : "stack empty";
  auditEl.innerHTML = log.length
    ? log.map((event) => `<div class="item"><strong>${event.type.replaceAll("_", " ")}</strong><span class="muted">${event.device || event.action || "HomeOps Agent"} · ${event.status || event.reason || event.timestamp}</span></div>`).join("")
    : "Audit events will appear here.";

  summaryEl.textContent = approvals.length ? "Good Night Check complete with human review required." : "Good Night Check complete.";
  auditCountEl.textContent = `${log.length} ${log.length === 1 ? "event" : "events"}`;
}

scenarioEl.addEventListener("change", () => {
  render(cloneScenario());
  summaryEl.textContent = "Ready to check the home.";
});
document.querySelector("#run-check").addEventListener("click", runGoodNightCheck);
render(cloneScenario());
