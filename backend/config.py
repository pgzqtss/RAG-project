import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from sentence_transformers import SentenceTransformer

load_dotenv()
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')

# ✅ Define directories
USER_PAPERS_DIR = 'backend/user_uploads'
OUTPUT_DIR = 'backend/processed_texts'
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'systematic_review.json')

# Pinecone Index Initialisation 
SEARCH_METRIC = 'cosine'
SPEC_CLOUD = 'aws'
SPEC_REGION = 'us-east-1'
VECTOR_DIMENSION = 1536  # OpenAI Embeddings dimension

# MySQL Initialisation
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
DATABASE_NAME = 'user_data'

pinecone = Pinecone(api_key=PINECONE_API_KEY)
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
model = ChatOpenAI(api_key=OPENAI_API_KEY, 
                  model='gpt-3.5-turbo',
                  temperature=0)

# Load BERT model for similarity-based filtering
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

# Define length constraints for different sections (words)
SECTION_LENGTH_LIMITS = {
    'Background': 1200, 
    'Methods': 1500, 
    'Results': 2500,
    'Discussion': 3000,
    'Conclusion': 600, 
}

# Define the character limit for each section for use in context prompt
SECTION_CHAR_LIMIT = 2000