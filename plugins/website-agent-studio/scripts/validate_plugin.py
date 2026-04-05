#!/usr/bin/env python3
"""Validate required Website Agent Studio plugin files."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED = [
    ".codex-plugin/plugin.json",
    "agents/openai.yaml",
    "templates/project_profile.template.json",
    "templates/project_state.template.json",
    "templates/workflow_queue.template.json",
    "scripts/init_project.py",
    "scripts/next_task.py",
    "skills/state-sync/SKILL.md",
    "skills/project-brief/SKILL.md",
    "skills/requirements-ia/SKILL.md",
    "skills/brand-assets/SKILL.md",
    "skills/frontend-build/SKILL.md",
    "skills/backend-integrations/SKILL.md",
    "skills/qa-release/SKILL.md",
    "skills/handoff-continuity/SKILL.md",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin-root", required=True)
    args = parser.parse_args()

    root = Path(args.plugin_root)
    missing = [rel for rel in REQUIRED if not (root / rel).exists()]

    if missing:
        print("Missing required files:")
        for rel in missing:
            print(f"- {rel}")
        raise SystemExit(1)

    print("Plugin structure is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

