# Relay — Project Brief

## What is Relay?

A **command memory and relay orchestrator** — a terminal companion, not a terminal replacement. Think "Grafana for scripts": a visibility and accessibility layer that sits alongside your terminal.

> "Your dev.md, but visual, searchable, and runnable."

Every DevOps engineer has a dev.md — a notes file, a Notion page, a pinned Slack message to themselves, a bash_aliases file that got out of hand. Relay solves that pain universally.

---

## Core concept

Two layers, same data model:

- **Actions** — your command library. Single commands or scripts, categorised, tagged, searchable. This is your dev.md replacement.
- **Relays** — chained actions. Link actions together, pass outputs as inputs, generate a script and hand it to your terminal. This is your workflow engine.

Same UI, same search, same JSON manifest. Complexity scales with the user.

### Positioning

- NOT a terminal replacement — a companion you use alongside your terminal
- Like a flight checklist on a pilot's kneeboard: the pilot still flies the plane
- Relay never owns execution — your terminal stays your terminal
- Config-as-code (JSON manifest), version-controllable, easy to share
- Target user: mid-level DevOps/SRE engineer with commands scattered across bash history, sticky notes, Notion pages, and markdown files they're tired of maintaining

---

## Roadmap

### Tier 1 — Action library (current)
- View, search, and filter actions
- Categorise and tag actions
- Shell type filtering (wsl / bash / powershell / zsh)
- Click to copy — clipboard toast notification
- Add actions via UI form (no JSON editing required)
- Add categories via popup
- **This alone is useful on day one**

### Tier 2 — Parameters + Relays
- Parameter input fields mapped to script arguments
- Param popup on run — enter values, command is built, copied to clipboard
- Relay builder — chain actions, link outputs to inputs
- Relay generates a temp bash script, same clipboard flow as single actions
- Run stats — last run time, copy count, basic usage tracking per action

### Tier 3 — Polish + team readiness
- Import from existing configs (e.g. Windows Terminal JSON, bash_history)
- Export/import action collections
- Scheduling (run every Monday)
- Onboarding flow for new colleagues

### Tier 4 — Team + sharing (product)
- Multi-user / team features
- Shared action libraries
- Distribution via PyPI (`pip install relay` / `pip install --upgrade relay`)
- Optional: bundled installer via PyInstaller for colleagues without Python
- Optional: startup update-check against PyPI version
- **This is where it becomes a product**

---

## Progression strategy

**Personal → Internal → Market**

1. Build it for yourself. Stop using dev.md entirely.
2. Get one colleague using it. Validate the library experience is sticky.
3. Build Relays on a validated foundation.
4. Then invest in distribution and team features.

> Do not build a sophisticated workflow engine on an unvalidated foundation. Nail the action library first.

---

## Tech stack

All Python, minimal new language learning.

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | FastAPI | Python, modern, auto-generated API docs |
| Frontend | HTML + CSS + HTMX | No React/framework needed. HTMX adds interactivity via HTML attributes |
| Desktop wrapper | PyWebView | Wraps the web UI in a native OS window — this is a desktop app, not a web app |
| Templating | Jinja2 | Renders HTML server-side, used by FastAPI |
| Data | JSON file | No database for Tier 1-2. Version-controllable, shareable |
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
│  │  - builds commands        │  │
│  │  - reads/writes JSON      │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

**Threading pattern:** Uvicorn runs in a background daemon thread. PyWebView takes the main thread (blocking). When the window closes, the daemon thread dies automatically.

---

## Competitor landscape

- **Rundeck** — enterprise, heavy, overkill for small teams
- **Raycast** — Mac-only, general productivity
- **Alfred** — Mac-only
- **ScriptKit** — developer-focused, different angle
- **Termius** — runs snippets on remote hosts only

**Gap:** Nobody does "command library + relay chainer + searchable memory for your terminal" as a lightweight cross-platform desktop tool.

---

## Key technical decisions log

1. **Python-only stack** — minimise new language learning, leverage existing skills
2. **HTMX over React** — adds interactivity via HTML attributes, no JS framework needed
3. **JSON over database** — simple for Tier 1-2, version-controllable, easy to share
4. **Desktop app via PyWebView** — not a web app, wraps the UI in a native OS window
5. **src layout** — prevents import bugs, Python best practice
6. **pyproject.toml over setup.py** — modern standard, single config file
7. **Editable install (`pip install -e`)** — code changes take effect immediately
8. **Separate Windows venv for PyWebView** — WSLg rendering broken, Windows Edge WebView2 works perfectly
9. **`--dev` flag for browser mode** — better dev experience with hot reload + browser dev tools
10. **Relay never owns execution** — commands always land in the user's terminal via clipboard, Relay is a companion not a replacement

---

## Environment details

- WSL Ubuntu 24.04, Python 3.12
- Windows Python 3.11 venv at: `C:\Users\noevh\Documents\MEGA\VsCode\rly-env\.venv`
- PyWebView on Windows uses Edge WebView2 (native, no GTK/QT needed)
- PyWebView does NOT work in WSLg (GTK renders white, QT has dependency issues)
- Jinja2 TemplateResponse uses new API: `templates.TemplateResponse(request, "index.html")`
- venv created with `--system-site-packages` in WSL for GTK bindings

---

## Development workflow

### Daily development (WSL)
```bash
cd ~/dev/relay
source .venv/bin/activate
python -m src.relay.main --dev
# Open http://127.0.0.1:8000 in browser
# Hot reload enabled, browser dev tools available
```

### Testing desktop window (PowerShell)
```powershell
& "\\wsl$\Ubuntu\home\noe\dev\relay\launch.ps1"
```
