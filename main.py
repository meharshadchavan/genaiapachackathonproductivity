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
import uuid
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

load_dotenv()

# Import shared storage and tools directly for REST endpoints
import storage
from tools.task_tools import create_task, list_tasks, delete_task, complete_task, get_task_summary, undo_delete_task
from tools.calendar_tools import create_event, list_events, delete_event, undo_last_calendar_action
from tools.personalization_tools import get_all_preferences, set_user_preference

# ADK session and runner (initialized at startup)
session_service: Optional[InMemorySessionService] = None
runner: Optional[Runner] = None
SESSIONS: dict = {}   # user_id -> session_id

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
    global session_service, runner
    print("[STARTUP] Multi-Agent Productivity Assistant API starting...")
    # Import agent here to avoid circular import at module level
    from agent import root_agent
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="productivity_assistant",
        session_service=session_service,
    )
    print("[STARTUP] ADK Runner initialized with Manager Agent 'Aria'.")
    yield
    print("[SHUTDOWN] API shutting down.")

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
        <title>Aria — Productivity Assistant</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            html { scroll-behavior: smooth; }
            body {
                font-family: 'Inter', sans-serif;
                min-height: 100vh;
                background: radial-gradient(circle at top left, rgba(103,126,234,0.18), transparent 28%),
                            radial-gradient(circle at bottom right, rgba(118,75,162,0.18), transparent 25%),
                            linear-gradient(180deg, #090b18 0%, #13162e 48%, #0c0f1d 100%);
                color: #e8ecff;
                padding: 0 18px 40px;
            }
            .page {
                max-width: 1200px;
                margin: 0 auto;
                padding: 28px 0;
            }
            .topbar {
                display: flex;
                flex-direction: column;
                gap: 14px;
                margin-bottom: 26px;
            }
            .topbar .badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 10px 16px;
                border-radius: 999px;
                background: rgba(103,126,234,0.18);
                color: #dbe2ff;
                font-weight: 700;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                font-size: 0.78rem;
            }
            .hero h1 {
                font-size: clamp(2.6rem, 4vw, 4.4rem);
                line-height: 1.02;
                letter-spacing: -0.05em;
                max-width: 780px;
                background: linear-gradient(90deg, #7c92ff, #9b6dff, #f093fb);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .hero p {
                max-width: 760px;
                color: #b8c2ff;
                font-size: 1rem;
                line-height: 1.75;
            }
            .status-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 16px;
                margin-top: 22px;
            }
            .status-card {
                padding: 18px 20px;
                border-radius: 22px;
                border: 1px solid rgba(255,255,255,0.08);
                background: rgba(255,255,255,0.05);
                box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
            }
            .status-card strong {
                display: block;
                font-size: 1.05rem;
                margin-bottom: 8px;
                color: #fff;
            }
            .status-card span {
                color: #abb7ff;
                font-size: 0.92rem;
                line-height: 1.7;
            }
            .layout {
                display: grid;
                grid-template-columns: 1.1fr 0.9fr;
                gap: 24px;
                align-items: start;
                margin-top: 32px;
            }
            .card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 24px;
                box-shadow: 0 26px 80px rgba(0,0,0,0.16);
                padding: 24px;
            }
            .card h2 {
                font-size: 1.2rem;
                margin-bottom: 18px;
                color: #f1f4ff;
            }
            .card p {
                color: #b8c2ff;
                line-height: 1.75;
                margin-bottom: 18px;
            }
            .tool-grid {
                display: grid;
                gap: 14px;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            }
            .tool-tile {
                padding: 18px;
                border-radius: 20px;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.08);
                transition: transform 0.2s ease, border-color 0.2s ease;
            }
            .tool-tile:hover {
                transform: translateY(-3px);
                border-color: rgba(103,126,234,0.32);
            }
            .tool-tile h3 {
                font-size: 1rem;
                margin-bottom: 8px;
                color: #fff;
            }
            .tool-tile p {
                color: #aaafff;
                font-size: 0.92rem;
                line-height: 1.6;
            }
            .chat-panel {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            .chat-window {
                display: flex;
                flex-direction: column;
                gap: 18px;
            }
            .chat-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
            }
            .chat-header h2 {
                font-size: 1.15rem;
                margin: 0;
            }
            .chat-header small {
                color: #a7b4ff;
            }
            .chat-messages {
                min-height: 420px;
                max-height: 600px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 12px;
                padding: 20px;
                border-radius: 22px;
                background: rgba(6,10,30,0.78);
                border: 1px solid rgba(255,255,255,0.08);
            }
            .message {
                max-width: 82%;
                padding: 14px 16px;
                border-radius: 18px;
                line-height: 1.6;
                font-size: 0.96rem;
                word-break: break-word;
                white-space: pre-wrap;
            }
            .message.user {
                align-self: flex-end;
                background: linear-gradient(135deg, rgba(102,126,234,0.28), rgba(118,75,162,0.28));
                border: 1px solid rgba(110,142,255,0.22);
            }
            .message.agent {
                align-self: flex-start;
                background: rgba(18,24,60,0.88);
                border: 1px solid rgba(96,108,224,0.14);
            }
            .message.typing {
                font-style: italic;
                color: #b0b9ff;
            }
            .chat-input-row {
                display: grid;
                gap: 12px;
            }
            .chat-input-row input {
                width: 100%;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.12);
                background: rgba(255,255,255,0.06);
                color: #eef2ff;
                padding: 16px 18px;
                font-size: 0.96rem;
                outline: none;
            }
            .chat-input-row button {
                width: 140px;
                justify-self: end;
                padding: 14px 18px;
                border-radius: 14px;
                border: none;
                cursor: pointer;
                color: #fff;
                background: linear-gradient(90deg, #667eea, #764ba2);
                font-weight: 700;
                transition: transform 0.2s ease, opacity 0.2s ease;
            }
            .chat-input-row button:hover { transform: translateY(-1px); opacity: 0.96; }
            .shortcut-buttons {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .shortcut-buttons button {
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 999px;
                background: rgba(255,255,255,0.05);
                color: #ccd6ff;
                padding: 10px 14px;
                font-size: 0.84rem;
                cursor: pointer;
                transition: background 0.2s ease, transform 0.2s ease;
            }
            .shortcut-buttons button:hover {
                background: rgba(103,126,234,0.16);
                transform: translateY(-1px);
            }
            @media (max-width: 960px) {
                .layout { grid-template-columns: 1fr; }
                .status-grid { grid-template-columns: 1fr; }
            }
            @media (max-width: 680px) {
                .topbar, .layout { gap: 18px; }
                .chat-input-row button { width: 100%; }
            }
        </style>
    </head>
    <body>
        <div class="page">
            <header class="topbar">
                <span class="badge">Gen AI APAC Hackathon 2026</span>
                <div class="hero">
                    <h1>Aria — your multi-agent productivity dashboard</h1>
                    <p>Use natural language to manage tasks, schedule meetings, and personalize your workspace. Aria routes your queries to the right specialist agent automatically.</p>
                </div>
            </header>
            <section class="status-grid">
                <div class="status-card">
                    <strong>Agent orchestration</strong>
                    <span>Manager + Task, Calendar, Personalization sub-agents.</span>
                </div>
                <div class="status-card">
                    <strong>Persistence ready</strong>
                    <span>Optional Firestore mode keeps tasks, events and profile persistent.</span>
                </div>
                <div class="status-card">
                    <strong>Cloud Run deployable</strong>
                    <span>REST API, UI and MCP tools all available inside one container.</span>
                </div>
            </section>
            <div class="layout">
                <div class="card">
                    <h2>Assistant workflow</h2>
                    <p>Aria understands natural language like:</p>
                    <ul style="color:#c4c9ff; margin: 0 0 18px 18px; line-height: 1.8;">
                        <li>"Create a high-priority task for the demo by Friday."</li>
                        <li>"Schedule a project review tomorrow at 3pm."</li>
                        <li>"Remember my name is Harshad and timezone is Asia/Kolkata."</li>
                        <li>"Undo the last calendar action."</li>
                    </ul>
                    <div class="tool-grid">
                        <div class="tool-tile">
                            <h3>Task management</h3>
                            <p>Create, complete, delete, undo and summarize tasks using natural language.</p>
                        </div>
                        <div class="tool-tile">
                            <h3>Calendar scheduling</h3>
                            <p>Schedule events, view meetings, delete items and restore them with undo.</p>
                        </div>
                        <div class="tool-tile">
                            <h3>Personalization</h3>
                            <p>Set preferences, timezone, work hours and default task priority.</p>
                        </div>
                    </div>
                </div>
                <div class="card chat-panel">
                    <div class="chat-window">
                        <div class="chat-header">
                            <div>
                                <h2>Chat with Aria</h2>
                                <small>Ask anything productivity-related.</small>
                            </div>
                            <span style="color:#8e9cff;">Live AI assistant</span>
                        </div>
                        <div id="chat-messages" class="chat-messages">
                            <div class="message agent">Hi, I'm <strong>Aria</strong>. I can help you manage tasks, schedule meetings, and remember preferences. What would you like to do?</div>
                        </div>
                    </div>
                    <div class="chat-input-row">
                        <input id="chat-input" type="text" placeholder="Type a request, e.g. 'Add a task to prepare slides'" autocomplete="off" onkeypress="if(event.key==='Enter')sendChat()" />
                        <button onclick="sendChat()" id="send-btn">Send</button>
                    </div>
                    <div class="shortcut-buttons">
                        <button onclick="quickSend('What can you do?')">What can you do?</button>
                        <button onclick="quickSend('Create a high priority task: finish the presentation')">Add urgent task</button>
                        <button onclick="quickSend('Schedule a meeting tomorrow at 11am with the team')">Schedule meeting</button>
                        <button onclick="quickSend('Show my task summary')">Task summary</button>
                        <button onclick="quickSend('My name is Harshad, timezone is Asia/Kolkata')">Set my profile</button>
                    </div>
                </div>
            </div>
        </div>
        <script>
            const USER_ID = localStorage.getItem('aria_user_id') || ('web_user_' + Math.random().toString(36).substr(2,6));
            localStorage.setItem('aria_user_id', USER_ID);
            const msgs = document.getElementById('chat-messages');
            function appendMsg(text, role) {
                const div = document.createElement('div');
                div.className = 'message ' + role;
                div.textContent = text;
                msgs.appendChild(div);
                msgs.scrollTop = msgs.scrollHeight;
            }
            function appendTyping() {
                const div = document.createElement('div');
                div.id = 'typing-indicator';
                div.className = 'message typing';
                div.textContent = 'Aria is thinking...';
                msgs.appendChild(div);
                msgs.scrollTop = msgs.scrollHeight;
            }
            function removeTyping() {
                const t = document.getElementById('typing-indicator');
                if (t) t.remove();
            }
            async function sendChat() {
                const input = document.getElementById('chat-input');
                const btn = document.getElementById('send-btn');
                const msg = input.value.trim();
                if (!msg) return;
                input.value = '';
                btn.disabled = true;
                btn.style.opacity = '0.6';
                appendMsg(msg, 'user');
                appendTyping();
                try {
                    const resp = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({message: msg, user_id: USER_ID})
                    });
                    const data = await resp.json();
                    removeTyping();
                    if (resp.ok) {
                        appendMsg(data.reply, 'agent');
                    } else {
                        appendMsg('[Error]: ' + (data.detail || 'Something went wrong.'), 'agent');
                    }
                } catch (e) {
                    removeTyping();
                    appendMsg('[Network error]: Could not reach the agent. Please try again.', 'agent');
                } finally {
                    btn.disabled = false;
                    btn.style.opacity = '1';
                    input.focus();
                }
            }
            function quickSend(text) {
                const input = document.getElementById('chat-input');
                input.value = text;
                sendChat();
            }
        </script>
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

# ── Chat Endpoint (ADK Runner) ──────────────────

@app.post("/chat", tags=["Chat"])
async def chat(req: ChatRequest):
    """Send a message to the Manager Agent and get a reply."""
    if runner is None:
        raise HTTPException(status_code=503, detail="Agent not initialized yet. Try again in a moment.")

    user_id = req.user_id or "default"

    # Get or create session for this user
    if user_id not in SESSIONS:
        session = await session_service.create_session(
            app_name="productivity_assistant",
            user_id=user_id,
        )
        SESSIONS[user_id] = session.id
    session_id = SESSIONS[user_id]

    new_message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=req.message)]
    )

    reply_parts = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message,
    ):
        # Collect only final agent text responses
        if event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        reply_parts.append(part.text)

    reply = "\n".join(reply_parts).strip() or "I processed your request."
    return {"status": "ok", "reply": reply, "user_id": user_id}

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
