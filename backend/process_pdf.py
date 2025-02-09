import fitz  # PyMuPDF for PDF processing
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

def pdf_to_text(pdf_path):
    """ Extracts text from a PDF file. """
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])

    # Clean text: remove unnecessary whitespace & empty lines
    text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])
    return text

def clean_text(text):
    """ Cleans text by removing extra spaces, line breaks, and merging broken words. """
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[§†‡]', '', text)
    text = re.sub(r'\b(\w+)-\s+(\w+)\b', r'\1\2', text)  # Merge broken words
    return text.strip()

def split_text_into_chunks(text, chunk_size=1000, overlap=200):
    """ Splits text into smaller chunks while keeping sentence integrity. """
    text = clean_text(text)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap, 
                                                   separators=["\n\n", "\n", ".", "?", "!"])
    return text_splitter.split_text(text)

if __name__ == "__main__":
    sample_pdf = "preloaded_papers/covid_vaccine_1.pdf"
    text = pdf_to_text(sample_pdf)
    chunks = split_text_into_chunks(text)
    print(chunks[:5])  # Print first 5 chunks for testing