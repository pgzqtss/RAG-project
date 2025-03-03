import re
import os
import sys
import io
import numpy as np
import matplotlib.pyplot as plt
from pypdf import PdfReader  # Use pypdf instead of PyPDF2
from chardet import detect

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Read file -------------------------------------------------
def read_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        return " ".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        return ""

def read_text_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            encoding = detect(raw_data)['encoding']
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading text file: {str(e)}")
        return ""

# Citation check -------------------------------------------------
def check_citation_count(review_text):
    # Using regex patterns
    citation_patterns = [
        r'\(([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+et\s+al\.?,\s+\d{4}))\)',  # Matches (Author et al., 2023)
        r'\(([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+,\s+\d{4})\)',  # Matches (Author Another Author, 2022)
        r'\(([A-Z][a-z]+(?:\s+&\s+[A-Z][a-z]+)+,\s+\d{4})\)',  # Matches (Author & Another Author, 2022)
        r'\b(10\.\d{4,}/[\w\.\-/]+)\b',  # Matches DOIs
        r'doi\.org/(10\.\d{4,}/[\w\.\-/]+)\b',  # Matches DOI URLs
        r'\[(\d{1,3})\]'  # Matches numbered citations like [1]
    ]
    
    # Set -> ensure unique citations
    found_citations = set()
    for pattern in citation_patterns:
        # Find all matches of each pattern in the review text and add them to the set
        found_citations.update(re.findall(pattern, review_text, re.IGNORECASE))
    
    return len(found_citations)

def analyze_document(file_path):
    # Read content
    text = read_pdf(file_path) if file_path.endswith('.pdf') else read_text_file(file_path)
    
    if not text:
        print("No content extracted from file.")
        return None
    
    # Count citations
    citation_count = check_citation_count(text)
    return citation_count

# Plot graph -----------------------------------------------------------
def plot_citation_distribution(actual_citations):
    # Simulated citation distribution
    bins = np.arange(0, 201, 10)
    data = [np.random.normal(45.07, (56 - 25) / 1.35, 96685)]  # Simulated normal distribution

    fig, ax = plt.subplots(figsize=(8, 5))  # Create a figure instance
    ax.hist(data, bins=bins, alpha=0.6, color='blue', edgecolor='black', label="Reference Distribution")

    # Mark actual citation count
    ax.axvline(actual_citations, color='red', linestyle='dashed', linewidth=2, label=f'Actual: {actual_citations}')

    ax.set_xlabel("Number of References")
    ax.set_ylabel("Article Count")
    ax.set_title("Citation Count Distribution in Systematic Reviews")
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    return fig  # Return the figure



if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), "../output.txt")
    
    citation_count = analyze_document(file_path)
    if citation_count is not None:
        print(f"Citation Count: {citation_count}")
        plot_citation_distribution(citation_count)