from homeops_agent.agent import HomeOpsAgent
from homeops_agent.tools import scenario_state


def test_good_night_check_executes_low_risk_actions():
    result = HomeOpsAgent(scenario_state("fix-needed")).run_good_night_check()

    assert result["approvals"] == []
    assert {action["action"] for action in result["actions"]} == {"dim_to_20", "turn_off", "confirm_idle"}
    assert any(event["type"] == "safe_action_executed" for event in result["audit_log"])
    assert {call["tool"] for call in result["tool_trace"]} >= {
        "get_device_state",
        "execute_safe_action",
        "write_audit_log",
    }


def test_unknown_lock_status_requires_human_approval():
    result = HomeOpsAgent(scenario_state("lock-unknown")).run_good_night_check()

    assert result["approvals"][0]["approval_status"] == "required"
    assert "Door lock state" in result["approvals"][0]["reason"]
    assert not any(action["device_id"] == "front-door" for action in result["actions"])
    assert any(call["tool"] == "request_human_approval" for call in result["tool_trace"])


def test_device_failure_is_recorded_without_changing_device():
    result = HomeOpsAgent(scenario_state("device-failure")).run_good_night_check()

    failed_action = next(action for action in result["actions"] if action["device_id"] == "bedside-bulb")
    failed_device = next(device for device in result["devices"] if device["device_id"] == "bedside-bulb")

    assert failed_action["ok"] is False
    assert failed_action["reason"] == "Device API is unavailable."
    assert failed_device["status"] == "unreachable"
    assert any(event["type"] == "safe_action_failed" for event in result["audit_log"])
