"""
storage.py — Shared in-memory data store for all sub-agents.
Provides events, tasks, user_profile with undo stacks.
"""

import uuid
from datetime import datetime
from typing import Any

# ─────────────────────────────────────────────
# Calendar Events store
# key: event_id (str)  →  value: event dict
# ─────────────────────────────────────────────
events: dict[str, dict] = {}
calendar_trash_stack: list[dict] = []   # undo stack for deleted/overwritten events

# ─────────────────────────────────────────────
# Tasks store
# key: task_id (str)  →  value: task dict
# ─────────────────────────────────────────────
tasks: dict[str, dict] = {}
task_trash_stack: list[dict] = []       # undo stack for soft-deleted tasks

# ─────────────────────────────────────────────
# User profile / personalisation
# ─────────────────────────────────────────────
user_profile: dict[str, Any] = {
    "name": "User",
    "timezone": "Asia/Kolkata",
    "work_start": "09:00",
    "work_end": "18:00",
    "preferred_priority": "medium",
    "theme": "dark",
}

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def new_id() -> str:
    """Return a short UUID."""
    return str(uuid.uuid4())[:8]

def now_iso() -> str:
    """Return current UTC time as ISO string."""
    return datetime.utcnow().isoformat() + "Z"
