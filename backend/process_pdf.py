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
