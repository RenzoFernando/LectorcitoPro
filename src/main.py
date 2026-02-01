import sys
import os
import traceback

# Añade el directorio actual al path para permitir importaciones relativas.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from controller.controller import LectorcitoController
import utils  # Importamos utils para el logging


# Punto de entrada principal de la aplicación.
def main():
    # 1. Configurar el sistema de logs antes de nada
    utils.setup_logging()

    try:
        # Crea una instancia del controlador y ejecuta la aplicación.
        app = LectorcitoController()
        app.run()

    except KeyboardInterrupt:
        # NUEVO: Captura la interrupción manual (Stop en IDE o Ctrl+C)
        # Esto evita que salga el Traceback rojo en la consola.
        print("\nAplicación detenida por el usuario.")
        sys.exit(0)

    except Exception as e:
        # Captura de errores críticos durante el arranque y los muestra en un popup.
        # Además, los guarda en el archivo de registro.
        utils.log_error("Error Crítico al iniciar la aplicación", e)

        import tkinter as tk
        from tkinter import messagebox

        log_file = utils.get_log_path()
        error_msg = f"No se pudo iniciar la aplicación debido a un error crítico:\n\n{e}\n\nDetalles guardados en:\n{log_file}"

        # Intentamos mostrar ventana nativa de error
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error Crítico Lectorcito Pro", error_msg)
            root.destroy()
        except:
            # Si falla tkinter, al menos queda en consola/log
            print(error_msg)


# Asegura que main() se ejecute solo cuando el script es el programa principal.
if __name__ == "__main__":
    main()