from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Device:
    id: str
    name: str
    kind: str
    status: str
    safe_actions: tuple[str, ...]


class HomeState:
    def __init__(self, devices: dict[str, Device]) -> None:
        self.devices = devices
        self.audit_log: list[dict[str, Any]] = []
        self.tool_trace: list[dict[str, Any]] = []

    def record_tool_call(self, name: str, input_payload: dict[str, Any], result: dict[str, Any]) -> None:
        self.tool_trace.append({"tool": name, "input": input_payload, "result": result})

    def get_device_state(self, device_id: str) -> dict[str, Any]:
        device = self.devices[device_id]
        return {
            "device_id": device.id,
            "name": device.name,
            "kind": device.kind,
            "status": device.status,
            "safe_actions": list(device.safe_actions),
        }

    def execute_safe_action(self, device_id: str, action: str) -> dict[str, Any]:
        device = self.devices[device_id]
        if device.status == "unreachable":
            return {"ok": False, "device_id": device_id, "action": action, "reason": "Device API is unavailable."}

        if action not in device.safe_actions:
            return {"ok": False, "device_id": device_id, "action": action, "reason": "Action is not low-risk."}

        next_status = {
            "dim_to_20": "dimmed to 20%",
            "turn_off": "off",
            "confirm_idle": "idle",
        }.get(action, device.status)

        self.devices[device_id] = replace(device, status=next_status)
        return {"ok": True, "device_id": device_id, "action": action, "status": next_status}

    def request_human_approval(self, action: str, reason: str) -> dict[str, Any]:
        return {"approval_status": "required", "action": action, "reason": reason}

    def write_audit_log(self, event: dict[str, Any]) -> dict[str, Any]:
        entry = {"timestamp": datetime.now(timezone.utc).isoformat(), **event}
        self.audit_log.append(entry)
        return entry


def scenario_state(name: str) -> HomeState:
    scenarios = {
        "all-clear": {
            "front-door": Device("front-door", "Front Door Lock", "lock", "locked", ()),
            "bedside-bulb": Device("bedside-bulb", "Govee Bedside Bulb", "light", "dimmed to 20%", ("dim_to_20",)),
            "switchbot-outlet": Device("switchbot-outlet", "SwitchBot Outlet", "outlet", "off", ("turn_off",)),
            "fire-tv": Device("fire-tv", "Fire TV", "media", "idle", ("confirm_idle",)),
            "echo-group": Device("echo-group", "Echo Surround Group", "speaker_group", "quiet", ()),
        },
        "fix-needed": {
            "front-door": Device("front-door", "Front Door Lock", "lock", "locked", ()),
            "bedside-bulb": Device("bedside-bulb", "Govee Bedside Bulb", "light", "on at 80%", ("dim_to_20",)),
            "switchbot-outlet": Device("switchbot-outlet", "SwitchBot Outlet", "outlet", "on", ("turn_off",)),
            "fire-tv": Device("fire-tv", "Fire TV", "media", "playing", ("confirm_idle",)),
            "echo-group": Device("echo-group", "Echo Surround Group", "speaker_group", "quiet", ()),
        },
        "lock-unknown": {
            "front-door": Device("front-door", "Front Door Lock", "lock", "unknown", ()),
            "bedside-bulb": Device("bedside-bulb", "Govee Bedside Bulb", "light", "on at 60%", ("dim_to_20",)),
            "switchbot-outlet": Device("switchbot-outlet", "SwitchBot Outlet", "outlet", "off", ("turn_off",)),
            "fire-tv": Device("fire-tv", "Fire TV", "media", "idle", ("confirm_idle",)),
            "echo-group": Device("echo-group", "Echo Surround Group", "speaker_group", "quiet", ()),
        },
        "device-failure": {
            "front-door": Device("front-door", "Front Door Lock", "lock", "locked", ()),
            "bedside-bulb": Device("bedside-bulb", "Govee Bedside Bulb", "light", "unreachable", ("dim_to_20",)),
            "switchbot-outlet": Device("switchbot-outlet", "SwitchBot Outlet", "outlet", "on", ("turn_off",)),
            "fire-tv": Device("fire-tv", "Fire TV", "media", "idle", ("confirm_idle",)),
            "echo-group": Device("echo-group", "Echo Surround Group", "speaker_group", "quiet", ()),
        },
    }
    return HomeState(dict(scenarios[name]))
