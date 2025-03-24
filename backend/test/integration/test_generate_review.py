import sys, os, pytest
from flask import Flask

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import __main__

app = Flask(__name__)
app.testing = True
__main__.app = app

from routes.gen_systematic_review import generate_full_systematic_review
app.add_url_rule("/api/generate", view_func=generate_full_systematic_review, methods=["POST"])

@pytest.fixture
def client():
    return app.test_client()

def test_generate_review_success(client):
    prompt = "What are the effects of MSCs in treating COVID-19?"
    response = client.post("/api/generate", json={"id": "test_user", "prompt": prompt})
    
    assert response.status_code == 200

    data = response.get_json()
    assert "systematic_review" in data
    review = data["systematic_review"]

    assert isinstance(review, str)
    assert len(review.strip()) > 50  # 不要太短
    
    assert any(k in review.lower() for k in ["background", "methods", "conclusion"])

def test_generate_review_missing_prompt(client):
    response = client.post("/api/generate", json={"id": "test_user"})
    assert response.status_code in (400, 422)

def test_generate_review_missing_user(client):
    response = client.post("/api/generate", json={"prompt": "missing user id test"})
    assert response.status_code in (400, 422)

def test_generate_review_empty_prompt(client):
    response = client.post("/api/generate", json={"id": "test_user", "prompt": ""})
    assert response.status_code in (400, 422, 500)

def test_generate_review_keywords_fallback(client):
    # 检查生成的 review 是否包含更多结构性关键词（可选增强）
    prompt = "Tell me about the role of AI in cancer diagnosis"
    response = client.post("/api/generate", json={"id": "test_user", "prompt": prompt})
    assert response.status_code == 200
    review = response.get_json().get("systematic_review", "").lower()

    possible_sections = ["background", "methods", "results", "discussion", "conclusion"]
    matched = [s for s in possible_sections if s in review]
    assert len(matched) >= 2  # 至少命中两个结构词段