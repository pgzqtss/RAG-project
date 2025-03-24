import sys
import os
import pytest
from flask import Flask


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import __main__
from flask import Flask
app = Flask(__name__)
app.testing = True
__main__.app = app  

@pytest.fixture
def client():
    """Flask test client setup."""
    return app.test_client()

def test_gen_quality_check(client, monkeypatch):

    import matplotlib.backends.backend_pdf as backend_pdf
    
    class DummyPdfPages:
        def __init__(self, filename):
            print(f"Dummy PdfPages init with: {filename}")
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def savefig(self, *args, **kwargs):
            print("DummyPdfPages: savefig called.")
    
    monkeypatch.setattr("matplotlib.backends.backend_pdf.PdfPages", DummyPdfPages)


    monkeypatch.setattr("routes.gen_quality_check.read_pdfs", lambda input_path: (["ref1.pdf"], ["doc1"]))
    monkeypatch.setattr("routes.gen_quality_check.pdf_to_text", lambda output_path: "hypothesis")
    monkeypatch.setattr("routes.gen_quality_check.CosineSimilarityChecker.calculate_similarity",
                        lambda self: ([0.8], 0.8))
    monkeypatch.setattr("routes.gen_quality_check.TFIDF.calculate_tfidf",
                        lambda self: __import__('pandas').DataFrame({"testword": [0.5]}))
    monkeypatch.setattr("routes.gen_quality_check.BLEUScorer.calculate_bleu", lambda self: [0.6])
    monkeypatch.setattr("utils.store_as_pdf.store_pdf", lambda text, id: None)
    monkeypatch.setattr("routes.gen_quality_check.generate_wordcloud", lambda areas, output_file, id: None)
    monkeypatch.setattr("quality_check.author_num.process_pdfs", lambda folder: {})
    monkeypatch.setattr("quality_check.themetic_area.load_documents", lambda folder: [])
    monkeypatch.setattr("quality_check.author_num.os.listdir", lambda path: [])


    from routes.gen_quality_check import generate_quality_check_graphs
    app.add_url_rule('/api/quality_check', view_func=generate_quality_check_graphs, methods=['POST'])

    payload = {"id": "dummy_id"}
    response = client.post("/api/quality_check", json=payload)
    data = response.get_json()


    assert response.status_code == 200, f"Got {response.status_code} instead of 200"
    assert data is not None, "Response JSON is None"
    assert "generated successfully" in data.get("message", "").lower()

    print("\n test_gen_quality_check passed successfully!")

if __name__ == '__main__':
    client_instance = app.test_client()
    test_gen_quality_check(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("test_gen_quality_check done.")