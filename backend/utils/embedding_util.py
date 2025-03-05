from config import embeddings

def get_text_embedding(text):
    '''Convert text into vector embeddings using OpenAI embeddings.'''
    if not isinstance(text, str):
        raise TypeError('❌ get_text_embedding() received a non-string input.')
    return embeddings.embed_query(text)