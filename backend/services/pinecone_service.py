from concurrent.futures import ThreadPoolExecutor, as_completed
from pinecone import ServerlessSpec
from config import (
  pinecone, 
  embeddings,
  PINECONE_INDEX_NAME, 
  VECTOR_DIMENSION, 
  SEARCH_METRIC, 
  SPEC_CLOUD, 
  SPEC_REGION
) 

def initialise_pinecone():
    ''' Initializes Pinecone and creates an index if it doesn't exist. '''
    
    # Check if index exists, if not create it
    if PINECONE_INDEX_NAME not in pinecone.list_indexes().names():
        print(f'Creating Pinecone index: {PINECONE_INDEX_NAME}...')
        pinecone.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=VECTOR_DIMENSION,
            metric=SEARCH_METRIC,
            spec=ServerlessSpec(
                cloud=SPEC_CLOUD,
                region=SPEC_REGION  
            )
        )
        print(f'Index "{PINECONE_INDEX_NAME}" created successfully!')
    else:
        print(f'Index "{PINECONE_INDEX_NAME}" already exists.')

def get_all_paper_ids():
    '''Get all stored paper IDs from Pinecone'''
    index = pinecone.Index(PINECONE_INDEX_NAME)
    index_stats = index.describe_index_stats()
    paper_ids = set()

    for namespace in index_stats['namespaces']:
        if namespace.startswith('systematic_review/'):
            parts = namespace.split('/')
            if len(parts) > 1:
                paper_ids.add(parts[1])

    return list(paper_ids)

def query_with_namespace(paper_id, section, query_vector, top_k, index):
    index = pinecone.Index(PINECONE_INDEX_NAME)
    namespace = f'systematic_review/{paper_id}/{section}'
    print(f'🔍 Querying Pinecone in namespace: "{namespace}"')

    results = index.query(vector=query_vector, top_k=top_k, namespace=namespace, include_metadata=True)

    if results['matches']:
        print(f'✅ Found {len(results["matches"])} results in {namespace}')
        # for match in results['matches']:
        #     print(f'📄 Fragment content: {match['metadata']['text'][:100]}...')
        # all_results.extend([match['metadata']['text'] for match in results['matches']])
        return results
    else:
        print(f'⚠️ No relevant results found in {namespace}')

def search_pinecone(query, paper_ids=None, section='Results', top_k=10):
    '''Search for relevant text fragments in Pinecone based on Paper_ID and Section'''
    index = pinecone.Index(PINECONE_INDEX_NAME)

    query_vector = embeddings.embed_query(query)
    print(f'🔍 Query vector (first 10 dimensions): {query_vector[:10]}')  # Print only the first 10 dimensions for debugging

    result = []

    if paper_ids is None:
        paper_ids = get_all_paper_ids()  # ✅ Automatically get all `Paper_ID`s

    if not paper_ids:
        print('⚠️ No stored papers found, unable to query.')
        return []

    print(f'📄 Found {len(paper_ids)} stored papers: {paper_ids}')

    with ThreadPoolExecutor() as executor:
        future_to_queries = {
            executor.submit(query_with_namespace, paper_id, section, query_vector, top_k, index): 
            paper_id for paper_id in paper_ids
        }

        for future in as_completed(future_to_queries):
            try:
                response = future.result()
                result.extend([match['metadata']['text'] for match in response['matches']])
            except Exception as e:
                print(f'Error querying namespace {future_to_queries[future]}: {e}')

    if not result:
        print('⚠️ Still no relevant results found, please check if Pinecone data storage is correct')

    return result