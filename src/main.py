import sys
import os

# Añade el directorio actual al path para permitir importaciones relativas.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from controller.controller import LectorcitoController

# Punto de entrada principal de la aplicación.
def main():
    try:
        # Crea una instancia del controlador y ejecuta la aplicación.
        app = LectorcitoController()
        app.run()
    except Exception as e:
        # Captura de errores críticos durante el arranque y los muestra en un popup.
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error Crítico", f"No se pudo iniciar la aplicación:\n\n{e}")
        root.destroy()

# Asegura que main() se ejecute solo cuando el script es el programa principal.
if __name__ == "__main__":
    main()