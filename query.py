import os
import dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

dotenv.load_dotenv()
pinecone_api_key = os.getenv('PINECONE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialise Pinecone and OpenAI embedding
pinecone = Pinecone(api_key=pinecone_api_key)
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

index_name = 'test'

# Get all the vectors from index with namespace
vector_store = PineconeVectorStore(
    index_name=index_name, 
    embedding=embeddings,
    namespace=''
)

query = 'What is the history of natural language processing?'

# Finds the 1 vector most similar to the query
vector_store.similarity_search(query, k=1)