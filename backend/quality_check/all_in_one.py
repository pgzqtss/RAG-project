import os
import re
import platform
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pdfplumber
from wordcloud import WordCloud
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import chardet
from collections import Counter
from tenacity import retry, stop_after_attempt, wait_random
from matplotlib.backends.backend_pdf import PdfPages

from citation_check import analyze_document, plot_citation_distribution
from cosine_similarity import CosineSimilarityChecker, read_pdfs_from_folder, read_pdf
from TF_IDF import TFIDF
from BLEU import BLEUScorer
from author_num import process_pdfs  # Import author processing function

# OpenAI API Key
openai_api_key = "your api key here"
llm = ChatOpenAI(api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0)

# Detect OS and set font path
if platform.system() == "Windows":
    font_path = "C:/Windows/Fonts/Arial.ttf"
elif platform.system() == "Darwin":
    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
else:
    font_path = None 

MEDICAL_STOPWORDS = {
    'cid', 'www', 'http', 'https', 'figure', 'table', 'equation',
    'section', 'pp', 'vol', 'no', 'et al', 'eg', 'ie', 'vs', 'fig',
    'doi', 'copyright', 'author', 'year', 'study', 'result', 'method',
    'conclusion', 'introduction', 'background', 'objective', 'purpose'
}

# Paths
input_folder = os.path.join(os.path.dirname(__file__), "../papers/papers")
output_doc = os.path.join(os.path.dirname(__file__), "../output.txt")

# Load documents
def load_documents(folder_path):
    documents = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        try:
            if file_name.lower().endswith('.pdf'):
                with pdfplumber.open(file_path) as pdf:
                    text_pages = [page.extract_text() for page in pdf.pages if page.extract_text()]
                    documents.append('\n'.join(text_pages))
            elif file_name.lower().endswith(('.txt', '.md')):
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
                documents.append(raw_data.decode(encoding, errors='ignore'))
        except Exception as e:
            print(f"Failed to process {file_name}: {e}")
    return documents

@retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
def extract_thematic_area(text):
    sample_text = text[:6000]  # Take a sample portion
    prompt = f"Extract 5-10 thematic areas from the following medical text (comma-separated):\n\n{sample_text}"
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"Thematic area extraction failed: {e}")
        return ""

# Processing
reference_files, reference_docs = read_pdfs_from_folder(input_folder)
hypothesis_doc = read_pdf(output_doc)
citation_count = analyze_document(output_doc)

# Cosine Similarity
similarity_checker = CosineSimilarityChecker(reference_docs, hypothesis_doc)
similarity_scores, overall_score = similarity_checker.calculate_similarity()

documents = load_documents(input_folder)
doc_areas = [extract_thematic_area(doc) for doc in documents]

# Process author count
author_counts = process_pdfs(input_folder)

def generate_wordcloud(areas, output_path="thematic_wordcloud.png"):
    filtered = [re.sub(r'\s+', ' ', a.strip().lower()) for a in areas if a.strip() and a.strip().lower() not in MEDICAL_STOPWORDS]
    freq = Counter(filtered)
    wc = WordCloud(width=1200, height=800, font_path=font_path, background_color="white", colormap="viridis").generate_from_frequencies(freq)
    plt.figure(figsize=(12, 8))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

# Generate Word Cloud
generate_wordcloud([item for sublist in doc_areas for item in sublist.split(',')])

top10_thematic = Counter([x.strip().lower() for sublist in doc_areas for x in sublist.split(',')]).most_common(10)
df_top10 = pd.DataFrame(top10_thematic, columns=["ThematicArea", "Count"])

# Create PDF Report
pdf_filename = 'quality_check_report.pdf'
with PdfPages(pdf_filename) as pdf:
    fig = plot_citation_distribution(citation_count)
    pdf.savefig(fig)
    plt.close(fig)
    
    if similarity_scores:
        df_similarity = pd.DataFrame({"Reference Document": [os.path.basename(f) for f in reference_files], "Cosine Similarity": similarity_scores})
        df_similarity["Cosine Similarity"] *= 100
        plt.figure(figsize=(10, 6))
        sns.barplot(x="Reference Document", y="Cosine Similarity", data=df_similarity, palette="coolwarm")
        plt.xticks(rotation=45)
        plt.title("Cosine Similarity")
        pdf.savefig()
        plt.close()
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df_top10, x="Count", y="ThematicArea", palette="viridis")
    plt.title("Top 10 Thematic Areas")
    plt.tight_layout()
    pdf.savefig()
    plt.close()

    df_authors = pd.DataFrame(author_counts.items(), columns=["Author", "Count"]).sort_values(by="Count", ascending=False)
    plt.figure(figsize=(10, 6))
    df_authors.head(10).plot(kind="bar", x="Author", y="Count", legend=False)
    plt.title("Top 10 Frequent Authors")
    plt.xlabel("Author Name")
    plt.ylabel("Count")
    pdf.savefig()
    plt.close()

print(f"PDF report saved as {pdf_filename}")
