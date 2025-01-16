# Rag-n-Bones
Rag-n-Bones is a web application that uses an input of PDFs to generate systematic reviews utilising Pinecone indexing and OpenAI's GPT models.

## Deployment Instructions
1. Clone the repository:
```
~ git clone https://github.com/pgzqtss/RAG-project.git
```

2. Install all necessary python libraries:
```
~ pip install -r requirements.txt
```

3. Create a `.env` file in the root directory using `.env.environment` as a template.

    | Environment Variable | Description | Source
    | ----------- | ----------- | ---------- |
    | PINECONE_API_KEY | API key for using Pinecone as a vector database | <a href='https://www.pinecone.io'> Pinecone <a/> |
    | OPENAI_API_KEY | API key for use of OpenAI's GPT 3.5 Turbo model | <a href='https://platform.openai.com/docs/overview'> OpenAI API Platform <a/>

4. Run `upload_pdfs.py` to upload test PDFs to the Pinecone database: (Creates vectors for LLM use)
```
~ python3 backend/upload_pdfs.py
```

5. Run `pipeline.py`: (Generates systematic review based on example prompt)
```
~ python3 backend/pipeline.py
```
