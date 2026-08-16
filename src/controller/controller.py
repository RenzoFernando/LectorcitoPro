import os
import threading
import webbrowser
from tkinter import filedialog

from app_meta import APP_WEBSITE_URL
import config
import utils
from view.translations import translate_default
from model import processor
from view.ui import LectorcitoApp
from controller import handlers
from platform_services import get_platform_service

# =============================================================================
# CONTROLADOR PRINCIPAL
# =============================================================================

class LectorcitoController:

    def __init__(self):
        self.platform = get_platform_service()
        self.config = config.load_config()
        self.view = LectorcitoApp(self.config, self)

        self.last_report_path = None
        self.is_processing = False
        self.cancel_event = None

        self._assign_commands()
        self._update_active_lecturas_path()

    def _assign_commands(self):
        self.view.main_buttons["selpath"].configure(command=lambda: handlers.select_destination_path(self))
        self.view.main_buttons["choose"].configure(command=self.select_reading_type)
        self.view.main_buttons["create_tree"].configure(command=self.create_tree_structure)
        self.view.main_buttons["openlect"].configure(command=lambda: handlers.open_destination_folder(self))
        self.view.main_buttons["openlast"].configure(command=lambda: handlers.open_last_report(self))
        self.view.main_buttons["delete"].configure(command=lambda: handlers.delete_all_readings(self))
        self.view.btn_cancel.configure(command=self.cancel_processing)

        self.view.sidebar_buttons["ver"].configure(command=lambda: handlers.show_view_config_dialog(self))
        self.view.sidebar_buttons["nover"].configure(command=lambda: handlers.show_no_view_config_dialog(self))
        self.view.sidebar_buttons["etiqueta"].configure(command=lambda: handlers.show_etiqueta_config_dialog(self))
        self.view.sidebar_buttons["theme_icon"].configure(command=lambda: handlers.toggle_theme(self))
        self.view.sidebar_buttons["traducir"].configure(command=lambda: handlers.toggle_language(self))
        self.view.sidebar_buttons["restaurar"].configure(command=lambda: handlers.restore_default_settings(self))
        self.view.sidebar_buttons["perfil"].configure(command=lambda: handlers.manage_profiles(self))
        self.view.sidebar_buttons["github"].configure(command=self.open_repository_link)
        self.view.sidebar_buttons["info"].configure(command=self.open_manual_link)
        self.view.sidebar_buttons["ajustes"].configure(command=lambda: handlers.show_settings_dialog(self))

    def open_repository_link(self):
        handlers.open_external_link_with_confirmation(
            parent=self.view,
            url=self.view.REPO_URL,
            title_key="dlg_external_link_title",
            message_key="msg_open_repository_confirm",
            target_label=self.view.REPO_URL,
            continue_key="btn_continue_external",
            cancel_key="btn_cancel_simple"
        )

    def open_manual_link(self):
        handlers.open_external_link_with_confirmation(
            parent=self.view,
            url=APP_WEBSITE_URL,
            title_key="dlg_external_link_title",
            message_key="msg_open_manual_confirm",
            target_label=APP_WEBSITE_URL,
            continue_key="btn_continue_external",
            cancel_key="btn_cancel_simple"
        )

    def run(self):
        self.view.mainloop()

    # =========================================================================
    # LOGICA DE PROCESAMIENTO
    # =========================================================================

    def select_reading_type(self):
        if not self._check_destination_path():
            return

        path = filedialog.askdirectory(
            title=self.view._tr("btn_choose_folder"),
            initialdir=self.config.get("last_read_folder", "")
        )

        if path:
            self.config["last_read_folder"] = path
            handlers.save_preferences_silent(self)
            self.start_processing(path)

    def start_processing(self, folder_path: str):
        if self.is_processing:
            return

        self.is_processing = True
        self.cancel_event = threading.Event()

        self.view.toggle_ui_for_processing(is_active=True)

        thread = threading.Thread(
            target=self._processing_thread_target,
            args=(folder_path, self.cancel_event),
            daemon=True
        )
        thread.start()

    def _processing_thread_target(self, folder_path: str, cancel_event: threading.Event):
        overall_status = "error"
        try:
            folder_name = os.path.basename(folder_path)
            self.view.after(0, self.view.set_progress, 0, folder_name)

            status, report_path = processor.generate_report(
                source_folder=folder_path,
                output_path=self.config["lecturas_path"],
                config=self.config,
                progress_callback=self._safe_progress_update,
                cancel_event=cancel_event
            )

            if status == "success":
                self.last_report_path = report_path
            overall_status = status

        except Exception as e:
            utils.log_error("Excepción en hilo de procesamiento", e)
            overall_status = "error"

        self.view.after(0, self._on_processing_finished, overall_status)

    def _safe_progress_update(self, percentage: float, file_context: str):
        self.view.after(0, self.view.set_progress, percentage, file_context)

    def _on_processing_finished(self, status: str):
        if status == "success":
            self.view.set_progress(100)

        delay = self.view.get_min_visible_completion_delay_ms() if status == "success" else 0
        self.view.after(delay, self._finalize_ui_and_message, status)

    def _finalize_ui_and_message(self, status: str):
        self.is_processing = False
        self.cancel_event = None
        self.view.toggle_ui_for_processing(is_active=False, final_status=status)

        if status == "success":
            report_name = os.path.basename(self.last_report_path) if self.last_report_path else self.view._tr("default_report_name") if hasattr(self.view, "_tr") else translate_default("default_report_name")
            self.view.show_message("info_title", "msg_done", report_name)
        else:
            message_map = {
                "cancelled": ("info_title", "msg_cancelled"),
                "no_files": ("info_title", "msg_no_files_found"),
                "error": ("error_title", "msg_error_generic")
            }
            if status in message_map:
                title_key, msg_key = message_map[status]
                self.view.show_message(title_key, msg_key)

    def cancel_processing(self):
        if self.cancel_event:
            self.cancel_event.set()

    # =========================================================================
    # LOGICA DE ARBOL
    # =========================================================================

    def create_tree_structure(self):
        if self.is_processing or not self._check_destination_path():
            return

        source_path = filedialog.askdirectory(title=self.view._tr("btn_create_tree"))
        if not source_path:
            return

        self.is_processing = True
        self.view.toggle_ui_for_processing(
            is_active=True, mode='indeterminate', text=self.view._tr("progress_generating_tree")
        )

        thread = threading.Thread(
            target=self._tree_thread_target, args=(source_path,), daemon=True
        )
        thread.start()

    def _tree_thread_target(self, source_path: str):
        try:
            status, report_path = processor.generate_tree_report(
                source_folder=source_path, output_path=self.config["lecturas_path"], config=self.config
            )
        except Exception as e:
            utils.log_error("Excepción en hilo de árbol", e)
            status, report_path = "error", None

        self.view.after(0, self._on_tree_generation_finished, status, report_path)

    def _on_tree_generation_finished(self, status: str, report_path: str | None):
        if status == "success":
            self.view.toggle_ui_for_processing(is_active=True, mode='determinate')
            self.view.set_progress(100)

        delay = self.view.get_min_visible_completion_delay_ms() if status == "success" else 0
        self.view.after(delay, self._finalize_tree_ui_and_message, status, report_path)

    def _finalize_tree_ui_and_message(self, status: str, report_path: str | None):
        self.is_processing = False
        self.view.toggle_ui_for_processing(is_active=False, final_status=status)

        if status == "success" and report_path:
            self.last_report_path = report_path
            self.view.show_message("info_title", "msg_tree_done", os.path.basename(report_path))
        else:
            self.view.show_message("error_title", "msg_error_generic")

    # =========================================================================
    # UTILIDADES INTERNAS
    # =========================================================================

    def _check_destination_path(self) -> bool:
        if not self.config.get("lecturas_path"):
            self.view.show_message("info_title", "msg_select_dest")
            return False
        return True

    def _update_active_lecturas_path(self):
        if self.config.get("use_default_path", True):
            self.config["lecturas_path"] = config.DEFAULT_LECTURAS_PATH
        else:
            self.config["lecturas_path"] = self.config.get("custom_lecturas_path", config.DEFAULT_LECTURAS_PATH)

        if self.config["lecturas_path"]:
            try:
                os.makedirs(self.config["lecturas_path"], exist_ok=True)
            except Exception as e:
                utils.log_error(f"Error creando carpeta lecturas: {self.config['lecturas_path']}", e)
