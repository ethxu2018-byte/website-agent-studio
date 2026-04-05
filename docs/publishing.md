# Publishing Notes

This repo is structured to be publishable to GitHub and usable as a Codex-compatible local marketplace plugin.

## Before Publishing

Update these fields in:

- `plugins/website-agent-studio/.codex-plugin/plugin.json`

Recommended updates:

- repository URL
- homepage URL
- author details
- screenshots if desired

## GitHub Publish Flow

1. Create a new repository on GitHub.
2. Initialize git in the repo root if needed.
3. Commit the repo.
4. Push to GitHub.
5. Update `plugin.json` repository and homepage fields.

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
