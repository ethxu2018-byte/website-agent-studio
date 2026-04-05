# Quickstart

## 1. Clone and install

```bash
git clone https://github.com/ethxu2018-byte/website-agent-studio.git
cd website-agent-studio
python3 -m pip install -e .
```

## 2. Initialize a project scaffold

```bash
python3 plugins/website-agent-studio/scripts/init_project.py \
  --plugin-root plugins/website-agent-studio \
  --output-root ./agent-data \
  --project-id demo-site
```

This creates:

- `agent-data/profiles/demo-site.project_profile.json`
- `agent-data/states/demo-site.project_state.json`
- `agent-data/queues/demo-site.workflow_queue.json`

## 3. Validate and inspect

```bash
website-agent validate-project \
  --profile agent-data/profiles/demo-site.project_profile.json \
  --state agent-data/states/demo-site.project_state.json \
  --queue agent-data/queues/demo-site.workflow_queue.json

website-agent status \
  --profile agent-data/profiles/demo-site.project_profile.json \
  --state agent-data/states/demo-site.project_state.json \
  --queue agent-data/queues/demo-site.workflow_queue.json \
  --json
```

## 4. Run the agent

### Safe demo mode

```bash
website-agent loop \
  --profile agent-data/profiles/demo-site.project_profile.json \
  --state agent-data/states/demo-site.project_state.json \
  --queue agent-data/queues/demo-site.workflow_queue.json \
  --executor mock \
  --max-steps 3
```

### Manual handoff mode

```bash
website-agent run \
  --profile agent-data/profiles/demo-site.project_profile.json \
  --state agent-data/states/demo-site.project_state.json \
  --queue agent-data/queues/demo-site.workflow_queue.json \
  --executor manual \
  --json
```

The runtime will write:

- a prompt packet under `.website-agent/<project-id>/prompts`
- a response target under `.website-agent/<project-id>/responses`
- checkpoints and journal entries under `.website-agent/<project-id>/memory`

## 5. Apply a manual response

Fill the generated response file using `plugins/website-agent-studio/templates/agent_response.template.json`, then:

```bash
website-agent apply \
  --profile agent-data/profiles/demo-site.project_profile.json \
  --state agent-data/states/demo-site.project_state.json \
  --queue agent-data/queues/demo-site.workflow_queue.json \
  --response-file .website-agent/demo-site/responses/<run-id>.json
```
