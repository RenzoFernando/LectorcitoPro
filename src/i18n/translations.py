# =============================================================================
# DICCIONARIO DE TRADUCCIONES
# =============================================================================

TRANSLATIONS = {
"es": {
    # --- GENERAL ---
    "title": "LECTORCITO PRO",
    "welcome": ", por favor seleccione una opción.",
    "footer_copyright": "Copyright © {} - {}",
    "manual_title": "Manual de Usuario",
    "info_title": "Información",
    "error_title": "Error",
    "critical_error_title": "Error Crítico {}",
    "critical_error_message": "Error crítico:\n\n{}\n\nDetalles en:\n{}",
    "fallback_user": "Usuario",

    # --- SALUDOS ---
    "greet_m": ["¡Buenos días!", "¡Un café y a programar!", "¿Listo para un nuevo día?",
                "¡Que tengas una mañana productiva!"],
    "greet_a": ["¡Buenas tardes!", "Espero que tu día vaya de maravilla.", "¡A seguir dándole al código!",
                "La tarde es para crear."],
    "greet_n": ["¡Buenas noches!", "Un último vistazo antes de descansar.", "¡Que el código te acompañe!",
                "Es hora de compilar sueños."],

    # --- BOTONES PRINCIPALES ---
    "btn_sel_lecturas": "Seleccionar Destino de Lecturas",
    "btn_choose_folder": "Generar Lectura Completa",
    "btn_create_tree": "Crear Estructura de Árbol",
    "btn_open_lecturas": "Abrir Carpeta de Lecturas",
    "btn_open_last": "Abrir Último Reporte",
    "btn_del": "Eliminar Todas las Lecturas",
    "btn_cancel": "Cancelar Lectura",

    # --- BOTONES COMUNES ---
    "btn_ok": "Aceptar",
    "btn_yes": "Sí",
    "btn_no": "No",
    "btn_save_changes": "Guardar Cambios",
    "btn_cancel_simple": "Cancelar",
    "btn_restore_defaults": "Restaurar Ajustes",
    "btn_autodetect": "Autodetectar",
    "btn_continue_external": "Continuar",
    "btn_format_txt": "TXT",
    "btn_format_md": "MD",

    # --- DIALOGOS TAGS ---
    "dlg_ver_title": "Configurar qué Ver",
    "dlg_ver_folder_prompt": "Carpetas a resaltar como Importantes (ej: src, utils):",
    "dlg_ver_file_prompt": "Extensiones de archivo a Leer (ej: .py, .md):",

    "dlg_nover_title": "Configurar qué No Ver",
    "dlg_nover_folder_prompt": "Carpetas a Ignorar por completo (ej: node_modules, .venv):",
    "dlg_nover_file_prompt": "Archivos a Ignorar por nombre completo (ej: license.txt, .env):",
    "chk_use_gitignore": "Excluir usando .gitignore",

    "dlg_etiqueta_title": "Configurar Multimedia y Binarios",
    "dlg_etiqueta_file_prompt": "Extensiones a Omitir Contenido (Solo Listar):",

    "placeholder_tags": "Escribir y presionar Enter para añadir...",
    "msg_tag_conflict": "La etiqueta '{}' ya existe en la configuración de 'Ver' o 'No Ver'.\nPor prioridad, no puede añadirla aquí.",
    "msg_autodetect_result": "Se detectaron y añadieron {} nuevas extensiones.",
    "msg_autodetect_none": "No se encontraron nuevas extensiones (o ya estaban configuradas/excluidas).",

    # --- PROGRESO ---
    "progress_processing_text": "Procesando...",
    "progress_generating_tree": "Generando árbol de directorios...",
    "progress_done": "¡Completado!",
    "status_waiting": "Esperando lectura",
    "status_reading": "Haciendo lectura",
    "status_done_panel": "¡Completado!",
    "processing_label": "Procesando:",

    # --- MENSAJES ACCIONES ---
    "msg_done": "¡Reporte completo guardado en '{}'!",
    "msg_tree_done": "¡Estructura de árbol guardada en '{}'!",
    "msg_cancelled": "La lectura fue cancelada.",
    "msg_select_dest": "Por favor, primero configure una carpeta de destino.",
    "msg_no_files_found": "No se encontraron archivos válidos para procesar.",
    "msg_no_report_yet": "Aún no se ha generado ningún reporte.",
    "msg_error_generic": "Ocurrió un error inesperado durante la operación.",
    "msg_coming_soon": "Próximamente...",
    "default_report_name": "Reporte",
    "rep_filename_prefix": "Reporte",
    "rep_tree_filename_prefix": "Arbol",

    # --- SELECCION DESTINO ---
    "dlg_dest_choice_title": "Elegir Destino de Reportes",
    "dlg_dest_choice_prompt": "Seleccione dónde guardar los reportes:",
    "dlg_dest_choice_op1": "Usar Ruta por Defecto",
    "dlg_dest_choice_op2": "Elegir Ruta Personalizada",
    "dest_set_default_msg": "Los reportes se guardarán en la ruta por defecto.",
    "dest_set_custom_msg": "Los reportes se guardarán en:\n{}",

    # --- CONFIRMACIONES ---
    "confirm_del_title": "Confirmar Eliminación",
    "confirm_del_prompt": "¿Está seguro de que desea eliminar permanentemente la carpeta de lecturas y todo su contenido?",
    "msg_delete_success": "Contenido de '{}' eliminado con éxito.",
    "msg_delete_error": "No se pudo eliminar la carpeta:\n{}",

    "confirm_restore_title": "Confirmar Restauración",
    "confirm_restore_prompt": "¿Está seguro de que desea restaurar todos los ajustes a sus valores por defecto?\n\nEsto eliminará sus configuraciones guardadas.",
    "msg_restore_success": "¡Ajustes restaurados a los valores por defecto!",
    "dlg_external_link_title": "Abrir enlace externo",
    "msg_open_repository_confirm": "Se abrirá el navegador para abrir el repositorio. ¿Desea continuar?",
    "msg_open_manual_confirm": "Se abrirá el navegador para abrir el manual/documentación. ¿Desea continuar?",

    # --- PERFILES ---
    "dlg_profiles_title": "Gestión de Perfiles",
    "lbl_select_profile": "Seleccione un Perfil de Trabajo",
    "ph_new_profile": "Nombre nuevo perfil (ej: Python)...",
    "msg_profile_exists": "Ya existe un perfil con ese nombre.",
    "confirm_del_profile": "¿Eliminar el perfil '{}'?\nEsta acción no se puede deshacer.",
    "msg_profile_changed": "Perfil '{}' activado.\nEntorno reconfigurado.",
    "msg_max_profiles_reached": "Máx. 5 perfiles",
    "lbl_default_name": "Predeterminado",
    "lbl_active_suffix": " (Activo)",

    # --- SETTINGS ---
    "dlg_settings_title": "Configuración General",
    "lbl_report_format": "Formato de archivo:",
    "lbl_exe_path": "Ruta de la aplicación ({}):",
    "lbl_exe_example": "Ejemplo: C:\\Users\\TuUsuario\\Downloads\\{}",
    "ph_exe_path": "Pegue la ruta aquí...",
    "lbl_system_shortcuts": "Accesos directos e integración:",
    "btn_shortcut_desktop": "Crear acceso directo en Escritorio",
    "btn_shortcut_start": "Añadir al Menú de Programas",
    "btn_shortcut_taskbar": "Anclar a Barra de Tareas",
    "btn_shortcut_pin_start": "Anclar a Inicio",
    "lbl_system_shortcuts_linux": "Integración con Linux:",
    "btn_shortcut_desktop_linux": "Crear acceso directo en Escritorio",
    "btn_shortcut_start_linux": "Añadir al Menú de Aplicaciones",
    "lbl_config_transfer": "Importación y exportación de configuración:",
    "lbl_config_transfer_desc": "Exporte toda la configuración actual a un archivo JSON o importe una configuración previamente exportada para replicar este entorno.",
    "btn_export_config": "Exportar configuración",
    "btn_import_config": "Importar configuración",
    "dlg_export_config_title": "Exportar Configuración",
    "dlg_import_config_title": "Importar Configuración",
    "filetype_config_json": "Configuración de Lectorcito Pro",
    "filetype_json": "Archivos JSON",
    "filetype_all": "Todos los archivos",
    "confirm_import_config_title": "Confirmar Importación",
    "confirm_import_config_prompt": "¿Desea importar esta configuración?\n\nSe sobrescribirá toda la configuración actual de la aplicación, incluidos el perfil activo, los perfiles guardados, tema, idioma, rutas, filtros y preferencias.\n\nEsta acción reemplazará su configuración actual.",
    "msg_export_success": "Configuración exportada correctamente.\n\nArchivo:\n{}",
    "msg_export_error": "No se pudo exportar la configuración:\n{}",
    "msg_import_success": "Configuración importada correctamente.\n\nArchivo:\n{}",
    "msg_import_error": "No se pudo importar la configuración:\n{}",

    "msg_shortcut_desktop_ok": "¡Acceso directo creado en el Escritorio correctamente!",
    "msg_shortcut_start_ok": "¡Añadido a la lista de Programas!\nBúscalo en 'Todas las aplicaciones' del menú Inicio.",
    "msg_shortcut_taskbar_ok": "¡Se intentó anclar a la Barra de Tareas!",
    "msg_shortcut_pin_start_ok": "¡Se intentó anclar a Inicio!",
    "msg_shortcut_linux_desktop_ok": "¡Acceso directo de Linux creado en el Escritorio correctamente!",
    "msg_shortcut_linux_menu_ok": "¡Lectorcito Pro fue añadido al Menú de Aplicaciones correctamente!",

    "msg_shortcut_manual_taskbar": "No se pudo anclar autom.\nSe abrió la carpeta: Arrastre el archivo a la barra.",
    "msg_shortcut_manual_start": "No se pudo anclar autom.\nSe abrió la carpeta: Click derecho > Anclar a inicio.",
    "lnk_name_taskbar": "ARRASTRAME_A_BARRA_DE_TAREAS",
    "lnk_name_start": "CLICK_DERECHO_ANCLAR_A_INICIO",

    "msg_shortcut_error": "No se pudo realizar la acción:\n{}",
    "msg_path_invalid": "La ruta proporcionada no existe o no es un archivo .exe válido.\nPor favor verifique que no tenga comillas.",
    "shortcut_desc": "{} - Análisis de Código",
    "shortcut_script_warning": "AVISO: En modo script, el acceso directo apuntará al intérprete Python.",

    # --- CONTENIDO REPORTE ---
    "rep_title": "LECTORCITO PRO - REPORTE DE PROYECTO",
    "rep_project": "PROYECTO: {}",
    "rep_path": "RUTA: {}",
    "rep_folder": "■ CARPETA: {}",
    "rep_root": "RAÍZ DEL PROYECTO",
    "rep_important": " [IMPORTANTE]",
    "rep_file": "  ● Archivo: {}",
    "rep_file_path": "    Ruta: {}",
    "rep_sep_start": "    >> INICIO DEL CONTENIDO: {}",
    "rep_sep_end": "    << FIN DEL CONTENIDO: {}",
    "rep_read_error": "      [Error al leer el archivo: {}]",
    "rep_md_project_label": "PROYECTO",
    "rep_md_path_label": "RUTA",
    "rep_md_folder_label": "CARPETA",
    "rep_md_file_label": "Archivo",
    "rep_md_important": "IMPORTANTE",
    "rep_md_toc": "Tabla de contenidos",
    "rep_md_content_start": "INICIO DEL CONTENIDO",
    "rep_md_content_end": "FIN DEL CONTENIDO",
    "rep_md_media_notice": "Archivo multimedia listado; contenido no expandido.",
    "rep_md_read_error": "Error al leer el archivo: {}",
    "rep_md_tree_title": "LECTORCITO PRO - ESTRUCTURA DEL PROYECTO",
    "rep_md_tree_structure": "Estructura",
    "rep_md_folder_anchor_prefix": "carpeta",
    "rep_md_file_anchor_prefix": "archivo",

    # --- TOOLTIPS ---
    "tooltip_ver": "Configurar qué carpetas y extensiones incluir en la lectura.",
    "tooltip_nover": "Configurar qué carpetas y archivos completos ignorar.",
    "tooltip_etiqueta": "Configurar archivos que se listarán pero sin leer su contenido.",
    "tooltip_tema": "Cambiar entre el tema claro y el oscuro.",
    "tooltip_idioma": "Cambiar entre Español e Inglés.",
    "tooltip_restaurar": "Restaurar todas las configuraciones a su estado inicial.",
    "tooltip_github": "Abrir el repositorio del proyecto en GitHub.",
    "tooltip_perfil": "Gestionar perfiles de configuración (ej: Java, Python).",
    "tooltip_info": "Abrir el manual de usuario y documentación online.",
    "tooltip_ajustes": "Configuración general, formato de reportes y accesos directos."
},

"en": {
    # --- GENERAL ---
    "title": "LECTORCITO PRO",
    "welcome": ", please select an option.",
    "footer_copyright": "Copyright © {} - {}",
    "manual_title": "User Manual",
    "info_title": "Information",
    "error_title": "Error",
    "critical_error_title": "Critical Error {}",
    "critical_error_message": "Critical error:\n\n{}\n\nDetails at:\n{}",
    "fallback_user": "User",

    # --- GREETINGS ---
    "greet_m": ["Good morning!", "Coffee and code, let's go!", "Ready for a new day?",
                "Have a productive morning!"],
    "greet_a": ["Good afternoon!", "Hope your day is going great.", "Let's keep pushing that code!",
                "The afternoon is for creating."],
    "greet_n": ["Good evening!", "One last look before logging off.", "May the code be with you.",
                "Time to compile some dreams."],

    # --- MAIN BUTTONS ---
    "btn_sel_lecturas": "Select Readings Destination",
    "btn_choose_folder": "Generate Full Report",
    "btn_create_tree": "Create Tree Structure",
    "btn_open_lecturas": "Open Readings Folder",
    "btn_open_last": "Open Last Report",
    "btn_del": "Delete All Readings",
    "btn_cancel": "Cancel Reading",

    # --- COMMON BUTTONS ---
    "btn_ok": "OK",
    "btn_yes": "Yes",
    "btn_no": "No",
    "btn_save_changes": "Save Changes",
    "btn_cancel_simple": "Cancel",
    "btn_restore_defaults": "Restore Defaults",
    "btn_autodetect": "Auto-detect",
    "btn_continue_external": "Continue",
    "btn_format_txt": "TXT",
    "btn_format_md": "MD",

    # --- DIALOGS ---
    "dlg_ver_title": "Configure what to View",
    "dlg_ver_folder_prompt": "Folders to highlight as Important (e.g., src, utils):",
    "dlg_ver_file_prompt": "File extensions to Read (e.g., .py, .md):",

    "dlg_nover_title": "Configure what Not to View",
    "dlg_nover_folder_prompt": "Folders to Ignore completely (e.g., node_modules, .venv):",
    "dlg_nover_file_prompt": "Files to Ignore by full name (e.g., license.txt, .env):",
    "chk_use_gitignore": "Exclude using .gitignore",

    "dlg_etiqueta_title": "Configure Multimedia & Binaries",
    "dlg_etiqueta_file_prompt": "Extensions to Skip Content (List Only):",

    "placeholder_tags": "Type and press Enter to add...",
    "msg_tag_conflict": "The tag '{}' already exists in 'View' or 'No View' settings.\nDue to priority, it cannot be added here.",
    "msg_autodetect_result": "Detected and added {} new extensions.",
    "msg_autodetect_none": "No new extensions found (or they were already configured/excluded).",

    # --- PROGRESS ---
    "progress_processing_text": "Processing...",
    "progress_generating_tree": "Generating directory tree...",
    "progress_done": "Completed!",
    "status_waiting": "Waiting for reading",
    "status_reading": "Reading in progress",
    "status_done_panel": "Completed!",
    "processing_label": "Processing:",

    # --- MESSAGES ---
    "msg_done": "Full report saved in '{}'!",
    "msg_tree_done": "Directory tree saved in '{}'!",
    "msg_cancelled": "The reading process was cancelled.",
    "msg_select_dest": "Please set a destination folder first.",
    "msg_no_files_found": "No valid files were found to process.",
    "msg_no_report_yet": "No report has been generated yet.",
    "msg_error_generic": "An unexpected error occurred during the operation.",
    "msg_coming_soon": "Coming soon...",
    "default_report_name": "Report",
    "rep_filename_prefix": "Report",
    "rep_tree_filename_prefix": "Tree",

    # --- DESTINATION ---
    "dlg_dest_choice_title": "Choose Report Destination",
    "dlg_dest_choice_prompt": "Select where to save the reports:",
    "dlg_dest_choice_op1": "Use Default Path",
    "dlg_dest_choice_op2": "Choose Custom Path",
    "dest_set_default_msg": "Reports will be saved to the default path.",
    "dest_set_custom_msg": "Reports will be saved to:\n{}",

    # --- DELETION ---
    "confirm_del_title": "Confirm Deletion",
    "confirm_del_prompt": "Are you sure you want to permanently delete the readings folder and all its contents?",
    "msg_delete_success": "Contents of '{}' deleted successfully.",
    "msg_delete_error": "Could not delete the folder:\n{}",

    "confirm_restore_title": "Confirm Restore",
    "confirm_restore_prompt": "Are you sure you want to restore all settings to their default values?\n\nThis will delete your saved configurations.",
    "msg_restore_success": "Settings have been restored to default!",
    "dlg_external_link_title": "Open external link",
    "msg_open_repository_confirm": "The browser will open to access the repository. Do you want to continue?",
    "msg_open_manual_confirm": "The browser will open to access the manual/documentation. Do you want to continue?",

    # --- PROFILES ---
    "dlg_profiles_title": "Profile Management",
    "lbl_select_profile": "Select Work Profile",
    "ph_new_profile": "New profile name (e.g. Python)...",
    "msg_profile_exists": "A profile with that name already exists.",
    "confirm_del_profile": "Delete profile '{}'?\nThis action cannot be undone.",
    "msg_profile_changed": "Profile '{}' activated.\nEnvironment reconfigured.",
    "msg_max_profiles_reached": "Max 5 profiles",
    "lbl_default_name": "Default",
    "lbl_active_suffix": " (Active)",

    # --- SETTINGS ---
    "dlg_settings_title": "General Settings",
    "lbl_report_format": "Report File Format:",
    "lbl_exe_path": "Application Path ({}):",
    "lbl_exe_example": "Ex: C:\\Users\\User\\Downloads\\{}",
    "ph_exe_path": "Paste path here...",
    "lbl_system_shortcuts": "System Integration:",
    "btn_shortcut_desktop": "Create Desktop Shortcut",
    "btn_shortcut_start": "Add to Programs Menu",
    "btn_shortcut_taskbar": "Pin to Taskbar",
    "btn_shortcut_pin_start": "Pin to Start",
    "lbl_system_shortcuts_linux": "Linux Integration:",
    "btn_shortcut_desktop_linux": "Create Desktop Shortcut",
    "btn_shortcut_start_linux": "Add to Applications Menu",
    "lbl_config_transfer": "Configuration import and export:",
    "lbl_config_transfer_desc": "Export the entire current configuration to a JSON file or import a previously exported configuration to replicate this environment.",
    "btn_export_config": "Export configuration",
    "btn_import_config": "Import configuration",
    "dlg_export_config_title": "Export Configuration",
    "dlg_import_config_title": "Import Configuration",
    "filetype_config_json": "Lectorcito Pro Configuration",
    "filetype_json": "JSON Files",
    "filetype_all": "All files",
    "confirm_import_config_title": "Confirm Import",
    "confirm_import_config_prompt": "Do you want to import this configuration?\n\nThis will overwrite the entire current application configuration, including the active profile, saved profiles, theme, language, paths, filters and preferences.\n\nThis action will replace your current configuration.",
    "msg_export_success": "Configuration exported successfully.\n\nFile:\n{}",
    "msg_export_error": "The configuration could not be exported:\n{}",
    "msg_import_success": "Configuration imported successfully.\n\nFile:\n{}",
    "msg_import_error": "The configuration could not be imported:\n{}",

    "msg_shortcut_desktop_ok": "Desktop shortcut created successfully!",
    "msg_shortcut_start_ok": "Added to Windows Programs list!",
    "msg_shortcut_taskbar_ok": "Attempted to pin to Taskbar!",
    "msg_shortcut_pin_start_ok": "Attempted to pin to Start!",
    "msg_shortcut_linux_desktop_ok": "Linux desktop shortcut created successfully!",
    "msg_shortcut_linux_menu_ok": "Lectorcito Pro was added to the Applications Menu successfully!",

    "msg_shortcut_manual_taskbar": "Auto-pin failed.\nFolder opened: Drag the file to Taskbar.",
    "msg_shortcut_manual_start": "Auto-pin failed.\nFolder opened: Right click > Pin to Start.",
    "lnk_name_taskbar": "DRAG_ME_TO_TASKBAR",
    "lnk_name_start": "RIGHT_CLICK_PIN_TO_START",

    "msg_shortcut_error": "Could not perform action:\n{}",
    "msg_path_invalid": "The provided path does not exist or is not a valid .exe file.\nPlease check (no quotes).",
    "shortcut_desc": "{} - Code Analysis",
    "shortcut_script_warning": "WARNING: In script mode, the shortcut will point to the Python interpreter.",

    # --- REPORT CONTENT ---
    "rep_title": "LECTORCITO PRO - PROJECT REPORT",
    "rep_project": "PROJECT: {}",
    "rep_path": "PATH: {}",
    "rep_folder": "■ FOLDER: {}",
    "rep_root": "PROJECT ROOT",
    "rep_important": " [IMPORTANT]",
    "rep_file": "  ● File: {}",
    "rep_file_path": "    Path: {}",
    "rep_sep_start": "    >> CONTENT START: {}",
    "rep_sep_end": "    << CONTENT END: {}",
    "rep_read_error": "      [Error reading file: {}]",
    "rep_md_project_label": "PROJECT",
    "rep_md_path_label": "PATH",
    "rep_md_folder_label": "FOLDER",
    "rep_md_file_label": "File",
    "rep_md_important": "IMPORTANT",
    "rep_md_toc": "Table of contents",
    "rep_md_content_start": "CONTENT START",
    "rep_md_content_end": "CONTENT END",
    "rep_md_media_notice": "Multimedia file listed; content not expanded.",
    "rep_md_read_error": "Error reading file: {}",
    "rep_md_tree_title": "LECTORCITO PRO - PROJECT STRUCTURE",
    "rep_md_tree_structure": "Structure",
    "rep_md_folder_anchor_prefix": "folder",
    "rep_md_file_anchor_prefix": "file",

    # --- TOOLTIPS ---
    "tooltip_ver": "Configure which folders and extensions to include in the reading.",
    "tooltip_nover": "Configure which folders and full filenames to ignore.",
    "tooltip_etiqueta": "Configure files to list without reading their content.",
    "tooltip_tema": "Toggle between light and dark theme.",
    "tooltip_idioma": "Switch between English and Spanish.",
    "tooltip_restaurar": "Restore all settings to their default state.",
    "tooltip_github": "Open the project repository on GitHub.",
    "tooltip_perfil": "Manage configuration profiles (e.g., Java, Python).",
    "tooltip_info": "Open the user manual and online documentation.",
    "tooltip_ajustes": "General settings, report format, and shortcuts."
}
}

def translate(language: str, key: str, *args):
    entry = TRANSLATIONS.get(language, TRANSLATIONS["es"]).get(key, f"<{key}>")
    if isinstance(entry, list):
        entry = entry[0] if entry else f"<{key}>"
    try:
        return entry.format(*args)
    except Exception:
        return entry


def translate_default(key: str, *args):
    return translate("es", key, *args)

