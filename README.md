# Website Agent Studio

Website Agent Studio is a portable plugin-style website workflow system for Codex and other coding agents.

It is designed to help an agent build or continue a website project through:

- product definition
- requirements and IA
- brand and asset alignment
- frontend implementation
- backend integrations
- QA and release
- handoff continuity

## Repo Layout

- marketplace metadata:
  - `.agents/plugins/marketplace.json`
- plugin:
  - `plugins/website-agent-studio`
- docs:
  - `docs`

## Plugin Path

- `plugins/website-agent-studio`

## What It Includes

- a Codex plugin manifest
- plugin marketplace metadata
- 8 reusable website phase skills
- project templates
- helper scripts
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

### Codex-style usage

Use the plugin folder inside a Codex plugin marketplace or local plugin directory.

### Claude Code or other agent usage

Use the templates, docs, and skill files as the workflow contract.

See:

- `docs/claude-code.md`

## Publishing

See:

- `docs/publishing.md`
- `docs/installing.md`
- `docs/repo-architecture.md`

## Examples

- `examples/arq-site`
- `examples/audio-brand-site`
