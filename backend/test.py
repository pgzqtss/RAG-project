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
    path = f'/Users/pingho/RAG-project/frontend/public/files/{str(id)}'
    namespaces = {} # Namespaces are the same as the file names

    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        
        if os.path.isfile(full_path):
            # Extract the filename without extension
            name_without_extension = os.path.splitext(filename)[0]
            namespaces[name_without_extension] = [full_path]

    return namespaces

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

# Function to compute the summary accuracy score using ChatGPT reasoning
def compute_summary_accuracy(summary_text, namespace, review_question):
    original_data = search_namespace(query=review_question,
                                      namespace=namespace)
    original_text = " ".join([text.page_content for text in original_data])

    print(f'Calculating summary accuracy score of {namespace}')
    prompt = f'''
    You are tasked with evaluating how well the following summary matches the original research context.
    Based on your analysis, provide a score between 0 and 100 (inclusive) that represents how accurately
    the summary reflects the main findings, conclusions, and insights of the original research.

    Summary:
    {summary_text}

    Original Text:
    {original_text}

    Return only the final score as a number (no extra text).
    '''
    response = model.invoke(prompt)
    try:
        score_text = response.content.strip()
        # Extract only the digits in case of any text
        match = search(r'\d+', score_text) 
        if match:
            score = int(match.group())  # Extract number and convert to integer
        else:
            score = 0
    except ValueError:
        score = 0

    return score

def get_accuracy_score(summaries, namespaces, review_question):
    scores = {paper : 0 for paper in namespaces}
    with ThreadPoolExecutor() as executor:
        # Map each question's namespace with their respective summaries
        future_to_summary = {
            executor.submit(compute_summary_accuracy, summaries.get(namespaces[i]), namespaces[i], review_question): i
            for i in range(len(namespaces))
        }

        for future in as_completed(future_to_summary):
            try:
                score = future.result()  # Waits for the computation to finish and fetch the result
                scores[namespaces[future_to_summary[future]]] = score
            except Exception as e:
                print(f"Error computing summary accuracy for namespace index {future_to_summary[future]}: {e}")
    return scores

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

def filter_low_accuracy_papers(summaries, namespaces, review_question, threshold=70):
    scores = get_accuracy_score(summaries=summaries,
                                namespaces=namespaces,
                                review_question=review_question)

    # Remove papers below the accuracy threshold
    filtered_summaries = {paper: summaries[paper] for paper in summaries if scores.get(paper, 0) >= threshold}

    return filtered_summaries, scores

@app.route('/api/generate', methods=['POST'])
def generate():
    # sleep(5)
    return jsonify({'message': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'}), 200


def main():
    # data = request.json
    # review_question = data.get('prompt')
    # id = data.get('id')
    id = '2316689836'
    review_question = 'What is the efficacy of COVID-19 vaccines?'
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

    # Filter each summary by accuracy
    filtered_summaries, scores = filter_low_accuracy_papers(summaries=summaries,
                                                            namespaces=namespaces,
                                                            review_question=review_question)

    # Generate systematic review from summaries
    systematic_review = generate_systematic_review(summaries=filtered_summaries, 
                                                    query=review_question)

    print(f'Systematic Review: {systematic_review}')
    print(f'Scores: {scores}')

main();