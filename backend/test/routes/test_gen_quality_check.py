import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import pytest
from flask import Flask

# Import the generate_quality_check_graphs route
from routes.gen_quality_check import generate_quality_check_graphs

app = Flask(__name__)
app.testing = True
import __main__
__main__.app = app
app.add_url_rule('/api/quality_check', view_func=generate_quality_check_graphs, methods=['POST'])

@pytest.fixture
def client():
    return app.test_client()

def test_gen_quality_check(client, monkeypatch):
    # Simulate file reading and PDF-related functions
    monkeypatch.setattr("gen_quality_check.read_pdfs", lambda input_path: (["ref1.pdf"], ["doc1"]))
    monkeypatch.setattr("gen_quality_check.pdf_to_text", lambda output_path: "hypothesis")
    monkeypatch.setattr("gen_quality_check.CosineSimilarityChecker.calculate_similarity", lambda self: ([0.8], 0.8))
    monkeypatch.setattr("gen_quality_check.TFIDF.calculate_tfidf", lambda self: __import__('pandas').DataFrame({"word": [0.5]}).set_index("word"))
    monkeypatch.setattr("gen_quality_check.BLEUScorer.calculate_bleu", lambda self: [0.6])
    monkeypatch.setattr("gen_quality_check.save_and_plot_results", lambda author_counts, output_image, id: None)
    monkeypatch.setattr("gen_quality_check.generate_wordcloud", lambda areas, output_file, id: None)
    monkeypatch.setattr("gen_quality_check.store_pdf", lambda text, id: None)
    
    payload = {"id": "dummy_id"}
    response = client.post("/api/quality_check", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "generated successfully" in data.get("message", "").lower()

if __name__ == '__main__':
    client_instance = app.test_client()
    test_gen_quality_check(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("gen_quality_check test passed")