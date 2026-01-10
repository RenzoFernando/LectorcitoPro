from __future__ import annotations

import os
import shutil
import threading
import webbrowser

from ...config import store as config_store, save_config
from ...features.reports.ui.controller import ReportsUIController
from ...features.settings.application.update_filters import normalize_extension_tags
from ...features.settings.application.update_language import toggle_language
from ...features.settings.application.update_theme import toggle_theme
from ...features.tree.ui.controller import TreeUIController
from ...infra.os_integration.file_dialogs import ask_directory
from ...infra.os_integration.open_path import open_path
from .main_window import LectorcitoApp
from ..dialogs.choice import ChoiceDialog
from ..dialogs.confirm import ConfirmDialog
from ..dialogs.select_folders import MultiFolderSelectDialog
from ..dialogs.tags_config import TagsConfigDialog


class LectorcitoController:
    def __init__(self):
        self.config = config_store.load_config()

        # --- FIX: Inicializar estado ANTES de crear la vista ---
        self.is_processing = False
        self.cancel_event: threading.Event | None = None
        self.last_report_path: str | None = None
        # -------------------------------------------------------

        # Ahora sí es seguro crear la vista, pues ya existe self.is_processing
        self.view = LectorcitoApp(self.config, self)

        # Controladores por feature (adaptadores)
        self.reports = ReportsUIController()
        self.tree = TreeUIController()

        # Asignar comandos finales
        self._assign_commands()

        # Evita abrir la misma ventana varias veces por clicks rápidos
        self._dialog_lock: set[str] = set()

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
        self.view.sidebar_buttons["github"].configure(command=lambda: webbrowser.open_new(self.view.REPO_URL))
        self.view.sidebar_buttons["info"].configure(command=self.view.show_app_info)

        self.view.btn_cancel.configure(command=self.cancel_processing)

    def run(self):
        try:
            self.view.mainloop()
        except KeyboardInterrupt:
            # Si se corta con Ctrl+C, intentamos cerrar limpio para evitar errores de Tcl.
            try:
                if self.view.winfo_exists():
                    self.view._safe_destroy()
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Persistencia / paths
    # -------------------------------------------------------------------------
    def _update_active_lecturas_path(self):
        if self.config.get("use_default_path", True):
            self.config["lecturas_path"] = config_store.DEFAULT_LECTURAS_PATH
        else:
            self.config["lecturas_path"] = self.config.get("custom_lecturas_path") or config_store.DEFAULT_LECTURAS_PATH

        try:
            os.makedirs(self.config["lecturas_path"], exist_ok=True)
        except Exception:
            pass

    def _save_preferences_silent(self):
        try:
            config_store.save_config(self.config)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Selección de destino
    # -------------------------------------------------------------------------
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
            path = ask_directory(title=self.view._tr("btn_sel_lecturas"), parent=self.view)
            if path:
                # Misma lógica que el original: crea subcarpeta "Lecturas" dentro del destino seleccionado
                custom_path = os.path.join(path, "Lecturas")
                self.config.update({"use_default_path": False, "custom_lecturas_path": custom_path})
                self.view.show_message("info_title", "dest_set_custom_msg", custom_path)

        self._update_active_lecturas_path()
        self._save_preferences_silent()

    def _check_destination_path(self) -> bool:
        p = self.config.get("lecturas_path")
        if not p:
            self.view.show_message("info_title", "msg_select_dest")
            return False
        return True

    # -------------------------------------------------------------------------
    # Lectura (single/multiple)
    # -------------------------------------------------------------------------
    def select_reading_type(self):
        """Abre el selector de tipo de lectura."""
        if "select_reading_type" in self._dialog_lock:
            return
        self._dialog_lock.add("select_reading_type")
        try:
            choice = ChoiceDialog.ask(
                parent=self.view,
                title=self.view._tr("dlg_read_type_title"),
                message=self.view._tr("dlg_read_type_prompt"),
                option1_text=self.view._tr("dlg_read_type_op1"),
                option2_text=self.view._tr("dlg_read_type_op2"),
                option1_value="folder",
                option2_value="multi"
            )

            # SOLUCIÓN DEFINITIVA:
            # Usamos 'after' para desacoplar el cierre del diálogo 1
            # de la apertura del diálogo 2. Esto evita la condición de carrera.
            if choice == "folder":
                self.view.after(150, self.select_single_folder_to_read)
            elif choice == "multi":
                self.view.after(150, self.select_multiple_folders_to_read)

        finally:
            self._dialog_lock.discard("select_reading_type")

    def select_single_folder_to_read(self):
        folder_path = ask_directory(title=self.view._tr("btn_choose_folder"), parent=self.view)
        if folder_path:
            self.start_batch_processing([folder_path])

    def select_multiple_folders_to_read(self):
        paths = MultiFolderSelectDialog.ask(self.view, self.config.get("last_read_folder", ""))
        if paths:
            self.config["last_read_folder"] = paths[0]
            self._save_preferences_silent()
            self.start_batch_processing(paths)

    def start_batch_processing(self, folder_paths: list[str]):
        if self.is_processing:
            return

        if len(folder_paths) > 1:
            self.view.show_message("info_title", "msg_batch_started", len(folder_paths))

        self.is_processing = True
        self.cancel_event = threading.Event()
        self.view.toggle_ui_for_processing(is_active=True)

        thread = threading.Thread(
            target=self._batch_processing_thread_target,
            args=(folder_paths, self.cancel_event),
            daemon=True,
        )
        thread.start()

    def _batch_processing_thread_target(self, folder_paths: list[str], cancel_event: threading.Event):
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

            status, report_path = self.reports.generate(
                source_folder=folder_path,
                output_path=self.config["lecturas_path"],
                config=self.config,
                progress_callback=self._safe_progress_update,
                cancel_event=cancel_event,
            )

            if status == "success":
                reports_generated += 1
                self.last_report_path = report_path
            elif status in ["error", "cancelled", "no_files"]:
                overall_status = status
                break

        self.view.after(0, self._on_processing_finished, overall_status, reports_generated)

    def _safe_progress_update(self, progress: float, status_text: str):
        if not self.cancel_event or self.cancel_event.is_set():
            return
        self.view.after(0, self.view.set_progress, progress, status_text)

    def cancel_processing(self):
        if self.is_processing and self.cancel_event:
            self.cancel_event.set()

    def _on_processing_finished(self, status: str, reports_generated: int = 0):
        if status == "success":
            self.view.set_progress(100)

        delay = 400 if status == "success" else 0
        self.view.after(delay, self._finalize_ui_and_message, status, reports_generated)

    def _finalize_ui_and_message(self, status: str, reports_generated: int):
        self.is_processing = False
        self.cancel_event = None
        self.view.toggle_ui_for_processing(is_active=False)

        if status == "success":
            if reports_generated > 1:
                self.view.show_message("info_title", "msg_batch_done", reports_generated)
            else:
                self.view.show_message("info_title", "msg_done")
            return

        message_map = {
            "cancelled": ("info_title", "msg_cancelled"),
            "no_files": ("info_title", "msg_no_files_found"),
            "error": ("error_title", "msg_error_generic"),
        }
        title_key, msg_key = message_map.get(status, ("error_title", "msg_error_generic"))
        self.view.show_message(title_key, msg_key)

    # -------------------------------------------------------------------------
    # Árbol
    # -------------------------------------------------------------------------
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

        source_path = ask_directory(title=self.view._tr("btn_create_tree"), parent=self.view)
        if not source_path:
            return

        self.is_processing = True
        self.view.toggle_ui_for_processing(
            is_active=True,
            mode="indeterminate",
            text=self.view._tr("progress_generating_tree"),
        )

        thread = threading.Thread(
            target=self._tree_thread_target,
            args=(source_path, choice == "filtered"),
            daemon=True,
        )
        thread.start()

    def _tree_thread_target(self, source_path: str, use_filters: bool):
        status, report_path = self.tree.generate(
            source_folder=source_path,
            output_path=self.config["lecturas_path"],
            use_config=use_filters,
            config=self.config,
        )
        self.view.after(0, self._on_tree_generation_finished, status, report_path)

    def _on_tree_generation_finished(self, status: str, report_path: str | None):
        if status == "success":
            self.view.toggle_ui_for_processing(is_active=True, mode="determinate")
            self.view.set_progress(100, self.view._tr("progress_done"))

        delay = 400 if status == "success" else 0
        self.view.after(delay, self._finalize_tree_ui_and_message, status, report_path)

    def _finalize_tree_ui_and_message(self, status: str, report_path: str | None):
        self.is_processing = False
        self.view.toggle_ui_for_processing(is_active=False)

        if status == "success" and report_path:
            self.last_report_path = report_path
            self.view.show_message("info_title", "msg_tree_done", os.path.basename(report_path))
        else:
            self.view.show_message("error_title", "msg_error_generic")

    # -------------------------------------------------------------------------
    # Configuración (tags)
    # -------------------------------------------------------------------------
    def show_view_config_dialog(self):
        """Abre el diálogo de configuración 'Ver'."""
        if "view_config" in self._dialog_lock:
            return
        self._dialog_lock.add("view_config")
        try:
            # FIX: Use correct keys from defaults.py
            current_folders = self.config.get("etiquetas_carpetas_importantes", [])
            current_files = self.config.get("etiquetas_extensiones_incluidas", [])

            # FIX: Call with new signature (folders + files)
            result = TagsConfigDialog.get_input(
                parent=self.view,
                title=self.view._tr("dlg_ver_title"),
                folders_prompt=self.view._tr("dlg_ver_folder_prompt"),
                initial_folders=current_folders,
                files_prompt=self.view._tr("dlg_ver_file_prompt"),
                initial_files=current_files
            )

            if result is not None:
                new_folders, new_files = result
                # Update config
                self.config["etiquetas_carpetas_importantes"] = new_folders
                # Normalize extensions (ensure they start with .)
                self.config["etiquetas_extensiones_incluidas"] = self.reports.normalize_extensions(new_files)

                config_store.save_config(self.config)
                self.view.show_message("info_title", "msg_done")
        finally:
            self._dialog_lock.discard("view_config")

    def show_no_view_config_dialog(self):
        """Abre el diálogo de configuración 'No ver'."""
        if "no_view_config" in self._dialog_lock:
            return
        self._dialog_lock.add("no_view_config")
        try:
            # FIX: Use correct keys from defaults.py
            current_folders = self.config.get("etiquetas_carpetas_excluidas", [])
            current_files = self.config.get("etiquetas_archivos_excluidos", [])

            # FIX: Call with new signature
            result = TagsConfigDialog.get_input(
                parent=self.view,
                title=self.view._tr("dlg_nover_title"),
                folders_prompt=self.view._tr("dlg_nover_folder_prompt"),
                initial_folders=current_folders,
                files_prompt=self.view._tr("dlg_nover_file_prompt"),
                initial_files=current_files
            )

            if result is not None:
                new_folders, new_files = result
                self.config["etiquetas_carpetas_excluidas"] = new_folders
                self.config["etiquetas_archivos_excluidos"] = new_files

                config_store.save_config(self.config)
                self.view.show_message("info_title", "msg_done")
        finally:
            self._dialog_lock.discard("no_view_config")

    def toggle_theme(self):
        self.view.current_theme = toggle_theme(self.view.current_theme)
        self.config["theme"] = self.view.current_theme
        self.view.apply_theme()
        self._save_preferences_silent()

    def toggle_language(self):
        self.view.lang = toggle_language(self.view.lang)
        self.config["language"] = self.view.lang
        self.view.update_ui_texts()
        self._save_preferences_silent()

    # -------------------------------------------------------------------------
    # Restaurar / abrir / eliminar
    # -------------------------------------------------------------------------
    def restore_default_settings(self):
        confirm = ConfirmDialog.ask(
            self.view,
            self.view._tr("confirm_restore_title"),
            self.view._tr("confirm_restore_prompt"),
        )
        if not confirm:
            return

        config_store.delete_config_file()
        self.config = config_store.load_config()

        self._update_active_lecturas_path()
        self.view.config = self.config
        self.view.lang = self.config.get("language", "es")
        self.view.current_theme = self.config.get("theme", "Light")
        self.view.update_ui_texts()
        self.view.apply_theme()
        self._save_preferences_silent()
        self.view.show_message("info_title", "msg_restore_success")

    def open_destination_folder(self):
        path = self.config.get("lecturas_path")
        if path and os.path.isdir(path):
            open_path(path)
        else:
            self.view.show_message("info_title", "msg_select_dest")

    def open_last_report(self):
        if self.last_report_path and os.path.isfile(self.last_report_path):
            open_path(self.last_report_path)
        else:
            self.view.show_message("info_title", "msg_no_report_yet")

    def delete_all_readings(self):
        path = self.config.get("lecturas_path")
        if not (path and os.path.isdir(path)):
            self.view.show_message("info_title", "msg_select_dest")
            return

        confirm = ConfirmDialog.ask(
            self.view,
            self.view._tr("confirm_del_title"),
            self.view._tr("confirm_del_prompt"),
        )
        if not confirm:
            return

        try:
            shutil.rmtree(path)
            os.makedirs(path, exist_ok=True)
            self.view.show_message("info_title", "msg_delete_success", os.path.basename(path))
        except Exception as e:
            self.view.show_message("error_title", "msg_delete_error", str(e))
