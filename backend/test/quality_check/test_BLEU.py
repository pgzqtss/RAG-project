import warnings
# Suppress all DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the path to the BLEU.py module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from quality_check.BLEU import BLEUScorer

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