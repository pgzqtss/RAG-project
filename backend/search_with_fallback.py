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
