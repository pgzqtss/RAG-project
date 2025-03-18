import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import pytest
from flask import Flask

from routes.upsert_vectors import init_pinecone

app = Flask(__name__)
app.testing = True
import __main__
__main__.app = app
app.add_url_rule('/api/upsert', view_func=init_pinecone, methods=['POST'])

@pytest.fixture
def client():
    return app.test_client()

def test_upsert_vectors(client, monkeypatch):
    monkeypatch.setattr("routes.upsert_vectors.initialise_pinecone", lambda: None)
    monkeypatch.setattr("routes.upsert_vectors.process_and_store_all_pdfs", lambda id: (5, {"paper1": "dummy_path"}))
    monkeypatch.setattr("routes.upsert_vectors.check_all_upserted_chunks", lambda files, chunks_count: None)
    payload = {"id": "dummy_id"}
    response = client.post("/api/upsert", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "upserted" in data.get("message", "").lower()

if __name__ == '__main__':
    client_instance = app.test_client()
    test_upsert_vectors(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("upsert_vectors test passed")
