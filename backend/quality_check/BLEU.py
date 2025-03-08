'''
BLEU (Bilingual Evaluation Understudy)
- comparing n-grams (Sequences of n words) in a generated text to
those in a reference text.
1. Tokenization
2. N-gram matching: count the number of matching n-grams in the hypothesis
3. Precision: ratio of the number of n-grams in the hypothesis that appear in the reference
4. BLEU Score: geometric mean of the n-gram precisions

    BLEU = BP * exp(sum(w_n * log(p_n)))
    BP = min(1, exp(1 - r/c))
    r = number of words in the hypothesis
    c = number of words in the reference
    w_n = 1/n (weights for each n-gram level)
    p_n = precision for each n-gram level
'''

import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

class BLEUScorer:
    def __init__(self, reference_docs, hypothesis_doc):
        nltk.download('punkt_tab')

        # Reference = inputted medical papers, Hypothesis = generated systematic review
        self.references = [self._tokenize(doc) for doc in reference_docs]
        self.hypothesis = self._tokenize(hypothesis_doc)

    def _tokenize(self, text):
        # Tokenizes text into sentences and words
        return [nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text)]
    
    def calculate_bleu(self):
        # SmoothingFunction().method1: Smoothing to handle short text
        smoothie = SmoothingFunction().method1
        # Flattens the tokenized hypothesis into a single list
        flattened_hypothesis = [token for sent in self.hypothesis for token in sent]
        # Compute BLEU scores for each reference
        scores = [sentence_bleu(ref, flattened_hypothesis, smoothing_function=smoothie) for ref in self.references]
        return scores