import os
import pickle
import fitz
import glob

class ConversationMemory:
    
    MEMORY_FILE_PATH = 'LlamaGPT/source/files/memories/memory.pkl'
    MEMORYPDF_FILE_PATH = 'LlamaGPT/source/files/memories/memoryPDF.pkl'

    def __init__(self, max_length=100):
        self.max_length = max_length
        self.memory = {}

    def add_interaction(self, question, response):
        # Almacena directamente la pregunta y respuesta
        self.memory[question] = response

        # Mantener la memoria dentro del límite
        if len(self.memory) > self.max_length:
            # Eliminar la pregunta más antigua para mantener el límite
            oldest_question = next(iter(self.memory))
            del self.memory[oldest_question]

    #Serializar Objeto        
    def save_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(self, file)

    def load_from_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                loaded_memory = pickle.load(file)
                self.memory = loaded_memory.memory
        except FileNotFoundError:
            raise

    def load_context(self, pdf_filename=None):
        if pdf_filename is None:
            # Si no se proporciona un nombre de archivo específico, buscar automáticamente un archivo PDF en la carpeta
            pdf_files = glob.glob("LlamaGPT/source/files/pdfs/*.pdf")
            if len(pdf_files) == 1:
                pdf_filename = pdf_files[0]
        try:
            doc = fitz.open(pdf_filename)
            pdf_text = ""
            for page_num in range(doc.page_count):
                page = doc[page_num]
                blocks = page.get_text("blocks")
                for block in blocks:
                    pdf_text += block[4] + ' '
                    
            self.memory['pdf_context'] = pdf_text
        except FileNotFoundError:
            self.memory['pdf_context'] = ""


    def get_context(self):
        pdf_context = self.memory['pdf_context']
        pdf_context= pdf_context.replace('\n', '')
        return pdf_context
    
    def print_conversation(self):
        for question, response_list in self.memory.items():
            # Imprimir cada interacción
            for response in response_list:
                print(f"Usuario: {question}")
                print(f"Sistema: {response}")
                print()