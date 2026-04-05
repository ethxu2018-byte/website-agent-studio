# Using Website Agent Studio With Claude Code

Claude Code will not consume the Codex plugin manifest directly, but it can still use this repo effectively.

## Recommended Use

1. Point Claude Code at this repository.
2. Tell it to read:
   - plugin README
   - `docs/runtime.md`
   - templates
   - relevant phase skills
3. Tell it which project it should operate on.

## Suggested Starter Instruction

```text
Use Website Agent Studio as the workflow contract for this website project. Start with state-sync, then select the correct next phase based on the project profile, project state, and workflow queue.
```

If you want Claude Code to behave more like a runtime-driven agent, have it follow this sequence:

1. read the project profile, project state, and workflow queue
2. read the next phase skill
3. produce strict JSON matching `templates/agent_response.template.json`
4. let the runtime apply that response

## Required Inputs

Claude Code should be given:

- a project profile
- a project state file
- a workflow queue
- the actual codebase path

## Runtime-Assisted Flow

Website Agent Studio can prepare prompt packets and response files for Claude Code through `website-agent run --executor manual`.

Recommended loop:

1. runtime writes prompt packet
2. Claude Code executes the task
3. Claude Code writes strict JSON response
4. runtime applies the response and advances queue/state

## Claude Code Shell Adapter

If your Claude Code installation supports non-interactive command execution, configure:

```json
{
  "agent_runtime": {
    "executor": {
      "mode": "shell",
      "preset": "claude-code",
      "command_template": "claude --print --output json --cd {project_root} < {prompt_file} > {response_file}"
    }
  }
}
```

The wrapper script is:

- `plugins/website-agent-studio/scripts/run_claude_code.py`

This lets the runtime stay platform-agnostic while Claude Code remains replaceable.

## Typical Workflow

1. Read `state-sync`
2. Determine current phase
3. Read that phase skill
4. Operate on the real website project
5. Update the state and queue
