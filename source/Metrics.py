import subprocess
import re
import time
import psutil
import pickle

class Metrics():
    METRICS_FILE_PATH = 'LlamaGPT/source/files/metrics/metrics.pkl'

    def __init__(self):
        self.gpu_memory_usage = []
        self.cpu_usage = [] 

    def get_gpu_info(self):
        result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, text=True, shell=True)
        gpu_info = result.stdout
        return gpu_info

    def extract_memory_usage(self, gpu_info):
        memory_matches = re.findall(r'(\d+)MiB / (\d+)MiB', gpu_info)
        if memory_matches:
            memory_usage = [int(match[0]) for match in memory_matches]
            return memory_usage
        return None
    
    def monitor_memory_usage(self,detener_hilo):
        while not detener_hilo.is_set():
            gpu_info = self.get_gpu_info()
            memory_info = self.extract_memory_usage(gpu_info)
            self.gpu_memory_usage.append(memory_info)
            time.sleep(2)

    def monitor_cpu_usage(self, detener_hilo):
        while not detener_hilo.is_set():
            cpu_percent = psutil.cpu_percent(interval=2)
            self.cpu_usage.append(cpu_percent)
    
    def serialize_gpu_metrics(self):
        with open(self.METRICS_FILE_PATH, 'wb') as archivo:
            pickle.dump(self.gpu_memory_usage, archivo)

    def serialize_cpu_metrics(self):
        with open(self.METRICS_FILE_PATH, 'wb') as archivo:
            pickle.dump(self.cpu_usage, archivo)
