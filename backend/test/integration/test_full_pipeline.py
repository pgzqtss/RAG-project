import sys, os, shutil, pytest
from flask import Flask

# 导入项目根目录路径，支持 from routes.* 正确导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import __main__
app = Flask(__name__)
app.testing = True
__main__.app = app

# ✅ 路由按项目注册方式一致
from routes.upsert_vectors import init_pinecone
from routes.gen_systematic_review import generate_full_systematic_review
from routes.save_history import save_history

app.add_url_rule("/api/upsert", view_func=init_pinecone, methods=["POST"])
app.add_url_rule("/api/generate", view_func=generate_full_systematic_review, methods=["POST"])
app.add_url_rule("/api/save", view_func=save_history, methods=["POST"])

@pytest.fixture
def client():
    return app.test_client()

# ✅ 测试 PDF 路径
SAMPLE_PDFS = ["P1.1.pdf", "P1.2.pdf"]
SOURCE_DIR = "backend/papers/test_papers"
TARGET_DIR = "frontend/public/files/test_user"

def prepare_test_files():
    os.makedirs(TARGET_DIR, exist_ok=True)
    for pdf in SAMPLE_PDFS:
        src = os.path.join(SOURCE_DIR, pdf)
        dst = os.path.join(TARGET_DIR, pdf)
        assert os.path.exists(src), f"❌ 测试 PDF 缺失: {src}"
        shutil.copyfile(src, dst)

# ✅ 主流程：上传 → 生成 → 存储
def test_full_rag_pipeline(client):
    prepare_test_files()

    # Step 1: 上传并 upsert 向量
    response_upsert = client.post("/api/upsert", json={"id": "test_user"})
    assert response_upsert.status_code == 200
    assert "upserted" in response_upsert.get_json()["message"].lower()

    # Step 2: 提交查询 → 生成综述
    prompt = "What are the effects of MSCs in treating COVID-19?"
    response_generate = client.post("/api/generate", json={"id": "test_user", "prompt": prompt})
    assert response_generate.status_code == 200
    review = response_generate.get_json().get("systematic_review", "")
    assert any(k in review.lower() for k in ["background", "methods", "conclusion"])

    # Step 3: 存储历史记录
    response_save = client.post("/api/save", json={
        "user_id": [1],
        "prompt_id": 1,
        "prompt": prompt,
        "systematic_review": review
    })
    assert response_save.status_code == 200
    assert "stored successfully" in response_save.get_json()["message"].lower()

    print("✅ 集成流程：向量 → 生成 → 存储 测试通过")