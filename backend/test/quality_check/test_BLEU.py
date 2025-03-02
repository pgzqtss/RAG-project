import warnings
# Suppress all DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the path to the BLEU.py module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../quality_check")))

from BLEU import BLEUScorer, read_pdf, read_pdfs_from_folder

@pytest.fixture
def sample_data():
    reference_docs = ["This is a sample reference text.", "Another reference document for testing."]
    hypothesis_doc = "This is a sample hypothesis text."
    return reference_docs, hypothesis_doc

@pytest.fixture
def bleu_scorer(sample_data):
    reference_docs, hypothesis_doc = sample_data
    return BLEUScorer(reference_docs, hypothesis_doc)

def test_tokenization(bleu_scorer):
    tokenized_ref = bleu_scorer._tokenize("This is a test sentence.")
    assert isinstance(tokenized_ref, list)
    assert all(isinstance(sent, list) for sent in tokenized_ref)

def test_bleu_calculation(bleu_scorer):
    scores = bleu_scorer.calculate_bleu()
    assert isinstance(scores, list)
    assert all(isinstance(score, float) for score in scores)

def test_read_pdf():
    with patch("BLEU.fitz.open") as mock_fitz:
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample text from PDF."
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz.return_value = mock_doc
        
        text = read_pdf("dummy.pdf")
        assert text == "Sample text from PDF."

def test_read_pdfs_from_folder():
    with patch("BLEU.os.listdir", return_value=["doc1.pdf", "doc2.pdf"]), \
         patch("BLEU.read_pdf", side_effect=["Text from doc1", "Text from doc2"]):
        
        file_paths, docs = read_pdfs_from_folder("dummy_folder")
        
        assert len(file_paths) == 2
        assert len(docs) == 2
        assert docs[0] == "Text from doc1"
        assert docs[1] == "Text from doc2"