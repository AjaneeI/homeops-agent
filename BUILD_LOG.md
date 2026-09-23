# HomeOps Agent Build Log

## Problem addressed
HomeOps Agent implements a deterministic **Good Night Check** workflow for smart-home operations:
- inspect known device state,
- complete low-risk routine actions,
- require human approval for security-sensitive or uncertain access decisions,
- and write an inspectable audit trail.

This file documents implemented behavior and test evidence as of the current repository state.

## Deterministic policy (source of truth)
Policy is implemented in [`src/homeops_agent/agent.py`](src/homeops_agent/agent.py).

`HomeOpsAgent.run_good_night_check()` iterates over:
- `front-door`
- `bedside-bulb`
- `switchbot-outlet`
- `fire-tv`
- `echo-group`

Key rules:
- Front door lock is never changed automatically; when lock state is not `locked`, the agent records an approval request.
- Low-risk routine actions are executed for eligible non-lock devices:
  - bedside bulb: `dim_to_20`
  - outlet: `turn_off`
  - Fire TV: `confirm_idle`
- Every state check, action result, and approval request is written to the audit log and tool trace.

## Simulated device and tool layer
Device simulation and tool behavior are implemented in [`src/homeops_agent/tools.py`](src/homeops_agent/tools.py).

`scenario_state()` provides deterministic scenarios (`all-clear`, `fix-needed`, `lock-unknown`, `device-failure`) backed by in-memory `Device` objects.

`HomeState` tool-like methods:
- `get_device_state(device_id)` returns device snapshot plus allowed safe actions.
- `execute_safe_action(device_id, action)` enforces safe-action allowlists and returns failure if device status is `unreachable`.
- `request_human_approval(action, reason)` returns `approval_status: required`.
- `write_audit_log(event)` appends timestamped entries.

## Strands adapter
Strands integration is in [`src/homeops_agent/strands_adapter.py`](src/homeops_agent/strands_adapter.py):
- `build_strands_tools()` wraps HomeState methods with Strands `@tool`.
- `build_strands_agent()` constructs a Strands `Agent` with HomeOps system prompt and tool set.
- `run_deterministic_demo()` runs local deterministic policy directly.
- `run_live_strands_demo()` invokes a live Strands run if model-provider credentials are configured.

## Approval gate and audit trail evidence
Evidence from deterministic tests in [`tests/test_agent.py`](tests/test_agent.py):
- `test_good_night_check_executes_low_risk_actions` verifies low-risk actions execute and tool/audit events are captured.
- `test_unknown_lock_status_requires_human_approval` verifies uncertain lock state triggers `request_human_approval` and avoids front-door action.
- `test_device_failure_is_recorded_without_changing_device` verifies device failure is recorded without mutating failed device state.

## Concrete failure path (implemented)
In scenario `device-failure`:
- `bedside-bulb` starts as `unreachable`.
- `execute_safe_action("bedside-bulb", "dim_to_20")` returns:
  - `ok: false`
  - `reason: "Device API is unavailable."`
- Agent records `safe_action_failed` in audit log.
- Device state remains unchanged (`unreachable`).

## Boundaries and non-claims
- Public demo behavior is based on **simulated devices**.
- Deterministic tests validate policy logic and simulated tool behavior.
- Deterministic tests do **not** verify live model-provider quality, prompt-response behavior, or real physical device integrations.
- This repository does not claim production deployment, physical device validation, or live model benchmarking.


## September 23, 2026 — SwitchBot outlet integration preparation

A narrow SwitchBot OpenAPI v1.1 adapter is implemented on a separate evaluation branch as the only current real-device candidate.

Implemented boundaries:
- simulation remains the default HomeOps path
- live provider execution requires an explicit `--live-switchbot-outlet` CLI flag
- credentials are read only from `SWITCHBOT_TOKEN`, `SWITCHBOT_SECRET`, and `SWITCHBOT_OUTLET_DEVICE_ID`
- signed API requests use a timestamp, nonce, and HMAC-SHA256 signature
- the adapter reads only the configured device status
- the only action exposed is `turnOff`
- an already-off outlet produces no action
- an unknown/missing power state blocks action
- missing credentials and provider/API failures fail closed and are surfaced in the returned audit log
- no lock or access path is present in the adapter
- automated tests use fakes/mocks and require no real credential or device

Evidence boundary:
- implementation and mock-test evidence are not physical-device evidence
- do not close issue #2 or claim a real smart-home integration until one credentialed physical outlet run succeeds and its result is reviewed
