import os, requests
import tkinter as tk
from tkinter import Listbox, Scrollbar, messagebox, Entry, Text
import keys

# Variables para la autenticación
server_passcode = keys.SERVER_PASSWORD
base_api_url = "http://127.0.0.1:8081/api/" #"http://smmcl.jotalea.com.ar/api/"
session_token = ""

# Obtener la ruta de la carpeta de niveles dependiendo del sistema operativo
if os.name == 'nt':  # Windows
    niveles_dir = os.path.join(os.path.expandvars('%APPDATA%'), 'SMM-CL', 'Niveles')
else:  # Pruebas ejecutando en el servidor
    niveles_dir = os.path.join(os.getcwd(), 'stages')
    print(niveles_dir)

# Verificar si la carpeta de niveles existe
if not os.path.isdir(niveles_dir):
    messagebox.showerror("Error", "La carpeta de niveles no fue encontrada.")
    exit()

# Función para cargar los nombres de archivo en la lista
def cargar_archivos():
    try:
        archivos = os.listdir(niveles_dir)
        for archivo in archivos:
            if os.path.isfile(os.path.join(niveles_dir, archivo)):
                listbox.insert(tk.END, archivo)
    except OSError:
        messagebox.showerror("Error", "Error al cargar los archivos.")

# Función para manejar la selección de un archivo
def seleccionar_archivo():
    if listbox.curselection():
        archivo_seleccionado = listbox.get(listbox.curselection())
        abrir_ventana_nivel(archivo_seleccionado)
    else:
        messagebox.showwarning("Advertencia", "Por favor selecciona un archivo.")

# Función para abrir una nueva ventana para el nivel seleccionado
def abrir_ventana_nivel(archivo):
    nivel_titulo = tk.StringVar()
    nivel_descripcion = tk.StringVar()

    def publicar_nivel():
        titulo = nivel_titulo.get()
        descripcion = nivel_descripcion.get()
        if titulo.strip() == "" or descripcion.strip() == "":
            messagebox.showwarning("Advertencia", "Por favor completa todos los campos.")
            return

        # Datos para la publicación del nivel
        auth = server_passcode
        stage_username = "StageUsername"  # Puedes cambiar esto según tus necesidades
        stage_content = "StageContentData"  # Puedes cambiar esto según tus necesidades

        # Realizar la solicitud HTTP POST para publicar el nivel
        try:
            print(session_token)
            response = requests.post(base_api_url + "stage/upload", headers={'Content-Type': 'application/json'},
                                     json={"auth": auth, "session": session_token, "username": stage_username,
                                           "title": titulo, "description": descripcion, "content": stage_content})
            data = response.json()
            if 'message' in data and data['message'].strip():
                messagebox.showinfo("Mensaje del Servidor", data['message'])
            elif response.status_code == 200:
                messagebox.showinfo("Éxito", "¡Nivel publicado correctamente!")
            else:
                messagebox.showerror("Error", "No se pudo publicar el nivel. Inténtalo de nuevo.")
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "No se pudo conectar al servidor.")

    # Crear una nueva ventana
    nivel_window = tk.Toplevel(root)
    nivel_window.title("Detalles del Nivel")

    # Entradas y etiquetas para título y descripción del nivel
    tk.Label(nivel_window, text="Título del Nivel:").pack(pady=5)
    tk.Entry(nivel_window, textvariable=nivel_titulo).pack(pady=5)

    tk.Label(nivel_window, text="Descripción del Nivel:").pack(pady=5)
    tk.Entry(nivel_window, textvariable=nivel_descripcion).pack(pady=5)

    # Botón para publicar el nivel
    tk.Button(nivel_window, text="Publicar", command=publicar_nivel).pack(pady=10)


# Función para abrir una nueva ventana para iniciar sesión
def abrir_ventana_sesion():
    global session_token

    usuario_text_box = tk.StringVar()
    contraseña_text_box = tk.StringVar()

    def iniciar_sesion():
        global session_token
        usuario = usuario_text_box.get()
        contraseña = contraseña_text_box.get()
        if usuario.strip() == "" or contraseña.strip() == "":
            messagebox.showwarning("Advertencia", "Por favor completa todos los campos.")
            return

        # Realizar la solicitud HTTP POST para iniciar sesión
        try:
            response = requests.post(
                base_api_url + "account/login",
                headers = {'Content-Type': 'application/json'},
                json = {"auth": server_passcode, "username": usuario, "password": contraseña}
            )

            data = response.json()
            if 'message' in data and data['message'].strip():
                messagebox.showinfo("Mensaje del Servidor", data['message'])
                print(session_token)
                session_token = data['token']
                print(session_token)
                session_window.destroy()
            else:
                messagebox.showerror("Error", "No se pudo iniciar sesión. Intentalo de nuevo.")
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "No se pudo conectar al servidor.")

    # Crear una nueva ventana
    session_window = tk.Toplevel(root)
    session_window.title("Iniciar sesión")

    tk.Label(session_window, text="Usuario:").pack(pady=5)
    tk.Entry(session_window, textvariable=usuario_text_box).pack(pady=5)

    tk.Label(session_window, text="Contraseña:").pack(pady=5)
    tk.Entry(session_window, textvariable=contraseña_text_box).pack(pady=5)

    # Botón para iniciar sesión
    tk.Button(session_window, text="Enviar", command=iniciar_sesion).pack(pady=10)

# Crear la ventana principal
root = tk.Tk()
root.title("Guardabot")
root.geometry("640x360")
root.minsize(640, 360)

# Crear un marco y una lista desplegable para los archivos
frame = tk.Frame(root)
frame.place(x=0, y=0, width=640, height=280)

scrollbar = Scrollbar(frame, orient=tk.VERTICAL)
scrollbar.place(x=620, y=10, width=10, height=270)

listbox = Listbox(frame, width=50, yscrollcommand=scrollbar.set)
listbox.place(x=10, y=10, width=600, height=280)

scrollbar.config(command=listbox.yview)

# Botón para cargar archivos
cargar_archivos_button = tk.Button(root, text="Actualizar", command=cargar_archivos)
cargar_archivos_button.place(x=10, y=290, width=120, height=30)

# Botón para cargar archivos
iniciar_sesion_button = tk.Button(root, text="Iniciar sesión", command=abrir_ventana_sesion)
iniciar_sesion_button.place(x=140, y=290, width=120, height=30)

# Botón para seleccionar archivo
seleccionar_button = tk.Button(root, text="Publicar nivel", command=seleccionar_archivo)
seleccionar_button.place(x=270, y=290, width=120, height=30)

# Función para autenticar al usuario antes de iniciar la aplicación
abrir_ventana_sesion()

# Ejecutar el bucle principal de la ventana
root.mainloop()