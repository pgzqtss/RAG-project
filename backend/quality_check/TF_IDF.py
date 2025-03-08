'''
TF-IDF stands for Term Frequency-Inverse Document Frequency
Term Frequency will be zero if a word does not appear in a document
TF = (Number of times a word appears in a document) / (Total number of words in the document)
Inverse Document Frequency will be zero if a word appears in all documents
TDF = log(Total number of documents / Number of documents with the word in it)
TF-IDF is the product of TF and IDF
Expected output - Matrix:
Row: Each row represents a document
Column: Each column represents a unique word
Value: The TF-IDF score for each word in each document
'''

import math
from collections import Counter
import pandas as pd

class TFIDF:
    def __init__(self, documents):
        self.documents = documents
        self.preprocessed = [self._preprocess(doc) for doc in documents]
        self.vocab = set(word for doc in self.preprocessed for word in doc)
        self.idf = self._calculate_idf()
        
    # Turn to lowercase, remove unwanted characters, split into words
    def _preprocess(self, text):
        text = text.lower()
        text = ''.join([c for c in text if c.isalnum() or c.isspace()])
        return text.split()
    
    # Calculate the term frequency of each word in a document
    # (How relevant the word is in one document)
    def _calculate_tf(self, document):
        word_count = len(document)
        tf_dict = {}
        counter = Counter(document)
        for word, count in counter.items():
            tf_dict[word] = count / word_count
        return tf_dict
    
    # Calculate the inverse document frequency of each word
    # (How unique the word is across all documents)
    def _calculate_idf(self):
        idf_dict = {}
        total_docs = len(self.preprocessed)
        for word in self.vocab:
            docs_with_word = sum(1 for doc in self.preprocessed if word in doc)
            idf_dict[word] = math.log(total_docs / (1 + docs_with_word))
        return idf_dict
    
    # Calculate the TF-IDF score for each word in each document
    def calculate_tfidf(self):
        tfidf_results = []
        for i, doc in enumerate(self.preprocessed):
            tf = self._calculate_tf(doc)
            tfidf = {word: tf.get(word, 0) * self.idf[word] for word in self.vocab}
            tfidf_results.append(tfidf)
        return pd.DataFrame(tfidf_results)