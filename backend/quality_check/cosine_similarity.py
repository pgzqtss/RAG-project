import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
from config import bert_model

class CosineSimilarityChecker:
    def __init__(self, reference_docs, hypothesis_doc):
        # Reference = input medical papers, Hypothesis = generated systematic review
        self.references = reference_docs
        self.hypothesis = hypothesis_doc

    # Removes non-ASCII characters from text
    def preprocess_text(self, text):
        # Replace non-ASCII characters with a single space and strip trailing spaces
        return re.sub(r'[^\x00-\x7F]+', ' ', text).strip()

    # Generates embeddings using SBERT model
    def fetch_embeddings(self, text):
        try:
            preprocessed_text = self.preprocess_text(text)
            embedding = bert_model.encode(preprocessed_text, convert_to_numpy=True)  # Returns NumPy array
            return embedding / np.linalg.norm(embedding)
        except Exception as e:
            print(f'Error generating embeddings: {str(e)}')
            return np.zeros(bert_model.get_sentence_embedding_dimension())  # Returns zero vector

    def calculate_similarity(self):
        # List of embeddings for ref and hyp
        input_embeddings = [self.fetch_embeddings(text) for text in self.references]
        output_embedding = self.fetch_embeddings(self.hypothesis)

        if not input_embeddings or np.all(output_embedding == 0):
            print('Error: Missing required embeddings')
            return [], 0.0  # Return empty list and 0.0 for overall_score

        # Converts input_embeddings to NumPy array
        input_embeddings = np.array(input_embeddings)
        # Reshapes output_embedding to 2D array -> match input format for cosine_similarity
        output_embedding = output_embedding.reshape(1, -1)

        # Iterates through each embedding in input_emb and calculates the cosine similarity with output_emb
        similarity_scores = [cosine_similarity(input_emb.reshape(1, -1), output_embedding)[0][0] for input_emb in input_embeddings]
        overall_score = np.mean(similarity_scores)

        return similarity_scores, overall_score