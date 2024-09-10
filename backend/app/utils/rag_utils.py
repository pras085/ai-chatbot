import os
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List


class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            return "\n".join(page.extract_text() for page in reader.pages)

    @staticmethod
    def process_pdf_directory(directory_path: str) -> List[str]:
        knowledge = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(directory_path, filename)
                text = PDFProcessor.extract_text_from_pdf(file_path)
                chunks = text.split("\n")
                knowledge.extend([chunk.strip() for chunk in chunks if chunk.strip()])
        return knowledge


class RAGModel:
    def __init__(self, knowledge_base: List[str]):
        self.vectorizer = TfidfVectorizer()
        self.knowledge_base = knowledge_base
        self.knowledge_vectors = self.vectorizer.fit_transform(knowledge_base)

    def find_relevant_knowledge(self, query: str, top_k: int = 2) -> List[str]:
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.knowledge_vectors).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [self.knowledge_base[i] for i in top_indices]

    def update_knowledge_base(self, new_knowledge_base: List[str]):
        self.knowledge_base = new_knowledge_base
        self.knowledge_vectors = self.vectorizer.fit_transform(self.knowledge_base)
