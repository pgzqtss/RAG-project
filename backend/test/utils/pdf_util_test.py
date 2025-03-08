import os
import sys
import pytest
from unittest.mock import patch, mock_open, MagicMock
from utils.pdf_util import read_pdfs

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

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