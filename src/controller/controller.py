import os
import shutil
import threading
import webbrowser
from tkinter import filedialog

# Importación de módulos del proyecto
import config
from model import processor
from view.ui import LectorcitoApp
# --- Se importan los manejadores de eventos ---
from controller import handlers


class LectorcitoController:
    """Coordina las interacciones entre la Vista (UI) y el Modelo (lógica de procesamiento)."""

    def __init__(self):
        self.config = config.load_config()
        self.view = LectorcitoApp(self.config, self)
        self.last_report_path = None
        self.is_processing = False
        self.cancel_event = None
        self._assign_commands()

    def _assign_commands(self):
        """Asigna los comandos de los widgets a sus manejadores correspondientes."""
        # Botones principales
        self.view.main_buttons["selpath"].configure(command=lambda: handlers.select_destination_path(self))
        self.view.main_buttons["choose"].configure(command=self.select_folder_to_read)
        self.view.main_buttons["create_tree"].configure(command=self.create_tree_structure)
        self.view.main_buttons["openlect"].configure(command=lambda: handlers.open_destination_folder(self))
        self.view.main_buttons["openlast"].configure(command=lambda: handlers.open_last_report(self))
        self.view.main_buttons["delete"].configure(command=lambda: handlers.delete_all_readings(self))

        # Botones de la barra lateral
        self.view.sidebar_buttons["ver"].configure(command=lambda: handlers.show_view_config_dialog(self))
        self.view.sidebar_buttons["nover"].configure(command=lambda: handlers.show_no_view_config_dialog(self))
        self.view.sidebar_buttons["theme_icon"].configure(command=lambda: handlers.toggle_theme(self))
        self.view.sidebar_buttons["traducir"].configure(command=lambda: handlers.toggle_language(self))
        self.view.sidebar_buttons["restaurar"].configure(command=lambda: handlers.restore_default_settings(self))
        self.view.sidebar_buttons["github"].configure(command=lambda: webbrowser.open_new(self.view.REPO_URL))
        self.view.sidebar_buttons["info"].configure(command=self.view.show_app_info)

        # Botón de cancelar
        self.view.btn_cancel.configure(command=self.cancel_processing)

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

    # --- Lógica de Procesamiento Principal (Se mantiene en el controlador) ---

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

        # Para esta función, el diálogo ChoiceDialog es parte del flujo, así que se queda aquí.
        from view.dialogs import ChoiceDialog
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

    def _safe_progress_update(self, percentage: float, file_context: str):
        """
        Garantiza que la actualización de la UI se ejecute en el hilo principal
        para evitar problemas de concurrencia con Tkinter.
        """
        self.view.after(0, self.view.set_progress, percentage, file_context)

    def _processing_thread_target(self, folder_path: str, cancel_event: threading.Event):
        # La llamada a `generate_report` ahora usa un callback seguro para el hilo.
        status, report_path = processor.generate_report(
            source_folder=folder_path, output_path=self.config["lecturas_path"], config=self.config,
            progress_callback=self._safe_progress_update,  # <-- CAMBIO CLAVE
            cancel_event=cancel_event
        )
        if status == "success":
            self.last_report_path = report_path

        # La finalización se programa en el hilo principal usando `after`.
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

    def cancel_processing(self):
        if self.cancel_event:
            self.cancel_event.set()

    def _check_destination_path(self) -> bool:
        if not self.config.get("lecturas_path"):
            self.view.show_message("info_title", "msg_select_dest")
            return False
        return True
