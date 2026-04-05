# Runtime Model

Website Agent Studio now includes a real runtime loop.

## Core Runtime Responsibilities

The runtime is responsible for:

- loading the project profile, project state, and workflow queue
- choosing the next task based on status, priority, phase order, and dependencies
- selecting the matching phase skill
- writing a run packet for the active task
- executing in one of three modes:
  - `manual`
  - `mock`
  - `shell`
- updating state, queue, journal, run records, and checkpoints
- resuming safely after interruption

## Execution Modes

### `manual`

The runtime writes a prompt file and waits for an external agent or human to produce a JSON response.

Use when:

- driving Claude Code manually
- testing a phase skill
- keeping a human approval step between runs

### `mock`

The runtime completes tasks with a built-in deterministic mock response. This is primarily for:

- smoke tests
- onboarding demos
- CI checks

### `shell`

The runtime shells out to an external command template. The executor can read the generated prompt file and either:

- write JSON to the designated response file
- or print strict JSON to stdout

Website Agent Studio also supports named shell presets through `agent_runtime.executor.preset`.

#### `codex-exec`

Tested on this repository. The runtime can shell out to `codex exec` with:

- structured JSON schema output
- prompt packet passed from the runtime
- response written back to the runtime response file

Example project profile fragment:

```json
{
  "agent_runtime": {
    "runtime_root": ".website-agent",
    "executor": {
      "mode": "shell",
      "preset": "codex-exec",
      "sandbox_mode": "workspace-write",
      "skip_git_repo_check": true
    }
  }
}
```

#### `claude-code`

Claude Code support is provided through a bridge wrapper. Because Claude Code installations vary, you supply a command template:

```json
{
  "agent_runtime": {
    "runtime_root": ".website-agent",
    "executor": {
      "mode": "shell",
      "preset": "claude-code",
      "command_template": "claude --print --output json --cd {project_root} < {prompt_file} > {response_file}"
    }
  }
}
```

Supported placeholders inside `command_template`:

- `{prompt_file}`
- `{response_file}`
- `{project_id}`
- `{task_id}`
- `{run_id}`
- `{timestamp}`
- `{project_root}`
- `{plugin_root}`

## Durable Memory

For each project, runtime files are written under:

- `.website-agent/<project-id>/memory`
- `.website-agent/<project-id>/runs`
- `.website-agent/<project-id>/prompts`
- `.website-agent/<project-id>/responses`
- `.website-agent/<project-id>/checkpoints`

This enables:

- restart after interruption
- prompt/response traceability
- checkpoint inspection
- decision persistence

## State Machine Rules

Task selection order:

1. existing `in_progress` task
2. highest-priority `open` task with satisfied dependencies
3. idle if no tasks qualify

Phase status is derived from queue reality:

- `completed` if all tasks in a phase are completed
- `blocked` if any task in the phase is blocked
- `in_progress` if any task in the phase is in progress
- `pending` otherwise

## Response Contract

The runtime expects strict JSON matching:

- `plugins/website-agent-studio/templates/agent_response.template.json`

That response drives:

- task completion or blocking
- queue updates
- quality gate updates
- artifacts
- notes and next actions
