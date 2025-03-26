import sys, os, pytest
from flask import Flask

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import __main__

app = Flask(__name__)
app.testing = True
__main__.app = app

from routes.save_history import save_history
app.add_url_rule("/api/save", view_func=save_history, methods=["POST"])

@pytest.fixture
def client():
    return app.test_client()

def test_save_history_success(client):
    prompt = "What are the effects of MSCs in treating COVID-19?"
    review = "Background: MSCs... Methods: ... Conclusion: ..."
    
    payload = {
        "user_id": [1],
        "prompt_id": 1,
        "prompt": prompt,
        "systematic_review": review
    }

    # ✅ 正常保存
    response = client.post("/api/save", json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert "message" in data
    assert "stored successfully" in data["message"].lower()

def test_save_history_missing_fields(client):
    # ❌ 缺少 prompt_id
    bad_payload = {
        "user_id": [1],
        "prompt": "Some prompt",
        "systematic_review": "Some result"
    }
    response = client.post("/api/save", json=bad_payload)
    assert response.status_code in (400, 422)

def test_save_history_wrong_types(client):
    # ❌ prompt_id 是字符串，数据库是整数
    bad_payload = {
        "user_id": ["1"],  # 应该是整数数组
        "prompt_id": "bad_id",
        "prompt": "Prompt here",
        "systematic_review": "Review here"
    }
    response = client.post("/api/save", json=bad_payload)
    assert response.status_code in (400, 422, 500)

def test_save_history_repeat_save(client):
    # ⏱️ 测试重复保存是否允许（取决于 DB 是否 UNIQUE）
    payload = {
        "user_id": [1],
        "prompt_id": 999,  # 特别指定一个测试 ID
        "prompt": "Repeat test",
        "systematic_review": "Repeat review"
    }

    response1 = client.post("/api/save", json=payload)
    response2 = client.post("/api/save", json=payload)

    assert response1.status_code == 200

    if response2.status_code == 200:
        assert "stored successfully" in response2.get_json()["message"].lower()
    else:
        assert response2.status_code in (400, 409, 500)  # 如果 DB 拒绝重复