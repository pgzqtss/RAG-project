import os
import dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from process_pdf import pdf_to_text, split_text_into_chunks

# ✅ Load environment variables
dotenv.load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "my-index"

# ✅ Connect to Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# ✅ Ensure index exists
if INDEX_NAME not in pc.list_indexes().names():
    raise ValueError(f"⚠️ Index '{INDEX_NAME}' not found! Run `initialize_pinecone.py` first.")

index = pc.Index(INDEX_NAME)

# ✅ Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# ✅ Initialize LLM model
llm_model = ChatOpenAI(api_key=OPENAI_API_KEY)

def classify_chunk_with_llm(chunk_text, model):
    """Classifies a text chunk into Background, Methods, Results, Discussion, or Conclusion using LLM."""
    prompt = f"""
    You are an AI assistant classifying research paper sections.
    The following text is an excerpt from a scientific paper.
    Determine whether it belongs to one of these sections:
    - Background
    - Methods
    - Results
    - Discussion
    - Conclusion

    If uncertain, choose the most relevant section.

    ---TEXT---
    {chunk_text}
    ------------------
    
    Output only the section name: 
    """

    try:
        response = model.invoke(prompt).content.strip()
        valid_sections = {"Background", "Methods", "Results", "Discussion", "Conclusion"}\
        
        classification = response if response in valid_sections else "Background"
        print(f"✅ LLM classified chunk as '{classification}'")
        return classification
    except Exception as e:
        print(f"⚠️ LLM classification failed: {e}. Defaulting to 'Background'.")
        return "Background"

def get_text_embedding(text):
    """Convert text into vector embeddings using OpenAI embeddings."""
    if not isinstance(text, str):
        raise TypeError("❌ get_text_embedding() received a non-string input.")

    return embeddings.embed_query(text)

def store_chunks_in_pinecone(text_chunks, paper_id):
    """Stores document chunks in Pinecone DB under Systematic Review namespaces."""

    global index  
    if INDEX_NAME not in pc.list_indexes().names():
        raise ValueError(f"⚠️ Index '{INDEX_NAME}' not found! Run `initialize_pinecone.py` first.")

    index = pc.Index(INDEX_NAME)

    # ✅ Get existing namespaces to avoid re-storing sections
    index_stats = index.describe_index_stats()
    existing_namespaces = index_stats.get("namespaces", {})

    # ✅ Instead of skipping the whole paper, only skip already stored sections
    stored_sections = {ns.split("/")[-1] for ns in existing_namespaces if ns.startswith(f"SYSTEMATIC_REVIEW/{paper_id}")}

    # ✅ Process each chunk separately
    for i, chunk in enumerate(text_chunks):
        if "text" not in chunk or not isinstance(chunk["text"], str):
            print(f"⚠️ Skipping invalid chunk {i} for '{paper_id}'.")
            continue

        # ✅ Call LLM for classification and ensure it's printed
        section = classify_chunk_with_llm(chunk["text"], llm_model)
        print(f"🔍 Chunk {i} classified as: {section}")  # ✅ Ensure we see LLM classification

        namespace = f"SYSTEMATIC_REVIEW/{paper_id}/{section}"

        # ✅ Skip storing chunks for sections that already exist
        if section in stored_sections:
            print(f"⚠️ Skipping chunk {i} (already stored in {namespace}).")
            continue

        vector = get_text_embedding(chunk["text"])

        # ✅ Explicitly store under correct namespace
        index.upsert([
            (
                f"{paper_id}-chunk-{i}",
                vector,
                {
                    "text": chunk["text"],
                    "source": paper_id,
                    "section": section
                }
            )
        ], namespace=namespace)

        print(f"✅ Stored chunk {i} in Pinecone under '{namespace}'!")

    print(f"✅ Successfully stored {len(text_chunks)} chunks in Pinecone under '{paper_id}'!")





def process_and_store_papers(directory="backend/papers"):
    """Processes all PDFs in the given directory and stores their embeddings in Pinecone."""
    
    if not os.path.exists(directory):
        print(f"⚠️ Directory '{directory}' not found.")
        return

    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]

    if not pdf_files:
        print("⚠️ No PDF files found in the directory.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory, pdf_file)
        paper_id = pdf_file.replace(".pdf", "")  # Use filename as paper ID

        print(f"📄 Processing {pdf_file}...")

        text = pdf_to_text(pdf_path)

        if not text:
            print(f"⚠️ Skipping '{pdf_file}' (empty or unreadable).")
            continue

        classified_chunks = split_text_into_chunks(text)  # ✅ Returns classified dictionary chunks

        print(f"🔄 Storing {len(classified_chunks)} chunks in Pinecone under '{paper_id}'...")
        store_chunks_in_pinecone(classified_chunks, paper_id)  # ✅ Pass structured chunks

if __name__ == "__main__":
    process_and_store_papers()
