import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import pytest
from flask import Flask

# Import the generate_full_systematic_review route
from routes.gen_systematic_review import generate_full_systematic_review

app = Flask(__name__)
app.testing = True
import __main__
__main__.app = app
app.add_url_rule('/api/generate', view_func=generate_full_systematic_review, methods=['POST'])

@pytest.fixture
def client():
    return app.test_client()

def test_gen_systematic_review(client, monkeypatch):
    monkeypatch.setattr("gen_systematic_review.get_files", lambda id: {"paper1": "dummy_path"})
    monkeypatch.setattr("services.pinecone_service.search_pinecone", lambda query, paper_ids, section, top_k: ["dummy result"])
    monkeypatch.setattr("services.section_prompts_service.generate_background_section", 
                          lambda results, query, chunk_size, previous_sections: "Background")
    monkeypatch.setattr("services.section_prompts_service.generate_methods_section", 
                          lambda results, query, chunk_size, previous_sections: "Methods")
    monkeypatch.setattr("services.section_prompts_service.generate_results_section", 
                          lambda results, query, chunk_size, previous_sections: "Results")
    monkeypatch.setattr("services.section_prompts_service.generate_discussion_section", 
                          lambda results, query, chunk_size, previous_sections: "Discussion")
    monkeypatch.setattr("services.section_prompts_service.generate_conclusion_section", 
                          lambda results, query, chunk_size, previous_sections: "Conclusion")
    payload = {"prompt": "Test query", "id": "dummy_id"}
    response = client.post("/api/generate", json=payload)
    data = response.get_json()
    combined = data.get("systematic_review", "")
    for sec in ["Background", "Methods", "Results", "Discussion", "Conclusion"]:
        assert sec in combined

if __name__ == '__main__':
    client_instance = app.test_client()
    test_gen_systematic_review(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("gen_systematic_review test passed")