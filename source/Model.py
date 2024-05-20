from transformers import AutoTokenizer
import transformers
import torch
import cloudpickle

class Model():

    STATE_FILE_PATH = 'LlamaGPT/source/files/states/state.pkl'
    CONFIG_PATH= 'LlamaGPT/source/files/states/config.txt'

    def __init__(self):
        device, self.lenght, self.temperature = self.read_device(Model.CONFIG_PATH)
        if device == 'gpu':
            self.device = 'auto'
        else: 
            self.device = 'cpu'

    def load_model(self,model):
        if self.device == 'cpu':
            torch_dtype=torch.float32
        else:
            torch_dtype=torch.float16

        tokenizer = AutoTokenizer.from_pretrained(model,  use_fast=True)
        pipeline = transformers.pipeline(
            "text-generation",
            model= model, 
            torch_dtype=torch_dtype,
            device_map=self.device,
            tokenizer=tokenizer,
        )
        return tokenizer, pipeline
    

    def asking(self,tokenizer, pipeline, question, max_length, temperature, top_k=10):
        sequences = pipeline(
            question,
            do_sample = True,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            top_k=top_k,
            max_length=max_length,
            temperature=temperature,
            truncation = True
        )
        response = sequences[0]['generated_text'][len(question):].strip()
        return response

    
    def save_state(self, tokenizer, pipeline):
        state = {'tokenizer': tokenizer, 'pipeline': pipeline}
        with open(self.STATE_FILE_PATH, 'wb') as file:
            cloudpickle.dump(state, file, protocol=cloudpickle.DEFAULT_PROTOCOL)

    def load_state(self):
        with open(self.STATE_FILE_PATH, 'rb') as file:
            state = cloudpickle.load(file)
        return state['tokenizer'], state['pipeline']

    def read_device(self, file_path):
        try:
            with open(file_path, "r") as file:
                first_line = file.readline().split()[1]
                second_line = file.readline().split()[1]
                third_line = file.readline().split()[1]
            return first_line, second_line, third_line
        except Exception as e:
            print(f"Error al leer la primera línea: {e}")
            return None