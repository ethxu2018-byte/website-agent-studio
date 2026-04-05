"""Executors for manual, mock, and shell-based agent runs."""

from __future__ import annotations

import json
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .registry import SkillDefinition
from .storage import utc_now


@dataclass
class ExecutionContext:
    project_profile: dict[str, Any]
    project_state: dict[str, Any]
    workflow_queue: list[dict[str, Any]]
    task: dict[str, Any]
    skill: SkillDefinition
    run_id: str
    prompt_path: Path
    response_path: Path


@dataclass
class ExecutionOutcome:
    kind: str
    response: dict[str, Any] | None = None
    stdout: str = ""
    stderr: str = ""
    prompt_path: Path | None = None
    response_path: Path | None = None


def build_prompt_bundle(context: ExecutionContext) -> str:
    reference_blocks = []
    for ref in context.skill.read_references:
        if ref.exists():
            reference_blocks.append(f"## Reference: {ref.name}\n\n{ref.read_text().strip()}\n")

    task_snapshot = json.dumps(context.task, indent=2)
    state_snapshot = json.dumps(
        {
            "current_phase": context.project_state.get("current_phase"),
            "blockers": context.project_state.get("blockers", []),
            "open_decisions": context.project_state.get("open_decisions", []),
            "next_actions": context.project_state.get("next_actions", []),
            "quality_gates": context.project_state.get("quality_gates", {}),
        },
        indent=2,
    )

    return "\n".join(
        [
            "# Website Agent Studio Run Packet",
            "",
            f"Run ID: {context.run_id}",
            f"Project: {context.project_profile['project_name']} ({context.project_profile['project_id']})",
            f"Phase: {context.skill.phase}",
            f"Skill: {context.skill.trigger_name}",
            "",
            "## Objective",
            "",
            context.task["title"],
            "",
            "## Project Profile",
            "",
            json.dumps(
                {
                    "project_type": context.project_profile.get("project_type"),
                    "category": context.project_profile.get("category"),
                    "primary_cta": context.project_profile.get("primary_cta"),
                    "business_goal": context.project_profile.get("business_goal"),
                    "brand_direction": context.project_profile.get("brand_direction", []),
                    "stack": context.project_profile.get("stack", []),
                    "workspace_root": context.project_profile.get("workspace_root"),
                    "codebase_path": context.project_profile.get("codebase_path"),
                },
                indent=2,
            ),
            "",
            "## Current State",
            "",
            state_snapshot,
            "",
            "## Active Task",
            "",
            task_snapshot,
            "",
            "## Skill Workflow",
            "",
            context.skill.body,
            "",
            "## Preferred Tools",
            "",
            json.dumps(context.skill.preferred_tools, indent=2),
            "",
            "## Verification Expectations",
            "",
            json.dumps(context.skill.verification, indent=2),
            "",
            *reference_blocks,
            "## Response Contract",
            "",
            "Return strict JSON only. Do not wrap it in markdown.",
            "",
            json.dumps(
                {
                    "task_id": context.task["id"],
                    "status": "completed",
                    "summary": "One short paragraph summarizing what changed or why it is blocked.",
                    "notes": [
                        "Short bullet-like notes as array strings."
                    ],
                    "blockers": [],
                    "open_decisions": [],
                    "next_actions": [],
                    "quality_gates": {
                        "lint": False,
                        "typecheck": False,
                        "test": False,
                        "build": False,
                        "browser-verification": False,
                    },
                    "queue_updates": [
                        {
                            "id": context.task["id"],
                            "status": "completed",
                        }
                    ],
                    "artifacts": [
                        {
                            "path": "path/to/file",
                            "description": "What this artifact is.",
                        }
                    ],
                },
                indent=2,
            ),
        ]
    ).strip() + "\n"


def parse_response(raw: str) -> dict[str, Any]:
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("Agent response must be a JSON object.")
    return payload


def validate_response(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = {
        "task_id": payload.get("task_id", task_id),
        "status": payload.get("status", "in_progress"),
        "summary": payload.get("summary", ""),
        "notes": payload.get("notes", []),
        "blockers": payload.get("blockers", []),
        "open_decisions": payload.get("open_decisions", []),
        "next_actions": payload.get("next_actions", []),
        "quality_gates": payload.get("quality_gates", {}),
        "queue_updates": payload.get("queue_updates", []),
        "artifacts": payload.get("artifacts", []),
    }
    if response["task_id"] != task_id:
        raise ValueError(f"Response task_id mismatch: expected {task_id}, got {response['task_id']}")
    if response["status"] not in {"completed", "blocked", "in_progress"}:
        raise ValueError(f"Unsupported response status: {response['status']}")
    return response


def execute_manual(context: ExecutionContext) -> ExecutionOutcome:
    bundle = build_prompt_bundle(context)
    context.prompt_path.write_text(bundle)
    return ExecutionOutcome(
        kind="manual_pending",
        prompt_path=context.prompt_path,
        response_path=context.response_path,
    )


def execute_mock(context: ExecutionContext) -> ExecutionOutcome:
    bundle = build_prompt_bundle(context)
    context.prompt_path.write_text(bundle)
    response = validate_response(
        context.task["id"],
        {
            "task_id": context.task["id"],
            "status": "completed",
            "summary": f"Mock executor completed task '{context.task['title']}' for phase {context.task['phase']}.",
            "notes": [
                "This was produced by the built-in mock executor.",
                f"Run packet generated at {context.prompt_path.name}.",
            ],
            "next_actions": [
                "Continue to the next queue item if one exists."
            ],
            "queue_updates": [
                {"id": context.task["id"], "status": "completed"}
            ],
            "artifacts": [
                {"path": str(context.prompt_path), "description": "Generated run packet used by the mock executor."}
            ],
        },
    )
    context.response_path.write_text(json.dumps(response, indent=2) + "\n")
    return ExecutionOutcome(
        kind="completed",
        response=response,
        prompt_path=context.prompt_path,
        response_path=context.response_path,
    )


def execute_shell(context: ExecutionContext, command_template: list[str] | str, response_mode: str) -> ExecutionOutcome:
    bundle = build_prompt_bundle(context)
    context.prompt_path.write_text(bundle)

    values = {
        "prompt_file": str(context.prompt_path),
        "response_file": str(context.response_path),
        "project_id": context.project_profile["project_id"],
        "task_id": context.task["id"],
        "run_id": context.run_id,
        "timestamp": utc_now(),
    }

    if isinstance(command_template, str):
        parts = shlex.split(command_template)
    else:
        parts = list(command_template)

    command = [part.format(**values) for part in parts]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Executor command failed ({result.returncode}): {result.stderr.strip()}")

    raw = ""
    if response_mode == "stdout":
        raw = result.stdout.strip()
    elif context.response_path.exists():
        raw = context.response_path.read_text().strip()
    else:
        raw = result.stdout.strip()

    response = validate_response(context.task["id"], parse_response(raw))
    if not context.response_path.exists():
        context.response_path.write_text(json.dumps(response, indent=2) + "\n")

    return ExecutionOutcome(
        kind="completed",
        response=response,
        stdout=result.stdout,
        stderr=result.stderr,
        prompt_path=context.prompt_path,
        response_path=context.response_path,
    )
