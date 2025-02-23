# services/pdf_processing_service.py
import os
from tqdm import tqdm
from utils.pdf_util import pdf_to_text
from utils.text_splitter import split_text_into_chunks
from services.upsert_pinecone_service import upsert_all_chunks
from config import USER_PAPERS_DIR

def process_and_store_all_pdfs():
    '''Processes user-uploaded PDFs and stores embeddings in Pinecone.'''
    
    user_files = [f for f in os.listdir(USER_PAPERS_DIR) if f.endswith('.pdf')]

    if not user_files:
        print('⚠️ No user-uploaded PDFs found in "backend/user_uploads/". Please upload files first.')
        return
    
    for pdf_file in tqdm(user_files, desc='Processing User Papers'): 
        pdf_path = os.path.join(USER_PAPERS_DIR, pdf_file)
        paper_id = pdf_file.replace('.pdf', '')  # Use filename as namespace

        print(f'📄 Extracting text from {pdf_file}...')
        text = pdf_to_text(pdf_path)
        text_chunks = split_text_into_chunks(text)  # Now returns classified sections

        print(f'📦 Storing {len(text_chunks)} chunks in Pinecone under {paper_id} ...')
        upsert_all_chunks(text_chunks=text_chunks, paper_id=paper_id)