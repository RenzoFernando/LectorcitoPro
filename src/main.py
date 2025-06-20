import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from controller.controller import LectorcitoController

def main():
    try:
        app = LectorcitoController()
        app.run()
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error Crítico", f"No se pudo iniciar la aplicación:\n\n{e}")
        root.destroy()

if __name__ == "__main__":
    main()
