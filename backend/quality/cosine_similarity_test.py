import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
import os
import dotenv
import re

dotenv.load_dotenv()

# Initialize Pinecone and embeddings
pinecone = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
embeddings = OpenAIEmbeddings(api_key=os.getenv('OPENAI_API_KEY'))

def preprocess_text(text):
    return re.sub(r'[^\x00-\x7F]+', ' ', text)

def load_embeddings(index_name, namespace):
    return LangchainPinecone.from_existing_index(
        index_name=index_name, 
        namespace=namespace,
        embedding=embeddings
    )

def fetch_embeddings(docsearch):
    try:
        docs = docsearch.similarity_search("", k=1)
        if not docs:
            return np.zeros(1536)  # Already a numpy array
        
        raw_content = docs[0].page_content
        preprocessed_content = preprocess_text(raw_content)
        # Convert OpenAI embedding list to numpy array
        return np.array(embeddings.embed_query(preprocessed_content))
    except Exception as e:
        print(f"Error in {docsearch.namespace}: {str(e).encode('ascii', 'ignore').decode()}")
        return np.zeros(1536)  # Already a numpy array

# Main logic
index_name = 'my-index'
p1_namespaces = ["P1.1", "P1.2", "P1.3"]
s1_namespace = "S1"

# Get embeddings for P1 group
p1_embeddings = []
for ns in p1_namespaces:
    vectorstore = load_embeddings(index_name, ns)
    embedding = fetch_embeddings(vectorstore)
    if not np.all(embedding == 0):  # Skip zero vectors
        p1_embeddings.append(embedding)

# Get S1 embedding
s1_vectorstore = load_embeddings(index_name, s1_namespace)
s1_embedding = fetch_embeddings(s1_vectorstore)

if not p1_embeddings or np.all(s1_embedding == 0):
    print("Error: Missing required embeddings")
else:
    # Ensure all embeddings are numpy arrays
    p1_avg_embedding = np.mean(p1_embeddings, axis=0).reshape(1, -1)
    s1_embedding = s1_embedding.reshape(1, -1)  # Now works with numpy array
    
    similarity_score = cosine_similarity(p1_avg_embedding, s1_embedding)[0][0] * 100
    print(f"Similarity between P1-group and S1: {similarity_score:.2f}%")