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
from fastapi.responses import HTMLResponse
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

@app.get("/", response_class=HTMLResponse, tags=["System"])
def root():
    """Landing page for the Multi-Agent Productivity Assistant."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Multi-Agent Productivity Assistant</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', sans-serif;
                min-height: 100vh;
                background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
                color: #e0e0e0;
                display: flex; align-items: center; justify-content: center;
            }
            .container {
                max-width: 800px; width: 90%; padding: 3rem;
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                border: 1px solid rgba(255,255,255,0.1);
                box-shadow: 0 25px 60px rgba(0,0,0,0.4);
            }
            .badge {
                display: inline-block; padding: 6px 14px;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 20px; font-size: 0.75rem;
                font-weight: 600; letter-spacing: 0.5px;
                text-transform: uppercase; color: #fff; margin-bottom: 1rem;
            }
            h1 { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem;
                 background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .subtitle { color: #aaa; font-size: 1rem; margin-bottom: 2rem; }
            .agents { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
            .agent-card {
                padding: 1.2rem; border-radius: 16px;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.08);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .agent-card:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(102,126,234,0.2); }
            .agent-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
            .agent-name { font-weight: 600; font-size: 0.95rem; margin-bottom: 0.3rem; }
            .agent-desc { font-size: 0.8rem; color: #999; }
            .endpoints { margin-bottom: 2rem; }
            .endpoints h3 { font-size: 1rem; font-weight: 600; margin-bottom: 0.8rem; color: #ccc; }
            .endpoint {
                display: flex; align-items: center; gap: 0.8rem;
                padding: 0.6rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);
                font-size: 0.85rem;
            }
            .method {
                padding: 3px 10px; border-radius: 6px; font-weight: 700;
                font-size: 0.7rem; min-width: 55px; text-align: center;
            }
            .get { background: rgba(34,197,94,0.15); color: #22c55e; }
            .post { background: rgba(59,130,246,0.15); color: #3b82f6; }
            .delete { background: rgba(239,68,68,0.15); color: #ef4444; }
            .path { font-family: 'Courier New', monospace; color: #e0e0e0; }
            .desc { color: #888; margin-left: auto; }
            .btn {
                display: inline-block; padding: 12px 28px;
                background: linear-gradient(90deg, #667eea, #764ba2);
                color: #fff; text-decoration: none;
                border-radius: 12px; font-weight: 600; font-size: 0.9rem;
                transition: opacity 0.2s;
            }
            .btn:hover { opacity: 0.85; }
            .footer { margin-top: 2rem; font-size: 0.75rem; color: #666; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="badge">Gen AI APAC Hackathon 2026</div>
            <h1>Multi-Agent Productivity Assistant</h1>
            <p class="subtitle">An AI-powered multi-agent system built with Google ADK, MCP &amp; Gemini</p>

            <div class="agents">
                <div class="agent-card">
                    <div class="agent-icon">&#128197;</div>
                    <div class="agent-name">Calendar Agent</div>
                    <div class="agent-desc">Schedule meetings, manage events, undo changes</div>
                </div>
                <div class="agent-card">
                    <div class="agent-icon">&#9989;</div>
                    <div class="agent-name">Task Agent</div>
                    <div class="agent-desc">CRUD tasks, priorities, tags, undo &amp; analytics</div>
                </div>
                <div class="agent-card">
                    <div class="agent-icon">&#128100;</div>
                    <div class="agent-name">Personalisation Agent</div>
                    <div class="agent-desc">User profile, timezone, work hours, preferences</div>
                </div>
            </div>

            <div class="endpoints">
                <h3>API Endpoints</h3>
                <div class="endpoint"><span class="method get">GET</span><span class="path">/health</span><span class="desc">Service health check</span></div>
                <div class="endpoint"><span class="method get">GET</span><span class="path">/tasks</span><span class="desc">List all tasks</span></div>
                <div class="endpoint"><span class="method post">POST</span><span class="path">/tasks</span><span class="desc">Create a task</span></div>
                <div class="endpoint"><span class="method post">POST</span><span class="path">/tasks/{id}/complete</span><span class="desc">Mark task done</span></div>
                <div class="endpoint"><span class="method delete">DEL</span><span class="path">/tasks/{id}</span><span class="desc">Soft-delete task</span></div>
                <div class="endpoint"><span class="method post">POST</span><span class="path">/tasks/undo</span><span class="desc">Undo last delete</span></div>
                <div class="endpoint"><span class="method get">GET</span><span class="path">/tasks/summary</span><span class="desc">Productivity dashboard</span></div>
                <div class="endpoint"><span class="method get">GET</span><span class="path">/events</span><span class="desc">List events</span></div>
                <div class="endpoint"><span class="method post">POST</span><span class="path">/events</span><span class="desc">Create an event</span></div>
                <div class="endpoint"><span class="method delete">DEL</span><span class="path">/events/{id}</span><span class="desc">Delete event</span></div>
                <div class="endpoint"><span class="method post">POST</span><span class="path">/events/undo</span><span class="desc">Undo last event action</span></div>
                <div class="endpoint"><span class="method get">GET</span><span class="path">/profile</span><span class="desc">User profile</span></div>
                <div class="endpoint"><span class="method post">POST</span><span class="path">/profile</span><span class="desc">Set preference</span></div>
            </div>

            <a class="btn" href="/docs">Explore Interactive API Docs &rarr;</a>

            <div class="footer">
                Built with Google ADK &bull; Gemini 2.0 Flash &bull; FastMCP &bull; AlloyDB &bull; Cloud Run<br>
                &copy; 2026 Harshad Chavan | Gen AI Academy APAC Cohort 1
            </div>
        </div>
    </body>
    </html>
    """

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
