from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_text_into_chunks(text, chunk_size=1500, overlap=300):
    '''Splits text into smaller chunks while keeping sentence integrity.'''
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap, 
                                                   separators=['\n\n', '\n', '.', '?', '!'])
    chunks = text_splitter.split_text(text)
    return chunks