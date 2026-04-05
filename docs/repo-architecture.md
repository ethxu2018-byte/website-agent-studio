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

## Plugin Internals

### `.codex-plugin/plugin.json`

The main plugin manifest for Codex-style plugin consumption.

### `agents/openai.yaml`

UI-facing metadata for supported surfaces that read this interface file.

### `skills/`

The phased website workflow skills.

### `templates/`

Project scaffolds for:

- project profile
- project state
- workflow queue
- orchestrator

### `references/`

Support material that keeps `SKILL.md` concise while giving the plugin a shared workflow language.

### `scripts/`

Small deterministic helpers for:

- creating a project scaffold
- reading the next task
- updating task status
- validating the plugin structure

