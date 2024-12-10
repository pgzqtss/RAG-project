from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone
import os
import dotenv
import weave
# import tiktoken

# Initiate Pinecone and OpenAI embedding
dotenv.load_dotenv()
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
pinecone = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

# Instantiate OpenAI model 
model = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), 
                   model='gpt-3.5-turbo',
                   temperature=0)

# Instantiate Pinecone query, namespaces and index
review_question = "What is the efficacy of vaccines for COVID-19?"
namespaces = ['paper1','paper2','paper3'] # Names of Papers
index_name = 'meow'

# Search each paper
def search_namespace(query, index_name, embeddings, namespace, top_k=10):
    print(f'Searching namespace: {namespace}')
    docsearch = LangchainPinecone.from_existing_index(index_name=index_name, 
                                                      namespace=namespace,
                                                      embedding=embeddings)
    return docsearch.similarity_search(query, k=top_k)

# Generates questions that are used to make the systematic review for all papers
@weave.op()
def generate_review_questions(query, model):
    prompt = f'''
    You are a researcher tasked with creating a systematic review by synthesizing information 
    from multiple research papers. 
    The goal is to produce a comprehensive and rigorous systematic review based on a specific 
    research query. 
    Here is the query for the review: '{query}'.

    To guide the systematic review process, please generate **5 detailed and focused 
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
@weave.op()
def generate_review_answer(question, data, model):
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

# Generate a summary of answers to each question for one paper
@weave.op()
def generate_summary(answers, query, model):
    prompt = f'''
    You are a researcher working on a systematic review and analyzing individual research 
    papers to extract key insights.

    Here is the query guiding the review: '{query}'

    Below is the data extracted from one research paper. Your task is to analyze this data
    and generate a concise summary that includes:
    - Key points discussed in the paper
    - Significant findings relevant to the query
    - Critical evaluations or observations made in the paper

    Data:
    {answers}

    Please ensure the summary is well-structured, accurate, and focused on the aspects most 
    relevant to the query.

    Summary:
    '''
    return model.invoke(prompt).content

# Generate a systematic review based on each paper summary
@weave.op()
def generate_systematic_review(summaries, query, model):
    prompt = f'''
    You are a researcher tasked with creating a systematic review based on individual
    research paper summaries. 
    The goal is to synthesize the information into a coherent and detailed systematic review.
    Here is the query for the review: '{query}'

    Below are summaries of individual research papers relevant to the query:

    Summaries:
    {summaries}

    Please analyze the provided summaries, identify key themes, findings, and trends, and
    generate a detailed systematic review.

    Systematic Review:
    '''

    return model.invoke(prompt).content

# Change how summaries are saved
# Make each paper and question in each paper run in parallel
# Check for token size
# Check for accuracy score
weave.init('Rag-n-Bones')
questions = generate_review_questions(query=review_question, model=model)
summaries = []
for paper in namespaces:
    summary = []
    for question in questions:
        data = search_namespace(query=question, 
                                index_name=index_name, 
                                embeddings=embeddings,
                                namespace=paper)
        
        answer = generate_review_answer(question=question, 
                                        data=data, 
                                        model=model)
        summary.append(answer)
    summaries.append(summary)
systematic_review = generate_systematic_review(summaries=summaries, 
                                                query=review_question,
                                                model=model)
print(f'Systematic Review: {systematic_review}')
