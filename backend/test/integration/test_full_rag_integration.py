import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import shutil
import pytest
from flask import Flask

# 设置 app 测试环境
import __main__
app = Flask(__name__)
app.testing = True
__main__.app = app

# 路由导入保持不变 ✅
from routes.upsert_vectors import init_pinecone
from routes.gen_systematic_review import generate_full_systematic_review
from routes.save_history import save_history

app.add_url_rule("/api/upsert", view_func=init_pinecone, methods=["POST"])
app.add_url_rule("/api/generate", view_func=generate_full_systematic_review, methods=["POST"])
app.add_url_rule("/api/save", view_func=save_history, methods=["POST"])

@pytest.fixture
def client():
    return app.test_client()

# ✅ 设置测试文件来源 & 目标
SAMPLE_PDFS = ["P1.1.pdf", "P1.2.pdf"]
SOURCE_DIR = "backend/papers/test_papers"
TARGET_DIR = "frontend/public/files/test_user"

def prepare_test_files():
    os.makedirs(TARGET_DIR, exist_ok=True)
    for pdf in SAMPLE_PDFS:
        shutil.copyfile(os.path.join(SOURCE_DIR, pdf), os.path.join(TARGET_DIR, pdf))

# ✅ 集成测试主流程
def test_full_rag_pipeline(client):
    prepare_test_files()

    # Step 1: 上传向量
    response_upsert = client.post("/api/upsert", json={"id": "test_user"})
    assert response_upsert.status_code == 200
    assert "upserted" in response_upsert.get_json()["message"].lower()

    # Step 2: 生成系统综述
    prompt = "What are the effects of MSCs in treating COVID-19?"
    response_generate = client.post("/api/generate", json={"id": "test_user", "prompt": prompt})
    assert response_generate.status_code == 200
    review = response_generate.get_json().get("systematic_review", "")
    assert any(key in review.lower() for key in ["background", "methods", "conclusion"])

    # Step 3: 保存综述历史
    response_save = client.post("/api/save", json={
        "user_id": [1],
        "prompt_id":1,
        "prompt": prompt,
        "systematic_review": review
    })
    assert response_save.status_code == 200
    assert "stored successfully" in response_save.get_json()["message"].lower()

# ✅ 让它也支持直接运行（调试用）
if __name__ == '__main__':
    client_instance = app.test_client()
    test_full_rag_pipeline(client_instance)
    print("✅ test_full_rag_pipeline passed")