import os
import dotenv
import re
import logging
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.docstore.document import Document
from pinecone import Pinecone

# ✅ Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Load environment variables
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

# ✅ Initialize OpenAI Embeddings and Pinecone
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
pinecone = Pinecone(api_key=PINECONE_API_KEY)

# ✅ Define the index name
index_name = "my-index"

# ✅ Function to clean text
def clean_text(text: str) -> str:
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[§†‡]', '', text)
    text = re.sub(r'\b(\w+)-\s+(\w+)\b', r'\1\2', text)
    return text.strip()

# ✅ Function to load and store text chunks into Pinecone
def load_texts(file_paths, paper_id):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    index = pinecone.Index(index_name)
    
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        doc = Document(page_content=content, metadata={"source": file_path})
        chunks = text_splitter.split_documents([doc])  # Split document into chunks

        for i, c in enumerate(chunks):
            c.page_content = clean_text(c.page_content)
            
            # Automatically classify section using LLM
            section = classify_chunk_with_llm(c.page_content)
            namespace = f"SYSTEMATIC_REVIEW/{paper_id}/{section}"
            
            # Store in Pinecone
            index.upsert([(f"{paper_id}-chunk-{i}", embeddings.embed_query(c.page_content), {"text": c.page_content, "source": paper_id, "section": section})])
        
        logger.info(f"Uploaded chunks from {file_path} into namespace '{namespace}'.")

# ✅ Function to classify chunk using LLM
def classify_chunk_with_llm(chunk):
    """ Uses LLM to classify text into a specific section of the systematic review """
    prompt = f"""
    You are an AI assistant classifying research paper sections.
    Determine which section this text belongs to: Background, Methods, Results, Discussion, Conclusion.

    ---TEXT---
    {chunk}
    ------------------
    
    Output only the section name:
    """
    
    model = ChatOpenAI(api_key=OPENAI_API_KEY)
    response = model.invoke(prompt).content.strip()
    
    valid_sections = {"Background", "Methods", "Results", "Discussion", "Conclusion"}
    return response if response in valid_sections else "Background"

# ✅ Function to search across specific papers and sections
def search_across_extra(query, index_name, embeddings, paper_id=None, section="Results", top_k=10):
    """ Searches for text chunks in Pinecone for a given Paper_ID and Section """

    # Construct namespace
    if paper_id:
        namespace = f"SYSTEMATIC_REVIEW/{paper_id}/{section}"
    else:
        namespace = f"SYSTEMATIC_REVIEW/*/{section}"  # Search across all papers for a specific section

    print(f"🔍 Searching Pinecone in namespace: '{namespace}' for query: '{query}'...")

    query_vector = embeddings.embed_query(query)

    # Query Pinecone index
    results = pinecone.Index(index_name).query(vector=query_vector, top_k=top_k, namespace=namespace, include_metadata=True)

    return [match["metadata"]["text"] for match in results["matches"]]

# ✅ Function to generate a systematic review
def generate_systematic_review(results, query, model):
    combined_content = "\n\n".join(results)
    prompt = f"""
    You are a researcher compiling a systematic review. Below is a collection of relevant text excerpts for the query: "{query}".
    Please generate a structured systematic review summarizing the key points, findings, and insights.

    ### Data:
    {combined_content}
    
    ### Systematic Review:
    """
    return model.invoke(prompt)

# ✅ Main Execution
if __name__ == "__main__":
    txt_dir = "../RAG-project/repodir"
    txt_dir_ab = "../RAG-project/repodir_ab"

    # Collect all text files
    txt_files = [os.path.join(txt_dir, fn) for fn in os.listdir(txt_dir) if fn.endswith(".txt") and os.path.isfile(os.path.join(txt_dir, fn))]
    text_ab_files = [os.path.join(txt_dir_ab, fn) for fn in os.listdir(txt_dir_ab) if fn.endswith(".txt") and os.path.isfile(os.path.join(txt_dir_ab, fn))]

    all_text_files = txt_files + text_ab_files

    # Load and store texts, using Paper_ID as filename (excluding ".txt")
    for file_path in all_text_files:
        paper_id = os.path.basename(file_path).replace(".txt", "")
        load_texts([file_path], paper_id)

    # Run a sample query
    query = "What is the efficacy of vaccines for COVID-19?"
    results = search_across_extra(
        query,
        index_name=index_name,
        embeddings=embeddings,
        section="Results",  # Default to searching in Results
        top_k=10
    )

    model = ChatOpenAI(api_key=OPENAI_API_KEY)
    review = generate_systematic_review(results, query, model)
    print(review.content)