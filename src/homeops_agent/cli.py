from __future__ import annotations

import argparse
import json

from .strands_adapter import build_strands_agent, run_deterministic_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the HomeOps Agent Good Night Check demo.")
    parser.add_argument(
        "--scenario",
        choices=["all-clear", "fix-needed", "lock-unknown"],
        default="fix-needed",
        help="Demo scenario to run.",
    )
    parser.add_argument(
        "--build-strands-agent",
        action="store_true",
        help="Instantiate the official Strands Agent object without invoking a model.",
    )
    args = parser.parse_args()

    if args.build_strands_agent:
        agent = build_strands_agent(args.scenario)
        print(f"Built Strands agent: {agent.name}")
        return

    print(json.dumps(run_deterministic_demo(args.scenario), indent=2))


if __name__ == "__main__":
    main()
