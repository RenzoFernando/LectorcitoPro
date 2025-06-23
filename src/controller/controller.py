import os
import shutil
import threading
import webbrowser
from tkinter import filedialog

import config
from model import processor
from view.ui import LectorcitoApp
from controller import handlers


# Clase principal del controlador (patrón MVC).
class LectorcitoController:

    # Inicializa el controlador, la vista y el estado de la aplicación.
    def __init__(self):
        self.config = config.load_config()
        self.view = LectorcitoApp(self.config, self)
        self.last_report_path = None
        self.is_processing = False
        self.cancel_event = None
        self._assign_commands()

    # Asigna los métodos de esta clase a los widgets de la interfaz gráfica.
    def _assign_commands(self):
        self.view.main_buttons["selpath"].configure(command=lambda: handlers.select_destination_path(self))
        self.view.main_buttons["choose"].configure(command=self.select_reading_type)
        self.view.main_buttons["create_tree"].configure(command=self.create_tree_structure)
        self.view.main_buttons["openlect"].configure(command=lambda: handlers.open_destination_folder(self))
        self.view.main_buttons["openlast"].configure(command=lambda: handlers.open_last_report(self))
        self.view.main_buttons["delete"].configure(command=lambda: handlers.delete_all_readings(self))

        self.view.sidebar_buttons["ver"].configure(command=lambda: handlers.show_view_config_dialog(self))
        self.view.sidebar_buttons["nover"].configure(command=lambda: handlers.show_no_view_config_dialog(self))
        self.view.sidebar_buttons["theme_icon"].configure(command=lambda: handlers.toggle_theme(self))
        self.view.sidebar_buttons["traducir"].configure(command=lambda: handlers.toggle_language(self))
        self.view.sidebar_buttons["restaurar"].configure(command=lambda: handlers.restore_default_settings(self))
        self.view.sidebar_buttons["github"].configure(command=lambda: webbrowser.open_new(self.view.REPO_URL))
        self.view.sidebar_buttons["info"].configure(command=self.view.show_app_info)

        self.view.btn_cancel.configure(command=self.cancel_processing)

    # Inicia el bucle principal de la aplicación.
    def run(self):
        self.view.mainloop()

    # Muestra un diálogo para elegir entre lectura simple o múltiple.
    def select_reading_type(self):
        if not self._check_destination_path():
            return

        from view.dialogs import ChoiceDialog
        choice = ChoiceDialog.ask(
            parent=self.view,
            title=self.view._tr("dlg_read_type_title"),
            message=self.view._tr("dlg_read_type_prompt"),
            option1_text=self.view._tr("dlg_read_type_op1"),
            option2_text=self.view._tr("dlg_read_type_op2"),
            option1_value="single",
            option2_value="multiple"
        )

        if choice == "single":
            self.select_single_folder_to_read()
        elif choice == "multiple":
            self.select_multiple_folders_to_read()

    # Abre el diálogo para seleccionar una única carpeta a procesar.
    def select_single_folder_to_read(self):
        path = filedialog.askdirectory(
            title=self.view._tr("btn_choose_folder"),
            initialdir=self.config.get("last_read_folder", "")
        )
        if path:
            self.config["last_read_folder"] = path
            self.start_batch_processing([path])

    # Abre un diálogo personalizado para seleccionar múltiples carpetas.
    def select_multiple_folders_to_read(self):
        from view.dialogs import SelectFoldersDialog
        paths = SelectFoldersDialog.ask(parent=self.view, title=self.view._tr("dlg_multi_folder_title"))

        if paths:
            self.config["last_read_folder"] = paths[0]
            self.start_batch_processing(paths)

    # Inicia el procesamiento de carpetas en un hilo secundario para no bloquear la UI.
    def start_batch_processing(self, folder_paths: list):
        if self.is_processing:
            return

        if len(folder_paths) > 1:
            self.view.show_message("info_title", "msg_batch_started", len(folder_paths))

        self.is_processing = True
        self.cancel_event = threading.Event()
        self.view.toggle_ui_for_processing(is_active=True)
        thread = threading.Thread(
            target=self._batch_processing_thread_target, args=(folder_paths, self.cancel_event), daemon=True
        )
        thread.start()

    # Función que ejecuta el hilo para procesar un lote de carpetas.
    def _batch_processing_thread_target(self, folder_paths: list, cancel_event: threading.Event):
        overall_status = "success"
        reports_generated = 0
        total_folders = len(folder_paths)

        for i, folder_path in enumerate(folder_paths):
            if cancel_event.is_set():
                overall_status = "cancelled"
                break

            folder_name = os.path.basename(folder_path)
            context_prefix = f"[{i + 1}/{total_folders}] " if total_folders > 1 else ""
            self.view.after(0, self.view.set_progress, 0, f"{context_prefix}{folder_name}")

            status, report_path = processor.generate_report(
                source_folder=folder_path,
                output_path=self.config["lecturas_path"],
                config=self.config,
                progress_callback=self._safe_progress_update,
                cancel_event=cancel_event
            )

            if status == "success":
                self.last_report_path = report_path
                reports_generated += 1
            elif status in ["error", "cancelled", "no_files"]:
                overall_status = status
                break

        self.view.after(0, self._on_processing_finished, overall_status, reports_generated)

    # Se ejecuta al finalizar el hilo de procesamiento para actualizar la UI.
    def _on_processing_finished(self, status: str, reports_generated: int = 0):
        if status == "success":
            self.view.set_progress(100)

        delay = 400 if status == 'success' else 0
        self.view.after(delay, self._finalize_ui_and_message, status, reports_generated)

    # Restaura la UI y muestra el mensaje final al usuario.
    def _finalize_ui_and_message(self, status: str, reports_generated: int):
        self.is_processing = False
        self.cancel_event = None
        self.view.toggle_ui_for_processing(is_active=False)

        if status == "success":
            if reports_generated > 1:
                self.view.show_message("info_title", "msg_batch_done", reports_generated)
            elif reports_generated == 1:
                self.view.show_message("info_title", "msg_done")
        else:
            message_map = {
                "cancelled": ("info_title", "msg_cancelled"),
                "no_files": ("info_title", "msg_no_files_found"),
                "error": ("error_title", "msg_error_generic")
            }
            if status in message_map:
                title_key, msg_key = message_map[status]
                self.view.show_message(title_key, msg_key)

    # Callback para actualizar el progreso de forma segura desde otro hilo.
    def _safe_progress_update(self, percentage: float, file_context: str):
        self.view.after(0, self.view.set_progress, percentage, file_context)

    # Establece el evento de cancelación para detener el procesamiento.
    def cancel_processing(self):
        if self.cancel_event:
            self.cancel_event.set()

    # Verifica si se ha configurado una ruta de destino.
    def _check_destination_path(self) -> bool:
        if not self.config.get("lecturas_path"):
            self.view.show_message("info_title", "msg_select_dest")
            return False
        return True

    # Inicia la creación de un reporte con la estructura de árbol del directorio.
    def create_tree_structure(self):
        if self.is_processing or not self._check_destination_path():
            return

        from view.dialogs import ChoiceDialog
        choice = ChoiceDialog.ask(
            parent=self.view, title=self.view._tr("dlg_tree_choice_title"),
            message=self.view._tr("dlg_tree_choice_prompt"),
            option1_text=self.view._tr("dlg_tree_op1"), option2_text=self.view._tr("dlg_tree_op2"),
            option1_value="complete", option2_value="filtered"
        )
        if not choice:
            return

        source_path = filedialog.askdirectory(title=self.view._tr("btn_create_tree"))
        if not source_path:
            return

        self.is_processing = True
        self.view.toggle_ui_for_processing(is_active=True, mode='indeterminate',
                                             text=self.view._tr("progress_generating_tree"))

        thread = threading.Thread(
            target=self._tree_thread_target, args=(source_path, choice == "filtered"), daemon=True
        )
        thread.start()

    # Función que ejecuta el hilo para generar la estructura de árbol.
    def _tree_thread_target(self, source_path: str, use_filters: bool):
        status, report_path = processor.generate_tree_report(
            source_folder=source_path, output_path=self.config["lecturas_path"], use_config=use_filters,
            config=self.config
        )
        self.view.after(0, self._on_tree_generation_finished, status, report_path)

    # Se ejecuta al finalizar la generación del árbol.
    def _on_tree_generation_finished(self, status: str, report_path: str | None):
        if status == "success":
            self.view.toggle_ui_for_processing(is_active=True, mode='determinate')
            self.view.set_progress(100, self.view._tr("progress_done"))

        delay = 400 if status == 'success' else 0
        self.view.after(delay, self._finalize_tree_ui_and_message, status, report_path)

    # Restaura la UI y muestra el mensaje final de la creación del árbol.
    def _finalize_tree_ui_and_message(self, status: str, report_path: str | None):
        self.is_processing = False
        self.view.toggle_ui_for_processing(is_active=False)

        if status == "success" and report_path:
            self.last_report_path = report_path
            self.view.show_message("info_title", "msg_tree_done", os.path.basename(report_path))
        else:
            self.view.show_message("error_title", "msg_error_generic")

    # Actualiza la ruta de destino activa según la configuración del usuario.
    def _update_active_lecturas_path(self):
        if self.config.get("use_default_path", True):
            self.config["lecturas_path"] = config.DEFAULT_LECTURAS_PATH
        else:
            self.config["lecturas_path"] = self.config.get("custom_lecturas_path", config.DEFAULT_LECTURAS_PATH)

        if self.config["lecturas_path"]:
            os.makedirs(self.config["lecturas_path"], exist_ok=True)