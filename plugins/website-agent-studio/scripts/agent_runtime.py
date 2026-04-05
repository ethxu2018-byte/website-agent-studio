#!/usr/bin/env python3
"""Wrapper entrypoint for Website Agent Studio runtime."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    plugin_root = Path(__file__).resolve().parents[1]
    runtime_root = plugin_root / "runtime"
    sys.path.insert(0, str(runtime_root))
    from website_agent_studio.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
