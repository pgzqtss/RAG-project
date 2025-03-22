import sys
import os
import pytest
import numpy as np
from unittest.mock import patch
from sentence_transformers import util

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from services.generate_section_service import generate_section

# 修改 dummy_model_invoke，使其接受 self 和 prompt 两个参数
def dummy_model_invoke(self, prompt):
    class DummyResponse:
        content = "Generated section content.\nUnique sentence."
    return DummyResponse()

def dummy_bert_encode(self, texts, convert_to_tensor):
    return [1.0 for _ in texts]

def test_generate_section(monkeypatch):
    # 替换 model 和 bert_model
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
    # 断言生成的内容中包含我们预期的字符串
    assert "Generated section content." in result

