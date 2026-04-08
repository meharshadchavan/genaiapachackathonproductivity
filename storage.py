"""
storage.py — Shared data store for all sub-agents.
Supports optional Firestore persistence for events, tasks, and user profile.
"""

import os
import uuid
from datetime import datetime
from typing import Any

try:
    from google.cloud import firestore
except ImportError:
    firestore = None

USE_FIRESTORE = os.getenv("USE_FIRESTORE", "false").lower() in ("1", "true", "yes") and firestore is not None

# ─────────────────────────────────────────────
# Firestore configuration
# ─────────────────────────────────────────────
FS_COLLECTION_EVENTS = "productivity_events"
FS_COLLECTION_TASKS = "productivity_tasks"
FS_COLLECTION_METADATA = "productivity_metadata"
FS_PROFILE_DOC = "user_profile"

fs_client = None
if USE_FIRESTORE:
    try:
        fs_client = firestore.Client()
    except Exception as exc:
        print(f"[storage] Firestore client init failed: {exc}")
        USE_FIRESTORE = False

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
# Utilities
# ─────────────────────────────────────────────

def new_id() -> str:
    """Return a short UUID."""
    return str(uuid.uuid4())[:8]


def now_iso() -> str:
    """Return current UTC time as ISO string."""
    return datetime.utcnow().isoformat() + "Z"


def _event_doc_ref(event_id: str):
    return fs_client.collection(FS_COLLECTION_EVENTS).document(event_id)


def _task_doc_ref(task_id: str):
    return fs_client.collection(FS_COLLECTION_TASKS).document(task_id)


def _profile_doc_ref():
    return fs_client.collection(FS_COLLECTION_METADATA).document(FS_PROFILE_DOC)


def persist_event(event: dict) -> None:
    if not USE_FIRESTORE:
        return
    try:
        _event_doc_ref(event["id"]).set(event)
    except Exception as exc:
        print(f"[storage] Failed to persist event {event['id']}: {exc}")


def delete_event_doc(event_id: str) -> None:
    if not USE_FIRESTORE:
        return
    try:
        _event_doc_ref(event_id).delete()
    except Exception as exc:
        print(f"[storage] Failed to delete event doc {event_id}: {exc}")


def persist_task(task: dict) -> None:
    if not USE_FIRESTORE:
        return
    try:
        _task_doc_ref(task["id"]).set(task)
    except Exception as exc:
        print(f"[storage] Failed to persist task {task['id']}: {exc}")


def delete_task_doc(task_id: str) -> None:
    if not USE_FIRESTORE:
        return
    try:
        _task_doc_ref(task_id).delete()
    except Exception as exc:
        print(f"[storage] Failed to delete task doc {task_id}: {exc}")


def persist_profile() -> None:
    if not USE_FIRESTORE:
        return
    try:
        _profile_doc_ref().set(user_profile)
    except Exception as exc:
        print(f"[storage] Failed to persist user profile: {exc}")


def load_firestore_state() -> None:
    if not USE_FIRESTORE:
        return
    try:
        events.clear()
        tasks.clear()

        for doc in fs_client.collection(FS_COLLECTION_EVENTS).stream():
            value = doc.to_dict()
            if value and "id" in value:
                events[value["id"]] = value

        for doc in fs_client.collection(FS_COLLECTION_TASKS).stream():
            value = doc.to_dict()
            if value and "id" in value:
                tasks[value["id"]] = value

        profile_doc = _profile_doc_ref().get()
        if profile_doc.exists:
            profile_data = profile_doc.to_dict() or {}
            user_profile.update(profile_data)
    except Exception as exc:
        print(f"[storage] Failed to load Firestore state: {exc}")


if USE_FIRESTORE:
    load_firestore_state()
