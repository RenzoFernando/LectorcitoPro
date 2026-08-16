import os
import shutil
import webbrowser
import customtkinter
from tkinter import filedialog

import config
from app_meta import APP_DISPLAY_NAME, APP_NAME_INTERNAL, APP_INSTALL_MARKER_FILE, APP_LINUX_DESKTOP_ID
from file_rules import canonical_file_rule, normalize_file_rule_list, normalize_file_tag_list
from view.dialogs import ConfirmDialog, ChoiceDialog, ExternalLinkDialog, MessageDialog
from view.tags_dialog import TagsConfigDialog
from view.profiles_dialog import ProfilesDialog
from view.settings_dialog import SettingsDialog
from view.translations import translate_default
from view.ui_constants import PROFILE_SWITCH_FADE_DELAY_MS, RESTORE_FADE_DELAY_MS
from view.ui_assets import get_app_icon_png_path

def _get_effective_launcher_path(controller, provided_path=None, persist_changes=True, allow_script_fallback=False):
    platform = controller.platform
    manual_path = platform.normalize_launcher_path(provided_path)
    saved_path = platform.normalize_launcher_path(controller.config.get("custom_exe_path", ""))
    runtime_path = platform.get_runtime_executable()
    installed_path = platform.get_installed_executable(APP_INSTALL_MARKER_FILE)

    if manual_path:
        return manual_path

    if installed_path:
        if persist_changes and platform.normalize_compare_path(saved_path) != platform.normalize_compare_path(installed_path):
            controller.config["custom_exe_path"] = installed_path
            save_preferences_silent(controller)
        return installed_path

    if saved_path and runtime_path and platform.normalize_compare_path(saved_path) == platform.normalize_compare_path(runtime_path):
        saved_path = ""
        if persist_changes and controller.config.get("custom_exe_path", ""):
            controller.config["custom_exe_path"] = ""
            save_preferences_silent(controller)

    if saved_path:
        return saved_path

    if allow_script_fallback:
        return platform.get_script_fallback_launcher()

    return ""


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
        path = filedialog.askdirectory(parent=controller.view, title=controller.view._tr("btn_sel_lecturas"))
        if path:
            custom_path = os.path.join(path, "Lecturas")
            controller.config.update({"use_default_path": False, "custom_lecturas_path": custom_path})
            controller.view.show_message("info_title", "dest_set_custom_msg", custom_path)

    controller._update_active_lecturas_path()
    save_preferences_silent(controller)


def open_destination_folder(controller):
    path = controller.config.get("lecturas_path")
    if path and os.path.isdir(path):
        controller.platform.open_folder(path)
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
        controller.platform.open_file(latest_report_path)
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
    current_exe = controller.config.get("custom_exe_path", "")
    if controller.platform.supports_launcher_configuration():
        current_exe = _get_effective_launcher_path(controller, persist_changes=True, allow_script_fallback=False)

    def on_save(new_ext, new_exe_path):
        _update_settings_values(controller, new_ext, new_exe_path)

    def on_shortcut(mode, exe_path_input, parent_window=None):
        _create_system_shortcut(controller, mode, exe_path_input, parent_window)

    def on_export(parent_window=None):
        _export_app_configuration(controller, parent_window)

    def on_import(parent_window=None):
        _import_app_configuration(controller, parent_window)

    dialog = controller.view.get_settings_dialog()
    dialog.load_state(
        current_extension=current_ext,
        current_exe_path=current_exe,
        on_save_callback=on_save,
        on_shortcut_callback=on_shortcut,
        on_export_callback=on_export,
        on_import_callback=on_import,
        platform_capabilities=controller.platform.get_capabilities()
    )
    dialog.present()
    dialog.wait_result()


def _export_app_configuration(controller, parent_window=None):
    suggested_name = f"{APP_NAME_INTERNAL}-config{config.EXPORT_FILE_EXTENSION}"
    file_path = filedialog.asksaveasfilename(
        parent=parent_window if parent_window and parent_window.winfo_exists() else controller.view,
        title=controller.view._tr("dlg_export_config_title"),
        defaultextension=config.EXPORT_FILE_EXTENSION,
        initialfile=suggested_name,
        filetypes=[
            (controller.view._tr("filetype_config_json"), f"*{config.EXPORT_FILE_EXTENSION}"),
            (controller.view._tr("filetype_json"), "*.json"),
            (controller.view._tr("filetype_all"), "*.*")
        ]
    )
    if not file_path:
        return
    try:
        config.export_config_to_file(file_path, controller.config)
        msg_parent = parent_window if parent_window and parent_window.winfo_exists() else controller.view
        msg_parent.after(120, lambda: _show_msg_safe(msg_parent, "info_title", "msg_export_success", file_path))
    except Exception as e:
        msg_parent = parent_window if parent_window and parent_window.winfo_exists() else controller.view
        msg_parent.after(120, lambda: _show_msg_safe(msg_parent, "error_title", "msg_export_error", str(e)))


def _import_app_configuration(controller, parent_window=None):
    file_path = filedialog.askopenfilename(
        parent=parent_window if parent_window and parent_window.winfo_exists() else controller.view,
        title=controller.view._tr("dlg_import_config_title"),
        filetypes=[
            (controller.view._tr("filetype_config_json"), f"*{config.EXPORT_FILE_EXTENSION}"),
            (controller.view._tr("filetype_json"), "*.json"),
            (controller.view._tr("filetype_all"), "*.*")
        ]
    )
    if not file_path:
        return

    try:
        runtime_config = config.import_config_from_file(file_path)
    except Exception as e:
        msg_parent = parent_window if parent_window and parent_window.winfo_exists() else controller.view
        msg_parent.after(120, lambda: _show_msg_safe(msg_parent, "error_title", "msg_import_error", str(e)))
        return

    confirmed = ConfirmDialog.ask(
        controller.view,
        controller.view._tr("confirm_import_config_title"),
        controller.view._tr("confirm_import_config_prompt")
    )
    if not confirmed:
        return

    if parent_window and parent_window.winfo_exists():
        try:
            parent_window._close_with_fade_out()
        except Exception:
            pass

    controller.view.prepare_soft_refresh()
    controller.view.after(RESTORE_FADE_DELAY_MS, lambda: _execute_import_config(controller, runtime_config, file_path))


def _execute_import_config(controller, runtime_config, file_path):
    try:
        _apply_runtime_config(controller, runtime_config)
        controller._update_active_lecturas_path()
        controller.last_report_path = None

        controller.view.lang = controller.config["language"]
        controller.view.current_theme = controller.config["theme"]
        customtkinter.set_appearance_mode(controller.view.current_theme)
        controller.view.update_ui_texts()
        controller.view.apply_theme()
        save_preferences_silent(controller)
    except Exception as e:
        controller.view.complete_soft_refresh()
        controller.view.after(120, lambda: controller.view.show_message("error_title", "msg_import_error", str(e)))
        return

    controller.view.after(180, controller.view.complete_soft_refresh)
    controller.view.after(320, lambda: controller.view.show_message("info_title", "msg_import_success", file_path))


def _update_settings_values(controller, new_ext, new_exe_path):
    changed = False

    if new_ext in [".txt", ".md"] and controller.config.get("report_extension") != new_ext:
        controller.config["report_extension"] = new_ext
        changed = True

    if controller.platform.supports_launcher_configuration():
        clean_path = controller.platform.normalize_launcher_path(new_exe_path)
        installed_path = controller.platform.get_installed_executable(APP_INSTALL_MARKER_FILE)

        if installed_path:
            clean_path = installed_path

        current_saved_path = controller.platform.normalize_launcher_path(controller.config.get("custom_exe_path", ""))
        runtime_path = controller.platform.get_runtime_executable()

        if clean_path and runtime_path and not installed_path:
            if controller.platform.normalize_compare_path(clean_path) == controller.platform.normalize_compare_path(runtime_path):
                clean_path = ""

        if controller.platform.normalize_compare_path(current_saved_path) != controller.platform.normalize_compare_path(clean_path):
            controller.config["custom_exe_path"] = clean_path
            changed = True

    if changed:
        save_preferences_silent(controller)


def _create_system_shortcut(controller, mode, user_exe_path, parent_window=None):
    msg_parent = parent_window if parent_window else controller.view
    platform = controller.platform

    if not platform.supports_shortcut_mode(mode):
        msg_parent.after(
            300,
            lambda: _show_msg_safe(msg_parent, "error_title", "msg_shortcut_error", f"Unsupported platform action: {mode}")
        )
        return

    manual_path = platform.normalize_launcher_path(user_exe_path)
    saved_path = platform.normalize_launcher_path(controller.config.get("custom_exe_path", ""))

    if manual_path:
        target_path = manual_path
        if not platform.is_valid_launcher(target_path):
            msg_parent.after(300, lambda: _show_msg_safe(msg_parent, "error_title", "msg_path_invalid"))
            return
        if platform.normalize_compare_path(saved_path) != platform.normalize_compare_path(target_path):
            controller.config["custom_exe_path"] = target_path
            save_preferences_silent(controller)
    else:
        target_path = _get_effective_launcher_path(
            controller,
            persist_changes=True,
            allow_script_fallback=True
        )

    if not target_path or not platform.is_valid_launcher(target_path):
        msg_parent.after(300, lambda: _show_msg_safe(msg_parent, "error_title", "msg_path_invalid"))
        return

    result = platform.create_system_shortcut(
        mode=mode,
        target_path=target_path,
        app_name=APP_NAME_INTERNAL,
        description=controller.view._tr("shortcut_desc", APP_DISPLAY_NAME),
        taskbar_instruction=controller.view._tr("lnk_name_taskbar"),
        start_instruction=controller.view._tr("lnk_name_start"),
        display_name=APP_DISPLAY_NAME,
        desktop_id=APP_LINUX_DESKTOP_ID,
        icon_path=get_app_icon_png_path()
    )

    if not result.success:
        error_text = result.error or result.status or mode
        msg_parent.after(
            300,
            lambda text=error_text: _show_msg_safe(msg_parent, "error_title", "msg_shortcut_error", text)
        )
        return

    message_map = {
        "desktop_created": "msg_shortcut_desktop_ok",
        "start_created": "msg_shortcut_start_ok",
        "taskbar_pinned": "msg_shortcut_taskbar_ok",
        "start_pinned": "msg_shortcut_pin_start_ok",
        "taskbar_manual": "msg_shortcut_manual_taskbar",
        "start_manual": "msg_shortcut_manual_start",
        "linux_desktop_created": "msg_shortcut_linux_desktop_ok",
        "linux_menu_created": "msg_shortcut_linux_menu_ok"
    }
    msg_key = message_map.get(result.status)
    if msg_key:
        msg_parent.after(300, lambda key=msg_key: _show_msg_safe(msg_parent, "info_title", key))


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
            MessageDialog(parent, translate_default(title_key), translate_default(msg_key, *args))
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
        continue_text = _resolve_translation(parent, continue_key or "btn_continue_external") or translate_default(continue_key or "btn_continue_external")
        cancel_text = _resolve_translation(parent, cancel_key or "btn_cancel_simple") or translate_default(cancel_key or "btn_cancel_simple")
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


def _apply_runtime_config(controller, runtime_config):
    controller.config = runtime_config
    try:
        controller.view.config = controller.config
    except Exception:
        pass


def _save_meta_immediate(controller, profiles_snapshot, active_id=None):
    clean_meta = {}
    for pid, data in (profiles_snapshot or {}).items():
        if data == "NEW":
            clean_meta[pid] = config.get_blank_profile()
        elif isinstance(data, dict):
            clean_meta[pid] = config.build_profile_config(data, pid)

    if "default" not in clean_meta:
        clean_meta["default"] = config.build_profile_config(config.DEFAULT_CONFIG_VALUES, "default")

    current_active_id = controller.config.get("_active_profile_id", "default")
    if current_active_id in clean_meta:
        clean_meta[current_active_id] = config.extract_profile_from_runtime_config(controller.config, current_active_id)

    target_active_id = active_id if active_id in clean_meta else current_active_id if current_active_id in clean_meta else "default"
    runtime_config = config.build_runtime_config(clean_meta, target_active_id)
    _apply_runtime_config(controller, runtime_config)
    save_preferences_silent(controller)


def _open_profiles_dialog_safe(controller):
    profiles = controller.config.get("_profiles_meta", {})
    active_id = controller.config.get("_active_profile_id", "default")

    if not profiles:
        profiles = {"default": config.build_profile_config(config.DEFAULT_CONFIG_VALUES, "default")}

    dialog = controller.view.get_profiles_dialog()
    dialog.load_state(
        profiles_meta=profiles,
        active_id=active_id,
        on_save_callback=lambda p, a: _save_meta_immediate(controller, p, a)
    )
    dialog.present()
    result = dialog.wait_result()

    if result:
        new_active_id, new_profiles_meta = result
        _switch_profile_sequence(controller, new_active_id, new_profiles_meta)


def _switch_profile_sequence(controller, new_active_id, new_profiles_meta):
    controller.view.switch_profile_animated(
        apply_callback=lambda: _load_profile_data(controller, new_active_id, new_profiles_meta),
        complete_callback=lambda: _show_app_after_switch(controller, new_active_id)
    )


def _load_profile_data(controller, new_active_id, new_profiles_meta):
    try:
        merged_profiles = config.clone_profiles_meta(new_profiles_meta)
        current_active_id = controller.config.get("_active_profile_id", "default")
        if current_active_id in merged_profiles:
            merged_profiles[current_active_id] = config.extract_profile_from_runtime_config(controller.config, current_active_id)

        runtime_config = config.build_runtime_config(merged_profiles, new_active_id)
        _apply_runtime_config(controller, runtime_config)
        controller._update_active_lecturas_path()

        controller.view.lang = controller.config["language"]
        controller.view.update_ui_texts()

        new_theme = controller.config["theme"]
        controller.view.current_theme = new_theme
        customtkinter.set_appearance_mode(new_theme)
        controller.view.apply_theme()
        save_preferences_silent(controller)

    except Exception as e:
        print(f"Error cargando perfil: {e}")


def _show_app_after_switch(controller, new_active_id):
    controller.view.show_message("info_title", "msg_profile_changed", new_active_id.capitalize())


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
        runtime_config = config.build_runtime_config({"default": config.DEFAULT_CONFIG_VALUES}, "default")
        _apply_runtime_config(controller, runtime_config)
        controller._update_active_lecturas_path()

        controller.view.lang = controller.config["language"]
        controller.view.update_ui_texts()

        new_theme = controller.config["theme"]
        controller.view.current_theme = new_theme
        customtkinter.set_appearance_mode(new_theme)
        controller.view.apply_theme()
        save_preferences_silent(controller)
    except Exception as e:
        print(f"Error restaurando: {e}")

    controller.view.after(300, lambda: _finish_restore(controller))


def _finish_restore(controller):
    controller.view.complete_soft_refresh()
    controller.view.after(100, lambda:
    controller.view.show_message("info_title", "msg_restore_success")
                          )


def save_preferences_silent(controller):
    active_id = controller.config.get("_active_profile_id", "default")
    profiles = config.clone_profiles_meta(controller.config.get("_profiles_meta", {}))
    profiles[active_id] = config.extract_profile_from_runtime_config(controller.config, active_id)
    runtime_config = config.build_runtime_config(profiles, active_id)
    _apply_runtime_config(controller, runtime_config)
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
