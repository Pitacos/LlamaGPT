import os
import sys
import threading
from Metrics import Metrics
from Model import Model

class LoadModel(Model):
    MODEL_FILE_PATH = 'meta-llama/Llama-2-7b-chat-hf'

    def __init__(self): 
        super().__init__()
        os.environ["TOKENIZERS_PARALLELISM"] = "false"  
        self.model= self.MODEL_FILE_PATH
        self.metrics = Metrics()
        self.detener_hilo = threading.Event()

         # Crear un hilo para monitorear el Memory Usage 
        if self.device == 'auto':
            self.thread= threading.Thread(target=self.metrics.monitor_memory_usage, args=[self.detener_hilo])
        else:
            self.thread= threading.Thread(target=self.metrics.monitor_cpu_usage, args=[self.detener_hilo])

    def config (self):
        self.thread.start()
        try:
            if not os.path.exists(self.STATE_FILE_PATH):
                tokenizer, pipeline = self.load_model(self.model)
                self.save_state(tokenizer,pipeline)
            else:
                print(f"Error al cargar el estado. Elimina el archivo {self.STATE_FILE_PATH} y vuelve a ejecutar el script.")
                sys.exit(1)
        except FileNotFoundError:
            print(f"Error: File not found - {self.STATE_FILE_PATH}")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        self.detener_hilo.set()
        self.thread.join()

        if self.device == 'auto':
            self.metrics.serialize_gpu_metrics()
        else:
            self.metrics.serialize_cpu_metrics()

        

    

if __name__ == '__main__':
    load_model = LoadModel()
    load_model.config()
