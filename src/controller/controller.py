# src/controller/controller.py
import os
import shutil
import threading
import webbrowser
from tkinter import filedialog

import config
from model import processor
from view.ui import LectorcitoApp
from controller import handlers


class LectorcitoController:

    def __init__(self):
        self.config = config.load_config()
        self.view = LectorcitoApp(self.config, self)
        self.last_report_path = None
        self.is_processing = False
        self.cancel_event = None
        self._assign_commands()

    def _assign_commands(self):
        self.view.main_buttons["selpath"].configure(command=lambda: handlers.select_destination_path(self))
        self.view.main_buttons["choose"].configure(command=self.select_reading_type)
        self.view.main_buttons["create_tree"].configure(command=self.create_tree_structure)
        self.view.main_buttons["openlect"].configure(command=lambda: handlers.open_destination_folder(self))
        self.view.main_buttons["openlast"].configure(command=lambda: handlers.open_last_report(self))
        self.view.main_buttons["delete"].configure(command=lambda: handlers.delete_all_readings(self))

        self.view.sidebar_buttons["ver"].configure(command=lambda: handlers.show_view_config_dialog(self))
        self.view.sidebar_buttons["nover"].configure(command=lambda: handlers.show_no_view_config_dialog(self))
        #etiqueta button para media_extensions config
        self.view.sidebar_buttons["theme_icon"].configure(command=lambda: handlers.toggle_theme(self))
        self.view.sidebar_buttons["traducir"].configure(command=lambda: handlers.toggle_language(self))
        self.view.sidebar_buttons["restaurar"].configure(command=lambda: handlers.restore_default_settings(self))
        self.view.sidebar_buttons["github"].configure(command=lambda: webbrowser.open_new(self.view.REPO_URL))
        #perfil button para tener perfiles de trabajo
        self.view.sidebar_buttons["info"].configure(command=self.view.show_app_info)

        self.view.btn_cancel.configure(command=self.cancel_processing)

    def run(self):
        self.view.mainloop()

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

    def select_single_folder_to_read(self):
        path = filedialog.askdirectory(
            title=self.view._tr("btn_choose_folder"),
            initialdir=self.config.get("last_read_folder", "")
        )
        if path:
            self.config["last_read_folder"] = path
            self.start_batch_processing([path])

    def select_multiple_folders_to_read(self):
        from view.dialogs import SelectFoldersDialog
        paths = SelectFoldersDialog.ask(parent=self.view, title=self.view._tr("dlg_multi_folder_title"))

        if paths:
            self.config["last_read_folder"] = paths[0]
            self.start_batch_processing(paths)

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

    def _on_processing_finished(self, status: str, reports_generated: int = 0):
        if status == "success":
            self.view.set_progress(100)

        delay = self.view.get_min_visible_completion_delay_ms() if status == "success" else 0
        self.view.after(delay, self._finalize_ui_and_message, status, reports_generated)

    def _finalize_ui_and_message(self, status: str, reports_generated: int):
        self.is_processing = False
        self.cancel_event = None
        self.view.toggle_ui_for_processing(is_active=False, final_status=status)

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

    def _safe_progress_update(self, percentage: float, file_context: str):
        self.view.after(0, self.view.set_progress, percentage, file_context)

    def cancel_processing(self):
        if self.cancel_event:
            self.cancel_event.set()

    def _check_destination_path(self) -> bool:
        if not self.config.get("lecturas_path"):
            self.view.show_message("info_title", "msg_select_dest")
            return False
        return True

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

    def _tree_thread_target(self, source_path: str, use_filters: bool):
        status, report_path = processor.generate_tree_report(
            source_folder=source_path, output_path=self.config["lecturas_path"], use_config=use_filters,
            config=self.config
        )
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

    def _update_active_lecturas_path(self):
        if self.config.get("use_default_path", True):
            self.config["lecturas_path"] = config.DEFAULT_LECTURAS_PATH
        else:
            self.config["lecturas_path"] = self.config.get("custom_lecturas_path", config.DEFAULT_LECTURAS_PATH)

        if self.config["lecturas_path"]:
            os.makedirs(self.config["lecturas_path"], exist_ok=True)
