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

from routes.query_user import query_user
app.add_url_rule('/api/query_user', view_func=query_user, methods=['POST'])

@pytest.fixture
def client():
    return app.test_client()

class DummyCursor:
    def execute(self, query, params):
        pass
    def fetchone(self):
        return (1,)
    def close(self):
        pass

class DummyConnectionUser:
    def cursor(self):
        return DummyCursor()
    def close(self):
        pass

def test_query_user(client, monkeypatch):
    monkeypatch.setattr("routes.query_user.connect_to_database", lambda: DummyConnectionUser())
    payload = {"username": "testuser"}
    response = client.post("/api/query_user", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "user_id" in data

if __name__ == '__main__':
    client_instance = app.test_client()
    test_query_user(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("query_user test passed")
