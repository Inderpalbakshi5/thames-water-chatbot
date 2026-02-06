"""
Gurbani Projection Server

FastAPI application that serves:
- Projection UI (full-screen display for projector)
- Admin panel (control interface for tablet/laptop)
- WebSocket endpoints for real-time state synchronization
- REST API for Bani management and system control
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import AppConfig
from .core.gurbani_db import GurbaniDatabase
from .core.state_manager import StateManager

logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "ui" / "templates"
STATIC_DIR = BASE_DIR / "ui" / "static"
DATA_DIR = BASE_DIR / "data"

# Global state
config = AppConfig()
db: GurbaniDatabase = None
state_manager: StateManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    global db, state_manager

    # Initialize database
    db_path = DATA_DIR / "gurbani.db"
    db = GurbaniDatabase(db_path)

    # Load any available Bani data files
    for json_file in DATA_DIR.glob("*.json"):
        try:
            db.load_bani_from_json(json_file)
            logger.info(f"Loaded Bani data from {json_file.name}")
        except Exception as e:
            logger.error(f"Failed to load {json_file.name}: {e}")

    # Initialize state manager
    state_manager = StateManager(config, db)

    available = db.get_available_banis()
    logger.info(f"Gurbani Projection Server started. Available Banis: {available}")

    yield

    # Cleanup
    db.close()
    logger.info("Server shutdown complete")


app = FastAPI(
    title="Gurbani Projection System",
    description="Automated Gurbani voice recognition and projection",
    version="0.1.0",
    lifespan=lifespan,
)

# Serve static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# --- HTML Pages ---

@app.get("/", response_class=HTMLResponse)
async def projection_page():
    """Serve the projection display page."""
    html_path = TEMPLATES_DIR / "projection.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """Serve the admin control panel."""
    html_path = TEMPLATES_DIR / "admin.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


# --- REST API ---

@app.get("/api/state")
async def get_state():
    """Get current system state."""
    return state_manager.get_state()


@app.get("/api/banis")
async def list_banis():
    """List available Banis."""
    return {"banis": db.get_available_banis()}


@app.post("/api/bani/{bani_name}")
async def select_bani(bani_name: str):
    """Select a Bani for projection."""
    available = db.get_available_banis()
    if bani_name not in available:
        return {"error": f"Bani '{bani_name}' not found. Available: {available}"}
    await state_manager.select_bani(bani_name)
    return {"status": "ok", "bani": bani_name}


@app.post("/api/start")
async def start_listening():
    """Start listening for Granthi voice."""
    await state_manager.start_listening()
    return {"status": "ok"}


@app.post("/api/stop")
async def stop_listening():
    """Stop listening."""
    await state_manager.stop_listening()
    return {"status": "ok"}


@app.post("/api/next")
async def next_verse():
    """Advance to next verse."""
    await state_manager.next_verse()
    return {"status": "ok"}


@app.post("/api/jump/{section}")
async def jump_to_section(section: int):
    """Jump to a specific section."""
    await state_manager.jump_to_section(section)
    return {"status": "ok"}


@app.post("/api/resume")
async def resume_listening():
    """Resume listening after pause."""
    await state_manager.resume_listening()
    return {"status": "ok"}


@app.get("/api/verses/{bani_name}")
async def get_bani_verses(bani_name: str):
    """Get all verses for a Bani (for offline caching)."""
    verses = db.get_bani_verses(bani_name)
    return {
        "bani": bani_name,
        "verses": [
            {
                "id": v.id,
                "section": v.section,
                "line_number": v.line_number,
                "gurmukhi": v.gurmukhi,
                "transliteration": v.transliteration,
                "translation_en": v.translation_en,
                "ang": v.ang,
            }
            for v in verses
        ],
    }


# --- WebSocket Endpoints ---

@app.websocket("/ws/projection")
async def ws_projection(websocket: WebSocket):
    """WebSocket for projection display. Receives state updates."""
    await websocket.accept()
    await state_manager.register_client(websocket)
    try:
        while True:
            # Projection client can send control commands (keyboard shortcuts)
            data = await websocket.receive_text()
            msg = json.loads(data)
            await _handle_command(msg)
    except WebSocketDisconnect:
        await state_manager.unregister_client(websocket)
    except Exception as e:
        logger.error(f"Projection WS error: {e}")
        await state_manager.unregister_client(websocket)


@app.websocket("/ws/admin")
async def ws_admin(websocket: WebSocket):
    """WebSocket for admin panel. Sends state, receives commands."""
    await websocket.accept()
    await state_manager.register_client(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            await _handle_command(msg)
    except WebSocketDisconnect:
        await state_manager.unregister_client(websocket)
    except Exception as e:
        logger.error(f"Admin WS error: {e}")
        await state_manager.unregister_client(websocket)


async def _handle_command(msg: dict):
    """Handle a command from WebSocket client."""
    action = msg.get("action")

    if action == "select_bani":
        bani = msg.get("bani")
        if bani:
            await state_manager.select_bani(bani)

    elif action == "start_listening":
        await state_manager.start_listening()

    elif action == "stop_listening":
        await state_manager.stop_listening()

    elif action == "next_verse":
        await state_manager.next_verse()

    elif action == "resume_listening":
        await state_manager.resume_listening()

    elif action == "jump_to_section":
        section = msg.get("section")
        if section is not None:
            await state_manager.jump_to_section(int(section))

    elif action == "stt_result":
        # Browser-based STT result
        text = msg.get("text", "")
        is_partial = msg.get("is_partial", False)
        if text:
            await state_manager.process_stt_result(text, is_partial)

    else:
        logger.warning(f"Unknown command: {action}")
