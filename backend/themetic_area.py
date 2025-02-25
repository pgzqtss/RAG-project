import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import chardet
from collections import Counter
from tenacity import retry, stop_after_attempt, wait_random

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0)

def load_documents(folder_path):
    documents = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
            encoding_info = chardet.detect(raw_data)
            encoding = encoding_info['encoding'] or 'utf-8'
            try:
                text = raw_data.decode(encoding, errors='ignore')
            except UnicodeDecodeError:
                text = raw_data.decode('utf-8', errors='ignore')
            documents.append(text)
        except Exception as e:
            print(f"Failed to read file {file_name}: {e}")
    return documents

@retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
def extract_keywords(text):
    clean_text = text[:3000].replace('\n', ' ').strip()
    prompt = f"Extract 5-10 key terms from the following content (comma-separated):\n\n{clean_text}"
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"Keyword extraction failed: {e}")
        return ""

@retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
def summarize_topic(keywords):
    if not keywords:
        return "Uncategorized"
    prompt = f"Summarize the following keywords into a short research topic (2-4 words): {keywords}"
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip().replace('"', '')
    except Exception as e:
        print(f"Topic summarization failed: {e}")
        return "Uncategorized"

if __name__ == "__main__":
    documents = load_documents("RAG-project/papers")
    document_keywords = [extract_keywords(doc) for doc in documents]
    document_topics = [summarize_topic(kw) for kw in document_keywords]

    df = pd.DataFrame({
        'Content': documents,
        'Keywords': document_keywords,
        'Topic': document_topics
    }).query("Topic != 'Uncategorized'")

    plt.figure(figsize=(12,6))
    topic_counts = df['Topic'].value_counts()
    sns.barplot(x=topic_counts.values, y=topic_counts.index, hue=topic_counts.index, palette="viridis", legend=False)
    plt.title("Document Topic Distribution")
    plt.xlabel("Count")
    plt.ylabel("Topic")
    plt.tight_layout()
    plt.show()

    font_path = "C:/Windows/Fonts/Arial.ttf"  
    keywords_list = [kw.strip() for kw in ",".join(df['Keywords']).split(',') if kw.strip()]
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        font_path=font_path,
        background_color="white"
    ).generate_from_frequencies(Counter(keywords_list))

    plt.figure(figsize=(10,5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Keyword Distribution")
    plt.show()
