import os
import dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from process_pdf import pdf_to_text, split_text_into_chunks

# Load environment variables
dotenv.load_dotenv()

# Initialize API keys
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_ENV = "us-east-1"
INDEX_NAME = "my-index"

# Initialize Pinecone client (v3+)
pc = Pinecone(api_key=PINECONE_API_KEY)

# Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def get_text_embedding(text):
    """Convert text into vector embeddings using OpenAI embeddings."""
    return embeddings.embed_query(text)

def store_chunks_in_pinecone(text_chunks, namespace):
    """Stores document chunks as vectors in Pinecone DB (Pinecone 3.0)."""
    
    # Ensure index exists
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"⚠️ Index '{INDEX_NAME}' not found! Run `initialize_pinecone.py` first.")
        return

    # Connect to the existing Pinecone index
    index = pc.Index(INDEX_NAME)

    # Generate vector embeddings
    vectors = [(f"{namespace}-doc-{i}", get_text_embedding(chunk), {"text": chunk}) 
               for i, chunk in enumerate(text_chunks)]

    # Store vectors in Pinecone
    index.upsert(vectors)
    
    print(f"✅ Stored {len(text_chunks)} chunks in Pinecone under namespace '{namespace}'!")

def process_and_store_papers(directory="backend/papers"):
    """Process all PDFs in the given directory and store their embeddings in Pinecone."""
    
    if not os.path.exists(directory):
        print(f"⚠️ Directory '{directory}' not found.")
        return
    
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]

    if not pdf_files:
        print("⚠️ No PDF files found in the directory.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory, pdf_file)
        namespace = pdf_file.replace(".pdf", "")  # Use filename as namespace

        print(f"📄 Processing {pdf_file}...")

        text = pdf_to_text(pdf_path)
        chunks = split_text_into_chunks(text)

        print(f"🔄 Storing {len(chunks)} chunks in Pinecone under namespace '{namespace}'...")
        store_chunks_in_pinecone(chunks, namespace)

if __name__ == "__main__":
    process_and_store_papers()