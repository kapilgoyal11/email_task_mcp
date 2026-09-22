"""
Loads configuration and secrets from a local .env file.
Uses python-dotenv + pathlib so nothing is hardcoded and nothing
relies on OS-level environment variables.
"""
from pathlib import Path
from dotenv import load_dotenv
import os

ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# .strip() guards against trailing whitespace/newlines from copy-pasting
# credentials into .env
SMTP_EMAIL = (os.getenv("SMTP_EMAIL") or "").strip()
SMTP_APP_PASSWORD = (os.getenv("SMTP_APP_PASSWORD") or "").strip()

TASKS_FILE = Path(__file__).parent / "tasks.json"