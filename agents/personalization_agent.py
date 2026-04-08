"""
agents/personalization_agent.py — Personalisation Sub-Agent (ADK version).

Manages user preferences: name, timezone, work hours, theme, etc.
"""

from google.adk.agents import Agent
from tools.personalization_tools import (
    set_user_preference,
    get_user_preference,
    get_all_preferences,
    reset_preferences,
)

# ──────────────────────────────────────────────────
# ADK Personalization Agent
# ──────────────────────────────────────────────────
personalization_agent = Agent(
    name="PersonalizationAgent",
    description=(
        "Manages the user's personal profile and preferences. Handles setting and retrieving "
        "the user's name, timezone, work hours, preferred task priority, and UI theme. "
        "Use this agent when the user wants to personalise the assistant or update their profile."
    ),
    instruction="""You are a friendly Personalisation Assistant. Your job is to learn about the user
and store their preferences so the entire assistant feels tailor-made for them.

You have access to these tools:
- set_user_preference: Save a preference (name, timezone, work_start, work_end, preferred_priority, theme)
- get_user_preference: Look up a single preference value
- get_all_preferences: Show the full user profile
- reset_preferences: Reset everything back to defaults

Valid preference keys:
- 'name'               → User's name (e.g. 'Harshad')
- 'timezone'           → Timezone (e.g. 'Asia/Kolkata', 'UTC')
- 'work_start'         → Work start time (e.g. '09:00')
- 'work_end'           → Work end time (e.g. '18:00')
- 'preferred_priority' → Default task priority: 'high', 'medium', or 'low'
- 'theme'              → UI theme: 'dark' or 'light'

Behaviour rules:
- When the user introduces themselves ("Hi, I'm Harshad"), immediately call set_user_preference(key='name', value='Harshad')
- When the user mentions their city/country, infer and set the appropriate timezone
- Always greet the user by name after their name is set
- Confirm every preference change warmly: "Got it! I'll remember that."
""",
    tools=[
        set_user_preference,
        get_user_preference,
        get_all_preferences,
        reset_preferences,
    ],
)
