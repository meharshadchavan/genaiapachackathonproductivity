"""
tools/calendar_tools.py — Google Calendar CRUD + Undo tools.

All functions return a dict with {"status": "ok"|"error", ...payload}.
The LLM reads docstrings to know when to call each tool.
"""

import copy
from datetime import datetime, timedelta
import storage


# ──────────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────────

def create_event(
    title: str,
    date_time: str,
    duration_mins: int = 60,
    description: str = "",
    attendees: str = "",
    location: str = "",
) -> dict:
    """
    Create a new calendar event / meeting.

    Args:
        title: Title of the event (e.g. 'Team Standup').
        date_time: Start date and time in ISO 8601 format (e.g. '2026-04-08T15:00:00').
        duration_mins: Duration in minutes (default 60).
        description: Optional description or agenda for the meeting.
        attendees: Comma-separated list of attendee emails or names.
        location: Optional location or meeting link.

    Returns:
        dict with status and the created event details.
    """
    try:
        # Validate datetime
        start_dt = datetime.fromisoformat(date_time.replace("Z", ""))
        end_dt = start_dt + timedelta(minutes=duration_mins)

        event_id = storage.new_id()
        event = {
            "id": event_id,
            "title": title,
            "date_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "duration_mins": duration_mins,
            "description": description,
            "attendees": [a.strip() for a in attendees.split(",") if a.strip()],
            "location": location,
            "created_at": storage.now_iso(),
            "updated_at": storage.now_iso(),
        }
        storage.events[event_id] = event
        return {"status": "ok", "message": f"Event '{title}' created.", "event": event}
    except ValueError as e:
        return {"status": "error", "message": f"Invalid date_time format: {e}"}


# ──────────────────────────────────────────────────
# READ / LIST
# ──────────────────────────────────────────────────

def list_events(date_filter: str = "") -> dict:
    """
    List all upcoming calendar events, optionally filtered by a date prefix.

    Args:
        date_filter: Optional date prefix to filter by (e.g. '2026-04-08' for a specific day,
                     or '2026-04' for the whole month). Leave empty to list all events.

    Returns:
        dict with status and list of events sorted by date.
    """
    all_events = list(storage.events.values())
    if date_filter:
        all_events = [e for e in all_events if e["date_time"].startswith(date_filter)]
    all_events.sort(key=lambda e: e["date_time"])
    return {
        "status": "ok",
        "count": len(all_events),
        "events": all_events,
    }


def get_event(event_id: str) -> dict:
    """
    Get the full details of a specific calendar event by its ID.

    Args:
        event_id: The unique ID of the event (visible in list_events results).

    Returns:
        dict with status and event details, or an error if not found.
    """
    event = storage.events.get(event_id)
    if not event:
        return {"status": "error", "message": f"Event with id '{event_id}' not found."}
    return {"status": "ok", "event": event}


# ──────────────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────────────

def update_event(
    event_id: str,
    title: str = "",
    date_time: str = "",
    duration_mins: int = 0,
    description: str = "",
    attendees: str = "",
    location: str = "",
) -> dict:
    """
    Update one or more fields of an existing calendar event.

    Args:
        event_id: The unique ID of the event to update.
        title: New title (leave empty to keep existing).
        date_time: New start date_time in ISO 8601 format (leave empty to keep existing).
        duration_mins: New duration in minutes (0 to keep existing).
        description: New description (leave empty to keep existing).
        attendees: New comma-separated attendees list (leave empty to keep existing).
        location: New location (leave empty to keep existing).

    Returns:
        dict with status and updated event details.
    """
    event = storage.events.get(event_id)
    if not event:
        return {"status": "error", "message": f"Event '{event_id}' not found."}

    # Push copy to undo stack before modifying
    storage.calendar_trash_stack.append(("update", copy.deepcopy(event)))

    if title:
        event["title"] = title
    if date_time:
        try:
            start_dt = datetime.fromisoformat(date_time.replace("Z", ""))
            dur = duration_mins if duration_mins > 0 else event["duration_mins"]
            event["date_time"] = start_dt.isoformat()
            event["end_time"] = (start_dt + timedelta(minutes=dur)).isoformat()
        except ValueError as e:
            return {"status": "error", "message": f"Invalid date_time: {e}"}
    if duration_mins > 0:
        event["duration_mins"] = duration_mins
        try:
            start_dt = datetime.fromisoformat(event["date_time"])
            event["end_time"] = (start_dt + timedelta(minutes=duration_mins)).isoformat()
        except Exception:
            pass
    if description:
        event["description"] = description
    if attendees:
        event["attendees"] = [a.strip() for a in attendees.split(",") if a.strip()]
    if location:
        event["location"] = location

    event["updated_at"] = storage.now_iso()
    return {"status": "ok", "message": f"Event '{event_id}' updated.", "event": event}


# ──────────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────────

def delete_event(event_id: str) -> dict:
    """
    Delete a calendar event by ID. The deleted event is saved for undo.

    Args:
        event_id: The unique ID of the event to delete.

    Returns:
        dict with status and confirmation message.
    """
    event = storage.events.pop(event_id, None)
    if not event:
        return {"status": "error", "message": f"Event '{event_id}' not found."}
    storage.calendar_trash_stack.append(("delete", event))
    return {"status": "ok", "message": f"Event '{event['title']}' deleted. You can undo this action."}


# ──────────────────────────────────────────────────
# UNDO
# ──────────────────────────────────────────────────

def undo_last_calendar_action() -> dict:
    """
    Undo the last calendar action (delete or update). Restores the previous state.

    Returns:
        dict with status and details of the restored event.
    """
    if not storage.calendar_trash_stack:
        return {"status": "error", "message": "Nothing to undo in calendar."}

    action, event = storage.calendar_trash_stack.pop()
    storage.events[event["id"]] = event
    return {
        "status": "ok",
        "message": f"Undo successful. Event '{event['title']}' restored (action: {action}).",
        "event": event,
    }
