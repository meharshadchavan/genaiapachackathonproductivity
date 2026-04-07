"""
tools/task_tools.py — Task Manager CRUD + Undo tools.

Supports create, list, get, update, complete, soft-delete, undo-delete, and summary.
"""

import copy
from datetime import datetime
import storage


# ──────────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────────

def create_task(
    title: str,
    priority: str = "medium",
    due_date: str = "",
    tags: str = "",
    notes: str = "",
) -> dict:
    """
    Create a new task in the to-do list.

    Args:
        title: Title or description of the task (e.g. 'Write project README').
        priority: Priority level — 'high', 'medium', or 'low' (default: 'medium').
        due_date: Optional due date in YYYY-MM-DD format (e.g. '2026-04-10').
        tags: Comma-separated tags for categorisation (e.g. 'work,coding,urgent').
        notes: Any additional notes or context for the task.

    Returns:
        dict with status and the created task details.
    """
    valid_priorities = {"high", "medium", "low"}
    if priority not in valid_priorities:
        priority = "medium"

    task_id = storage.new_id()
    task = {
        "id": task_id,
        "title": title,
        "status": "pending",
        "priority": priority,
        "due_date": due_date,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "notes": notes,
        "created_at": storage.now_iso(),
        "updated_at": storage.now_iso(),
        "completed_at": None,
    }
    storage.tasks[task_id] = task
    return {"status": "ok", "message": f"Task '{title}' created with priority={priority}.", "task": task}


# ──────────────────────────────────────────────────
# READ / LIST
# ──────────────────────────────────────────────────

def list_tasks(
    status_filter: str = "",
    priority_filter: str = "",
    tag_filter: str = "",
) -> dict:
    """
    List tasks with optional filters.

    Args:
        status_filter: Filter by status — 'pending', 'done', or '' for all.
        priority_filter: Filter by priority — 'high', 'medium', 'low', or '' for all.
        tag_filter: Filter by a specific tag (e.g. 'work'). Leave empty for all.

    Returns:
        dict with status and filtered list of tasks sorted by priority then due date.
    """
    priority_order = {"high": 0, "medium": 1, "low": 2}
    all_tasks = list(storage.tasks.values())

    if status_filter:
        all_tasks = [t for t in all_tasks if t["status"] == status_filter]
    if priority_filter:
        all_tasks = [t for t in all_tasks if t["priority"] == priority_filter]
    if tag_filter:
        all_tasks = [t for t in all_tasks if tag_filter in t["tags"]]

    all_tasks.sort(key=lambda t: (priority_order.get(t["priority"], 99), t.get("due_date") or "9999"))

    return {
        "status": "ok",
        "count": len(all_tasks),
        "tasks": all_tasks,
    }


def get_task(task_id: str) -> dict:
    """
    Get full details of a specific task by its ID.

    Args:
        task_id: The unique ID of the task (visible in list_tasks results).

    Returns:
        dict with status and task details, or an error if not found.
    """
    task = storage.tasks.get(task_id)
    if not task:
        return {"status": "error", "message": f"Task '{task_id}' not found."}
    return {"status": "ok", "task": task}


# ──────────────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────────────

def update_task(
    task_id: str,
    title: str = "",
    priority: str = "",
    due_date: str = "",
    tags: str = "",
    notes: str = "",
) -> dict:
    """
    Update one or more fields of an existing task.

    Args:
        task_id: The unique ID of the task to update.
        title: New title (leave empty to keep existing).
        priority: New priority — 'high', 'medium', or 'low' (leave empty to keep existing).
        due_date: New due date in YYYY-MM-DD format (leave empty to keep existing).
        tags: New comma-separated tags (leave empty to keep existing).
        notes: New notes (leave empty to keep existing).

    Returns:
        dict with status and updated task details.
    """
    task = storage.tasks.get(task_id)
    if not task:
        return {"status": "error", "message": f"Task '{task_id}' not found."}

    if title:
        task["title"] = title
    if priority in {"high", "medium", "low"}:
        task["priority"] = priority
    if due_date:
        task["due_date"] = due_date
    if tags:
        task["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
    if notes:
        task["notes"] = notes

    task["updated_at"] = storage.now_iso()
    return {"status": "ok", "message": f"Task '{task_id}' updated.", "task": task}


def complete_task(task_id: str) -> dict:
    """
    Mark a task as completed / done.

    Args:
        task_id: The unique ID of the task to mark as done.

    Returns:
        dict with status and confirmation.
    """
    task = storage.tasks.get(task_id)
    if not task:
        return {"status": "error", "message": f"Task '{task_id}' not found."}
    if task["status"] == "done":
        return {"status": "ok", "message": f"Task '{task['title']}' was already completed."}
    task["status"] = "done"
    task["completed_at"] = storage.now_iso()
    task["updated_at"] = storage.now_iso()
    return {"status": "ok", "message": f"✅ Task '{task['title']}' marked as done!", "task": task}


# ──────────────────────────────────────────────────
# SOFT DELETE + UNDO
# ──────────────────────────────────────────────────

def delete_task(task_id: str) -> dict:
    """
    Soft-delete a task (moves it to trash, recoverable via undo_delete_task).

    Args:
        task_id: The unique ID of the task to delete.

    Returns:
        dict with status and confirmation. The deletion can be undone.
    """
    task = storage.tasks.pop(task_id, None)
    if not task:
        return {"status": "error", "message": f"Task '{task_id}' not found."}
    storage.task_trash_stack.append(task)
    return {
        "status": "ok",
        "message": f"Task '{task['title']}' deleted (moved to trash). Say 'undo' to restore it.",
    }


def undo_delete_task() -> dict:
    """
    Undo the last task deletion, restoring the most recently deleted task.

    Returns:
        dict with status and the restored task details.
    """
    if not storage.task_trash_stack:
        return {"status": "error", "message": "No deleted tasks to restore."}
    task = storage.task_trash_stack.pop()
    storage.tasks[task["id"]] = task
    return {
        "status": "ok",
        "message": f"↩️ Task '{task['title']}' restored successfully!",
        "task": task,
    }


# ──────────────────────────────────────────────────
# ANALYTICS / SUMMARY
# ──────────────────────────────────────────────────

def get_task_summary() -> dict:
    """
    Get a productivity summary — counts of pending, done, high-priority, and overdue tasks.

    Returns:
        dict with status and a summary of the task board state.
    """
    all_tasks = list(storage.tasks.values())
    today = datetime.utcnow().strftime("%Y-%m-%d")

    pending = [t for t in all_tasks if t["status"] == "pending"]
    done = [t for t in all_tasks if t["status"] == "done"]
    high_priority = [t for t in pending if t["priority"] == "high"]
    overdue = [
        t for t in pending
        if t.get("due_date") and t["due_date"] < today
    ]

    return {
        "status": "ok",
        "summary": {
            "total": len(all_tasks),
            "pending": len(pending),
            "done": len(done),
            "high_priority_pending": len(high_priority),
            "overdue": len(overdue),
            "trash": len(storage.task_trash_stack),
        },
    }
