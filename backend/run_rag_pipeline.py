import os
import json
from tqdm import tqdm
from initialize_pinecone import initialize_pinecone
from preload_vector_db import preload_research_papers
from process_pdf import pdf_to_text, split_text_into_chunks
from store_to_pinecone import store_chunks_in_pinecone
from search_with_fallback import search_pinecone_with_fallback
from search_with_fallback import get_all_paper_ids
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
INDEX_NAME = "my-index"
USER_PAPERS_DIR = "backend/user_uploads"
OUTPUT_DIR = "backend/processed_texts"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "systematic_review.json")

# ✅ Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Initialize LLM model
model = ChatOpenAI(api_key=OPENAI_API_KEY)

def generate_background_section(results, query, model, chunk_size=5):
    """单独生成 Background 章节"""
    section_title = "Background"
    section_prompt = textwrap.dedent(f"""
        ## {section_title} (800-1200 words)

        Generate the {section_title} section for a Systematic Review with the following structure and guidelines:

        ### 🔹 Required Content:
        1. **Introduction to the Topic:**
           - Clearly introduce the research topic and its significance.
           - Explain fundamental concepts relevant to the topic (e.g., cytokine storm, immunopathology in COVID-19).
           - Describe how the topic relates to clinical practice, public health, or policy-making.

        2. **Summary of Existing Literature:**
           - Provide a comprehensive overview of previous studies, including key findings and limitations.
           - Cite relevant systematic reviews, meta-analyses, and primary research.
           - Explain inconsistencies, knowledge gaps, and unresolved issues in the existing literature.

        3. **Justification for This Systematic Review:**
           - Clearly state why this review is necessary.
           - Explain how it fills the existing research gap.
           - Define the specific research question using the PICO framework (Population, Intervention, Comparison, Outcome) if applicable.

        ### 🔹 Writing Style:
        ✅ Formal and academic tone  
        ✅ Use citations from peer-reviewed sources  
        ✅ Avoid subjective statements—stick to evidence  
        ✅ Logical flow from broad background to the specific research question  
    """).strip()
    return generate_section(results, query, model, section_title, section_prompt, chunk_size)


def generate_methods_section(results, query, model, chunk_size=5):
    """Generate the Methods section for a Systematic Review following PRISMA guidelines."""
    
    section_title = "Methods"
    section_prompt = textwrap.dedent(f"""
        ## {section_title} (1000-1500 words)

        Generate the {section_title} section for a Systematic Review following PRISMA guidelines, ensuring transparency and reproducibility.

        ### 🔹 Required Content:
        1. **Study Design:**
           - Specify whether this is a Systematic Review or Meta-Analysis.
           - State that PRISMA guidelines were followed.

        2. **Literature Search Strategy:**
           - List the databases searched (e.g., PubMed, EMBASE, Cochrane, Web of Science).
           - Provide exact search terms, MeSH terms, and Boolean operators used.
           - Mention the date range of included studies and the last search date.

        3. **Inclusion and Exclusion Criteria:**
           - Define study eligibility criteria (e.g., language, study design, sample size).
           - Specify types of interventions, outcomes, and comparison groups included/excluded.
           - Clearly explain reasons for study exclusion.

        4. **Study Selection Process:**
           - Describe the screening process (title, abstract, full-text).
           - Mention if two independent reviewers conducted screening.
           - State how discrepancies were resolved (third reviewer, consensus).

        5. **Data Extraction & Variables Collected:**
           - List extracted data fields: author, year, study design, population, intervention, outcome measures.
           - Mention software/tools used for data extraction (e.g., Covidence, Excel).

        6. **Quality Assessment & Risk of Bias Evaluation:**
           - State the tool used (Cochrane RoB 2.0, ROBINS-I, GRADE) to assess study quality.
           - Explain how bias was evaluated (e.g., blinding, selection bias).

        7. **Statistical Analysis (for Meta-Analysis):**
           - Describe the statistical methods used:
             - Effect measures (OR, RR, SMD with 95% CI).
             - Heterogeneity analysis (I² statistic, subgroup analysis).
             - Publication bias assessment (funnel plots, Egger’s test).

        ### 🔹 Writing Style:
        ✅ Transparent, detailed, and structured  
        ✅ Passive voice is recommended for objectivity  
        ✅ Ensure reproducibility by providing search terms, databases, and statistical methods  
    """).strip()

    return generate_section(results, query, model, section_title, section_prompt, chunk_size)


def generate_results_section(results, query, model, chunk_size=5):
    """Generate the Results section for a Systematic Review."""

    section_title = "Results"
    section_prompt = textwrap.dedent(f"""
        ## {section_title} (1500-2500 words)

        Generate the {section_title} section for a Systematic Review, structuring it as follows:

        ### 🔹 Required Content:
        1. **Study Selection Process:**
           - Present PRISMA flow diagram details (number of records screened, included, and excluded).
           - Mention reasons for study exclusion after full-text review.

        2. **Study Characteristics:**
           - Summarize included studies in a table (author, year, sample size, intervention, outcome).
           - Specify study designs (RCTs, cohort studies, case-control).

        3. **Main Findings (Quantitative & Qualitative Analysis):**
           - **If Meta-Analysis:**
             - Provide effect sizes (OR, RR, SMD) with 95% CIs.
             - Include a Forest Plot to show combined effect estimates.
           - **If Narrative Synthesis:**
             - Summarize key patterns across studies.
             - Identify consistent/inconsistent findings.

        4. **Heterogeneity & Sensitivity Analysis:**
           - Report I² statistics and interpret heterogeneity.
           - Explain subgroup and sensitivity analyses.

        ### 🔹 Writing Style:
        ✅ Data-driven—avoid subjective interpretation  
        ✅ Use figures (forest plots, tables) to enhance clarity  
        ✅ Organize findings logically—from overall effects to subgroup differences  
    """).strip()

    return generate_section(results, query, model, section_title, section_prompt, chunk_size)


def generate_discussion_section(results, query, model, chunk_size=5):
    """Generate the Discussion section for a Systematic Review."""

    section_title = "Discussion"
    section_prompt = textwrap.dedent(f"""
        ## {section_title} (2000-3000 words)

        Generate the {section_title} section for a Systematic Review, structured as follows:

        ### 🔹 Required Content:
        1. **Summary of Main Findings:**
           - Restate key results concisely.
           - Compare with previous studies—highlight similarities and discrepancies.

        2. **Interpretation of Findings:**
           - Discuss potential explanations for the findings.
           - Explore biological mechanisms, clinical implications, or public health relevance.

        3. **Strengths and Limitations:**
           - Highlight study strengths (comprehensive search, rigorous bias assessment, large sample size).
           - Discuss limitations (heterogeneity, risk of bias, missing data, publication bias).

        4. **Future Research Directions:**
           - Recommend specific improvements for future studies (e.g., need for RCTs, larger sample sizes).

        ### 🔹 Writing Style:
        ✅ Logical flow from findings to broader implications  
        ✅ Avoid overgeneralization—stay evidence-based  
        ✅ Use hedging language (e.g., "suggests," "may indicate")  
    """).strip()

    return generate_section(results, query, model, section_title, section_prompt, chunk_size)


def generate_conclusion_section(results, query, model, chunk_size=5):
    """Generate the Conclusion section for a Systematic Review."""

    section_title = "Conclusion"
    section_prompt = textwrap.dedent(f"""
        ## {section_title} (300-600 words)

        Generate the {section_title} section for a Systematic Review with the following structure:

        ### 🔹 Required Content:
        1. **Concise Summary of Key Findings:**
           - Reiterate the most important takeaways from the study.

        2. **Clinical & Public Health Implications:**
           - Highlight how findings may influence practice or policy.
           - Avoid overstating results—acknowledge limitations.

        3. **Final Recommendations:**
           - Suggest next steps for research based on gaps identified.

        ### 🔹 Writing Style:
        ✅ Concise and direct  
        ✅ Avoid new information—only summarize previous sections  
        ✅ Provide actionable insights where possible  
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
    # 📚 **Systematic Review Writing Task: {section_title}**
    You are an expert researcher conducting a **Systematic Review** following **PRISMA guidelines**.
    Your goal is to write the **{section_title}** section in a **structured, evidence-based, and academic** manner.
    
    ## 🔍 **Key Writing Guidelines**
    - Follow **PRISMA guidelines** for transparency & reproducibility.
    - Use **formal academic language** and peer-reviewed citations (e.g., "[Smith et al., 2022]").
    - Ensure **logical consistency** by referencing previously written sections.
    - Avoid **redundancy** (summarize rather than repeating ideas).
    - Use **transition sentences** for smooth readability.

    ## 📌 **Context (Previously Generated Sections & Research Data)**
    Below is the **previously generated content** along with research data:
    ```
    {context_data}
    ```

    ## 🛠 **Instructions for Writing This Section**
    {section_prompt}

    ## 🎯 **Output Constraints**
    - Ensure a structured format (use headings & subheadings where appropriate).
    - Follow an academic style and cite relevant literature.
    - **Avoid redundant content** (summarize when needed).
    - **Use transition sentences** to maintain readability.
    - **Word Limit:** Generate **{max_length} words** for this section.
    
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
    preload_research_papers()

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
