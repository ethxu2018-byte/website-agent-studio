"""Discover skills and references from the plugin."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .constants import PHASE_ORDER, SKILL_HINTS


@dataclass
class SkillDefinition:
    phase: str
    trigger_name: str
    description: str
    skill_path: Path
    body: str
    read_references: list[Path]
    preferred_tools: list[str]
    verification: list[str]


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
REFERENCE_RE = re.compile(r"`([^`]+)`")


def parse_skill(skill_path: Path) -> SkillDefinition:
    content = skill_path.read_text()
    match = FRONTMATTER_RE.match(content)
    if not match:
        raise ValueError(f"Skill file missing frontmatter: {skill_path}")

    frontmatter_raw, body = match.groups()
    metadata: dict[str, str] = {}
    for line in frontmatter_raw.splitlines():
        field = FIELD_RE.match(line.strip())
        if field:
            metadata[field.group(1)] = field.group(2)

    phase = skill_path.parent.name
    references: list[Path] = []
    for raw_ref in REFERENCE_RE.findall(body):
        if raw_ref.startswith("../../"):
            references.append((skill_path.parent / raw_ref).resolve())

    hints = SKILL_HINTS.get(phase, {})
    return SkillDefinition(
        phase=phase,
        trigger_name=metadata.get("name", phase),
        description=metadata.get("description", ""),
        skill_path=skill_path,
        body=body.strip(),
        read_references=references,
        preferred_tools=hints.get("preferred_tools", []),
        verification=hints.get("verification", []),
    )


def load_skill_registry(plugin_root: Path) -> dict[str, SkillDefinition]:
    registry: dict[str, SkillDefinition] = {}
    for phase in PHASE_ORDER:
        skill_path = plugin_root / "skills" / phase / "SKILL.md"
        registry[phase] = parse_skill(skill_path)
    return registry
