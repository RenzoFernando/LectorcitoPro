TRANSLATIONS = {
    "es": {
        # --- GENERAL / INTERFAZ PRINCIPAL ---
        "title": "LECTORCITO PRO",
        "welcome": ", por favor seleccione una opción.",
        "footer_copyright": "Copyright © {} - {} - Todos los derechos reservados.",
        "manual_title": "Manual de Usuario",
        "info_title": "Información",
        "error_title": "Error",

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

        # --- BOTONES DE DIÁLOGOS ---
        "btn_ok": "OK",
        "btn_yes": "Sí",
        "btn_no": "No",
        "btn_save_changes": "Guardar Cambios",
        "btn_cancel_simple": "Cancelar",
        "btn_restore_defaults": "Restaurar Ajustes",
        "btn_autodetect": "Autodetectar",

        # --- DIÁLOGOS DE CONFIGURACIÓN (VER/NO VER/ETIQUETAS) ---
        "dlg_ver_title": "Configurar qué Ver",
        "dlg_ver_folder_prompt": "Carpetas a resaltar como Importantes (ej: src, utils):",
        "dlg_ver_file_prompt": "Extensiones de archivo a Leer (ej: .py, .md):",

        "dlg_nover_title": "Configurar qué No Ver",
        "dlg_nover_folder_prompt": "Carpetas a Ignorar por completo (ej: node_modules, .venv):",
        "dlg_nover_file_prompt": "Archivos a Ignorar por nombre completo (ej: license.txt, .env):",

        "dlg_etiqueta_title": "Configurar Multimedia y Binarios",
        "dlg_etiqueta_file_prompt": "Extensiones a Omitir Contenido (Solo Listar):",

        "placeholder_tags": "Escribir y presionar Enter para añadir...",

        # --- MENSAJES DE ESTADO Y PROGRESO ---
        "progress_processing_text": "Procesando...",
        "progress_generating_tree": "Generando árbol de directorios...",
        "progress_done": "¡Completado!",
        "status_waiting": "Esperando lectura",
        "status_reading": "Haciendo lectura",
        "status_done_panel": "¡Completado!",
        "processing_label": "Procesando:",

        # --- MENSAJES DE ACCIONES ---
        "msg_done": "¡Reporte completo guardado en '{}'!",
        "msg_tree_done": "¡Estructura de árbol guardada en '{}'!",
        "msg_cancelled": "La lectura fue cancelada.",
        "msg_select_dest": "Por favor, primero configure una carpeta de destino.",
        "msg_no_files_found": "No se encontraron archivos válidos para procesar.",
        "msg_no_report_yet": "Aún no se ha generado ningún reporte.",
        "msg_infographic_error": "No se pudo cargar la infografía.\nVerifique que 'Infografía_LectorcitoPro.png' exista en la carpeta 'recursos'.",
        "msg_error_generic": "Ocurrió un error inesperado durante la operación.",
        "msg_coming_soon": "Próximamente...",  # NUEVO

        # --- CONFLICTOS DE ETIQUETAS ---
        "msg_tag_conflict": "La etiqueta '{}' ya existe en la configuración de 'Ver' o 'No Ver'.\nPor prioridad, no puede añadirla aquí.",

        "msg_autodetect_result": "Se detectaron y añadieron {} nuevas extensiones.",
        "msg_autodetect_none": "No se encontraron nuevas extensiones (o ya estaban configuradas/excluidas).",

        # --- DESTINO DE GUARDADO ---
        "dlg_dest_choice_title": "Elegir Destino de Reportes",
        "dlg_dest_choice_prompt": "Seleccione dónde guardar los reportes:",
        "dlg_dest_choice_op1": "Usar Ruta por Defecto",
        "dlg_dest_choice_op2": "Elegir Ruta Personalizada",
        "dest_set_default_msg": "Los reportes se guardarán en la ruta por defecto.",
        "dest_set_custom_msg": "Los reportes se guardarán en:\n{}",

        # --- ELIMINACIÓN Y RESTAURACIÓN ---
        "confirm_del_title": "Confirmar Eliminación",
        "confirm_del_prompt": "¿Está seguro de que desea eliminar permanentemente la carpeta de lecturas y todo su contenido?",
        "msg_delete_success": "Contenido de '{}' eliminado con éxito.",
        "msg_delete_error": "No se pudo eliminar la carpeta:\n{}",

        "confirm_restore_title": "Confirmar Restauración",
        "confirm_restore_prompt": "¿Está seguro de que desea restaurar todos los ajustes a sus valores por defecto?\n\nEsto eliminará sus configuraciones guardadas.",
        "msg_restore_success": "¡Ajustes restaurados a los valores por defecto!",

        # --- PERFILES ---
        "dlg_profiles_title": "Gestión de Perfiles",
        "lbl_select_profile": "Seleccione un Perfil de Trabajo",
        "ph_new_profile": "Nombre nuevo perfil (ej: Python)...",
        "msg_profile_exists": "Ya existe un perfil con ese nombre.",
        "confirm_del_profile": "¿Eliminar el perfil '{}'?\nEsta acción no se puede deshacer.",
        "msg_profile_changed": "Perfil '{}' activado.\nEntorno reconfigurado.",

        # --- TOOLTIPS ---
        "tooltip_ver": "Configurar qué carpetas y extensiones incluir en la lectura.",
        "tooltip_nover": "Configurar qué carpetas y archivos completos ignorar.",
        "tooltip_etiqueta": "Configurar archivos que se listarán pero sin leer su contenido.",
        "tooltip_tema": "Cambiar entre el tema claro y el oscuro.",
        "tooltip_idioma": "Cambiar entre Español e Inglés.",
        "tooltip_restaurar": "Restaurar todas las configuraciones a su estado inicial.",
        "tooltip_github": "Abrir el repositorio del proyecto en GitHub.",
        "tooltip_perfil": "Gestionar perfiles de configuración (ej: Java, Python).",
        "tooltip_info": "Mostrar el manual de usuario y la información de la aplicación.",
        "tooltip_ajustes": "Configuración general de la aplicación."
    },

    "en": {
        # --- GENERAL / MAIN INTERFACE ---
        "title": "LECTORCITO PRO",
        "welcome": ", please select an option.",
        "footer_copyright": "Copyright © {} - {} - All Rights Reserved.",
        "manual_title": "User Manual",
        "info_title": "Information",
        "error_title": "Error",

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

        # --- DIALOG BUTTONS ---
        "btn_ok": "OK",
        "btn_yes": "Yes",
        "btn_no": "No",
        "btn_save_changes": "Save Changes",
        "btn_cancel_simple": "Cancel",
        "btn_restore_defaults": "Restore Defaults",
        "btn_autodetect": "Auto-detect",

        # --- CONFIG DIALOGS ---
        "dlg_ver_title": "Configure what to View",
        "dlg_ver_folder_prompt": "Folders to highlight as Important (e.g., src, utils):",
        "dlg_ver_file_prompt": "File extensions to Read (e.g., .py, .md):",

        "dlg_nover_title": "Configure what Not to View",
        "dlg_nover_folder_prompt": "Folders to Ignore completely (e.g., node_modules, .venv):",
        "dlg_nover_file_prompt": "Files to Ignore by full name (e.g., license.txt, .env):",

        "dlg_etiqueta_title": "Configure Multimedia & Binaries",
        "dlg_etiqueta_file_prompt": "Extensions to Skip Content (List Only):",

        "placeholder_tags": "Type and press Enter to add...",

        # --- STATUS AND PROGRESS ---
        "progress_processing_text": "Processing...",
        "progress_generating_tree": "Generating directory tree...",
        "progress_done": "Completed!",
        "status_waiting": "Waiting for reading",
        "status_reading": "Reading in progress",
        "status_done_panel": "Completed!",
        "processing_label": "Processing:",

        # --- ACTION MESSAGES ---
        "msg_done": "Full report saved in '{}'!",
        "msg_tree_done": "Directory tree saved in '{}'!",
        "msg_cancelled": "The reading process was cancelled.",
        "msg_select_dest": "Please set a destination folder first.",
        "msg_no_files_found": "No valid files were found to process.",
        "msg_no_report_yet": "No report has been generated yet.",
        "msg_infographic_error": "Could not load the infographic.\nPlease ensure 'Infografía_LectorcitoPro.png' exists in the 'recursos' folder.",
        "msg_error_generic": "An unexpected error occurred during the operation.",
        "msg_coming_soon": "Coming soon...",  # NUEVO

        "msg_tag_conflict": "The tag '{}' already exists in 'View' or 'No View' settings.\nDue to priority, it cannot be added here.",

        "msg_autodetect_result": "Detected and added {} new extensions.",
        "msg_autodetect_none": "No new extensions found (or they were already configured/excluded).",

        # --- SAVE DESTINATION ---
        "dlg_dest_choice_title": "Choose Report Destination",
        "dlg_dest_choice_prompt": "Select where to save the reports:",
        "dlg_dest_choice_op1": "Use Default Path",
        "dlg_dest_choice_op2": "Choose Custom Path",
        "dest_set_default_msg": "Reports will be saved to the default path.",
        "dest_set_custom_msg": "Reports will be saved to:\n{}",

        # --- DELETION AND RESTORE ---
        "confirm_del_title": "Confirm Deletion",
        "confirm_del_prompt": "Are you sure you want to permanently delete the readings folder and all its contents?",
        "msg_delete_success": "Contents of '{}' deleted successfully.",
        "msg_delete_error": "Could not delete the folder:\n{}",

        "confirm_restore_title": "Confirm Restore",
        "confirm_restore_prompt": "Are you sure you want to restore all settings to their default values?\n\nThis will delete your saved configurations.",
        "msg_restore_success": "Settings have been restored to default!",

        # --- PROFILES ---
        "dlg_profiles_title": "Profile Management",
        "lbl_select_profile": "Select Work Profile",
        "ph_new_profile": "New profile name (e.g. Python)...",
        "msg_profile_exists": "A profile with that name already exists.",
        "confirm_del_profile": "Delete profile '{}'?\nThis action cannot be undone.",
        "msg_profile_changed": "Profile '{}' activated.\nEnvironment reconfigured.",

        # --- TOOLTIPS ---
        "tooltip_ver": "Configure which folders and extensions to include in the reading.",
        "tooltip_nover": "Configure which folders and full filenames to ignore.",
        "tooltip_etiqueta": "Configure files to list without reading their content.",
        "tooltip_tema": "Toggle between light and dark theme.",
        "tooltip_idioma": "Switch between English and Spanish.",
        "tooltip_restaurar": "Restore all settings to their default state.",
        "tooltip_github": "Open the project repository on GitHub.",
        "tooltip_perfil": "Manage configuration profiles (e.g., Java, Python).",
        "tooltip_info": "Show the user manual and application information.",
        "tooltip_ajustes": "General application settings."
    }
}