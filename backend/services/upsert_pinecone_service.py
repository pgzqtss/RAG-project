from concurrent.futures import ThreadPoolExecutor

from config import PINECONE_INDEX_NAME, pinecone
from utils.embedding_util import get_text_embedding
from services.classify_chunk_service import classify_chunk_with_llm
from time import sleep

def upsert_all_chunks(text_chunks, paper_id):
    '''Stores document chunks in Pinecone DB under Systematic Review namespaces.'''
    index = pinecone.Index(PINECONE_INDEX_NAME)

    chunks_count = len(text_chunks)

    # if PINECONE_INDEX_NAME not in index.list_indexes().names():
    #     raise ValueError(f'⚠️ Index "{PINECONE_INDEX_NAME}" not found! Run `initialize_pinecone.py` first.')

    # ✅ Get existing namespaces to avoid re-storing sections
    index_stats = index.describe_index_stats()
    existing_namespaces = index_stats.get('namespaces', {})

    # ✅ Instead of skipping the whole paper, only skip already stored sections
    stored_sections = {ns.split('/')[-1] for ns in existing_namespaces if ns.startswith(f'systematic_review/{paper_id}')}

    with ThreadPoolExecutor() as executor:
        for i, chunk in enumerate(text_chunks):
            executor.submit(upsert_chunk, i, chunk, paper_id, stored_sections, index)
    
    check_all_upserted_chunks(index=index, paper_id=paper_id, chunks_count=chunks_count)
    print(f'✅ Successfully stored {len(text_chunks)} chunks in Pinecone under "{paper_id}"!')

def upsert_chunk(i, chunk, paper_id, stored_sections, index):
    if not isinstance(chunk, str):
        print(f'⚠️ Skipping invalid chunk {i} for "{paper_id}".')
        return

    # ✅ Call LLM for classification and ensure it's printed
    section = classify_chunk_with_llm(chunk)
    print(f'🔍 Chunk {i} classified as: {section}')  # ✅ Ensure we see LLM classification

    namespace = f'systematic_review/{paper_id}/{section}'

    # ✅ Skip storing chunks for sections that already exist
    if section in stored_sections:
        print(f'⚠️ Skipping chunk {i} (already stored in {namespace}).')
        return

    vector = get_text_embedding(chunk)

    # ✅ Explicitly store under correct namespace
    index.upsert([
        (
            f'{paper_id}-chunk-{i}',
            vector,
            {
                'text': chunk,
                'source': paper_id,
                'section': section
            }
        )
    ], namespace=namespace)

    print(f'✅ Stored chunk {i} in Pinecone under "{namespace}"!')

def check_all_upserted_chunks(index, paper_id, chunks_count, max_retries=10, delay=2):
    retries = 0
    while retries < max_retries:
        print(f'Retries: {retries}')
        total_vector_count = 0
        index_stats = index.describe_index_stats()
        namespaces = index_stats.get('namespaces', {})
        for namespace, stats in namespaces.items():
            if namespace.startswith(f'systematic_review/{paper_id}'):
                total_vector_count += stats.get('vector_count', 0)
        print(f'Vector Count: {total_vector_count}')

        if total_vector_count == chunks_count:
            print(f'✅ Vectors for paper "{paper_id}" are fully indexed!')
            return
        
        retries += 1
        sleep(delay)
    print(f'⚠️ Vectors for paper "{paper_id}" may not be fully indexed yet. Proceeding with querying.')