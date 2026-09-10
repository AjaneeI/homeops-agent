from homeops_agent.agent import HomeOpsAgent
from homeops_agent.tools import scenario_state


def test_good_night_check_executes_low_risk_actions():
    result = HomeOpsAgent(scenario_state("fix-needed")).run_good_night_check()

    assert result["approvals"] == []
    assert {action["action"] for action in result["actions"]} == {"dim_to_20", "turn_off", "confirm_idle"}
    assert any(event["type"] == "safe_action_executed" for event in result["audit_log"])


def test_unknown_lock_status_requires_human_approval():
    result = HomeOpsAgent(scenario_state("lock-unknown")).run_good_night_check()

    assert result["approvals"][0]["approval_status"] == "required"
    assert "Door lock state" in result["approvals"][0]["reason"]
    assert not any(action["device_id"] == "front-door" for action in result["actions"])
