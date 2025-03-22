import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from services.pinecone_service import initialise_pinecone, get_all_paper_ids

def test_initialise_pinecone(monkeypatch):
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
        def Index(self, index_name):
            class DummyIndex:
                def describe_index_stats(self):
                    return {"namespaces": {"systematic_review/testpaper/Background": {"vector_count": 2}}}
            return DummyIndex()
    dummy = DummyPinecone()
    monkeypatch.setattr("services.pinecone_service.pinecone", dummy)
    initialise_pinecone()
    assert dummy.created is True

def test_get_all_paper_ids(monkeypatch):
    class DummyIndex:
        def describe_index_stats(self):
            return {"namespaces": {"systematic_review/testpaper/Background": {"vector_count": 2}}}
    monkeypatch.setattr("services.pinecone_service.pinecone.Index", lambda name: DummyIndex())
    paper_ids = get_all_paper_ids()
    assert "testpaper" in paper_ids
