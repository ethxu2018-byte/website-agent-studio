# Installing Website Agent Studio

## As a Python CLI

1. Clone the repository.
2. Install editable mode:

```bash
python3 -m pip install -e .
```

3. Verify:

```bash
website-agent --help
```

4. Start with:

- `docs/quickstart.md`
- `docs/runtime.md`

## As a Local Codex Plugin

1. Clone or copy this repository onto the target machine.
2. Point the local Codex marketplace to:

- `/path/to/website-agent-studio/.agents/plugins/marketplace.json`

3. Install the plugin entry:

- `website-agent-studio`

4. Use the plugin skills from:

- `/path/to/website-agent-studio/plugins/website-agent-studio/skills`

## As a Portable Workflow Repo

If the target platform does not support Codex plugins directly:

1. clone the repository
2. read the plugin README
3. use the templates and skills as the workflow contract

Key paths:

- templates:
  - `plugins/website-agent-studio/templates`
- skills:
  - `plugins/website-agent-studio/skills`
- scripts:
  - `plugins/website-agent-studio/scripts`
- runtime:
  - `plugins/website-agent-studio/runtime/website_agent_studio`
- docs:
  - `docs`

## For Claude Code

See:

- `docs/claude-code.md`
- `docs/quickstart.md`
