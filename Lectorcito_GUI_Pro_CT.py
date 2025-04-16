import os
import sys
import shutil
import threading
import ctypes
import webbrowser
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

# --------------------------------------------------------------------------------
#                          FUNCIÓN PARA CARGAR RECURSOS
# --------------------------------------------------------------------------------
def get_resource_path(relative_path):
    """
    Devuelve la ruta absoluta del recurso, tanto si se está ejecutando
    como script normal como si se ha empaquetado con PyInstaller.
    """
    try:
        # Si se ha empaquetado con PyInstaller, _MEIPASS es donde están los recursos
        base_path = sys._MEIPASS
    except Exception:
        # Caso normal: ruta al directorio actual del script
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# DPI AWARENESS PARA WINDOWS
if os.name == 'nt':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# --------- COLORES Y VARIABLES GLOBALES ---------
COLOR_FONDO_CLARO = "#EBEBEB"
COLOR_FONDO_OSCURO = "#1A1E22"
COLOR_TEXTO_CLARO  = "#000000"
COLOR_TEXTO_OSCURO = "#FFFFFF"

COLOR_BOTON_AZUL   = "#3B8ED0"

COLOR_BOTON_VERDE  = "#3BD056"
COLOR_BOTON_VERDE_DARK = "#2FA047"   # verde más oscuro al pasar el mouse
COLOR_BOTON_ROJO   = "#D03B3D"
COLOR_BOTON_ROJO_DARK  = "#A03031"   # rojo más oscuro al pasar el mouse

EXTENSIONES_TEXTO  = ['.txt', '.py', '.html', '.java', '.md', '.css']
CARPETAS_EXCLUIDAS = ['__pycache__', 'venv', '.venv', 'migrations', '.git']


class LectorcitoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lectorcito Pro")
        self.resizable(False, False)
        self.geometry("625x425")

        # -------------- Variables de ruta --------------
        self.folder_to_read = None       # Carpeta que se va a leer
        self.lecturas_path = None       # Ruta donde se creará la carpeta Lecturas
        self.archivo_generado = None    # Último archivo generado
        self.current_mode = "light"     # Modo inicial (light/dark)

        # -------------- Cargar íconos --------------
        icon_path_ico = get_resource_path("recursos/lector.ico")
        icon_path_png = get_resource_path("recursos/lector.png")

        if os.path.exists(icon_path_ico):
            try:
                self.iconbitmap(icon_path_ico)
            except Exception:
                pass

        # Íconos para modo (sol y luna)
        sun_png  = get_resource_path("recursos/sol.png")
        moon_png = get_resource_path("recursos/luna.png")

        self.img_sun  = None
        self.img_moon = None

        if os.path.exists(sun_png) and os.path.exists(moon_png):
            try:
                self.img_sun = ctk.CTkImage(
                    light_image=Image.open(sun_png),
                    dark_image=Image.open(sun_png),
                    size=(28, 28)
                )
                self.img_moon = ctk.CTkImage(
                    light_image=Image.open(moon_png),
                    dark_image=Image.open(moon_png),
                    size=(28, 28)
                )
            except Exception as e:
                print(f"Error cargando imágenes sol/luna: {e}")

        # -------------- Configurar y crear widgets --------------
        self.configure_gui()
        self.create_widgets()
        self.apply_theme(self.current_mode)


    # --------------------------------------------------------------------
    # ------------------------ CONFIGURAR VENTANA -------------------------
    # --------------------------------------------------------------------
    def configure_gui(self):
        """Configura el modo de apariencia inicial (light)."""
        ctk.set_appearance_mode("light")  # Por defecto
        ctk.set_default_color_theme("blue")


    # --------------------------------------------------------------------
    # ------------------------- CREAR WIDGETS ----------------------------
    # --------------------------------------------------------------------
    def create_widgets(self):
        # Frame superior (header) para título y botón de cambiar modo
        self.frame_top = ctk.CTkFrame(self, corner_radius=0)
        self.frame_top.pack(side="top", fill="x", pady=5)

        self.label_title = ctk.CTkLabel(
            self.frame_top,
            text="Lectorcito Pro",
            font=("Segoe UI", 18, "bold")
        )
        self.label_title.pack(side="left", padx=10)

        # Botón modo (sol/luna) en la esquina superior derecha
        self.btn_mode_toggle = ctk.CTkButton(
            self.frame_top,
            text="",
            width=40,
            fg_color="#3B8ED0",  # valor inicial; será reasignado en apply_theme
            hover_color="#3B8ED0",
            command=self.toggle_mode
        )
        # Imagen inicial (icono de luna si empezamos en modo claro)
        if self.img_moon:
            self.btn_mode_toggle.configure(image=self.img_moon)
        self.btn_mode_toggle.pack(side="right", padx=10)

        # Etiqueta de bienvenida
        self.label_welcome = ctk.CTkLabel(
            self,
            text="Bienvenid@, por favor seleccione una opción a realizar",
            font=("Segoe UI", 14, "bold")
        )
        self.label_welcome.pack(pady=(10, 10))

        # ------------------- Botones principales -------------------
        self.btn_seleccionar_lecturas = ctk.CTkButton(
            self,
            text="Seleccionar Ruta de Lecturas",
            width=220,
            command=self.seleccionar_ruta_lecturas
        )
        self.btn_seleccionar_lecturas.pack(pady=5)

        self.btn_elegir_carpeta = ctk.CTkButton(
            self,
            text="Elegir Carpeta a Leer",
            width=220,
            command=self.seleccionar_carpeta_leer
        )
        self.btn_elegir_carpeta.pack(pady=5)

        self.btn_abrir_lecturas = ctk.CTkButton(
            self,
            text="Abrir archivo Lecturas",
            width=220,
            command=self.abrir_carpeta_lecturas
        )
        self.btn_abrir_lecturas.pack(pady=5)

        self.btn_abrir_ultimo_archivo = ctk.CTkButton(
            self,
            text="Abrir último archivo generado",
            width=220,
            fg_color=COLOR_BOTON_VERDE,
            hover_color=COLOR_BOTON_VERDE_DARK,
            text_color="#FFFFFF",
            command=self.abrir_archivo_generado
        )
        self.btn_abrir_ultimo_archivo.pack(pady=5)

        self.btn_eliminar_lecturas = ctk.CTkButton(
            self,
            text="Eliminar todas las Lecturas",
            width=220,
            fg_color=COLOR_BOTON_ROJO,
            hover_color=COLOR_BOTON_ROJO_DARK,
            text_color="#FFFFFF",
            command=self.eliminar_todas_lecturas
        )
        self.btn_eliminar_lecturas.pack(pady=5)

        # ----------------- Barra de progreso y % -----------------
        self.frame_progress = ctk.CTkFrame(self, corner_radius=0)
        self.frame_progress.pack(pady=(15, 0))

        self.progress_bar = ctk.CTkProgressBar(self.frame_progress, width=300)
        self.progress_bar.grid(row=0, column=0, padx=5)
        self.progress_bar.set(0)

        self.label_progress_percent = ctk.CTkLabel(
            self.frame_progress,
            text="0%"
        )
        self.label_progress_percent.grid(row=0, column=1, padx=5)

        # ----------------- Créditos y link -----------------
        self.frame_footer = ctk.CTkFrame(self, corner_radius=0)
        self.frame_footer.pack(side="bottom", fill="x", pady=0)

        font_footer_bold    = ("Segoe UI", 10, "bold")
        font_footer_regular = ("Segoe UI", 10)

        self.label_footer_1 = ctk.CTkLabel(
            self.frame_footer,
            text="Lectorcito Pro v2.3",
            font=font_footer_bold
        )
        self.label_footer_1.pack(anchor="center", pady=0)

        self.label_footer_2 = ctk.CTkLabel(
            self.frame_footer,
            text="Desarrollado por: Renzo Fernando Mosquera Daza y ChatGPT Plus",
            font=font_footer_regular
        )
        self.label_footer_2.pack(anchor="center", pady=0)

        self.label_footer_link = ctk.CTkLabel(
            self.frame_footer,
            text="https://github.com/RenzoFernando/LectorcitoPro.git",
            font=("Segoe UI", 10, "underline"),
            cursor="hand2"
        )
        self.label_footer_link.bind("<Button-1>", self.open_github_link)
        self.label_footer_link.pack(anchor="center", pady=0)

        self.label_footer_3 = ctk.CTkLabel(
            self.frame_footer,
            text="© 2025 github.com/RenzoFernando - All Rights Reserved.",
            font=font_footer_regular
        )
        self.label_footer_3.pack(anchor="center", pady=0)


    # --------------------------------------------------------------------
    # --------------------- APLICAR TEMA (MODO) --------------------------
    # --------------------------------------------------------------------
    def apply_theme(self, mode):
        """
        Ajusta colores de fondo, texto, botones, etc. de forma manual
        para simular los estilos solicitados (modo claro/oscuro).
        """
        if mode == "light":
            bg_color = COLOR_FONDO_CLARO
            text_color = COLOR_TEXTO_CLARO
            # Botón de modo oscuro => color #1A1E22, ícono = luna
            self.btn_mode_toggle.configure(fg_color="#1A1E22", hover_color="#1A1E22")
            if self.img_moon:
                self.btn_mode_toggle.configure(image=self.img_moon)
        else:
            bg_color = COLOR_FONDO_OSCURO
            text_color = COLOR_TEXTO_OSCURO
            # Botón de modo claro => color #EBEBEB, ícono = sol
            self.btn_mode_toggle.configure(fg_color="#EBEBEB", hover_color="#EBEBEB")
            if self.img_sun:
                self.btn_mode_toggle.configure(image=self.img_sun)

        # Fondo principal
        self.configure(fg_color=bg_color)
        self.frame_top.configure(fg_color=bg_color)
        self.frame_footer.configure(fg_color=bg_color)
        self.frame_progress.configure(fg_color=bg_color)

        # Texto (títulos, labels)
        self.label_title.configure(text_color=text_color)
        self.label_welcome.configure(text_color=text_color)

        self.label_footer_1.configure(text_color=text_color)
        self.label_footer_2.configure(text_color=text_color)
        self.label_footer_link.configure(text_color=text_color)
        self.label_footer_3.configure(text_color=text_color)

        self.label_progress_percent.configure(text_color=text_color)

        # Botones principales
        self.btn_elegir_carpeta.configure(fg_color=COLOR_BOTON_AZUL,
                                          text_color="#FFFFFF")
        self.btn_seleccionar_lecturas.configure(fg_color=COLOR_BOTON_AZUL,
                                                text_color="#FFFFFF")
        self.btn_abrir_lecturas.configure(fg_color=COLOR_BOTON_AZUL,
                                          text_color="#FFFFFF")
        self.btn_abrir_ultimo_archivo.configure(fg_color=COLOR_BOTON_VERDE,
                                                text_color="#FFFFFF")
        self.btn_eliminar_lecturas.configure(fg_color=COLOR_BOTON_ROJO,
                                             text_color="#FFFFFF")

        # Ajustar barra de progreso
        self.progress_bar.configure(
            progress_color=COLOR_BOTON_AZUL,  # color de la barra
            fg_color="#CCCCCC" if mode == "light" else "#333333"  # color del fondo de la barra
        )


    # --------------------------------------------------------------------
    # ------------------- TOGGLE MODO CLARO/OSCURO -----------------------
    # --------------------------------------------------------------------
    def toggle_mode(self):
        """Alterna entre modo claro y oscuro, aplicando los estilos."""
        if self.current_mode == "light":
            self.current_mode = "dark"
            ctk.set_appearance_mode("dark")
        else:
            self.current_mode = "light"
            ctk.set_appearance_mode("light")
        self.apply_theme(self.current_mode)


    # --------------------------------------------------------------------
    # ------------------- MANEJO DE CARPETAS Y ARCHIVOS ------------------
    # --------------------------------------------------------------------
    def seleccionar_ruta_lecturas(self):
        """Selecciona la ruta donde se creará (o existe) la carpeta 'Lecturas'."""
        ruta = filedialog.askdirectory(title="Seleccione la ruta donde se creará la carpeta Lecturas")
        if ruta:
            self.lecturas_path = os.path.join(ruta, "Lecturas")
            # Crea la carpeta si no existe
            if not os.path.exists(self.lecturas_path):
                try:
                    os.makedirs(self.lecturas_path)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo crear la carpeta Lecturas:\n{e}")

    def seleccionar_carpeta_leer(self):
        """Selecciona la carpeta a leer y, si ya se ha establecido la ruta de Lecturas, inicia el procesamiento."""
        carpeta = filedialog.askdirectory(title="Seleccione la carpeta a analizar")
        if carpeta:
            self.folder_to_read = carpeta
            if self.lecturas_path:
                self.start_processing()
            else:
                messagebox.showwarning("Atención", "Primero debe seleccionar la ruta de Lecturas.")

    def eliminar_todas_lecturas(self):
        """Elimina la carpeta Lecturas con todo su contenido."""
        if not self.lecturas_path or not os.path.exists(self.lecturas_path):
            messagebox.showinfo("Atención", "No hay carpeta Lecturas para eliminar.")
            return

        resp = messagebox.askyesno("Confirmación", "¿Está seguro de eliminar la carpeta Lecturas y todo su contenido?")
        if resp:
            try:
                shutil.rmtree(self.lecturas_path)
                messagebox.showinfo("¡Listo!", "Se han eliminado todas las lecturas correctamente.")
            except Exception as e:
                messagebox.showerror("❗ Error", f"No se pudo eliminar la carpeta:\n{e}")

    def abrir_carpeta_lecturas(self):
        """Abre la carpeta Lecturas en el explorador de archivos."""
        if not self.lecturas_path or not os.path.exists(self.lecturas_path):
            messagebox.showwarning("Atención", "No existe carpeta 'Lecturas' aún.")
            return
        try:
            os.startfile(self.lecturas_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta Lecturas:\n{e}")

    def abrir_archivo_generado(self):
        """Abre el último archivo generado en la carpeta Lecturas."""
        if not self.archivo_generado or not os.path.exists(self.archivo_generado):
            messagebox.showwarning("Atención", "Primero debe generar un archivo para poder abrirlo.")
            return
        try:
            os.startfile(self.archivo_generado)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")


    # --------------------------------------------------------------------
    # ----------------------- PROCESAR LECTURAS --------------------------
    # --------------------------------------------------------------------
    def start_processing(self):
        """Inicia el proceso de lectura de la carpeta seleccionada y guarda el contenido en la carpeta Lecturas."""
        if not self.folder_to_read:
            messagebox.showwarning("Atención", "Primero seleccione la carpeta a leer.")
            return
        if not self.lecturas_path:
            messagebox.showwarning("Atención", "Primero seleccione la ruta de Lecturas.")
            return

        threading.Thread(target=self.procesar_lecturas, daemon=True).start()

    def procesar_lecturas(self):
        """Procesa la carpeta, leyendo archivos de texto y guardándolos."""
        self.bloquear_interfaz()

        self.progress_bar.set(0)
        self.label_progress_percent.configure(text="0%")

        total_files = self.contar_archivos(self.folder_to_read)
        self.archivo_generado = self.crear_nombre_archivo_salida(self.folder_to_read)

        try:
            actual = 0
            with open(self.archivo_generado, "w", encoding="utf-8") as salida:
                salida.write(f"REPORTE DE ARCHIVOS EN: {self.folder_to_read}\n\n")

                for root, dirs, files in os.walk(self.folder_to_read):
                    # Filtrar carpetas excluidas
                    dirs[:] = [d for d in dirs if d.lower() not in [ex.lower() for ex in CARPETAS_EXCLUIDAS]]

                    rel_folder = os.path.relpath(root, self.folder_to_read)
                    salida.write(f"Carpeta: {rel_folder}\n")
                    for file_ in sorted(files):
                        ext = os.path.splitext(file_)[1].lower()
                        if ext in EXTENSIONES_TEXTO:
                            archivo_path = os.path.join(root, file_)
                            rel_path = os.path.relpath(archivo_path, self.folder_to_read)
                            salida.write(f"    Archivo: {rel_path} ({ext})\n")
                            salida.write("    -------- CONTENIDO --------\n")
                            try:
                                with open(archivo_path, "r", encoding="utf-8") as f:
                                    for linea in f:
                                        salida.write(f"    {linea.rstrip()}\n")
                            except Exception as e:
                                salida.write(f"    Error leyendo {file_}: {e}\n")
                            salida.write("    -------- FIN --------\n\n")

                            actual += 1
                            if total_files > 0:
                                porcentaje = (actual / total_files) * 100
                                self.update_progress(porcentaje)

            messagebox.showinfo("¡Listo!", "El contenido fue guardado correctamente.")

        except Exception:
            messagebox.showerror("Error", "Ocurrió un error durante el análisis. Intente con otra carpeta.")

        self.desbloquear_interfaz()


    def bloquear_interfaz(self):
        """Bloquea botones para evitar múltiples procesos simultáneos."""
        self.btn_elegir_carpeta.configure(state="disabled")
        self.btn_seleccionar_lecturas.configure(state="disabled")
        self.btn_abrir_lecturas.configure(state="disabled")
        self.btn_abrir_ultimo_archivo.configure(state="disabled")
        self.btn_eliminar_lecturas.configure(state="disabled")

    def desbloquear_interfaz(self):
        """Desbloquea botones tras finalizar la lectura."""
        self.btn_elegir_carpeta.configure(state="normal")
        self.btn_seleccionar_lecturas.configure(state="normal")
        self.btn_abrir_lecturas.configure(state="normal")
        self.btn_abrir_ultimo_archivo.configure(state="normal")
        self.btn_eliminar_lecturas.configure(state="normal")

    def update_progress(self, porcentaje):
        """Actualiza la barra de progreso y la etiqueta de porcentaje."""
        self.progress_bar.set(porcentaje / 100.0)
        self.label_progress_percent.configure(text=f"{porcentaje:.0f}%")
        self.update_idletasks()

    def contar_archivos(self, folder):
        """Cuenta la cantidad total de archivos con EXTENSIONES_TEXTO, ignorando CARPETAS_EXCLUIDAS."""
        contador = 0
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d.lower() not in [ex.lower() for ex in CARPETAS_EXCLUIDAS]]
            for file_ in files:
                ext = os.path.splitext(file_)[1].lower()
                if ext in EXTENSIONES_TEXTO:
                    contador += 1
        return contador

    def crear_nombre_archivo_salida(self, carpeta_origen):
        """Genera un nombre único para el archivo de salida dentro de self.lecturas_path."""
        nombre_carpeta = os.path.basename(carpeta_origen.rstrip("\\/"))
        version = 1
        while True:
            nombre_archivo = f"{nombre_carpeta}_v{version}.txt"
            ruta_salida = os.path.join(self.lecturas_path, nombre_archivo)
            if not os.path.exists(ruta_salida):
                return ruta_salida
            version += 1


    # --------------------------------------------------------------------
    # ------------------------- ABRIR LINK GITHUB -------------------------
    # --------------------------------------------------------------------
    def open_github_link(self, event):
        """Abre el repositorio en el navegador."""
        url = "https://github.com/RenzoFernando/LectorcitoPro.git"
        webbrowser.open_new(url)


# ------------------------------------------------------------------------
# ----------------------- EJECUCIÓN PRINCIPAL ----------------------------
# ------------------------------------------------------------------------
if __name__ == "__main__":
    app = LectorcitoApp()
    app.mainloop()
