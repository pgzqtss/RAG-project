import os
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
#  Pinecone API Key
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# connect Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("my-index")  # 你的 Pinecone 索引名称





# ✅ 初始化 OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)





def search_pinecone(query, namespace="default", top_k=10):
    """ 在 Pinecone 中搜索与查询最相关的文本片段 """

    # ✅ 先将文本查询转换为向量
    query_vector = embeddings.embed_query(query)  # 🔥 **修正点：转换文本为嵌入向量**

    # ✅ 使用向量在 Pinecone 中进行查询
    results = index.query(vector=query_vector, top_k=top_k, namespace=namespace, include_metadata=True)

    # ✅ 提取匹配的文本片段
    return [match["metadata"]["text"] for match in results["matches"]]

def search_pinecone_with_fallback(query, user_namespace="user-uploaded", top_k=5):
    """Search user-uploaded data first, then fall back to preloaded research if needed."""

    print(f"🔍 Searching Pinecone for query: {query}")

    # ✅ 先从用户上传的数据中搜索
    user_chunks = search_pinecone(query, namespace=user_namespace, top_k=top_k)

    print(f"📌 Retrieved {len(user_chunks)} chunks from user namespace '{user_namespace}'")
    for i, chunk in enumerate(user_chunks[:3]):  # 仅打印前 3 个片段
        print(f"📄 User Chunk {i+1}: {chunk[:200]}...")  # 只显示前 200 个字符

    # ✅ 如果用户数据不足，则补充预加载数据
    if len(user_chunks) < top_k:
        print("⚠️ Not enough user data. Retrieving from preloaded research...")
        fallback_chunks = search_pinecone(query, namespace="preloaded-research", top_k=top_k - len(user_chunks))
        user_chunks.extend(fallback_chunks)

        print(f"📌 Retrieved {len(fallback_chunks)} chunks from preloaded research")
        for i, chunk in enumerate(fallback_chunks[:3]):  # 仅打印前 3 个片段
            print(f"📄 Preloaded Chunk {i+1}: {chunk[:200]}...")

    return user_chunks