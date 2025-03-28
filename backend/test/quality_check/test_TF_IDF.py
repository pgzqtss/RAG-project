import sys
import os

# Add the parent directory of `TF_IDF.py` to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from quality_check.TF_IDF import TFIDF
from utils.pdf_util import pdf_to_text, read_pdfs

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

# Fixtures for test data
@pytest.fixture
def sample_documents():
    return [
        "This is a sample document.",
        "Another document for testing TF-IDF.",
        "TF-IDF is a useful metric for text analysis.",
    ]

@pytest.fixture
def tfidf_instance(sample_documents):
    return TFIDF(sample_documents)

# Test _preprocess
def test_preprocess(tfidf_instance):
    text = "This is a test document with numbers 123 and symbols !@#."
    processed_text = tfidf_instance._preprocess(text)
    assert processed_text == ["this", "is", "a", "test", "document", "with", "numbers", "123", "and", "symbols"]

# Test _calculate_tf
def test_calculate_tf(tfidf_instance):
    document = ["this", "is", "a", "test", "document", "this", "is", "test"]
    tf = tfidf_instance._calculate_tf(document)
    expected_tf = {
        "this": 2 / 8,
        "is": 2 / 8,
        "a": 1 / 8,
        "test": 2 / 8,
        "document": 1 / 8,
    }
    assert tf == expected_tf

# Test _calculate_idf
def test_calculate_idf(tfidf_instance):
    idf = tfidf_instance._calculate_idf()
    assert isinstance(idf, dict)
    assert all(isinstance(value, float) for value in idf.values())

# Test calculate_tfidf
def test_calculate_tfidf(tfidf_instance):
    tfidf_results = tfidf_instance.calculate_tfidf()
    assert isinstance(tfidf_results, pd.DataFrame)
    assert not tfidf_results.empty