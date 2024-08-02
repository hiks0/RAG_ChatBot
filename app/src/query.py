import os
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI
from dotenv import load_dotenv
from Chunks2embedding import TextEmbeddingIngestion
from langchain_chroma import Chroma
import chromadb.utils.embedding_functions as embedding_functions
import json
import chromadb
from ChatData import ChatDatabase

load_dotenv()
TEMPLATE_PATH = "../template.json"


class QAChain:
    def __init__(self, file_path, mongo_uri):
        OpenAI.api_key = os.getenv("OPENAI_KEY")
        self.chain = load_qa_chain(OpenAI(), chain_type="stuff", )
        temp = TextEmbeddingIngestion()
        self.client = chromadb.HttpClient()
        self.embedding_function = embedding_functions.HuggingFaceEmbeddingFunction(  # embedding function problem
            api_key="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",
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.document_search = temp.generate_embeddings(file_path=file_path)
        self.query = '''
        You are an expert assistant, trained to provide answers regarding a given PDF file.
        
        previous chat history: \n {chat_history}
        question:{question}
        
        Analyze the question and provide a JSON response following the schema:
        {json}
        
        '''
        self.mongo_handler = ChatDatabase(mongo_uri)

    def generate_query(self, user_id: str, question: str):
        chat_history = self.mongo_handler.get_chat_history(user_id)
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as template_file:
            content = template_file.read()
            json_template = json.loads(content)
            prompt_formatted = self.query.format(chat_history=chat_history, question=question,
                                                 json=json_template)
        return prompt_formatted

    def ask_question(self, user_id: str, question: str):
        db4 = Chroma(
            client=self.client,
            collection_name="my_collection",
            embedding_function=self.embedding_function,
        )
        docs = db4.similarity_search(question)
        query = self.generate_query(user_id, question)
        output = self.chain.run(input_documents=docs, question=query)
        return output



