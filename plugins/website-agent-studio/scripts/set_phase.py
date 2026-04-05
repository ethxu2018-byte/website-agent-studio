#!/usr/bin/env python3
"""Set current phase and active skill in a project state file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--skill", required=False)
    args = parser.parse_args()

    state_path = Path(args.state)
    state = json.loads(state_path.read_text())
    state["current_phase"] = args.phase
    state["active_skill"] = args.skill or args.phase

    phase_status = state.setdefault("phase_status", {})
    if args.phase in phase_status and phase_status[args.phase] == "pending":
        phase_status[args.phase] = "in_progress"

    state_path.write_text(json.dumps(state, indent=2) + "\n")
    print(f"Set phase -> {args.phase}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

