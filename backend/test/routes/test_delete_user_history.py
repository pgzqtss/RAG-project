import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import pytest
from flask import Flask

# Dummy classes to simulate database behavior
class DummyCursor:
    def execute(self, query, params):
        pass
    def fetchall(self):
        return [("dummy result",)]
    def close(self):
        pass

class DummyConnection:
    def cursor(self):
        return DummyCursor()
    def commit(self):
        pass
    def close(self):
        pass

# Import the delete_user_history route
from routes.delete_user_history import delete_user_history

# Create a Flask app and register the route
app = Flask(__name__)
app.testing = True
import __main__
__main__.app = app
app.add_url_rule('/api/delete_user_history', view_func=delete_user_history, methods=['POST'])

@pytest.fixture
def client():
    return app.test_client()

def test_delete_user_history(client, monkeypatch):
    monkeypatch.setattr("delete_user_history.connect_to_database", lambda: DummyConnection())
    payload = {"prompt_id": "dummy_id"}
    response = client.post("/api/delete_user_history", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "systematic review successfully" in data.get("message", "").lower()

if __name__ == '__main__':
    client_instance = app.test_client()
    test_delete_user_history(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("delete_user_history test passed")
