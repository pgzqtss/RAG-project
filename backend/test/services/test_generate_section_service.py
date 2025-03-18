import sys
import os
import pytest
import numpy as np
from unittest.mock import patch
from sentence_transformers import util

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from services.generate_section_service import generate_section

def dummy_model_invoke(prompt):
    class DummyResponse:
        content = "Generated section content.\nUnique sentence."
    return DummyResponse()

def dummy_bert_encode(texts, convert_to_tensor):
    return [1.0 for _ in texts]

def test_generate_section(monkeypatch):
    DummyModel = type("DummyModel", (), {"invoke": dummy_model_invoke})
    monkeypatch.setattr("services.generate_section_service.model", DummyModel())
    DummyBert = type("DummyBert", (), {"encode": dummy_bert_encode})
    monkeypatch.setattr("services.generate_section_service.bert_model", DummyBert())
    monkeypatch.setattr(util, "pytorch_cos_sim", lambda a, b: np.array([[0.5]]))
    
    result = generate_section(
        results=["chunk1", "chunk2"],
        query="Test query",
        section_title="Background",
        section_prompt="Section prompt",
        previous_sections=[]
    )
    assert "Generated section content." in result
