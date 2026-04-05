#!/usr/bin/env python3
"""Bridge script for Claude Code-style executor commands."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--response-file", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--command-template", required=False, default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    template = args.command_template.strip()
    if not template:
        raise SystemExit(
            "Claude Code command template is required. Example: "
            "\"claude --print --output json --cd {project_root} < {prompt_file} > {response_file}\""
        )

    values = {
        "prompt_file": str(Path(args.prompt_file).expanduser().resolve()),
        "response_file": str(Path(args.response_file).expanduser().resolve()),
        "project_root": str(Path(args.project_root).expanduser().resolve()),
    }
    command = template.format(**values)

    if args.dry_run:
        print(command)
        return 0

    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(
            "\n".join(
                [
                    f"Claude Code command failed with exit code {result.returncode}",
                    result.stdout.strip(),
                    result.stderr.strip(),
                ]
            ).strip()
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
