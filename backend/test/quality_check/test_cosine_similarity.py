import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="google")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fitz")

import sys
import os

# Add the parent directory of `cosine_similarity.py` to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../quality_check")))

from cosine_similarity import CosineSimilarityChecker

import pytest
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd

# Fixtures for test data
@pytest.fixture
def sample_reference_docs():
    return [
        "This is a sample reference text.",
        "Another reference document for testing.",
    ]

@pytest.fixture
def sample_hypothesis_doc():
    return "This is a sample hypothesis text."

@pytest.fixture
def sample_embeddings():
    return np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

@pytest.fixture
def cosine_similarity_checker(sample_reference_docs, sample_hypothesis_doc):
    return CosineSimilarityChecker(sample_reference_docs, sample_hypothesis_doc)

def test_preprocess_text(cosine_similarity_checker):
    text = "This is a test text with non-ASCII characters: ©®™"
    processed_text = cosine_similarity_checker.preprocess_text(text)
    assert processed_text == "This is a test text with non-ASCII characters:"

@patch("config.bert_model.encode", return_value=np.array([0.1, 0.2, 0.3]))
def test_fetch_embeddings(mock_encode, cosine_similarity_checker):
    embeddings = cosine_similarity_checker.fetch_embeddings("Sample text")
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (3,)

def test_calculate_similarity(cosine_similarity_checker, sample_embeddings):
    with patch("cosine_similarity.CosineSimilarityChecker.fetch_embeddings") as mock_fetch_embeddings:
        mock_fetch_embeddings.side_effect = [
            sample_embeddings[0],  # Embedding for first reference
            sample_embeddings[1],  # Embedding for second reference
            sample_embeddings[0],  # Embedding for hypothesis
        ]
        similarity_scores, overall_score = cosine_similarity_checker.calculate_similarity()
        assert isinstance(similarity_scores, list)
        assert isinstance(overall_score, float)
        assert len(similarity_scores) == 2  # Two reference documents

# def test_read_pdf():
#     with patch("cosine_similarity.fitz.open") as mock_fitz:
#         mock_doc = MagicMock()
#         mock_page = MagicMock()
#         mock_page.get_text.return_value = "Sample text from PDF."
#         mock_doc.__iter__.return_value = [mock_page]
#         mock_fitz.return_value = mock_doc

#         text = pdf_to_text("dummy.pdf")
#         assert text == "Sample text from PDF."

# def test_read_pdfs_from_folder(tmp_path):
#     pdf1 = tmp_path / "doc1.pdf"
#     pdf1.write_text("Fake PDF content 1")
#     pdf2 = tmp_path / "doc2.pdf"
#     pdf2.write_text("Fake PDF content 2")

#     with patch("cosine_similarity.read_pdf", side_effect=["Fake PDF content 1", "Fake PDF content 2"]):
#         file_paths, docs = read_pdfs(tmp_path)

#         assert len(file_paths) == 2
#         assert docs[0] == "Fake PDF content 1"
#         assert docs[1] == "Fake PDF content 2"

def test_fetch_embeddings_error(cosine_similarity_checker):
    with patch("config.bert_model.encode", side_effect=Exception("Embedding error")):
        embeddings = cosine_similarity_checker.fetch_embeddings("Sample text")
        assert np.all(embeddings == 0)  # Should return zero vector on error

def test_calculate_similarity_error(cosine_similarity_checker):
    with patch("cosine_similarity.CosineSimilarityChecker.fetch_embeddings", return_value=np.zeros(3)):
        similarity_scores, overall_score = cosine_similarity_checker.calculate_similarity()
        assert similarity_scores == []  # Expecting an empty list
        assert overall_score == 0.0  # Expecting 0.0 for overall_score