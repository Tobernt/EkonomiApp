# Sample data

`budget.sample.db` is the original prototype's SQLite test fixture: one category and two financial entries. The project owner confirmed that these are test data, not employer or customer records.

`setup_local.py` copies this file into the ignored `instance` directory on first setup. The application edits that local copy. Re-running setup preserves existing local data and credentials.

No shared login password or signing key is included. Setup asks for a local password and creates a random session-signing key.
