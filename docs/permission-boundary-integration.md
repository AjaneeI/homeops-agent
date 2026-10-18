# Host-enforced permission boundary (simulated HomeOps)

## Scope and objective

The public HomeOps agent already exposes a Strands `@tool` function named
`execute_safe_action(device_id, action)`. Previously, the simulated device
method trusted each device's `safe_actions` hint. That was narrower than
unrestricted tool access, but insufficient as the final authorization rule:
incorrect or expanded capability hints could approve an unintended action.

This integration adds an independently defined, host-owned policy at the actual
execution entry point. Both the deterministic Good Night workflow and the
Strands-facing action tool call `HomeState.execute_safe_action`.

```text
untrusted agent arguments
  -> Strands execute_safe_action tool
  -> HomeState.execute_safe_action    [trusted decision + outcome record]
  -> decide_action(device_id, action, trusted Device)
  -> allow exactly one approved pair
  -> _apply_safe_action               [mutates simulated state]
```

`_apply_safe_action` is never registered as an agent-facing tool. No model
provider is needed for deterministic verification.

## Exact policy

| Device ID | Expected kind | Only executable action |
| --- | --- | --- |
| `bedside-bulb` | `light` | `dim_to_20` |
| `switchbot-outlet` | `outlet` | `turn_off` |
| `fire-tv` | `media` | `confirm_idle` |

- An exact known device, kind, host-policy action, and simulated
  `safe_actions` capability are all necessary to execute.
- Any lock or `front-door` action is `approval_required` and does not
  execute. An approval request alone cannot lift it; no approval resolution
  flow has been implemented.
- Unknown devices, bad types, mismatched IDs/kinds, disallowed operations,
  and missing capability are denied before the mutator.
- If the evaluator raises or returns an unsupported verdict, the entry point
  denies by default.
- If an authorized device is unreachable, the existing failure response is
  preserved and no mutation occurs.
- Authorized arguments are passed unchanged to the mutator; there is no
  model-controlled policy update, argument rewriting, or raw shell tool.

The immutable device record and exact policy pair belong to the trusted host.
A model-visible `safe_actions` list is explanatory metadata, not authority.

## Evidence and how to reproduce

```bash
python -m pip install -e ".[dev]"
python -m pytest -q tests/test_permission_boundary.py
python -m pytest -q
PYTHONPATH=src python -m homeops_agent.cli --scenario fix-needed
```

The focused tests call the **same tool functions passed to** `@strands.tool`
using a locally injected identity decorator. This proves that the host
dispatcher mediates a model-proposed tool call without invoking a language
model. With the pinned Strands SDK installed, a separate test checks real
decorator registration; it still does not make a live model call.

The tests check: exact authorized execution once; denied/approval-required
requests causing no protected effect; unknown and malformed input; injected
approval claims; a misleading device capability hint; kind/ID mismatch;
policy failures; device outage; exact arguments at mutation; and an
agent-authored fake audit entry failing to authorize a tool action. Existing
Good Night Check scenarios remain regression coverage.

The trusted in-memory `HomeState.enforcement_log` records verdict and
whether the mutator ran. It is separate from `audit_log`: the agent-facing
`write_audit_log` tool can produce arbitrary narrative entries, so that
agent-authored log is **not authoritative enforcement evidence**.

## Trust and limitations

- The host and its Python policy module are **trusted**. An adversary with
  arbitrary code execution inside the host could call the private mutator or
  change the policy. This is not a sandbox or backend authorization.
- The devices and side effects are simulated. No real smart-home API,
  locks, credentials, or real-device isolation are exercised.
- The policy is specific to the three published low-risk actions, not an
  extensible governance framework or general-purpose command filter.
- Reads, approval request wording, and agent-authored audit entries remain
  outside this one-action policy. Those entries cannot grant tool execution.
- `enforcement_log` is in-memory and not tamper-evident or durable; do not
  present it as a production security audit service.
- The action policy is a **local analogue of pre-tool-call enforcement**, not
  an Agent Control Specification (ACS) implementation, agent-hooks emitter,
  or conformance claim. A follow-up may compare it against the pinned
  `responsibleai/agent-control-spec` runtime and
  `microsoft/agent-governance-toolkit` host adapter.
- No live Strands model/tool-calling quality, production guarantees, OS
  isolation, or upstream contribution is claimed.

## Contribution direction

A possible next contribution is a framework-agnostic regression case that
asserts **a denied tool call never reaches its effecting callback**, including
approval-shaped and malformed proposals. Before an upstream issue or PR,
inspect current specifications and existing test coverage, isolate a minimal
reproducer, and confirm maintainers actually need the case. The previous
Agentic Analytics ASSERT Q3 rejection is a separate, completed experiment.
