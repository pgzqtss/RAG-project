from tqdm import tqdm
from utils.pdf_util import pdf_to_text
from utils.text_splitter import split_text_into_chunks
from services.upsert_pinecone_service import upsert_all_chunks
from utils.get_files import get_files
from flask import jsonify

def process_and_store_all_pdfs(id):
    '''Processes user-uploaded PDFs and stores embeddings in Pinecone.'''
    try:
      files = get_files(id)
      print(f'Files: {files}')
    except Exception as e:
        print(f'error: {str(e)}')
        return jsonify({'error': str(e)}), 500

    if not files:
        print('⚠️ No user-uploaded PDFs found in "../files/".')
        return
    
    for file in tqdm(files, desc='Processing User Papers'): 
        path = files[file]
        print(f'File {file}')
        print(f'Path {path}')

        print(f'📄 Extracting text from {file}...')
        text = pdf_to_text(path)
        text_chunks = split_text_into_chunks(text)  # Now returns classified sections

        print(f'📦 Storing {len(text_chunks)} chunks in Pinecone under {file} ...')
        upsert_all_chunks(text_chunks=text_chunks, paper_id=file)