import json
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).parent.parent

templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter(prefix="/api", tags=["actions"])

def find_project_root():
    path = Path(__file__).parent
    while path != path.parent:
        if (path / "pyproject.toml").exists():
            return path
        path = path.parent
    raise FileNotFoundError("Could not find project root")

DATA_PATH = find_project_root() / "data" / "actions.json"

@router.get("/actions")
async def get_actions():
    # Open JSON and parse it
    with open(DATA_PATH) as f:
        return json.load(f)

@router.get("/actions/cards")
async def get_action_cards(request: Request, category: str = None):
    with open(DATA_PATH) as f:
        actions = json.load(f)

    if category:
        actions = [a for a in actions if a["category"] == category]
    
    return templates.TemplateResponse(request, "cards.html", {"actions": actions})
