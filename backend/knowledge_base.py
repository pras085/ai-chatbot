import os
import json
from backend.app.utils.rag_utils import PDFProcessor


class KnowledgeBase:
    def __init__(self, pdf_filename):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.pdf_file = os.path.join(current_dir, "src", pdf_filename)
        print(f"Attempting to access PDF at: {self.pdf_file}")  # Debug print
        self.knowledge = self.refresh_knowledge()

    def refresh_knowledge(self):
        if not os.path.exists(self.pdf_file):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_file}")
        return PDFProcessor.extract_text_from_pdf(self.pdf_file)

    def get_knowledge(self):
        return self.knowledge

    def add_knowledge(self, new_knowledge):
        self.knowledge.append(new_knowledge)

    def remove_knowledge(self, index):
        return self.knowledge.pop(index) if 0 <= index < len(self.knowledge) else None

    def save_to_file(self, filename):
        with open(filename, "w") as f:
            json.dump(self.knowledge, f)

    def load_from_file(self, filename):
        with open(filename, "r") as f:
            self.knowledge = json.load(f)


# Initialization
PDF_FILE = "about_muatmuat.pdf"
knowledge_base = KnowledgeBase(PDF_FILE)
