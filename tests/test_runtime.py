from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "website-agent-studio"
WRAPPER = PLUGIN_ROOT / "scripts" / "agent_runtime.py"
INIT_SCRIPT = PLUGIN_ROOT / "scripts" / "init_project.py"


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.output_root = self.workspace / "agent-data"
        subprocess.run(
            [
                "python3",
                str(INIT_SCRIPT),
                "--plugin-root",
                str(PLUGIN_ROOT),
                "--output-root",
                str(self.output_root),
                "--project-id",
                "demo-site",
            ],
            check=True,
        )
        self.profile = self.output_root / "profiles" / "demo-site.project_profile.json"
        self.state = self.output_root / "states" / "demo-site.project_state.json"
        self.queue = self.output_root / "queues" / "demo-site.workflow_queue.json"

        profile_payload = json.loads(self.profile.read_text())
        profile_payload["workspace_root"] = str(self.workspace)
        profile_payload["codebase_path"] = str(self.workspace / "site")
        profile_payload["agent_runtime"]["executor"]["mode"] = "mock"
        self.profile.write_text(json.dumps(profile_payload, indent=2) + "\n")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_mock_loop_completes_first_task(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(WRAPPER),
                "loop",
                "--plugin-root",
                str(PLUGIN_ROOT),
                "--profile",
                str(self.profile),
                "--state",
                str(self.state),
                "--queue",
                str(self.queue),
                "--executor",
                "mock",
                "--max-steps",
                "1",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "completed")

        queue = json.loads(self.queue.read_text())
        self.assertEqual(queue[0]["status"], "completed")

        state = json.loads(self.state.read_text())
        self.assertEqual(state["runtime"]["last_run_status"], "completed")
        self.assertTrue((self.workspace / ".website-agent" / "demo-site" / "memory" / "journal.jsonl").exists())

    def test_manual_run_then_apply_response(self) -> None:
        profile_payload = json.loads(self.profile.read_text())
        profile_payload["agent_runtime"]["executor"]["mode"] = "manual"
        self.profile.write_text(json.dumps(profile_payload, indent=2) + "\n")

        run = subprocess.run(
            [
                "python3",
                str(WRAPPER),
                "run",
                "--plugin-root",
                str(PLUGIN_ROOT),
                "--profile",
                str(self.profile),
                "--state",
                str(self.state),
                "--queue",
                str(self.queue),
                "--executor",
                "manual",
                "--json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        run_payload = json.loads(run.stdout)
        self.assertEqual(run_payload["status"], "waiting_manual")

        rerun = subprocess.run(
            [
                "python3",
                str(WRAPPER),
                "run",
                "--plugin-root",
                str(PLUGIN_ROOT),
                "--profile",
                str(self.profile),
                "--state",
                str(self.state),
                "--queue",
                str(self.queue),
                "--executor",
                "manual",
                "--json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        rerun_payload = json.loads(rerun.stdout)
        self.assertEqual(rerun_payload["status"], "waiting_manual")
        self.assertEqual(rerun_payload["run_id"], run_payload["run_id"])

        response_file = Path(run_payload["response_path"])
        response_payload = {
            "task_id": "task-001",
            "status": "completed",
            "summary": "Manual response applied.",
            "notes": ["Recovered through apply command."],
            "blockers": [],
            "open_decisions": [],
            "next_actions": ["Continue to the next task."],
            "quality_gates": {},
            "queue_updates": [{"id": "task-001", "status": "completed"}],
            "artifacts": [],
        }
        response_file.write_text(json.dumps(response_payload, indent=2) + "\n")

        apply = subprocess.run(
            [
                "python3",
                str(WRAPPER),
                "apply",
                "--plugin-root",
                str(PLUGIN_ROOT),
                "--profile",
                str(self.profile),
                "--state",
                str(self.state),
                "--queue",
                str(self.queue),
                "--response-file",
                str(response_file),
                "--json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        apply_payload = json.loads(apply.stdout)
        self.assertEqual(apply_payload["status"], "completed")

        queue = json.loads(self.queue.read_text())
        self.assertEqual(queue[0]["status"], "completed")


if __name__ == "__main__":
    unittest.main()
