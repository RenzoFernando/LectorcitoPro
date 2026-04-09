import os
import sys
import shutil
import webbrowser
import subprocess
import customtkinter
from tkinter import filedialog
import win32com.client

import config
from app_meta import APP_DISPLAY_NAME, APP_NAME_INTERNAL
from file_rules import canonical_file_rule, normalize_file_rule_list, normalize_file_tag_list
from view.dialogs import ConfirmDialog, ChoiceDialog, ExternalLinkDialog, MessageDialog
from view.tags_dialog import TagsConfigDialog
from view.profiles_dialog import ProfilesDialog
from view.settings_dialog import SettingsDialog
from view.ui_constants import PROFILE_SWITCH_FADE_DELAY_MS, RESTORE_FADE_DELAY_MS


INSTALL_MARKER_FILE = ".lectorcito_installed"


def _normalize_exe_path(path):
    return str(path).strip().replace('"', '') if path is not None else ""


def _normalize_compare_path(path):
    clean_path = _normalize_exe_path(path)
    if not clean_path:
        return ""
    try:
        return os.path.normcase(os.path.abspath(clean_path))
    except Exception:
        return os.path.normcase(clean_path)


def _get_runtime_exe_path():
    if not getattr(sys, 'frozen', False):
        return ""
    exe_path = os.path.abspath(sys.executable)
    if not os.path.isfile(exe_path):
        return ""
    if not exe_path.lower().endswith(".exe"):
        return ""
    return exe_path


def _get_install_marker_path(exe_path=""):
    resolved_exe_path = _normalize_exe_path(exe_path) or _get_runtime_exe_path()
    if not resolved_exe_path:
        return ""
    return os.path.join(os.path.dirname(resolved_exe_path), INSTALL_MARKER_FILE)


def _is_installed_runtime(exe_path=""):
    marker_path = _get_install_marker_path(exe_path)
    return bool(marker_path and os.path.isfile(marker_path))


def _get_installed_exe_path():
    runtime_exe_path = _get_runtime_exe_path()
    if runtime_exe_path and _is_installed_runtime(runtime_exe_path):
        return runtime_exe_path
    return ""


def _get_effective_exe_path(controller, provided_path=None, persist_changes=True, allow_script_fallback=False):
    manual_path = _normalize_exe_path(provided_path)
    saved_path = _normalize_exe_path(controller.config.get("custom_exe_path", ""))
    runtime_exe_path = _get_runtime_exe_path()
    installed_exe_path = _get_installed_exe_path()

    if manual_path:
        return manual_path

    if installed_exe_path:
        if persist_changes and _normalize_compare_path(saved_path) != _normalize_compare_path(installed_exe_path):
            controller.config["custom_exe_path"] = installed_exe_path
            save_preferences_silent(controller)
        return installed_exe_path

    if saved_path and runtime_exe_path and _normalize_compare_path(saved_path) == _normalize_compare_path(runtime_exe_path):
        saved_path = ""
        if persist_changes and controller.config.get("custom_exe_path", ""):
            controller.config["custom_exe_path"] = ""
            save_preferences_silent(controller)

    if saved_path:
        return saved_path

    if allow_script_fallback and not getattr(sys, 'frozen', False):
        return _normalize_exe_path(sys.executable)

    return ""


def _get_programs_folder(shell):
    start_menu = shell.SpecialFolders("StartMenu")
    programs_folder = os.path.join(start_menu, "Programs")
    if not os.path.exists(programs_folder):
        try:
            os.makedirs(programs_folder)
        except Exception:
            programs_folder = start_menu
    return programs_folder


# =============================================================================
# MANEJADORES DE RUTAS Y ARCHIVOS
# =============================================================================

def select_destination_path(controller):
    choice = ChoiceDialog.ask(
        parent=controller.view,
        title=controller.view._tr("dlg_dest_choice_title"),
        message=controller.view._tr("dlg_dest_choice_prompt"),
        option1_text=controller.view._tr("dlg_dest_choice_op1"),
        option2_text=controller.view._tr("dlg_dest_choice_op2"),
        option1_value="default",
        option2_value="custom"
    )

    if choice == "default":
        controller.config["use_default_path"] = True
        controller.view.show_message("info_title", "dest_set_default_msg")

    elif choice == "custom":
        path = filedialog.askdirectory(title=controller.view._tr("btn_sel_lecturas"))
        if path:
            custom_path = os.path.join(path, "Lecturas")
            controller.config.update({"use_default_path": False, "custom_lecturas_path": custom_path})
            controller.view.show_message("info_title", "dest_set_custom_msg", custom_path)

    controller._update_active_lecturas_path()
    save_preferences_silent(controller)


def open_destination_folder(controller):
    path = controller.config.get("lecturas_path")
    if path and os.path.isdir(path):
        webbrowser.open(os.path.realpath(path))
    else:
        controller.view.show_message("info_title", "msg_select_dest")


def _get_latest_report_path_from_active_folder(controller):
    path = controller.config.get("lecturas_path")
    if not path:
        return ""

    try:
        active_folder = os.path.abspath(path)
    except Exception:
        active_folder = path

    if not os.path.isdir(active_folder):
        controller.last_report_path = None
        return ""

    valid_extensions = {".txt", ".md"}
    valid_prefixes = ("reporte_", "arbol_")
    latest_report = None

    try:
        with os.scandir(active_folder) as entries:
            for entry in entries:
                if not entry.is_file():
                    continue

                filename = entry.name
                extension = os.path.splitext(filename)[1].lower()
                if extension not in valid_extensions:
                    continue
                if not filename.lower().startswith(valid_prefixes):
                    continue

                try:
                    stats = entry.stat()
                    sort_key = (stats.st_mtime, stats.st_ctime, filename.lower())
                except OSError:
                    continue

                if latest_report is None or sort_key > latest_report[0]:
                    latest_report = (sort_key, entry.path)
    except OSError:
        controller.last_report_path = None
        return ""

    controller.last_report_path = latest_report[1] if latest_report else None
    return controller.last_report_path or ""


def open_last_report(controller):
    active_path = controller.config.get("lecturas_path")
    if not active_path:
        controller.view.show_message("info_title", "msg_select_dest")
        return

    latest_report_path = _get_latest_report_path_from_active_folder(controller)
    if latest_report_path and os.path.isfile(latest_report_path):
        webbrowser.open(os.path.realpath(latest_report_path))
    else:
        controller.view.show_message("info_title", "msg_no_report_yet")


def delete_all_readings(controller):
    path = controller.config.get("lecturas_path")
    if not (path and os.path.isdir(path)):
        controller.view.show_message("info_title", "msg_select_dest")
        return

    if ConfirmDialog.ask(controller.view, controller.view._tr("confirm_del_title"),
                         controller.view._tr("confirm_del_prompt")):
        try:
            shutil.rmtree(path)
            os.makedirs(path, exist_ok=True)
            controller.last_report_path = None
            controller.view.show_message("info_title", "msg_delete_success", os.path.basename(path))
        except Exception as e:
            controller.view.show_message("error_title", "msg_delete_error", str(e))


# =============================================================================
# MANEJADORES DE FILTROS (TAGS)
# =============================================================================

def show_view_config_dialog(controller):
    current_folders = controller.config.get("etiquetas_carpetas_importantes", [])
    current_files = controller.config.get("etiquetas_extensiones_incluidas", [])

    excl_folders = controller.config.get("etiquetas_carpetas_excluidas", [])
    excl_files = controller.config.get("etiquetas_archivos_excluidos", [])
    media_exts = controller.config.get("media_extensions", [])

    dialog = controller.view.get_view_dialog()
    dialog.load_state(
        title=controller.view._tr("dlg_ver_title"),
        folders_prompt=controller.view._tr("dlg_ver_folder_prompt"),
        initial_folders=current_folders,
        files_prompt=controller.view._tr("dlg_ver_file_prompt"),
        initial_files=current_files,
        allow_autodetect=True,
        excluded_folders=excl_folders,
        excluded_files=excl_files,
        media_extensions=media_exts
    )
    dialog.present()
    result = dialog.wait_result()

    if result is not None:
        new_folders, new_files = result
        controller.config["etiquetas_carpetas_importantes"] = new_folders
        controller.config["etiquetas_extensiones_incluidas"] = normalize_file_tag_list(new_files)
        save_preferences_silent(controller)


def show_no_view_config_dialog(controller):
    current_folders = controller.config.get("etiquetas_carpetas_excluidas", [])
    current_files = controller.config.get("etiquetas_archivos_excluidos", [])
    use_gitignore_exclusions = controller.config.get("use_gitignore_exclusions", False)

    dialog = controller.view.get_no_view_dialog()
    dialog.load_state(
        title=controller.view._tr("dlg_nover_title"),
        folders_prompt=controller.view._tr("dlg_nover_folder_prompt"),
        initial_folders=current_folders,
        files_prompt=controller.view._tr("dlg_nover_file_prompt"),
        initial_files=current_files,
        extra_checkbox_text=controller.view._tr("chk_use_gitignore"),
        extra_checkbox_value=use_gitignore_exclusions
    )
    dialog.present()
    result = dialog.wait_result()

    if result is not None:
        new_folders, new_files, use_gitignore_exclusions = result
        controller.config["etiquetas_carpetas_excluidas"] = new_folders
        controller.config["etiquetas_archivos_excluidos"] = normalize_file_tag_list(new_files)
        controller.config["use_gitignore_exclusions"] = bool(use_gitignore_exclusions)
        save_preferences_silent(controller)


def show_etiqueta_config_dialog(controller):
    tags_stored = controller.config.get("etiquetas_multimedia_config", [])

    if not tags_stored:
        raw_exts = controller.config.get("media_extensions", [])
        current_files = [{"nombre": x, "estado": "activo"} for x in raw_exts]
    else:
        current_files = tags_stored

    view_exts = {canonical_file_rule(t["nombre"]) for t in controller.config.get("etiquetas_extensiones_incluidas", [])}
    no_view_items = {canonical_file_rule(t["nombre"]) for t in controller.config.get("etiquetas_archivos_excluidos", [])}
    forbidden_set = view_exts.union(no_view_items)

    dialog = controller.view.get_media_dialog()
    dialog.load_state(
        title=controller.view._tr("dlg_etiqueta_title"),
        folders_prompt=None,
        initial_folders=None,
        files_prompt=controller.view._tr("dlg_etiqueta_file_prompt"),
        initial_files=current_files,
        forbidden_items=forbidden_set
    )
    dialog.present()
    result = dialog.wait_result()

    if result is not None:
        _, new_files = result
        normalized_files = normalize_file_tag_list(new_files)
        controller.config["etiquetas_multimedia_config"] = normalized_files

        active_media_exts = [t["nombre"] for t in normalized_files if t["estado"] == "activo"]
        controller.config["media_extensions"] = normalize_file_rule_list(active_media_exts)

        save_preferences_silent(controller)


# =============================================================================
# MANEJADORES DE AJUSTES Y SHORTCUTS
# =============================================================================

def show_settings_dialog(controller):
    current_ext = controller.config.get("report_extension", ".txt")
    current_exe = _get_effective_exe_path(controller, persist_changes=True, allow_script_fallback=False)

    def on_save(new_ext, new_exe_path):
        _update_settings_values(controller, new_ext, new_exe_path)

    def on_shortcut(mode, exe_path_input, parent_window=None):
        _create_system_shortcut(controller, mode, exe_path_input, parent_window)

    dialog = controller.view.get_settings_dialog()
    dialog.load_state(
        current_extension=current_ext,
        current_exe_path=current_exe,
        on_save_callback=on_save,
        on_shortcut_callback=on_shortcut
    )
    dialog.present()
    dialog.wait_result()


def _update_settings_values(controller, new_ext, new_exe_path):
    changed = False

    if new_ext in [".txt", ".md"] and controller.config.get("report_extension") != new_ext:
        controller.config["report_extension"] = new_ext
        changed = True

    clean_path = _normalize_exe_path(new_exe_path)
    installed_exe_path = _get_installed_exe_path()

    if installed_exe_path:
        clean_path = installed_exe_path

    current_saved_path = _normalize_exe_path(controller.config.get("custom_exe_path", ""))
    runtime_exe_path = _get_runtime_exe_path()

    if clean_path and runtime_exe_path and not installed_exe_path:
        if _normalize_compare_path(clean_path) == _normalize_compare_path(runtime_exe_path):
            clean_path = ""

    if _normalize_compare_path(current_saved_path) != _normalize_compare_path(clean_path):
        controller.config["custom_exe_path"] = clean_path
        changed = True

    if changed:
        save_preferences_silent(controller)


def _create_system_shortcut(controller, mode, user_exe_path, parent_window=None):
    msg_parent = parent_window if parent_window else controller.view
    manual_path = _normalize_exe_path(user_exe_path)
    saved_path = _normalize_exe_path(controller.config.get("custom_exe_path", ""))
    target_path = ""

    if manual_path:
        target_path = manual_path
        if not os.path.exists(target_path) or not target_path.lower().endswith(".exe"):
            msg_parent.after(300, lambda: _show_msg_safe(msg_parent, "error_title", "msg_path_invalid"))
            return
        if _normalize_compare_path(saved_path) != _normalize_compare_path(target_path):
            controller.config["custom_exe_path"] = target_path
            save_preferences_silent(controller)
    else:
        target_path = _get_effective_exe_path(controller, persist_changes=True, allow_script_fallback=True)

    if not target_path or not os.path.exists(target_path) or not target_path.lower().endswith(".exe"):
        msg_parent.after(300, lambda: _show_msg_safe(msg_parent, "error_title", "msg_path_invalid"))
        return

    try:
        work_dir = os.path.dirname(target_path)
        app_name = APP_NAME_INTERNAL
        icon_path = target_path

        if not os.path.exists(icon_path):
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            if not getattr(sys, 'frozen', False):
                base_path = os.path.abspath(os.path.join(base_path, ".", "."))
            icon_path = os.path.join(base_path, 'resources', 'branding', 'lector.ico')
            icon_path = os.path.normpath(icon_path)

        shell = win32com.client.Dispatch("WScript.Shell")
        link_path = ""
        msg_key = ""
        force_open_explorer = False
        rename_to_instruction = False

        if mode == "desktop":
            desktop_dir = shell.SpecialFolders("Desktop")
            link_path = os.path.join(desktop_dir, f"{app_name}.lnk")
            msg_key = "msg_shortcut_desktop_ok"

        elif mode == "start":
            programs_folder = _get_programs_folder(shell)
            link_path = os.path.join(programs_folder, f"{app_name}.lnk")
            msg_key = "msg_shortcut_start_ok"

        elif mode in ["taskbar", "start_pin"]:
            programs_folder = _get_programs_folder(shell)
            link_path = os.path.join(programs_folder, f"{app_name}.lnk")
            msg_key = "msg_shortcut_taskbar_ok" if mode == "taskbar" else "msg_shortcut_pin_start_ok"

        shortcut = shell.CreateShortCut(link_path)
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = work_dir
        if os.path.exists(icon_path):
            shortcut.IconLocation = f"{icon_path},0"
        shortcut.WindowStyle = 1
        shortcut.Description = controller.view._tr("shortcut_desc", APP_DISPLAY_NAME)
        shortcut.Save()

        if mode in ["taskbar", "start_pin"]:
            success_pin = _try_programmatic_pin(target_path, taskbar=(mode == "taskbar"))
            if not success_pin:
                success_pin = _try_programmatic_pin(link_path, taskbar=(mode == "taskbar"))

            if success_pin:
                force_open_explorer = False
            else:
                force_open_explorer = True
                rename_to_instruction = True
                msg_key = "msg_shortcut_manual_taskbar" if mode == "taskbar" else "msg_shortcut_manual_start"

        if rename_to_instruction:
            try:
                folder = os.path.dirname(link_path)
                instruction_name = controller.view._tr("lnk_name_taskbar" if mode == "taskbar" else "lnk_name_start")
                safe_name = "".join(x for x in instruction_name if x.isalnum() or x in " _-")
                new_path = os.path.join(folder, f"{safe_name}.lnk")

                if os.path.exists(new_path):
                    os.remove(new_path)

                os.rename(link_path, new_path)
                link_path = new_path
            except Exception as e:
                print(f"Error renombrando LNK: {e}")

        if force_open_explorer:
            try:
                subprocess.run(f'explorer /select,"{link_path}"', shell=True)
            except Exception:
                pass

        msg_parent.after(300, lambda: _show_msg_safe(msg_parent, "info_title", msg_key))
    except Exception as e:
        msg_parent.after(300, lambda: _show_msg_safe(msg_parent, "error_title", "msg_shortcut_error", str(e)))


def _try_programmatic_pin(link_path, taskbar=True):
    try:
        path = os.path.abspath(link_path)
        folder = os.path.dirname(path)
        filename = os.path.basename(path)

        shell = win32com.client.Dispatch("Shell.Application")
        ns = shell.NameSpace(folder)
        item = ns.ParseName(filename)
        if not item:
            return False

        keywords = ["anclar a la barra de tareas", "pin to taskbar", "taskbar"] if taskbar else \
            ["anclar a inicio", "pin to start", "start"]

        for verb in item.Verbs():
            v_name = verb.Name.lower()
            if any(k in v_name for k in keywords):
                if "desanclar" in v_name or "unpin" in v_name:
                    continue
                verb.DoIt()
                return True
        return False
    except Exception as e:
        print(f"Intento de anclaje fallido: {e}")
        return False


def _show_msg_safe(parent, title_key, msg_key, *args):
    tr_func = getattr(parent, "_tr", None)
    if not tr_func and hasattr(parent, "parent_view"):
        tr_func = getattr(parent.parent_view, "_tr", None)
    if not tr_func and hasattr(parent, "master") and hasattr(parent.master, "_tr"):
        tr_func = parent.master._tr
    try:
        if tr_func:
            title = tr_func(title_key)
            msg = tr_func(msg_key, *args)
            MessageDialog(parent, title, msg)
        else:
            MessageDialog(parent, title_key, msg_key)
    except Exception:
        try:
            if hasattr(parent, "restore_ui_from_modal"):
                parent.restore_ui_from_modal()
        except Exception:
            pass


def _resolve_translation(parent, key_or_text, *args):
    if key_or_text is None:
        return None
    tr_func = getattr(parent, "_tr", None)
    if tr_func:
        try:
            translated = tr_func(key_or_text, *args)
            if translated != f"<{key_or_text}>":
                return translated
        except Exception:
            pass
    if args:
        try:
            return str(key_or_text).format(*args)
        except Exception:
            pass
    return str(key_or_text)


def open_external_link_with_confirmation(parent, url, title_key, message_key, target_label=None, continue_key=None, cancel_key=None):
    if not url:
        return False
    try:
        title = _resolve_translation(parent, title_key)
        message = _resolve_translation(parent, message_key)
        continue_text = _resolve_translation(parent, continue_key or "btn_continue_external") or "Continue"
        cancel_text = _resolve_translation(parent, cancel_key or "btn_cancel_simple") or "Cancel"
        should_open = ExternalLinkDialog.ask(
            parent=parent,
            title=title,
            message=message,
            target_label=target_label,
            continue_text=continue_text,
            cancel_text=cancel_text
        )
        if not should_open:
            return False
        webbrowser.open_new(url)
        return True
    except Exception:
        try:
            if hasattr(parent, "restore_ui_from_modal"):
                parent.restore_ui_from_modal()
        except Exception:
            pass
        return False


# =============================================================================
# MANEJADORES DE PERFILES
# =============================================================================

def manage_profiles(controller):
    _open_profiles_dialog_safe(controller)


def _save_meta_immediate(controller, profiles_snapshot):
    clean_meta = profiles_snapshot.copy()
    for pid, data in clean_meta.items():
        if data == "NEW":
            clean_meta[pid] = config.get_blank_profile()
    controller.config["_profiles_meta"] = clean_meta
    save_preferences_silent(controller)


def _open_profiles_dialog_safe(controller):
    profiles = controller.config.get("_profiles_meta", {})
    active_id = controller.config.get("_active_profile_id", "default")

    if not profiles:
        profiles = {"default": config.DEFAULT_CONFIG_VALUES.copy()}

    dialog = controller.view.get_profiles_dialog()
    dialog.load_state(
        profiles_meta=profiles,
        active_id=active_id,
        on_save_callback=lambda p: _save_meta_immediate(controller, p)
    )
    dialog.present()
    result = dialog.wait_result()

    if result:
        new_active_id, new_profiles_meta = result
        _switch_profile_sequence(controller, new_active_id, new_profiles_meta)


def _switch_profile_sequence(controller, new_active_id, new_profiles_meta):
    controller.view.prepare_soft_refresh()
    controller.view.after(PROFILE_SWITCH_FADE_DELAY_MS, lambda: _load_profile_data(controller, new_active_id, new_profiles_meta))


def _load_profile_data(controller, new_active_id, new_profiles_meta):
    try:
        if new_active_id in new_profiles_meta and new_profiles_meta[new_active_id] == "NEW":
            selected_profile_data = config.get_blank_profile()
            new_profiles_meta[new_active_id] = selected_profile_data
        else:
            selected_profile_data = new_profiles_meta[new_active_id]

        controller.config = selected_profile_data.copy()
        controller.config["_profiles_meta"] = new_profiles_meta
        controller.config["_active_profile_id"] = new_active_id

        save_preferences_silent(controller)
        controller._update_active_lecturas_path()

        controller.view.lang = controller.config["language"]
        controller.view.update_ui_texts()

        new_theme = controller.config["theme"]
        controller.view.current_theme = new_theme
        customtkinter.set_appearance_mode(new_theme)
        controller.view.apply_theme()

    except Exception as e:
        print(f"Error cargando perfil: {e}")

    controller.view.after(300, lambda: _show_app_after_switch(controller, new_active_id))


def _show_app_after_switch(controller, new_active_id):
    controller.view.complete_soft_refresh()
    controller.view.after(100, lambda:
    controller.view.show_message("info_title", "msg_profile_changed", new_active_id.capitalize())
                          )


# =============================================================================
# MANEJADORES DE RESTAURACION Y OTROS
# =============================================================================

def restore_default_settings(controller):
    if ConfirmDialog.ask(controller.view, controller.view._tr("confirm_restore_title"),
                         controller.view._tr("confirm_restore_prompt")):
        controller.view.prepare_soft_refresh()
        controller.view.after(RESTORE_FADE_DELAY_MS, lambda: _execute_restore(controller))


def _execute_restore(controller):
    try:
        config.delete_config_file()
        default_profile = config.DEFAULT_CONFIG_VALUES.copy()

        controller.config = default_profile.copy()
        controller.config["_profiles_meta"] = {"default": default_profile.copy()}
        controller.config["_active_profile_id"] = "default"

        save_preferences_silent(controller)
        controller._update_active_lecturas_path()

        controller.view.lang = controller.config["language"]
        controller.view.update_ui_texts()

        new_theme = controller.config["theme"]
        controller.view.current_theme = new_theme
        customtkinter.set_appearance_mode(new_theme)
        controller.view.apply_theme()
    except Exception as e:
        print(f"Error restaurando: {e}")

    controller.view.after(300, lambda: _finish_restore(controller))


def _finish_restore(controller):
    controller.view.complete_soft_refresh()
    controller.view.after(100, lambda:
    controller.view.show_message("info_title", "msg_restore_success")
                          )


def save_preferences_silent(controller):
    config.save_config(controller.config)


def toggle_theme(controller):
    new_theme = "Dark" if controller.view.current_theme == "Light" else "Light"
    controller.config["theme"] = new_theme
    controller.view.switch_theme_animated(new_theme)
    save_preferences_silent(controller)


def toggle_language(controller):
    controller.view.lang = "en" if controller.view.lang == "es" else "es"
    controller.config["language"] = controller.view.lang
    controller.view.update_ui_texts()
    save_preferences_silent(controller)