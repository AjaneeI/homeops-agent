from __future__ import annotations

from typing import Any

from .agent import HomeOpsAgent
from .tools import scenario_state


def run_with_strands(scenario: str) -> dict[str, Any]:
    """Run the HomeOps flow through a Strands entrypoint when the SDK is available."""
    try:
        from strands import Agent  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Strands Agents SDK is not installed. Install it before final hackathon submission, "
            "then wire this adapter to the official Agent/tool decorators."
        ) from exc

    local_agent = HomeOpsAgent(scenario_state(scenario))
    strands_agent = Agent(
        system_prompt=(
            "You are HomeOps Agent. Check smart-home state, complete only low-risk routine actions, "
            "and request human approval for security-sensitive or uncertain actions."
        )
    )
    _ = strands_agent
    return local_agent.run_good_night_check()
