import sys
import os
import pytest

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from services.pdf_processing_service import process_and_store_all_pdfs

def dummy_get_files(id):
    return {"paper1": "dummy_path"}

def dummy_pdf_to_text(path):
    return "dummy pdf text"

def dummy_split_text_into_chunks(text, chunk_size=1500, overlap=300):
    return ["chunk1", "chunk2"]

def dummy_upsert_all_chunks(text_chunks, paper_id):
    # For testing, do nothing
    return

def test_process_and_store_all_pdfs(monkeypatch):
    monkeypatch.setattr("services.pdf_processing_service.get_files", dummy_get_files)
    monkeypatch.setattr("utils.pdf_util.pdf_to_text", dummy_pdf_to_text)
    monkeypatch.setattr("utils.text_splitter.split_text_into_chunks", dummy_split_text_into_chunks)
    monkeypatch.setattr("services.upsert_pinecone_service.upsert_all_chunks", dummy_upsert_all_chunks)
    
    result = process_and_store_all_pdfs("test_id")
    # Expect two chunks from one file
    assert result == (2, {"paper1": "dummy_path"})
