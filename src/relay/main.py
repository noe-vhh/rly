import threading
import uvicorn
import webview
import argparse
import json
from relay.api.routes import router
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# .parent goes up one directory level, so BASE_DIR -> src/relay/
BASE_DIR = Path(__file__).parent

# FastAPI app
app = FastAPI()

app.include_router(router)

# Tell FastAPI where to find static files (CSS, JS) and templates (HTML)
# The "/static" first arg is the URL path, so your CSS will be at /static/css/style.css
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

def find_project_root():
    path = Path(__file__).parent
    while path != path.parent:
        if (path / "pyproject.toml").exists():
            return path
        path = path.parent
    raise FileNotFoundError("Could not find project root")

DATA_PATH = find_project_root() / "data" / "actions.json"

@app.get("/")
def home(request: Request):
    with open(DATA_PATH) as f:
        actions = json.load(f)

    categories = sorted(set(a["category"] for a in actions))
    print(f"DEBUG categories: {categories}")

    return templates.TemplateResponse(request, "index.html", {"categories": categories})

def start_server():
    """
    Run the FastAPI server in a background thread
    """
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # store_true means: if --dev is present, set it to True
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args()

    if args.dev:
        # runs directly, blocks until you Ctrl+C
        start_server()  
    else:
        # Start the server in a BACKGROUND thread | daemon=True means "kill this thread when the main program exits"
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        # Open the PyWebView window pointing at our local server
        # This is the MAIN thread, it blocks until the window is closed
        webview.create_window("relay", "http://127.0.0.1:8000", width=1000, height=700)
        webview.start()
