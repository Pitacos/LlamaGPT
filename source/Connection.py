import paramiko
from scp import SCPClient
import pickle
import os


class SSHScriptExecutor:
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.activate_command = 'source LlamaGPT/bin/activate'
        self.script_local_path=''
        self.script_remote_path=''
        self.metrics_remote_path =''
        self.local_pdf = ''
        self.remote_pdf= ''
        self.last_pdf=''
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        

    def connect(self):
        try:
            self.client.connect(self.hostname, self.port, self.username, self.password)
        except Exception as e:
            print(f"Error connecting to the server: {e}")
            raise

    def transfer_scripts(self,pdf_path):
        if pdf_path == None:
            self.metrics_remote_path = 'LlamaGPT/source/files/metrics/metrics.pkl'
            self.script_local_paths  = ['source/Normal_Conver.py','source/PDF_Conver.py', 'source/LoadModel.py', 'source/Memory.py', 'source/Metrics.py', 'source/Model.py', 'files/config.txt']
            self.script_remote_paths = ['LlamaGPT/source/Normal_Conver.py','LlamaGPT/source/PDF_Conver.py.py','LlamaGPT/source/LoadModel.py','LlamaGPT/source/Memory.py', 'LlamaGPT/source/Metrics.py', 'LlamaGPT/source/Model.py','LlamaGPT/source/files/states/config.txt' ]
        else:
            self.last_pdf=self.remote_pdf
            name = os.path.basename(pdf_path)
            self.local_pdf  = [pdf_path]
            self.remote_pdf= ['LlamaGPT/source/files/pdfs/'+ name.replace(" ", "")]

        try: 
            if pdf_path:
                if self.last_pdf!='':
                    #Definir la ruta del archivo a eliminar en el servidor remoto
                    delete_file = self.last_pdf[0]
                    delete_memory= 'LlamaGPT/source/files/memories/memoryPDF.pkl'
                    # Construir el comando para eliminar el archivo usando el comando rm
                    command= f'rm {delete_file} {delete_memory}'
                    # Ejecutar el comando en el servidor remoto mediante SSH
                    stdin, stdout, stderr = self.client.exec_command(command)

                with SCPClient(self.client.get_transport()) as scp:
                    for local_path, remote_path in zip(self.local_pdf, self.remote_pdf):
                            scp.put(local_path, remote_path=remote_path)  
            else:
                with SCPClient(self.client.get_transport()) as scp:
                    for local_path, remote_path in zip(self.script_local_paths, self.script_remote_paths):
                            scp.put(local_path, remote_path=remote_path)  

        except Exception as e:
                print(f"Error transferring script to the server: {e}")
                raise

    def execute_load_model(self):
        full_command = f'{self.activate_command} && python {self.script_remote_paths[2]}'
        stdin, stdout, stderr = self.client.exec_command(full_command)
        error_output = stderr.read().decode()
        print(error_output)
        response_lines = [line.strip() for line in stdout]
        response_text = "\n".join(response_lines)
        print(response_text)
        # Leer y deserializar el objeto directamente desde el servidor remoto
        with self.client.open_sftp().file(self.metrics_remote_path, 'rb') as file:
            metrics = pickle.load(file)
        return metrics

    def execute_script(self, user_question, is_pdf):
        try:
            if is_pdf:
                full_command = f'{self.activate_command} && python {self.script_remote_paths[1]} "{user_question}"'
            else:
                full_command = f'{self.activate_command} && python {self.script_remote_paths[0]} "{user_question}"'

            
            # Agregar las líneas de salida al cuadro de texto de conversación en la GUI
            # Capturar y mostrar errores durante la ejecución en el servidor
            stdin, stdout, stderr = self.client.exec_command(full_command)
            error_output = stderr.read().decode('utf-8')
            print(f"Salida de error remota: {error_output}")
            # Recolectar la salida del script en el servidor
            response_lines = [line.strip() for line in stdout]
            response_text = "\n".join(response_lines)
            # Leer y deserializar el objeto directamente desde el servidor remoto
            with self.client.open_sftp().file(self.metrics_remote_path, 'rb') as file:
                metrics = pickle.load(file)
    
            return response_text, metrics
        
        except Exception as e:
            error_message = f"Error executing script on the server: {e}"
            raise

    def delete_files(self):
        delete_pdf = ''
        delete_memory = ''
        try:
            # Verificar si la conexión SSH está activa
            if self.client is None:
                print("SSH connection is not active.")
                return
            # Verificar si la conexión SSH está activa
            transport = self.client.get_transport()
            if transport is not None and transport.is_active():
                if self.remote_pdf!='':
                    delete_pdf = self.remote_pdf[0]
                    delete_memory = 'LlamaGPT/source/files/memories/memoryPDF.pkl'
                # Definir la ruta del archivo a eliminar en el servidor remoto
                delete_file = 'LlamaGPT/source/files/states/state.pkl'
                # Construir el comando para eliminar el archivo usando el comando rm
                comando = f'rm {delete_file} {delete_memory} {delete_pdf}'
                # Ejecutar el comando en el servidor remoto mediante SSH
                stdin, stdout, stderr = self.client.exec_command(comando)
                error_output = stderr.read().decode('utf-8')
                print(f"Salida de error remota: {error_output}")
        except Exception as e:
            # Si ocurre una excepción durante el proceso, imprimir un mensaje de error
            print(f"Error delete files: {e}")

            # Volver a generar la excepción para propagarla más adelante si es necesario
            raise

    def close_connection(self):
        
        try:
            self.delete_files()
            # Cerrar la conexión SSH
            self.client.close()
        except Exception as e:
            # Si ocurre una excepción durante el proceso, imprimir un mensaje de error
            print(f"Error closing the SSH connection: {e}")

            # Volver a generar la excepción para propagarla más adelante si es necesario
            raise
