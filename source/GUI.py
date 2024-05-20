import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import fitz
from ttkthemes import ThemedTk
from Connection import SSHScriptExecutor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

class WelcomeTab(ttk.Frame):
    def __init__(self, master, switch_callback):
        super().__init__(master)

        ttk.Label(self, text="LlamaGPT", font=("Helvetica", 24, "bold"), anchor="center").pack(pady=20)
        ttk.Label(self, text="LlamaGPT te brinda una experiencia de lectura única en dos niveles. \nEn el modo básico, conversa con el lenguaje; \ny en el modo avanzado, ¡dialoga directamente con el contenido de tu PDF! \n¡Disfruta de la versatilidad y sumérgete en una lectura interactiva a tu medida!", font=("Helvetica", 14), anchor="center").pack(pady=10)

        # Entry para elegir entre GPU y CPU
        self.device_var = tk.StringVar(value="gpu")  # Valor predeterminado: GPU
        ttk.Label(self, text="Selecciona el dispositivo:", font=("Helvetica", 12)).pack(pady=5)
        ttk.Radiobutton(self, text="GPU", variable=self.device_var, value="gpu").pack(pady=5, anchor="center")
        ttk.Radiobutton(self, text="CPU", variable=self.device_var, value="cpu").pack(pady=5, anchor="center")
        
        # Entry para la longitud (min: 100, max: 4096)
        self.length_var = tk.IntVar(value=500)  # Valor predeterminado: 500
        ttk.Label(self, text="Longitud (min: 100, max: 4096):", font=("Helvetica", 12)).pack(pady=5)
        ttk.Entry(self, textvariable=self.length_var).pack(pady=5)

        # Entry para la temperatura (min: 0, max: 1)
        self.temperature_var = tk.DoubleVar(value=0.5)  # Valor predeterminado: 0.5
        ttk.Label(self, text="Temperatura (min: 0, max: 1):", font=("Helvetica", 12)).pack(pady=5)
        ttk.Entry(self, textvariable=self.temperature_var).pack(pady=5)

        # Label para explicar el propósito de los parámetros
        ttk.Label(self, text="Estos parámetros modifican el modelo de lenguaje. Si no se alteran se cargará la configuracion predeterminada.", font=("Helvetica", 10), anchor="center", foreground="gray").pack(pady=10)

        ttk.Button(self, text="Empezar", command=lambda: self.start_and_save_configuration(switch_callback)).pack(pady=10)

    def start_and_save_configuration(self, switch_callback):
        # Obtener los valores de los parámetros
        device = self.device_var.get()
        length = self.length_var.get()
        temperature = self.temperature_var.get()

        # Guardar la configuración en un archivo
        self.save_configuration(device, length, temperature)

        # Llamar al callback para cambiar a la interfaz principal
        switch_callback()

    def save_configuration(self, device, length, temperature):
        with open("files/config.txt", "w") as file:
            file.write(f"Dispositivo: {device}\n")
            file.write(f"Longitud: {length}\n")
            file.write(f"Temperatura: {temperature}\n")

class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Interfaz Gráfica para Conversación")
        self.pdf_context = ""
        self.pdf_path=""
        self.conversation_type = tk.StringVar(value="normal")
        self.ssh_executor = None
        self.metrics_graph_created = False
        self.master.withdraw()

        self.create_main_interface()
        self.create_welcome_tab()

        # Ocultar las pestañas principales al inicio
        self.notebook.hide(self.metrics_tab)
        self.notebook.hide(self.normal_conversation_tab)
        self.notebook.hide(self.pdf_conversation_tab)

        # Mostrar la pestaña de bienvenida al inicio
        self.notebook.select(self.welcome_tab)
        # Bind the close event to the cleanup method
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_welcome_tab(self):
        self.welcome_tab = WelcomeTab(self.notebook, self.switch_to_main_interface)
        self.notebook.add(self.welcome_tab, text="Bienvenida")

    def on_closing(self):
        # Llamada al método para destruir el gráfico y cerrar la conexión SSH
        self.destroy_metrics_graph()
        if self.ssh_executor:
            self.ssh_executor.close_connection()
        # Cerrar la interfaz
        self.master.destroy()

    def switch_to_main_interface(self):
        # Ocultar la pestaña de bienvenida y mostrar la interfaz principal
        self.ssh_executor = SSHScriptExecutor(hostname='Host', port=22, username='user', password='password')
        self.ssh_executor.connect()
        self.ssh_executor.transfer_scripts(None)
        # Envía el mensaje directamente a execute_script
        start_time_load_model = time.time()
        metrics = self.ssh_executor.execute_load_model()
        end_time_load_model = time.time()
        elapsed_time_load_model = end_time_load_model - start_time_load_model
        print(f"Tiempo de ejecución de load_state(): {elapsed_time_load_model:.2f} segundos")
        self.show_graph_in_tkinter(metrics)

        self.notebook.hide(self.welcome_tab)
        self.notebook.select(self.pdf_conversation_tab)
        self.notebook.select(self.metrics_tab)
        self.notebook.select(self.normal_conversation_tab)


    def create_main_interface(self):
        self.style = ttk.Style()
        self.style.configure('TNotebook', tabposition='n')
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12))
        self.style.configure('TNotebook.Tab', font=('Helvetica', 12))
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12))

        self.notebook = ttk.Notebook(self.master)
        self.metrics_tab = ttk.Frame(self.notebook)
        self.normal_conversation_tab = ttk.Frame(self.notebook)
        self.pdf_conversation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.normal_conversation_tab, text="Conversación Normal")
        self.notebook.add(self.pdf_conversation_tab, text="Conversación PDF")
        self.notebook.add(self.metrics_tab, text="Métricas")
        self.create_metrics_tab()
        self.create_normal_conversation_tab()
        self.create_pdf_conversation_tab()
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.center_window(self.master, 1000, 600)
        self.master.deiconify()

    def create_metrics_tab(self):

        # Incorporar el gráfico en la interfaz
        self.canvas_metrics = FigureCanvasTkAgg(master=self.metrics_tab)
        self.canvas_metrics_widget = self.canvas_metrics.get_tk_widget()
        self.canvas_metrics_widget.grid(row=1, column=0, pady=10, padx=100, sticky="nsew")


        back_button_metrics = ttk.Button(self.metrics_tab, text="Atrás", command=self.go_back_to_welcome)
        back_button_metrics.grid(row=3, column=0, pady=10, padx=10, sticky='w')

        for i in range(2):
            self.metrics_tab.grid_columnconfigure(i, weight=1)
        self.metrics_tab.grid_rowconfigure(1, weight=1)
        self.metrics_tab.grid_rowconfigure(2, weight=1)

    def update_gpu_graph(self, gpu_memory_usage):
        data_gpu0 = [dupla[0] for dupla in gpu_memory_usage]
        data_gpu1 = [dupla[1] for dupla in gpu_memory_usage]

        if not self.metrics_graph_created:
            # If the graph hasn't been created, create it
            self.create_metrics_graph()

            # Update the flag to indicate that the graph has been created
            self.metrics_graph_created = True

        # Update the data on the existing graph
        self.ax_metrics.clear()
        self.ax_metrics.plot(data_gpu0, label='GPU 0')
        self.ax_metrics.plot(data_gpu1, label='GPU 1')
        self.ax_metrics.set_xlabel('Tiempo (s)')
        self.ax_metrics.set_ylabel('Uso de Memoria (MiB)')
        self.ax_metrics.set_title('Uso de Memoria de GPU')
        self.ax_metrics.legend()

        # Update the interface
        self.canvas_metrics.draw()

    def update_cpu_graph(self, cpu_usage):
        # Los datos de la CPU son simplemente una lista de valores de uso de la CPU
        data_cpu = cpu_usage

        if not self.metrics_graph_created:
            # Si el gráfico no ha sido creado, créalo
            self.create_metrics_graph()

            # Actualiza el indicador para indicar que el gráfico ha sido creado
            self.metrics_graph_created = True

        # Actualiza los datos en el gráfico existente
        self.ax_metrics.clear()
        self.ax_metrics.plot(data_cpu, label='CPU')
        self.ax_metrics.set_xlabel('Tiempo (s)')
        self.ax_metrics.set_ylabel('Uso de CPU (%)')
        self.ax_metrics.set_title('Uso de CPU')
        self.ax_metrics.legend()

        # Actualiza la interfaz
        self.canvas_metrics.draw()

    def create_metrics_graph(self):
        # Create the initial graph
        figure_metrics, self.ax_metrics = plt.subplots(figsize=(8, 4))
        self.canvas_metrics = FigureCanvasTkAgg(figure_metrics, master=self.metrics_tab)
        self.canvas_metrics.get_tk_widget().grid(row=1, column=0, pady=10, padx=10, sticky="nsew")

        # Other elements (you can add more as needed)
        self.datos_tecnicos_text = ttk.Label(self.metrics_tab, text="Datos técnicos:")
        self.datos_tecnicos_text.grid(row=2, column=0, pady=10, padx=10, sticky='w')

        back_button_metrics = ttk.Button(self.metrics_tab, text="Atrás", command=self.go_back_to_welcome)
        back_button_metrics.grid(row=3, column=0, pady=10, padx=10, sticky='w')

        # Configuration for expansion
        self.metrics_tab.grid_columnconfigure(0, weight=1)
        self.metrics_tab.grid_rowconfigure(1, weight=1)

    def show_graph_in_tkinter(self,metrics):
        if self.welcome_tab.device_var.get() == 'gpu':
            # Llama a este método desde donde quieras mostrar el gráfico
            self.update_gpu_graph(metrics)
        else:
            self.update_cpu_graph(metrics)

        for i in range(2):
            self.metrics_tab.grid_columnconfigure(i, weight=1)
        self.metrics_tab.grid_rowconfigure(1, weight=1)
        self.metrics_tab.grid_rowconfigure(2, weight=1)

    def destroy_metrics_graph(self):
        if hasattr(self, 'canvas_metrics') and self.metrics_graph_created :
            self.canvas_metrics.get_tk_widget().destroy()
            plt.close(self.ax_metrics.figure)
            delattr(self, 'canvas_metrics')
            delattr(self, 'ax_metrics')
            self.metrics_graph_created = False

    def create_normal_conversation_tab(self):
        ttk.Label(self.normal_conversation_tab, text="Ingresa tu pregunta:").grid(row=0, column=0, pady=10, padx=10, sticky='w')
        self.normal_user_question_entry = ttk.Entry(self.normal_conversation_tab, width=70)
        self.normal_user_question_entry.grid(row=0, column=1, pady=10, padx=10)
        self.normal_submit_user_button = ttk.Button(self.normal_conversation_tab, text="Enviar Pregunta", command=self.normal_submit_user_question)
        self.normal_submit_user_button.grid(row=0, column=3, pady=10, padx=10)
        self.normal_download_button = ttk.Button(self.normal_conversation_tab, text="Descargar Conversación", command=self.download_conversation)
        self.normal_download_button.grid(row=1, column=0, columnspan=4, pady=10, padx=10, sticky='nsew')
        self.normal_conversation_text_user = scrolledtext.ScrolledText(self.normal_conversation_tab, width=100, height=20, wrap=tk.WORD)
        self.normal_conversation_text_user.grid(row=2, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")
        # En el método create_normal_conversation_tab:
        back_button_normal = ttk.Button(self.normal_conversation_tab, text="Atrás", command=self.go_back_to_welcome)
        back_button_normal.grid(row=3, column=0, pady=10, padx=10, sticky='w')

        self.configure_text_widget(self.normal_conversation_text_user)

        # Configuración de expansión para la pestaña de conversación normal
        for i in range(4):  # Número de columnas en la pestaña
            self.normal_conversation_tab.grid_columnconfigure(i, weight=1)
        self.normal_conversation_tab.grid_rowconfigure(2, weight=1)


    def create_pdf_conversation_tab(self):
        ttk.Label(self.pdf_conversation_tab, text="Seleccionar PDF:").grid(row=0, column=0, pady=10, padx=10, sticky='w')
        ttk.Label(self.pdf_conversation_tab, text="Ingresa tu pregunta:").grid(row=1, column=0, pady=10, padx=10, sticky='w')
        self.pdf_select_pdf_button = ttk.Button(self.pdf_conversation_tab, text="Seleccionar PDF", command=self.pdf_select_pdf)
        self.pdf_select_pdf_button.grid(row=0, column=1, pady=10, padx=10)
        self.pdf_user_question_entry = ttk.Entry(self.pdf_conversation_tab, width=70)
        self.pdf_user_question_entry.grid(row=1, column=1, pady=10, padx=100)
        self.pdf_submit_user_button = ttk.Button(self.pdf_conversation_tab, text="Enviar Pregunta", command=self.pdf_submit_user_question)
        self.pdf_submit_user_button.grid(row=1, column=3, pady=10, padx=10)
        self.pdf_submit_user_button['state'] = 'disabled'
        self.pdf_download_button = ttk.Button(self.pdf_conversation_tab, text="Descargar Conversación", command=self.download_conversation)
        self.pdf_download_button.grid(row=2, column=0, columnspan=4, pady=10, padx=10, sticky='nsew')
        self.pdf_conversation_text_user = scrolledtext.ScrolledText(self.pdf_conversation_tab, width=100, height=20, wrap=tk.WORD)
        self.pdf_conversation_text_user.grid(row=3, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")
        # En el método create_pdf_conversation_tab:
        back_button_pdf = ttk.Button(self.pdf_conversation_tab, text="Atrás", command=self.go_back_to_welcome)
        back_button_pdf.grid(row=4, column=0, pady=10, padx=10, sticky='w')
        self.configure_text_widget(self.pdf_conversation_text_user)

        # Configuración de expansión para la pestaña de conversación PDF
        for i in range(4):  # Número de columnas en la pestaña
            self.pdf_conversation_tab.grid_columnconfigure(i, weight=1)
        self.pdf_conversation_tab.grid_rowconfigure(3, weight=1)

    def normal_submit_user_question(self):
        user_question = self.normal_user_question_entry.get()
        self.normal_user_question_entry.delete(0, tk.END)
        self.execute_user_scripts(user_question, conversation_type="normal")

    def pdf_submit_user_question(self):
        user_question = self.pdf_user_question_entry.get()
        self.pdf_user_question_entry.delete(0, tk.END)
        self.execute_user_scripts(user_question, conversation_type="pdf")
    

    def execute_user_scripts(self, user_question, conversation_type):
        # Iniciar conexión SSH según el tipo de conversación
        if conversation_type == "normal":
            is_pdf = False
        elif conversation_type == "pdf":
            is_pdf = True

        # Envía el mensaje directamente a execute_script
        start_time_load_model = time.time()
        response_script, metrics= self.ssh_executor.execute_script(user_question,is_pdf)
        self.master.after(0, self.update_conversation, user_question, response_script, 'user', conversation_type)
        end_time_load_model = time.time()
        elapsed_time_load_model = end_time_load_model - start_time_load_model
        print(f"Tiempo de ejecución: {elapsed_time_load_model:.2f} segundos")
        self.show_graph_in_tkinter(metrics)



    def pdf_select_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        self.ssh_executor.transfer_scripts(self.pdf_path)
        if self.pdf_path:
            self.load_pdf_context(self.pdf_path, conversation_type="pdf")
            self.pdf_submit_user_button['state'] = 'normal'
        

    def load_pdf_context(self, pdf_path, conversation_type):
        try:
            doc = fitz.open(pdf_path)
            pdf_text = ""
            for page_num in range(doc.page_count):
                page = doc[page_num]
                blocks = page.get_text("blocks")
                for block in blocks:
                    pdf_text += block[4] + ' '
            self.pdf_context = pdf_text
            if conversation_type == "pdf":
                self.pdf_conversation_text_user.insert(tk.END, "Contenido del PDF:\n")
                self.pdf_conversation_text_user.insert(tk.END, pdf_text + '\n\n')
        except FileNotFoundError:
            self.pdf_context = ""

    
    def go_back_to_welcome(self):
        self.notebook.hide(self.metrics_tab)
        self.notebook.hide(self.normal_conversation_tab)
        self.notebook.hide(self.pdf_conversation_tab)
        # Cambiar a la pestaña de bienvenida
        self.notebook.select(self.welcome_tab)
        # Desconectar la sesión SSH si está conectada
        if self.ssh_executor:
            self.ssh_executor.close_connection()

    def download_conversation(self):
        if self.conversation_type.get() == "normal":
            conversation_text = self.normal_conversation_text_user.get("1.0", tk.END)
        elif self.conversation_type.get() == "pdf":
            conversation_text = self.pdf_conversation_text_user.get("1.0", tk.END)

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])

        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(conversation_text)
            messagebox.showinfo("Guardado", "Conversación guardada con éxito.")
            
    def update_conversation(self, user_question, response_from_second_script, mode, conversation_type):
        if mode == 'user':
            if conversation_type == "normal":
                conversation_text = f"Usuario (Normal): {user_question}\nSistema: {response_from_second_script}\n\n"
                self.normal_conversation_text_user.insert(tk.END, conversation_text)
            elif conversation_type == "pdf":
                conversation_text = f"Usuario (PDF): {user_question}\nSistema: {response_from_second_script}\n\n"
                self.pdf_conversation_text_user.insert(tk.END, conversation_text)

    def configure_text_widget(self, text_widget):
        text_widget.configure(font=('Helvetica', 12))

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")

# Función principal
def main():
    root = ThemedTk(theme="plastik")
    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
