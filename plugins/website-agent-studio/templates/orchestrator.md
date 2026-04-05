# Website Agent Studio Orchestrator

## Input Contract

Every run should load:

1. a project profile
2. a project state
3. a workflow queue

## Control Loop

1. Read project state
2. Read queue
3. Confirm current phase
4. Choose the matching phase skill
5. Execute the phase skill
6. Update state and queue
7. Verify before advancing

## Phase Map

- `state-sync`
- `project-brief`
- `requirements-ia`
- `brand-assets`
- `frontend-build`
- `backend-integrations`
- `qa-release`
- `handoff-continuity`

