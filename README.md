# Website Agent Studio

Website Agent Studio is a portable plugin-style website workflow agent system for Codex, Claude Code, and other coding agents.

It is designed to help an agent build or continue a website project through:

- product definition
- requirements and IA
- brand and asset alignment
- frontend implementation
- backend integrations
- QA and release
- handoff continuity

It now includes a real runtime loop that can:

- read project profile, state, and queue
- decide the next task automatically
- select the correct phase skill
- update state and queue after each run
- persist memory, checkpoints, and run records
- work in manual, mock, or shell-executor mode

Shell executor presets currently include:

- `codex-exec` for structured `codex exec` runs
- `claude-code` as a configurable bridge wrapper

## Repo Layout

- marketplace metadata:
  - `.agents/plugins/marketplace.json`
- plugin:
- `plugins/website-agent-studio`
- docs:
  - `docs`
- tests:
  - `tests`

## Plugin Path

- `plugins/website-agent-studio`

## What It Includes

- a Codex plugin manifest
- plugin marketplace metadata
- 8 reusable website phase skills
- project templates
- helper scripts
- runtime package and CLI
- shared references
- example project states
- publishing notes
- Claude Code usage notes

## Main Skills

- `state-sync`
- `project-brief`
- `requirements-ia`
- `brand-assets`
- `frontend-build`
- `backend-integrations`
- `qa-release`
- `handoff-continuity`

## Installation Concepts

### Python CLI usage

```bash
python3 -m pip install -e .
website-agent --help
```

### Codex-style usage

Use the plugin folder inside a Codex plugin marketplace or local plugin directory.

### Claude Code or other agent usage

Use the templates, docs, and skill files as the workflow contract.

See:

- `docs/claude-code.md`
- `docs/quickstart.md`
- `docs/runtime.md`

## Publishing

See:

- `docs/publishing.md`
- `docs/installing.md`
- `docs/repo-architecture.md`
- `docs/runtime.md`

## Examples

- `examples/arq-site`
- `examples/audio-brand-site`
