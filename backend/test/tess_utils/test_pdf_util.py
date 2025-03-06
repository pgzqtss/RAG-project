import pytest
from unittest.mock import patch, MagicMock
import fitz  # ✅ Use pymupdf to avoid conflicts
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from utils.pdf_util import pdf_to_text, clean_text 

@patch("fitz.open")
def test_pdf_to_text(mock_fitz_open):
    """Test extracting text from a PDF file."""
    # ✅ Simulate a PDF document with one page
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Page 1 text"

    mock_doc = MagicMock()
    mock_doc.__iter__.return_value = [mock_page]  # ✅ Ensure it returns an iterable list
    mock_fitz_open.return_value = mock_doc

    text = pdf_to_text("sample.pdf")
    assert text == "Page 1 text"

@pytest.mark.parametrize("input_text, expected_output", [
    ("Hello\nWorld", "Hello World"),  # ✅ Newline should be replaced by a space
    ("Extra   spaces  here", "Extra spaces here"),  # ✅ Multiple spaces should be reduced to one
    ("Broken-\nword test", "Brokenword test"),  # ✅ Handle hyphenated words correctly
    ("Unnecessary symbols †‡§", "Unnecessary symbols")  # ✅ Remove special symbols
])
def test_clean_text(input_text, expected_output):
    """Test text cleaning function."""
    assert clean_text(input_text) == expected_output
