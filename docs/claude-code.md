# Using Website Agent Studio With Claude Code

Claude Code will not consume the Codex plugin manifest directly, but it can still use this repo effectively.

## Recommended Use

1. Point Claude Code at this repository.
2. Tell it to read:
   - plugin README
   - templates
   - relevant phase skills
3. Tell it which project it should operate on.

## Suggested Starter Instruction

```text
Use Website Agent Studio as the workflow contract for this website project. Start with state-sync, then select the correct next phase based on the project profile, project state, and workflow queue.
```

## Required Inputs

Claude Code should be given:

- a project profile
- a project state file
- a workflow queue
- the actual codebase path

## Typical Workflow

1. Read `state-sync`
2. Determine current phase
3. Read that phase skill
4. Operate on the real website project
5. Update the state and queue

