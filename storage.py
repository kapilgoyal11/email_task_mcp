"""
Read/write helpers for the local tasks.json file, using pathlib
(per rubric requirement — never os.path).
"""
import json
from pathlib import Path
from config import TASKS_FILE


def load_tasks() -> list[dict]:
    """Return the list of tasks, or an empty list if the file is
    missing or unreadable."""
    if not TASKS_FILE.exists():
        return []
    try:
        return json.loads(TASKS_FILE.read_text())
    except json.JSONDecodeError:
        return []


def save_tasks(tasks: list[dict]) -> None:
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))