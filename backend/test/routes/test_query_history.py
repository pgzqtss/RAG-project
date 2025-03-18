import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import pytest
from flask import Flask

import __main__
from flask import Flask
app = Flask(__name__)
app.testing = True
__main__.app = app

from routes.query_history import query
app.add_url_rule('/api/query', view_func=query, methods=['POST'])

@pytest.fixture
def client():
    return app.test_client()

class DummyCursor:
    def execute(self, query, params):
        pass
    def fetchone(self):
        return ("dummy prompt", "dummy review")
    def close(self):
        pass

class DummyConnection:
    def cursor(self):
        return DummyCursor()
    def commit(self):
        pass
    def close(self):
        pass

def test_query_history(client, monkeypatch):
    monkeypatch.setattr("routes.query_history.connect_to_database", lambda: DummyConnection())
    payload = {"prompt_id": "dummy_id"}
    response = client.post("/api/query", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert data.get("prompt") == "dummy prompt"
    assert data.get("systematic_review") == "dummy review"

if __name__ == '__main__':
    client_instance = app.test_client()
    test_query_history(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("query_history test passed")
