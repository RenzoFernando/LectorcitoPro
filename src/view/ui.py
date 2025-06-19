import customtkinter as ctk
from tkinter import Canvas, filedialog
from PIL import Image
import webbrowser
import datetime
import os
from utils import resource_path

# --- Constantes de la Interfaz ---
VERSION = "4.4.0"  # Versión actualizada con cancelación
YEAR = datetime.datetime.now().year
AUTHOR = "Renzo Fernando Mosquera Daza"
REPO_URL = "https://github.com/RenzoFernando/LectorcitoPro.git"

# --- Paleta de Colores ---
COLORS = {
    "light": {"bg": "#EBEBEB", "text": "#000000", "left_bar": "#1A1E22", "progress_bar": "#D9D9D9"},
    "dark": {"bg": "#1A1E22", "text": "#FFFFFF", "left_bar": "#EBEBEB", "progress_bar": "#333333"},
    "button": {"blue": "#3B8ED0", "green": "#3BD056", "red": "#D03B3D"},
    "button_hover": {"green": "#2FA047", "red": "#A03031"}
}

# --- Geometría ---
BTN_W_MAIN, BTN_H_MAIN = 250, 30
BTN_W_ICON, BTN_H_ICON = 35, 35
PROGRESS_W = 357


# --- DIÁLOGOS PERSONALIZADOS (sin cambios) ---
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
                    self.wm_iconbitmap(parent._icon_path)
            except Exception as e:
                print(f"Error al establecer el icono de la sub-ventana: {e}")

        self.after(200, _set_icon)
        self.result = None
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind("<Escape>", self._on_cancel)

    def _on_ok(self, event=None):
        self.destroy()

    def _on_cancel(self, event=None):
        self.destroy()


class InputDialog(BaseDialog):
    def __init__(self, parent, title, prompt, initial_value=""):
        super().__init__(parent, title)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=prompt, wraplength=350).pack(fill="x", pady=(0, 10))
        self.entry = ctk.CTkEntry(main_frame, width=350)
        self.entry.insert(0, initial_value)
        self.entry.pack(fill="x", pady=(0, 20))
        self.entry.focus_set()
        self.entry.bind("<Return>", self._on_ok)
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()
        ctk.CTkButton(button_frame, text="OK", width=100, command=self._on_ok).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Cancelar", width=100, command=self._on_cancel).pack(side="left", padx=10)

    def _on_ok(self, event=None):
        self.result = self.entry.get()
        super()._on_ok()

    @classmethod
    def get_input(cls, parent, title, prompt, initial_value=""):
        dialog = cls(parent, title, prompt, initial_value)
        parent.wait_window(dialog)
        return dialog.result


class MessageDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350).pack(fill="x", pady=(0, 20))
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()
        ok_button = ctk.CTkButton(button_frame, text="OK", width=100, command=self._on_ok)
        ok_button.pack()
        ok_button.focus_set()
        self.bind("<Return>", self._on_ok)


class ConfirmDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        self.result = False
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350).pack(fill="x", pady=(0, 20))
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
    def __init__(self, parent, title: str, message: str, option1_text: str, option2_text: str):
        super().__init__(parent, title)
        self.result = None
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350).pack(fill="x", pady=(0, 20))
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()
        btn1 = ctk.CTkButton(button_frame, text=option1_text, width=180, command=self._on_option1)
        btn1.pack(pady=5)
        btn2 = ctk.CTkButton(button_frame, text=option2_text, width=180, command=self._on_option2)
        btn2.pack(pady=5)

    def _on_option1(self): self.result = "default"; super()._on_ok()

    def _on_option2(self): self.result = "custom"; super()._on_ok()

    @classmethod
    def ask(cls, parent, title: str, message: str, option1_text: str, option2_text: str) -> str | None:
        dialog = cls(parent, title, message, option1_text, option2_text)
        parent.wait_window(dialog)
        return dialog.result


# --- CLASE PRINCIPAL DE LA VISTA ---
class LectorcitoApp(ctk.CTk):
    TRANSLATIONS = {
        "es": {
            # --- Textos para la cancelación ---
            "btn_cancel": "Cancelar Lectura",
            "msg_cancelled": "Lectura cancelada por el usuario.",

            # --- Otros textos ---
            "dlg_dest_choice_title": "Elegir Destino",
            "dlg_dest_choice_prompt": "Seleccione cómo desea establecer la carpeta de destino:",
            "dlg_dest_choice_op1": "Usar Ruta por Defecto",
            "dlg_dest_choice_op2": "Elegir Ruta Personalizada",
            "dest_set_default_msg": "Destino establecido en la ruta por defecto.",
            "dest_set_custom_msg": "Destino establecido en:\n{}",
            "title": "LECTORCITO PRO",
            "welcome": "por favor seleccione una opción",
            "btn_choose_folder": "Elegir Carpeta a Leer", "btn_sel_lecturas": "Seleccionar Destino de Lecturas",
            "btn_open_lecturas": "Abrir Carpeta de Lecturas", "btn_open_last": "Abrir Último Archivo Generado",
            "btn_del": "Eliminar Todas las Lecturas", "msg_done": "¡Listo! Operación completada.",
            "msg_select_dest": "Primero debe seleccionar una carpeta de destino.",
            "msg_no_files": "No se encontraron archivos válidos en la carpeta seleccionada.",
            "dlg_exts_title": "Configurar Extensiones",
            "dlg_exts_prompt": "Extensiones permitidas (separadas por coma):",
            "dlg_excl_title": "Configurar Carpetas Excluidas",
            "dlg_excl_prompt": "Carpetas a excluir (separadas por coma):",
            "info_title": "Información", "confirm_del_title": "Confirmar Eliminación",
            "confirm_del_prompt": "¿Está seguro de que desea eliminar la carpeta de lecturas y su contenido?",
            "greet_m": "Buenos días", "greet_a": "Buenas tardes", "greet_n": "Buenas noches",
            "save_prefs_title": "Guardado", "save_prefs_msg": "Preferencias guardadas correctamente."
        },
        "en": {
            # --- English translations for cancellation ---
            "btn_cancel": "Cancel Reading",
            "msg_cancelled": "Reading cancelled by the user.",

            # --- Other English translations ---
            "dlg_dest_choice_title": "Choose Destination",
            "dlg_dest_choice_prompt": "Select how to set the destination folder:",
            "dlg_dest_choice_op1": "Use Default Path",
            "dlg_dest_choice_op2": "Choose Custom Path",
            "dest_set_default_msg": "Destination set to the default path.",
            "dest_set_custom_msg": "Destination set to:\n{}",
            "title": "LECTORCITO PRO",
            "welcome": "please select an option",
            "btn_choose_folder": "Choose Folder to Read", "btn_sel_lecturas": "Select Readings Destination",
            "btn_open_lecturas": "Open Readings Folder", "btn_open_last": "Open Last Generated File",
            "btn_del": "Delete All Readings", "msg_done": "Done! Operation completed.",
            "msg_select_dest": "You must first select a destination folder.",
            "msg_no_files": "No valid files were found in the selected folder.",
            "dlg_exts_title": "Configure Extensions", "dlg_excl_prompt": "Allowed extensions (comma-separated):",
            "dlg_excl_title": "Configure Excluded Folders", "dlg_excl_prompt": "Folders to exclude (comma-separated):",
            "info_title": "Information", "confirm_del_title": "Confirm Deletion",
            "confirm_del_prompt": "Are you sure you want to permanently delete the readings folder and all its contents?",
            "greet_m": "Good morning", "greet_a": "Good afternoon", "greet_n": "Good evening",
            "save_prefs_title": "Saved", "save_prefs_msg": "Preferences saved successfully."
        }
    }

    def __init__(self, cfg: dict, controller):
        super().__init__()
        self.config = cfg
        self.controller = controller
        self.lang = self.config.get("language", "es")
        self.current_theme = self.config.get("theme", "Light")
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("blue")
        self.title("Lectorcito Pro")
        self.geometry("600x425")
        self.resizable(False, False)
        self._icon_path = None
        try:
            icon_path = resource_path("lector.ico")
            if os.path.exists(icon_path):
                self._icon_path = icon_path
                self.wm_iconbitmap(self._icon_path)
        except Exception as e:
            print(f"Error al cargar icono: {e}")
        self._load_image_assets()
        self._build_ui()
        self.update_ui_texts()
        self._apply_theme()

    def _tr(self, key, *args):
        translation = self.TRANSLATIONS[self.lang].get(key, f"<{key}>")
        return translation.format(*args) if args else translation

    def _load_image_assets(self):
        self.icons = {}
        icon_keys = ["ver", "nover", "guardar", "traducir", "github", "info"]
        for key in icon_keys:
            try:
                light = Image.open(resource_path(f"{key}_oscuro.png"))
                dark = Image.open(resource_path(f"{key}_claro.png"))
                self.icons[key] = ctk.CTkImage(light_image=dark, dark_image=light, size=(24, 24))
            except FileNotFoundError:
                self.icons[key] = None
        self.icons['sun'] = ctk.CTkImage(Image.open(resource_path("sol.png")), size=(24, 24))
        self.icons['moon'] = ctk.CTkImage(Image.open(resource_path("luna.png")), size=(24, 24))

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._create_left_sidebar()
        self._create_right_sidebar()
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(60, 80))
        self._create_header(center_frame)
        self._create_main_buttons(center_frame)
        self._create_progress_bar_and_cancel(center_frame)
        self._create_footer()

    def _create_left_sidebar(self):
        self.side_left = ctk.CTkFrame(self, width=40, height=310, corner_radius=17)
        self.side_left.place(x=15, y=43)
        self.canvas_left = Canvas(self.side_left, width=25, height=270, highlightthickness=0)
        self.canvas_left.place(relx=0.5, rely=0.5, anchor="center")
        self.canvas_left.bind("<Configure>", self._paint_left_sidebar_text)

    def _paint_left_sidebar_text(self, _=None):
        self.canvas_left.delete("all")
        w, h = self.canvas_left.winfo_width(), self.canvas_left.winfo_height()
        color = COLORS['dark']['text'] if self.current_theme == "Light" else COLORS['light']['text']
        self.canvas_left.create_text(w / 2, h / 2, text=f"Lectorcito Pro v{VERSION}", angle=90,
                                     font=("Segoe UI", 10, "bold"), fill=color)

    def _create_right_sidebar(self):
        self.side_right = ctk.CTkFrame(self, width=60, height=310, fg_color="transparent")
        self.side_right.place(x=525, y=40)
        buttons = {
            "ver": self.controller.show_extensions_dialog, "nover": self.controller.show_excludes_dialog,
            "guardar": self.controller.save_preferences, "theme_icon": self.controller.toggle_theme,
            "traducir": self.controller.toggle_language, "github": lambda: webbrowser.open_new(REPO_URL),
            "info": self.show_app_info
        }
        self.sidebar_buttons = {}
        for key, cmd in buttons.items():
            btn = self._create_sidebar_button(self.side_right, key, cmd)
            self.sidebar_buttons[key] = btn

    def _create_sidebar_button(self, parent, icon_key, command):
        img = self.icons.get(icon_key)
        if icon_key == "theme_icon":
            img = self.icons['moon'] if self.current_theme == "Light" else self.icons['sun']
        button = ctk.CTkButton(parent, image=img, text="", width=BTN_W_ICON, height=BTN_H_ICON, command=command,
                               corner_radius=10)
        button.pack(pady=5, padx=5)
        return button

    def _create_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(pady=(15, 10))
        self.lbl_title = ctk.CTkLabel(header, font=("Segoe UI", 16, "bold"))
        self.lbl_title.pack()
        self.lbl_greet = ctk.CTkLabel(header, font=("Segoe UI", 13))
        self.lbl_greet.pack()

    def _create_main_buttons(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=10)
        opts = {"width": BTN_W_MAIN, "height": BTN_H_MAIN, "corner_radius": 10, "font": ("Segoe UI", 11, "bold")}
        self.main_buttons = {
            "selpath": ctk.CTkButton(frame, **opts, command=self.controller.select_destination_path),
            "choose": ctk.CTkButton(frame, **opts, command=self.controller.select_folder_to_read),
            "openlect": ctk.CTkButton(frame, **opts, command=self.controller.open_destination_folder),
            "openlast": ctk.CTkButton(frame, **opts, command=self.controller.open_last_report,
                                      fg_color=COLORS['button']['green'], hover_color=COLORS['button_hover']['green']),
            "delete": ctk.CTkButton(frame, **opts, command=self.controller.delete_all_readings,
                                    fg_color=COLORS['button']['red'], hover_color=COLORS['button_hover']['red'])
        }
        for btn in self.main_buttons.values(): btn.pack(pady=4)

    def _create_progress_bar_and_cancel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=10, fill="x", anchor="center")
        frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(frame, width=PROGRESS_W, corner_radius=10, mode='determinate')
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        self.lbl_percent = ctk.CTkLabel(frame, text="0%")
        self.lbl_percent.grid(row=1, column=0, pady=(0, 5))

        self.btn_cancel = ctk.CTkButton(frame, text=self._tr("btn_cancel"), command=self.controller.cancel_processing,
                                        width=150, height=28, state="disabled")
        self.btn_cancel.grid(row=2, column=0, pady=(5, 0))

    def _create_footer(self):
        footer = ctk.CTkFrame(self, height=30, corner_radius=0)
        footer.grid(row=4, column=0, columnspan=2, sticky="ew")
        ctk.CTkLabel(footer, text=f"Copyright © {YEAR} - {AUTHOR} - All Rights Reserved.", font=("Segoe UI", 9)).place(
            relx=0.5, rely=0.5, anchor="center")

    def _apply_theme(self):
        is_light = self.current_theme == "Light"
        ctk.set_appearance_mode(self.current_theme)
        theme = COLORS['light' if is_light else 'dark']
        self.configure(fg_color=theme['bg'])
        for label in [self.lbl_title, self.lbl_greet, self.lbl_percent]:
            label.configure(text_color=theme['text'])
        self.side_left.configure(fg_color=theme['left_bar'])
        self.canvas_left.configure(bg=theme['left_bar'])
        self._paint_left_sidebar_text()
        for btn in self.sidebar_buttons.values():
            btn.configure(fg_color=theme['left_bar'], hover_color=theme['left_bar'])
        self.sidebar_buttons['theme_icon'].configure(image=self.icons['moon'] if is_light else self.icons['sun'])
        self.progress_bar.configure(progress_color=COLORS['button']['blue'], fg_color=theme['progress_bar'])

    def update_ui_texts(self):
        self.lbl_title.configure(text=self._tr("title"))
        h = datetime.datetime.now().hour
        greet_key = "greet_m" if 5 <= h < 12 else "greet_a" if 12 <= h < 19 else "greet_n"
        user = os.getlogin() if hasattr(os, "getlogin") else "User"
        self.lbl_greet.configure(text=f"{self._tr(greet_key)} {user}, {self._tr('welcome')}")
        self.main_buttons["selpath"].configure(text=self._tr("btn_sel_lecturas"))
        self.main_buttons["choose"].configure(text=self._tr("btn_choose_folder"))
        self.main_buttons["openlect"].configure(text=self._tr("btn_open_lecturas"))
        self.main_buttons["openlast"].configure(text=self._tr("btn_open_last"))
        self.main_buttons["delete"].configure(text=self._tr("btn_del"))
        self.btn_cancel.configure(text=self._tr("btn_cancel"))

    def set_progress(self, percentage):
        self.progress_bar.set(percentage / 100)
        self.lbl_percent.configure(text=f"{int(percentage)}%")
        self.update_idletasks()

    def toggle_main_buttons_state(self, state: str):
        for btn in self.main_buttons.values():
            btn.configure(state=state)

    def toggle_cancel_button_state(self, state: str):
        self.btn_cancel.configure(state=state)

    def ask_for_directory(self, title_key: str) -> str | None:
        return filedialog.askdirectory(title=self._tr(title_key))

    def show_message(self, title_key: str, message_key_or_text: str, *args):
        message = self._tr(message_key_or_text, *args)
        MessageDialog(self, self._tr(title_key), message)

    def show_app_info(self):
        info_text = (f"Lectorcito Pro v{VERSION}\n\n"
                     f"Desarrollado por: \n{AUTHOR}\n\n"
                     f"Repositorio: {REPO_URL}\n\n"
                     f"© {YEAR} - All Rights Reserved.")
        MessageDialog(self, self._tr("info_title"), info_text)
