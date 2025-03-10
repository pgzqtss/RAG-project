import pytest
import sys
import re
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from unittest.mock import MagicMock
from utils.embedding_util import get_text_embedding

@pytest.fixture
def mock_embeddings():
    """Mock the OpenAIEmbeddings object to return a fixed-length vector."""
    mock = MagicMock()
    mock.embed_query.return_value = [0.1, 0.2, 0.3]  # Simulated embedding output
    return mock

def test_get_text_embedding_valid_input(mock_embeddings, monkeypatch):
    """Test if get_text_embedding correctly processes a valid string input."""
    monkeypatch.setattr("utils.embedding_util.embeddings", mock_embeddings)

    text = "Hello, world!"
    result = get_text_embedding(text)

    assert isinstance(result, list), "Output should be a list"
    assert all(isinstance(x, float) for x in result), "All elements should be floats"
    assert len(result) == 3, "Embedding length should match the mock output"

def test_get_text_embedding_invalid_input():
    """Test if get_text_embedding raises TypeError for non-string inputs."""
    with pytest.raises(TypeError, match=re.escape("❌ get_text_embedding() received a non-string input.")):
        get_text_embedding(123)

    with pytest.raises(TypeError):
        get_text_embedding(None)

    with pytest.raises(TypeError):
        get_text_embedding(["text in a list"])
