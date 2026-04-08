import json
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).parent.parent

templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter(prefix="/api", tags=["actions"])

@router.get("/actions")
async def get_actions():
    # Build the path to data/actions.json
    data_path = Path(__file__).parent.parent.parent.parent / "data" / "actions.json"

    # Open and parse it
    with open(data_path) as f:
        return json.load(f)

@router.get("/actions/cards")
async def get_action_cards(request: Request):
    data_path = Path(__file__).parent.parent.parent.parent / "data" / "actions.json"
    
    with open(data_path) as f:
        actions = json.load(f)
    
    return templates.TemplateResponse(request, "cards.html", {"actions": actions})
