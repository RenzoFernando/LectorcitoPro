import customtkinter as ctk
from tkinter import Canvas
from PIL import Image
import webbrowser
import datetime
import os
from utils import resource_path

# --- Constantes de la Interfaz ---
VERSION = "4.10.2"
YEAR = datetime.datetime.now().year
AUTHOR = "Renzo Fernando Mosquera Daza"
REPO_URL = "https://github.com/RenzoFernando/LectorcitoPro.git"

# --- Paleta de Colores y Geometría ---
COLORS = {
    "light": {"bg": "#EBEBEB", "text": "#000000", "left_bar": "#1A1E22", "progress_bar": "#D9D9D9"},
    "dark": {"bg": "#1A1E22", "text": "#FFFFFF", "left_bar": "#EBEBEB", "progress_bar": "#333333"},
    "button": {"blue": "#3B8ED0", "green": "#3BD056", "red": "#D03B3D"},
    "button_hover": {"blue_h": "#3073A8", "green_h": "#2FA047", "red_h": "#A03031"}
}
BTN_W_MAIN, BTN_H_MAIN = 250, 30
BTN_W_ICON, BTN_H_ICON = 35, 35
PROGRESS_W = 357

# --- DIÁLOGOS PERSONALIZADOS ---
class BaseDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()

        def _set_icon():
            try:
                if hasattr(parent, '_icon_path') and parent._icon_path and os.path.exists(parent._icon_path):
                    self.iconbitmap(parent._icon_path)
            except Exception as e:
                print(f"Error al establecer el icono de la sub-ventana: {e}")

        self.after(200, _set_icon)
        self.result = None
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind("<Escape>", lambda e: self._on_cancel())

    def _on_ok(self, event=None):
        self.destroy()

    def _on_cancel(self, event=None):
        self.destroy()


class FilterConfigDialog(BaseDialog):
    """Un diálogo para configurar filtros de carpetas y archivos en dos campos."""

    def __init__(self, parent, title, folder_prompt, file_prompt, initial_folder_value, initial_file_value):
        super().__init__(parent, title)

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # --- Campo de Carpetas ---
        ctk.CTkLabel(main_frame, text=folder_prompt, wraplength=350, font=("Segoe UI", 12, "bold")).pack(fill="x",
                                                                                                        pady=(0, 5))
        self.folder_entry = ctk.CTkEntry(main_frame, width=350)
        self.folder_entry.insert(0, initial_folder_value)
        self.folder_entry.pack(fill="x", pady=(0, 15))

        # --- Campo de Archivos ---
        ctk.CTkLabel(main_frame, text=file_prompt, wraplength=350, font=("Segoe UI", 12, "bold")).pack(fill="x",
                                                                                                    pady=(0, 5))
        self.file_entry = ctk.CTkEntry(main_frame, width=350)
        self.file_entry.insert(0, initial_file_value)
        self.file_entry.pack(fill="x", pady=(0, 20))

        self.folder_entry.focus_set()

        # --- Botones ---
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()
        ctk.CTkButton(button_frame, text="OK", width=100, command=self._on_ok).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Cancelar", width=100, command=self._on_cancel).pack(side="left", padx=10)

    def _on_ok(self, event=None):
        self.result = (self.folder_entry.get(), self.file_entry.get())
        super()._on_ok()

    @classmethod
    def get_input(cls, parent, title, folder_prompt, file_prompt, initial_folder_value, initial_file_value):
        dialog = cls(parent, title, folder_prompt, file_prompt, initial_folder_value, initial_file_value)
        parent.wait_window(dialog)
        return dialog.result


class MessageDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, justify="center").pack(fill="x", pady=(0, 20))
        ok_button = ctk.CTkButton(main_frame, text="OK", width=100, command=self._on_ok)
        ok_button.pack(pady=(0, 10))
        ok_button.focus_set()
        self.bind("<Return>", self._on_ok)


class ConfirmDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        self.result = False
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, justify="center").pack(fill="x", pady=(0, 20))
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()
        ctk.CTkButton(button_frame, text="Sí", width=100, command=self._on_yes).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="No", width=100, command=self._on_no).pack(side="left", padx=10)

    def _on_yes(self): self.result = True; super()._on_ok()

    def _on_no(self): self.result = False; super()._on_cancel()

    @classmethod
    def ask(cls, parent, title, message):
        dialog = cls(parent, title, message)
        parent.wait_window(dialog)
        return dialog.result


class ChoiceDialog(BaseDialog):
    def __init__(self, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        super().__init__(parent, title)
        self.option1_value = option1_value
        self.option2_value = option2_value
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350).pack(fill="x", pady=(0, 20))
        ctk.CTkButton(main_frame, text=option1_text, width=200, command=self._on_option1).pack(pady=5)
        ctk.CTkButton(main_frame, text=option2_text, width=200, command=self._on_option2).pack(pady=5)

    def _on_option1(self): self.result = self.option1_value; self._on_ok()

    def _on_option2(self): self.result = self.option2_value; self._on_ok()

    @classmethod
    def ask(cls, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        dialog = cls(parent, title, message, option1_text, option2_text, option1_value, option2_value)
        parent.wait_window(dialog)
        return dialog.result


# --- CLASE PRINCIPAL DE LA VISTA ---
class LectorcitoApp(ctk.CTk):
    TRANSLATIONS = {
        "es": {
            "btn_restore_defaults": "Restaurar Ajustes", "confirm_restore_title": "Confirmar Restauración",
            "confirm_restore_prompt": "¿Está seguro de que desea restaurar todos los ajustes a sus valores por defecto?\n\nEsto eliminará sus configuraciones guardadas.",
            "msg_restore_success": "¡Ajustes restaurados a los valores por defecto!",
            "btn_create_tree": "Crear Estructura de Árbol",
            "dlg_tree_choice_title": "Tipo de Árbol",
            "dlg_tree_choice_prompt": "Seleccione cómo generar la estructura del árbol:",
            "dlg_tree_op1": "Completo (ignorar filtros)", "dlg_tree_op2": "Filtrado (usar configuración)",
            "msg_tree_done": "¡Árbol de directorios guardado en '{}'!", "btn_cancel": "Cancelar Lectura",
            "msg_cancelled": "La lectura fue cancelada.", "error_title": "Error",
            "msg_error_generic": "Ocurrió un error inesperado durante la operación.",
            "dlg_dest_choice_title": "Elegir Destino de Reportes",
            "dlg_dest_choice_prompt": "Seleccione dónde guardar los reportes:",
            "dlg_dest_choice_op1": "Usar Ruta por Defecto", "dlg_dest_choice_op2": "Elegir Ruta Personalizada",
            "dest_set_default_msg": "Los reportes se guardarán en la ruta por defecto.",
            "dest_set_custom_msg": "Los reportes se guardarán en:\n{}",
            "title": "LECTORCITO PRO", "welcome": ", por favor seleccione una opción.",
            "btn_choose_folder": "Elegir Carpeta a Leer", "btn_sel_lecturas": "Seleccionar Destino de Lecturas",
            "btn_open_lecturas": "Abrir Carpeta de Lecturas", "btn_open_last": "Abrir Último Reporte",
            "btn_del": "Eliminar Todas las Lecturas", "msg_done": "¡Listo! Operación completada con éxito.",
            "msg_select_dest": "Por favor, primero configure una carpeta de destino.",
            "msg_no_files_found": "No se encontraron archivos válidos para procesar.",
            "msg_no_report_yet": "Aún no se ha generado ningún reporte.", "info_title": "Información",
            "confirm_del_title": "Confirmar Eliminación",
            "confirm_del_prompt": "¿Está seguro de que desea eliminar permanentemente la carpeta de lecturas y todo su contenido?",
            "msg_delete_success": "Contenido de '{}' eliminado con éxito.",
            "msg_delete_error": "No se pudo eliminar la carpeta:\n{}",
            "greet_m": "Buenos días", "greet_a": "Buenas tardes", "greet_n": "Buenas noches",
            "dlg_ver_title": "Configurar qué Ver",
            "dlg_ver_folder_prompt": "Carpetas a resaltar como Importantes (separadas por comas):",
            "dlg_ver_file_prompt": "Extensiones de archivo a Leer (ej: .py, .md, .txt):",
            "dlg_nover_title": "Configurar qué No Ver",
            "dlg_nover_folder_prompt": "Carpetas a Ignorar por completo (separadas por comas):",
            "dlg_nover_file_prompt": "Archivos a Ignorar por nombre completo (ej: readme.md, license.txt):"
        },
        "en": {
            "btn_restore_defaults": "Restore Defaults", "confirm_restore_title": "Confirm Restore",
            "confirm_restore_prompt": "Are you sure you want to restore all settings to their default values?\n\nThis will delete your saved configurations.",
            "msg_restore_success": "Settings have been restored to default!",
            "btn_create_tree": "Create Directory Tree",
            "dlg_tree_choice_title": "Tree Type",
            "dlg_tree_choice_prompt": "Select how to generate the directory tree:",
            "dlg_tree_op1": "Full (ignore filters)", "dlg_tree_op2": "Filtered (use configuration)",
            "msg_tree_done": "Directory tree saved in '{}'!", "btn_cancel": "Cancel Reading",
            "msg_cancelled": "The reading process was cancelled.", "error_title": "Error",
            "msg_error_generic": "An unexpected error occurred during the operation.",
            "dlg_dest_choice_title": "Choose Report Destination",
            "dlg_dest_choice_prompt": "Select where to save the reports:",
            "dlg_dest_choice_op1": "Use Default Path", "dlg_dest_choice_op2": "Choose Custom Path",
            "dest_set_default_msg": "Reports will be saved to the default path.",
            "dest_set_custom_msg": "Reports will be saved to:\n{}",
            "title": "LECTORCITO PRO", "welcome": ", please select an option.",
            "btn_choose_folder": "Choose Folder to Read", "btn_sel_lecturas": "Select Readings Destination",
            "btn_open_lecturas": "Open Readings Folder", "btn_open_last": "Open Last Report",
            "btn_del": "Delete All Readings", "msg_done": "Done! Operation completed successfully.",
            "msg_select_dest": "Please set a destination folder first.",
            "msg_no_files_found": "No valid files were found to process.",
            "msg_no_report_yet": "No report has been generated yet.", "info_title": "Information",
            "confirm_del_title": "Confirm Deletion",
            "confirm_del_prompt": "Are you sure you want to permanently delete the readings folder and all its contents?",
            "msg_delete_success": "Contents of '{}' deleted successfully.",
            "msg_delete_error": "Could not delete the folder:\n{}",
            "greet_m": "Good morning", "greet_a": "Good afternoon", "greet_n": "Good evening",
            "dlg_ver_title": "Configure what to View",
            "dlg_ver_folder_prompt": "Folders to highlight as Important (comma separated):",
            "dlg_ver_file_prompt": "File extensions to Read (e.g., .py, .md, .txt):",
            "dlg_nover_title": "Configure what Not to View",
            "dlg_nover_folder_prompt": "Folders to Ignore completely (comma separated):",
            "dlg_nover_file_prompt": "Files to Ignore by full name (e.g., readme.md, license.txt):"
        }
    }

    def __init__(self, cfg: dict, controller):
        super().__init__()
        self.config = cfg
        self.controller = controller
        self.lang = self.config.get("language", "es")
        self.current_theme = self.config.get("theme", "Light")

        self.title("Lectorcito Pro")
        self.geometry("600x450")
        self.resizable(False, False)

        self._icon_path = resource_path("lector.ico")
        if os.path.exists(self._icon_path):
            self.iconbitmap(self._icon_path)

        self._load_image_assets()
        self._build_ui()
        self.update_ui_texts()
        self.apply_theme()

    def _tr(self, key, *args):
        return self.TRANSLATIONS.get(self.lang, self.TRANSLATIONS["es"]).get(key, f"<{key}>").format(*args)

    def _load_image_assets(self):
        self.icons = {}
        icon_keys = ["ver", "nover", "restaurar", "traducir", "github", "info"]
        for key in icon_keys:
            try:
                img_for_dark_theme = Image.open(resource_path(f"{key}_oscuro.png"))
                img_for_light_theme = Image.open(resource_path(f"{key}_claro.png"))
                self.icons[key] = ctk.CTkImage(light_image=img_for_light_theme, dark_image=img_for_dark_theme,
                                                size=(22, 22))
            except Exception as e:
                print(f"Error cargando icono '{key}': {e}")
                self.icons[key] = None
        try:
            self.icons['sun'] = ctk.CTkImage(Image.open(resource_path("sol.png")), size=(24, 24))
            self.icons['moon'] = ctk.CTkImage(Image.open(resource_path("luna.png")), size=(24, 24))
        except Exception as e:
            print(f"Error cargando iconos de tema: {e}")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._create_left_sidebar()
        self._create_right_sidebar()
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(60, 80))
        self._create_header(center_frame)
        self._create_main_buttons(center_frame)
        self._create_progress_and_cancel(center_frame)
        self._create_footer()

    def _create_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(pady=(20, 15))
        self.lbl_title = ctk.CTkLabel(header, font=("Segoe UI", 18, "bold"))
        self.lbl_title.pack()
        self.lbl_greet = ctk.CTkLabel(header, font=("Segoe UI", 13))
        self.lbl_greet.pack()

    def _create_main_buttons(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=5, fill="x", expand=True)
        opts = {"width": BTN_W_MAIN, "height": BTN_H_MAIN, "corner_radius": 8, "font": ("Segoe UI", 11, "bold")}
        self.main_buttons = {
            "selpath": ctk.CTkButton(frame, **opts, command=self.controller.select_destination_path),
            "choose": ctk.CTkButton(frame, **opts, command=self.controller.select_folder_to_read),
            "create_tree": ctk.CTkButton(frame, **opts, command=self.controller.create_tree_structure),
            "openlect": ctk.CTkButton(frame, **opts, command=self.controller.open_destination_folder),
            "openlast": ctk.CTkButton(frame, **opts, fg_color=COLORS['button']['green'],
                                    hover_color=COLORS['button_hover']['green_h'],
                                    command=self.controller.open_last_report),
            "delete": ctk.CTkButton(frame, **opts, fg_color=COLORS['button']['red'],
                                    hover_color=COLORS['button_hover']['red_h'],
                                    command=self.controller.delete_all_readings)
        }
        for btn in self.main_buttons.values():
            btn.pack(pady=4)

    def _create_progress_and_cancel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=10, fill="x")
        frame.grid_columnconfigure(0, weight=1)
        self.progress_bar = ctk.CTkProgressBar(frame, width=PROGRESS_W, corner_radius=8, mode='determinate')
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        self.lbl_percent = ctk.CTkLabel(frame, text="0%", font=("Segoe UI", 10))
        self.lbl_percent.grid(row=1, column=0)
        self.btn_cancel = ctk.CTkButton(frame, width=150, height=28, command=self.controller.cancel_processing)
        self.btn_cancel.grid(row=2, column=0, pady=(5, 0))
        self.btn_cancel.grid_remove()

    def _create_left_sidebar(self):
        self.side_left = ctk.CTkFrame(self, width=40, height=350, corner_radius=15)
        self.side_left.place(x=15, y=43)
        self.canvas_left = Canvas(self.side_left, width=25, height=310, highlightthickness=0)
        self.canvas_left.place(relx=0.5, rely=0.5, anchor="center")
        self.canvas_left.bind("<Configure>", self._paint_left_sidebar_text)

    def _create_right_sidebar(self):
        self.side_right = ctk.CTkFrame(self, width=60, height=350, fg_color="transparent")
        self.side_right.place(x=525, y=40)
        # Se actualizan los comandos para llamar a los nuevos métodos del controlador
        button_defs = [
            ("ver", self.controller.show_view_config_dialog),
            ("nover", self.controller.show_no_view_config_dialog),
            ("restaurar", self.controller.restore_default_settings),
            ("theme_icon", self.controller.toggle_theme), ("traducir", self.controller.toggle_language),
            ("github", lambda: webbrowser.open_new(REPO_URL)), ("info", self.show_app_info)
        ]
        self.sidebar_buttons = {}
        theme = COLORS['light' if self.current_theme == "Light" else 'dark']
        btn_color = theme['left_bar']
        for key, cmd in button_defs:
            initial_icon = self.icons.get('moon') if key == "theme_icon" and self.current_theme == "Light" else \
                self.icons.get('sun') if key == "theme_icon" else self.icons.get(key)
            btn = ctk.CTkButton(self.side_right, image=initial_icon, text="", width=BTN_W_ICON, height=BTN_H_ICON,
                                corner_radius=8, command=cmd, fg_color=btn_color, hover_color=btn_color)
            btn.pack(pady=4, padx=5)
            self.sidebar_buttons[key] = btn

    def _create_footer(self):
        footer = ctk.CTkFrame(self, height=30, corner_radius=0)
        footer.grid(row=4, column=0, columnspan=2, sticky="ew")
        ctk.CTkLabel(footer, text=f"Copyright © {YEAR} - {AUTHOR} - All Rights Reserved.", font=("Segoe UI", 9)).place(
            relx=0.5, rely=0.5, anchor="center")

    def update_ui_texts(self):
        self.lbl_title.configure(text=self._tr("title"))
        hour = datetime.datetime.now().hour
        greet_key = "greet_m" if 5 <= hour < 12 else "greet_a" if 12 <= hour < 19 else "greet_n"
        try:
            user = os.getlogin()
        except OSError:
            user = "User"
        self.lbl_greet.configure(text=f"{self._tr(greet_key)} {user}{self._tr('welcome')}")
        key_map = {
            "selpath": "btn_sel_lecturas", "choose": "btn_choose_folder", "create_tree": "btn_create_tree",
            "openlect": "btn_open_lecturas", "openlast": "btn_open_last", "delete": "btn_del"
        }
        for key, btn in self.main_buttons.items():
            if key in key_map:
                btn.configure(text=self._tr(key_map[key]))
        self.btn_cancel.configure(text=self._tr("btn_cancel"))

    def apply_theme(self):
        is_light = self.current_theme == "Light"
        ctk.set_appearance_mode(self.current_theme)
        theme = COLORS['light' if is_light else 'dark']
        self.configure(fg_color=theme['bg'])
        self.side_left.configure(fg_color=theme['left_bar'])
        self.canvas_left.configure(bg=theme['left_bar'])
        self._paint_left_sidebar_text()
        self.progress_bar.configure(progress_color=COLORS['button']['blue'], fg_color=theme['progress_bar'])
        btn_color = theme['left_bar']
        for btn in self.sidebar_buttons.values():
            btn.configure(fg_color=btn_color, hover_color=btn_color)
        self.sidebar_buttons['theme_icon'].configure(
            image=self.icons.get('moon') if is_light else self.icons.get('sun'))

    def _paint_left_sidebar_text(self, event=None):
        self.canvas_left.delete("all")
        w, h = self.canvas_left.winfo_width(), self.canvas_left.winfo_height()
        color = COLORS['dark']['text'] if self.current_theme == "Light" else COLORS['light']['text']
        self.canvas_left.create_text(w / 2, h / 2, text=f"Lectorcito Pro v{VERSION}", angle=90,
                                font=("Segoe UI", 10, "bold"), fill=color)

    def set_progress(self, percentage):
        self.progress_bar.set(percentage / 100)
        self.lbl_percent.configure(text=f"{int(percentage)}%")
        self.update_idletasks()

    def toggle_ui_for_processing(self, is_active: bool):
        state = "disabled" if is_active else "normal"
        for btn in self.main_buttons.values():
            btn.configure(state=state)
        for btn in self.sidebar_buttons.values():
            btn.configure(state=state)
        if is_active:
            self.btn_cancel.grid()
        else:
            self.btn_cancel.grid_remove()

    def show_message(self, title_key: str, message_key: str, *args):
        MessageDialog(self, self._tr(title_key), self._tr(message_key, *args))

    def show_app_info(self):
        info_text = (f"Lectorcito Pro v{VERSION}\n\n"
                    f"Desarrollado por: \n{AUTHOR}\n\n"
                    f"Repositorio: {REPO_URL}\n\n"
                    f"© {YEAR} - All Rights Reserved.")
        MessageDialog(self, self._tr("info_title"), info_text)
