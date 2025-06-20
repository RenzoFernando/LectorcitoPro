import os
import shutil
import webbrowser
from tkinter import filedialog
import config
from view.dialogs import ConfirmDialog, ChoiceDialog
# --- Importamos el nuevo diálogo de etiquetas ---
from view.tags_dialog import TagsConfigDialog


def select_destination_path(controller):
    """Maneja la selección de la ruta de destino para los reportes."""
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


def show_view_config_dialog(controller):
    """Muestra el nuevo diálogo de etiquetas para configurar qué incluir."""
    # Obtener las listas actuales del config
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
        # El diálogo devuelve las listas de etiquetas modificadas
        new_folders, new_files = result
        # Asegurarse de que las extensiones tengan el punto inicial
        for tag in new_files:
            if not tag["nombre"].startswith("."):
                tag["nombre"] = f".{tag['nombre']}"

        controller.config["etiquetas_carpetas_importantes"] = new_folders
        controller.config["etiquetas_extensiones_incluidas"] = new_files
        save_preferences_silent(controller)


def show_no_view_config_dialog(controller):
    """Muestra el nuevo diálogo de etiquetas para configurar qué excluir."""
    # Obtener las listas actuales del config
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
        # El diálogo devuelve las listas de etiquetas modificadas
        new_folders, new_files = result
        controller.config["etiquetas_carpetas_excluidas"] = new_folders
        controller.config["etiquetas_archivos_excluidos"] = new_files
        save_preferences_silent(controller)


def save_preferences_silent(controller):
    """Guarda la configuración actual en el archivo JSON."""
    config.save_config(controller.config)


def toggle_theme(controller):
    """Cambia entre el tema claro y oscuro."""
    controller.view.current_theme = "Dark" if controller.view.current_theme == "Light" else "Light"
    controller.config["theme"] = controller.view.current_theme
    controller.view.apply_theme()
    save_preferences_silent(controller)


def toggle_language(controller):
    """Cambia entre español e inglés."""
    controller.view.lang = "en" if controller.view.lang == "es" else "es"
    controller.config["language"] = controller.view.lang
    controller.view.update_ui_texts()
    save_preferences_silent(controller)


def restore_default_settings(controller):
    """Restaura todas las configuraciones a sus valores por defecto."""
    if ConfirmDialog.ask(controller.view, controller.view._tr("confirm_restore_title"),
                         controller.view._tr("confirm_restore_prompt")):
        config.delete_config_file()
        controller.config = config.load_config()

        controller._update_active_lecturas_path()
        controller.view.lang = controller.config["language"]
        controller.view.current_theme = controller.config["theme"]
        controller.view.update_ui_texts()
        controller.view.apply_theme()
        save_preferences_silent(controller)
        controller.view.show_message("info_title", "msg_restore_success")


def open_destination_folder(controller):
    """Abre la carpeta de destino de los reportes."""
    path = controller.config.get("lecturas_path")
    if path and os.path.isdir(path):
        webbrowser.open(os.path.realpath(path))
    else:
        controller.view.show_message("info_title", "msg_select_dest")


def open_last_report(controller):
    """Abre el último reporte generado."""
    if controller.last_report_path and os.path.isfile(controller.last_report_path):
        webbrowser.open(os.path.realpath(controller.last_report_path))
    else:
        controller.view.show_message("info_title", "msg_no_report_yet")


def delete_all_readings(controller):
    """Elimina la carpeta de lecturas con todo su contenido."""
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
