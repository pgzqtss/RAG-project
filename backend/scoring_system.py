import fitz  # PyMuPDF
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai
import matplotlib.pyplot as plt
import os
import datetime

# Configure OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Weight configuration
WEIGHTS = {"citation": 0.4, "recency": 0.3, "relevance": 0.3}

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def count_references(text):
    """
    Count the number of references in the text
    """
    references = re.findall(r"(References|Bibliography)", text, re.IGNORECASE)
    return len(references)

def extract_year(text):
    """
    Extract the publication year from the text
    """
    years = re.findall(r"\b(19[0-9]{2}|20[0-9]{2})\b", text)
    if years:
        return max(map(int, years))  # Return the most recent year
    return None

def get_embedding(text, model="text-embedding-ada-002"):
    """
    Get text embedding using OpenAI API
    """
    try:
        response = openai.Embedding.create(model=model, input=text)
        return np.array(response['data'][0]['embedding'])
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return np.zeros(1536)  # Return a zero vector as fallback

def calculate_citation_score(citations, max_citations):
    """
    Calculate citation score
    """
    return min(citations / max_citations, 1.0) * 100

def calculate_recency_score(publication_year, decay_factor=10):
    """
    Calculate recency score
    """
    if publication_year is None:
        return 0  # No year found, score is 0
    current_year = datetime.datetime.now().year
    age = current_year - publication_year
    return max(0, 1 - age / decay_factor) * 100

def calculate_relevance_score(doc_embedding, query_embedding):
    """
    Calculate relevance score
    """
    if not doc_embedding.any() or not query_embedding.any():
        return 0  # If embeddings are invalid, relevance is 0
    similarity = cosine_similarity([doc_embedding], [query_embedding])
    return similarity[0][0] * 100

def calculate_overall_score(citation_score, recency_score, relevance_score, weights=WEIGHTS):
    """
    Calculate overall score
    """
    return (
        weights["citation"] * citation_score +
        weights["recency"] * recency_score +
        weights["relevance"] * relevance_score
    )

def visualize_scores(scores, labels):
    """
    Visualize scores as a bar chart
    """
    plt.bar(labels, scores, color=['blue', 'green', 'orange', 'red'])
    plt.ylabel('Score')
    plt.title('Document Scoring Breakdown')
    plt.show()

# Main program
if __name__ == "__main__":
    # Path to the PDF file
    pdf_path = "backend/papers/paper1.pdf"

    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("Failed to extract text from the PDF.")
        exit()

    # Count references
    citation_count = count_references(text)

    # Extract publication year
    publication_year = extract_year(text)

    # Generate embeddings
    doc_embedding = get_embedding(text)
    query_embedding = get_embedding("The role of AI in modern medicine")

    # Calculate individual scores
    max_citations = 50  # Assume the maximum citation count is 50
    citation_score = calculate_citation_score(citation_count, max_citations)
    recency_score = calculate_recency_score(publication_year)
    relevance_score = calculate_relevance_score(doc_embedding, query_embedding)

    # Calculate overall score
    overall_score = calculate_overall_score(citation_score, recency_score, relevance_score)

    # Print results
    print(f"Citation Score: {citation_score:.2f}")
    print(f"Recency Score: {recency_score:.2f}")
    print(f"Relevance Score: {relevance_score:.2f}")
    print(f"Overall Score: {overall_score:.2f}")

    # Visualize results
    labels = ['Citation', 'Recency', 'Relevance', 'Overall']
    scores = [citation_score, recency_score, relevance_score, overall_score]
    visualize_scores(scores, labels)
