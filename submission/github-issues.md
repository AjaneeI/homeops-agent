# GitHub Issues To Create After Public Repo Exists

## 1. Add Strands SDK Agent Wrapper

Due: 2026-09-11

Create the Strands Agent wrapper for the Good Night Check flow while preserving the existing tool contracts and safety behavior.

Acceptance criteria:
- Agent invokes device-state and action tools.
- Lock/access actions remain read-only or approval-gated.
- Simulation mode still works without real device credentials.

## 2. Add One Safe Smart-Home Integration

Due: 2026-09-11

Evaluate Govee or SwitchBot as the first real integration. Prefer light or outlet status/action. Do not automate lock changes.

Acceptance criteria:
- README clearly documents required environment variables.
- Demo gracefully falls back to simulation if credentials are missing.
- No security-sensitive device is controlled automatically.

## 3. Finish Web Demo Scenarios

Due: 2026-09-12

Make the three demo scenarios reliable: all clear, fix needed, lock unknown.

Acceptance criteria:
- Fresh browser run works.
- Each scenario has visible state, actions, approvals, and audit log.
- No UI overlap on mobile or desktop.

## 4. Prepare Submission Assets

Due: 2026-09-13

Finalize README, architecture diagram, Devpost copy, screenshots, and demo script.

Acceptance criteria:
- Architecture diagram is visible in docs.
- Devpost copy is ready to paste.
- README states simulated vs. real integrations truthfully.

## 5. Final Submission QA

Due: 2026-09-14

Confirm the public repo, public video, AWS Builder ID, and Devpost submission fields before final submit.

Acceptance criteria:
- Public GitHub repo is reachable.
- Demo video is under five minutes and public.
- Devpost checklist is complete before 8:00 PM ET.
