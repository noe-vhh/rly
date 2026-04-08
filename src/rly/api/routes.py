import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["actions"])

@router.get("/actions")
async def get_actions():
    # Build the path to data/actions.json
    data_path = Path(__file__).parent.parent.parent.parent / "data" / "actions.json"

    # Open and parse it
    with open(data_path) as f:
        return json.load(f)
