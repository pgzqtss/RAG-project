import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from services.classify_chunk_service import classify_chunk_with_llm

# 修改 dummy_invoke_valid 使其接受 self 和 prompt 两个参数
def dummy_invoke_valid(self, prompt):
    class DummyResponse:
        content = "Methods"
    return DummyResponse()

def dummy_invoke_invalid(self, prompt):
    class DummyResponse:
        content = "InvalidSection"
    return DummyResponse()

def dummy_invoke_exception(self, prompt):
    raise Exception("LLM error")

def test_classify_chunk_valid(monkeypatch):
    DummyModel = type("DummyModel", (), {"invoke": dummy_invoke_valid})
    monkeypatch.setattr("services.classify_chunk_service.model", DummyModel())
    result = classify_chunk_with_llm("Test text")
    # 预期返回 "Methods"
    assert result == "Methods"

def test_classify_chunk_invalid(monkeypatch):
    DummyModel = type("DummyModel", (), {"invoke": dummy_invoke_invalid})
    monkeypatch.setattr("services.classify_chunk_service.model", DummyModel())
    result = classify_chunk_with_llm("Test text")
    # 无效时默认返回 "Background"
    assert result == "Background"

def test_classify_chunk_exception(monkeypatch):
    DummyModel = type("DummyModel", (), {"invoke": dummy_invoke_exception})
    monkeypatch.setattr("services.classify_chunk_service.model", DummyModel())
    result = classify_chunk_with_llm("Test text")
    assert result == "Background"
