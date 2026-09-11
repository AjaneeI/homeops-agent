# AgentCore Deployment Plan

HomeOps Agent is designed so the current Strands agent can move from deterministic judging mode into an AWS-backed runtime without changing the product concept.

## Current State

- Web demo: hosted static dashboard
- Agent logic: Python package
- Strands integration: `src/homeops_agent/strands_adapter.py`
- Device layer: simulated devices for repeatable judging
- Safety policy: lock and access changes are approval-gated
- Audit layer: every state check, action, and approval request is recorded

## Proposed AWS Shape

1. The user starts a Good Night Check from the web interface.
2. The request is sent to a small API endpoint.
3. Amazon Bedrock AgentCore Runtime hosts the Strands agent.
4. AgentCore Gateway exposes approved tools to the agent.
5. Device adapters read smart-home state through safe integrations.
6. The approval gate blocks security-sensitive actions.
7. Audit events are written to storage and surfaced in the dashboard.

## AgentCore Gateway Tools

The first gateway tools should mirror the local contracts:

- `get_device_state(device_id)`
- `execute_safe_action(device_id, action)`
- `request_human_approval(action, reason)`
- `write_audit_log(event)`

Keeping the tool boundary stable lets the project move from simulation to real integrations one piece at a time.

## First Real Integration Candidate

The safest first live integration is a low-risk lighting or outlet action:

- Govee bedside bulb: read state and dim to a bedtime level
- SwitchBot outlet: read state and turn off

Door lock behavior should stay read-only or approval-gated. The MVP should never unlock doors automatically.

## Why This Helps The Submission

AgentCore is not required for the hackathon, but showing the deployment path strengthens the technical story. It demonstrates that HomeOps Agent is more than a front-end demo: the local Strands tools, safety boundary, and audit trail are shaped for a real AWS agent runtime.
