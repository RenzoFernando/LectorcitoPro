import customtkinter as ctk
import datetime
import os
import webbrowser
from tkinter import PhotoImage, Canvas, filedialog, messagebox
from PIL import Image
from utils import resource_path
from tkinter import simpledialog

# --- Constantes de la Interfaz ---
VERSION = "4.0"
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


class LectorcitoApp(ctk.CTk):
    # --- Traducciones ---
    TRANSLATIONS = {
        "es": {
            "title": "LECTORCITO PRO", "welcome": "por favor seleccione una opción",
            "btn_choose_folder": "Elegir Carpeta a Leer", "btn_sel_lecturas": "Seleccionar Destino de Lecturas",
            "btn_open_lecturas": "Abrir Carpeta de Lecturas", "btn_open_last": "Abrir Último Archivo Generado",
            "btn_del": "Eliminar Todas las Lecturas", "msg_done": "¡Listo! Operación completada.",
            "msg_select_read": "Primero debe seleccionar la carpeta que desea leer.",
            "msg_select_dest": "Primero debe seleccionar una carpeta de destino para las lecturas.",
            "msg_no_files": "No se encontraron archivos válidos en la carpeta seleccionada.",
            "dlg_exts_title": "Configurar Extensiones",
            "dlg_exts_prompt": "Extensiones permitidas (separadas por coma):",
            "dlg_excl_title": "Configurar Carpetas Excluidas",
            "dlg_excl_prompt": "Carpetas a excluir (separadas por coma):",
            "info_title": "Información", "confirm_del_title": "Confirmar Eliminación",
            "confirm_del_prompt": "¿Está seguro de que desea eliminar permanentemente la carpeta de lecturas y todo su contenido?",
            "greet_m": "Buenos días", "greet_a": "Buenas tardes", "greet_n": "Buenas noches",
            "save_prefs_title": "Guardado", "save_prefs_msg": "Preferencias guardadas correctamente."
        },
        "en": {
            "title": "LECTORCITO PRO", "welcome": "please select an option to perform",
            "btn_choose_folder": "Choose Folder to Read", "btn_sel_lecturas": "Select Readings Destination",
            "btn_open_lecturas": "Open Readings Folder", "btn_open_last": "Open Last Generated File",
            "btn_del": "Delete All Readings", "msg_done": "Done! Operation completed successfully.",
            "msg_select_read": "You must first select the folder you want to read.",
            "msg_select_dest": "You must first select a destination folder for the readings.",
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

        try:
            self._icon = PhotoImage(file=resource_path("lector.png"))
            self.iconphoto(True, self._icon)
            self.iconbitmap(resource_path("lector.ico"))
        except Exception as e:
            print(f"Error al cargar iconos: {e}")

        self._load_image_assets()
        self._build_ui()
        self.update_ui_texts()

    def _tr(self, key):
        return self.TRANSLATIONS[self.lang].get(key, f"<{key}>")

    def _load_image_assets(self):
        self.icons = {}
        icon_keys = ["ver", "nover", "guardar", "traducir", "github", "info"]
        for key in icon_keys:
            try:
                self.icons[key] = ctk.CTkImage(
                    light_image=Image.open(resource_path(f"{key}_claro.png")),
                    dark_image=Image.open(resource_path(f"{key}_oscuro.png")),
                    size=(24, 24))
            except FileNotFoundError:
                print(f"Advertencia: No se encontró el icono para '{key}'.")

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
        self._create_progress_bar(center_frame)
        self._create_footer()

        self._apply_theme()

    def _create_left_sidebar(self):
        self.side_left = ctk.CTkFrame(self, width=40, height=310, corner_radius=17)
        self.side_left.place(x=15, y=43)

        self.canvas_left = Canvas(self.side_left, width=25, height=270, highlightthickness=0)
        self.canvas_left.place(relx=0.5, rely=0.5, anchor="center")
        self.canvas_left.bind("<Configure>", self._paint_left_sidebar_text)

    def _paint_left_sidebar_text(self, _=None):
        self.canvas_left.delete("all")
        w, h = self.canvas_left.winfo_width(), self.canvas_left.winfo_height()
        font_color = COLORS['light']['text'] if self.current_theme == "Dark" else COLORS['dark']['text']
        self.canvas_left.create_text(w / 2, h / 2, text=f"Lectorcito Pro v{VERSION}", angle=90,
                                        font=("Segoe UI", 10, "bold"), fill=font_color)

    def _create_right_sidebar(self):
        self.side_right = ctk.CTkFrame(self, width=60, height=310, fg_color="transparent")
        self.side_right.place(x=600 - 60 - 15, y=40)

        self._create_sidebar_button(self.side_right, "ver", self.controller.show_extensions_dialog)
        self._create_sidebar_button(self.side_right, "nover", self.controller.show_excludes_dialog)
        self._create_sidebar_button(self.side_right, "guardar", self.controller.save_preferences)
        self.btn_toggle_theme = self._create_sidebar_button(self.side_right, "theme_icon", self.controller.toggle_theme)
        self._create_sidebar_button(self.side_right, "traducir", self.controller.toggle_language)
        self._create_sidebar_button(self.side_right, "github", lambda: webbrowser.open_new(REPO_URL))
        self._create_sidebar_button(self.side_right, "info", self.show_app_info)

        for btn in self.side_right.winfo_children():
            btn.pack(pady=5, padx=5)

    def _create_sidebar_button(self, parent, icon_key, command):
        img = self.icons.get(icon_key, None)
        if icon_key == "theme_icon":
            img = self.icons['moon'] if self.current_theme == "Light" else self.icons['sun']

        return ctk.CTkButton(parent, image=img, text="", width=BTN_W_ICON, height=BTN_H_ICON,
                                command=command, corner_radius=10, fg_color="transparent")

    def _create_header(self, parent):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(pady=(15, 10))

        self.lbl_title = ctk.CTkLabel(header_frame, text=self._tr("title"), font=("Segoe UI", 16, "bold"))
        self.lbl_title.pack()

        self.lbl_greet = ctk.CTkLabel(header_frame, font=("Segoe UI", 13))
        self.lbl_greet.pack()

    def _create_main_buttons(self, parent):
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(pady=10)
        opts = {"width": BTN_W_MAIN, "height": BTN_H_MAIN, "corner_radius": 10, "font": ("Segoe UI", 11, "bold")}

        self.btn_selpath = ctk.CTkButton(buttons_frame, **opts, command=self.controller.select_destination_path)
        self.btn_choose = ctk.CTkButton(buttons_frame, **opts, command=self.controller.select_folder_to_read)
        self.btn_openlect = ctk.CTkButton(buttons_frame, **opts, command=self.controller.open_destination_folder)
        self.btn_openlast = ctk.CTkButton(buttons_frame, **opts, command=self.controller.open_last_report,
                                        fg_color=COLORS['button']['green'],
                                        hover_color=COLORS['button_hover']['green'])
        self.btn_delete = ctk.CTkButton(buttons_frame, **opts, command=self.controller.delete_all_readings,
                                        fg_color=COLORS['button']['red'], hover_color=COLORS['button_hover']['red'])

        for btn in buttons_frame.winfo_children():
            btn.pack(pady=4)

    def _create_progress_bar(self, parent):
        progress_frame = ctk.CTkFrame(parent, fg_color="transparent")
        progress_frame.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=PROGRESS_W, corner_radius=10, mode='determinate')
        self.progress_bar.set(0)
        self.progress_bar.pack()

        self.lbl_percent = ctk.CTkLabel(progress_frame, text="0%")
        self.lbl_percent.pack(pady=3)

    def _create_footer(self):
        footer_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        footer_frame.grid(row=4, column=0, columnspan=2, sticky="ew")
        ctk.CTkLabel(footer_frame, text=f"Copyright © {YEAR} - {AUTHOR} - All Rights Reserved.",
                    font=("Segoe UI", 9)).place(relx=0.5, rely=0.5, anchor="center")

    def _apply_theme(self):
        is_light = self.current_theme == "Light"
        theme = COLORS['light'] if is_light else COLORS['dark']
        font_color = theme['text']

        self.configure(fg_color=theme['bg'])
        for label in [self.lbl_title, self.lbl_greet, self.lbl_percent]:
            label.configure(text_color=font_color)

        self.side_left.configure(fg_color=theme['left_bar'])
        self.canvas_left.configure(bg=theme['left_bar'])
        self._paint_left_sidebar_text()

        for btn in self.side_right.winfo_children():
            btn.configure(fg_color=theme['left_bar'], hover_color=theme['left_bar'])

        self.btn_toggle_theme.configure(image=self.icons['moon'] if is_light else self.icons['sun'])
        self.progress_bar.configure(progress_color=COLORS['button']['blue'], fg_color=theme['progress_bar'])

    def update_ui_texts(self):
        self.lbl_title.configure(text=self._tr("title"))
        h = datetime.datetime.now().hour
        greet_key = "greet_m" if h < 12 else "greet_a" if h < 18 else "greet_n"
        user = os.getlogin() if hasattr(os, "getlogin") else "User"
        self.lbl_greet.configure(text=f"{self._tr(greet_key)} {user}, {self._tr('welcome')}")
        self.btn_selpath.configure(text=self._tr("btn_sel_lecturas"))
        self.btn_choose.configure(text=self._tr("btn_choose_folder"))
        self.btn_openlect.configure(text=self._tr("btn_open_lecturas"))
        self.btn_openlast.configure(text=self._tr("btn_open_last"))
        self.btn_delete.configure(text=self._tr("btn_del"))

    def set_progress(self, percentage):
        self.progress_bar.set(percentage / 100)
        self.lbl_percent.configure(text=f"{percentage:.0f}%")
        self.update_idletasks()

    def set_buttons_state(self, state: str):
        for btn in [self.btn_selpath, self.btn_choose, self.btn_openlect, self.btn_openlast, self.btn_delete]:
            btn.configure(state=state)

    def show_custom_dialog(self, title_key: str, prompt_key: str, initial_value: str) -> str|None:
        """
        Usa el simpledialog de Tkinter para permitir un valor inicial.
        """
        return simpledialog.askstring(
            title=self._tr(title_key),
            prompt=self._tr(prompt_key),
            initialvalue=initial_value,
            parent=self
        )

    def ask_for_directory(self, title_key: str) -> str:
        return filedialog.askdirectory(title=self._tr(title_key))

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def show_warning(self, title, message):
        messagebox.showwarning(title, message)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def ask_yes_no(self, title, message):
        return messagebox.askyesno(title, message)

    def show_app_info(self):
        info_text = (f"Lectorcito Pro v{VERSION}\n\n"
                    f"Desarrollado por: {AUTHOR}\n"
                    f"Repositorio: {REPO_URL}\n\n"
                    f"© {YEAR} - All Rights Reserved.")
        self.show_info(self._tr("info_title"), info_text)
