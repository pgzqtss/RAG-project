import sys
import os
import pytest
from flask import Flask

# 添加父目录到 sys.path，确保能够导入模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# 设置 Flask 应用，并赋值给 __main__.app（以便 routes 中使用 from __main__ import app）
import __main__
from flask import Flask
app = Flask(__name__)
app.testing = True
__main__.app = app

# 为避免循环依赖，我们在测试函数内部局部导入 generate_quality_check_graphs
@pytest.fixture
def client():
    return app.test_client()

def test_gen_quality_check(client, monkeypatch):
    # 覆盖文件操作相关函数，避免真实访问文件系统
    monkeypatch.setattr("routes.gen_quality_check.read_pdfs", lambda input_path: (["ref1.pdf"], ["doc1"]))
    monkeypatch.setattr("routes.gen_quality_check.pdf_to_text", lambda output_path: "hypothesis")
    monkeypatch.setattr("routes.gen_quality_check.CosineSimilarityChecker.calculate_similarity", lambda self: ([0.8], 0.8))
    monkeypatch.setattr("routes.gen_quality_check.TFIDF.calculate_tfidf",
                          lambda self: __import__('pandas').DataFrame({"testword": [0.5]}))
    monkeypatch.setattr("routes.gen_quality_check.BLEUScorer.calculate_bleu", lambda self: [0.6])
    # 覆盖 store_pdf（store_pdf 从 utils.store_as_pdf 导入）
    monkeypatch.setattr("utils.store_as_pdf.store_pdf", lambda text, id: None)
    monkeypatch.setattr("routes.gen_quality_check.generate_wordcloud", lambda areas, output_file, id: None)
    
    # 覆盖会访问文件系统的函数：
    monkeypatch.setattr("quality_check.author_num.process_pdfs", lambda folder: {})
    monkeypatch.setattr("quality_check.themetic_area.load_documents", lambda folder: [])
    # 如果 quality_check.author_num 中是用 "from os import listdir" 导入的，则覆盖该模块的 listdir
    monkeypatch.setattr("quality_check.author_num.os.listdir", lambda path: [])
    
    # 局部导入 generate_quality_check_graphs 以避免循环依赖问题
    from routes.gen_quality_check import generate_quality_check_graphs
    app.add_url_rule('/api/quality_check', view_func=generate_quality_check_graphs, methods=['POST'])
    
    payload = {"id": "dummy_id"}
    response = client.post("/api/quality_check", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    # 根据实际返回结果调整断言，此处假设返回信息中包含 "generated successfully"
    assert "generated successfully" in data.get("message", "").lower()

if __name__ == '__main__':
    client_instance = app.test_client()
    test_gen_quality_check(client_instance, monkeypatch=pytest.MonkeyPatch())
    print("gen_quality_check test passed")
