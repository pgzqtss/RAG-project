from langchain_community.document_loaders import PyPDFLoader, OnlinePDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

file_path = "Users/pingho/RAG-project/example.pdf"

loader = PyPDFLoader(file_path=file_path)

data = loader.load()

# PyPDFLoader splits the document into pages
print(f'You have {len(data)} document(s) /pages in your data')
print(f'There are {len(data[0].page_content)} characters in your sample document')
# print(f'Here is a sample: {data[0].page_content[:500]}')

# Split the text into sentences (chunk size = 1000 characters)
# We need chunk overlap to maintain context between chunks for NLP
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(data)

print (f'Now you have {len(texts)} documents')

# Create Embeddings of the text
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
import os
import dotenv

dotenv.load_dotenv()

embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
# initialize pinecone
pc = Pinecone(
    api_key = os.getenv('PINECONE_API_KEY'),
)

if 'my-index' not in pc.list_indexes().names():
    pc.create_index(
        name='my-index',
        dimension=1536,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            ragion='us-east-1',
        )
    )
index_name = "my-index"

docsearch = LangchainPinecone.from_texts([t.page_content for t in texts], embeddings, index_name = index_name)
