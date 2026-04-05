#!/usr/bin/env python3
"""Initialize a new website-agent project scaffold from templates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def write_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--project-id", required=True)
    args = parser.parse_args()

    plugin_root = Path(args.plugin_root)
    output_root = Path(args.output_root)
    project_id = args.project_id

    profile = json.loads((plugin_root / "templates" / "project_profile.template.json").read_text())
    state = json.loads((plugin_root / "templates" / "project_state.template.json").read_text())
    queue = json.loads((plugin_root / "templates" / "workflow_queue.template.json").read_text())

    profile["project_id"] = project_id
    profile["project_name"] = project_id.replace("-", " ").title()
    state["project_id"] = project_id

    write_json(output_root / "profiles" / f"{project_id}.project_profile.json", profile)
    write_json(output_root / "states" / f"{project_id}.project_state.json", state)
    write_json(output_root / "queues" / f"{project_id}.workflow_queue.json", queue)

    print(f"Initialized project scaffold for {project_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

