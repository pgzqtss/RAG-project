from flask import Flask, request, jsonify
import mysql.connector
import bcrypt
from flask_cors import CORS

import os
import dotenv
from re import sub
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app)

dotenv.load_dotenv()

def connect_to_database():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='user_data'
    )

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (%s, %s)',
            (username, password_hash)
        )
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'User already exists'}), 409
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('SELECT id, password_hash FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
        return jsonify({'message': 'User logged in successfully'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401
    
def load_pdfs(file_paths):
    all_texts = []
    for file_path in file_paths:
        loader = PyPDFLoader(file_path=file_path)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(data)
        # Clean the text
        for text in texts:
            text.page_content = clean_text(text.page_content)
        all_texts.extend(texts)
        print (f'Loaded {len(texts)} documents from {file_path}')
        # in this case if len(text) which means number of text chunks == number of vectors -> successful
    return all_texts

def upsert_embeddings(texts, embeddings, index_name, namespace):
    # Extract text content from Document objects
    texts_content = [t.page_content for t in texts]
    docsearch = LangchainPinecone.from_texts(texts_content, embeddings, index_name=index_name, namespace=namespace)

def clean_namespace(index, namespace): 
    index.delete(delete_all=True, namespace=namespace) 
    
def clean_text(text):
    text = text.replace('\n', ' ')
    text = sub(r'\s+', ' ', text)
    text = sub(r'[§†‡]', '', text)
    # Merge split words
    text = sub(r'\b(\w+)-\s+(\w+)\b', r'\1\2', text)
    return text.strip()

@app.route('/api/upsert', methods=['POST'])
def upsert():
    data = request.json
    id = data.get('id')
    
    path = f'/Users/pingho/RAG-project/frontend/public/files/{str(id)}'
    namespaces = {} # Namespaces are the same as the file names
    try:
        for filename in os.listdir(path):
            full_path = os.path.join(path, filename)
            
            if os.path.isfile(full_path):
                # Extract the filename without extension
                name_without_extension = os.path.splitext(filename)[0]
                namespaces[name_without_extension] = [full_path]
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
    pinecone = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    pinecone_index_name = str(id)
    print(f'pinecone.list_indexes().names(): {pinecone.list_indexes().names()}')

    if pinecone_index_name not in pinecone.list_indexes().names():
        pinecone.create_index(
            name=pinecone_index_name,
            dimension=1536,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )

    embeddings = OpenAIEmbeddings(api_key=os.getenv('OPENAI_API_KEY'))

    pinecone_index = pinecone.Index(pinecone_index_name)

    for namespace, file_paths in namespaces.items():
        # database cleanup if namespace already exists
        stats = pinecone_index.describe_index_stats()
        if namespace in stats['namespaces'] and stats['namespaces'][namespace]['vector_count'] > 0: 
            print(f'Namespace {namespace} already has vectors. Cleaning up before loading new data.') 
            clean_namespace(pinecone_index, namespace) 
        else: 
            print(f'Namespace {namespace} is empty or does not exist. Proceeding with loading data.')
        
        # Load PDFs and upsert embeddings
        all_texts = load_pdfs(file_paths)
        upsert_embeddings(all_texts, embeddings, pinecone_index_name, namespace)

    print(f'Upserted documents into namespaces {list(namespaces.keys())}')
    
    return jsonify({'message': 'PDFs have been upserted into Pinecone successfully'}), 200

    
# @app.route('/query', methods=['POST'])
# def query():
#     user_input = request.form['user_input']
#     user_id = int(request.form['user_id'])
#     model_output = generate_model_output(user_input)
#     conn = connect_to_database()
#     cursor = conn.cursor()
#     cursor.execute(
#         'INSERT INTO history (user_id, user_input, model_output) VALUES (%s, %s, %s)',
#         (user_id, user_input, model_output)
#     )
#     conn.commit()
#     cursor.close()
#     conn.close()
#     flash(f'Query saved! Model output: {model_output}', 'success')
#     return redirect(url_for('index'))

# @app.route('/history/<int:user_id>')
# def view_history(user_id):
#     conn = connect_to_database()
#     cursor = conn.cursor()
#     cursor.execute(
#         'SELECT user_input, model_output, created_at FROM history WHERE user_id = %s ORDER BY created_at DESC',
#         (user_id,)
#     )
#     records = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('history.html', records=records)

# @app.route('/')
# def index():
#     return render_template('index.html')

# def generate_model_output(user_input):
#     return f'Processed: {user_input}'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
