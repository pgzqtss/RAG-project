import os
import pinecone
import dotenv

# Load API keys
dotenv.load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = "us-east-1"
INDEX_NAME = "my-index"
VECTOR_DIMENSION = 1536  # OpenAI Embeddings dimension

# New way to initialize Pinecone (v3+)
from pinecone import Pinecone, ServerlessSpec

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

def initialize_pinecone():
    """ Initializes Pinecone and creates an index if it doesn't exist. """
    
    # Check if index exists, if not create it
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating Pinecone index: {INDEX_NAME}...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=VECTOR_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'  
            )
        )
        print(f"Index '{INDEX_NAME}' created successfully!")
    else:
        print(f"Index '{INDEX_NAME}' already exists.")

if __name__ == "__main__":
    initialize_pinecone()