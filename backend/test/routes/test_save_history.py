import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import pytest
from flask import Flask
import mysql.connector

from routes.save_history import save_history

app = Flask(__name__)
app.testing = True
import __main__
__main__.app = app
app.add_url_rule('/api/save', view_func=save_history, methods=['POST'])

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

def test_save_history(client, monkeypatch):
    monkeypatch.setattr("routes.save_history.connect_to_database", lambda: DummyConnection())
    payload = {
        "user_id": [1],
        "prompt_id":999999,
        "prompt": "dummy prompt",
        "systematic_review": "dummy review"
    }
    response = client.post("/api/save", json=payload)
    data = response.get_json()
    assert response.status_code in (200, 201)
    assert "stored successfully" in data.get("message", "").lower()

if __name__ == '__main__':
    client_instance = app.test_client()
    test_save_history(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("save_history test passed")
