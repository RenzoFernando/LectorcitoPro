# src/controller/handlers.py
import os
import shutil
import webbrowser
import customtkinter
from tkinter import filedialog
import config
from view.dialogs import ConfirmDialog, ChoiceDialog
from view.tags_dialog import TagsConfigDialog
from view.profiles_dialog import ProfilesDialog


# Maneja la selección de la ruta de destino para los reportes.
def select_destination_path(controller):
    choice = ChoiceDialog.ask(
        parent=controller.view, title=controller.view._tr("dlg_dest_choice_title"),
        message=controller.view._tr("dlg_dest_choice_prompt"),
        option1_text=controller.view._tr("dlg_dest_choice_op1"),
        option2_text=controller.view._tr("dlg_dest_choice_op2"),
        option1_value="default", option2_value="custom"
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


# Muestra el diálogo para configurar qué carpetas y extensiones incluir.
def show_view_config_dialog(controller):
    current_folders = controller.config.get("etiquetas_carpetas_importantes", [])
    current_files = controller.config.get("etiquetas_extensiones_incluidas", [])

    result = TagsConfigDialog.get_input(
        parent=controller.view,
        title=controller.view._tr("dlg_ver_title"),
        folders_prompt=controller.view._tr("dlg_ver_folder_prompt"),
        initial_folders=current_folders,
        files_prompt=controller.view._tr("dlg_ver_file_prompt"),
        initial_files=current_files
    )

    if result is not None:
        new_folders, new_files = result
        for tag in new_files:
            if not tag["nombre"].startswith("."):
                tag["nombre"] = f".{tag['nombre']}"

        controller.config["etiquetas_carpetas_importantes"] = new_folders
        controller.config["etiquetas_extensiones_incluidas"] = new_files
        save_preferences_silent(controller)


# Muestra el diálogo para configurar qué carpetas y archivos excluir.
def show_no_view_config_dialog(controller):
    current_folders = controller.config.get("etiquetas_carpetas_excluidas", [])
    current_files = controller.config.get("etiquetas_archivos_excluidos", [])

    result = TagsConfigDialog.get_input(
        parent=controller.view,
        title=controller.view._tr("dlg_nover_title"),
        folders_prompt=controller.view._tr("dlg_nover_folder_prompt"),
        initial_folders=current_folders,
        files_prompt=controller.view._tr("dlg_nover_file_prompt"),
        initial_files=current_files
    )

    if result is not None:
        new_folders, new_files = result
        controller.config["etiquetas_carpetas_excluidas"] = new_folders
        controller.config["etiquetas_archivos_excluidos"] = new_files
        save_preferences_silent(controller)


# Muestra el diálogo para configurar archivos multimedia y binarios.
def show_etiqueta_config_dialog(controller):
    tags_stored = controller.config.get("etiquetas_multimedia_config", [])

    if not tags_stored:
        raw_exts = controller.config.get("media_extensions", [])
        current_files = [{"nombre": x, "estado": "activo"} for x in raw_exts]
    else:
        current_files = tags_stored

    result = TagsConfigDialog.get_input(
        parent=controller.view,
        title=controller.view._tr("dlg_etiqueta_title"),
        folders_prompt=None,
        initial_folders=None,
        files_prompt=controller.view._tr("dlg_etiqueta_file_prompt"),
        initial_files=current_files
    )

    if result is not None:
        _, new_files = result

        for tag in new_files:
            if not tag["nombre"].startswith("."):
                tag["nombre"] = f".{tag['nombre']}"

        controller.config["etiquetas_multimedia_config"] = new_files

        active_media_exts = [t["nombre"] for t in new_files if t["estado"] == "activo"]
        controller.config["media_extensions"] = active_media_exts

        save_preferences_silent(controller)


# --- GESTIÓN DE PERFILES: MODO "PASO A PASO" (SIN LAG) ---
def manage_profiles(controller):
    # Paso 1: Delay inicial muy generoso (300ms) para que el click termine visualmente
    controller.view.after(300, lambda: _open_profiles_dialog_safe(controller))


def _save_meta_immediate(controller, profiles_snapshot):
    """Callback para guardar perfiles sin necesidad de activarlos."""
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

    result = ProfilesDialog.ask(
        controller.view,
        profiles,
        active_id,
        on_save_callback=lambda p: _save_meta_immediate(controller, p)
    )

    if result:
        new_active_id, new_profiles_meta = result
        # Iniciamos la transición lenta y segura
        _step_1_hide_app(controller, new_active_id, new_profiles_meta)


# --- SECUENCIA DE TRANSICIÓN "PASO A PASO" (PERFILES) ---

def _step_1_hide_app(controller, new_active_id, new_profiles_meta):
    """Paso 1: Ocultar la aplicación inmediatamente."""
    controller.view.attributes("-alpha", 0.0)
    # Dar un "respiro" largo de 600ms antes de procesar nada
    controller.view.after(600, lambda: _step_2_load_data(controller, new_active_id, new_profiles_meta))


def _step_2_load_data(controller, new_active_id, new_profiles_meta):
    """Paso 2: Cargar datos pesados mientras no se ve nada."""
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

        # Actualizar componentes visuales
        controller._update_active_lecturas_path()
        controller.view.lang = controller.config["language"]
        controller.view.update_ui_texts()

        new_theme = controller.config["theme"]
        controller.view.current_theme = new_theme
        customtkinter.set_appearance_mode(new_theme)
        controller.view.apply_theme()

    except Exception as e:
        print(f"Error cargando perfil: {e}")

    # Dar otro respiro de 300ms para que Tkinter termine de pintar internamente
    controller.view.after(300, lambda: _step_3_show_app(controller, new_active_id))


def _step_3_show_app(controller, new_active_id):
    """Paso 3: Mostrar la aplicación renovada."""
    controller.view.attributes("-alpha", 1.0)
    # Mensaje final
    controller.view.after(100, lambda:
    controller.view.show_message("info_title", "msg_profile_changed", new_active_id.capitalize())
                          )


# --- SECUENCIA DE TRANSICIÓN "PASO A PASO" (RESTAURAR) ---

def restore_default_settings(controller):
    if ConfirmDialog.ask(controller.view, controller.view._tr("confirm_restore_title"),
                         controller.view._tr("confirm_restore_prompt")):
        # Paso 1: Ocultar aplicación (Fantasma)
        _step_1_restore_hide(controller)


def _step_1_restore_hide(controller):
    controller.view.attributes("-alpha", 0.0)
    # Respiro largo (800ms) para operaciones de disco
    controller.view.after(800, lambda: _step_2_restore_logic(controller))


def _step_2_restore_logic(controller):
    try:
        # 1. Eliminar archivo físico
        config.delete_config_file()

        # 2. Reiniciar memoria a estado de fábrica (Default Profile Only)
        default_profile = config.DEFAULT_CONFIG_VALUES.copy()

        # Reconstruir el config del controlador como si fuera la primera ejecución
        controller.config = default_profile.copy()
        controller.config["_profiles_meta"] = {"default": default_profile.copy()}
        controller.config["_active_profile_id"] = "default"

        # 3. Guardar el estado limpio (recrea config.json)
        save_preferences_silent(controller)

        # 4. Actualizar toda la UI
        controller._update_active_lecturas_path()

        # Reset Idioma
        controller.view.lang = controller.config["language"]
        controller.view.update_ui_texts()

        # Reset Tema
        new_theme = controller.config["theme"]
        controller.view.current_theme = new_theme
        customtkinter.set_appearance_mode(new_theme)
        controller.view.apply_theme()

    except Exception as e:
        print(f"Error restaurando: {e}")

    # Respiro para renderizado interno
    controller.view.after(300, lambda: _step_3_restore_show(controller))


def _step_3_restore_show(controller):
    controller.view.attributes("-alpha", 1.0)
    controller.view.after(100, lambda:
    controller.view.show_message("info_title", "msg_restore_success")
                          )


# Guarda la configuración actual sin mostrar notificaciones.
def save_preferences_silent(controller):
    config.save_config(controller.config)


# Alterna entre el tema claro y oscuro.
def toggle_theme(controller):
    new_theme = "Dark" if controller.view.current_theme == "Light" else "Light"
    controller.config["theme"] = new_theme
    controller.view.switch_theme_animated(new_theme)
    save_preferences_silent(controller)


# Alterna entre español e inglés.
def toggle_language(controller):
    controller.view.lang = "en" if controller.view.lang == "es" else "es"
    controller.config["language"] = controller.view.lang
    controller.view.update_ui_texts()
    save_preferences_silent(controller)


# Abre la carpeta de destino de los reportes.
def open_destination_folder(controller):
    path = controller.config.get("lecturas_path")
    if path and os.path.isdir(path):
        webbrowser.open(os.path.realpath(path))
    else:
        controller.view.show_message("info_title", "msg_select_dest")


# Abre el último reporte generado.
def open_last_report(controller):
    if controller.last_report_path and os.path.isfile(controller.last_report_path):
        webbrowser.open(os.path.realpath(controller.last_report_path))
    else:
        controller.view.show_message("info_title", "msg_no_report_yet")


# Elimina la carpeta de lecturas.
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