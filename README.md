# HomeOps Agent

HomeOps Agent is not a smart-home remote. It is an operations layer for the home: it checks device state, completes low-risk routine actions, and escalates safety-sensitive decisions to the human.

This hackathon MVP focuses on one polished scenario: **Good Night Check**. It uses a Strands-ready agent shape with explicit tools, simulated smart-home devices, an approval gate, and an audit trail.

## Why It Matters

Smart homes often become a pile of separate routines, apps, and voice commands. HomeOps Agent treats the home like an operations system: it checks what is true now, fixes routine issues quietly, and keeps humans in control of decisions involving access, locks, or uncertainty.

## MVP Demo

The web demo includes three scenarios:

- **All clear:** the home is already ready for the night.
- **Outlet/light fix needed:** the agent dims the bedside bulb and turns off the SwitchBot outlet.
- **Lock status unknown:** the agent does not change the lock automatically and requests human review.

The dashboard also includes a visible tool-call trace so judges can see the agent workflow: device-state reads, safe action execution, approval requests, and audit-log writes.

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

Run the deterministic agent simulation:

```bash
PYTHONPATH=src python -m homeops_agent.cli --scenario fix-needed
```

Verify the Strands agent object can be built after installing dependencies:

```bash
PYTHONPATH=src python -m homeops_agent.cli --build-strands-agent
```

## Strands Integration

The MVP keeps agent tools isolated in `src/homeops_agent/tools.py` and the Good Night Check policy in `src/homeops_agent/agent.py`. `src/homeops_agent/strands_adapter.py` uses the official Strands `Agent` and `@tool` interfaces.

The local web demo stays deterministic so judges can reliably see the safety behavior. The Strands entrypoint is ready for model-backed execution once AWS Bedrock or another model provider is configured.

## Judging Strategy

HomeOps Agent is built around one thesis: it is not a smart-home remote, but an operations layer for the home. The scoring case is documented in [`docs/judging-map.md`](docs/judging-map.md).

The strongest technical next step is an AWS-backed Strands invocation or AgentCore deployment path. The current deployment plan is captured in [`docs/agentcore-deployment-plan.md`](docs/agentcore-deployment-plan.md).

## Simulated vs. Real Integrations

Current demo state is simulated so the judging walkthrough is reliable. One real safe integration can be added before submission, preferably Govee light control or SwitchBot outlet status/action. Door-lock behavior should remain read-only or approval-gated.

## Submission Checklist

- [x] Public GitHub repo named `homeops-agent`
- [x] README skeleton
- [x] MIT license
- [x] Architecture diagram draft
- [x] Good Night Check local demo
- [x] Visible tool-call trace
- [x] Draft video script
- [x] Demo narration, captions, and recording guide
- [x] Judging map
- [x] AgentCore deployment plan
- [x] Strands SDK installed locally and wired to adapter
- [ ] Model provider credentials configured for live Strands invocation
- [ ] AWS credits request form submitted
- [ ] Public demo video under five minutes
- [ ] AWS Builder ID
- [ ] Devpost submission before September 14, 2026 at 8:00 PM ET
