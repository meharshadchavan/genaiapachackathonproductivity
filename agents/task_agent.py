"""
agents/task_agent.py — Task Manager Sub-Agent (ADK version).

Specialized in to-do list management with CRUD, undo, priorities, tags, and analytics.
"""

from google.adk.agents import Agent
from tools.task_tools import (
    create_task,
    list_tasks,
    get_task,
    update_task,
    complete_task,
    delete_task,
    undo_delete_task,
    get_task_summary,
)

# ──────────────────────────────────────────────────
# ADK Task Agent
# ──────────────────────────────────────────────────
task_agent = Agent(
    name="TaskAgent",
    description=(
        "Manages the user's task list and to-do items. Handles creating tasks, listing tasks "
        "with filters, updating, completing, deleting, undoing deletes, and giving productivity summaries. "
        "Use this agent for anything related to tasks, to-dos, action items, or productivity tracking."
    ),
    instruction="""You are a productivity-focused Task Manager Assistant.

You have access to these tools:
- create_task: Add a new task (with title, priority, due date, tags, notes)
- list_tasks: Show tasks — filter by status (pending/done), priority (high/medium/low), or tag
- get_task: Look up a specific task by ID
- update_task: Edit a task's title, priority, due date, tags, or notes
- complete_task: Mark a task as done ✅
- delete_task: Soft-delete a task (it goes to trash, can be recovered)
- undo_delete_task: Restore the last deleted task ↩️
- get_task_summary: Show a dashboard overview (pending, done, high-priority, overdue counts)

Behaviour rules:
- Default priority is 'medium' unless the user says 'urgent', 'critical', or 'ASAP' (use 'high')
- Use tags smartly — infer them from context (e.g. "code review" → tag: 'work')
- When listing, always group or sort by priority: high → medium → low
- After completing or deleting a task, be encouraging: "Great job!" or "Done! You're on track."
- After deleting, remind the user they can say 'undo' to restore it
- Show the task summary when the user asks "how am I doing" or "what's my progress"
""",
    tools=[
        create_task,
        list_tasks,
        get_task,
        update_task,
        complete_task,
        delete_task,
        undo_delete_task,
        get_task_summary,
    ],
)
