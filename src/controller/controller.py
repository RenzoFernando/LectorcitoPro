import os
import threading
import time
from tkinter import filedialog

import config
import utils
from app_meta import APP_WEBSITE_URL
from controller import handlers
from i18n.translations import translate_default
from model import processor
from platform_services import get_platform_service
from view.ui import LectorcitoApp
from view.ui_constants import STATUS_CANCELLING_MIN_VISIBLE_MS

PROCESSING_UI_POLL_INTERVAL_MS = 32

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
        self._cancel_requested_at = None
        self._processing_state_lock = threading.Lock()
        self._pending_progress_update = None
        self._pending_processing_status = None
        self._processing_poll_after_id = None

        self._assign_commands()
        self._update_active_lecturas_path()

    def _assign_commands(self):
        def modal_action(callback):
            return lambda: self.view.run_modal_action(callback)

        self.view.main_buttons["selpath"].configure(
            command=modal_action(lambda: handlers.select_destination_path(self))
        )
        # Estas acciones ya bloquean la interfaz mediante su selector nativo.
        # Evitar un modal exterior permite activar correctamente el estado de procesamiento.
        self.view.main_buttons["choose"].configure(command=self.select_reading_type)
        self.view.main_buttons["create_tree"].configure(command=self.create_tree_structure)
        self.view.main_buttons["openlect"].configure(
            command=lambda: handlers.open_destination_folder(self)
        )
        self.view.main_buttons["openlast"].configure(
            command=lambda: handlers.open_last_report(self)
        )
        self.view.main_buttons["delete"].configure(
            command=modal_action(lambda: handlers.delete_all_readings(self))
        )
        self.view.btn_cancel.configure(command=self.cancel_processing)

        self.view.sidebar_buttons["ver"].configure(
            command=modal_action(lambda: handlers.show_view_config_dialog(self))
        )
        self.view.sidebar_buttons["nover"].configure(
            command=modal_action(lambda: handlers.show_no_view_config_dialog(self))
        )
        self.view.sidebar_buttons["etiqueta"].configure(
            command=modal_action(lambda: handlers.show_etiqueta_config_dialog(self))
        )
        self.view.sidebar_buttons["theme_icon"].configure(
            command=lambda: handlers.toggle_theme(self)
        )
        self.view.sidebar_buttons["traducir"].configure(
            command=lambda: handlers.toggle_language(self)
        )
        self.view.sidebar_buttons["restaurar"].configure(
            command=modal_action(lambda: handlers.restore_default_settings(self))
        )
        self.view.sidebar_buttons["perfil"].configure(
            command=modal_action(lambda: handlers.manage_profiles(self))
        )
        self.view.sidebar_buttons["github"].configure(
            command=modal_action(self.open_repository_link)
        )
        self.view.sidebar_buttons["info"].configure(command=modal_action(self.open_manual_link))
        self.view.sidebar_buttons["ajustes"].configure(
            command=modal_action(lambda: handlers.show_settings_dialog(self))
        )

    def open_repository_link(self):
        handlers.open_external_link_with_confirmation(
            parent=self.view,
            url=self.view.REPO_URL,
            title_key="dlg_external_link_title",
            message_key="msg_open_repository_confirm",
            target_label=self.view.REPO_URL,
            continue_key="btn_continue_external",
            cancel_key="btn_cancel_simple",
            platform_service=self.platform,
        )

    def open_manual_link(self):
        handlers.open_external_link_with_confirmation(
            parent=self.view,
            url=APP_WEBSITE_URL,
            title_key="dlg_external_link_title",
            message_key="msg_open_manual_confirm",
            target_label=APP_WEBSITE_URL,
            continue_key="btn_continue_external",
            cancel_key="btn_cancel_simple",
            platform_service=self.platform,
        )

    def run(self):
        # La ventana se revela desde el propio event loop, nunca durante __init__.
        # Así Tk termina de crear widgets y recursos antes del primer dibujo visible.
        utils.log_info("Iniciando event loop de interfaz.", operation="startup_ui")
        self.view.after(0, self.view.show_main_window)
        self.view.mainloop()

    # =========================================================================
    # LOGICA DE PROCESAMIENTO
    # =========================================================================

    def select_reading_type(self):
        if not self._check_destination_path():
            return

        path = self.view.run_native_modal(
            lambda: filedialog.askdirectory(
                parent=self.view,
                title=self.view._tr("btn_choose_folder"),
                initialdir=self.platform.get_dialog_initial_directory(
                    self.config.get("last_read_folder", "")
                ),
            )
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
        self._cancel_requested_at = None
        self._reset_processing_dispatch()

        self.view.toggle_ui_for_processing(is_active=True)
        self.view.set_progress(0, folder_path, None)
        self._schedule_processing_poll()

        thread = threading.Thread(
            target=self._processing_thread_target,
            args=(folder_path, self.cancel_event),
            daemon=True,
        )
        thread.start()

    def _processing_thread_target(self, folder_path: str, cancel_event: threading.Event):
        overall_status = "error"
        try:
            status, report_path = processor.generate_report(
                source_folder=folder_path,
                output_path=self.config["lecturas_path"],
                config=self.config,
                progress_callback=self._safe_progress_update,
                cancel_event=cancel_event,
            )

            if status == "success":
                self.last_report_path = report_path
            overall_status = status

        except Exception as e:
            utils.log_error(
                "Excepción en hilo de procesamiento",
                e,
                operation="processing_thread",
                file_path=folder_path,
            )
            overall_status = "error"

        with self._processing_state_lock:
            self._pending_processing_status = overall_status

    def _safe_progress_update(
        self, percentage: float, file_context: str, report_context: str | None = None
    ):
        cancel_event = self.cancel_event
        if cancel_event is None or cancel_event.is_set():
            return

        with self._processing_state_lock:
            self._pending_progress_update = (percentage, file_context, report_context)

    def _reset_processing_dispatch(self):
        if self._processing_poll_after_id is not None:
            try:
                self.view.after_cancel(self._processing_poll_after_id)
            except Exception:
                pass
            self._processing_poll_after_id = None

        with self._processing_state_lock:
            self._pending_progress_update = None
            self._pending_processing_status = None

    def _schedule_processing_poll(self):
        if self._processing_poll_after_id is not None or not self.is_processing:
            return
        self._processing_poll_after_id = self.view.after(
            PROCESSING_UI_POLL_INTERVAL_MS, self._poll_processing_state
        )

    def _poll_processing_state(self):
        self._processing_poll_after_id = None

        with self._processing_state_lock:
            progress_update = self._pending_progress_update
            self._pending_progress_update = None
            finished_status = self._pending_processing_status
            if finished_status is not None:
                self._pending_processing_status = None

        if finished_status is not None:
            if finished_status == "success" and progress_update is not None:
                self.view.set_progress(*progress_update)
            self._on_processing_finished(finished_status)
            return

        cancel_event = self.cancel_event
        if progress_update is not None and cancel_event is not None and not cancel_event.is_set():
            self.view.set_progress(*progress_update)

        if self.is_processing:
            self._schedule_processing_poll()

    def _on_processing_finished(self, status: str):
        if status == "success":
            self.view.set_progress(100)
            delay = self.view.get_min_visible_completion_delay_ms()
        elif status == "cancelled":
            delay = self._get_cancelling_visible_delay_ms()
        else:
            delay = 0

        self.view.after(delay, self._finalize_ui_and_message, status)

    def _get_cancelling_visible_delay_ms(self) -> int:
        requested_at = self._cancel_requested_at
        if requested_at is None:
            return STATUS_CANCELLING_MIN_VISIBLE_MS

        elapsed_ms = max(0.0, (time.monotonic() - requested_at) * 1000.0)
        return max(0, int(STATUS_CANCELLING_MIN_VISIBLE_MS - elapsed_ms))

    def _finalize_ui_and_message(self, status: str):
        self.is_processing = False
        self._reset_processing_dispatch()
        self.cancel_event = None
        self._cancel_requested_at = None
        self.view.toggle_ui_for_processing(is_active=False, final_status=status)

        if status == "success":
            report_name = (
                os.path.basename(self.last_report_path)
                if self.last_report_path
                else self.view._tr("default_report_name")
                if hasattr(self.view, "_tr")
                else translate_default("default_report_name")
            )
            self.view.show_message("info_title", "msg_done", report_name)
        else:
            message_map = {
                "cancelled": ("info_title", "msg_cancelled"),
                "no_files": ("info_title", "msg_no_files_found"),
                "error": ("error_title", "msg_error_generic"),
            }
            if status in message_map:
                title_key, msg_key = message_map[status]
                self.view.show_message(title_key, msg_key)

    def cancel_processing(self):
        if self.cancel_event and not self.cancel_event.is_set():
            self._cancel_requested_at = time.monotonic()
            self.cancel_event.set()
            with self._processing_state_lock:
                self._pending_progress_update = None
            self.view.set_processing_cancelling()

    # =========================================================================
    # LOGICA DE ARBOL
    # =========================================================================

    def create_tree_structure(self):
        if self.is_processing or not self._check_destination_path():
            return

        source_path = self.view.run_native_modal(
            lambda: filedialog.askdirectory(
                parent=self.view, title=self.view._tr("btn_create_tree")
            )
        )
        if not source_path:
            return

        self.is_processing = True
        self.view.toggle_ui_for_processing(
            is_active=True, mode="indeterminate", text=self.view._tr("progress_generating_tree")
        )

        thread = threading.Thread(target=self._tree_thread_target, args=(source_path,), daemon=True)
        thread.start()

    def _tree_thread_target(self, source_path: str):
        try:
            status, report_path = processor.generate_tree_report(
                source_folder=source_path,
                output_path=self.config["lecturas_path"],
                config=self.config,
            )
        except Exception as e:
            utils.log_error(
                "Excepción en hilo de árbol", e, operation="tree_thread", file_path=source_path
            )
            status, report_path = "error", None

        self.view.after(0, self._on_tree_generation_finished, status, report_path)

    def _on_tree_generation_finished(self, status: str, report_path: str | None):
        if status == "success":
            self.view.toggle_ui_for_processing(is_active=True, mode="determinate")
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
        resolved_path, using_default = self.platform.resolve_readings_path(
            self.config.get("use_default_path", True),
            self.config.get("custom_lecturas_path", ""),
            config.DEFAULT_LECTURAS_PATH,
        )
        self.config["use_default_path"] = using_default
        self.config["lecturas_path"] = resolved_path

        if self.config["lecturas_path"]:
            try:
                os.makedirs(self.config["lecturas_path"], exist_ok=True)
            except Exception as e:
                utils.log_error(
                    "Error creando carpeta lecturas.",
                    e,
                    operation="create_readings_folder",
                    file_path=self.config["lecturas_path"],
                )
