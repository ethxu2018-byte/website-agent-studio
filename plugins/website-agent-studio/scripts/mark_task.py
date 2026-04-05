#!/usr/bin/env python3
"""Mark a workflow queue task status."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--status", required=True, choices=["open", "in_progress", "completed", "blocked"])
    args = parser.parse_args()

    queue_path = Path(args.queue)
    queue = json.loads(queue_path.read_text())

    found = False
    for item in queue:
        if item.get("id") == args.task_id:
            item["status"] = args.status
            found = True
            break

    if not found:
        raise SystemExit(f"Task not found: {args.task_id}")

    queue_path.write_text(json.dumps(queue, indent=2) + "\n")
    print(f"Updated {args.task_id} -> {args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

