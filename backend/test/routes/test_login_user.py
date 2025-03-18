import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import pytest
import bcrypt
from flask import Flask

import __main__
from flask import Flask
app = Flask(__name__)
app.testing = True
__main__.app = app

from routes.login_user import login
app.add_url_rule('/api/login', view_func=login, methods=['POST'])

@pytest.fixture
def client():
    return app.test_client()

def test_login(client, monkeypatch):
    password = "secret"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    class DummyCursor:
        def execute(self, query, params):
            pass
        def fetchone(self):
            return (1, hashed)
        def close(self):
            pass
    class DummyConnection:
        def cursor(self):
            return DummyCursor()
        def close(self):
            pass
    monkeypatch.setattr("routes.login_user.connect_to_database", lambda: DummyConnection())
    payload = {"username": "testuser", "password": "secret"}
    response = client.post("/api/login", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "logged in successfully" in data.get("message", "").lower()

if __name__ == '__main__':
    client_instance = app.test_client()
    test_login(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("login test passed")
