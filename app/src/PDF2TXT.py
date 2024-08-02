import os
import PyPDF2

OUTPUT_FILE = "../data.txt"


class PDFTextExtractor:
    def __init__(self, pdf_directory):
        self.pdf_directory = pdf_directory
        self.output_file = OUTPUT_FILE

    def extract_text_from_pdf(self, pdf_path):
        text = ""
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text()
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
        return text

    def save_text_to_single_file(self, text):
        with open(self.output_file, "a", encoding="utf-8") as file:
            file.write(text + "\n\n")

    def load_pdfs_from_directory(self):
        for filename in os.listdir(self.pdf_directory):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(self.pdf_directory, filename)
                text = self.extract_text_from_pdf(pdf_path)

                self.save_text_to_single_file(text)

    def clear_output_file(self):
        open(self.output_file, "w").close()


#
