import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomPromptHandler:
    def __init__(self, base_prompt, openai_api_key, pinecone_api_key, pinecone_index_name, namespace):
        """
        Initialize the CustomPromptHandler.

        :param base_prompt: The base prompt template.
        :param openai_api_key: OpenAI API key for the language model.
        :param pinecone_api_key: Pinecone API key for vector database.
        :param pinecone_index_name: Name of the Pinecone index.
        :param namespace: Namespace for storing/retrieving data in Pinecone.
        """
        load_dotenv()  # Load environment variables from .env
        self.base_prompt = base_prompt
        self.embeddings = ChatOpenAI(api_key=openai_api_key)
        self.pinecone = Pinecone(api_key=pinecone_api_key)
        self.index_name = pinecone_index_name
        self.namespace = namespace
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        # Ensure Pinecone index exists
        if self.index_name not in [idx.name for idx in self.pinecone.list_indexes()]:
            logger.info(f"Index '{self.index_name}' does not exist. Creating it now...")
            spec = ServerlessSpec(cloud="aws", region="us-east-1")  # Customize as needed
            self.pinecone.create_index(name=self.index_name, dimension=1536, metric="cosine", spec=spec)

        self.vector_store = LangchainPinecone.from_existing_index(
            index_name=self.index_name, namespace=self.namespace, embedding=self.embeddings
        )

    def generate_custom_prompt(self, user_input):
        """
        Combine the base prompt with user input to generate a custom prompt.

        :param user_input: The user's custom prompt input.
        :return: The combined prompt.
        """
        return f"""
        {self.base_prompt}

        User Customization:
        {user_input}
        """

    def retrieve_similar_documents(self, query, top_k=5):
        """
        Retrieve the most relevant documents from the vector database.

        :param query: Query text for similarity search.
        :param top_k: Number of top results to retrieve.
        :return: List of relevant documents.
        """
        try:
            results = self.vector_store.similarity_search(query, k=top_k)
            logger.info(f"Retrieved {len(results)} documents for query: '{query}'")
            return results
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def generate_analysis(self, user_input):
        """
        Generate an analysis based on user input and retrieved documents.

        :param user_input: The user's custom input for analysis.
        :return: Generated analysis text.
        """
        # Generate the custom prompt
        custom_prompt = self.generate_custom_prompt(user_input)

        # Retrieve relevant documents from the vector database
        retrieved_docs = self.retrieve_similar_documents(query=user_input)

        if not retrieved_docs:
            return "No relevant documents found to generate analysis."

        # Combine the retrieved documents into the prompt
        doc_contents = "\n\n".join([doc.page_content for doc in retrieved_docs])
        complete_prompt = f"""
        {custom_prompt}

        Relevant Documents:
        {doc_contents}
        """

        # Use the language model to generate the analysis
        try:
            response = self.embeddings.invoke(complete_prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return "Error generating analysis."

    def upsert_documents(self, file_path):
        """
        Process and insert a new document into the vector database.

        :param file_path: Path to the document file.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                raw_text = file.read()

            # Split the document into chunks
            texts = self.text_splitter.split_text(raw_text)

            # Insert into the vector database
            self.vector_store.add_texts(texts, namespace=self.namespace)
            logger.info(f"Inserted {len(texts)} chunks from {file_path} into Pinecone namespace {self.namespace}.")
        except Exception as e:
            logger.error(f"Error upserting document {file_path}: {e}")

# Example Usage
if __name__ == "__main__":
    BASE_PROMPT = "You are an AI assistant specializing in systematic reviews."
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = "example-index"
    NAMESPACE = "medical-research"

    handler = CustomPromptHandler(
        base_prompt=BASE_PROMPT,
        openai_api_key=OPENAI_API_KEY,
        pinecone_api_key=PINECONE_API_KEY,
        pinecone_index_name=PINECONE_INDEX_NAME,
        namespace=NAMESPACE
    )

    # Example: Add documents
    handler.upsert_documents("example.txt")

    # Example: Generate analysis
    user_prompt = "Analyze the efficacy of COVID-19 vaccines."
    result = handler.generate_analysis(user_prompt)
    print(result)
