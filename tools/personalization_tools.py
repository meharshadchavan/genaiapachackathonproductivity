"""
tools/personalization_tools.py — User preference and personalisation tools.

Stores name, timezone, work hours, preferred priority, and theme.
"""

import storage

VALID_KEYS = {
    "name", "timezone", "work_start", "work_end",
    "preferred_priority", "theme"
}


def set_user_preference(key: str, value: str) -> dict:
    """
    Save a user preference or personalisation setting.

    Args:
        key: The preference to set. Valid keys:
             'name'               — User's name (e.g. 'Harshad')
             'timezone'           — Timezone string (e.g. 'Asia/Kolkata', 'UTC', 'America/New_York')
             'work_start'         — Work start time in HH:MM format (e.g. '09:00')
             'work_end'           — Work end time in HH:MM format (e.g. '18:00')
             'preferred_priority' — Default task priority: 'high', 'medium', or 'low'
             'theme'              — UI theme preference: 'dark' or 'light'
        value: The value to store for the given key.

    Returns:
        dict with status and confirmation.
    """
    if key not in VALID_KEYS:
        return {
            "status": "error",
            "message": f"Unknown preference key '{key}'. Valid keys: {sorted(VALID_KEYS)}",
        }
    storage.user_profile[key] = value
    storage.persist_profile()
    return {
        "status": "ok",
        "message": f"Preference '{key}' set to '{value}'.",
        "profile": storage.user_profile,
    }


def get_user_preference(key: str) -> dict:
    """
    Retrieve a specific user preference value.

    Args:
        key: The preference key to look up (e.g. 'name', 'timezone').

    Returns:
        dict with status and the value of the requested preference.
    """
    if key not in VALID_KEYS:
        return {
            "status": "error",
            "message": f"Unknown preference key '{key}'. Valid keys: {sorted(VALID_KEYS)}",
        }
    return {
        "status": "ok",
        "key": key,
        "value": storage.user_profile.get(key),
    }


def get_all_preferences() -> dict:
    """
    Retrieve the full user profile with all personalisation settings.

    Returns:
        dict with status and the complete user profile.
    """
    return {
        "status": "ok",
        "profile": storage.user_profile,
    }


def reset_preferences() -> dict:
    """
    Reset all user preferences to their default values.

    Returns:
        dict with status and the reset profile.
    """
    defaults = {
        "name": "User",
        "timezone": "Asia/Kolkata",
        "work_start": "09:00",
        "work_end": "18:00",
        "preferred_priority": "medium",
        "theme": "dark",
    }
    storage.user_profile.update(defaults)
    storage.persist_profile()
    return {
        "status": "ok",
        "message": "All preferences reset to defaults.",
        "profile": storage.user_profile,
    }
