"""CLI entrypoint for Website Agent Studio runtime."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import apply_response_file, clear_blocker, load_engine_context, record_decision, run_cycle, status_payload
from .storage import ensure_profile, ensure_queue, ensure_state, load_json, save_json


def _default_plugin_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="website-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--plugin-root", default=str(_default_plugin_root()))
    common.add_argument("--profile", required=True)
    common.add_argument("--state", required=True)
    common.add_argument("--queue", required=True)

    init = subparsers.add_parser("validate-project", parents=[common])
    init = init  # quiet lint

    status = subparsers.add_parser("status", parents=[common])
    status.add_argument("--json", action="store_true")

    next_cmd = subparsers.add_parser("next", parents=[common])
    next_cmd.add_argument("--json", action="store_true")

    run = subparsers.add_parser("run", parents=[common])
    run.add_argument("--executor", choices=["manual", "mock", "shell"])
    run.add_argument("--json", action="store_true")

    loop = subparsers.add_parser("loop", parents=[common])
    loop.add_argument("--executor", choices=["manual", "mock", "shell"])
    loop.add_argument("--max-steps", type=int, default=5)

    apply_cmd = subparsers.add_parser("apply", parents=[common])
    apply_cmd.add_argument("--response-file", required=True)
    apply_cmd.add_argument("--json", action="store_true")

    decision = subparsers.add_parser("record-decision", parents=[common])
    decision.add_argument("--decision", required=True)
    decision.add_argument("--close-open", action="store_true")

    unblock = subparsers.add_parser("clear-blocker", parents=[common])
    unblock.add_argument("--blocker", required=True)

    return parser


def _paths_from_args(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    plugin_root = Path(args.plugin_root).expanduser().resolve()
    profile = Path(args.profile).expanduser().resolve()
    state = Path(args.state).expanduser().resolve()
    queue = Path(args.queue).expanduser().resolve()
    return plugin_root, profile, state, queue


def _emit(payload: dict, as_json: bool = False) -> int:
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    plugin_root, profile_path, state_path, queue_path = _paths_from_args(args)

    if args.command == "validate-project":
        profile = ensure_profile(load_json(profile_path))
        state = ensure_state(load_json(state_path), profile["project_id"])
        queue = ensure_queue(load_json(queue_path))
        save_json(profile_path, profile)
        save_json(state_path, state)
        save_json(queue_path, queue)
        print("Project files are valid and normalized.")
        return 0

    context = load_engine_context(plugin_root, profile_path, state_path, queue_path)

    if args.command == "status":
        return _emit(status_payload(context), args.json)

    if args.command == "next":
        payload = status_payload(context)
        return _emit({"next_task": payload.get("next_task"), "current_phase": payload.get("current_phase")}, args.json)

    if args.command == "run":
        return _emit(run_cycle(context, executor_override=args.executor), args.json)

    if args.command == "loop":
        last: dict[str, object] = {}
        for _ in range(max(args.max_steps, 1)):
            context = load_engine_context(plugin_root, profile_path, state_path, queue_path)
            result = run_cycle(context, executor_override=args.executor)
            last = result
            if result["status"] in {"idle", "blocked", "waiting_manual"}:
                break
        print(json.dumps(last, indent=2))
        return 0

    if args.command == "apply":
        result = apply_response_file(context, Path(args.response_file).expanduser().resolve())
        return _emit(result, args.json)

    if args.command == "record-decision":
        return _emit(record_decision(context, args.decision, close_open=args.close_open))

    if args.command == "clear-blocker":
        return _emit(clear_blocker(context, args.blocker))

    parser.error("Unknown command")
    return 2
