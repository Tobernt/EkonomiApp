import importlib
from contextlib import closing
import os
from pathlib import Path
import secrets
import sqlite3
import tempfile
import unittest
from unittest.mock import patch


class LocalSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ekonomiapp-test-")
        self.environment = patch.dict(os.environ, {"EKONOMIAPP_DATA_DIR": self.temp.name})
        self.environment.start()
        self.secret_override = os.environ.pop("FLASK_SECRET_KEY", None)
        import settings
        self.settings = importlib.reload(settings)
        import setup_local
        self.setup = importlib.reload(setup_local)
        self.password = secrets.token_urlsafe(24)

    def tearDown(self):
        if self.secret_override is not None:
            os.environ["FLASK_SECRET_KEY"] = self.secret_override
        self.environment.stop()
        self.temp.cleanup()

    def test_missing_configuration_fails_closed(self):
        with self.assertRaises(RuntimeError):
            self.settings.load_session_key()

    def test_setup_preserves_existing_credentials_and_data(self):
        self.setup.initialize_local(self.password)
        paths = [self.settings.DATABASE_PATH, self.settings.PASSWORD_PATH, self.settings.SESSION_KEY_PATH]
        before = [path.read_bytes() for path in paths]
        self.setup.initialize_local("different password")
        self.assertEqual(before, [path.read_bytes() for path in paths])
        self.assertGreaterEqual(len(self.settings.load_session_key()), 32)
        self.assertNotIn(self.password.encode(), self.settings.PASSWORD_PATH.read_bytes())
        self.assertEqual(self.settings.DATABASE_PATH.parent, Path(self.temp.name))

    def test_environment_key_takes_precedence(self):
        self.setup.initialize_local(self.password)
        value = secrets.token_hex(32)
        with patch.dict(os.environ, {"FLASK_SECRET_KEY": value}):
            self.assertEqual(self.settings.load_session_key(), value)

    def test_login_and_transaction_use_local_database(self):
        self.setup.initialize_local(self.password)
        import database
        import helpers
        import logic
        import app
        for module in (database, helpers, logic, app):
            importlib.reload(module)
        app.app.config["TESTING"] = True
        client = app.app.test_client()
        self.assertEqual(client.get("/").status_code, 302)
        rejected = client.post("/start", data={"password": "wrong"})
        self.assertEqual(rejected.status_code, 302)
        self.assertTrue(rejected.location.endswith("/start"))
        self.assertEqual(client.get("/").status_code, 302)
        self.assertEqual(client.post("/start", data={"password": self.password}).status_code, 302)
        self.assertEqual(client.get("/").status_code, 200)
        fixture = self.settings.PROJECT_DIR / "fixtures" / "budget.sample.db"
        original = fixture.read_bytes()
        response = client.post("/ny", data={
            "date": "2026-01-01", "category": "Demo", "item_name": "Synthetic transaction",
            "description": "Regression fixture", "amount": "12", "type": "Utgift", "taxrate": "30"
        })
        self.assertEqual(response.status_code, 302)
        with closing(sqlite3.connect(self.settings.DATABASE_PATH)) as connection:
            count = connection.execute("SELECT COUNT(*) FROM info WHERE item_name = ?", ("Synthetic transaction",)).fetchone()[0]
        self.assertEqual(count, 1)
        self.assertEqual(fixture.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
