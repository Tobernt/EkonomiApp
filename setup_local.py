import getpass
import json
import secrets
import shutil

from werkzeug.security import generate_password_hash

from settings import DATA_DIR, DATABASE_PATH, PASSWORD_PATH, PROJECT_DIR, SESSION_KEY_PATH


def initialize_local(password=None):
    """Create local configuration without replacing existing data or credentials."""
    if not PASSWORD_PATH.exists() and not password:
        raise ValueError("A password is required for the first setup.")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATABASE_PATH.exists():
        shutil.copyfile(PROJECT_DIR / "fixtures" / "budget.sample.db", DATABASE_PATH)
    if not SESSION_KEY_PATH.exists():
        with SESSION_KEY_PATH.open("x", encoding="utf-8") as stream:
            stream.write(secrets.token_hex(32))
    if not PASSWORD_PATH.exists():
        with PASSWORD_PATH.open("x", encoding="utf-8") as stream:
            json.dump({"password": generate_password_hash(password)}, stream)


def main():
    password = None
    if not PASSWORD_PATH.exists():
        password = getpass.getpass("Choose a local login password: ")
        confirmation = getpass.getpass("Repeat password: ")
        if not password or password != confirmation:
            raise SystemExit("Passwords must match and cannot be empty.")
    initialize_local(password)
    print("Local setup is ready. Run python app.py to start the application.")


if __name__ == "__main__":
    main()
