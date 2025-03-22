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

from routes.gen_systematic_review import generate_full_systematic_review


app.add_url_rule('/api/generate', view_func=generate_full_systematic_review, methods=['POST'])

@pytest.fixture
def client():
    return app.test_client()

def test_generate_full_systematic_review(client, monkeypatch):
    monkeypatch.setattr(
        "routes.gen_systematic_review.get_files",
        lambda id: {"paperA": "dummy_path1", "paperB": "dummy_path2"}
    )

    monkeypatch.setattr(
        "routes.gen_systematic_review.search_pinecone",
        lambda query, paper_ids, section, top_k: [f"{section}-dummy-result"]
    )

    monkeypatch.setattr(
        "routes.gen_systematic_review.store_pdf",
        lambda text, id: print(f"store_pdf called with text: {text[:30]}..., id: {id}")
    )

    monkeypatch.setattr(
        "routes.gen_systematic_review.generate_background_section",
        lambda results, query, chunk_size, previous_sections: "Background---"
    )
    monkeypatch.setattr(
        "routes.gen_systematic_review.generate_methods_section",
        lambda results, query, chunk_size, previous_sections: "Methods---"
    )
    monkeypatch.setattr(
        "routes.gen_systematic_review.generate_results_section",
        lambda results, query, chunk_size, previous_sections: "Results---"
    )
    monkeypatch.setattr(
        "routes.gen_systematic_review.generate_discussion_section",
        lambda results, query, chunk_size, previous_sections: "Discussion---"
    )
    monkeypatch.setattr(
        "routes.gen_systematic_review.generate_conclusion_section",
        lambda results, query, chunk_size, previous_sections: "Conclusion---"
    )

    # 5) mock _get_fixed_limit_previous_sections
    monkeypatch.setattr(
        "routes.gen_systematic_review._get_fixed_limit_previous_sections",
        lambda sr, limit: ["TRUNCATED"]
    )

    payload = {"prompt": "Test query", "id": "dummy_id"}
    response = client.post("/api/generate", json=payload)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.get_json()
    combined = data.get("systematic_review", "")


    for sec in ["Background", "Methods", "Results", "Discussion", "Conclusion"]:
        assert sec in combined, f"{sec} not found in combined text"

    print("\n✅ test_generate_systematic_review passed successfully!")

if __name__ == '__main__':
    client_instance = app.test_client()
    test_generate_full_systematic_review(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("test_generate_full_systematic_review done.")
