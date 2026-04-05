from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "website-agent-studio"
CODEX_WRAPPER = PLUGIN_ROOT / "scripts" / "run_codex_exec.py"
CLAUDE_WRAPPER = PLUGIN_ROOT / "scripts" / "run_claude_code.py"


class ShellPresetTests(unittest.TestCase):
    def test_codex_wrapper_dry_run_builds_command(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(CODEX_WRAPPER),
                "--prompt-file",
                str(REPO_ROOT / "README.md"),
                "--response-file",
                str(REPO_ROOT / "tmp-response.json"),
                "--project-root",
                str(REPO_ROOT),
                "--plugin-root",
                str(PLUGIN_ROOT),
                "--skip-git-repo-check",
                "--dry-run",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("codex exec", result.stdout)
        self.assertIn("--skip-git-repo-check", result.stdout)
        self.assertIn("--sandbox workspace-write", result.stdout)

    def test_claude_wrapper_dry_run_expands_placeholders(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(CLAUDE_WRAPPER),
                "--prompt-file",
                str(REPO_ROOT / "README.md"),
                "--response-file",
                str(REPO_ROOT / "tmp-response.json"),
                "--project-root",
                str(REPO_ROOT),
                "--command-template",
                "claude --cd {project_root} < {prompt_file} > {response_file}",
                "--dry-run",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("claude --cd", result.stdout)
        self.assertIn("tmp-response.json", result.stdout)


if __name__ == "__main__":
    unittest.main()
