import threading
import uvicorn
import webview
import argparse
import json
from contextlib import asynccontextmanager
from relay.api.routes import router
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Paths
BASE_DIR = Path(__file__).parent

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

# Startup seeding
def seed_categories():
    with open(DATA_PATH) as f:
        actions = json.load(f)

    with open(CATEGORIES_PATH) as f:
        categories = json.load(f)

    if not categories["categories"]:
        seen = set()
        new_cats = []
        for action in actions:
            if action["category"] not in seen:
                seen.add(action["category"])
                new_cats.append({
                    "id": action["category"],
                    "name": action["category"].capitalize()
                })
        categories["categories"] = new_cats
        with open(CATEGORIES_PATH, "w") as f:
            json.dump(categories, f, indent=4)

# App startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_categories()
    yield

# App
app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Routes
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

# Server
def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args()

    if args.dev:
        start_server()
    else:
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        webview.create_window("relay", "http://127.0.0.1:8000", width=1000, height=700)
        webview.start()
