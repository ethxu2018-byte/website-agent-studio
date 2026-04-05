"""Resolve runtime paths for a project."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    plugin_root: Path
    workspace_root: Path
    codebase_path: Path
    runtime_root: Path
    memory_dir: Path
    runs_dir: Path
    prompts_dir: Path
    responses_dir: Path
    checkpoints_dir: Path
    decisions_path: Path
    journal_path: Path


def resolve_runtime_paths(profile: dict, plugin_root: Path, fallback_root: Path | None = None) -> RuntimePaths:
    fallback = fallback_root.resolve() if fallback_root else plugin_root.resolve()

    workspace_candidate = Path(profile["workspace_root"]).expanduser()
    if not workspace_candidate.is_absolute():
        workspace_candidate = (fallback / workspace_candidate).resolve()
    elif workspace_candidate.exists():
        workspace_candidate = workspace_candidate.resolve()

    workspace_root = workspace_candidate if workspace_candidate.exists() else fallback

    codebase_candidate = Path(profile["codebase_path"]).expanduser()
    if not codebase_candidate.is_absolute():
        codebase_candidate = (workspace_root / codebase_candidate).resolve()
    elif codebase_candidate.exists():
        codebase_candidate = codebase_candidate.resolve()

    codebase_path = codebase_candidate
    runtime_config = profile.get("agent_runtime", {})
    runtime_root_raw = runtime_config.get("runtime_root", ".website-agent")
    runtime_root = Path(runtime_root_raw)
    if not runtime_root.is_absolute():
        runtime_root = (workspace_root / runtime_root / profile["project_id"]).resolve()

    memory_dir = runtime_root / "memory"
    runs_dir = runtime_root / "runs"
    prompts_dir = runtime_root / "prompts"
    responses_dir = runtime_root / "responses"
    checkpoints_dir = runtime_root / "checkpoints"

    for directory in [runtime_root, memory_dir, runs_dir, prompts_dir, responses_dir, checkpoints_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    return RuntimePaths(
        plugin_root=plugin_root,
        workspace_root=workspace_root,
        codebase_path=codebase_path,
        runtime_root=runtime_root,
        memory_dir=memory_dir,
        runs_dir=runs_dir,
        prompts_dir=prompts_dir,
        responses_dir=responses_dir,
        checkpoints_dir=checkpoints_dir,
        decisions_path=memory_dir / "decisions.json",
        journal_path=memory_dir / "journal.jsonl",
    )


def common_fallback_root(*paths: Path) -> Path:
    parent_dirs = [str(path.parent.resolve()) for path in paths]
    return Path(os.path.commonpath(parent_dirs))
