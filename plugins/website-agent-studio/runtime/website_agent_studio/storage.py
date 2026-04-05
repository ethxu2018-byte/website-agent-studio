"""Load, normalize, validate, and persist project files."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .constants import PHASE_ORDER, PRIORITY_ORDER, VALID_EXECUTOR_MODES, VALID_PHASE_STATUSES, VALID_TASK_STATUSES


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def ensure_profile(profile: dict[str, Any]) -> dict[str, Any]:
    required = ["project_id", "project_name", "workspace_root", "codebase_path"]
    for key in required:
        if not profile.get(key):
            raise ValueError(f"Missing required profile field: {key}")

    normalized = deepcopy(profile)
    runtime = normalized.setdefault("agent_runtime", {})
    runtime.setdefault("runtime_root", ".website-agent")
    runtime.setdefault(
        "executor",
        {
            "mode": "manual",
            "command_template": [],
            "response_mode": "file",
        },
    )
    executor = runtime["executor"]
    mode = executor.get("mode", "manual")
    if mode not in VALID_EXECUTOR_MODES:
        raise ValueError(f"Unsupported executor mode: {mode}")

    if "quality_gates" not in normalized:
        normalized["quality_gates"] = ["lint", "typecheck", "test", "build", "browser-verification"]

    return normalized


def ensure_state(state: dict[str, Any], project_id: str) -> dict[str, Any]:
    normalized = deepcopy(state)
    normalized.setdefault("project_id", project_id)
    normalized.setdefault("current_phase", PHASE_ORDER[0])
    normalized.setdefault("active_skill", normalized["current_phase"])
    normalized.setdefault("last_completed_phase", "")
    normalized.setdefault("blockers", [])
    normalized.setdefault("open_decisions", [])
    normalized.setdefault("next_actions", [])
    normalized.setdefault("notes", "Update after each meaningful phase action.")
    normalized.setdefault("quality_gates", {})
    normalized.setdefault("links", {"production": "", "health": ""})
    phase_status = normalized.setdefault("phase_status", {})
    for phase in PHASE_ORDER:
        if phase == normalized["current_phase"]:
            phase_status.setdefault(phase, "in_progress")
        else:
            phase_status.setdefault(phase, "pending")
        if phase_status[phase] not in VALID_PHASE_STATUSES:
            raise ValueError(f"Invalid phase status for {phase}: {phase_status[phase]}")

    runtime = normalized.setdefault("runtime", {})
    runtime.setdefault("active_run_id", "")
    runtime.setdefault("active_task_id", "")
    runtime.setdefault("active_prompt_path", "")
    runtime.setdefault("active_response_path", "")
    runtime.setdefault("last_run_id", "")
    runtime.setdefault("last_run_status", "")
    runtime.setdefault("resume_required", False)
    runtime.setdefault("consecutive_failures", 0)
    runtime.setdefault("last_checkpoint_path", "")
    runtime.setdefault("last_journal_path", "")
    runtime.setdefault("memory_summary", "")

    return normalized


def ensure_queue(queue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(queue):
        task = deepcopy(item)
        task.setdefault("id", f"task-{index + 1:03d}")
        task.setdefault("title", task["id"])
        task.setdefault("phase", "")
        task.setdefault("owner_skill", task.get("phase", ""))
        task.setdefault("priority", "P2")
        task.setdefault("status", "open")
        task.setdefault("depends_on", [])
        task.setdefault("attempts", 0)
        task.setdefault("blocked_reason", "")
        task.setdefault("summary", "")
        task.setdefault("artifacts", [])
        task.setdefault("history", [])
        if task["status"] not in VALID_TASK_STATUSES:
            raise ValueError(f"Invalid task status for {task['id']}: {task['status']}")
        normalized.append(task)

    normalized.sort(key=lambda item: (PRIORITY_ORDER.get(item["priority"], 9), item["id"]))
    return normalized


def load_project_files(profile_path: Path, state_path: Path, queue_path: Path) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    profile = ensure_profile(load_json(profile_path))
    state = ensure_state(load_json(state_path), profile["project_id"])
    queue = ensure_queue(load_json(queue_path))
    return profile, state, queue
