'''
BLEU (Bilingual Evaluation Understudy)
Evaluating the quality of text which has been machine-translated 
from one natural language to another
So in this case, compare between the generated systematic review
and the medical papers users input
'''

import os
import nltk
import fitz  # PyMuPDF
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

# nltk.download('punkt')

class BLEUScorer:
    def __init__(self, reference_docs, hypothesis_doc):
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

def read_pdf(file_path):
    doc = fitz.open(file_path)
    return " ".join([page.get_text() for page in doc])

def read_pdfs_from_folder(folder_path):
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]
    return pdf_files, [read_pdf(pdf) for pdf in pdf_files]

# Paths
input_folder = r"C:\Users\znkje\OneDrive\Desktop\Systems\RAG-project\backend\papers\input_papers\P3"
output_doc = r"C:\Users\znkje\OneDrive\Desktop\Systems\RAG-project\backend\papers\output_reviews\S3.pdf"

# Load documents
reference_files, reference_docs = read_pdfs_from_folder(input_folder)
hypothesis_doc = read_pdf(output_doc)

# Compute BLEU scores
bleu_scorer = BLEUScorer(reference_docs, hypothesis_doc)
bleu_scores = bleu_scorer.calculate_bleu()

# Extract file names from paths
reference_filenames = [os.path.basename(file) for file in reference_files]

# Terminal Output ----------------------------------------------
# Convert to DataFrame
results_df = pd.DataFrame({
    "Reference Document": reference_filenames,
    "BLEU Score": bleu_scores
})
results_df["BLEU Percentage"] = results_df["BLEU Score"] * 100  # Convert to percentage

print(results_df)
print(f"\nAverage BLEU Score: {results_df['BLEU Score'].mean():.4f} ({results_df['BLEU Percentage'].mean():.2f}%)")

# Bar Plot Visualization ----------------------------------------
plt.figure(figsize=(10, 6))
sns.barplot(x="Reference Document", y="BLEU Percentage", data=results_df, palette="coolwarm")
plt.title("BLEU Score Bar Plot")
plt.xlabel("Reference Document")
plt.ylabel("BLEU Percentage")
plt.show()