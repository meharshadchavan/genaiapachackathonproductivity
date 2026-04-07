"""Quick smoke test — exercises every tool function directly."""
import sys
sys.path.insert(0, ".")

from tools.calendar_tools import create_event, list_events, update_event, delete_event, undo_last_calendar_action
from tools.task_tools import create_task, list_tasks, complete_task, delete_task, undo_delete_task, get_task_summary
from tools.personalization_tools import set_user_preference, get_all_preferences

PASS = "[PASS]"
FAIL = "[FAIL]"

def check(label, result, expected_status="ok"):
    ok = result.get("status") == expected_status
    print(f"  {PASS if ok else FAIL} {label}")
    if not ok:
        print(f"       => {result}")
    return ok

print("\n=== Calendar Tools ===")
r = create_event("Team Standup", "2026-04-08T09:00:00", duration_mins=30, attendees="harshad,sara")
check("create_event", r)
eid = r["event"]["id"]

r = list_events()
check("list_events", r)

r = update_event(eid, title="Daily Standup", location="Zoom")
check("update_event", r)

r = delete_event(eid)
check("delete_event", r)

r = undo_last_calendar_action()
check("undo_last_calendar_action", r)

print("\n=== Task Tools ===")
r = create_task("Write README", priority="high", due_date="2026-04-09", tags="work,docs")
check("create_task", r)
tid = r["task"]["id"]

r = list_tasks()
check("list_tasks", r)

r = list_tasks(priority_filter="high")
check("list_tasks (high priority filter)", r)

r = complete_task(tid)
check("complete_task", r)

r = create_task("Another task", priority="low")
check("create_task #2", r)
tid2 = r["task"]["id"]

r = delete_task(tid2)
check("delete_task (soft)", r)

r = undo_delete_task()
check("undo_delete_task", r)

r = get_task_summary()
check("get_task_summary", r)

print("\n=== Personalization Tools ===")
r = set_user_preference("name", "Harshad")
check("set_user_preference name", r)

r = set_user_preference("timezone", "Asia/Kolkata")
check("set_user_preference timezone", r)

r = get_all_preferences()
check("get_all_preferences", r)
print(f"       Profile => {r['profile']}")

print("\n=== All tests complete ===")
