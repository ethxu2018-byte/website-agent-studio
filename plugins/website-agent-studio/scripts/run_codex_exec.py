#!/usr/bin/env python3
"""Execute a Website Agent Studio run packet through codex exec."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--response-file", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--plugin-root", required=True)
    parser.add_argument("--schema-file")
    parser.add_argument("--use-schema", action="store_true")
    parser.add_argument("--model")
    parser.add_argument("--sandbox-mode", default="workspace-write", choices=["read-only", "workspace-write", "danger-full-access"])
    parser.add_argument("--skip-git-repo-check", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    prompt_file = Path(args.prompt_file).expanduser().resolve()
    response_file = Path(args.response_file).expanduser().resolve()
    project_root = Path(args.project_root).expanduser().resolve()
    plugin_root = Path(args.plugin_root).expanduser().resolve()
    schema_file = Path(args.schema_file).expanduser().resolve() if args.schema_file else plugin_root / "schemas" / "agent_response.schema.json"

    prompt_text = prompt_file.read_text()

    command = [
        "codex",
        "exec",
        "-",
        "-C",
        str(project_root),
        "--sandbox",
        args.sandbox_mode,
        "-o",
        str(response_file),
    ]
    if args.use_schema:
        command.extend(["--output-schema", str(schema_file)])
    if args.skip_git_repo_check:
        command.append("--skip-git-repo-check")
    if args.model:
        command.extend(["--model", args.model])

    if args.dry_run:
        print(" ".join(command))
        return 0

    result = subprocess.run(command, input=prompt_text, text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(
            "\n".join(
                [
                    f"codex exec failed with exit code {result.returncode}",
                    result.stdout.strip(),
                    result.stderr.strip(),
                ]
            ).strip()
        )

    if not response_file.exists():
        raise SystemExit("codex exec finished without producing a response file.")

    raw = response_file.read_text().strip()
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"codex exec produced invalid JSON: {exc}") from exc

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
