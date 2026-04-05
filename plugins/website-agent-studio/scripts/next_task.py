#!/usr/bin/env python3
"""Print the current phase summary and next queue item."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--queue", required=True)
    args = parser.parse_args()

    state = load_json(Path(args.state))
    queue = load_json(Path(args.queue))

    rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    open_tasks = [item for item in queue if item.get("status") == "open"]
    open_tasks.sort(key=lambda item: (rank.get(item.get("priority", "P3"), 9), item.get("id", "")))

    print(f"Project: {state.get('project_id', 'unknown')}")
    print(f"Current phase: {state.get('current_phase', 'unknown')}")
    print(f"Active skill: {state.get('active_skill', 'unknown')}")
    print("")

    if state.get("blockers"):
      print("Blockers:")
      for blocker in state["blockers"]:
          print(f"- {blocker}")
      print("")

    if open_tasks:
      task = open_tasks[0]
      print("Next queue task:")
      print(f"- id: {task.get('id')}")
      print(f"- title: {task.get('title')}")
      print(f"- phase: {task.get('phase')}")
      print(f"- owner_skill: {task.get('owner_skill')}")
      print(f"- priority: {task.get('priority')}")
    else:
      print("Next queue task:")
      print("- none")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

