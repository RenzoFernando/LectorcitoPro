import os
import shutil
import threading
import webbrowser
from tkinter import messagebox
import customtkinter as ctk

# Importaciones locales de la aplicación
import config
from model import processor
from view.ui import LectorcitoApp
from config import load_cfg, save_cfg
from config import load_config, save_config



class LectorcitoController:
    """
    El Controlador. Conecta la Vista (UI) con el Modelo (lógica de negocio).
    Maneja las acciones del usuario y actualiza la vista según sea necesario.
    """

    def __init__(self):
        self.config = load_config()
        self.view   = LectorcitoApp(self.config, self)

        # Estado de la aplicación
        self.last_report_path = None
        self.is_processing = False

    def run(self):
        """Inicia el bucle principal de la aplicación."""
        self.view.mainloop()

    # --- Manejadores de eventos de la UI ---

    def select_destination_path(self):
        """Maneja la selección de la carpeta de destino para las lecturas."""
        path = self.view.ask_for_directory("btn_sel_lecturas")
        if path:
            self.config["lecturas_path"] = os.path.join(path, "Lecturas")
            os.makedirs(self.config["lecturas_path"], exist_ok=True)
            self.view.show_info(self.view._tr("info_title"), f"Destino establecido en:\n{self.config['lecturas_path']}")

    def select_folder_to_read(self):
        """Selecciona la carpeta a leer e inicia el procesamiento."""
        if not self.config.get("lecturas_path"):
            messagebox.showwarning(self.view._tr("info_title"), self.view._tr("msg_select_dest"))
            return

        path = self.view.ask_for_directory("btn_choose_folder")
        if path:
            self.config["last_read_folder"] = path
            self.start_processing(path)

    def open_destination_folder(self):
        """Abre la carpeta de destino en el explorador de archivos."""
        path = self.config.get("lecturas_path")
        if path and os.path.isdir(path):
            webbrowser.open(os.path.realpath(path))
        else:
            messagebox.showwarning(self.view._tr("info_title"), self.view._tr("msg_select_dest"))

    def open_last_report(self):
        """Abre el último archivo de reporte generado."""
        if self.last_report_path and os.path.isfile(self.last_report_path):
            webbrowser.open(os.path.realpath(self.last_report_path))
        else:
            messagebox.showinfo(self.view._tr("info_title"), self.view._tr("msg_no_files"))

    def delete_all_readings(self):
        """Elimina la carpeta de lecturas y todo su contenido."""
        path = self.config.get("lecturas_path")
        if path and os.path.isdir(path):
            if messagebox.askyesno(self.view._tr("confirm_del_title"), self.view._tr("confirm_del_prompt")):
                try:
                    shutil.rmtree(path)
                    messagebox.showinfo(self.view._tr("info_title"), f"Carpeta '{path}' eliminada.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar la carpeta:\n{e}")
        else:
            messagebox.showwarning(self.view._tr("info_title"), self.view._tr("msg_select_dest"))

    # --- Lógica de Procesamiento ---

    def start_processing(self, folder_path: str):
        """Inicia el proceso de generación de reporte en un hilo separado."""
        if self.is_processing:
            return

        self.is_processing = True
        self.view.set_buttons_state("disabled")
        self.view.set_progress(0)

        thread = threading.Thread(
            target=self._processing_thread_target,
            args=(folder_path,),
            daemon=True
        )
        thread.start()

    def _processing_thread_target(self, folder_path: str):
        """Función que se ejecuta en el hilo para no bloquear la UI."""
        report_path = processor.generate_report(
            source_folder=folder_path,
            output_path=self.config["lecturas_path"],
            extensions=self.config["text_extensions"],
            excludes=self.config["excluded_folders"],
            progress_callback=self.view.set_progress
        )

        self.last_report_path = report_path

        # La actualización de la UI debe hacerse en el hilo principal
        self.view.after(0, self._on_processing_finished, report_path is not None)

    def _on_processing_finished(self, success: bool):
        """Callback que se ejecuta en el hilo principal cuando el procesamiento termina."""
        if success:
            messagebox.showinfo(self.view._tr("info_title"), self.view._tr("msg_done"))
        else:
            messagebox.showinfo(self.view._tr("info_title"), self.view._tr("msg_no_files"))

        self.view.set_progress(0)
        self.view.set_buttons_state("normal")
        self.is_processing = False

    # --- Manejadores de la Barra Derecha ---

    def show_extensions_dialog(self):
        """Configura las extensiones permitidas."""
        # 1) Texto actual
        current = ",".join(self.config["text_extensions"])
        # 2) Pide al usuario la nueva lista
        new = self.view.show_custom_dialog(
            "dlg_exts_title",   # clave de título en tus TRANSLATIONS
            "dlg_exts_prompt",  # clave del prompt
            current
        )
        if not new:
            return
        # 3) Parsea y asegura que empiece con punto
        exts = []
        for part in new.split(","):
            e = part.strip()
            if not e:
                continue
            if not e.startswith("."):
                e = "." + e
            exts.append(e.lower())
        # 4) Actualiza config y guarda
        self.config["text_extensions"] = exts
        save_config(self.config)
        # 5) Feedback
        self.view.show_info(
            self.view._tr("save_prefs_title"),
            self.view._tr("save_prefs_msg")
        )

    def show_excludes_dialog(self):
        """Configura las carpetas excluidas."""
        current = ",".join(self.config["excluded_folders"])
        new = self.view.show_custom_dialog(
            "dlg_excl_title",
            "dlg_excl_prompt",
            current
        )
        if not new:
            return
        excl = [d.strip() for d in new.split(",") if d.strip()]
        self.config["excluded_folders"] = excl
        save_config(self.config)
        self.view.show_info(
            self.view._tr("save_prefs_title"),
            self.view._tr("save_prefs_msg")
        )

    def save_preferences(self):
        """Guarda la configuración actual en el archivo JSON."""
        config.save_config(self.config)
        messagebox.showinfo(self.view._tr("save_prefs_title"), self.view._tr("save_prefs_msg"))

    def toggle_theme(self):
        """Cambia entre el tema claro y oscuro."""
        self.view.current_theme = "Dark" if self.view.current_theme == "Light" else "Light"
        self.config["theme"] = self.view.current_theme
        ctk.set_appearance_mode(self.view.current_theme)
        self.view._apply_theme()  # Pide a la vista que se redibuje

    def toggle_language(self):
        """Cambia entre español e inglés."""
        self.view.lang = "en" if self.view.lang == "es" else "es"
        self.config["language"] = self.view.lang
        self.view.update_ui_texts()  # Pide a la vista que actualice sus textos

    def show_info(self):
        """Muestra la información de la aplicación."""
        info_text = (
            f"Lectorcito Pro v{self.view.VERSION}\n\n"
            f"Desarrollado por: {self.view.AUTHOR}\n"
            f"Repositorio: {self.view.REPO_URL}\n\n"
            f"© {self.view.YEAR} - All Rights Reserved."
        )
        messagebox.showinfo(self.view._tr("info_title"), info_text)
