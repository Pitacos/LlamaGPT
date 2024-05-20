import threading
import os
import sys
from Memory import ConversationMemory
from Metrics import Metrics
from Model import Model

class PDFConversation(Model):
    
    def __init__(self): 
        super().__init__()
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        self.pipeline = None
        self.tokenizer= None
        self.memory = ConversationMemory()
        self.metrics = Metrics()
        self.detener_hilo = threading.Event()

          # Crear un hilo para monitorear el Memory Usage 
        if self.device == 'auto':
            self.thread= threading.Thread(target=self.metrics.monitor_memory_usage, args=[self.detener_hilo])
        else:
            self.thread= threading.Thread(target=self.metrics.monitor_cpu_usage, args=[self.detener_hilo])

        try:
            # Intenta cargar desde el archivo de memoria
            self.memory.load_from_file(self.memory.MEMORYPDF_FILE_PATH)
        except (FileNotFoundError, EOFError):
        # Si el archivo de memoria tampoco existe o hay un error EOFError, carga el contexto
            self.memory.load_context()
            self.memory.save_to_file(self.memory.MEMORYPDF_FILE_PATH)

    def config (self):
        self.thread.start()

        try:
            # Intenta cargar el estado guardado
            self.tokenizer, self.pipeline = self.load_state()
        except (FileNotFoundError, EOFError):
            print(f"Error al cargar el estado. Elimina el archivo {self.STATE_FILE_PATH} y vuelve a ejecutar el script.")
            sys.exit(1)

    def main(self):
        user_question = sys.argv[1]
        context = self.memory.get_context()
        question = context + '/n' + user_question
        response = self.asking(self.tokenizer, self.pipeline, question, 4096, float(self.temperature))
        self.detener_hilo.set()
        self.thread.join()
        # Crear un hilo para monitorear el Memory Usage 
        if self.device == 'auto':
            self.metrics.serialize_gpu_metrics()
        else:
            self.metrics.serialize_cpu_metrics()
        print(response)



if __name__ == '__main__':
     
    pdfConver = PDFConversation()
    pdfConver.config()
    pdfConver.main()
    
   