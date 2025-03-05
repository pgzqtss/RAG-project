from re import sub
import fitz  # PyMuPDF

def pdf_to_text(pdf_path):
    '''Extracts text from a PDF file.'''
    doc = fitz.open(pdf_path)
    text = '\n'.join([page.get_text('text') for page in doc])

    # Clean text: remove unnecessary whitespace & empty lines
    text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
    return text

def clean_text(text):
    '''Cleans text by removing extra spaces, line breaks, and merging broken words.'''
    text = text.replace('\n', ' ')
    text = sub(r'\s+', ' ', text)
    text = sub(r'[§†‡]', '', text)
    text = sub(r'\b(\w+)-\s+(\w+)\b', r'\1\2', text)  # Merge broken words
    return text.strip()