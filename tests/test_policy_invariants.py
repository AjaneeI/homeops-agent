import pytest

from homeops_agent.agent import HomeOpsAgent
from homeops_agent.tools import scenario_state


SCENARIOS = ["all-clear", "fix-needed", "lock-unknown", "device-failure"]


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_front_door_is_never_changed_automatically(scenario: str) -> None:
    result = HomeOpsAgent(scenario_state(scenario)).run_good_night_check()

    assert not any(action.get("device_id") == "front-door" for action in result["actions"])
    assert not any(
        call["tool"] == "execute_safe_action"
        and call["input"].get("device_id") == "front-door"
        for call in result["tool_trace"]
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_every_scenario_preserves_a_visible_audit_trail(scenario: str) -> None:
    result = HomeOpsAgent(scenario_state(scenario)).run_good_night_check()

    checked_devices = {
        event["device"]
        for event in result["audit_log"]
        if event.get("type") == "state_checked"
    }
    assert checked_devices == {
        "Front Door Lock",
        "Govee Bedside Bulb",
        "SwitchBot Outlet",
        "Fire TV",
        "Echo Surround Group",
    }
    assert all(
        any(call["tool"] == "write_audit_log" and call["result"] == event for call in result["tool_trace"])
        for event in result["audit_log"]
    )


def test_all_clear_path_has_no_actions_or_approvals() -> None:
    result = HomeOpsAgent(scenario_state("all-clear")).run_good_night_check()

    assert result["actions"] == []
    assert result["approvals"] == []
    assert result["summary"] == "Good Night Check complete."
