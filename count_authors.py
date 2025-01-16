import os
import re
import dotenv
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone, ServerlessSpec
from collections import defaultdict

dotenv.load_dotenv()

# Initialize embeddings and Pinecone
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
pinecone = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

def extract_authors(text):
    # Use regular expressions to extract author names
    author_pattern = re.compile(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),?\s(?:M\.D\.|Ph\.D\.|D\.V\.M\.)')
    authors = author_pattern.findall(text)
    return authors if authors else ["Unknown Author"]

def count_papers_per_academic(texts):
    author_count = defaultdict(int)
    for text in texts:
        authors = extract_authors(text.page_content)
        for author in authors:
            author_count[author] += 1
    return author_count

def count_authors_across_namespaces(namespaces, index_name, embeddings):
    combined_author_count = defaultdict(int)
    for namespace in namespaces:
        print(f"Querying namespace: {namespace}")
        docsearch = LangchainPinecone.from_existing_index(index_name=index_name, namespace=namespace, embedding=embeddings)
        results = docsearch.similarity_search("dummy query", k=10)  # Adjust the query and k as needed
        author_count = count_papers_per_academic(results)
        for author, count in author_count.items():
            combined_author_count[author] += count
    return combined_author_count

# Main function
def main():
    namespaces = ['paper1', 'paper2', 'paper3']  # Namespaces for the papers
    index_name = 'my-index'  # Name of the Pinecone index
    author_count = count_authors_across_namespaces(namespaces, index_name, embeddings)
    
    print("\nFinal Author Counts:")
    for author, count in author_count.items():
        print(f"Author: {author}, Papers: {count}")

if __name__ == "__main__":
    main()