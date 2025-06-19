import os
import shutil
import threading
import webbrowser
from tkinter import filedialog

# Importación de módulos del proyecto
import config
from model import processor
from view.ui import LectorcitoApp, InputDialog, ConfirmDialog, ChoiceDialog


class LectorcitoController:
    """Coordina las interacciones entre la Vista (UI) y el Modelo (lógica de procesamiento)."""

    def __init__(self):
        self.config = config.load_config()
        self._update_active_lecturas_path()
        self.view = LectorcitoApp(self.config, self)
        self.last_report_path = None
        self.is_processing = False
        self.cancel_event = None

    def run(self):
        """Inicia el bucle principal de la aplicación."""
        self.view.mainloop()

    def _update_active_lecturas_path(self):
        """Asegura que la ruta de guardado de lecturas esté definida y exista."""
        if self.config.get("use_default_path", True):
            self.config["lecturas_path"] = config.DEFAULT_LECTURAS_PATH
        else:
            self.config["lecturas_path"] = self.config.get("custom_lecturas_path", config.DEFAULT_LECTURAS_PATH)

        if self.config["lecturas_path"]:
            os.makedirs(self.config["lecturas_path"], exist_ok=True)

    # --- Manejadores de Eventos de la UI ---

    def select_folder_to_read(self):
        if self._check_destination_path():
            path = filedialog.askdirectory(title=self.view._tr("btn_choose_folder"))
            if path:
                self.config["last_read_folder"] = path
                self.start_processing(path)

    def create_tree_structure(self):
        if not self._check_destination_path():
            return
        source_path = filedialog.askdirectory(title=self.view._tr("btn_create_tree"))
        if not source_path:
            return

        choice = ChoiceDialog.ask(
            parent=self.view, title=self.view._tr("dlg_tree_choice_title"),
            message=self.view._tr("dlg_tree_choice_prompt"),
            option1_text=self.view._tr("dlg_tree_op1"), option2_text=self.view._tr("dlg_tree_op2"),
            option1_value="complete", option2_value="filtered"
        )
        if not choice:
            return

        use_filters = (choice == "filtered")
        status, report_path = processor.generate_tree_report(
            source_folder=source_path, output_path=self.config["lecturas_path"], use_config=use_filters,
            config=self.config
        )

        if status == "success":
            self.last_report_path = report_path
            self.view.show_message("info_title", "msg_tree_done", os.path.basename(report_path))
        else:
            self.view.show_message("error_title", "msg_error_generic")

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
            self.view.show_message("info_title", "msg_no_report_yet")

    def delete_all_readings(self):
        path = self.config.get("lecturas_path")
        if not (path and os.path.isdir(path)):
            self.view.show_message("info_title", "msg_select_dest")
            return

        if ConfirmDialog.ask(self.view, self.view._tr("confirm_del_title"), self.view._tr("confirm_del_prompt")):
            try:
                shutil.rmtree(path)
                os.makedirs(path, exist_ok=True)
                self.view.show_message("info_title", "msg_delete_success", os.path.basename(path))
            except Exception as e:
                self.view.show_message("error_title", "msg_delete_error", str(e))

    # --- Lógica de Procesamiento en Hilo Separado ---

    def start_processing(self, folder_path: str):
        if self.is_processing:
            return
        self.is_processing = True
        self.cancel_event = threading.Event()
        self.view.toggle_ui_for_processing(is_active=True)
        thread = threading.Thread(
            target=self._processing_thread_target, args=(folder_path, self.cancel_event), daemon=True
        )
        thread.start()

    def _processing_thread_target(self, folder_path: str, cancel_event: threading.Event):
        status, report_path = processor.generate_report(
            source_folder=folder_path, output_path=self.config["lecturas_path"], config=self.config,
            progress_callback=self.view.set_progress, cancel_event=cancel_event
        )
        if status == "success":
            self.last_report_path = report_path
        self.view.after(0, self._on_processing_finished, status)

    def _on_processing_finished(self, status: str):
        message_map = {
            "success": ("info_title", "msg_done"), "cancelled": ("info_title", "msg_cancelled"),
            "no_files": ("info_title", "msg_no_files_found"), "error": ("error_title", "msg_error_generic")
        }
        if status in message_map:
            title_key, msg_key = message_map[status]
            self.view.show_message(title_key, msg_key)

        self.is_processing = False
        self.cancel_event = None
        self.view.toggle_ui_for_processing(is_active=False)
        self.view.set_progress(0)

    def cancel_processing(self):
        if self.cancel_event:
            self.cancel_event.set()

    # --- Manejadores de Configuración ---

    def select_destination_path(self):
        choice = ChoiceDialog.ask(
            parent=self.view, title=self.view._tr("dlg_dest_choice_title"),
            message=self.view._tr("dlg_dest_choice_prompt"),
            option1_text=self.view._tr("dlg_dest_choice_op1"), option2_text=self.view._tr("dlg_dest_choice_op2"),
            option1_value="default", option2_value="custom"
        )
        if choice == "default":
            self.config["use_default_path"] = True
            self.view.show_message("info_title", "dest_set_default_msg")
        elif choice == "custom":
            path = filedialog.askdirectory(title=self.view._tr("btn_sel_lecturas"))
            if path:
                custom_path = os.path.join(path, "Lecturas")
                self.config.update({"use_default_path": False, "custom_lecturas_path": custom_path})
                self.view.show_message("info_title", "dest_set_custom_msg", custom_path)

        self._update_active_lecturas_path()
        self.save_preferences_silent()

    def show_extensions_dialog(self):
        current_exts = ", ".join(self.config["text_extensions"])
        new_exts_str = InputDialog.get_input(
            self.view, self.view._tr("dlg_exts_title"), self.view._tr("dlg_exts_prompt"), current_exts
        )
        if new_exts_str is not None:
            self.config["text_extensions"] = [f".{e.strip().lstrip('.')}" for e in new_exts_str.split(",") if e.strip()]
            self.save_preferences_silent()

    def show_excludes_dialog(self):
        current_excl = ", ".join(self.config["excluded_folders"])
        new_excl_str = InputDialog.get_input(
            self.view, self.view._tr("dlg_excl_title"), self.view._tr("dlg_excl_prompt"), current_excl
        )
        if new_excl_str is not None:
            self.config["excluded_folders"] = [d.strip() for d in new_excl_str.split(",") if d.strip()]
            self.save_preferences_silent()

    def save_preferences_silent(self):
        """Guarda la configuración actual sin notificar al usuario."""
        config.save_config(self.config)

    def toggle_theme(self):
        self.view.current_theme = "Dark" if self.view.current_theme == "Light" else "Light"
        self.config["theme"] = self.view.current_theme
        self.view.apply_theme()
        self.save_preferences_silent()

    def toggle_language(self):
        self.view.lang = "en" if self.view.lang == "es" else "es"
        self.config["language"] = self.view.lang
        self.view.update_ui_texts()
        self.save_preferences_silent()

    def restore_default_settings(self):
        """Restaura la configuración por defecto eliminando el archivo JSON."""
        if ConfirmDialog.ask(self.view, self.view._tr("confirm_restore_title"),
                             self.view._tr("confirm_restore_prompt")):
            config.delete_config_file()
            self.config = config.load_config()

            self._update_active_lecturas_path()
            self.view.lang = self.config["language"]
            self.view.current_theme = self.config["theme"]
            self.view.update_ui_texts()
            self.view.apply_theme()
            self.save_preferences_silent()
            self.view.show_message("info_title", "msg_restore_success")

    def _check_destination_path(self) -> bool:
        if not self.config.get("lecturas_path"):
            self.view.show_message("info_title", "msg_select_dest")
            return False
        return True
