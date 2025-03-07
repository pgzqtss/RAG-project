import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
from quality_check.citation_check import analyze_document, plot_citation_distribution
from quality_check.cosine_similarity import CosineSimilarityChecker
from quality_check.TF_IDF import TFIDF
from quality_check.BLEU import BLEUScorer
from quality_check.author_num import process_pdfs, save_and_plot_results
from quality_check.themetic_area import load_documents, extract_thematic_area, generate_wordcloud
from utils.pdf_util import pdf_to_text, read_pdfs

from flask import jsonify, request
from __main__ import app

@app.route('/api/quality_check', methods=['POST'])
def generate_quality_check_graphs():
    data = request.json
    id = data.get('id')

    input_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'public', 'files', str(id)))
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'public', 'output', str(id), 'systematic_review.pdf'))

    # Load documents for citation, cosine similarity, TF-IDF, and BLEU
    reference_files, reference_docs = read_pdfs(input_path)
    hypothesis_doc = pdf_to_text(output_path)

    # Citation Count
    citation_count = analyze_document(output_path)

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
    author_counts = process_pdfs(input_path)
    author_counts_image = 'author_counts.png'
    save_and_plot_results(author_counts=author_counts, output_image=author_counts_image, id=id)

    # Process thematic areas
    docs = load_documents(input_path)
    doc_areas = [extract_thematic_area(doc) for doc in docs]
    all_areas = []
    for area_str in doc_areas:
        cleaned_str = area_str.replace('\n', ' ').replace('\r', ' ')
        splitted = [a.strip() for a in cleaned_str.split(',') if a.strip()]
        all_areas.extend(splitted)
    wordcloud_image = 'thematic_wordcloud.png'
    generate_wordcloud(areas=all_areas, output_file=wordcloud_image, id=id)

    # Create PDF
    pdf_filename = 'quality_check_report.pdf'
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'public', 'output', str(id), str(pdf_filename)))
    with PdfPages(pdf_path) as pdf:
        # Add author counts bar plot
        if os.path.exists(author_counts_image):
            img = plt.imread(author_counts_image)
            plt.figure(figsize=(10, 6))
            plt.imshow(img)
            plt.axis('off')
            pdf.savefig()
            plt.close()
        else:
            print(f'Warning: {author_counts_image} does not exist and will be skipped.')

        # Add thematic word cloud
        if os.path.exists(wordcloud_image):
            img = plt.imread(wordcloud_image)
            plt.figure(figsize=(10, 6))
            plt.imshow(img)
            plt.axis('off')
            pdf.savefig()
            plt.close()
        else:
            print(f'Warning: {wordcloud_image} does not exist and will be skipped.')

        # Citation Distribution Plot
        # fig = plot_citation_distribution(citation_count)  # Get the figure instance
        # pdf.savefig(fig)  # Save the returned figure
        # plt.close(fig)  # Ensure the figure is closed properly

        # Cosine Similarity Bar Plot
        if similarity_scores is not None:
            results_df = pd.DataFrame({
                'Reference Document': [os.path.basename(file) for file in reference_files],
                'Cosine Similarity': similarity_scores
            })
            results_df['Cosine Similarity Percentage'] = results_df['Cosine Similarity'] * 100

            plt.figure(figsize=(10, 6))
            sns.barplot(x='Reference Document', y='Cosine Similarity Percentage', data=results_df, palette='coolwarm')
            plt.title('Cosine Similarity')
            plt.xlabel('Reference Document')
            plt.ylabel('Cosine Similarity Percentage')
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
            'Reference Document': [os.path.basename(file) for file in reference_files],
            'BLEU Score': bleu_scores
        })
        results_df['BLEU Percentage'] = results_df['BLEU Score'] * 100

        plt.figure(figsize=(10, 6))
        sns.barplot(x='Reference Document', y='BLEU Percentage', data=results_df, palette='coolwarm')
        plt.title('BLEU Score')
        plt.xlabel('Reference Document')
        plt.ylabel('BLEU Percentage')
        plt.xticks(rotation=45)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    print(f'PDF report saved as {pdf_filename}')

    return jsonify({'message': 'Quality check graphs have been generated successfully'}), 200 