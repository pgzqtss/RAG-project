import os
import dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA  
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

query = 'What is the brief history of natural language processing?'
retriever = vector_store.as_retriever(search_kwargs={"k": 10}) # k most similar vectors

llm = ChatOpenAI(  
    openai_api_key=openai_api_key,  
    model_name='gpt-3.5-turbo',  
    temperature=0.0  
)  

# Asks ChatGPT using only data from the vector store
qa = RetrievalQA.from_chain_type(  
    llm=llm,  
    chain_type="stuff",  
    retriever=retriever  
)  

a = qa.invoke(query)  
print(a)