from services.pinecone_service import initialise_pinecone
from services.pdf_processing_service import process_and_store_all_pdfs

def init_pinecone():
  try:
    initialise_pinecone()
  except Exception as e:
    print(f"Error initializing Pinecone: {e}")

  try:
    process_and_store_all_pdfs()
  except Exception as e:
    print(f"Error processing and storing PDFs: {e}")