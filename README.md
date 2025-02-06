# Rag-n-Bones
Rag-n-Bones is a web application that uses an input of PDFs to generate systematic reviews utilising Pinecone indexing and OpenAI's GPT models.

## Deployment Instructions

### Prerequisites
- Latest version of `pip` is installed
- `MySQL` installed (database)
- `Node.js` and `npm` installed (frontend)

### Instructions
### 1. Clone the repository:
```
~ git clone https://github.com/pgzqtss/RAG-project.git
~ cd RAG-project
```

### 2. Install all dependencies:

#### Backend
```
~ cd backend
~ pip install -r requirements.txt
```

#### Frontend
```
~ cd frontend
~ npm install
```

### 3. Create a `.env` file in the root directory using `.env.environment` as a template.

| Environment Variable | Description | Source
| ----------- | ----------- | ---------- |
| PINECONE_API_KEY | API key for using Pinecone as a vector database | <a href='https://www.pinecone.io'> Pinecone <a/> |
| PINECONE_INDEX_NAME | Name of an index to store and read from all vectors | ^| 
| OPENAI_API_KEY | API key for use of OpenAI's GPT 3.5 Turbo model | <a href='https://platform.openai.com/docs/overview'> OpenAI API Platform <a/>
| MYSQL_PASSWORD | Personal password for MySQL database (empty if none) | |
    

### 4. Start MySQL server

#### Mac
```
~ brew services start mysql
```

#### Windows
```
~ net start mysql
```

### 5. Create the MySQL database
```
~ cd backend
~ mysql -u root -p < schema.sql
```

### 6. Run the backend
```
~ cd backend
~ python3 app.py
```

### 7. Run the frontend
```
~ cd frontend
~ npm run dev
```

The Next.js app will run on <a href='http:/localhost:3000'>http://localhost:3000</a>