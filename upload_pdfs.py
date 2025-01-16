from langchain_community.document_loaders import PyPDFLoader, OnlinePDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
import os
import dotenv
import re

dotenv.load_dotenv()

def load_pdfs(file_paths):
    all_texts = []
    for file_path in file_paths:
        loader = PyPDFLoader(file_path=file_path)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(data)
        # Clean the text
        for text in texts:
            text.page_content = clean_text(text.page_content)
        all_texts.extend(texts)
        print (f'Loaded {len(texts)} documents from {file_path}')
        # in this case if len(text) which means number of text chunks == number of vectors -> successful
    return all_texts

def upsert_embeddings(texts, embeddings, index_name, namespace):
    # Extract text content from Document objects
    texts_content = [t.page_content for t in texts]
    docsearch = LangchainPinecone.from_texts(texts_content, embeddings, index_name=index_name, namespace=namespace)

def clean_namespace(index, namespace): 
    index.delete(delete_all=True, namespace=namespace) 

# Remove newlines, extra spaces and weird characters
def clean_text(text):
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[§†‡]', '', text)
    # Merge split words
    text = re.sub(r'\b(\w+)-\s+(\w+)\b', r'\1\2', text)
    return text.strip()

# Main code ----------------------------------------------------

# List of PDF file paths (group them for different namespaces)
namespaces = {
    "paper1": ["../RAG-project/papers/paper1.pdf"],
    "paper2": ["../RAG-project/papers/paper2.pdf"],
    "paper3": ["../RAG-project/papers/paper3.pdf"]
}

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

# Ensure the index exists
if 'my-index' not in pc.list_indexes().names():
    pc.create_index(
        name='my-index',
        dimension=1536,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1',
        )
    )
index_name = "my-index"

# Create Embeddings of the text
embeddings = OpenAIEmbeddings(api_key=os.getenv('OPENAI_API_KEY'))

# Get the index (for cleanup)
index = pc.Index(index_name)

# Process each namespace
for namespace, file_paths in namespaces.items():
    # database cleanup if namespace already exists
    stats = index.describe_index_stats()
    if namespace in stats['namespaces'] and stats['namespaces'][namespace]['vector_count'] > 0: 
        print(f'Namespace {namespace} already has vectors. Cleaning up before loading new data.') 
        clean_namespace(index, namespace) 
    else: 
        print(f'Namespace {namespace} is empty or does not exist. Proceeding with loading data.')
    
    # Load PDFs and upsert embeddings
    all_texts = load_pdfs(file_paths)
    upsert_embeddings(all_texts, embeddings, index_name, namespace)

print(f'Upserted documents into namespaces {list(namespaces.keys())}')
