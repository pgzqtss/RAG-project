from process_pdf import pdf_to_text, split_text_into_chunks
from store_to_pinecone import store_chunks_in_pinecone
from initialize_pinecone import initialize_pinecone
from tqdm import tqdm
import os

def preload_research_papers():
    """ Preloads a set of research papers into Pinecone. """
    initialize_pinecone()  # Ensure Pinecone is initialized

    preloaded_papers = {
        "P1.1": [r"backend\papers\P1.1.pdf"],
        "P1.2": [r"backend\papers\P1.2.pdf"],
        "P1.3": [r"backend\papers\P1.3.pdf"],
        "P2.1": [r"backend\papers\P2.1.pdf"],
        "P2.2": [r"backend\papers\P2.2.pdf"],
        "P2.3": [r"backend\papers\P2.3.pdf"],
        "P2.4": [r"backend\papers\P2.4.pdf"],
        "P2.5": [r"backend\papers\P2.5.pdf"],
        "P3.1": [r"backend\papers\P3.1.pdf"],
        "P3.2": [r"backend\papers\P3.2.pdf"],
        "P3.3": [r"backend\papers\P3.3.pdf"],
        "P3.4": [r"backend\papers\P3.4.pdf"],
        "P3.5": [r"backend\papers\P3.5.pdf"],
        "S1": [r"backend\papers\S1.pdf"],
        "S2": [r"backend\papers\S2.pdf"],
        "S3": [r"backend\papers\S3.pdf"],
        "paper1": [r"backend\papers\paper1.pdf"],
        "paper2": [r"backend\papers\paper2.pdf"],
        "paper3": [r"backend\papers\paper3.pdf"],
    }

    for paper_name, pdf_paths in tqdm(preloaded_papers.items(), desc="Preloading Papers"):
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                print(f"Skipping {pdf_path} (file not found).")
                continue

            text = pdf_to_text(pdf_path)
            chunks = split_text_into_chunks(text)
            store_chunks_in_pinecone(chunks, namespace=paper_name)

    print("✅ Preloading complete!")

if __name__ == "__main__":
    preload_research_papers()