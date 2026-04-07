"""
main.py — FastAPI REST API server.

Wraps the ADK multi-agent system as a Cloud Run-deployable REST API.
Endpoints:
  GET  /health          → Health check
  GET  /profile         → Get user profile
  POST /chat            → Send a message to the Manager Agent
  POST /tasks           → Create a task directly
  GET  /tasks           → List all tasks
  POST /events          → Create an event directly
  GET  /events          → List all events
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Import shared storage and tools directly for REST endpoints
import storage
from tools.task_tools import create_task, list_tasks, delete_task, complete_task, get_task_summary, undo_delete_task
from tools.calendar_tools import create_event, list_events, delete_event, undo_last_calendar_action
from tools.personalization_tools import get_all_preferences, set_user_preference

# ──────────────────────────────────────────────────
# Request / Response Models
# ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"

class TaskRequest(BaseModel):
    title: str
    priority: str = "medium"
    due_date: str = ""
    tags: str = ""
    notes: str = ""

class EventRequest(BaseModel):
    title: str
    date_time: str
    duration_mins: int = 60
    description: str = ""
    attendees: str = ""
    location: str = ""

class PreferenceRequest(BaseModel):
    key: str
    value: str

# ──────────────────────────────────────────────────
# App Initialization
# ──────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Multi-Agent Productivity Assistant API starting...")
    yield
    print("🛑 API shutting down.")

app = FastAPI(
    title="Multi-Agent Productivity Assistant",
    description=(
        "A multi-agent AI system built with Google ADK and MCP for managing tasks, "
        "schedules, and productivity with contextual memory."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for hackathon demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check():
    """Health check for Cloud Run liveness probe."""
    return {
        "status": "healthy",
        "service": "Multi-Agent Productivity Assistant",
        "version": "1.0.0",
        "agents": ["manager_agent", "calendar_agent", "task_agent", "personalization_agent"],
    }

# ── Task Endpoints ──────────────────────────────

@app.post("/tasks", tags=["Tasks"])
def api_create_task(req: TaskRequest):
    """Create a new task."""
    result = create_task(
        title=req.title,
        priority=req.priority,
        due_date=req.due_date,
        tags=req.tags,
        notes=req.notes,
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/tasks", tags=["Tasks"])
def api_list_tasks(
    status: Optional[str] = "",
    priority: Optional[str] = "",
    tag: Optional[str] = "",
):
    """List tasks with optional filters."""
    return list_tasks(
        status_filter=status or "",
        priority_filter=priority or "",
        tag_filter=tag or "",
    )

@app.post("/tasks/{task_id}/complete", tags=["Tasks"])
def api_complete_task(task_id: str):
    """Mark a task as done."""
    result = complete_task(task_id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@app.delete("/tasks/{task_id}", tags=["Tasks"])
def api_delete_task(task_id: str):
    """Soft-delete a task (can be undone)."""
    result = delete_task(task_id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@app.post("/tasks/undo", tags=["Tasks"])
def api_undo_task():
    """Undo the last task deletion."""
    return undo_delete_task()

@app.get("/tasks/summary", tags=["Tasks"])
def api_task_summary():
    """Get a productivity summary dashboard."""
    return get_task_summary()

# ── Calendar Endpoints ──────────────────────────

@app.post("/events", tags=["Calendar"])
def api_create_event(req: EventRequest):
    """Create a new calendar event."""
    result = create_event(
        title=req.title,
        date_time=req.date_time,
        duration_mins=req.duration_mins,
        description=req.description,
        attendees=req.attendees,
        location=req.location,
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/events", tags=["Calendar"])
def api_list_events(date: Optional[str] = ""):
    """List calendar events, optionally filtered by date prefix (YYYY-MM-DD)."""
    return list_events(date_filter=date or "")

@app.delete("/events/{event_id}", tags=["Calendar"])
def api_delete_event(event_id: str):
    """Delete a calendar event (can be undone)."""
    result = delete_event(event_id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@app.post("/events/undo", tags=["Calendar"])
def api_undo_event():
    """Undo the last calendar deletion or update."""
    return undo_last_calendar_action()

# ── Profile Endpoints ───────────────────────────

@app.get("/profile", tags=["Personalisation"])
def api_get_profile():
    """Get the user's full profile and preferences."""
    return get_all_preferences()

@app.post("/profile", tags=["Personalisation"])
def api_set_preference(req: PreferenceRequest):
    """Set a user preference (name, timezone, work_start, work_end, etc.)."""
    result = set_user_preference(key=req.key, value=req.value)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
