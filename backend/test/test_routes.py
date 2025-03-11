import pytest
import sys
import os
import json
import bcrypt
import numpy as np
from flask import Flask, jsonify
from sentence_transformers import util

# -------------------------------
# 设置路径，确保可以导入 backend/routes 模块
# -------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# -------------------------------
# Dummy 类用于模拟数据库行为
# -------------------------------
class DummyCursor:
    def execute(self, query, params):
        pass
    def fetchone(self):
        # 用于 query_history 和 query_user，返回 ("dummy prompt", "dummy review") 或 (1,)
        return ("dummy prompt", "dummy review")
    def fetchall(self):
        # 用于 delete_user_history，返回一个列表
        return [("dummy result",)]
    def close(self):
        pass

class DummyConnection:
    def cursor(self):
        return DummyCursor()
    def commit(self):
        pass
    def close(self):
        pass

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

# -------------------------------
# Pytest Fixture - 创建 Flask App 并注册所有路由
# -------------------------------
@pytest.fixture
def app():
    app = Flask(__name__)
    app.testing = True

    # 为了让各路由文件中的 "from __main__ import app" 正常工作，
    # 将当前 app 设置到 __main__ 模块中
    import __main__
    __main__.app = app

    # 导入并注册 routes 目录中的各路由（由于路由文件在导入时已经通过装饰器注册到 app 中）
    from routes.delete_user_history import delete_user_history
    from routes.gen_systematic_review import generate_full_systematic_review
    from routes.login_user import login
    from routes.query_history import query
    from routes.query_user import query_user
    from routes.query_user_history import query_user_history
    from routes.register_user import register
    from routes.save_history import save_history
    from routes.upsert_vectors import init_pinecone

    return app

@pytest.fixture
def client(app):
    return app.test_client()

# -------------------------------
# Pytest 测试用例（针对各路由）
# -------------------------------

def test_delete_user_history(client, monkeypatch):
    monkeypatch.setattr("delete_user_history.connect_to_database", lambda: DummyConnection())
    payload = {"prompt_id": "dummy_id"}
    response = client.post("/api/delete_user_history", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "systematic review successfully" in data.get("message", "").lower()

def test_gen_systematic_review(client, monkeypatch):
    # 模拟 get_files、search_pinecone 和各 section 生成函数
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
    assert response.status_code == 200
    combined = data.get("systematic_review", "")
    for section in ["Background", "Methods", "Results", "Discussion", "Conclusion"]:
        assert section in combined

def test_login(client, monkeypatch):
    password = "secret"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    class DummyCursorLogin:
        def execute(self, query, params):
            pass
        def fetchone(self):
            return (1, hashed)
        def close(self):
            pass
    class DummyConnectionLogin:
        def cursor(self):
            return DummyCursorLogin()
        def close(self):
            pass
    monkeypatch.setattr("login_user.connect_to_database", lambda: DummyConnectionLogin())
    payload = {"username": "testuser", "password": "secret"}
    response = client.post("/api/login", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "logged in successfully" in data.get("message", "").lower()

def test_query_history(client, monkeypatch):
    monkeypatch.setattr("query_history.connect_to_database", lambda: DummyConnection())
    payload = {"prompt_id": "dummy_id"}
    response = client.post("/api/query", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    # DummyCursor.fetchone 返回 ("dummy prompt", "dummy review")
    assert data.get("prompt") == "dummy prompt"
    assert data.get("systematic_review") == "dummy review"

def test_query_user(client, monkeypatch):
    monkeypatch.setattr("query_user.connect_to_database", lambda: DummyConnectionUser())
    payload = {"username": "testuser"}
    response = client.post("/api/query_user", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "user_id" in data

def test_query_user_history(client, monkeypatch):
    monkeypatch.setattr("query_user_history.connect_to_database", lambda: DummyConnection())
    payload = {"user_id": 1}
    response = client.post("/api/query_user_history", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert isinstance(data.get("result"), list)

def test_register_user(client, monkeypatch):
    # 模拟用户注册成功（返回 201）
    class DummyCursorReg:
        def execute(self, query, params):
            pass
        def close(self):
            pass
    class DummyConnectionReg:
        def cursor(self):
            return DummyCursorReg()
        def commit(self):
            pass
        def close(self):
            pass
    monkeypatch.setattr("register_user.connect_to_database", lambda: DummyConnectionReg())
    payload = {"username": "newuser", "password": "newpass"}
    response = client.post("/api/register", json=payload)
    data = response.get_json()
    assert response.status_code == 201
    assert "registered successfully" in data.get("message", "").lower()

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
    assert response.status_code in (200, 201)
    assert "stored successfully" in data.get("message", "").lower()

def test_upsert_vectors(client, monkeypatch):
    # 覆盖 upsert_vectors 中的相关函数
    monkeypatch.setattr("upsert_vectors.initialise_pinecone", lambda: None)
    monkeypatch.setattr("upsert_vectors.process_and_store_all_pdfs", lambda id: (5, {"paper1": "dummy_path"}))
    monkeypatch.setattr("upsert_vectors.check_all_upserted_chunks", lambda files, chunks_count: None)
    payload = {"id": "dummy_id"}
    response = client.post("/api/upsert", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "upserted" in data.get("message", "").lower()

# -------------------------------
# Main 函数：独立运行所有路由测试（包含 assert 检查）
# -------------------------------
def main_routes():
    print("正在运行独立的路由测试...\n")
    # 创建一个测试用的 Flask app（利用 fixture 中的 app）
    app_instance = Flask(__name__)
    app_instance.testing = True

    # 将当前 app 设置到 __main__ 中，供各路由文件导入
    import __main__
    __main__.app = app_instance

    # 手动注册各路由（同样可以直接导入路由模块，触发装饰器注册）
    from routes.delete_user_history import delete_user_history
    from routes.gen_systematic_review import generate_full_systematic_review
    from routes.login_user import login
    from routes.query_history import query
    from routes.query_user import query_user
    from routes.query_user_history import query_user_history
    from routes.register_user import register
    from routes.save_history import save_history
    from routes.upsert_vectors import init_pinecone

    test_client = app_instance.test_client()

    # 测试 delete_user_history
    payload = {"prompt_id": "dummy_id"}
    response = test_client.post("/api/delete_user_history", json=payload)
    data = response.get_json()
    print("delete_user_history response:", data)
    assert response.status_code == 200
    assert "systematic review successfully" in data.get("message", "").lower()

    # 测试 generate_full_systematic_review
    # 覆盖 get_files、search_pinecone 与各 section 生成函数
    import routes.gen_systematic_review as gsr
    gsr.get_files = lambda id: {"paper1": "dummy_path"}
    gsr.search_pinecone = lambda query, paper_ids, section, top_k: ["dummy result"]
    gsr.generate_background_section = lambda results, query, chunk_size, previous_sections: "Background"
    gsr.generate_methods_section = lambda results, query, chunk_size, previous_sections: "Methods"
    gsr.generate_results_section = lambda results, query, chunk_size, previous_sections: "Results"
    gsr.generate_discussion_section = lambda results, query, chunk_size, previous_sections: "Discussion"
    gsr.generate_conclusion_section = lambda results, query, chunk_size, previous_sections: "Conclusion"
    payload = {"prompt": "Test query", "id": "dummy_id"}
    response = test_client.post("/api/generate", json=payload)
    data = response.get_json()
    print("generate_full_systematic_review response:", data)
    assert response.status_code == 200
    for sec in ["Background", "Methods", "Results", "Discussion", "Conclusion"]:
        assert sec in data.get("systematic_review", "")

    # 测试 login
    password = "secret"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    class DummyCursorLogin:
        def execute(self, query, params):
            pass
        def fetchone(self):
            return (1, hashed)
        def close(self):
            pass
    class DummyConnectionLogin:
        def cursor(self):
            return DummyCursorLogin()
        def close(self):
            pass
    import routes.login_user as lu
    lu.connect_to_database = lambda: DummyConnectionLogin()
    payload = {"username": "testuser", "password": "secret"}
    response = test_client.post("/api/login", json=payload)
    data = response.get_json()
    print("login response:", data)
    assert response.status_code == 200
    assert "logged in successfully" in data.get("message", "").lower()

    # 测试 query_history
    import routes.query_history as qh
    qh.connect_to_database = lambda: DummyConnection()
    payload = {"prompt_id": "dummy_id"}
    response = test_client.post("/api/query", json=payload)
    data = response.get_json()
    print("query response:", data)
    assert response.status_code == 200
    assert data.get("prompt") == "dummy prompt"
    assert data.get("systematic_review") == "dummy review"

    # 测试 query_user
    import routes.query_user as qu
    qu.connect_to_database = lambda: DummyConnectionUser()
    payload = {"username": "testuser"}
    response = test_client.post("/api/query_user", json=payload)
    data = response.get_json()
    print("query_user response:", data)
    assert response.status_code == 200
    assert "user_id" in data

    # 测试 query_user_history
    import routes.query_user_history as quh
    quh.connect_to_database = lambda: DummyConnection()
    payload = {"user_id": 1}
    response = test_client.post("/api/query_user_history", json=payload)
    data = response.get_json()
    print("query_user_history response:", data)
    assert response.status_code == 200
    assert isinstance(data.get("result"), list)

    # 测试 register_user
    import routes.register_user as ru
    class DummyCursorReg:
        def execute(self, query, params):
            pass
        def close(self):
            pass
    class DummyConnectionReg:
        def cursor(self):
            return DummyCursorReg()
        def commit(self):
            pass
        def close(self):
            pass
    ru.connect_to_database = lambda: DummyConnectionReg()
    payload = {"username": "newuser", "password": "newpass"}
    response = test_client.post("/api/register", json=payload)
    data = response.get_json()
    print("register response:", data)
    assert response.status_code == 201
    assert "registered successfully" in data.get("message", "").lower()

    # 测试 save_history
    import routes.save_history as sh
    sh.connect_to_database = lambda: DummyConnection()
    payload = {
        "user_id": [1],
        "prompt_id": "dummy_id",
        "prompt": "dummy prompt",
        "systematic_review": "dummy review"
    }
    response = test_client.post("/api/save", json=payload)
    data = response.get_json()
    print("save_history response:", data)
    assert response.status_code in (200, 201)
    assert "stored successfully" in data.get("message", "").lower()

    # 测试 upsert_vectors
    import routes.upsert_vectors as uv
    uv.initialise_pinecone = lambda: None
    uv.process_and_store_all_pdfs = lambda id: (5, {"paper1": "dummy_path"})
    uv.check_all_upserted_chunks = lambda files, chunks_count: None
    payload = {"id": "dummy_id"}
    response = test_client.post("/api/upsert", json=payload)
    data = response.get_json()
    print("upsert_vectors response:", data)
    assert response.status_code == 200
    assert "upserted" in data.get("message", "").lower()

    print("\n所有独立的路由测试已完成。")

if __name__ == '__main__':
    main_routes()