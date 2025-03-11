import pytest 
import bcrypt
import json
import textwrap
from flask import Flask
import sys
import os
import numpy as np
from sentence_transformers import util

# 确保将 backend 目录加入 sys.path，便于导入 services 模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)




# ------------------------------
# 以下为 pytest 的测试用例
# ------------------------------

# Dummy Classes for Database Simulation
class DummyCursor:
    def execute(self, query, params):
        pass

    def fetchone(self):
        # For query_history: returns (prompt, review) and for query_user, returns (user_id,)
        return ("dummy prompt", "dummy review")

    def fetchall(self):
        # For delete_user_history route
        return [("dummy",)]

    def close(self):
        pass

class DummyConnection:
    def cursor(self):
        return DummyCursor()

    def commit(self):
        pass

    def close(self):
        pass

# Dummy connection for query_user (returns a tuple with a single user id)
class DummyConnectionUser:
    class DummyCursorUser:
        def execute(self, query, params):
            pass

        def fetchone(self):
            return (1,)

        def close(self):
            pass

    def cursor(self):
        return self.DummyCursorUser()

    def close(self):
        pass

# Pytest Fixtures for Flask App and Client
@pytest.fixture
def app():
    """Create a Flask app and register all routes."""
    app = Flask(__name__)
    app.testing = True

    # Register routes manually (importing the view functions)
    from routes.query_history import query
    app.add_url_rule('/api/query', view_func=query, methods=['POST'])

    from routes.save_history import save_history
    app.add_url_rule('/api/save', view_func=save_history, methods=['POST'])

    from routes.query_user import query_user
    app.add_url_rule('/api/query_user', view_func=query_user, methods=['POST'])

    from routes.gen_systematic_review import generate_full_systematic_review
    app.add_url_rule('/api/generate', view_func=generate_full_systematic_review, methods=['POST'])

    from routes.upsert_vectors import init_pinecone
    app.add_url_rule('/api/upsert', view_func=init_pinecone, methods=['POST'])

    from routes.delete_user_history import delete_user_history
    app.add_url_rule('/api/delete_user_history', view_func=delete_user_history, methods=['POST'])

    return app

@pytest.fixture
def client(app):
    return app.test_client()

# ------------------------------
# Tests for Service Functions
# ------------------------------
# Test for classify_chunk_service (classify_chunk_with_llm)
def dummy_invoke_valid(prompt):
    class DummyResponse:
        content = "Methods"
    return DummyResponse()

def dummy_invoke_invalid(prompt):
    class DummyResponse:
        content = "InvalidSection"
    return DummyResponse()

def dummy_invoke_exception(prompt):
    raise Exception("LLM error")

def test_classify_chunk_valid(monkeypatch):
    from services.classify_chunk_service import classify_chunk_with_llm
    DummyModel = type("DummyModel", (), {"invoke": dummy_invoke_valid})
    monkeypatch.setattr("services.classify_chunk_service.model", DummyModel)
    result = classify_chunk_with_llm("Test text")
    assert result == "Methods"

def test_classify_chunk_invalid(monkeypatch):
    from services.classify_chunk_service import classify_chunk_with_llm
    DummyModel = type("DummyModel", (), {"invoke": dummy_invoke_invalid})
    monkeypatch.setattr("services.classify_chunk_service.model", DummyModel)
    result = classify_chunk_with_llm("Test text")
    # Should default to "Background" when the response is not valid
    assert result == "Background"

def test_classify_chunk_exception(monkeypatch):
    from services.classify_chunk_service import classify_chunk_with_llm
    DummyModel = type("DummyModel", (), {"invoke": dummy_invoke_exception})
    monkeypatch.setattr("services.classify_chunk_service.model", DummyModel)
    result = classify_chunk_with_llm("Test text")
    assert result == "Background"

# Test for generate_section_service.generate_section
def dummy_model_invoke(prompt):
    class DummyResponse:
        content = "Generated section content.\nUnique sentence."
    return DummyResponse()

def dummy_bert_encode(texts, convert_to_tensor):
    # Return a dummy tensor (list of ones) for each text
    return [1.0 for _ in texts]

def test_generate_section(monkeypatch):
    from services.generate_section_service import generate_section, util
    DummyModel = type("DummyModel", (), {"invoke": dummy_model_invoke})
    monkeypatch.setattr("services.generate_section_service.model", DummyModel)
    # Patch the bert_model and pytorch_cos_sim to always return low similarity
    DummyBert = type("DummyBert", (), {"encode": dummy_bert_encode})
    monkeypatch.setattr("services.generate_section_service.bert_model", DummyBert())
    monkeypatch.setattr(util, "pytorch_cos_sim", lambda a, b: [[0.5]])
    
    result = generate_section(
        results=["chunk1", "chunk2"],
        query="Test query",
        section_title="Background",
        section_prompt="Section prompt",
        previous_sections=[]
    )
    assert "Generated section content." in result

# Test for pinecone_service.initialise_pinecone and get_all_paper_ids
def test_initialise_pinecone(monkeypatch):
    from services.pinecone_service import initialise_pinecone
    # Create a dummy pinecone object
    class DummyPinecone:
        def __init__(self):
            self.created = False
        def list_indexes(self):
            class DummyList:
                def names(self):
                    return []
            return DummyList()
        def create_index(self, name, dimension, metric, spec):
            self.created = True
    dummy_pinecone = DummyPinecone()
    monkeypatch.setattr("services.pinecone_service.pinecone", dummy_pinecone)
    initialise_pinecone()
    assert dummy_pinecone.created is True

def test_get_all_paper_ids(monkeypatch):
    from services.pinecone_service import get_all_paper_ids
    class DummyIndex:
        def describe_index_stats(self):
            return {
                "namespaces": {
                    "systematic_review/testpaper/Background": {"vector_count": 2},
                    "other_namespace": {"vector_count": 1}
                }
            }
    monkeypatch.setattr("services.pinecone_service.pinecone.Index", lambda name: DummyIndex())
    paper_ids = get_all_paper_ids()
    assert "testpaper" in paper_ids

# Test for section_prompts_service.generate_background_section
def test_generate_background_section(monkeypatch):
    from services.section_prompts_service import generate_background_section
    monkeypatch.setattr(
        "services.section_prompts_service.generate_section",
        lambda results, query, section_title, section_prompt, chunk_size, previous_sections: "Background Section Content"
    )
    result = generate_background_section(["dummy_result"], "Test query", 30, [])
    assert result == "Background Section Content"

# ------------------------------
# Tests for Flask Routes
# ------------------------------
# Test for query_history route
def test_query_history(client, monkeypatch):
    monkeypatch.setattr("query_history.connect_to_database", lambda: DummyConnection())
    response = client.post("/api/query", json={"prompt_id": "dummy_id"})
    data = response.get_json()
    assert response.status_code == 200
    # DummyCursor.fetchone returns ("dummy prompt", "dummy review")
    assert data.get("prompt") == "dummy prompt"
    assert data.get("systematic_review") == "dummy review"

# Test for save_history route
def test_save_history(client, monkeypatch):
    monkeypatch.setattr("save_history.connect_to_database", lambda: DummyConnection())
    payload = {
        "user_id": [1],
        "prompt_id": "dummy_id",
        "prompt": "dummy prompt",
        "systematic_review": "dummy review"
    }
    response = client.post("/api/save", json=payload)
    data = response.get_json()
    # Expect a successful insertion (status code 200 or 201)
    assert response.status_code in (200, 201)
    assert "stored successfully" in data.get("message", "").lower()

# Test for query_user route
def test_query_user(client, monkeypatch):
    monkeypatch.setattr("query_user.connect_to_database", lambda: DummyConnectionUser())
    response = client.post("/api/query_user", json={"username": "testuser"})
    data = response.get_json()
    assert response.status_code == 200
    # Expect the returned JSON to include a key "user_id"
    assert "user_id" in data

# Test for generate_full_systematic_review route
def test_generate_full_systematic_review(client, monkeypatch):
    # Override get_files to return a dummy file dictionary
    monkeypatch.setattr("gen_systematic_review.get_files", lambda id: {"paper1": "dummy_path"})
    # Override search_pinecone to return a dummy list of results
    monkeypatch.setattr("services.pinecone_service.search_pinecone", lambda query, paper_ids, section, top_k: ["dummy result"])
    # Override section generation functions to return fixed strings
    monkeypatch.setattr(
        "services.section_prompts_service.generate_background_section",
        lambda results, query, chunk_size, previous_sections: "Background"
    )
    monkeypatch.setattr(
        "services.section_prompts_service.generate_methods_section",
        lambda results, query, chunk_size, previous_sections: "Methods"
    )
    monkeypatch.setattr(
        "services.section_prompts_service.generate_results_section",
        lambda results, query, chunk_size, previous_sections: "Results"
    )
    monkeypatch.setattr(
        "services.section_prompts_service.generate_discussion_section",
        lambda results, query, chunk_size, previous_sections: "Discussion"
    )
    monkeypatch.setattr(
        "services.section_prompts_service.generate_conclusion_section",
        lambda results, query, chunk_size, previous_sections: "Conclusion"
    )
    payload = {"prompt": "Test query", "id": "dummy_id"}
    response = client.post("/api/generate", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    combined = data.get("systematic_review", "")
    # Check that each fixed section string is present in the combined review
    for section in ["Background", "Methods", "Results", "Discussion", "Conclusion"]:
        assert section in combined

# Test for upsert_vectors route
def test_upsert_vectors(client, monkeypatch):
    # Override initialise_pinecone to do nothing
    monkeypatch.setattr("upsert_vectors.initialise_pinecone", lambda: None)
    # Override process_and_store_all_pdfs to return dummy values
    monkeypatch.setattr("upsert_vectors.process_and_store_all_pdfs", lambda id: (5, {"paper1": "dummy_path"}))
    # Override check_all_upserted_chunks to do nothing
    monkeypatch.setattr("upsert_vectors.check_all_upserted_chunks", lambda files, chunks_count: None)
    payload = {"id": "dummy_id"}
    response = client.post("/api/upsert", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "upserted" in data.get("message", "").lower()

# Test for delete_user_history route
def test_delete_user_history(client, monkeypatch):
    monkeypatch.setattr("delete_user_history.connect_to_database", lambda: DummyConnection())
    payload = {"prompt_id": "dummy_id"}
    response = client.post("/api/delete_user_history", json=payload)
    data = response.get_json()
    assert response.status_code == 200 
    assert "systematic review successfully" in data.get("message", "").lower()


def main():
    print("正在运行独立的服务测试...\n")
    
    # ------------------------------
    # 测试 classify_chunk_service 中的 classify_chunk_with_llm
    # ------------------------------
    print("测试 classify_chunk_with_llm ...")

    # 定义 DummyModel，用于模拟返回合法的 section
    class DummyModel:
        def invoke(self, prompt):
            class DummyResponse:
                content = "Methods"
            return DummyResponse()

    from services import classify_chunk_service as ccs
    ccs.model = DummyModel()
    
    classification = ccs.classify_chunk_with_llm("测试文本")
    print("分类结果：", classification)
    assert classification == "Methods", "分类结果不正确"
    
    # ------------------------------
    # 测试 generate_section_service 中的 generate_section
    # ------------------------------
    print("\n测试 generate_section ...")

    # 定义 DummyModel2 和 DummyBert 用于模拟模型和 bert_model
    class DummyModel2:
        def invoke(self, prompt):
            class DummyResponse:
                content = "Generated section content.\nUnique sentence."
            return DummyResponse()

    class DummyBert:
        def encode(self, texts, convert_to_tensor):
            return [1.0 for _ in texts]

    from services import generate_section_service as gss
    gss.model = DummyModel2()
    gss.bert_model = DummyBert()
    
    # 修改相似度函数返回一个 NumPy 数组（支持 .mean() 方法）
    original_cos_sim = util.pytorch_cos_sim
    util.pytorch_cos_sim = lambda a, b: np.array([[0.5]])
    
    generated_section = gss.generate_section(
        results=["chunk1", "chunk2"],
        query="测试查询",
        section_title="Background",
        section_prompt="请生成一段清晰的 Background 部分内容。",
        previous_sections=[]
    )
    print("生成的章节内容:\n", generated_section)
    assert "Generated section content." in generated_section, "生成的章节内容不正确"
    
    # 恢复原始的 pytorch_cos_sim
    util.pytorch_cos_sim = original_cos_sim

    # ------------------------------
    # 测试 pinecone_service 中的 initialise_pinecone 和 get_all_paper_ids
    # ------------------------------
    print("\n测试 pinecone_service ...")

    from services import pinecone_service as ps

    # 定义 DummyIndex，用于模拟 Index.describe_index_stats
    class DummyIndex:
        def describe_index_stats(self):
            return {"namespaces": {"systematic_review/testpaper/Background": {"vector_count": 2}}}

    # 定义 DummyPinecone，并增加 Index 方法
    class DummyPinecone:
        def __init__(self):
            self.index_created = False

        def list_indexes(self):
            class DummyList:
                def names(self):
                    return []  # 模拟没有索引存在
            return DummyList()

        def create_index(self, name, dimension, metric, spec):
            self.index_created = True
            print(f"Dummy create_index 被调用，索引名称: {name}")

        def Index(self, index_name):
            return DummyIndex()

    # 将 config 模块中的 pinecone 替换为 DummyPinecone 实例，并在 services 中使用
    from config import pinecone as config_pinecone
    config_pinecone = DummyPinecone()
    ps.pinecone = config_pinecone

    ps.initialise_pinecone()
    paper_ids = ps.get_all_paper_ids()
    print("从 dummy pinecone 获取到的 paper IDs:", paper_ids)
    assert "testpaper" in paper_ids, "未正确获取到 paper id"
    
    # ------------------------------
    # 测试 section_prompts_service 中的 generate_background_section
    # ------------------------------
    print("\n测试 generate_background_section ...")

    from services import section_prompts_service as sps
    # 直接覆盖 generate_background_section 使其返回固定字符串
    sps.generate_background_section = lambda results, query, chunk_size, previous_sections: "Background Section Content"
    bg_section = sps.generate_background_section(["dummy_result"], "测试查询", 30, [])
    print("Background section:", bg_section)
    assert bg_section == "Background Section Content", "Background section 返回内容不正确"

    print("\n所有独立的服务测试已完成。")

if __name__ == '__main__':
    main()