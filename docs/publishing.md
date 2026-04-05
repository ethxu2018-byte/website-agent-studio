# Publishing Notes

This repo is structured to be publishable to GitHub, installable as a Python CLI, and usable as a Codex-compatible local marketplace plugin.

## Before Publishing

Update these fields in:

- `plugins/website-agent-studio/.codex-plugin/plugin.json`

Recommended updates:

- repository URL
- homepage URL
- author details
- screenshots if desired

## GitHub Publish Flow

1. Validate the plugin structure.
2. Run runtime tests.
3. Commit the repo.
4. Push to GitHub.
5. Tag a release.
6. Update `plugin.json` screenshots if desired.

Suggested pre-release checks:

```bash
python3 plugins/website-agent-studio/scripts/validate_plugin.py \
  --plugin-root plugins/website-agent-studio

python3 -m unittest discover -s tests
```

## Marketplace-Oriented Structure

This repo already includes:

- `.agents/plugins/marketplace.json`
- `plugins/website-agent-studio/.codex-plugin/plugin.json`

That means it is already organized like a plugin collection repo with a single plugin entry.

## Other Platforms

For agents that do not support Codex plugin manifests directly, use:

- the skills as workflow instructions
- the templates as project state scaffolds
- the docs as the operational contract

See:

- `docs/claude-code.md`
- `docs/runtime.md`
- `docs/quickstart.md`
