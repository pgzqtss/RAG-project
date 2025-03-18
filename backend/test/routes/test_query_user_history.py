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

from routes.query_user_history import query_user_history
app.add_url_rule('/api/query_user_history', view_func=query_user_history, methods=['POST'])

@pytest.fixture
def client():
    return app.test_client()

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

def test_query_user_history(client, monkeypatch):
    monkeypatch.setattr("routes.query_user_history.connect_to_database", lambda: DummyConnection())
    payload = {"user_id": 1}
    response = client.post("/api/query_user_history", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert isinstance(data.get("result"), list)

if __name__ == '__main__':
    client_instance = app.test_client()
    test_query_user_history(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("query_user_history test passed")
