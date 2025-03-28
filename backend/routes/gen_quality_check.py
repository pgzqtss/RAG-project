import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
from quality_check.cosine_similarity import CosineSimilarityChecker
from quality_check.TF_IDF import TFIDF
from quality_check.BLEU import BLEUScorer
from quality_check.author_num import process_pdfs, save_and_plot_results
from quality_check.themetic_area import load_documents, extract_thematic_area, generate_wordcloud
from utils.pdf_util import pdf_to_text, read_pdfs

from flask import jsonify, request
from __main__ import app

# Helper functions moved outside the route
def add_image_to_pdf(image_path, pdf):
    try:
        img = plt.imread(image_path)
        plt.figure(figsize=(10, 6))
        plt.imshow(img)
        plt.axis('off')
        pdf.savefig()
        plt.close()
    except Exception as e:
        print(f'Error adding {image_path} to PDF: {str(e)}')

def create_cosine_plot(pdf, reference_files, scores):
    if scores:
        df = pd.DataFrame({
            'Document': [os.path.basename(f) for f in reference_files],
            'Score': [s * 100 for s in scores]
        })
        plt.figure(figsize=(10, 6))
        sns.barplot(
            x='Document',
            y='Score',
            hue='Document',
            data=df,
            palette='coolwarm',
            legend=False
        )
        plt.title('Cosine Similarity Scores (%)')
        plt.xticks(rotation=45)
        pdf.savefig()
        plt.close()

def create_bleu_plot(pdf, reference_files, scores):
    if scores:
        df = pd.DataFrame({
            'Document': [os.path.basename(f) for f in reference_files],
            'Score': [s * 100 for s in scores]
        })
        plt.figure(figsize=(10, 6))
        sns.barplot(
            x='Document',
            y='Score',
            hue='Document',
            data=df,
            palette='coolwarm',
            legend=False
        )
        plt.title('BLEU Scores (%)')
        plt.xticks(rotation=45)
        pdf.savefig()
        plt.close()

def create_tfidf_heatmap(pdf, tfidf_results):
    if not tfidf_results.empty:
        top_words = tfidf_results.mean().nlargest(50).index
        plt.figure(figsize=(16, 10))
        sns.heatmap(tfidf_results[top_words], cmap='viridis')
        plt.title('TF-IDF Heatmap (Top 50 Terms)')
        pdf.savefig()
        plt.close()

@app.route('/api/quality_check', methods=['POST'])
def generate_quality_check_graphs():
    data = request.json
    id = data.get('id')


    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    input_path = os.path.join(base_dir, 'frontend', 'public', 'files', str(id))
    output_dir = os.path.join(base_dir, 'frontend', 'public', 'output', str(id))
    

    os.makedirs(input_path, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    try:
        reference_files, reference_docs = read_pdfs(input_path)
        hypothesis_doc = pdf_to_text(os.path.join(output_dir, 'systematic_review.pdf'))
    except Exception as e:
        return jsonify({'error': f'Document loading failed: {str(e)}'}), 500

    try:
        similarity_checker = CosineSimilarityChecker(reference_docs, hypothesis_doc)
        similarity_scores, _ = similarity_checker.calculate_similarity()

        documents = reference_docs + [hypothesis_doc]
        tfidf = TFIDF(documents)
        tfidf_results = tfidf.calculate_tfidf()

        bleu_scorer = BLEUScorer(reference_docs, hypothesis_doc)
        bleu_scores = bleu_scorer.calculate_bleu()

        author_counts = process_pdfs(input_path)
        author_counts_image = os.path.join(output_dir, 'author_counts.png')
        save_and_plot_results(author_counts=author_counts, output_image=author_counts_image, id=id)


        docs = load_documents(input_path)
        doc_areas = [extract_thematic_area(doc) for doc in docs]
        all_areas = [a.strip() for area_str in doc_areas for a in area_str.replace('\n', ' ').split(',') if a.strip()]
        wordcloud_image = os.path.join(output_dir, 'thematic_wordcloud.png')
        generate_wordcloud(areas=all_areas, output_file=wordcloud_image, id=id)

    except Exception as e:
        return jsonify({'error': f'Metric processing failed: {str(e)}'}), 500

    # Generate PDF report
    pdf_path = os.path.join(output_dir, 'quality_check_report.pdf')
    try:
        with PdfPages(pdf_path) as pdf:
            # Add author counts plot
            if os.path.exists(author_counts_image):
                add_image_to_pdf(author_counts_image, pdf)
            
            # Add word cloud
            if os.path.exists(wordcloud_image):
                add_image_to_pdf(wordcloud_image, pdf)

            # Cosine Similarity plot
            create_cosine_plot(pdf, reference_files, similarity_scores)

            # TF-IDF heatmap
            create_tfidf_heatmap(pdf, tfidf_results)

            # BLEU score plot
            create_bleu_plot(pdf, reference_files, bleu_scores)

        print(f'PDF report saved to {pdf_path}')
        return jsonify({'message': 'Quality check report generated successfully', 'path': pdf_path}), 200

    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500