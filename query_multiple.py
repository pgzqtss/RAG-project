
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone, ServerlessSpec
import os
import dotenv

# Initialize embeddings and Pinecone

dotenv.load_dotenv()
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
pinecone = Pinecone(api_key='PINECONE_API_KEY')

def search_across_namespaces(query, index_name, embeddings, namespaces, top_k=5):
    combined_results = []
    for namespace in namespaces:
        print(f"Searching in namespace: {namespace}")
        # Initialize the Pinecone vector store for the namespace
        docsearch = LangchainPinecone.from_existing_index(index_name=index_name, namespace=namespace, embedding=embeddings)
        # Perform the similarity search
        results = docsearch.similarity_search(query, k=top_k)
        combined_results.extend(results)
    return combined_results

def generate_systematic_review(results, query, model):
    # Combine the contents of the results
    combined_content = "\n\n".join([res.page_content for res in results])
    
    # Create a prompt for systematic review
    prompt = f"""
    You are a researcher. Here is a collection of text chunks relevant to the query: "{query}".
    Please generate a systematic review summarizing the key points, findings, and insights.

    Data:
    {combined_content}
    
    Systematic Review:
    """
    return model.invoke(prompt)

# Perform search across namespaces
query = "What are the recent advancements in vaccines for COVID-19?"
namespaces = ['paper1','paper2','paper3']  # List of namespaces
index_name = 'meow'
results = search_across_namespaces(query, index_name=index_name, embeddings=embeddings, namespaces=namespaces)

# Generate systematic review 
model = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Use your LLM
review = generate_systematic_review(results, query, model)
print(review)