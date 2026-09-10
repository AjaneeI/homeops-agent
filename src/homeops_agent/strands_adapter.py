from __future__ import annotations

from typing import Any

from .agent import HomeOpsAgent
from .tools import HomeState, scenario_state


SYSTEM_PROMPT = (
    "You are HomeOps Agent. Check smart-home state, complete only low-risk routine actions, "
    "and request human approval for security-sensitive or uncertain actions. Never unlock doors "
    "or change access automatically."
)


def build_strands_tools(state: HomeState) -> list[Any]:
    """Create Strands-decorated tools bound to the selected home state."""
    from strands import tool

    @tool
    def get_device_state(device_id: str) -> dict[str, Any]:
        """Return the current status and allowed low-risk actions for a smart-home device."""
        return state.get_device_state(device_id)

    @tool
    def execute_safe_action(device_id: str, action: str) -> dict[str, Any]:
        """Execute a low-risk routine action only when it is explicitly allowed for the device."""
        return state.execute_safe_action(device_id, action)

    @tool
    def request_human_approval(action: str, reason: str) -> dict[str, Any]:
        """Create a human approval request for security-sensitive or uncertain actions."""
        return state.request_human_approval(action, reason)

    @tool
    def write_audit_log(event: dict[str, Any]) -> dict[str, Any]:
        """Record a visible audit event for a state check, action, skip, failure, or approval request."""
        return state.write_audit_log(event)

    return [get_device_state, execute_safe_action, request_human_approval, write_audit_log]


def build_strands_agent(scenario: str = "fix-needed") -> Any:
    """Build the Strands Agent with HomeOps tools.

    This constructs the official Strands `Agent` object. Calling it may require configured
    model credentials because Bedrock is the default provider.
    """
    from strands import Agent

    state = scenario_state(scenario)
    return Agent(
        tools=build_strands_tools(state),
        system_prompt=SYSTEM_PROMPT,
        name="HomeOps Agent",
        description="Good Night Check agent for mixed smart-home routines.",
    )


def run_deterministic_demo(scenario: str) -> dict[str, Any]:
    """Run the same policy deterministically for local demos and tests."""
    return HomeOpsAgent(scenario_state(scenario)).run_good_night_check()
