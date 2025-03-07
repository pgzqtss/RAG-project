import re
import os
import sys
import io
import numpy as np
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader
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
        r'\(([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+et\s+al\.?,\s+\d{4}))\)',
        r'\(([A-Z][a-z]+(?:\s+&\s+[A-Z][a-z]+)+,\s+\d{4})\)',
        r'\b(10\.\d{4,}/[\w\.\-/]+)\b',
        r'doi\.org/(10\.\d{4,}/[\w\.\-/]+)\b',
        r'\[(\d{1,3})\]'
    ]
    
    # Set -> ensure unique citations
    found_citations = set()
    for pattern in citation_patterns:
        # Find all matches of each pattern in the review text and add the to set
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
import numpy as np
import matplotlib.pyplot as plt

def plot_citation_distribution(actual_citations):
    # Simulated citation distribution based on given data
    bins = np.arange(0, 201, 10)  # Bin size of 10 references
    data = [np.random.normal(45.07, (56 - 25) / 1.35, 96685)]  # Approximate normal distribution

    plt.figure(figsize=(8, 5))
    plt.hist(data, bins=bins, alpha=0.6, color='blue', edgecolor='black', label="Reference Distribution")

    # Mark actual citation count
    plt.axvline(actual_citations, color='red', linestyle='dashed', linewidth=2, label=f'Actual: {actual_citations}')

    plt.xlabel("Number of References")
    plt.ylabel("Article Count")
    plt.title("Citation Count Distribution in Systematic Reviews")
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()


if __name__ == "__main__":
    file_path = r"C:\\Users\\znkje\\OneDrive\\Desktop\\Systems\\RAG-project\\backend\\papers\\output_reviews\\S2.pdf"
    
    citation_count = analyze_document(file_path)
    if citation_count is not None:
        print(f"Citation Count: {citation_count}")
        plot_citation_distribution(citation_count)

'''
Normal distribution for link below:
https://quantifyinghealth.com/how-many-references-to-use-for-research-papers/
'''