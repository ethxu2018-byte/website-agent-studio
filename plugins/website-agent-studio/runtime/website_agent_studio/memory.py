"""Durable memory, run records, and checkpoints."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .storage import save_json, utc_now


def append_journal(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"timestamp": utc_now(), **event}
    with path.open("a") as handle:
        handle.write(json.dumps(payload) + "\n")


def write_run_record(path: Path, record: dict[str, Any]) -> None:
    save_json(path, record)


def update_run_record(path: Path, updates: dict[str, Any]) -> None:
    record = json.loads(path.read_text())
    record.update(updates)
    save_json(path, record)


def write_checkpoint(path: Path, state: dict[str, Any], queue: list[dict[str, Any]]) -> None:
    payload = {
        "timestamp": utc_now(),
        "state": deepcopy(state),
        "queue": deepcopy(queue),
    }
    save_json(path, payload)


def append_decision(path: Path, decision: dict[str, Any]) -> None:
    if path.exists():
        existing = json.loads(path.read_text())
    else:
        existing = []
    existing.append({"timestamp": utc_now(), **decision})
    save_json(path, existing)
