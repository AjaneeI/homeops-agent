from __future__ import annotations

from typing import Any

from .tools import HomeState


class HomeOpsAgent:
    def __init__(self, state: HomeState) -> None:
        self.state = state

    def run_good_night_check(self) -> dict[str, Any]:
        actions: list[dict[str, Any]] = []
        approvals: list[dict[str, Any]] = []

        for device_id in ["front-door", "bedside-bulb", "switchbot-outlet", "fire-tv", "echo-group"]:
            device = self.state.get_device_state(device_id)
            self.state.record_tool_call("get_device_state", {"device_id": device_id}, device)
            self._audit({"type": "state_checked", "device": device["name"], "status": device["status"]})

            if device_id == "front-door":
                if device["status"] != "locked":
                    approval = self._approval(
                        "verify_front_door_lock",
                        "Door lock state is security-sensitive or uncertain, so the agent will not change it automatically.",
                    )
                    approvals.append(approval)
                    self._audit({"type": "approval_requested", **approval})
                continue

            if device_id == "bedside-bulb" and device["status"] != "dimmed to 20%":
                actions.append(self._execute(device_id, "dim_to_20"))
            elif device_id == "switchbot-outlet" and device["status"] == "on":
                actions.append(self._execute(device_id, "turn_off"))
            elif device_id == "fire-tv" and device["status"] != "idle":
                actions.append(self._execute(device_id, "confirm_idle"))

        summary = "Good Night Check complete with human review required." if approvals else "Good Night Check complete."
        return {
            "summary": summary,
            "devices": [self.state.get_device_state(device_id) for device_id in self.state.devices],
            "actions": actions,
            "approvals": approvals,
            "audit_log": self.state.audit_log,
            "tool_trace": self.state.tool_trace,
        }

    def _execute(self, device_id: str, action: str) -> dict[str, Any]:
        result = self.state.execute_safe_action(device_id, action)
        self.state.record_tool_call("execute_safe_action", {"device_id": device_id, "action": action}, result)
        event_type = "safe_action_executed" if result["ok"] else "safe_action_failed"
        self._audit({"type": event_type, **result})
        return result

    def _approval(self, action: str, reason: str) -> dict[str, Any]:
        result = self.state.request_human_approval(action, reason)
        self.state.record_tool_call("request_human_approval", {"action": action, "reason": reason}, result)
        return result

    def _audit(self, event: dict[str, Any]) -> dict[str, Any]:
        result = self.state.write_audit_log(event)
        self.state.record_tool_call("write_audit_log", {"event": event}, result)
        return result
