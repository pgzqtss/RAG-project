import os
from tqdm import tqdm
from process_pdf import pdf_to_text, split_text_into_chunks
from store_to_pinecone import store_chunks_in_pinecone

def preload_research_papers(directory="backend/preload_papers"):
    """Process and store preloaded research papers into Pinecone."""

    if not os.path.exists(directory):
        print(f"⚠️ Directory '{directory}' not found.")
        return

    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]

    if not pdf_files:
        print("⚠️ No preloaded PDFs found.")
        return

    for pdf_file in tqdm(pdf_files, desc="Preloading Papers"):
        pdf_path = os.path.join(directory, pdf_file)
        paper_name = pdf_file.replace(".pdf", "")  # Use filename as paper ID

        print(f"📄 Extracting text from {pdf_file}...")
        text = pdf_to_text(pdf_path)
        classified_chunks = split_text_into_chunks(text)  # Returns classified sections

        print(f"📦 Storing {len(classified_chunks)} chunks in Pinecone under '{paper_name}'...")
        store_chunks_in_pinecone(classified_chunks, paper_id=paper_name)  # ✅ Fixed Argument

    print("✅ Preloaded all research papers into Pinecone.")

if __name__ == "__main__":
    preload_research_papers()
