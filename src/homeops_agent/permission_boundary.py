"""Deterministic host-owned authorization for simulated HomeOps actions.

This is a small local policy, not an Agent Control Specification implementation.
Model text, tool arguments and per-device capability hints do not grant authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol


Decision = Literal["allow", "deny", "approval_required"]


class DeviceView(Protocol):
    id: str
    kind: str
    safe_actions: tuple[str, ...]


@dataclass(frozen=True)
class ActionVerdict:
    decision: Decision
    reason: str


# Host-owned and intentionally smaller than any model-visible safe_actions hint.
_ALLOWED: dict[str, tuple[str, str]] = {
    "bedside-bulb": ("light", "dim_to_20"),
    "switchbot-outlet": ("outlet", "turn_off"),
    "fire-tv": ("media", "confirm_idle"),
}


def decide_action(device_id: object, action: object, device: DeviceView | None) -> ActionVerdict:
    """Return a fail-closed decision for the exact proposed action."""
    if type(device_id) is not str or type(action) is not str or not device_id or not action:
        return ActionVerdict("deny", "Invalid action arguments.")
    if device is None or device.id != device_id:
        return ActionVerdict("deny", "Unknown or mismatched device.")

    # Lock and access actions cannot be lifted by an agent-provided claim.
    if device_id == "front-door" or device.kind == "lock":
        return ActionVerdict("approval_required", "Lock or access actions require human review.")

    rule = _ALLOWED.get(device_id)
    if rule is None or device.kind != rule[0] or action != rule[1]:
        return ActionVerdict("deny", "Action is outside the host policy.")
    if action not in device.safe_actions:
        return ActionVerdict("deny", "Device does not advertise this action as safe.")
    return ActionVerdict("allow", "Approved low-risk action.")
