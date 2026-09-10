# HomeOps Agent

HomeOps Agent coordinates a mixed smart home by checking device state, completing low-risk routine actions, and escalating safety-sensitive decisions to the human.

This hackathon MVP focuses on one polished scenario: **Good Night Check**. It uses a Strands-ready agent shape with explicit tools, simulated smart-home devices, an approval gate, and an audit trail.

## Why It Matters

Smart homes often become a pile of separate routines, apps, and voice commands. HomeOps Agent treats the home like an operations system: it checks current state first, takes safe routine actions, and keeps humans in control of decisions involving access, locks, or uncertainty.

## MVP Demo

The web demo includes three scenarios:

- **All clear:** the home is already ready for the night.
- **Outlet/light fix needed:** the agent dims the bedside bulb and turns off the SwitchBot outlet.
- **Lock status unknown:** the agent does not change the lock automatically and requests human review.

## Safety Boundaries

- The agent never unlocks doors automatically.
- Door locks and access changes are read-only or approval-gated.
- Failed device calls leave the device unchanged.
- Every action, skipped action, and approval request is recorded in the audit trail.

## Tool Contracts

- `get_device_state(device_id) -> status`
- `execute_safe_action(device_id, action) -> result`
- `request_human_approval(action, reason) -> approval_status`
- `write_audit_log(event) -> log_entry`

## Run Locally

```bash
python3 -m http.server 4173 -d web
```

Then open:

```text
http://localhost:4173
```

## Strands Integration

The MVP keeps agent tools isolated in `src/homeops_agent/tools.py` and the Good Night Check policy in `src/homeops_agent/agent.py`. `src/homeops_agent/strands_adapter.py` is the handoff point for the Strands Agents SDK.

Strands is not vendored into this repo. Before final submission, install the SDK in your environment and replace the adapter stub with the official Strands `Agent` and tool decorators while preserving the same tool contracts and safety policy.

## Simulated vs. Real Integrations

Current demo state is simulated so the judging walkthrough is reliable. One real safe integration can be added before submission, preferably Govee light control or SwitchBot outlet status/action. Door-lock behavior should remain read-only or approval-gated.

## Submission Checklist

- [ ] Public GitHub repo named `homeops-agent`
- [x] README skeleton
- [x] MIT license
- [x] Architecture diagram draft
- [x] Good Night Check local demo
- [ ] Strands SDK installed and wired to adapter
- [ ] Public demo video under five minutes
- [ ] AWS Builder ID
- [ ] Devpost submission before September 14, 2026 at 8:00 PM ET
