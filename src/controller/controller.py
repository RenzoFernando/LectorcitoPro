import os
import shutil
import threading
import webbrowser

import config
from model import processor
from view.ui import LectorcitoApp, InputDialog, ConfirmDialog, ChoiceDialog


class LectorcitoController:

    def __init__(self):
        self.config = config.load_config()
        self._update_active_lecturas_path()

        self.view = LectorcitoApp(self.config, self)

        self.last_report_path = None
        self.is_processing = False
        self.cancel_event = None  # Evento para la cancelación

    def run(self):
        self.view.mainloop()

    def _update_active_lecturas_path(self):
        if self.config.get("use_default_path", True):
            self.config["lecturas_path"] = config.DEFAULT_LECTURAS_PATH
        else:
            self.config["lecturas_path"] = self.config.get("custom_lecturas_path", config.DEFAULT_LECTURAS_PATH)

        if self.config["lecturas_path"]:
            os.makedirs(self.config["lecturas_path"], exist_ok=True)

    def select_destination_path(self):
        choice = ChoiceDialog.ask(
            parent=self.view,
            title=self.view._tr("dlg_dest_choice_title"),
            message=self.view._tr("dlg_dest_choice_prompt"),
            option1_text=self.view._tr("dlg_dest_choice_op1"),
            option2_text=self.view._tr("dlg_dest_choice_op2")
        )
        if choice == "default":
            self.config["use_default_path"] = True
            self.config["lecturas_path"] = config.DEFAULT_LECTURAS_PATH
            config.save_config(self.config)
            self.view.show_message("info_title", "dest_set_default_msg")
        elif choice == "custom":
            path = self.view.ask_for_directory("btn_sel_lecturas")
            if path:
                custom_path = os.path.join(path, "Lecturas")
                os.makedirs(custom_path, exist_ok=True)
                self.config.update({
                    "use_default_path": False,
                    "custom_lecturas_path": custom_path,
                    "lecturas_path": custom_path
                })
                config.save_config(self.config)
                self.view.show_message("info_title", "dest_set_custom_msg", custom_path)

    def select_folder_to_read(self):
        if not self.config.get("lecturas_path"):
            self.view.show_message("info_title", "msg_select_dest")
            return
        path = self.view.ask_for_directory("btn_choose_folder")
        if path:
            self.config["last_read_folder"] = path
            config.save_config(self.config)
            self.start_processing(path)

    def start_processing(self, folder_path: str):
        if self.is_processing: return
        self.is_processing = True
        self.cancel_event = threading.Event()

        self.view.toggle_main_buttons_state("disabled")
        self.view.toggle_cancel_button_state("normal")
        self.view.set_progress(0)

        thread = threading.Thread(
            target=self._processing_thread_target,
            args=(folder_path, self.cancel_event),
            daemon=True
        )
        thread.start()

    def _processing_thread_target(self, folder_path: str, cancel_event: threading.Event):
        status, report_path = processor.generate_report(
            source_folder=folder_path,
            output_path=self.config["lecturas_path"],
            extensions=self.config["text_extensions"],
            media_extensions=self.config["media_extensions"],
            excludes=self.config["excluded_folders"],
            progress_callback=self.view.set_progress,
            cancel_event=cancel_event
        )
        if status == "success":
            self.last_report_path = report_path

        self.view.after(0, self._on_processing_finished, status)

    def _on_processing_finished(self, status: str):
        if status == "success":
            self.view.show_message("info_title", "msg_done")
        elif status == "cancelled":
            self.view.show_message("info_title", "msg_cancelled")
        elif status == "no_files":
            self.view.show_message("info_title", "msg_no_files")

        self.view.set_progress(0)
        self.view.toggle_main_buttons_state("normal")
        self.view.toggle_cancel_button_state("disabled")
        self.is_processing = False
        self.cancel_event = None

    def cancel_processing(self):
        """Método llamado por el botón 'Cancelar' en la vista."""
        if self.cancel_event:
            self.cancel_event.set()

    # --- Otros manejadores sin cambios relevantes para esta función ---
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
                    os.makedirs(path, exist_ok=True)
                    self.view.show_message("info_title", f"Contenido de '{os.path.basename(path)}' eliminado.")
                except Exception as e:
                    self.view.show_message("Error", f"No se pudo eliminar la carpeta:\n{e}")
        else:
            self.view.show_message("info_title", "msg_select_dest")

    def show_extensions_dialog(self):
        current_exts = ",".join(self.config["text_extensions"])
        new_exts_str = InputDialog.get_input(self.view, self.view._tr("dlg_exts_title"),
                                             self.view._tr("dlg_exts_prompt"), current_exts)
        if new_exts_str is not None:
            exts = [f".{e.strip().lstrip('.')}" for e in new_exts_str.split(",") if e.strip()]
            self.config["text_extensions"] = exts
            self.save_preferences()

    def show_excludes_dialog(self):
        current_excl = ",".join(self.config["excluded_folders"])
        new_excl_str = InputDialog.get_input(self.view, self.view._tr("dlg_excl_prompt"), current_excl)
        if new_excl_str is not None:
            self.config["excluded_folders"] = [d.strip() for d in new_excl_str.split(",") if d.strip()]
            self.save_preferences()

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
