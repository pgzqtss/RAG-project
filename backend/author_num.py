import os
import re
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

openai_api_key = os.getenv("OPENAI_API_KEY")

def extract_first_pages(pdf_path, max_pages=2):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i in range(min(max_pages, len(pdf.pages))):
                text += pdf.pages[i].extract_text() + "\n"
    except Exception as e:
        print(f"can't read {pdf_path}: {e}")
    return text

def extract_author_section(text):
    abstract_keywords = ["Abstract", "ABSTRACT"]
    abstract_index = None
    for keyword in abstract_keywords:
        idx = text.find(keyword)
        if idx != -1:
            abstract_index = idx
            break
    if abstract_index is not None:
        text = text[:abstract_index]
    
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) > 1:
        author_text = "\n".join(lines[1:])
        return author_text
    else:
        return text

def parse_authors(raw_authors):

    processed = raw_authors.replace(" and ", ",").replace(";", ",").replace("\n", ",")
    tokens = [t.strip() for t in processed.split(",") if t.strip()]
    authors = []
    for token in tokens:
        token = re.sub(r"^\d+\.\s*", "", token)
        token = re.sub(r"\^?\d+", "", token)
        token = re.sub(r"\(.*?\)", "", token)
        token = token.strip(" ,;")
        token = token.title()
        if token:
            authors.append(token)
    seen = set()
    unique_authors = []
    for a in authors:
        if a.lower() not in seen:
            unique_authors.append(a)
            seen.add(a.lower())
    return unique_authors

def get_authors_from_langchain(text):
    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        messages = [
            SystemMessage(content="You are an AI specializing in academic paper analysis. Extract the author names from the text below, specifically the names located below the title and above the abstract. Return them as a list separated by commas, semicolons, newlines, or the word 'and'."),
            HumanMessage(content=f"Paper content:\n{text}\n\nOnly output the author names without any additional explanation. For example: John Doe, Jane Smith, Alice Johnson")
        ]
        response = llm.invoke(messages)
        response_text = response.content.strip()
        return parse_authors(response_text)
    except Exception as e:
        print(f"LangChain API requests failed: {e}")
        return []

def process_pdfs(pdf_folder):
    author_counter = Counter()
    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, file)
            full_text = extract_first_pages(pdf_path, max_pages=2)
            author_text = extract_author_section(full_text)
            authors = get_authors_from_langchain(author_text)
            author_counter.update(authors)
    return author_counter

def save_and_plot_results(author_counter, output_csv="author_counts.csv"):
    if not author_counter:
        print("get author_counter failed")
        return

    df = pd.DataFrame(author_counter.items(), columns=["Author", "Count"])
    df["Count"] = df["Count"].astype(int)
    df = df.sort_values(by="Count", ascending=False)
    df.to_csv(output_csv, index=False)
    print(f"Saved results to {output_csv}")

    plt.figure(figsize=(10, 6))
    df.head(10).plot(kind="bar", x="Author", y="Count", legend=False)
    plt.title("Top 10 Frequent Authors")
    plt.xlabel("Author Name")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--")
    plt.show()

pdf_folder_path = "RAG-project/papers"
author_counts = process_pdfs(pdf_folder_path)
save_and_plot_results(author_counts)
