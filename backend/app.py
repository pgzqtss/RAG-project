from flask import Flask, request, jsonify
import mysql.connector
import bcrypt
from flask_cors import CORS

import os
import dotenv
from re import sub, search
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app)

dotenv.load_dotenv()
pinecone = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
pinecone_index_name = os.getenv('PINECONE_INDEX_NAME')
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
model = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), 
                   model='gpt-3.5-turbo',
                   temperature=0)

def get_namespaces(id):
    path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'files', str(id))
    namespaces = {} # Namespaces are the same as the file names

    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        
        if os.path.isfile(full_path):
            # Extract the filename without extension
            name_without_extension = os.path.splitext(filename)[0]
            namespaces[name_without_extension] = [full_path]

    return namespaces

def connect_to_database():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password=os.getenv('MYSQL_PASSWORD'),
        database='user_data'
    )

'''

Login & Signup Functions

'''

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
    

'''

Upsert Vectors into Pinecone

'''
    
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
from time import sleep
def upsert():
    sleep(5)
    return jsonify({'message': 'PDFs have been upserted into Pinecone successfully'}), 200

@app.route('/api/upsert', methods=['POST'])
def upsert2():
    data = request.json
    id = data.get('id')
    
    try:
        namespaces = get_namespaces(id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
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


'''

Generate Systematic Review

'''

def search_namespace(query, namespace, top_k=10):
    print(f'Searching namespace: {namespace}')
    docsearch = LangchainPinecone.from_existing_index(index_name=pinecone_index_name, 
                                                      namespace=namespace,
                                                      embedding=embeddings)
    return docsearch.similarity_search(query, k=top_k)

# Generates questions that are used to make the systematic review for all papers
def generate_review_questions(review_question):
    print(f'Generating questions from query: {review_question}')
    prompt = f'''
    You are a researcher tasked with creating a systematic review by synthesizing information 
    from multiple research papers. 
    The goal is to produce a comprehensive and rigorous systematic review based on a specific 
    research query. 
    Here is the query for the review: '{review_question}'.

    To guide the systematic review process, please generate **10 detailed and focused 
    questions** that can be consistently asked for each paper. 
    These questions should help extract relevant insights, findings, or data from the papers 
    in a way that aligns with the query.

    Provide the questions in a clear and concise format.

    List of questions:
    '''

    questions = model.invoke(prompt)
    separated_questions = [line.strip() for line in 
                           questions.content.strip().split('\n') if line.strip()]
    return separated_questions

# Generates answers to a question for one paper using the most similar vector data
def generate_review_answer(question, data, paper):
    print(f'Generating answer for {paper} to the question: {question}')
    prompt = f'''
    You are a researcher working on a systematic review. To create the review, you are 
    analyzing individual research papers to extract relevant information.

    Here is the question being addressed: '{question}'

    Below is the data from a single research paper that may contain an answer to the 
    question:

    Data:
    {data}

    Please analyze the data carefully and generate a detailed, accurate, and concise answer 
    to the question.

    Answer:
    '''
    return model.invoke(prompt).content

# Generate answers for each question per paper concurrently
def generate_answers(questions, namespaces):
    answers = {paper: [] for paper in namespaces}  # Initialize summaries dictionary

    with ThreadPoolExecutor() as executor:
        # Submit all question-answering tasks
        future_to_question = {
            executor.submit(answer_question_for_paper, question, paper): (question, paper)
            for paper in namespaces
            for question in questions
        }

        # Collect results
        for future in as_completed(future_to_question):
            try:
                question, paper = future_to_question[future]
                response = future.result()  # Get the answer for the question
                answers[paper].append(response[2])  # Extract and append the generated answer
            except Exception as e:
                print(f"Error processing question '{question}' for namespace '{paper}': {e}")

    return answers

# Generate a summary of answers to each question for one paper
def generate_summary(answers, paper, review_question):
    print(f'Generating summaries of paper: {paper}')
    prompt = f'''
    You are a researcher working on a systematic review and analyzing individual research 
    papers to extract key insights.

    Here is the query guiding the review: '{review_question}'

    Below is the data extracted from one research paper. Your task is to analyze this data
    and generate a concise summary that includes:
    - Key points discussed in the paper
    - Significant findings relevant to the query
    - Critical evaluations or observations made in the paper
    - Specific data points within the paper

    Data:
    {answers}

    Please ensure the summary is well-structured, accurate, and focused on the aspects most 
    relevant to the query.

    Summary:
    '''
    return model.invoke(prompt).content

def generate_summaries(answers, namespaces, review_question):
    summaries = {paper: [] for paper in namespaces}

    with ThreadPoolExecutor() as executor:
        future_to_summary = {
            executor.submit(generate_summary, answers.get(paper), paper, review_question): paper
            for paper in namespaces
        }

        for future in as_completed(future_to_summary):
            try:
                response = future.result()
                summaries[future_to_summary[future]] = response
            except Exception as e:
                 print(f"Error processing answers '{answers}' for namespace '{future_to_summary[future]}': {e}")
    return summaries

# Generate a systematic review based on each paper summary
def generate_systematic_review(summaries, query):
    print('Generating systematic review.')
    prompt = f'''
    You are a researcher tasked with creating a systematic review based on individual
    research paper summaries. 
    The goal is to synthesize the information into a coherent and detailed systematic review.
    Here is the query for the review: '{query}'

    Below are summaries of individual research papers relevant to the query:

    Summaries:
    {summaries}

    Please analyze the provided summaries, identify key themes, findings, and trends, and
    generate a detailed systematic review. Include evalutations and any limitations.

    Systematic Review:
    '''

    return model.invoke(prompt).content

# Ran concurrently with ThreadPoolExecutor
def answer_question_for_paper(question, paper):
    # Search namespace for data
    data = search_namespace(query=question,  
                             namespace=paper)
    
    # Generate the answer
    answer = generate_review_answer(question=question, 
                                    data=data, 
                                    paper=paper)
    return question, paper, answer

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    review_question = data.get('prompt')
    id = data.get('id')

    try:
        namespaces = get_namespaces(id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Get questions used for a systematic review
    questions = generate_review_questions(review_question=review_question)

    # Get all answers from each paper
    answers = generate_answers(questions=questions, 
                               namespaces=namespaces)

    # Get summary of each paper
    summaries = generate_summaries(answers=answers, 
                                   namespaces=namespaces, 
                                   review_question=review_question)

    # Generate systematic review from summaries
    systematic_review = generate_systematic_review(summaries=summaries, 
                                                    query=review_question)

    print(f'Systematic Review: {systematic_review}')

    return jsonify({'systematic_review': systematic_review}), 200


'''

History Database Functions

'''

@app.route('/api/save', methods=['POST'])
def save_history():
    data = request.json
    user_id = data.get('user_id')
    user_id = user_id[0]
    prompt_id = data.get('prompt_id')
    prompt = data.get('prompt')
    systematic_review = data.get('systematic_review')

    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO history (user_id, prompt_id, user_input, model_output) VALUES (%s, %s, %s, %s)',
            (user_id, prompt_id, prompt, systematic_review)
        )
        conn.commit()
        return jsonify({'message': 'Systematic review has been stored successfully'})
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Systematic review already exists'}), 409
    finally:
        cursor.close()
        conn.close()

@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    prompt_id = data.get('prompt_id')

    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT user_input, model_output FROM history WHERE prompt_id = %s',
            (prompt_id,)
        )
        result = cursor.fetchone()
        user_input, model_output = result
        return jsonify({'message': 'Found systematic review successfully',
                        'prompt': user_input,
                        'systematic_review': model_output}), 200
    except:
        return jsonify({'error': 'No systematic review found'}), 404
    finally:
        cursor.close()
        conn.close()

@app.route('/api/query_user', methods=['POST'])
def query_user():
    data = request.json
    username = data.get('username')
    print(f'Username: {username}')

    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT id FROM users WHERE username = %s',
            (username,)
        )
        result = cursor.fetchone()
        return jsonify({'message': 'Found user successfully',
                        'user_id': result}), 200
    except:
        return jsonify({'error': 'No user found'}), 404
    finally:
        cursor.close()
        conn.close()
        

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
