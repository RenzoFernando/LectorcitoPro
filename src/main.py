import sys
import os
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from controller.controller import LectorcitoController
from app_meta import APP_DISPLAY_NAME
import utils


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

def main():
    utils.setup_logging()

    try:
        app = LectorcitoController()
        app.run()

    except KeyboardInterrupt:
        print("\nAplicación detenida por el usuario.")
        sys.exit(0)

    except Exception as e:
        utils.log_error("Error Crítico al iniciar", e)

        log_file = utils.get_log_path()
        error_msg = f"Error crítico:\n\n{e}\n\nDetalles en:\n{log_file}"

        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(f"Error Crítico {APP_DISPLAY_NAME}", error_msg)
            root.destroy()
        except:
            print(error_msg)


if __name__ == "__main__":
    main()