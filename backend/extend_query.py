import os
import dotenv
import re
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.docstore.document import Document
from pinecone import Pinecone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')


embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)


pinecone = Pinecone(api_key=PINECONE_API_KEY)


index_name = "my-index"
txtfiles_namespace = "txtfiles"


txt_vectorstore = LangchainPinecone.from_existing_index(
    index_name=index_name,
    namespace=txtfiles_namespace,
    embedding=embeddings
)

txt_dir = "../RAG-project/repodir"
txt_dir_ab = "../RAG-project/repodir_ab"

def clean_text(text: str) -> str:
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[§†‡]', '', text)
    text = re.sub(r'\b(\w+)-\s+(\w+)\b', r'\1\2', text)
    return text.strip()

def load_texts(file_paths):

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()


        doc = Document(page_content=content, metadata={"source": file_path})
        # 分块
        chunks = text_splitter.split_documents([doc])


        for c in chunks:
            c.page_content = clean_text(c.page_content)
            txt_vectorstore.add_texts([c.page_content], metadatas=[c.metadata])
        logger.info(f"Uploaded chunks from {file_path} into namespace '{txtfiles_namespace}'.")


def search_across_extra(query, index_name, embeddings, namespaces, top_k=10):

    combined_results = []
    for ns in [namespaces]: 
        print(f"Searching in namespace: {ns}")
        docsearch = LangchainPinecone.from_existing_index(
            index_name=index_name,
            namespace=ns,
            embedding=embeddings
        )
        results = docsearch.similarity_search(query, k=top_k)
        combined_results.extend(results)
    return combined_results

def generate_systematic_review(results, query, model):
    combined_content = "\n\n".join([res.page_content for res in results])
    prompt = f"""
    You are a researcher. Here is a collection of text chunks relevant to the query: "{query}".
    Please generate a large systematic review summarising the key points, findings, and insights.

    Data:
    {combined_content}
    
    Systematic Review:
    """
    return model.invoke(prompt)

if __name__ == "__main__":
    txt_files = []
    for fn in os.listdir(txt_dir):
        full_path = os.path.join(txt_dir, fn)
        if fn.endswith(".txt") and os.path.isfile(full_path):
            txt_files.append(full_path)

    text_ab_files = []
    for fn in os.listdir(txt_dir_ab):
        full_path = os.path.join(txt_dir_ab, fn)
        if fn.endswith(".txt") and os.path.isfile(full_path):
            text_ab_files.append(full_path)

    all_text_files = txt_files + text_ab_files
    load_texts(all_text_files)


    query = "What is the efficacy of vaccines for COVID-19?"
    results = search_across_extra(
        query,
        index_name=index_name,
        embeddings=embeddings,
        namespaces=txtfiles_namespace,
        top_k=10
    )

    model = ChatOpenAI(api_key=OPENAI_API_KEY)
    review = generate_systematic_review(results, query, model)
    print(review.content)
