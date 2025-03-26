import sys, os, shutil, pytest
from flask import Flask

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import __main__

# 初始化 Flask 应用
app = Flask(__name__)
app.testing = True
__main__.app = app

# 注册路由
from routes.upsert_vectors import init_pinecone
app.add_url_rule("/api/upsert", view_func=init_pinecone, methods=["POST"])

@pytest.fixture
def client():
    return app.test_client()

SAMPLE_PDFS = ["P1.1.pdf"]
SOURCE_DIR = "backend/papers/test_papers"
TARGET_DIR = "frontend/public/files/test_user"

def prepare_test_files():
    os.makedirs(TARGET_DIR, exist_ok=True)
    for pdf in SAMPLE_PDFS:
        src = os.path.join(SOURCE_DIR, pdf)
        dst = os.path.join(TARGET_DIR, pdf)
        assert os.path.exists(src), f"测试 PDF 缺失：{src}"
        shutil.copyfile(src, dst)

def test_upsert_vector_success(client):
    prepare_test_files()
    response = client.post("/api/upsert", json={"id": "test_user"})
    assert response.status_code == 200
    assert "upserted" in response.get_json()["message"].lower()