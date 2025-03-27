import os
import re
import platform
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pdfplumber
from wordcloud import WordCloud
from langchain.schema import HumanMessage
import chardet
from collections import Counter
from tenacity import retry, stop_after_attempt, wait_random
from config import model

# Detect OS and set font path
if platform.system() == 'Windows':
    font_path = 'C:/Windows/Fonts/Arial.ttf'
elif platform.system() == 'Darwin': 
    font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
else:
    font_path = None 

MEDICAL_STOPWORDS = {
    'cid', 'www', 'http', 'https', 'figure', 'table', 'equation',
    'section', 'pp', 'vol', 'no', 'et al', 'eg', 'ie', 'vs', 'fig',
    'doi', 'copyright', 'author', 'year', 'study', 'result', 'method',
    'conclusion', 'introduction', 'background', 'objective', 'purpose'
}

def load_documents(folder_path):
    documents = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        try:
            if file_name.lower().endswith('.pdf'):
                with pdfplumber.open(file_path) as pdf:
                    text_pages = []
                    for page in pdf.pages:
                        raw_text = page.extract_text()
                        if raw_text:
                            cleaned = '\n'.join(
                                line for line in raw_text.split('\n')
                                if not line.strip().isdigit()
                                and not line.startswith('Received:')
                            )
                            text_pages.append(cleaned)
                    documents.append('\n'.join(text_pages))
            elif file_name.lower().endswith(('.txt', '.md')):
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
                documents.append(raw_data.decode(encoding, errors='ignore'))
        except Exception as e:
            print(f'Failed to process {file_name}: {e}')
    return documents

@retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
def extract_thematic_area(text):
    start_pos = max(0, len(text)//4)
    sample_text = text[start_pos:start_pos+6000]
    patterns = [
        r'\d{4} Elsevier Ltd\. All rights reserved\.',
        r'http(s)?://\S+',
        r'\(cid:\d+\)'
    ]
    for pattern in patterns:
        sample_text = re.sub(pattern, '', sample_text)
    prompt = f'Extract 5-10 thematic areas from the following medical text (comma-separated):\n\n{sample_text}'
    try:
        response = model.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        print(f'Thematic area extraction failed: {e}')
        return ''

def generate_wordcloud(areas, id, output_file='thematic_wordcloud.png'):
    output_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', 'frontend', 'public', 'output', str(id), str(output_file)
    ))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    filtered = []
    for a in areas:
        cleaned = a.strip().lower()
        cleaned = re.sub(r'\s+', ' ', cleaned.replace('\n', ' ').replace('\r', ' '))
        if (cleaned and len(cleaned) > 1 
            and cleaned not in MEDICAL_STOPWORDS 
            and not cleaned.isdigit()):
            filtered.append(cleaned)
    freq = Counter(filtered)
    wc = WordCloud(
        width=1200,
        height=800,
        font_path=font_path if font_path else None,
        background_color='white',
        colormap='viridis',
        max_words=200
    ).generate_from_frequencies(freq)
    plt.figure(figsize=(12, 8))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    folder_path = 'RAG-project/backend/papers/papers'
    docs = load_documents(folder_path)
    doc_areas = [extract_thematic_area(doc) for doc in docs]

    df = pd.DataFrame({'Content': docs, 'ThematicArea': doc_areas})
    df.to_csv('thematic_analysis.csv', index=False, encoding='utf-8-sig')

    all_areas = []
    for area_str in doc_areas:
        cleaned_str = area_str.replace('\n', ' ').replace('\r', ' ')
        # Split and clean each area
        splitted = [a.strip() for a in cleaned_str.split(',') if a.strip()]
        all_areas.extend(splitted)

    # Generate frequency and top 10
    freq = Counter([re.sub(r'\s+', ' ', x.lower().strip()) for x in all_areas if x])
    top10 = freq.most_common(10)
    
    df_top10 = pd.DataFrame({'ThematicArea': [x[0] for x in top10], 'Count': [x[1] for x in top10]})

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=df_top10,
        x='Count',
        y='ThematicArea',
        hue='ThematicArea',
        palette='viridis',
        dodge=False,
        legend=False
    )
    plt.title('Top 10 Thematic Areas')
    plt.xlabel('Count')
    plt.ylabel('Thematic Area')
    plt.tight_layout()
    plt.show()

    generate_wordcloud(all_areas, 'thematic_wordcloud.png')
    print('Processing complete. Results saved as:')
    print('- Thematic analysis CSV: thematic_analysis.csv')
    print('- Word Cloud: thematic_wordcloud.png')