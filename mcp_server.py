"""
mcp_server.py — FastMCP Server exposing all tools via MCP protocol.

This server satisfies the hackathon's MCP requirement.
The Manager Agent connects to it as an MCP client via StdioServerParameters.

Run standalone for testing:
    python mcp_server.py
"""

from fastmcp import FastMCP

# Import all tool functions
from tools.calendar_tools import (
    create_event,
    list_events,
    get_event,
    update_event,
    delete_event,
    undo_last_calendar_action,
)
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
from tools.personalization_tools import (
    set_user_preference,
    get_user_preference,
    get_all_preferences,
    reset_preferences,
)

# ──────────────────────────────────────────────────
# Initialise FastMCP server
# ──────────────────────────────────────────────────
mcp = FastMCP(
    name="ProductivityAssistantMCP",
    instructions=(
        "MCP server for the Multi-Agent Productivity Assistant. "
        "Provides tools for Google Calendar management, task management, "
        "and user personalisation."
    ),
)

# ──────────────────────────────────────────────────
# Register Calendar tools
# ──────────────────────────────────────────────────
mcp.tool()(create_event)
mcp.tool()(list_events)
mcp.tool()(get_event)
mcp.tool()(update_event)
mcp.tool()(delete_event)
mcp.tool()(undo_last_calendar_action)

# ──────────────────────────────────────────────────
# Register Task Manager tools
# ──────────────────────────────────────────────────
mcp.tool()(create_task)
mcp.tool()(list_tasks)
mcp.tool()(get_task)
mcp.tool()(update_task)
mcp.tool()(complete_task)
mcp.tool()(delete_task)
mcp.tool()(undo_delete_task)
mcp.tool()(get_task_summary)

# ──────────────────────────────────────────────────
# Register Personalisation tools
# ──────────────────────────────────────────────────
mcp.tool()(set_user_preference)
mcp.tool()(get_user_preference)
mcp.tool()(get_all_preferences)
mcp.tool()(reset_preferences)


if __name__ == "__main__":
    print("🚀 Starting Productivity Assistant MCP Server (stdio)...")
    mcp.run(transport="stdio")
