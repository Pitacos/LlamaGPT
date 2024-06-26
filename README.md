# LlamaGPT

LlamaGPT es un proyecto desarrollado como parte de mi Trabajo de Fin de Grado (TFG) en la Universidad Rey Juan Carlos. Este software implementa una inteligencia artificial basada en modelos de lenguaje a gran escala (LLM) capaz de mantener conversaciones naturales y coherentes con los usuarios.

## Requisitos del Sistema

Para un rendimiento óptimo, es necesario conectarse a un servidor que disponga de gran potencia de GPUs. Los requisitos mínimos son:

- **GPU**: 32 GB de memoria
- **RAM**: 64 GB (recomendado)
- **CPU**: 16 núcleos (recomendado)

## Instalación

1. **Clonar el Repositorio**


    ```bash
      git clone https://github.com/Pitacos/LlamaGPT.git
      cd LlamaGPT
    ```

3. **Crear y Activar el Entorno Virtual**


    Es necesario crear un entorno virtual llamado `LlamaGPT`:

    ```bash
       python3 -m venv LlamaGPT
       source LlamaGPT/bin/activate
    ```    

4. **Instalar las Dependencias**


    Asegúrate de estar dentro del entorno virtual e instala las dependencias requeridas:

    ```bash
        pip install -r requirements.txt
    ```

6. **Estructura del Proyecto**


    Dentro del entorno virtual LlamaGPT, asegúrate de tener la siguiente estructura de carpetas:

        LlamaGPT/
        ├── source/            # Archivos del proyecto que se van a transmitir
        ├── files/
             ├── memories/      # Memoria del LLM
             ├── metrics/       # Métricas del proyecto
             ├── pdfs/          # PDFs del usuario
             └── states/        # Estado del LLM tras su creación
        
6. **Uso**
 
  
      Para iniciar el proyecto, ejecuta la interfaz del proyecto desde tu oredenador local, despúes de haber configurado las credenciales de tu servidor
       en el archivo GUI.py, y disfruta de la experiencia.
   
   ```python
      self.ssh_executor = SSHScriptExecutor(hostname='Host', port=22, username='user', password='password')
    ```
    ```bash
      python source/GUI.py
    ```

6. **Contribución**


    Si deseas contribuir a este proyecto, por favor sigue los siguientes pasos:
      
      - Haz un fork del proyecto.
   
      - Crea una nueva rama (git checkout -b feature-nueva-funcionalidad).
      
      - Realiza tus cambios y haz commit (git commit -am 'Añadir nueva funcionalidad').
   
      - Envía tus cambios a tu fork (git push origin feature-nueva-funcionalidad).
   
      - Abre un Pull Request en el repositorio original.



8. **Licencia**
 
  
   Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

   Nota: Este proyecto también utiliza modelos de Llama 2 de Meta, los cuales están disponibles bajo una licencia comercial. Al utilizar este proyecto, estás de acuerdo con cumplir con         los términos y condiciones de la licencia de Llama 2, la política de uso aceptable y la política de privacidad de Meta.
    
    Modelos disponibles:
    
    - Llama-2-7b
    - Llama-2-7b-chat
    - Llama-2-13b
    - Llama-2-13b-chat
    - Llama-2-70b
    - Llama-2-70b-chat
   
    Con cada descarga del modelo, recibirás una copia de la Licencia y la Política de Uso Aceptable.
    Puedes encontrar más información en el [repositorio de GitHub de Llama 2](https://github.com/facebookresearch/llama).


8. **Contacto**


   Para más información, puedes contactar conmigo a través de mi correo electrónico (`"luisdiezpita@gmail.com"`) o visitar mi perfil de GitHub.
