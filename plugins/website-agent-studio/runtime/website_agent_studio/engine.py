"""Core runtime engine for Website Agent Studio."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constants import PHASE_ORDER, PRIORITY_ORDER
from .executor import ExecutionContext, ExecutionOutcome, execute_manual, execute_mock, execute_shell, resolve_executor, validate_response
from .memory import append_decision, append_journal, update_run_record, write_checkpoint, write_run_record
from .paths import RuntimePaths, common_fallback_root, resolve_runtime_paths
from .registry import SkillDefinition, load_skill_registry
from .storage import ensure_profile, ensure_queue, ensure_state, load_project_files, save_json, utc_now


@dataclass
class EngineContext:
    plugin_root: Path
    profile_path: Path
    state_path: Path
    queue_path: Path
    profile: dict[str, Any]
    state: dict[str, Any]
    queue: list[dict[str, Any]]
    paths: RuntimePaths
    skill_registry: dict[str, SkillDefinition]


def load_engine_context(plugin_root: Path, profile_path: Path, state_path: Path, queue_path: Path) -> EngineContext:
    profile, state, queue = load_project_files(profile_path, state_path, queue_path)
    paths = resolve_runtime_paths(profile, plugin_root, fallback_root=common_fallback_root(profile_path, state_path, queue_path))
    registry = load_skill_registry(plugin_root)
    return EngineContext(
        plugin_root=plugin_root,
        profile_path=profile_path,
        state_path=state_path,
        queue_path=queue_path,
        profile=profile,
        state=state,
        queue=queue,
        paths=paths,
        skill_registry=registry,
    )


def save_context(context: EngineContext) -> None:
    save_json(context.profile_path, context.profile)
    save_json(context.state_path, context.state)
    save_json(context.queue_path, context.queue)


def dependency_satisfied(queue: list[dict[str, Any]], task: dict[str, Any]) -> bool:
    completed = {item["id"] for item in queue if item["status"] == "completed"}
    return all(dep in completed for dep in task.get("depends_on", []))


def sort_key(task: dict[str, Any]) -> tuple[int, int, str]:
    return (
        PRIORITY_ORDER.get(task.get("priority", "P3"), 9),
        PHASE_ORDER.index(task.get("phase")) if task.get("phase") in PHASE_ORDER else 99,
        task.get("id", ""),
    )


def pick_next_task(queue: list[dict[str, Any]]) -> dict[str, Any] | None:
    in_progress = [task for task in queue if task["status"] == "in_progress"]
    if in_progress:
        in_progress.sort(key=sort_key)
        return in_progress[0]

    candidates = [task for task in queue if task["status"] == "open" and dependency_satisfied(queue, task)]
    if not candidates:
        return None
    candidates.sort(key=sort_key)
    return candidates[0]


def update_phase_statuses(context: EngineContext) -> None:
    grouped: dict[str, list[dict[str, Any]]] = {phase: [] for phase in PHASE_ORDER}
    for task in context.queue:
        phase = task.get("phase")
        if phase in grouped:
            grouped[phase].append(task)

    for phase in PHASE_ORDER:
        tasks = grouped[phase]
        if not tasks:
            continue
        statuses = {task["status"] for task in tasks}
        if statuses == {"completed"}:
            context.state["phase_status"][phase] = "completed"
        elif "blocked" in statuses:
            context.state["phase_status"][phase] = "blocked"
        elif "in_progress" in statuses:
            context.state["phase_status"][phase] = "in_progress"
        elif "open" in statuses:
            if context.state["phase_status"].get(phase) == "completed":
                continue
            context.state["phase_status"][phase] = "pending"


def ensure_runtime_summary(context: EngineContext) -> None:
    next_task = pick_next_task(context.queue)
    next_actions = context.state.get("next_actions", [])
    if next_task and (not next_actions or next_actions[0] != next_task["title"]):
        context.state["next_actions"] = [next_task["title"]]


def status_payload(context: EngineContext) -> dict[str, Any]:
    next_task = pick_next_task(context.queue)
    return {
        "project_id": context.profile["project_id"],
        "project_name": context.profile["project_name"],
        "current_phase": context.state.get("current_phase"),
        "active_skill": context.state.get("active_skill"),
        "active_run_id": context.state.get("runtime", {}).get("active_run_id", ""),
        "resume_required": context.state.get("runtime", {}).get("resume_required", False),
        "next_task": next_task,
        "blockers": context.state.get("blockers", []),
        "open_decisions": context.state.get("open_decisions", []),
        "quality_gates": context.state.get("quality_gates", {}),
        "runtime_root": str(context.paths.runtime_root),
    }


def _new_run_id(task_id: str) -> str:
    stamp = utc_now().replace(":", "").replace("-", "")
    return f"{stamp}-{task_id}"


def _active_run_path(paths: RuntimePaths, run_id: str) -> Path:
    return paths.runs_dir / f"{run_id}.json"


def _start_task(context: EngineContext, task: dict[str, Any]) -> tuple[str, Path, Path]:
    run_id = _new_run_id(task["id"])
    prompt_path = context.paths.prompts_dir / f"{run_id}.md"
    response_path = context.paths.responses_dir / f"{run_id}.json"

    if task["status"] == "open":
        task["status"] = "in_progress"
        task["attempts"] = int(task.get("attempts", 0)) + 1
        task["history"].append(
            {
                "timestamp": utc_now(),
                "event": "started",
                "run_id": run_id,
            }
        )

    context.state["current_phase"] = task["phase"]
    context.state["active_skill"] = task.get("owner_skill") or task["phase"]
    context.state["phase_status"][task["phase"]] = "in_progress"
    context.state["runtime"]["active_run_id"] = run_id
    context.state["runtime"]["active_task_id"] = task["id"]
    context.state["runtime"]["active_prompt_path"] = str(prompt_path)
    context.state["runtime"]["active_response_path"] = str(response_path)
    context.state["runtime"]["resume_required"] = True

    record = {
        "run_id": run_id,
        "task_id": task["id"],
        "phase": task["phase"],
        "started_at": utc_now(),
        "status": "started",
        "prompt_path": str(prompt_path),
        "response_path": str(response_path),
    }
    write_run_record(_active_run_path(context.paths, run_id), record)
    append_journal(
        context.paths.journal_path,
        {
            "event": "run_started",
            "run_id": run_id,
            "task_id": task["id"],
            "phase": task["phase"],
        },
    )
    write_checkpoint(context.paths.checkpoints_dir / "latest.json", context.state, context.queue)
    context.state["runtime"]["last_checkpoint_path"] = str(context.paths.checkpoints_dir / "latest.json")
    context.state["runtime"]["last_journal_path"] = str(context.paths.journal_path)
    save_context(context)
    return run_id, prompt_path, response_path


def _apply_response(context: EngineContext, task: dict[str, Any], run_id: str, response: dict[str, Any]) -> None:
    task["summary"] = response.get("summary", "")
    task["artifacts"] = response.get("artifacts", [])
    task["history"].append(
        {
            "timestamp": utc_now(),
            "event": response["status"],
            "run_id": run_id,
            "summary": response.get("summary", ""),
        }
    )
    task["status"] = "completed" if response["status"] == "completed" else response["status"]
    if task["status"] == "blocked":
        task["blocked_reason"] = "; ".join(response.get("blockers", []))
    else:
        task["blocked_reason"] = ""

    for update in response.get("queue_updates", []):
        target = next((item for item in context.queue if item["id"] == update.get("id")), None)
        if target:
            target["status"] = update.get("status", target["status"])

    context.state["blockers"] = response.get("blockers", [])
    context.state["open_decisions"] = response.get("open_decisions", [])
    context.state["next_actions"] = response.get("next_actions", [])
    context.state["notes"] = response.get("summary", context.state.get("notes", ""))
    context.state["runtime"]["last_run_id"] = run_id
    context.state["runtime"]["last_run_status"] = response["status"]
    context.state["runtime"]["memory_summary"] = response.get("summary", "")

    if response["status"] == "blocked":
        context.state["runtime"]["consecutive_failures"] = int(context.state["runtime"].get("consecutive_failures", 0)) + 1
    else:
        context.state["runtime"]["consecutive_failures"] = 0

    context.state["runtime"]["active_run_id"] = ""
    context.state["runtime"]["active_task_id"] = ""
    context.state["runtime"]["active_prompt_path"] = ""
    context.state["runtime"]["active_response_path"] = ""
    context.state["runtime"]["resume_required"] = False

    for key, value in response.get("quality_gates", {}).items():
        context.state["quality_gates"][key] = bool(value)

    update_phase_statuses(context)
    if task["status"] == "completed":
        context.state["last_completed_phase"] = task["phase"]

    next_task = pick_next_task(context.queue)
    if next_task:
        context.state["current_phase"] = next_task["phase"]
        context.state["active_skill"] = next_task.get("owner_skill") or next_task["phase"]

    append_journal(
        context.paths.journal_path,
        {
            "event": "run_finished",
            "run_id": run_id,
            "task_id": task["id"],
            "status": response["status"],
            "summary": response.get("summary", ""),
        },
    )
    update_run_record(
        _active_run_path(context.paths, run_id),
        {
            "completed_at": utc_now(),
            "status": response["status"],
            "summary": response.get("summary", ""),
            "artifacts": response.get("artifacts", []),
        },
    )
    write_checkpoint(context.paths.checkpoints_dir / "latest.json", context.state, context.queue)
    context.state["runtime"]["last_checkpoint_path"] = str(context.paths.checkpoints_dir / "latest.json")
    ensure_runtime_summary(context)
    save_context(context)


def run_cycle(context: EngineContext, executor_override: str | None = None) -> dict[str, Any]:
    runtime = context.state.get("runtime", {})
    active_run_id = runtime.get("active_run_id", "")
    active_task_id = runtime.get("active_task_id", "")
    active_response_path = runtime.get("active_response_path", "")
    if active_run_id and active_task_id and runtime.get("resume_required"):
        response_candidate = Path(active_response_path) if active_response_path else None
        if response_candidate and response_candidate.exists() and response_candidate.read_text().strip():
            return apply_response_file(context, response_candidate)
        return {
            "status": "waiting_manual",
            "run_id": active_run_id,
            "task_id": active_task_id,
            "prompt_path": runtime.get("active_prompt_path", ""),
            "response_path": active_response_path,
            "message": "Active run is waiting for a response. Apply the response file or clear the run before starting a new one.",
        }

    task = pick_next_task(context.queue)
    if task is None:
        context.state["next_actions"] = []
        update_phase_statuses(context)
        save_context(context)
        return {"status": "idle", "message": "No open tasks remain."}

    run_id, prompt_path, response_path = _start_task(context, task)
    skill = context.skill_registry[task["phase"]]
    exec_context = ExecutionContext(
        plugin_root=context.plugin_root,
        project_profile=context.profile,
        project_state=context.state,
        workflow_queue=context.queue,
        task=task,
        skill=skill,
        run_id=run_id,
        prompt_path=prompt_path,
        response_path=response_path,
    )

    executor_config = context.profile.get("agent_runtime", {}).get("executor", {})
    mode = executor_override or executor_config.get("mode", "manual")

    if mode == "manual":
        outcome = execute_manual(exec_context)
        update_run_record(
            _active_run_path(context.paths, run_id),
            {"status": "waiting_manual"},
        )
        append_journal(
            context.paths.journal_path,
            {
                "event": "waiting_manual",
                "run_id": run_id,
                "task_id": task["id"],
                "prompt_path": str(prompt_path),
                "response_path": str(response_path),
            },
        )
        save_context(context)
        return {
            "status": "waiting_manual",
            "run_id": run_id,
            "task_id": task["id"],
            "prompt_path": str(outcome.prompt_path),
            "response_path": str(outcome.response_path),
        }

    if mode == "mock":
        outcome = execute_mock(exec_context)
    else:
        command_template, response_mode = resolve_executor(
            executor_config.get("command_template", []),
            executor_config.get("response_mode", "file"),
            executor_config,
            exec_context,
        )
        outcome = execute_shell(
            exec_context,
            command_template,
            response_mode,
        )

    _apply_response(context, task, run_id, outcome.response or {})
    return {
        "status": outcome.response["status"] if outcome.response else "unknown",
        "run_id": run_id,
        "task_id": task["id"],
        "summary": outcome.response["summary"] if outcome.response else "",
    }


def apply_response_file(context: EngineContext, response_file: Path) -> dict[str, Any]:
    runtime = context.state.get("runtime", {})
    run_id = runtime.get("active_run_id", "")
    task_id = runtime.get("active_task_id", "")
    if not run_id or not task_id:
        raise RuntimeError("No active manual run to apply.")

    task = next((item for item in context.queue if item["id"] == task_id), None)
    if task is None:
        raise RuntimeError(f"Active task not found: {task_id}")

    payload = validate_response(task_id, json.loads(response_file.read_text()))
    _apply_response(context, task, run_id, payload)
    return {
        "status": payload["status"],
        "run_id": run_id,
        "task_id": task_id,
        "summary": payload["summary"],
    }


def record_decision(context: EngineContext, decision: str, close_open: bool = False) -> dict[str, Any]:
    append_decision(
        context.paths.decisions_path,
        {
            "project_id": context.profile["project_id"],
            "decision": decision,
        },
    )
    append_journal(
        context.paths.journal_path,
        {
            "event": "decision_recorded",
            "project_id": context.profile["project_id"],
            "decision": decision,
        },
    )
    if close_open and context.state.get("open_decisions"):
        context.state["open_decisions"] = context.state["open_decisions"][1:]
    context.state["notes"] = decision
    save_context(context)
    return {"status": "recorded", "decision": decision}


def clear_blocker(context: EngineContext, blocker: str) -> dict[str, Any]:
    context.state["blockers"] = [item for item in context.state.get("blockers", []) if item != blocker]
    append_journal(
        context.paths.journal_path,
        {
            "event": "blocker_cleared",
            "project_id": context.profile["project_id"],
            "blocker": blocker,
        },
    )
    save_context(context)
    return {"status": "cleared", "blockers": context.state["blockers"]}
