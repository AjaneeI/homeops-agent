from __future__ import annotations

import argparse
import json

from .strands_adapter import build_strands_agent, run_deterministic_demo, run_live_strands_demo


SCENARIOS = ["all-clear", "fix-needed", "lock-unknown", "device-failure"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the HomeOps Agent Good Night Check demo.")
    parser.add_argument(
        "--scenario",
        choices=SCENARIOS,
        default="fix-needed",
        help="Demo scenario to run.",
    )
    parser.add_argument(
        "--build-strands-agent",
        action="store_true",
        help="Instantiate the official Strands Agent object without invoking a model.",
    )
    parser.add_argument(
        "--live-strands-run",
        action="store_true",
        help="Invoke the official Strands Agent. Requires configured model provider credentials.",
    )
    args = parser.parse_args()

    if args.build_strands_agent:
        agent = build_strands_agent(args.scenario)
        print(f"Built Strands agent: {agent.name}")
        return

    if args.live_strands_run:
        try:
            print(run_live_strands_demo(args.scenario))
        except Exception as error:
            print(
                "Live Strands invocation could not run because model provider credentials are not configured "
                f"or are unavailable in this environment. The Strands agent object still builds successfully. Error: {error}"
            )
        return

    print(json.dumps(run_deterministic_demo(args.scenario), indent=2))


if __name__ == "__main__":
    main()
