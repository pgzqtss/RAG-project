import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from services.upsert_pinecone_service import upsert_all_chunks

def dummy_classify_chunk(chunk):
    # 固定返回 "Methods"
    return "Methods"

def dummy_get_text_embedding(text):
    return [0.1] * 1536

def test_upsert_all_chunks(monkeypatch):
    monkeypatch.setattr("services.upsert_pinecone_service.classify_chunk_with_llm", lambda chunk: dummy_classify_chunk(chunk))
    monkeypatch.setattr("services.upsert_pinecone_service.get_text_embedding", lambda text: dummy_get_text_embedding(text))
    
    # 定义 DummyIndex，必须实现 describe_index_stats 和 upsert 方法
    class DummyIndex:
        def describe_index_stats(self):
            return {"namespaces": {}}
        def upsert(self, items, namespace):
            self.items = items
    dummy_index = DummyIndex()
    monkeypatch.setattr("services.upsert_pinecone_service.pinecone.Index", lambda name: dummy_index)
    
    upsert_all_chunks(["chunk1", "chunk2"], "paper1")
    assert hasattr(dummy_index, "items")
    assert len(dummy_index.items) > 0
