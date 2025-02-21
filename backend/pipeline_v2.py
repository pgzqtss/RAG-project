import os
import json
from tqdm import tqdm
from langchain_openai import ChatOpenAI
import dotenv
import textwrap
from sentence_transformers import SentenceTransformer, util
import torch

# ✅ Load environment variables
dotenv.load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Define directories
INDEX_NAME = "fuck"
USER_PAPERS_DIR = "backend/user_uploads"
OUTPUT_DIR = "backend/processed_texts"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "systematic_review.json")

# ✅ Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Initialize LLM model
model = ChatOpenAI(api_key=OPENAI_API_KEY,
                   model='gpt-3.5-turbo',
                   temperature=0)

def generate_background_section(results, query, model, chunk_size=5):
    """单独生成 Background 章节"""
    section_title = "Background"
    section_prompt = textwrap.dedent(f"""
        {section_title}
                                        
        Generate the {section_title} section for the systematic review using the relevant information from the retrieved documents. 
        Integrate findings directly from the provided sources and ensure all claims are supported by the retrieved evidence.

        🔹 Required Content:
            1.	Introduction to the Topic:
                •	Introduce the research topic and highlight its significance using insights from the most relevant retrieved documents.
                •	Define essential concepts based on the retrieved material, ensuring consistency with the latest research.
                •	Discuss the broader relevance of the topic, drawing on real-world examples or applications mentioned in the retrieved sources.
            2.	Summary of Existing Literature:
                •	Summarize key findings from the retrieved documents, focusing on significant trends, major discoveries, and methodologies.
                •	Critically assess the strengths, limitations, and relevance of the studies retrieved.
                •	Address inconsistencies or conflicting evidence found in the sources, offering possible explanations or highlighting gaps.
            3.	Justification for This Systematic Review:
                •	Clearly explain why this review is necessary based on the gaps or unresolved issues identified in the retrieved documents.
                •	Describe how this review will address limitations or contribute new insights beyond what the retrieved studies have already established.
                •	Define the research question clearly. Use frameworks like PICO (Population, Intervention, Comparison, Outcome) only if supported by the retrieved material.

        🔹 Writing Style and Source Integration Guidelines:

        ✅ Use a formal, academic tone appropriate for scholarly work
        ✅ Prioritize evidence from the retrieved sources to support all claims
        ✅ Avoid including information not supported by the retrieved evidence.
        ✅ Address conflicting information from different sources, providing analysis or explanation
        ✅ Focus on depth and relevance—highlight the most pertinent findings
        ✅ Adapt the depth of each section based on the relevance and strength of the retrieved evidence
    """).strip()
    return generate_section(results, query, model, section_title, section_prompt, chunk_size)


def generate_methods_section(results, query, model, chunk_size=5):
    """Generate the Methods section for a Systematic Review following PRISMA guidelines."""
    
    section_title = "Methods"
    section_prompt = textwrap.dedent(f"""
        {section_title}
                                     
        Generate the {section_title} section for the Systematic Review using relevant information retrieved through a RAG system. 
        The output should follow the structure of a systematic review, emphasizing clarity, logical flow, and evidence-based reasoning.

        🔹 Required Content:
            1.	Study Design:
                •	Specify this is a Systematic Review.
                •	State that the methodology aligns with PRISMA guidelines where applicable, focusing on transparency and reproducibility.
            2.	Evidence Synthesis:
                •	Summarize the key themes and findings from the retrieved research.
                •	Highlight any consistent patterns, agreements, or notable contrasts in the evidence.
            3.	Inclusion Rationale:
                •	Emphasize the relevance of the information retrieved to the query.
                •	Clearly explain why certain insights were prioritized (e.g. relevance to the research question, recent developments).
            4.	Strengths and Limitations of Retrieved Information:
                •	Discuss the general strengths of the body of information retrieved.
                •	Note any potential gaps, such as limited coverage or conflicting information.
            5.	Key Insights Summary:
                •	Present major findings, outcomes, or conclusions derived from the available data.
                •	Focus on clear, concise summaries without requiring detailed statistical breakdowns.

        🔹 Writing Style:

        ✅ Clear, structured, and evidence-informed
        ✅ No citations required—focus on summarizing key points
        ✅ Present insights logically, highlighting relevance to the research query  
    """).strip()

    return generate_section(results, query, model, section_title, section_prompt, chunk_size)


def generate_results_section(results, query, model, chunk_size=5):
    """Generate the Results section for a Systematic Review."""

    section_title = "Results"
    section_prompt = textwrap.dedent(f"""
        {section_title}                             

        Generate the {section_title} section for the Systematic Review using relevant information retrieved through a RAG system. Structure the content logically and focus on summarizing the key findings from the retrieved information.

        🔹 Required Content:
            1.	Relevant Information Summary:
                •	Provide a general overview of the information retrieved that is relevant to the research query.
                •	Focus on summarizing the main themes and findings present across the retrieved documents.
            2.	Study Types and Methodological Insights (If Available):
                •	Briefly describe any study types or methodological details that appear in the retrieved information (e.g., experimental research, observational analysis).
                •	Only include this information if it is explicitly mentioned in the retrieved content.
            3.	Key Findings and Themes:
                •	Present a clear, concise summary of major findings from the retrieved content.
                •	Highlight recurring themes or notable differences, without inferring patterns from incomplete information.
            4.	General Observations and Gaps:
                •	Mention any apparent gaps in the retrieved information, such as missing data on certain outcomes or study populations.
                •	Avoid making assumptions—only report what is supported by the retrieved content.

        🔹 Writing Style:

        ✅ Focused on clear, unbiased summaries
        ✅ Only present information directly supported by retrieved content
        ✅ Flexible structure, prioritizing relevance over strict formatting
    """).strip()

    return generate_section(results, query, model, section_title, section_prompt, chunk_size)


def generate_discussion_section(results, query, model, chunk_size=5):
    """Generate the Discussion section for a Systematic Review."""

    section_title = "Discussion"
    section_prompt = textwrap.dedent(f"""
        {section_title}

        Generate the {section_title} section for the Systematic Review using relevant information retrieved through a RAG system. 
        Focus on summarizing the most relevant findings, clearly presenting insights while acknowledging any gaps or inconsistencies.

        🔹 Required Content:
            1.	Summary of Main Findings:
                •	Concisely summarize the key results from the retrieved content.
                •	Highlight consistent themes and acknowledge any conflicting information without attempting to resolve discrepancies.
            2.	Interpretation of Findings:
                •	Discuss potential explanations supported by the retrieved evidence.
                •	Where applicable, note any preliminary findings or well-established conclusions relevant to the research topic.
            3.	Strengths and Limitations of Retrieved Information:
                •	Describe strengths of the available information (e.g., relevance, breadth of coverage).
                •	Address limitations, including gaps, conflicting findings, or lack of depth in the retrieved content.
            4.	Potential Areas for Future Research:
                •	Suggest general future research directions based on observed gaps or trends in the retrieved evidence.
                •	Avoid proposing specific methodological recommendations unless explicitly supported by the retrieved information.

        🔹 Additional Guidelines:

        ✅ Prioritize the most relevant and clearly supported findings
        ✅ Acknowledge conflicting evidence without resolving it
        ✅ Use cautious, evidence-based language (e.g., “may suggest,” “potentially indicates”)
        ✅ Clearly state when information is incomplete or lacking depth 
    """).strip()

    return generate_section(results, query, model, section_title, section_prompt, chunk_size)


def generate_conclusion_section(results, query, model, chunk_size=5):
    """Generate the Conclusion section for a Systematic Review."""

    section_title = "Conclusion"
    section_prompt = textwrap.dedent(f"""
        {section_title}

        Generate the {section_title} section for a Systematic Review using the following structure and guidelines:

        🔹 Required Content:

        1.  Concise Summary of Key Findings:
            •   Summarize the most critical findings from the study, focusing on outcomes that are strongly supported by the retrieved evidence.
            •   Ensure the summary is clear, concise, and directly tied to the data retrieved by the RAG system.
        2.  Clinical & Public Health Implications:
            •   Highlight practical implications for healthcare practice or policy, based on the retrieved evidence.
            •   Clearly state limitations and uncertainties to avoid overgeneralization.
            •   Use cautious language (e.g., "may suggest," "could potentially") when discussing implications that are not definitively supported by the evidence.
        3.  Final Recommendations:
            •   Propose specific, actionable next steps for research or practice, addressing gaps or limitations identified in the retrieved evidence.
            •   Avoid generic statements like "more research is needed"—instead, specify the type of research or areas requiring further investigation.
            •   Ensure recommendations are grounded in the findings and directly linked to the retrieved data.
        🔹 Writing Style:

        ✅ Evidence-based and precise: Use only information retrieved by the RAG system. Do not introduce new ideas or unsupported claims.
        ✅ Structured and logical: Ensure a clear flow from summary to implications to recommendations.
        ✅ Cautious and balanced: Acknowledge limitations and avoid overstating results.
        ✅ Actionable and specific: Provide tailored recommendations that are practical and relevant to stakeholders.
    """).strip()

    return generate_section(results, query, model, section_title, section_prompt, chunk_size)



# Load BERT model for similarity-based filtering
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

# Define length constraints for different sections
section_length_limits = {
    "Background": 1200,  # 800-1200 words
    "Methods": 1500,  # 1000-1500 words
    "Results": 2500,  # 1500-2500 words
    "Discussion": 3000,  # 2000-3000 words
    "Conclusion": 600,  # 300-600 words
}

def generate_section(results, query, model, section_title, section_prompt, 
                     previous_sections=None, chunk_size=30, similarity_threshold=0.8):
    """
    Generates a **Systematic Review** section with:
    - **Context awareness** (previously generated sections as input)
    - **De-duplication** (removes redundant content using BERT-based similarity checking)
    - **Smooth transitions** (AI is explicitly instructed to generate transition sentences)
    - **Flexible length control** (section-specific length limits)
    
    Parameters:
    - results: Research data in chunks
    - query: Current research topic
    - model: AI model for text generation
    - section_title: The title of the section being generated
    - section_prompt: Writing instructions for the section
    - previous_sections: Previously generated sections (to enhance continuity)
    - chunk_size: Number of data chunks to use for context
    - similarity_threshold: Sentence similarity threshold for de-duplication
    """

    seen_sentences = set()  # Store unique sentences

    # 🔥 Ensure `previous_sections` is always a list
    if not isinstance(previous_sections, list):  
        previous_sections = []  # 强制转换为空列表，确保不会出错

    # Retrieve the max length for this section
    max_length = section_length_limits.get(section_title, 1500)  # Default to 1500 words if unspecified

    # 1️⃣ **Context Expansion** (Use both research data and previously generated sections)
    context_data = "\n\n".join(results[:chunk_size]) if results else ""

    # 🔥 防止 `join()` 报错，确保 previous_sections 是 list 并且不包含非字符串元素
    previous_content = "\n\n".join(str(s) for s in previous_sections) if previous_sections else ""

    if previous_content:
        context_data = previous_content + "\n\n" + context_data  # Append previous sections for better flow

    # 2️⃣ **Construct the Prompt**
    prompt = textwrap.dedent(f"""
    **Revised Systematic Review Writing Prompt**

    # 📚 **Systematic Review Writing Task: {section_title}**

    You are an expert researcher conducting a **Systematic Review** following **PRISMA guidelines**. 
    Your task is to generate the **{section_title}** section in a **structured, evidence-based, and academic** manner.

    ## 🔍 **Key Writing Guidelines**

    - Follow **PRISMA guidelines** for transparency & reproducibility.
    - Use **formal academic language** and ensure logical coherence with previous sections.
    - **Maintain logical flow** with clear transition sentences.
    - **Avoid redundancy**—summarize rather than repeat ideas.

    ## 📌 **Context (Original Query, Previously Generated Sections & Research Data)**

    Below is the **original query** that sets the topic of the systematic review, followed by previously generated content and relevant research data:

    ```
    {query}
    ```

    ```
    {context_data}
    ```

    ## 🛠 **Instructions for Writing This Section**
    {section_prompt}

    - Use this data as a reference to ensure consistency.
    - If methodology or prior findings are referenced, align your section accordingly.

    ## 🛠 **Instructions for Writing This Section**

    ## 🎯 **Output Constraints**

    - **Format:** Use clear headings & subheadings where necessary.
    - **Word Limit:** Aim for **{max_length} words**, prioritizing essential details.
    - **Clarity & Coherence:** Ensure smooth readability and logical consistency.

    ## 📝 **Now, generate the full {section_title} section:**


    """)

    try:
        # 3️⃣ **AI Generates the Text**
        response = model.invoke(prompt).content if model else None

        # 🔥 **Check if response is None**
        if response is None or not isinstance(response, str):
            raise ValueError(f"AI model did not return a valid response for {section_title}")

        response = response.strip()

        # 🔥 **Check if response is empty**
        if not response:
            raise ValueError(f"Generated response is empty for {section_title}")

        # Limit the text length based on the predefined constraints
        response = response[:max_length * 6]  # Approximate conversion: 1 word ≈ 6 characters
        
        # 4️⃣ **Deduplication Logic**
        generated_sentences = response.split("\n")
        unique_sentences = []

        for sentence in generated_sentences:
            if sentence.strip() and sentence not in seen_sentences:
                unique_sentences.append(sentence)
                seen_sentences.add(sentence)

        # 5️⃣ **BERT-based Semantic Deduplication**
        filtered_sentences = []
        for sentence in unique_sentences:
            if not filtered_sentences:  # First sentence is always added
                filtered_sentences.append(sentence)
                continue
            
            # Compute similarity between new sentence and existing filtered ones
            embeddings1 = bert_model.encode([sentence], convert_to_tensor=True)
            embeddings2 = bert_model.encode(filtered_sentences, convert_to_tensor=True)
            similarity_scores = util.pytorch_cos_sim(embeddings1, embeddings2).mean().item()

            # Only add sentence if it is not too similar to previous ones
            if similarity_scores < similarity_threshold:
                filtered_sentences.append(sentence)

        final_section = "\n".join(filtered_sentences)  # Return the final cleaned section
        
        # ✅ **Append the generated section to previous_sections for future use**
        previous_sections.append(final_section)

        return final_section

    except ValueError as ve:
        print(f"⚠️ ValueError in {section_title}: {ve}")
        return ""
    except Exception as e:
        print(f"⚠️ Unexpected error in {section_title}: {e}")
        return ""




def generate_full_systematic_review(query, model):
    """逐步生成 Systematic Review 的不同章节，每个章节独立处理"""

    paper_ids = get_all_paper_ids()  # ✅ 获取所有存储的论文 ID
    systematic_review = {}

    print("🔍 生成 Background 章节...")
    background_results = search_pinecone_with_fallback(query, paper_ids=paper_ids, section="Background", top_k=50)
    systematic_review["Background"] = generate_background_section(background_results, query, model)

    print("🔍 生成 Methods 章节...")
    methods_results = search_pinecone_with_fallback(query, paper_ids=paper_ids, section="Methods", top_k=50)
    systematic_review["Methods"] = generate_methods_section(methods_results, query, model)

    print("🔍 生成 Results 章节...")
    results_results = search_pinecone_with_fallback(query, paper_ids=paper_ids, section="Results", top_k=50)
    systematic_review["Results"] = generate_results_section(results_results, query, model)

    print("🔍 生成 Discussion 章节...")
    discussion_results = search_pinecone_with_fallback(query, paper_ids=paper_ids, section="Discussion", top_k=50)
    systematic_review["Discussion"] = generate_discussion_section(discussion_results, query, model)

    print("🔍 生成 Conclusion 章节...")
    conclusion_results = search_pinecone_with_fallback(query, paper_ids=paper_ids, section="Conclusion", top_k=50)
    systematic_review["Conclusion"] = generate_conclusion_section(conclusion_results, query, model)

    return systematic_review


def process_and_store_pdfs():
    """Processes user-uploaded PDFs and stores embeddings in Pinecone."""
    
    user_files = [f for f in os.listdir(USER_PAPERS_DIR) if f.endswith(".pdf")]

    if not user_files:
        print("⚠️ No user-uploaded PDFs found in 'backend/user_uploads/'. Please upload files first.")
        return

    for pdf_file in tqdm(user_files, desc="Processing User Papers"):
        pdf_path = os.path.join(USER_PAPERS_DIR, pdf_file)
        paper_id = pdf_file.replace(".pdf", "")  # Use filename as namespace

        print(f"📄 Extracting text from {pdf_file}...")
        text = pdf_to_text(pdf_path)
        classified_chunks = split_text_into_chunks(text)  # Now returns classified sections

        print(f"📦 Storing {len(classified_chunks)} chunks in Pinecone under '{paper_id}'...")
        store_chunks_in_pinecone(classified_chunks, paper_id=paper_id)

def main():
    """Pipeline for processing user PDFs and generating a systematic review."""

    # ✅ Step 1: Initialize Pinecone
    initialize_pinecone()

    # ✅ Step 2: Preload default research papers if missing
    # preload_research_papers()

    # ✅ Step 3: Process and store user PDFs
    process_and_store_pdfs()

    # ✅ Step 4: Generate systematic review
    query = "What are the key findings on COVID-19 vaccines?"
    print("📖 Generating final systematic review...")

    final_review = generate_full_systematic_review(query, model)

    # ✅ Step 5: Save results
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"review": final_review}, f, indent=4, ensure_ascii=False)

    print(f"✅ Systematic review saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()

###

import os
import pinecone
import dotenv

# Load API keys
dotenv.load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = "us-east-1"
INDEX_NAME = "fuck"
VECTOR_DIMENSION = 1536  # OpenAI Embeddings dimension

# New way to initialize Pinecone (v3+)
from pinecone import Pinecone, ServerlessSpec

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

def initialize_pinecone():
    """ Initializes Pinecone and creates an index if it doesn't exist. """
    
    # Check if index exists, if not create it
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating Pinecone index: {INDEX_NAME}...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=VECTOR_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'  
            )
        )
        print(f"Index '{INDEX_NAME}' created successfully!")
    else:
        print(f"Index '{INDEX_NAME}' already exists.")

if __name__ == "__main__":
    initialize_pinecone()

###

import fitz  # PyMuPDF for PDF processing
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
import os
import dotenv

# ✅ Load environment variables
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Initialize OpenAI LLM
model = ChatOpenAI(api_key=OPENAI_API_KEY)

def pdf_to_text(pdf_path):
    """Extracts text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])

    # Clean text: remove unnecessary whitespace & empty lines
    text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])
    return text

def clean_text(text):
    """Cleans text by removing extra spaces, line breaks, and merging broken words."""
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[§†‡]', '', text)
    text = re.sub(r'\b(\w+)-\s+(\w+)\b', r'\1\2', text)  # Merge broken words
    return text.strip()

def classify_chunk_with_llm(chunk):
    """Classifies a text chunk into Background, Methods, Results, Discussion, or Conclusion using LLM."""
    prompt = f"""
    You are an AI assistant classifying research paper sections.
    Determine which section this text belongs to: Background, Methods, Results, Discussion, Conclusion.

    ---TEXT---
    {chunk}
    ------------------
    
    Output only the section name:
    """
    response = model.invoke(prompt).content.strip()
    valid_sections = {"Background", "Methods", "Results", "Discussion", "Conclusion"}
    return response if response in valid_sections else "Background"

def split_text_into_chunks(text, chunk_size=1500, overlap=300):
    """Splits text into smaller chunks while keeping sentence integrity and classifies sections."""
    text = clean_text(text)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap, 
                                                   separators=["\n\n", "\n", ".", "?", "!"])
    chunks = text_splitter.split_text(text)

    # Classify chunks into sections
    classified_chunks = [{"text": chunk, "section": classify_chunk_with_llm(chunk)} for chunk in chunks]
    
    return classified_chunks

if __name__ == "__main__":
    sample_pdf = "preloaded_papers/covid_vaccine_1.pdf"
    text = pdf_to_text(sample_pdf)
    classified_chunks = split_text_into_chunks(text)

    # Print first 5 classified chunks for testing
    for chunk in classified_chunks[:5]:
        print(f"📄 Section: {chunk['section']}\n🔹 {chunk['text'][:500]}...\n")

###

import os
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings

# ✅ Load API Keys
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Connect to Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("my-index")  # Update with your Pinecone index name

# ✅ Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def search_pinecone(query, paper_id=None, section="Results", top_k=10):
    """Search for relevant text chunks in Pinecone based on Paper_ID and Section."""

    # Construct namespace based on whether a specific paper is requested
    if paper_id:
        namespace = f"SYSTEMATIC_REVIEW/{paper_id}/{section}"
    else:
        namespace = f"SYSTEMATIC_REVIEW/*/{section}"  # Search all papers' Results by default

    print(f"🔍 Searching Pinecone in namespace: '{namespace}' for query: '{query}'...")

    # Convert query to vector
    query_vector = embeddings.embed_query(query)

    # Query Pinecone index
    results = index.query(vector=query_vector, top_k=top_k, namespace=namespace, include_metadata=True)

    # Extract relevant text
    return [match["metadata"]["text"] for match in results["matches"]]


def get_all_paper_ids():
    """从 Pinecone 获取所有存储的论文 ID"""
    index_stats = index.describe_index_stats()
    paper_ids = set()

    for namespace in index_stats["namespaces"]:
        if namespace.startswith("SYSTEMATIC_REVIEW/"):
            parts = namespace.split("/")
            if len(parts) > 1:
                paper_ids.add(parts[1])

    return list(paper_ids)

def search_pinecone_with_fallback(query, paper_ids=None, section="Results", top_k=10):
    """在 Pinecone 里根据 Paper_ID 和 Section 搜索相关文本片段"""

    query_vector = embeddings.embed_query(query)
    print(f"🔍 查询向量 (前10维): {query_vector[:10]}")  # 仅打印前 10 维以供调试

    all_results = []

    if paper_ids is None:
        paper_ids = get_all_paper_ids()  # ✅ 自动获取所有 `Paper_ID`

    if not paper_ids:
        print("⚠️ 没有找到任何已存储的论文，无法进行查询。")
        return []

    print(f"📄 发现 {len(paper_ids)} 篇存储的论文: {paper_ids}")

    # ✅ 遍历所有 `Paper_ID`，分别查询
    for paper_id in paper_ids:
        namespace = f"SYSTEMATIC_REVIEW/{paper_id}/{section}"
        print(f"🔍 正在 Pinecone 查询 namespace: '{namespace}'，搜索问题: '{query}'...")

        results = index.query(vector=query_vector, top_k=top_k, namespace=namespace, include_metadata=True)

        if results["matches"]:
            print(f"✅ 在 {namespace} 中检索到 {len(results['matches'])} 条结果")
            for match in results["matches"]:
                print(f"📄 片段内容: {match['metadata']['text'][:100]}...")
            all_results.extend([match["metadata"]["text"] for match in results["matches"]])
        else:
            print(f"⚠️ 在 {namespace} 没有找到相关结果")

    if not all_results:
        print("⚠️ 仍然没有找到相关结果，请检查 Pinecone 数据存储是否正确")

    return all_results

##

import os
import dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from process_pdf import pdf_to_text, split_text_into_chunks

# ✅ Load environment variables
dotenv.load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "fuck"

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
