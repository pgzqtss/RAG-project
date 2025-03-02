import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import os
import re
import fitz  # PyMuPDF
import pandas as pd
import seaborn as sns

# Load a local embedding model (SBERT)
# Mb change it to OpenAI??
model = SentenceTransformer('all-MiniLM-L6-v2')

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
            embedding = model.encode(preprocessed_text, convert_to_numpy=True)  # Returns NumPy array
            return embedding / np.linalg.norm(embedding)
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            return np.zeros(model.get_sentence_embedding_dimension())  # Returns zero vector

    def calculate_similarity(self):
        # List of embeddings for ref and hyp
        input_embeddings = [self.fetch_embeddings(text) for text in self.references]
        output_embedding = self.fetch_embeddings(self.hypothesis)

        if not input_embeddings or np.all(output_embedding == 0):
            print("Error: Missing required embeddings")
            return [], 0.0  # Return empty list and 0.0 for overall_score

        # Converts input_embeddings to NumPy array
        input_embeddings = np.array(input_embeddings)
        # Reshapes output_embedding to 2D array -> match input format for cosine_similarity
        output_embedding = output_embedding.reshape(1, -1)

        # Iterates through each embedding in input_emb and calculates the cosine similarity with output_emb
        similarity_scores = [cosine_similarity(input_emb.reshape(1, -1), output_embedding)[0][0] for input_emb in input_embeddings]
        overall_score = np.mean(similarity_scores)

        return similarity_scores, overall_score

def read_pdf(file_path):
    doc = fitz.open(file_path)
    return " ".join([page.get_text() for page in doc])

def read_pdfs_from_folder(folder_path):
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]
    return pdf_files, [read_pdf(pdf) for pdf in pdf_files]

# Paths
input_folder = os.path.join(os.path.dirname(__file__), "../papers/papers")
output_doc = os.path.join(os.path.dirname(__file__), "../output.txt")

# Load documents
reference_files, reference_docs = read_pdfs_from_folder(input_folder)
hypothesis_doc = read_pdf(output_doc)

# Compute cosine similarity scores
similarity_checker = CosineSimilarityChecker(reference_docs, hypothesis_doc)
similarity_scores, overall_score = similarity_checker.calculate_similarity()

if similarity_scores is not None:
    # Convert to DataFrame
    results_df = pd.DataFrame({
        "Reference Document": [os.path.basename(file) for file in reference_files],
        "Cosine Similarity": similarity_scores
    })
    results_df["Cosine Similarity Percentage"] = results_df["Cosine Similarity"]

    # Print results
    print(results_df)
    print(f"\nAverage Cosine Similarity: {results_df['Cosine Similarity'].mean():.4f} ({results_df['Cosine Similarity Percentage'].mean():.2f}%)")

    # Bar Plot Visualization ----------------------------------------
    plt.figure(figsize=(10, 6))
    sns.barplot(
        x="Reference Document",
        y="Cosine Similarity Percentage",
        hue="Reference Document",  # Add this
        data=results_df,
        palette="coolwarm",
        legend=False  # Disable legend
    )
    plt.title("Cosine Similarity Bar Plot")
    plt.xlabel("Reference Document")
    plt.ylabel("Cosine Similarity Percentage")
    plt.show()