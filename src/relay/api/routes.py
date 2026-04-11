import json
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent

templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter(prefix="/api", tags=["actions"])

class NewCategory(BaseModel):
    name: str

def find_project_root():
    path = Path(__file__).parent
    while path != path.parent:
        if (path / "pyproject.toml").exists():
            return path
        path = path.parent
    raise FileNotFoundError("Could not find project root")

PROJECT_ROOT = find_project_root()
DATA_PATH = PROJECT_ROOT / "data" / "actions.json"
CATEGORIES_PATH = PROJECT_ROOT / "data" / "categories.json"

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

@router.post("/categories")
async def add_category(category: NewCategory):
    with open(CATEGORIES_PATH) as f:
        data = json.load(f)

    new_cat = {
        "id": category.name.lower().replace(" ", "-"),
        "name": category.name
    }
    data["categories"].append(new_cat)

    with open(CATEGORIES_PATH, "w") as f:
        json.dump(data, f, indent=4)

    return data

@router.get("/categories")
async def get_categories(request: Request):
    with open(CATEGORIES_PATH) as f:
        categories = json.load(f)

    return templates.TemplateResponse(request, "categories.html", {"categories": categories["categories"]})

@router.delete("/categories/{category_id}")
async def delete_category(request: Request, category_id: str):
    with open(CATEGORIES_PATH) as f:
        categories = json.load(f)

    categories["categories"] = [
        c for c in categories["categories"] if c["id"] != category_id
    ]

    with open(CATEGORIES_PATH, "w") as f:
        json.dump({"categories": categories["categories"]}, f, indent=4)

    return templates.TemplateResponse(request, "categories.html", {"categories": categories["categories"]})
