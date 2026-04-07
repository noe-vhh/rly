# rly

Command memory and workflow orchestrator - a terminal companion.

> Think "Grafana for scripts": a visibility and accessibility layer that sits alongside your terminal. Organise, search, and run your commands without replacing the CLI.

## Status

Early development - Tier 1 (command library)

## Stack

- **Backend:** Python + FastAPI
- **Frontend:** HTML + CSS + HTMX (no JavaScript framework)
- **Desktop wrapper:** PyWebView
- **Data:** JSON manifest (no database)

---

## Quick start (WSL - browser dev mode)

### Prerequisites

- WSL2 with Ubuntu (22.04 or 24.04)
- Python 3.10+
- Git

### Setup

```bash
# Clone the repo
git clone git@github.com:YOUR_USERNAME/rly.git
cd rly

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install rly in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Run

```bash
# Start the dev server (hot reload enabled)
python -m src.rly.main --dev
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Desktop app (Windows - PyWebView)

This runs rly as a native desktop window using Edge WebView2. Useful for testing the desktop experience or running rly as a standalone app.

### Prerequisites

- Python 3.10+ installed on Windows
- The WSL setup above completed first (source code lives in WSL)

### One-time setup

```powershell
# Create a Windows venv
# Choose any local Windows path you like
mkdir "C:\dev\rly-env"
python -m venv "C:\dev\rly-env\.venv"

# If you get an execution policy error, run this first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Activate the Windows venv
& "C:\dev\rly-env\.venv\Scripts\Activate.ps1"

# Install rly from the WSL project (adjust the path to match your WSL distro/username)
pip install -e "\\wsl$\Ubuntu\home\YOUR_USERNAME\dev\rly[dev]"
```

### Update launch.ps1

Edit `launch.ps1` in the project root and update both paths to match your setup:

- `$projectRoot` - your WSL project path
- `$pythonExe` - your Windows venv Python path

### Run

```powershell
# From any directory in PowerShell
& "\\wsl$\Ubuntu\home\YOUR_USERNAME\dev\rly\launch.ps1"
```

### Why the separate Windows venv?

PyWebView on Windows uses Edge WebView2 via `pythonnet`. The `pythonnet` library crashes when loaded from a UNC path (`\\wsl$\...`), so the venv must live on a native Windows drive. The source code stays in WSL - only the venv is on the Windows side.

If you add new dependencies to `pyproject.toml`, re-run `pip install -e "\\wsl$\...\rly[dev]"` in the Windows venv to sync them.

---

## Project structure

```
rly/
├── README.md              # You are here
├── pyproject.toml         # Project metadata and dependencies
├── launch.ps1             # Windows desktop launcher
├── .gitignore
├── src/
│   └── rly/
│       ├── __init__.py
│       ├── main.py        # App entry point (FastAPI + PyWebView)
│       ├── api/            # FastAPI route handlers
│       ├── core/           # Business logic (script runner, etc.)
│       ├── static/         # CSS, JS, images
│       └── templates/      # Jinja2 HTML templates
├── data/
│   └── actions.json       # Your action library
└── tests/
```

## Development notes

### Daily workflow

| Task | Command |
|------|---------|
| Start dev server (WSL) | `python -m src.rly.main --dev` |
| Test desktop window (PowerShell) | `& "\\wsl$\...\rly\launch.ps1"` |
| Run tests | `pytest` |
| Lint | `ruff check src/` |

### Known issues

- **PyWebView does not render in WSLg.** The GTK/WebKit backend opens a window but displays white. The QT backend has unresolved dependency issues. Use browser mode for WSL development and the Windows launcher for desktop testing.
- The `MESA: error: ZINK: failed to choose pdev` warning in WSL is cosmetic and can be ignored.
