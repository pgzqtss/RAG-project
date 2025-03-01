from time import sleep
from config import pinecone, PINECONE_INDEX_NAME

def check_all_upserted_chunks(files, chunks_count, max_retries=10, delay=2):
    index = pinecone.Index(PINECONE_INDEX_NAME)
    
    retries = 0
    while retries < max_retries:
        print(f'Retries: {retries}')
        total_vector_count = 0
        index_stats = index.describe_index_stats()
        namespaces = index_stats.get('namespaces', {})
        for namespace, stats in namespaces.items():
            for paper_id in files:
                if namespace.startswith(f'systematic_review/{paper_id}'):
                    total_vector_count += stats.get('vector_count', 0)
        print(f'Vector Count: {total_vector_count}')

        if total_vector_count == chunks_count:
            print(f'✅ All vectors are fully indexed!')
            return
        
        retries += 1
        sleep(delay)
    print(f'⚠️ Vectors may not be fully indexed yet. Proceeding with querying.')