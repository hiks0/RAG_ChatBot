from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer





class TextChunker:
    def __init__(self, file_path, chunk_size=1):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.text = self._read_text()
        self.chunks = self._chunk_text()

    def _read_text(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                content = file.read()
            return content
        except Exception as e:
            print(f"Error reading {self.file_path}: {e}")
            return None

    def _chunk_text(self):
        max_tokens = 100
        tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
        splitter = TextSplitter.from_huggingface_tokenizer(tokenizer, max_tokens)
        chunks = splitter.chunks(self.text)
        return chunks

    def get_chunks(self):
        return self.chunks



