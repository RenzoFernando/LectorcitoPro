import os
import threading
import webbrowser
from tkinter import filedialog

from core import config_manager
from core.constants import REPO_URL
from core.logger import log_exception
from domain.enums import Language, ProcessStatus, Theme
from services import report_writer, tree_generator
from ui.dialogs.base_dialog import ChoiceDialog, ConfirmDialog
from ui.dialogs.config_view import TagsConfigDialog
from ui.dialogs.folder_selector import SelectFoldersDialog
from ui.main_window import MainWindow
from ui.theme_manager import toggle_theme


class AppController:
    def __init__(self):
        self.config = config_manager.load_config()
        self._update_active_lecturas_path()
        self.view = MainWindow(self.config, self)
        self.last_report_path: str | None = None
        self.is_processing = False
        self.cancel_event: threading.Event | None = None
        self._assign_commands()

    def _assign_commands(self):
        self.view.main_buttons["selpath"].configure(command=self.select_destination_path)
        self.view.main_buttons["choose"].configure(command=self.select_reading_type)
        self.view.main_buttons["create_tree"].configure(command=self.create_tree_structure)
        self.view.main_buttons["openlect"].configure(command=self.open_destination_folder)
        self.view.main_buttons["openlast"].configure(command=self.open_last_report)
        self.view.main_buttons["delete"].configure(command=self.delete_all_readings)

        self.view.sidebar_buttons["ver"].configure(command=self.show_view_config_dialog)
        self.view.sidebar_buttons["nover"].configure(command=self.show_no_view_config_dialog)
        self.view.sidebar_buttons["theme_icon"].configure(command=self.toggle_theme)
        self.view.sidebar_buttons["traducir"].configure(command=self.toggle_language)
        self.view.sidebar_buttons["restaurar"].configure(command=self.restore_default_settings)
        self.view.sidebar_buttons["github"].configure(command=lambda: webbrowser.open_new(REPO_URL))
        self.view.sidebar_buttons["info"].configure(command=self.view.show_app_info)

        self.view.btn_cancel.configure(command=self.cancel_processing)

    def run(self):
        try:
            self.view.mainloop()
        except Exception as exc:
            log_exception(exc)

    def select_reading_type(self):
        if not self._check_destination_path():
            return

        choice = ChoiceDialog.ask(
            parent=self.view,
            title=self.view._tr("dlg_read_type_title"),
            message=self.view._tr("dlg_read_type_prompt"),
            option1_text=self.view._tr("dlg_read_type_op1"),
            option2_text=self.view._tr("dlg_read_type_op2"),
            option1_value="single",
            option2_value="multiple",
        )

        if choice == "single":
            self.select_single_folder_to_read()
        elif choice == "multiple":
            self.select_multiple_folders_to_read()

    def select_single_folder_to_read(self):
        path = filedialog.askdirectory(title=self.view._tr("btn_choose_folder"), initialdir=self.config.get("last_read_folder", ""))
        if path:
            self.config["last_read_folder"] = path
            self.start_batch_processing([path])

    def select_multiple_folders_to_read(self):
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
        overall_status: str = ProcessStatus.SUCCESS.value
        reports_generated = 0
        total_folders = len(folder_paths)

        for i, folder_path in enumerate(folder_paths):
            if cancel_event.is_set():
                overall_status = ProcessStatus.CANCELLED.value
                break

            folder_name = os.path.basename(folder_path)
            context_prefix = f"[{i + 1}/{total_folders}] " if total_folders > 1 else ""
            self.view.after(0, self.view.set_progress, 0, f"{context_prefix}{folder_name}")

            status, report_path = report_writer.generate_report(
                source_folder=folder_path,
                output_path=self.config["lecturas_path"],
                config=self.config,
                progress_callback=self._safe_progress_update,
                cancel_event=cancel_event,
            )

            if status == ProcessStatus.SUCCESS.value:
                self.last_report_path = report_path
                reports_generated += 1
            elif status in [ProcessStatus.ERROR.value, ProcessStatus.CANCELLED.value, ProcessStatus.NO_FILES.value]:
                overall_status = status
                break

        self.view.after(0, self._on_processing_finished, overall_status, reports_generated)

    def _on_processing_finished(self, status: str, reports_generated: int = 0):
        if status == ProcessStatus.SUCCESS.value:
            self.view.set_progress(100)
        delay = 400 if status == ProcessStatus.SUCCESS.value else 0
        self.view.after(delay, self._finalize_ui_and_message, status, reports_generated)

    def _finalize_ui_and_message(self, status: str, reports_generated: int):
        self.is_processing = False
        self.cancel_event = None
        self.view.toggle_ui_for_processing(is_active=False)

        if status == ProcessStatus.SUCCESS.value:
            if reports_generated > 1:
                self.view.show_message("info_title", "msg_batch_done", reports_generated)
            elif reports_generated == 1:
                self.view.show_message("info_title", "msg_done")
        else:
            message_map = {
                ProcessStatus.CANCELLED.value: ("info_title", "msg_cancelled"),
                ProcessStatus.NO_FILES.value: ("info_title", "msg_no_files_found"),
                ProcessStatus.ERROR.value: ("error_title", "msg_error_generic"),
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

        choice = ChoiceDialog.ask(
            parent=self.view,
            title=self.view._tr("dlg_tree_choice_title"),
            message=self.view._tr("dlg_tree_choice_prompt"),
            option1_text=self.view._tr("dlg_tree_op1"),
            option2_text=self.view._tr("dlg_tree_op2"),
            option1_value="complete",
            option2_value="filtered",
        )
        if not choice:
            return

        source_path = filedialog.askdirectory(title=self.view._tr("btn_create_tree"))
        if not source_path:
            return

        self.is_processing = True
        self.view.toggle_ui_for_processing(is_active=True, mode="indeterminate", text=self.view._tr("progress_generating_tree"))

        thread = threading.Thread(target=self._tree_thread_target, args=(source_path, choice == "filtered"), daemon=True)
        thread.start()

    def _tree_thread_target(self, source_path: str, use_filters: bool):
        status, report_path = tree_generator.generate_tree_report(
            source_folder=source_path, output_path=self.config["lecturas_path"], use_config=use_filters, config=self.config
        )
        self.view.after(0, self._on_tree_generation_finished, status, report_path)

    def _on_tree_generation_finished(self, status: str, report_path: str | None):
        if status == ProcessStatus.SUCCESS.value:
            self.view.toggle_ui_for_processing(is_active=True, mode="determinate")
            self.view.set_progress(100, self.view._tr("progress_done"))

        delay = 400 if status == ProcessStatus.SUCCESS.value else 0
        self.view.after(delay, self._finalize_tree_ui_and_message, status, report_path)

    def _finalize_tree_ui_and_message(self, status: str, report_path: str | None):
        self.is_processing = False
        self.view.toggle_ui_for_processing(is_active=False)

        if status == ProcessStatus.SUCCESS.value and report_path:
            self.last_report_path = report_path
            self.view.show_message("info_title", "msg_tree_done", os.path.basename(report_path))
        else:
            self.view.show_message("error_title", "msg_error_generic")

    def select_destination_path(self):
        choice = ChoiceDialog.ask(
            parent=self.view,
            title=self.view._tr("dlg_dest_choice_title"),
            message=self.view._tr("dlg_dest_choice_prompt"),
            option1_text=self.view._tr("dlg_dest_choice_op1"),
            option2_text=self.view._tr("dlg_dest_choice_op2"),
            option1_value="default",
            option2_value="custom",
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

    def show_view_config_dialog(self):
        current_folders = self.config.get("etiquetas_carpetas_importantes", [])
        current_files = self.config.get("etiquetas_extensiones_incluidas", [])

        result = TagsConfigDialog.get_input(
            parent=self.view,
            title=self.view._tr("dlg_ver_title"),
            folders_prompt=self.view._tr("dlg_ver_folder_prompt"),
            initial_folders=current_folders,
            files_prompt=self.view._tr("dlg_ver_file_prompt"),
            initial_files=current_files,
        )

        if result is not None:
            new_folders, new_files = result
            for tag in new_files:
                if not tag["nombre"].startswith("."):
                    tag["nombre"] = f".{tag['nombre']}"

            self.config["etiquetas_carpetas_importantes"] = new_folders
            self.config["etiquetas_extensiones_incluidas"] = new_files
            self.save_preferences_silent()

    def show_no_view_config_dialog(self):
        current_folders = self.config.get("etiquetas_carpetas_excluidas", [])
        current_files = self.config.get("etiquetas_archivos_excluidos", [])

        result = TagsConfigDialog.get_input(
            parent=self.view,
            title=self.view._tr("dlg_nover_title"),
            folders_prompt=self.view._tr("dlg_nover_folder_prompt"),
            initial_folders=current_folders,
            files_prompt=self.view._tr("dlg_nover_file_prompt"),
            initial_files=current_files,
        )

        if result is not None:
            new_folders, new_files = result
            self.config["etiquetas_carpetas_excluidas"] = new_folders
            self.config["etiquetas_archivos_excluidos"] = new_files
            self.save_preferences_silent()

    def save_preferences_silent(self):
        config_manager.save_config(self.config)

    def toggle_theme(self):
        self.view.current_theme = toggle_theme(self.view.current_theme)
        self.config["theme"] = self.view.current_theme
        self.view.apply_theme()
        self.save_preferences_silent()

    def toggle_language(self):
        self.view.lang = Language.EN.value if self.view.lang == Language.ES.value else Language.ES.value
        self.view.translator.lang = self.view.lang
        self.config["language"] = self.view.lang
        self.view.update_ui_texts()
        self.save_preferences_silent()

    def restore_default_settings(self):
        if ConfirmDialog.ask(self.view, self.view._tr("confirm_restore_title"), self.view._tr("confirm_restore_prompt")):
            config_manager.delete_config_file()
            self.config = config_manager.load_config()
            self._update_active_lecturas_path()
            self.view.lang = self.config["language"]
            self.view.translator.lang = self.view.lang
            self.view.current_theme = self.config["theme"]
            self.view.update_ui_texts()
            self.view.apply_theme()
            self.save_preferences_silent()
            self.view.show_message("info_title", "msg_restore_success")

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
                import shutil

                shutil.rmtree(path)
                os.makedirs(path, exist_ok=True)
                self.view.show_message("info_title", "msg_delete_success", os.path.basename(path))
            except Exception as e:
                self.view.show_message("error_title", "msg_delete_error", str(e))

    def _update_active_lecturas_path(self):
        if self.config.get("use_default_path", True):
            self.config["lecturas_path"] = config_manager.DEFAULT_LECTURAS_PATH
        else:
            self.config["lecturas_path"] = self.config.get("custom_lecturas_path", config_manager.DEFAULT_LECTURAS_PATH)

        if self.config["lecturas_path"]:
            os.makedirs(self.config["lecturas_path"], exist_ok=True)
