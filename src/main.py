import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import utils
from app_meta import APP_DISPLAY_NAME
from controller.controller import LectorcitoController
from i18n.translations import translate_default

# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================


def _open_log_folder(log_file: str) -> bool:
    folder = os.path.dirname(os.path.abspath(str(log_file or "")))
    if not folder or not os.path.isdir(folder):
        return False

    try:
        if sys.platform.startswith("win"):
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
        return True
    except Exception:
        return False


def _show_critical_error_dialog(error_msg: str, log_file: str):
    root = tk.Tk()
    root.title(translate_default("critical_error_title", APP_DISPLAY_NAME))
    root.resizable(False, False)

    width, height = 540, 290
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = max(0, (screen_w - width) // 2)
    y = max(0, (screen_h - height) // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    content = ttk.Frame(root, padding=(22, 20, 22, 14))
    content.pack(fill="both", expand=True)

    title = ttk.Label(
        content,
        text=translate_default("critical_error_label"),
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    )
    title.pack(fill="x")

    message = ttk.Label(
        content,
        text=error_msg,
        justify="left",
        anchor="nw",
        wraplength=490,
    )
    message.pack(fill="both", expand=True, pady=(8, 14))

    buttons = ttk.Frame(content)
    buttons.pack(fill="x")

    def open_logs():
        if not _open_log_folder(log_file):
            messagebox.showerror(
                translate_default("error_title"),
                translate_default("critical_log_folder_error"),
                parent=root,
            )

    ttk.Button(
        buttons,
        text=translate_default("btn_open_log_folder"),
        command=open_logs,
    ).pack(side="left")
    ttk.Button(buttons, text="OK", command=root.destroy).pack(side="right")

    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.lift()
    try:
        root.attributes("-topmost", True)
        root.after(250, lambda: root.attributes("-topmost", False))
    except Exception:
        pass
    root.mainloop()


def main():
    utils.setup_logging()
    utils.log_info("Inicio de aplicacion.", operation="startup")

    try:
        app = LectorcitoController()
        app.run()

    except KeyboardInterrupt:
        utils.log_info("Aplicacion cancelada por teclado.", operation="shutdown")
        print("\n" + translate_default("msg_cancelled"))
        sys.exit(0)

    except Exception as e:
        utils.log_error("Error Crítico al iniciar", e)

        log_file = utils.create_critical_error_log("Error Crítico al iniciar", e)
        error_msg = translate_default("critical_error_message", e, log_file)

        try:
            _show_critical_error_dialog(error_msg, log_file)
        except Exception:
            print(error_msg)


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    main()