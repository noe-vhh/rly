# rly — Project brief

## What is rly?

A **command memory + workflow orchestrator** — a terminal companion, not a terminal replacement. Think "Grafana for scripts": a visibility and accessibility layer that sits alongside your terminal.

### Core concept

Everything is an "action" at different scales:
- **Command** — single line, quick (e.g. `kubectl rollout restart ...`)
- **Script** — multi-step, parameterised (e.g. `cost_report.py --month 04`)
- **Workflow** — chained actions (e.g. wipe → init → wait)

Same data model, same UI, same search. Complexity scales with the user.

### Positioning

- NOT a terminal replacement — a companion you use alongside your terminal
- Like a flight checklist on a pilot's kneeboard: the pilot still flies the plane
- The CLI purist answer: config-as-code (JSON manifest), shows exact commands run, doesn't hide the terminal, positioned as a team/onboarding tool
- Target user: mid-level DevOps/SRE with 20-50 commands/scripts accumulated across bash history, sticky notes, Notion pages, and hacked terminal configs

---

## Research tree (roadmap)

### Tier 1 — Command library (weeks 1-3)
- Add commands via UI
- Tag and categorise them
- Search and filter
- Click to copy or run
- Import from existing configs (e.g. Windows Terminal JSON)
- **This alone is useful on day one**

### Tier 2 — Parameters + history (weeks 4-6)
- Parameter input fields mapped to script arguments
- Run history with timestamps and exit codes
- Show exact command executed

### Tier 3 — Workflows (weeks 7-10)
- Chain actions together (if A succeeds, run B)
- Pass outputs between steps
- Scheduling (run every Monday)
- Export/import action collections

### Tier 4 — Team + sharing (future)
- Multi-user / team features
- Remote execution
- Plugin system or marketplace
- **This is where it becomes a product**

---

## Tech stack

All Python, minimal new language learning.

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | FastAPI | Python, modern, auto-generated API docs |
| Frontend | HTML + CSS + HTMX | No React/framework needed. HTMX adds interactivity via HTML attributes |
| Desktop wrapper | PyWebView | Wraps the web UI in a native OS window |
| Templating | Jinja2 | Renders HTML server-side, used by FastAPI |
| Data | JSON file | No database for Tier 1-2. Script manifest is a JSON file |
| Server | Uvicorn | ASGI server that runs FastAPI |

### Architecture

```
┌─────────────────────────────────┐
│  PyWebView (native window)      │
│  ┌───────────────────────────┐  │
│  │  HTML + CSS + HTMX        │  │
│  │  (your UI)                │  │
│  └──────────┬────────────────┘  │
│             │ HTTP calls         │
│  ┌──────────▼────────────────┐  │
│  │  FastAPI (Python)         │  │
│  │  - serves the UI          │  │
│  │  - runs scripts           │  │
│  │  - reads/writes JSON      │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

**Threading pattern:** Uvicorn runs in a background daemon thread. PyWebView takes the main thread (blocking). When the window closes, the daemon thread dies automatically.

---

## Project structure

```
rly/
├── README.md
├── .gitignore
├── pyproject.toml         # Project metadata + dependencies
├── launch.ps1             # Windows PowerShell launcher for PyWebView
├── src/
│   └── rly/
│       ├── __init__.py
│       ├── main.py        # FastAPI app + PyWebView launcher
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py  # FastAPI endpoints
│       ├── core/
│       │   ├── __init__.py
│       │   └── runner.py  # Script execution logic
│       ├── static/
│       │   └── css/
│       │       └── style.css
│       └── templates/
│           └── index.html
├── data/
│   └── actions.json       # Action library manifest
└── tests/
    └── __init__.py
```

---

## Data model

### Unified action entity

```json
{
  "id": "ci-restart-pods",
  "name": "CI: Restart pods",
  "description": "Restart the CI deployment and wait for rollout",
  "type": "command",
  "category": "kubernetes",
  "tags": ["k8s", "ci", "quick"],
  "command": "kubectl rollout restart deployment/farearth-ci-deployment -n ns-farearth-ci && kubectl rollout status deployment/farearth-ci-deployment -n ns-farearth-ci",
  "workingDirectory": "~",
  "parameters": [],
  "dangerLevel": "normal"
}
```

### Workflow action (Tier 3)

```json
{
  "id": "ci-full-reset",
  "name": "CI: Full wipe, init & wait",
  "type": "workflow",
  "tags": ["k8s", "ci", "destructive"],
  "dangerLevel": "destructive",
  "steps": [
    { "ref": "ci-wipe" },
    { "ref": "ci-init" },
    { "ref": "ci-rollout-wait" }
  ]
}
```

---

## Development workflow

### Daily development (WSL)
```bash
cd ~/dev/rly
source .venv/bin/activate
python -m src.rly.main --dev
# Open http://127.0.0.1:8000 in browser
# Hot reload enabled, browser dev tools available
```

### Testing desktop window (PowerShell)
```powershell
& "\\wsl$\Ubuntu\home\noe\dev\rly\launch.ps1"
```

### Environment details
- WSL Ubuntu 24.04, Python 3.12
- Windows Python 3.11 venv at: `C:\Users\noevh\Documents\MEGA\VsCode\rly-env\.venv`
- PyWebView on Windows uses Edge WebView2 (native, no GTK/QT needed)
- PyWebView does NOT work in WSLg (GTK renders white, QT has dependency issues)
- Jinja2 TemplateResponse uses new API: `templates.TemplateResponse(request, "index.html")` (not the old dict style)
- venv created with `--system-site-packages` in WSL for GTK bindings

---

## Design direction

### Branding
- **Name:** rly (from "relay")
- **Logo concept:** Purple relay switch / circuit symbol — a line hitting a contact point that triggers another line
- **Primary colour:** Purple (#a78bfa / #534AB7)
- **Aesthetic:** Dark theme, circuitry-inspired, clean and minimal

### UI concept
- Left sidebar: categories/tags for filtering
- Main area: action cards showing name, truncated command, tags, run button
- Bottom panel: output from last run (shows exact command, stdout/stderr, exit code)
- Destructive actions get warning badges (amber)
- Run history badge shows last execution time
- Search bar for filtering across all actions

---

## Real-world test data (user's actual daily commands)

```json
[
  {
    "id": "ci-activate-venv",
    "name": "CI - Activate Python Venv (WSL)",
    "command": "cd ~/dev/gitea/TechOps/devops/jenkins/4_deploy_to_ci/testing/python && source .venv/bin/activate"
  },
  {
    "id": "ci-restart-pods",
    "name": "CI: Restart Pods",
    "command": "kubectl rollout restart deployment/farearth-ci-deployment -n ns-farearth-ci && kubectl rollout status deployment/farearth-ci-deployment -n ns-farearth-ci"
  },
  {
    "id": "ci-full-reset",
    "name": "CI: Full Wipe, Init & Wait",
    "command": "cd ~/dev/gitea/TechOps/devops/jenkins/4_deploy_to_ci/k8s-deployment/ && bash wipe.sh && bash init.sh && kubectl rollout status deployment/farearth-ci-deployment -n ns-farearth-ci",
    "dangerLevel": "destructive"
  },
  {
    "id": "ci-run-wsl",
    "name": "CI - Run (WSL)",
    "command": "cd ~/dev/gitea/TechOps/devops/jenkins/4_deploy_to_ci/testing/python && bash run.sh"
  },
  {
    "id": "wsl-update",
    "name": "WSL: Update & Upgrade Ubuntu",
    "command": "echo 'Updating Ubuntu...' && sudo apt-get update && sudo apt-get -y upgrade && sudo apt-get autoremove && echo 'Update complete.'"
  }
]
```

---

## Competitor landscape

- **Rundeck** — enterprise, heavy, overkill for small teams
- **Raycast** — Mac-only, general productivity
- **Alfred** — Mac-only
- **ScriptKit** — developer-focused, different angle
- **Termius** — runs snippets on remote hosts only

**Gap:** Nobody does "command library + workflow chainer + searchable memory for your terminal" as a lightweight cross-platform tool.

---

## Key technical decisions log

1. **Python-only stack** — minimise new language learning, leverage existing skills
2. **HTMX over React** — adds interactivity via HTML attributes, no JS framework needed
3. **JSON over database** — simple for Tier 1-2, version-controllable, easy to share
4. **src layout** — prevents import bugs, Python best practice
5. **pyproject.toml over setup.py** — modern standard, single config file
6. **Editable install (`pip install -e`)** — code changes take effect immediately
7. **Separate Windows venv for PyWebView** — WSLg rendering broken, Windows Edge WebView2 works perfectly
8. **`--dev` flag for browser mode** — better dev experience with hot reload + browser dev tools
