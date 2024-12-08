from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone
import os
import dotenv

# Initialize embeddings and Pinecone

dotenv.load_dotenv()
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
pinecone = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

def search_across_namespaces(query, index_name, embeddings, namespaces, top_k=10):
    combined_results = []
    for namespace in namespaces:
        print(f"Searching in namespace: {namespace}")
        # Initialize the Pinecone vector store for the namespace
        docsearch = LangchainPinecone.from_existing_index(index_name=index_name, namespace=namespace, embedding=embeddings)
        # Perform the similarity search
        results = docsearch.similarity_search(query, k=top_k)
        combined_results.extend(results)
    return combined_results

def generate_questions(query, model):
    # Create a prompt for systematic review
    prompt = f"""
    You are a researcher wanting to create a systematic review. Here is the query for the review: "{query}".
    Please generate a list of 5 questions that can be asked for each paper that can later be used
    to produce a systematic review.

    List of Questions:
    """
    return model.invoke(prompt)

# Perform search across namespaces
query = "What is the efficacy of vaccines for COVID-19?"
namespaces = ['paper1','paper2','paper3']  # List of namespaces
index_name = 'meow'
# results = search_across_namespaces(query, index_name=index_name, embeddings=embeddings, namespaces=namespaces)

# Generate systematic review 
model = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Use your LLM
review = generate_questions(query, model)
print(review.content)

# Split questions by line and clean
questions = [line.strip() for line in review.content.strip().split('\n') if line.strip()]
clean_questions = [q[q.find('.')+1:].strip() for q in questions]

def generate_answers(results, query, model):
    combined_content = "\n\n".join([res.page_content for res in results])
    
    # Create a prompt for answers
    prompt = f"""
    You are a researcher making a systematic review. 
    Here is a collection of text chunks relevant to the query: "{query}".
    Please generate a summary of the following data that answers the query while
    maintaining the information about each paper.

    Data:
    {combined_content}
    
    Systematic Review:
    """
    return model.invoke(prompt)

# Database for results
concatenated_results = {q[q.find('.')+1:].strip(): "" for q in questions}

for question in questions:
    answers = search_across_namespaces(question, index_name=index_name, embeddings=embeddings, namespaces=namespaces)
    answer_summary = generate_answers(answers, query, model).content
    concatenated_results[question] = answer_summary
    print(f'Question: {question}\nAnswer:{answer_summary}')