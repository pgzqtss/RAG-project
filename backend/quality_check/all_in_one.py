import os
import re
import platform
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from matplotlib.backends.backend_pdf import PdfPages
from collections import Counter
from citation_check import analyze_document, plot_citation_distribution
from cosine_similarity import CosineSimilarityChecker, read_pdfs_from_folder, read_pdf
from TF_IDF import TFIDF
from BLEU import BLEUScorer
from author_num import process_pdfs, save_and_plot_results
from themetic_area import load_documents, extract_thematic_area, generate_wordcloud

# Paths
input_folder = os.path.join(os.path.dirname(__file__), "../papers/papers")
output_doc = os.path.join(os.path.dirname(__file__), "../output.txt")

# Load documents for citation, cosine similarity, TF-IDF, and BLEU
reference_files, reference_docs = read_pdfs_from_folder(input_folder)
hypothesis_doc = read_pdf(output_doc)

# Citation Count
citation_count = analyze_document(output_doc)

# Cosine Similarity
similarity_checker = CosineSimilarityChecker(reference_docs, hypothesis_doc)
similarity_scores, overall_score = similarity_checker.calculate_similarity()

# TF-IDF
documents = reference_docs + [hypothesis_doc]
tfidf = TFIDF(documents)
tfidf_results = tfidf.calculate_tfidf()

# BLEU Score
bleu_scorer = BLEUScorer(reference_docs, hypothesis_doc)
bleu_scores = bleu_scorer.calculate_bleu()

# Process author counts and thematic areas
pdf_folder_path = "RAG-project/backend/papers/papers"
author_counts = process_pdfs(pdf_folder_path)
author_counts_image = "author_counts.png"
save_and_plot_results(author_counts, output_image=author_counts_image)

# Process thematic areas
folder_path = "RAG-project/backend/papers/papers"
docs = load_documents(folder_path)
doc_areas = [extract_thematic_area(doc) for doc in docs]
all_areas = []
for area_str in doc_areas:
    cleaned_str = area_str.replace('\n', ' ').replace('\r', ' ')
    splitted = [a.strip() for a in cleaned_str.split(",") if a.strip()]
    all_areas.extend(splitted)
wordcloud_image = "thematic_wordcloud.png"
generate_wordcloud(all_areas, wordcloud_image)

# Create PDF
pdf_filename = 'quality_check_report.pdf'
with PdfPages(pdf_filename) as pdf:
    # Add author counts bar plot
    if os.path.exists(author_counts_image):
        img = plt.imread(author_counts_image)
        plt.figure(figsize=(10, 6))
        plt.imshow(img)
        plt.axis('off')
        pdf.savefig()
        plt.close()
    else:
        print(f"Warning: {author_counts_image} does not exist and will be skipped.")

    # Add thematic word cloud
    if os.path.exists(wordcloud_image):
        img = plt.imread(wordcloud_image)
        plt.figure(figsize=(10, 6))
        plt.imshow(img)
        plt.axis('off')
        pdf.savefig()
        plt.close()
    else:
        print(f"Warning: {wordcloud_image} does not exist and will be skipped.")

    # Citation Distribution Plot
    fig = plot_citation_distribution(citation_count)  # Get the figure instance
    pdf.savefig(fig)  # Save the returned figure
    plt.close(fig)  # Ensure the figure is closed properly

    # Cosine Similarity Bar Plot
    if similarity_scores is not None:
        results_df = pd.DataFrame({
            "Reference Document": [os.path.basename(file) for file in reference_files],
            "Cosine Similarity": similarity_scores
        })
        results_df["Cosine Similarity Percentage"] = results_df["Cosine Similarity"] * 100

        plt.figure(figsize=(10, 6))
        sns.barplot(x="Reference Document", y="Cosine Similarity Percentage", data=results_df, palette="coolwarm")
        plt.title("Cosine Similarity")
        plt.xlabel("Reference Document")
        plt.ylabel("Cosine Similarity Percentage")
        plt.xticks(rotation=45)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    # TF-IDF Heatmap
    average_tfidf = tfidf_results.mean(axis=0)
    top_words = average_tfidf.nlargest(50).index
    filtered_results = tfidf_results[top_words]

    plt.figure(figsize=(16, 10))
    sns.heatmap(filtered_results, annot=False, cmap='viridis')
    plt.title('TF-IDF Heatmap (Top 50 Words)')
    plt.tight_layout()
    pdf.savefig()
    plt.close()

    # BLEU Score Bar Plot
    results_df = pd.DataFrame({
        "Reference Document": [os.path.basename(file) for file in reference_files],
        "BLEU Score": bleu_scores
    })
    results_df["BLEU Percentage"] = results_df["BLEU Score"] * 100

    plt.figure(figsize=(10, 6))
    sns.barplot(x="Reference Document", y="BLEU Percentage", data=results_df, palette="coolwarm")
    plt.title("BLEU Score")
    plt.xlabel("Reference Document")
    plt.ylabel("BLEU Percentage")
    plt.xticks(rotation=45)
    plt.tight_layout()
    pdf.savefig()
    plt.close()

print(f"PDF report saved as {pdf_filename}")