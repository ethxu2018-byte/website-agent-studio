# Repo Architecture

## Purpose

This repository is organized as a portable agent product, not just a local notes folder.

## Top Level

- `.agents/plugins/marketplace.json`
  - local marketplace metadata
- `plugins/website-agent-studio`
  - actual plugin payload
- `docs`
  - installation and publishing notes
- `examples`
  - reusable example project states
- `tests`
  - runtime smoke tests
- `pyproject.toml`
  - Python CLI packaging entrypoint

## Plugin Internals

### `.codex-plugin/plugin.json`

The main plugin manifest for Codex-style plugin consumption.

### `agents/openai.yaml`

UI-facing metadata for supported surfaces that read this interface file.

### `skills/`

The phased website workflow skills.

### `runtime/website_agent_studio`

The actual agent runtime package:

- CLI
- state loading and normalization
- skill registry
- task selection
- execution adapters
- memory and checkpoint persistence

### `templates/`

Project scaffolds for:

- project profile
- project state
- workflow queue
- orchestrator
- agent response contract

### `references/`

Support material that keeps `SKILL.md` concise while giving the plugin a shared workflow language.

### `scripts/`

Small deterministic helpers for:

- creating a project scaffold
- reading the next task
- updating task status
- running the runtime wrapper
- validating the plugin structure
