"""Shared constants for Website Agent Studio runtime."""

from __future__ import annotations

PHASE_ORDER = [
    "state-sync",
    "project-brief",
    "requirements-ia",
    "brand-assets",
    "frontend-build",
    "backend-integrations",
    "qa-release",
    "handoff-continuity",
]

PRIORITY_ORDER = {
    "P0": 0,
    "P1": 1,
    "P2": 2,
    "P3": 3,
}

SKILL_HINTS = {
    "state-sync": {
        "preferred_tools": ["filesystem", "json", "shell"],
        "verification": ["state consistency", "path validation"],
    },
    "project-brief": {
        "preferred_tools": ["markdown", "research notes"],
        "verification": ["CTA clarity", "audience clarity"],
    },
    "requirements-ia": {
        "preferred_tools": ["markdown", "csv", "sitemap"],
        "verification": ["route coverage", "flow coverage"],
    },
    "brand-assets": {
        "preferred_tools": ["design tokens", "asset matrix", "copy review"],
        "verification": ["visual consistency", "asset mapping"],
    },
    "frontend-build": {
        "preferred_tools": ["code editor", "browser", "lint", "build"],
        "verification": ["responsive UI", "metadata", "interactions"],
    },
    "backend-integrations": {
        "preferred_tools": ["env", "API routes", "service layer", "logs"],
        "verification": ["runtime behavior", "fallback behavior"],
    },
    "qa-release": {
        "preferred_tools": ["lint", "typecheck", "tests", "browser"],
        "verification": ["release gates", "browser verification", "health checks"],
    },
    "handoff-continuity": {
        "preferred_tools": ["markdown", "checklists", "release notes"],
        "verification": ["continuity packet completeness"],
    },
}

VALID_TASK_STATUSES = {"open", "in_progress", "completed", "blocked"}
VALID_PHASE_STATUSES = {"pending", "in_progress", "completed", "blocked"}
VALID_EXECUTOR_MODES = {"manual", "mock", "shell"}
