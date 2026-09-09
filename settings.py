import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("EKONOMIAPP_DATA_DIR", PROJECT_DIR / "instance"))
DATABASE_PATH = DATA_DIR / "budget.db"
PASSWORD_PATH = DATA_DIR / "key.json"
SESSION_KEY_PATH = DATA_DIR / "session.key"


def load_session_key():
    value = os.environ.get("FLASK_SECRET_KEY")
    if not value:
        try:
            value = SESSION_KEY_PATH.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            raise RuntimeError("Run python setup_local.py before starting the app.") from None
    if len(value) < 32:
        raise RuntimeError("The session-signing key must contain at least 32 characters.")
    return value
