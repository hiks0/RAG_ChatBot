import chromadb
import uuid
from chromadb.config import Settings
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from TXT2Chunks import TextChunker
from dotenv import load_dotenv
from PDF2TXT import PDFTextExtractor

load_dotenv()
OUTPUT_FILE = "../data.txt"


class TextEmbeddingIngestion:
    def __init__(self):
        self.embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


    def generate_embeddings(self, file_path):
        extractor = PDFTextExtractor(file_path)
        extractor.clear_output_file()
        extractor.load_pdfs_from_directory()
        chunker = TextChunker(OUTPUT_FILE)
        chunks = chunker.get_chunks()
        client = chromadb.HttpClient(settings=Settings(allow_reset=True))
        client.reset()
        collection = client.create_collection(name="new_collection", metadata={"hnsw:space": "cosine"})
        for doc in chunks:
            collection.add(
                ids=[str(uuid.uuid1())], documents=doc
            )

