import os
import threading
import ctypes
import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage

# DPI AWARENESS PARA WINDOWS
if os.name == 'nt':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# Constantes
EXTENSIONES_TEXTO = ['.txt', '.py', '.html', '.java', '.md', '.css']
CARPETAS_EXCLUIDAS = ['__pycache__', 'venv', '.venv', 'migrations', '.git', '.venv']
CARPETA_DESTINO = r"C:\Users\renzi\Documents\PROYECTO INTEGRADOR I\Lecturas"

class LectorcitoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lectorcito Pro")
        self.geometry("600x400")
        self.resizable(False, False)
        self.archivo_generado = None

        # Verifica y crea la carpeta Lecturas si no existe (solo una vez al iniciar)
        if not os.path.exists(CARPETA_DESTINO):
            try:
                os.makedirs(CARPETA_DESTINO)
            except Exception as e:
                print(f"Error al crear la carpeta Lecturas: {e}")

        # Icono del ejecutable + posible icono de ventana
        if os.path.exists("lector.ico"):
            try:
                self.iconbitmap("lector.ico")
            except Exception as e:
                print(f"Error al cargar iconbitmap: {e}")
        if os.path.exists("lector.png"):
            try:
                icon = PhotoImage(file="lector.png")
                self.tk.call("wm", "iconphoto", self._w, icon)
            except Exception as e:
                print(f"Error al asignar iconphoto: {e}")

        self.create_widgets()

    def create_widgets(self):
        # Etiqueta de título
        self.label_title = ctk.CTkLabel(
            self, 
            text="Seleccione una carpeta para analizar:", 
            font=("Segoe UI", 16)
        )
        self.label_title.pack(pady=(20, 10))

        # Botón para elegir carpeta
        self.btn_select = ctk.CTkButton(
            self, 
            text="Elegir carpeta", 
            command=self.seleccionar_carpeta, 
            width=200
        )
        self.btn_select.pack(pady=10)

        # Barra de progreso (inicialmente oculta)
        self.progress = ctk.CTkProgressBar(self, width=300, mode="indeterminate")
        self.progress.set(0)
        self.progress.pack(pady=10)
        self.progress.stop()
        self.progress.pack_forget()

        # Botón para abrir el archivo generado
        self.btn_abrir = ctk.CTkButton(
            self, 
            text="Abrir archivo generado", 
            command=self.abrir_archivo
        )
        self.btn_abrir.pack(pady=10)
        self.btn_abrir.configure(state="disabled")

        # Botón para abrir la carpeta Lecturas
        self.btn_open_folder = ctk.CTkButton(
            self, 
            text="Abrir carpeta Lecturas", 
            command=self.abrir_carpeta_lecturas
        )
        self.btn_open_folder.pack(pady=10)

        # Etiqueta de información y créditos
        self.label_info = ctk.CTkLabel(
            self,
            text="Lectorcito Pro v1.5\nDesarrollado por: Renzo Fernando Mosquera Daza, ChatGPT-o3-mini-high y ChatGPT-4o\n2025",
            font=("Segoe UI", 10)
        )
        self.label_info.pack(side="bottom", pady=(5, 10))

        # Etiqueta para resultados/mensajes
        self.label_result = ctk.CTkLabel(self, text="", wraplength=500, justify="center")
        self.label_result.pack(pady=10)

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(title="Seleccione la carpeta a analizar")
        if carpeta:
            self.progress.pack()
            self.progress.start()
            threading.Thread(target=self.procesar, args=(carpeta,), daemon=True).start()

    def procesar(self, carpeta):
        try:
            archivo = self.guardar_contenido_completo(carpeta)
            self.archivo_generado = archivo
            self.after(0, lambda: self.label_result.configure(
                text=f"El contenido fue guardado en:\n{archivo}"
            ))
            self.after(0, lambda: self.btn_abrir.configure(state="normal"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Ocurrió un error:\n{e}"))
        finally:
            self.after(0, self.progress.stop)
            self.after(0, self.progress.pack_forget)

    def abrir_archivo(self):
        if self.archivo_generado:
            try:
                os.startfile(self.archivo_generado)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
        else:
            messagebox.showwarning("Atención", "No se ha generado ningún archivo.")

    def abrir_carpeta_lecturas(self):
        try:
            os.startfile(CARPETA_DESTINO)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{e}")

    def guardar_contenido_completo(self, carpeta):
        nombre_carpeta = os.path.basename(carpeta.rstrip("\\/"))
        version = 1

        while True:
            nombre_archivo = f"{nombre_carpeta}_v{version}.txt"
            ruta_salida = os.path.join(CARPETA_DESTINO, nombre_archivo)
            if not os.path.exists(ruta_salida):
                break
            version += 1

        with open(ruta_salida, "w", encoding="utf-8") as salida:
            salida.write(f"REPORTE DE ARCHIVOS EN: {carpeta}\n\n")
            self.recorrer_carpeta(carpeta, salida, carpeta)
        return ruta_salida

    def recorrer_carpeta(self, folder, salida, raiz, nivel=0):
        indent = " " * nivel
        rel_folder = os.path.relpath(folder, raiz)
        salida.write(f"{indent}Carpeta: {rel_folder}\n")
        try:
            items = sorted(os.listdir(folder))
        except Exception as e:
            salida.write(f"{indent}Error al listar {folder}: {e}\n")
            return

        for item in items:
            ruta_item = os.path.join(folder, item)
            if os.path.isdir(ruta_item):
                self.recorrer_carpeta(ruta_item, salida, raiz, nivel + 1)
            elif os.path.isfile(ruta_item):
                ext = os.path.splitext(item)[1].lower()
                if ext in EXTENSIONES_TEXTO:
                    try:
                        rel_path = os.path.relpath(ruta_item, raiz)
                        salida.write(f"{indent}    Archivo: {rel_path} ({ext})\n")
                        salida.write(f"{indent}    -------- CONTENIDO --------\n")
                        with open(ruta_item, "r", encoding="utf-8") as f:
                            contenido = f.read()
                        # ❌ SIN LÍMITE DE LÍNEAS:
                        for linea in contenido.splitlines():
                            salida.write(f"{indent}    {linea}\n")
                        salida.write(f"{indent}    -------- FIN --------\n\n")
                    except Exception as e:
                        salida.write(f"{indent}    Error leyendo {item}: {e}\n\n")

if __name__ == "__main__":
    # Modo claro siempre.
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    app = LectorcitoApp()
    app.mainloop()
