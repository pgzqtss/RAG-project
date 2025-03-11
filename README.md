<img src='frontend/public/rag-icon.png' alt='Rag-n-Bones Icon' width='400'/>

# Rag-n-Bones
Rag-n-Bones is a web application that uses an input of PDFs to generate systematic reviews utilising Pinecone indexing and OpenAI's GPT models.

## Features

- User Authentication
- Prompt Input
- PDF Upload
- Systematic Review Generation
- File Input Access
- Export as PDF
- Quality Check Graphs
- Systematic Review History

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
| OPENAI_API_KEY | API key for use of OpenAI's GPT 3.5 Turbo model | <a href='https://platform.openai.com/docs/overview'> OpenAI API Platform <a/>
| MYSQL_PASSWORD | Personal password for MySQL database (empty if none) | |

### 4. Modify `config.py` as needed
The `config.py` file in `/backend` manages key settings for the application, including:
- Pinecone initialisation for vector storage and retrieval.
- MySQL configuration for database connectivity.
- Embedding and OpenAI model settings for text processing and generation.

### 5. Start MySQL server

#### Mac
```
~ brew services start mysql
```

#### Windows
```
~ net start mysql
```

### 6. Create the MySQL database
```
~ cd backend
~ mysql -u root -p < schema.sql
```

### 7. Run the backend
```
~ cd backend
~ python3 app.py
```

### 8. Run the frontend
```
~ cd frontend
~ npm run dev
```

The Next.js app will run on <a href='http:/localhost:3000'>http://localhost:3000</a>

## Testing Instructions

### Backend

### 1. Navigate to the backend directory:
```
~ cd backend
```

### 2. Install the dependencies if not already installed:
```
~ pip install -r requirements.txt
```

### 3. Run the tests using `pytest`:
```
~ pytest
```

This will execute all the tests in the `tests` directory and provide a summary of the results.