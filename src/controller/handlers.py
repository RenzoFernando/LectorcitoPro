

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
from view.dialogs import ConfirmDialog, ChoiceDialog, MessageDialog
from view.tags_dialog import TagsConfigDialog
from view.profiles_dialog import ProfilesDialog
from view.settings_dialog import SettingsDialog
from view.ui_constants import PROFILE_SWITCH_FADE_DELAY_MS, RESTORE_FADE_DELAY_MS


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


def open_last_report(controller):
    if controller.last_report_path and os.path.isfile(controller.last_report_path):
        webbrowser.open(os.path.realpath(controller.last_report_path))
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

    dialog = controller.view.get_no_view_dialog()
    dialog.load_state(
        title=controller.view._tr("dlg_nover_title"),
        folders_prompt=controller.view._tr("dlg_nover_folder_prompt"),
        initial_folders=current_folders,
        files_prompt=controller.view._tr("dlg_nover_file_prompt"),
        initial_files=current_files
    )
    dialog.present()
    result = dialog.wait_result()

    if result is not None:
        new_folders, new_files = result
        controller.config["etiquetas_carpetas_excluidas"] = new_folders
        controller.config["etiquetas_archivos_excluidos"] = normalize_file_tag_list(new_files)
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
    if new_ext in [".txt", ".md"]:
        controller.config["report_extension"] = new_ext
        changed = True
    clean_path = new_exe_path.strip().replace('"', '')
    if clean_path is not None:
        controller.config["custom_exe_path"] = clean_path
        changed = True

    if changed:
        save_preferences_silent(controller)


def _create_system_shortcut(controller, mode, user_exe_path, parent_window=None):
    msg_parent = parent_window if parent_window else controller.view
    target_path = ""
    if user_exe_path and str(user_exe_path).strip():
        target_path = str(user_exe_path).strip().replace('"', '')
        controller.config["custom_exe_path"] = target_path
        save_preferences_silent(controller)
    else:
        target_path = controller.config.get("custom_exe_path", "").strip().replace('"', '')

    if not target_path or not os.path.exists(target_path) or not target_path.lower().endswith(".exe"):
        if not getattr(sys, 'frozen', False):
            target_path = sys.executable
            print(controller.view._tr("shortcut_script_warning"))
        else:
            msg_parent.after(300, lambda: _show_msg_safe(msg_parent, "error_title", "msg_path_invalid"))
            return

    try:
        work_dir = os.path.dirname(target_path)
        app_name = APP_NAME_INTERNAL

        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        if not getattr(sys, 'frozen', False):
            base_path = os.path.join(base_path, "..")
        icon_path = os.path.join(base_path, 'recursos', 'lector.ico')
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
            start_menu = shell.SpecialFolders("StartMenu")
            programs_folder = os.path.join(start_menu, "Programs")
            if not os.path.exists(programs_folder):
                try:
                    os.makedirs(programs_folder)
                except:
                    programs_folder = start_menu
            link_path = os.path.join(programs_folder, f"{app_name}.lnk")
            msg_key = "msg_shortcut_start_ok"

        elif mode in ["taskbar", "start_pin"]:
            docs_dir = shell.SpecialFolders("MyDocuments")
            link_path = os.path.join(docs_dir, f"{app_name}.lnk")
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
        if not item: return False

        keywords = ["anclar a la barra de tareas", "pin to taskbar", "taskbar"] if taskbar else \
            ["anclar a inicio", "pin to start", "start"]

        for verb in item.Verbs():
            v_name = verb.Name.lower()
            if any(k in v_name for k in keywords):
                if "desanclar" in v_name or "unpin" in v_name: continue
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
    controller.view.attributes("-alpha", 0.0)
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
    controller.view.attributes("-alpha", 1.0)
    controller.view.after(100, lambda:
    controller.view.show_message("info_title", "msg_profile_changed", new_active_id.capitalize())
                          )


# =============================================================================
# MANEJADORES DE RESTAURACION Y OTROS
# =============================================================================

def restore_default_settings(controller):
    if ConfirmDialog.ask(controller.view, controller.view._tr("confirm_restore_title"),
                         controller.view._tr("confirm_restore_prompt")):
        controller.view.attributes("-alpha", 0.0)
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
    controller.view.attributes("-alpha", 1.0)
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
