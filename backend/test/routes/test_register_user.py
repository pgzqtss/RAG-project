import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import pytest
import bcrypt
from flask import Flask
import mysql.connector

from routes.register_user import register

app = Flask(__name__)
app.testing = True
import __main__
__main__.app = app
app.add_url_rule('/api/register', view_func=register, methods=['POST'])

@pytest.fixture
def client():
    return app.test_client()

class DummyCursor:
    def execute(self, query, params):
        pass
    def close(self):
        pass

class DummyConnection:
    def cursor(self):
        return DummyCursor()
    def commit(self):
        pass
    def close(self):
        pass

def test_register_user(client, monkeypatch):
    # Option A: Set config.MYSQL_PASSWORD to a dummy value so that the test passes.
    monkeypatch.setattr("config.MYSQL_PASSWORD", "dummy")
    monkeypatch.setattr("routes.register_user.connect_to_database", lambda: DummyConnection())
    payload = {"username": "newuser", "password": "newpass"}
    response = client.post("/api/register", json=payload)
    data = response.get_json()
    assert response.status_code == 201
    assert "registered successfully" in data.get("message", "").lower()

if __name__ == '__main__':
    client_instance = app.test_client()
    test_register_user(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("register_user test passed")
