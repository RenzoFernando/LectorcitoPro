import os
import shutil
import threading
import webbrowser

import config
from model import processor
from view.ui import LectorcitoApp, InputDialog, ConfirmDialog


class LectorcitoController:

    def __init__(self):
        self.config = config.load_config()
        self.view = LectorcitoApp(self.config, self)

        self.last_report_path = None
        self.is_processing = False

    def run(self):
        self.view.mainloop()

    # --- Manejadores de eventos de la UI ---

    def select_destination_path(self):
        path = self.view.ask_for_directory("btn_sel_lecturas")
        if path:
            self.config["lecturas_path"] = os.path.join(path, "Lecturas")
            os.makedirs(self.config["lecturas_path"], exist_ok=True)
            self.view.show_message("info_title", f"Destino establecido en:\n{self.config['lecturas_path']}")

    def select_folder_to_read(self):
        if not self.config.get("lecturas_path"):
            self.view.show_message("info_title", "msg_select_dest")
            return
        path = self.view.ask_for_directory("btn_choose_folder")
        if path:
            self.config["last_read_folder"] = path
            config.save_config(self.config)  # Guardar la última carpeta leída
            self.start_processing(path)

    def open_destination_folder(self):
        path = self.config.get("lecturas_path")
        if path and os.path.isdir(path):
            webbrowser.open(os.path.realpath(path))
        else:
            self.view.show_message("info_title", "msg_select_dest")

    def open_last_report(self):
        if self.last_report_path and os.path.isfile(self.last_report_path):
            webbrowser.open(os.path.realpath(self.last_report_path))
        else:
            self.view.show_message("info_title", "msg_no_files")

    def delete_all_readings(self):
        path = self.config.get("lecturas_path")
        if path and os.path.isdir(path):
            if ConfirmDialog.ask(self.view, self.view._tr("confirm_del_title"), self.view._tr("confirm_del_prompt")):
                try:
                    shutil.rmtree(path)
                    self.view.show_message("info_title", f"Carpeta '{path}' eliminada.")
                except Exception as e:
                    self.view.show_message("Error", f"No se pudo eliminar la carpeta:\n{e}")
        else:
            self.view.show_message("info_title", "msg_select_dest")

    # --- Lógica de Procesamiento ---

    def start_processing(self, folder_path: str):
        if self.is_processing: return
        self.is_processing = True
        self.view.set_buttons_state("disabled")
        self.view.set_progress(0)
        thread = threading.Thread(target=self._processing_thread_target, args=(folder_path,), daemon=True)
        thread.start()

    def _processing_thread_target(self, folder_path: str):
        report_path = processor.generate_report(
            source_folder=folder_path,
            output_path=self.config["lecturas_path"],
            extensions=self.config["text_extensions"],
            excludes=self.config["excluded_folders"],
            progress_callback=self.view.set_progress
        )
        self.last_report_path = report_path
        self.view.after(0, self._on_processing_finished, report_path is not None)

    def _on_processing_finished(self, success: bool):
        if success:
            self.view.show_message("info_title", "msg_done")
        else:
            self.view.show_message("info_title", "msg_no_files")
        self.view.set_progress(0)
        self.view.set_buttons_state("normal")
        self.is_processing = False

    # --- Manejadores de la Barra Derecha ---

    def show_extensions_dialog(self):
        current_exts = ",".join(self.config["text_extensions"])
        new_exts_str = InputDialog.get_input(self.view, self.view._tr("dlg_exts_title"),
                                            self.view._tr("dlg_exts_prompt"), current_exts)
        if new_exts_str is not None:
            exts = [f".{e.strip().lstrip('.')}" for e in new_exts_str.split(",") if e.strip()]
            self.config["text_extensions"] = exts
            config.save_config(self.config)
            self.view.show_message("save_prefs_title", "save_prefs_msg")

    def show_excludes_dialog(self):
        current_excl = ",".join(self.config["excluded_folders"])
        new_excl_str = InputDialog.get_input(self.view, self.view._tr("dlg_excl_title"),
                                            self.view._tr("dlg_excl_prompt"), current_excl)
        if new_excl_str is not None:
            self.config["excluded_folders"] = [d.strip() for d in new_excl_str.split(",") if d.strip()]
            config.save_config(self.config)
            self.view.show_message("save_prefs_title", "save_prefs_msg")

    def save_preferences(self):
        config.save_config(self.config)
        self.view.show_message("save_prefs_title", "save_prefs_msg")

    def toggle_theme(self):
        self.view.current_theme = "Dark" if self.view.current_theme == "Light" else "Light"
        self.config["theme"] = self.view.current_theme
        self.view._apply_theme()
        config.save_config(self.config)

    def toggle_language(self):
        self.view.lang = "en" if self.view.lang == "es" else "es"
        self.config["language"] = self.view.lang
        self.view.update_ui_texts()
        config.save_config(self.config)
