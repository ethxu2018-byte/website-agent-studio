---
name: website-agent-studio-state-sync
description: Use when starting, resuming, or auditing a website project run and you need to align the project profile, project state, workflow queue, and workspace reality before choosing the next website phase skill.
---

# Website Agent Studio State Sync

Use this skill at the start of any website-agent run.

## Read

- the active project profile
- the active project state
- the active workflow queue
- `../../templates/orchestrator.md`
- `../../references/phase-model.md`
- `../../references/state-files.md`

## Workflow

1. Confirm the project identity and paths.
2. Confirm the active codebase exists.
3. Confirm whether the recorded phase still matches reality.
4. Update blockers, next actions, and quality gates.
5. Select the next phase skill.

## Completion Criteria

- the current phase is accurate
- blockers are explicit
- the next skill is clear
