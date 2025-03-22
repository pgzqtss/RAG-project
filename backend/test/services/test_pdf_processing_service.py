import sys
import os
import pytest

# 添加上级目录到 sys.path，以便导入 backend 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from services.pdf_processing_service import process_and_store_all_pdfs

# Dummy functions for testing
def dummy_get_files(id):
    return {"paper1": "dummy_path"}

def dummy_pdf_to_text(path):
    return "dummy pdf text"

def dummy_split_text_into_chunks(text, chunk_size=1500, overlap=300):
    return ["chunk1", "chunk2"]

def dummy_upsert_all_chunks(text_chunks, paper_id):
    # For testing, do nothing
    return

def dummy_pinecone():
    class DummyPineconeClass:
        def Index(self, name):
            class DummyIndex:
                def describe_index_stats(self):
                    return {"namespaces": {}}
            return DummyIndex()
    return DummyPineconeClass()

def test_process_and_store_all_pdfs(monkeypatch):
    # Override functions in pdf_processing_service
    monkeypatch.setattr("services.pdf_processing_service.get_files", dummy_get_files)
    monkeypatch.setattr("services.pdf_processing_service.pdf_to_text", dummy_pdf_to_text)
    monkeypatch.setattr("services.pdf_processing_service.split_text_into_chunks", dummy_split_text_into_chunks)
    monkeypatch.setattr("services.pdf_processing_service.upsert_all_chunks", dummy_upsert_all_chunks)
    # IMPORTANT: 覆盖 upsert_pinecone_service 中的 pinecone 对象
    monkeypatch.setattr("services.upsert_pinecone_service.pinecone", dummy_pinecone())
    
    result = process_and_store_all_pdfs("test_id")
    # 预期返回 2 chunks 和 get_files 返回的字典
    assert result == (2, {"paper1": "dummy_path"})

