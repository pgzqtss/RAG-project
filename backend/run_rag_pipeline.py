import os
import json
from tqdm import tqdm
from initialize_pinecone import initialize_pinecone
from preload_vector_db import preload_research_papers
from process_pdf import pdf_to_text, split_text_into_chunks
from store_to_pinecone import store_chunks_in_pinecone
from search_with_fallback import search_pinecone_with_fallback
from together import Complete
from pinecone import Pinecone
import openai


import dotenv

# ✅ Load environment variables
dotenv.load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# 📂 Define directories
INDEX_NAME = "my-index"
user_papers_dir = "backend/user_uploads"
output_dir = "backend/processed_texts"
output_path = os.path.join(output_dir, "systematic_review.json")

# ✅ Ensure directories exist
for directory in [user_papers_dir, output_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📂 Created missing directory: {directory}")

# ✅ Connect to Pinecone (only once)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

def check_if_preloaded_data_exists():
    """Check if preloaded research papers exist in Pinecone."""
    stats = index.describe_index_stats()
    namespaces = stats.get("namespaces", {})

    # Preloaded research papers typically have namespaces like "P1.1", "P2.1", "S3", etc.
    return any(ns.startswith("P") or ns.startswith("S") or ns.startswith("paper") for ns in namespaces)

def summarize_paper(paper_chunks):
    """Use OpenAI GPT to summarize a research paper into 3-4 structured paragraphs."""
    if not paper_chunks:
        return "⚠️ No data found to summarize."

    print(f"\n📊 Summarizing paper with {len(paper_chunks)} retrieved chunks...")

    joined_text = "\n\n".join(paper_chunks[:10])  # 只取前 10 个片段
    print(f"📄 Sample of text being summarized: {joined_text[:500]}...\n")  # 只打印前 500 个字符

    prompt = f"""
    You are a researcher. Summarize the following research paper into 3-4 paragraphs:
    - Background
    - Methods
    - Results
    - Conclusion

    Paper Content:
    {joined_text}

    Summary:
    """

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # ✅ 适配 OpenAI 新 API
        response = client.chat.completions.create(
            model="gpt-4",  # 你可以用 "gpt-3.5-turbo" 或 "gpt-4"
            messages=[
                {"role": "system", "content": "You are a helpful research assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Error during summarization: {e}")
        return "⚠️ Failed to summarize."

def generate_systematic_review(paper_summaries):
    """Combine multiple paper summaries into a structured systematic review using OpenAI GPT."""
    if not paper_summaries:
        return "⚠️ No summaries available for review."

    print(f"\n📖 Generating systematic review from {len(paper_summaries)} papers...")

    joined_summaries = "\n\n".join(paper_summaries)
    print(f"📄 Sample of summaries being compiled: {joined_summaries[:500]}...\n")

    prompt = f"""
    You are conducting a systematic review of research papers. Based on the following summaries, generate a final review covering:
    - Background
    - Methods
    - Results
    - Conclusions

    Summaries:
    {joined_summaries}

    Systematic Review:
    """

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # ✅ 适配 OpenAI 新 API
        response = client.chat.completions.create(
            model="gpt-4",  # 你可以用 "gpt-3.5-turbo" 或 "gpt-4"
            messages=[
                {"role": "system", "content": "You are a helpful research assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Error during systematic review generation: {e}")
        return "⚠️ Failed to generate review."

def main():
    # Step 1️⃣: **Initialize Pinecone (only if not already initialized)**
    if "PINECONE_INITIALIZED" not in globals():
        print("✅ Initializing Pinecone...")
        initialize_pinecone()
        global PINECONE_INITIALIZED
        PINECONE_INITIALIZED = True  # Prevent multiple initializations

    # Step 2️⃣: **Preload research papers only if missing**
    if not check_if_preloaded_data_exists():
        print("🔄 Preloading default research papers into Pinecone...")
        preload_research_papers()
    else:
        print("✅ Preloaded research papers already exist in Pinecone. Skipping preload.")

    # Step 3️⃣: **Process user-uploaded PDFs**
    user_files = [f for f in os.listdir(user_papers_dir) if f.endswith(".pdf")]

    if not user_files:
        print("⚠️ No user-uploaded PDFs found in 'backend/user_uploads/'. Please upload files first.")
        return

    paper_summaries = {}

    for pdf_file in tqdm(user_files, desc="Processing User Papers"):
        pdf_path = os.path.join(user_papers_dir, pdf_file)
        namespace = pdf_file.replace(".pdf", "")  # Use filename as namespace

        print(f"📄 Extracting text from {pdf_file}...")
        text = pdf_to_text(pdf_path)
        chunks = split_text_into_chunks(text)

        print(f"📦 Storing {len(chunks)} chunks in Pinecone under '{namespace}'...")
        store_chunks_in_pinecone(chunks, namespace=namespace)

        print(f"🔍 Retrieving top 10 relevant chunks for {pdf_file}...")
        retrieved_chunks = search_pinecone_with_fallback("What are the key findings?", namespace)

        print(f"📑 Summarizing {pdf_file}...")
        paper_summary = summarize_paper(retrieved_chunks)
        paper_summaries[namespace] = paper_summary

    # Step 4️⃣: Generate systematic review
    print("📖 Generating final systematic review...")
    final_review = generate_systematic_review(list(paper_summaries.values()))

    # Step 5️⃣: Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"papers": paper_summaries, "review": final_review}, f, indent=4, ensure_ascii=False)

    print(f"✅ Systematic review saved to {output_path}")

if __name__ == "__main__":
    main()
    exit(0)