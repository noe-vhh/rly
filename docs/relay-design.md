# Relay — Design Document

## Branding

- **Name:** Relay
- **Origin:** From "relay" — passing signals, chaining actions, relay race handoff
- **Logo concept:** Purple relay switch / circuit symbol — a line hitting a contact point that triggers another line (see logo explorations: Option A relay switch is the strongest fit)
- **Primary colour:** Purple (#a78bfa / #534AB7)
- **Aesthetic:** Dark theme, circuitry-inspired, clean and minimal

---

## Execution model

> Relay never owns execution. Your terminal stays your terminal.

### Single action
1. User finds action in library
2. Clicks **Run**
3. If action has parameters → param popup appears, user fills in values
4. Command is built with params interpolated
5. Command copied to clipboard
6. Toast notification: "Copied to clipboard"
7. User switches to their terminal and pastes

### Relay (chained actions)
1. User opens a relay (built via UI or JSON)
2. Clicks **Run**
3. If relay has parameters → param popup for any unresolved inputs
4. Relay generates a temporary bash script (e.g. `/tmp/relay-abc123.sh`)
5. Script call copied to clipboard (`bash /tmp/relay-abc123.sh`)
6. Toast notification: "Copied to clipboard"
7. User switches to their terminal and pastes
8. Full output streams naturally in their terminal — 100s of lines, scrollback, grep, all normal

### Run modes

Each action has a `runMode` field set when creating or editing the action:

| Mode | Behaviour |
|------|-----------|
| `copy` | Default. Command copied to clipboard, toast notification shown. User pastes in their terminal. |
| `spawn` | Opens a new terminal window, runs the command there. Stays open or closes based on `spawnBehaviour` field. |
| `silent` | Spawns a terminal, runs, closes immediately. Fire and forget. |

**Spawn behaviour field** (only relevant when `runMode: spawn`):
- `stay` — terminal stays open after command completes
- `close` — terminal closes on completion

> Auto-paste was considered and rejected — timing issues, wrong window focus, misfires. Clipboard + toast is simpler, safer, and respects that the terminal belongs to the user.

### No in-app output — ever
Relay does not capture or display command output. This is intentional:
- Output belongs in the terminal where it can be scrolled, grepped, and acted on
- Keeps Relay's role clear: library and launcher, not executor
- Avoids the "which terminal does it run on" problem entirely

---

## UI layout

```
┌─────────────────────┬──────────────────────────────────────┐
│  Sidebar            │  Main content area                   │
│                     │                                       │
│  [Relay logo]       │  [Page title]     [Search bar]       │
│                     │                                       │
│  Actions            │  ┌─────────────────────────────────┐ │
│  > All              │  │ Action card                     │ │
│  > Kubernetes       │  │ Name          [shell tag]       │ │
│  > CI / CD          │  │ command truncated...            │ │
│  > Cloud costs      │  │ [tag] [tag] [destructive]  [▶] │ │
│  > System           │  └─────────────────────────────────┘ │
│                     │                                       │
│  Relays             │  ┌─────────────────────────────────┐ │
│  > All relays       │  │ Action card                     │ │
│                     │  └─────────────────────────────────┘ │
│  [+ Add category]   │                                       │
│                     │  [+ New action]                      │
└─────────────────────┴──────────────────────────────────────┘
```

### Sidebar
- Split into two sections: **Actions** and **Relays**
- Actions section lists categories (user-defined)
- Relays section lists saved relays
- **+ Add category** button at the bottom opens a popup
- Active item highlighted with accent border

### Action cards
- Name (bold)
- Truncated command (monospace, muted)
- Shell tag pill (wsl / bash / powershell / zsh) — distinct from regular tags
- Regular tags as pills
- Danger badge if `dangerLevel: destructive` (amber)
- Run button (▶) top right
- Last run stat (e.g. "last: 2h ago") — Tier 2

### Search
- Filters across name, command, tags, category in real time
- Lives in the content header, not the sidebar

---

## Views

Relay has three distinct views. Same underlying action data, different lenses.

### Library view (Tier 1)
The dev.md replacement. Browse, search, find, copy. Value is **organisation and discoverability** — you come here when you've forgotten a command or want to find something.
- Full action cards with all metadata
- Search and filter by category, tag, shell
- Click card → opens detail/edit view
- Run button copies to clipboard

### Detail / edit view (Tier 1)
Full card expanded. All fields visible and editable inline. This is where you manage an action — not the library card itself, which stays compact for browsing.
- All action fields editable
- Save writes back to JSON
- Delete action
- "Pin to launchpad" toggle

### Launchpad view (Tier 3)
Streamdeck-style. Curated, visual, one-click. Value is **speed for things you run constantly** — you come here when you know exactly what you want to run.
- Grid of pinned actions
- Each action has an icon (user assigned or auto-generated from name initials)
- User arranges grid layout
- Click to run — param popup if needed, then clipboard + toast
- Separate from the library — you curate what lives here

> **Build order rationale:** Library first, always. You can't pin to a launchpad that doesn't exist yet. The launchpad is also the demo moment — immediately legible to colleagues in a way the library takes time to appreciate.

---

## Add action — UI form

Accessible via **+ New action** button. Opens a modal/panel. No JSON editing required.

### Form fields

| Field | Input type | Notes |
|-------|-----------|-------|
| Name | Text | Free text |
| Description | Text | Optional, free text |
| Command | Textarea | Free text, monospace |
| Category | Dropdown + inline "+" | Lists existing categories. "+ New category" opens popup |
| Shell | Dropdown | Fixed options: `wsl`, `bash`, `zsh`, `powershell` |
| Type | Dropdown | Fixed options: `command`, `script` |
| Danger level | Dropdown | Fixed options: `normal`, `destructive` |
| Tags | Tag input | Type and press Enter to add. Pill displayed, click to remove |
| Working directory | Text | Optional, defaults to `~` |
| Parameters | Dynamic list | "+ Add param" adds a row: param name + type + optional default |
| Run mode | Dropdown | Fixed options: `copy`, `spawn`, `silent` — see run modes |

### Add category popup
- Triggered by "+ New category" in the category dropdown, or "+ Add category" in sidebar
- Simple single input: category name
- Confirm adds it to the JSON and selects it in the form
- No page reload — HTMX updates the dropdown and sidebar inline

---

## Data models

### Action

```json
{
  "id": "ci-restart-pods",
  "name": "CI: Restart pods",
  "description": "Restart the CI deployment and wait for rollout",
  "type": "command",
  "shell": "wsl",
  "category": "kubernetes",
  "tags": ["k8s", "ci", "quick"],
  "command": "kubectl rollout restart deployment/farearth-ci-deployment -n ns-farearth-ci && kubectl rollout status deployment/farearth-ci-deployment -n ns-farearth-ci",
  "workingDirectory": "~",
  "parameters": [],
  "dangerLevel": "normal",
  "runMode": "copy",
  "spawnBehaviour": null,
  "capture": []
}
```

### Action with parameters and capture

```json
{
  "id": "ci-run-tests",
  "name": "CI: Run tests",
  "description": "Run the test suite for a given date",
  "type": "script",
  "shell": "wsl",
  "category": "ci-cd",
  "tags": ["ci", "tests"],
  "command": "python main.py --date {date} --env {env}",
  "workingDirectory": "~/dev/ci",
  "parameters": [
    { "name": "date", "type": "string", "default": "" },
    { "name": "env",  "type": "string", "default": "staging" }
  ],
  "dangerLevel": "normal",
  "runMode": "copy",
  "spawnBehaviour": null,
  "capture": [
    { "name": "result", "from": "stdout", "pattern": "Result: (\\S+)" },
    { "name": "exitCode", "from": "exit_code" }
  ]
}
```

### Relay

```json
{
  "id": "ci-full-reset",
  "name": "CI: Full wipe, init & wait",
  "description": "Wipe the CI environment, reinitialise, and wait for rollout",
  "tags": ["k8s", "ci", "destructive"],
  "dangerLevel": "destructive",
  "steps": [
    {
      "ref": "ci-wipe",
      "params": {}
    },
    {
      "ref": "ci-init",
      "params": {}
    },
    {
      "ref": "ci-rollout-wait",
      "params": {
        "namespace": "$.steps.ci-init.output.namespace"
      }
    }
  ]
}
```

> `$.steps.<id>.output.<key>` is the output-linking syntax — Tier 2. Step outputs are captured and passed as params to subsequent steps.

### Categories manifest

Categories are stored separately so they can be managed independently of actions:

```json
{
  "categories": [
    { "id": "kubernetes",   "name": "Kubernetes" },
    { "id": "ci-cd",        "name": "CI / CD" },
    { "id": "cloud-costs",  "name": "Cloud costs" },
    { "id": "system",       "name": "System maintenance" },
    { "id": "dev",          "name": "Dev" }
  ]
}
```

### Launchpad manifest (Tier 3)

Stored separately. References action IDs from the library. User arranges grid position and assigns icons.

```json
{
  "launchpad": [
    { "actionId": "ci-restart-pods", "icon": "🔄", "position": 0 },
    { "actionId": "wsl-update",      "icon": "⬆️",  "position": 1 },
    { "actionId": "ci-full-reset",   "icon": "💥",  "position": 2 }
  ]
}
```

---

## Shell tag behaviour

The `shell` field on an action serves two purposes:

1. **Display** — shown as a distinct pill on the action card, styled differently from regular tags
2. **Filtering** — sidebar or filter bar can filter by shell type

Shell values: `wsl`, `bash`, `zsh`, `powershell`

---

## Relay builder (Tier 2)

### Canvas
- n8n-style visual drag-and-drop canvas
- Actions dragged from the library panel onto the canvas as nodes
- Nodes connected by drawing lines between output → input ports
- Each node shows action name, shell tag, and its defined params
- Unlinked params are surfaced in the param popup at run time
- On run: Relay generates a temp bash script, copies to clipboard, toast notification

### Output capture and linking

This is the mechanism that lets step 1's output feed into step 2 as input.

**Approach: named captures**
Rather than trying to parse arbitrary stdout (fragile, breaks on noisy output like test runners), the user defines what an action "returns" in the action manifest. Relay extracts only those named values and makes them available to the next step.

```json
"capture": [
  { "name": "namespace", "from": "stdout", "pattern": "namespace: (\\S+)" },
  { "name": "exitCode",  "from": "exit_code" }
]
```

Captured outputs are stored as a JSON object during relay execution:

```json
{
  "ci-init": {
    "namespace": "ns-farearth-ci",
    "exitCode": 0
  }
}
```

Referenced in subsequent steps using dot notation:

```json
"params": {
  "namespace": "$.steps.ci-init.namespace"
}
```

**Why not raw stdout piping?**
Raw stdout piping works for simple cases but breaks on commands with noisy output (test runners, apt-get, kubectl rollout status). Named captures let the user define exactly what's useful. Defined once in the action, works everywhere it's used.

### Relay data model (updated)

```json
{
  "id": "ci-full-reset",
  "name": "CI: Full wipe, init & wait",
  "description": "Wipe the CI environment, reinitialise, and wait for rollout",
  "tags": ["k8s", "ci", "destructive"],
  "dangerLevel": "destructive",
  "steps": [
    {
      "ref": "ci-wipe",
      "params": {}
    },
    {
      "ref": "ci-init",
      "params": {}
    },
    {
      "ref": "ci-rollout-wait",
      "params": {
        "namespace": "$.steps.ci-init.namespace"
      }
    }
  ]
}
```

---

## Real-world test data

```json
[
  {
    "id": "ci-activate-venv",
    "name": "CI - Activate Python Venv (WSL)",
    "shell": "wsl",
    "category": "ci-cd",
    "tags": ["ci", "python", "venv"],
    "command": "cd ~/dev/gitea/TechOps/devops/jenkins/4_deploy_to_ci/testing/python && source .venv/bin/activate",
    "dangerLevel": "normal"
  },
  {
    "id": "ci-restart-pods",
    "name": "CI: Restart Pods",
    "shell": "wsl",
    "category": "kubernetes",
    "tags": ["k8s", "ci", "quick"],
    "command": "kubectl rollout restart deployment/farearth-ci-deployment -n ns-farearth-ci && kubectl rollout status deployment/farearth-ci-deployment -n ns-farearth-ci",
    "dangerLevel": "normal"
  },
  {
    "id": "ci-full-reset",
    "name": "CI: Full Wipe, Init & Wait",
    "shell": "wsl",
    "category": "kubernetes",
    "tags": ["k8s", "ci", "destructive"],
    "command": "cd ~/dev/gitea/TechOps/devops/jenkins/4_deploy_to_ci/k8s-deployment/ && bash wipe.sh && bash init.sh && kubectl rollout status deployment/farearth-ci-deployment -n ns-farearth-ci",
    "dangerLevel": "destructive"
  },
  {
    "id": "ci-run-wsl",
    "name": "CI - Run (WSL)",
    "shell": "wsl",
    "category": "ci-cd",
    "tags": ["ci", "run"],
    "command": "cd ~/dev/gitea/TechOps/devops/jenkins/4_deploy_to_ci/testing/python && bash run.sh",
    "dangerLevel": "normal"
  },
  {
    "id": "wsl-update",
    "name": "WSL: Update & Upgrade Ubuntu",
    "shell": "wsl",
    "category": "system",
    "tags": ["wsl", "ubuntu", "maintenance"],
    "command": "echo 'Updating Ubuntu...' && sudo apt-get update && sudo apt-get -y upgrade && sudo apt-get autoremove && echo 'Update complete.'",
    "dangerLevel": "normal"
  }
]
```
