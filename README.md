# HomeOps Agent

HomeOps Agent is an applied AI prototype for treating the home as an operations system rather than a collection of disconnected smart-device routines. It checks device state, completes low-risk routine actions, and escalates safety-sensitive decisions to the human.

[Live case study](https://ajaneeigharo.com/work/homeops-agent)

## Recruiter Quick Read

**What I built:** a deterministic agent workflow around a `Good Night Check` scenario, with explicit tool contracts, simulated smart-home devices, approval gates, failure handling, and an audit trail.

**What this demonstrates:** agent/tool design, human-in-the-loop controls, safety boundaries, deterministic testing/demo behavior, failure-path thinking, and integration planning.

**Current implementation state:** the local workflow and web demo are implemented with simulated devices. A Strands adapter is wired so the agent object can be built, while live model-provider credentials and a real device integration are not part of the current public implementation.

## Why This Project Exists

Smart homes often become a pile of separate apps, routines, and voice commands. HomeOps Agent explores a different pattern: an agent checks what is true now, resolves low-risk issues quietly, and preserves human control when access, locks, uncertainty, or failed integrations raise the risk.

The design question is:

> What should an agent be allowed to do automatically, and where should it stop and ask a human?

## Current Scenario: Good Night Check

The demo covers four paths:

- **All clear:** the home is already ready for the night.
- **Outlet/light fix needed:** the agent performs low-risk actions such as dimming the bedside bulb and turning off an outlet.
- **Lock status unknown:** the agent does not change the lock automatically and requests human review.
- **Device API failure:** the agent records the failure, reports it clearly, and leaves the device unchanged.

The dashboard includes a visible tool-call trace showing device-state reads, safe action execution, approval requests, and audit-log writes.

## Safety Boundaries

- The agent never unlocks doors automatically.
- Door locks and access changes are read-only or approval-gated.
- Failed device calls leave the device unchanged.
- Every action, skipped action, and approval request is recorded in the audit trail.
- The deterministic local demo is kept separate from live model-provider behavior so safety logic can be inspected reliably.

## Tool Contracts

- `get_device_state(device_id) -> status`
- `execute_safe_action(device_id, action) -> result`
- `request_human_approval(action, reason) -> approval_status`
- `write_audit_log(event) -> log_entry`

## Architecture

The agent tools live in `src/homeops_agent/tools.py`, while the Good Night Check policy is defined in `src/homeops_agent/agent.py`. `src/homeops_agent/strands_adapter.py` uses the Strands `Agent` and `@tool` interfaces.

The core separation is intentional:

```text
Device state
   |
   v
Agent policy
   |
   +--> low-risk action --------> execute + log
   |
   +--> safety-sensitive action -> human approval
   |
   +--> failed/unknown state ----> report + leave unchanged
```

## Run Locally

Start the web demo:

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

Run the failure path:

```bash
PYTHONPATH=src python -m homeops_agent.cli --scenario device-failure
```

Verify the Strands agent object can be built after installing dependencies:

```bash
PYTHONPATH=src python -m homeops_agent.cli --build-strands-agent
```

Run the automated tests:

```bash
python -m pytest
```

A live Strands entrypoint is also available when model-provider credentials are configured:

```bash
PYTHONPATH=src python -m homeops_agent.cli --live-strands-run --scenario fix-needed
```

## Simulated vs. Real Integrations

The current public demo uses simulated devices so the agent's safety and failure behavior can be reproduced consistently. It does **not** claim a production smart-home deployment.

A useful next engineering step would be one real, low-risk device integration such as a light or outlet status/action path while preserving door-lock behavior as read-only or approval-gated.

## Design Decisions

- Prefer deterministic behavior where safety rules can be tested directly.
- Separate safe routine actions from high-impact actions that require approval.
- Treat uncertainty as a reason to stop, not as permission to guess.
- Keep an audit trail so agent behavior can be inspected after the fact.
- Add real integrations incrementally rather than broadening permissions before the safety model is clear.

## Supporting Docs

- [`BUILD_LOG.md`](BUILD_LOG.md) summarizes implemented behavior, deterministic evidence, and scope boundaries.
- [`docs/judging-map.md`](docs/judging-map.md) captures the original hackathon framing and scoring map.
- [`docs/agentcore-deployment-plan.md`](docs/agentcore-deployment-plan.md) captures the planned AWS/AgentCore deployment path.

Those documents remain as project history. The README is now the current portfolio-facing description of the implemented system and its limitations.
