import pytest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from utils.text_splitter import split_text_into_chunks  

@patch("utils.text_splitter.RecursiveCharacterTextSplitter")
def test_split_text_into_chunks(mock_splitter):
    """Test text splitting function."""
    mock_instance = MagicMock()
    mock_instance.split_text.return_value = ["Chunk 1", "Chunk 2"]
    mock_splitter.return_value = mock_instance

    text = "This is a long text. It will be split."
    result = split_text_into_chunks(text, chunk_size=10, overlap=2)

    assert result == ["Chunk 1", "Chunk 2"]
    mock_splitter.assert_called_once_with(chunk_size=10, chunk_overlap=2, separators=['\n\n', '\n', '.', '?', '!'])
