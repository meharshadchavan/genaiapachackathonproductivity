"""
agents/calendar_agent.py — Calendar Sub-Agent (ADK version).

Specialized in all things scheduling: meetings, events, deadlines.
Delegates real work to calendar_tools functions.
"""

from google.adk.agents import Agent
from tools.calendar_tools import (
    create_event,
    list_events,
    get_event,
    update_event,
    delete_event,
    undo_last_calendar_action,
)

# ──────────────────────────────────────────────────
# ADK Calendar Agent
# ──────────────────────────────────────────────────
calendar_agent = Agent(
    name="CalendarAgent",
    description=(
        "Handles all calendar and scheduling tasks: creating meetings, listing upcoming events, "
        "updating event details, deleting events, and undoing calendar changes. "
        "Use this agent for anything related to scheduling, appointments, or meetings."
    ),
    instruction="""You are a smart Calendar Assistant. Your job is to manage the user's schedule.

You have access to these tools:
- create_event: Schedule a new meeting or event
- list_events: Show upcoming events (can filter by date)
- get_event: Look up a specific event by ID
- update_event: Modify an existing event's details
- delete_event: Remove an event from the calendar
- undo_last_calendar_action: Restore the last deleted or modified event

Personalisation rules:
- When listing events, format dates in a human-friendly way (e.g. "Tuesday, 8 April 2026 at 3:00 PM")
- If the user says "tomorrow", "next Monday", etc., interpret relative to today's date
- Always confirm after creating or deleting an event
- After deleting, remind the user they can undo

IMPORTANT: If you don't know the current date/time, ask the user to specify it or use the date in their message.
""",
    tools=[
        create_event,
        list_events,
        get_event,
        update_event,
        delete_event,
        undo_last_calendar_action,
    ],
)
