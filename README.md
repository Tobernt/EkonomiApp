# EkonomiApp

A Flask and SQLite budget-management prototype. It records income and expenses, groups transactions by category and month, and supports CSV/Excel import and Excel export.

The included database contains test data confirmed by the project owner. It is not an employer or customer dataset. See `fixtures/README.md`.

## Local setup

Use Python 3.10 or later. From the repository directory:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python setup_local.py
python app.py
```

Setup asks for a login password without displaying it, stores its hash locally, and generates a random session-signing key. Open localhost on port 5000 and log in with the password you chose.

The application uses `instance/budget.db`, copied from `fixtures/budget.sample.db` during setup. Password hashes, session keys, uploads and exports also stay in `instance/`, which is ignored by Git. Setup never replaces existing local data or credentials.

On Windows, `starta_budget_app.bat` performs setup and starts Waitress on localhost port 8000. The Flask development server is intended for local development.

## Configuration

- `FLASK_SECRET_KEY`: optional override for the local session key; use a randomly generated value of at least 32 characters. Changing it invalidates existing sessions.
- `EKONOMIAPP_DATA_DIR`: optional directory for runtime data; defaults to `instance/` beside the application.

No shared password or hardcoded signing key is used. Run setup before starting a WSGI server as well.

## Code guide

- `app.py`: Flask routes and request handling.
- `database.py`: SQLite queries and schema initialization.
- `logic.py`: transaction validation and file import.
- `helpers.py`: password verification.
- `settings.py` and `setup_local.py`: local data paths and first-time setup.
- `templates/`: server-rendered interface.

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests use temporary local directories. They cover setup, credential persistence, session-key configuration, login and a transaction write while checking that the committed sample database remains unchanged.

This is a single-user prototype for code review and local experimentation. It does not implement a production accounting workflow or a multi-user permission model.
