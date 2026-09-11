# Judging Map

This page maps HomeOps Agent to the Agents for Humans Hackathon judging criteria.

## Technological Implementation

HomeOps Agent uses a Strands-ready architecture with explicit tool contracts:

- `get_device_state`
- `execute_safe_action`
- `request_human_approval`
- `write_audit_log`

The project includes a deterministic web demo for reliable judging and a Python adapter using the official Strands `Agent` and `@tool` interfaces. The implementation is intentionally transparent: the dashboard shows the tool trace so judges can see how the agent moves from state reading to safe actions, approval requests, and audit logging.

The CLI also includes a live Strands invocation path for environments with model provider credentials configured. In environments without credentials, the command reports that missing dependency clearly while still confirming that the Strands agent object can be built.

## Design

The demo is a complete product experience around one focused workflow: Good Night Check. It avoids a generic chat box and instead shows the operational surface a user would need at night:

- current device state
- actions taken
- approvals required
- audit history
- tool trace

The interface supports three scenarios so the evaluator can see routine success, routine fixes, and safety escalation.

## Potential Impact

Smart homes often spread daily routines across separate devices, apps, voice commands, and automations. HomeOps Agent frames the home as an operations system: it reduces repeated checking while keeping humans responsible for access, locks, and ambiguous device states.

The initial audience is people managing mixed smart-home setups. The same pattern could extend to caregivers, renters, property managers, and households where routines need to be reliable but not reckless.

## Creativity And Originality

The project is not another universal remote or command wrapper. The original idea is the safety-aware operations layer: an agent that knows the difference between routine work and a decision that needs a person.

That distinction is especially important for smart homes because convenience and safety are often in tension. HomeOps Agent makes that tension visible and designs around it.

## Presentation

The demo video should show the project working end to end:

1. Start with the problem: fragmented smart-home routines.
2. Run the Good Night Check with low-risk fixes.
3. Show the visible tool trace.
4. Switch to the lock-unknown scenario.
5. Show the approval request and audit trail.
6. End with the thesis: less repetitive checking, stronger human control.
