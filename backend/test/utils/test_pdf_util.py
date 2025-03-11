import pytest
from unittest.mock import patch, MagicMock
import fitz  # ✅ Use pymupdf to avoid conflicts
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from utils.pdf_util import pdf_to_text, clean_text, read_pdfs

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

@patch('utils.pdf_util.os.listdir')
@patch('utils.pdf_util.pdf_to_text')
def test_read_pdfs(mock_pdf_to_text, mock_listdir):
    # Mock the list of PDF files in the directory
    mock_listdir.return_value = ['file1.pdf', 'file2.pdf', 'file3.txt']
    
    # Mock the text extraction from PDF files
    mock_pdf_to_text.side_effect = ['Text from file1', 'Text from file2']

    folder_path = '/mock/folder/path'
    pdf_files, texts = read_pdfs(folder_path)

    # Verify the list of PDF files
    assert pdf_files == [os.path.join(folder_path, 'file1.pdf'), os.path.join(folder_path, 'file2.pdf')]
    
    # Verify the extracted texts
    assert texts == ['Text from file1', 'Text from file2']

    # Verify the functions are called with correct arguments
    mock_listdir.assert_called_once_with(folder_path)
    mock_pdf_to_text.assert_any_call(os.path.join(folder_path, 'file1.pdf'))
    mock_pdf_to_text.assert_any_call(os.path.join(folder_path, 'file2.pdf'))