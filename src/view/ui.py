import customtkinter as ctk
from tkinter import Canvas
from PIL import Image
import webbrowser
import datetime
import os
import random

from utils import resource_path
from view.translations import TRANSLATIONS
# --- Se importan los diálogos desde su propio módulo ---
from view.dialogs import MessageDialog, InfographicDialog

# --- Constantes de la Interfaz ---
VERSION = "5.7.3"
YEAR = datetime.datetime.now().year
AUTHOR = "Renzo Fernando Mosquera Daza"
REPO_URL = "https://github.com/RenzoFernando/LectorcitoPro.git"
GIF_CHANGE_INTERVAL_MS = 1 * 60 * 1000  # 1 minutos en milisegundos

# --- Paleta de Colores y Geometría ---
COLORS = {
    "light": {"bg": "#EBEBEB", "text": "#000000", "left_bar": "#1A1E22", "progress_bar": "#D9D9D9"},
    "dark": {"bg": "#1A1E22", "text": "#FFFFFF", "left_bar": "#EBEBEB", "progress_bar": "#333333"},
    "button": {"blue": "#3B8ED0", "green": "#3BD056", "red": "#D03B3D"},
    "button_hover": {"blue_h": "#3073A8", "green_h": "#2FA047", "red_h": "#A03031"},
    "progress_colors": {"start": "#3B8ED0", "mid": "#F9A825", "done": "#4CAF50"}
}
BTN_W_MAIN, BTN_H_MAIN = 250, 30
BTN_W_ICON, BTN_H_ICON = 35, 35
PROGRESS_W = 357


# --- CLASE PRINCIPAL DE LA VISTA ---
class LectorcitoApp(ctk.CTk):
    def __init__(self, cfg: dict, controller):
        super().__init__()
        self.attributes("-alpha", 0.0)
        self.TRANSLATIONS = TRANSLATIONS
        self.config = cfg
        self.controller = controller
        self.lang = self.config.get("language", "es")
        self.current_theme = self.config.get("theme", "Light")
        self.current_progress = 0
        self.target_progress = 0
        self.animation_after_id = None

        # --- Gestión de GIFs ---
        self.gif_names = ["Cat_Working.gif", "Hacker_Coding.gif", "Computer_Coding.gif", "Mad_Artificial_Intelligence.gif", "Thinking_Working.gif", "Ctrl_C_V.gif", "Coding_Coffee.gif"]
        self.gif_pil_frames = []
        self.gif_frame_index = 0
        self.gif_animation_after_id = None
        self.gif_delay = 100
        self.gif_change_timer_id = None  # ID para el temporizador de cambio de GIF

        self.title("Lectorcito Pro")
        self.geometry("600x525")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)

        self._icon_path = resource_path("lector.ico")
        if os.path.exists(self._icon_path):
            self.iconbitmap(self._icon_path)

        self._load_image_assets()
        self._build_ui()
        self.update_ui_texts()
        self.apply_theme()
        self.toggle_ui_for_processing(is_active=False)
        self.after(50, self._fade_in)

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1:
            alpha = min(alpha + 0.08, 1.0);
            self.attributes("-alpha", alpha);
            self.after(15, self._fade_in)

    def _close_with_fade_out(self):
        # Cancelar todos los temporizadores pendientes al cerrar
        if self.gif_animation_after_id:
            self.after_cancel(self.gif_animation_after_id)
        if self.gif_change_timer_id:
            self.after_cancel(self.gif_change_timer_id)

        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha = max(alpha - 0.08, 0.0);
            self.attributes("-alpha", alpha);
            self.after(15, self._close_with_fade_out)
        else:
            self.destroy()

    def _tr(self, key, *args):
        translation_entry = self.TRANSLATIONS.get(self.lang, self.TRANSLATIONS["es"]).get(key, f"<{key}>")
        if isinstance(translation_entry, list):
            return random.choice(translation_entry).format(*args)
        return translation_entry.format(*args)

    def _load_image_assets(self):
        self.icons = {}
        icon_keys = ["ver", "nover", "traducir", "restaurar", "github", "info"]
        for key in icon_keys:
            try:
                img_for_dark_theme = Image.open(resource_path(f"{key}_oscuro.png"))
                img_for_light_theme = Image.open(resource_path(f"{key}_claro.png"))
                self.icons[key] = ctk.CTkImage(light_image=img_for_light_theme, dark_image=img_for_dark_theme,
                                               size=(22, 22))
            except Exception as e:
                print(f"Error cargando icono '{key}': {e}");
                self.icons[key] = None
        try:
            self.icons['sun'] = ctk.CTkImage(Image.open(resource_path("sol.png")), size=(24, 24))
            self.icons['moon'] = ctk.CTkImage(Image.open(resource_path("luna.png")), size=(24, 24))
        except Exception as e:
            print(f"Error cargando iconos de tema: {e}")

    def _load_and_prepare_gif(self):
        """Selecciona, carga y redimensiona un GIF aleatorio para que quepa en el
        área de progreso manteniendo la relación de aspecto."""
        self.gif_pil_frames = []
        self.gif_frame_index = 0

        if not self.gif_names:
            return

        try:
            self.progress_frame.update_idletasks()
            container_width = self.progress_frame.winfo_width()
            container_height = self.progress_frame.winfo_height()

            padding = 20
            max_w = container_width - padding
            max_h = container_height - padding

            if max_w <= 20 or max_h <= 20:
                print(f"Advertencia: El área para el GIF es muy pequeña ({max_w}x{max_h}).")
                return

            chosen_gif = random.choice(self.gif_names)
            gif_path = resource_path(chosen_gif)

            with Image.open(gif_path) as im:
                self.gif_delay = im.info.get('duration', 100)

                original_width, original_height = im.size
                if original_height <= 0 or original_width <= 0:
                    return

                ratio = min(max_w / original_width, max_h / original_height)

                target_width = int(original_width * ratio)
                target_height = int(original_height * ratio)

                gif_size = (target_width, target_height)

                for i in range(im.n_frames):
                    im.seek(i)
                    frame_rgba = im.convert("RGBA")
                    resized_frame = frame_rgba.resize(gif_size, Image.Resampling.LANCZOS)
                    self.gif_pil_frames.append(resized_frame)

        except Exception as e:
            print(f"Error al cargar o redimensionar el GIF: {e}")
            self.gif_pil_frames = []

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1);
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
        self.header_frame = ctk.CTkFrame(parent, fg_color="transparent");
        self.header_frame.pack(pady=(20, 15), fill="x")
        self.lbl_title = ctk.CTkLabel(self.header_frame, font=("Segoe UI", 18, "bold"));
        self.lbl_title.pack()
        self.lbl_greet = ctk.CTkLabel(self.header_frame, font=("Segoe UI", 13));
        self.lbl_greet.pack()

    def _create_main_buttons(self, parent):
        self.main_buttons_frame = ctk.CTkFrame(parent, fg_color="transparent");
        self.main_buttons_frame.pack(pady=5, fill="x")
        opts = {"width": BTN_W_MAIN, "height": BTN_H_MAIN, "corner_radius": 8, "font": ("Segoe UI", 11, "bold")}
        self.main_buttons = {
            "selpath": ctk.CTkButton(self.main_buttons_frame, **opts),
            "choose": ctk.CTkButton(self.main_buttons_frame, **opts),
            "create_tree": ctk.CTkButton(self.main_buttons_frame, **opts),
            "openlect": ctk.CTkButton(self.main_buttons_frame, **opts),
            "openlast": ctk.CTkButton(self.main_buttons_frame, **opts, fg_color=COLORS['button']['green'],
                                      hover_color=COLORS['button_hover']['green_h']),
            "delete": ctk.CTkButton(self.main_buttons_frame, **opts, fg_color=COLORS['button']['red'],
                                    hover_color=COLORS['button_hover']['red_h'])
        }
        for btn in self.main_buttons.values(): btn.pack(pady=4)

    def _create_progress_and_cancel(self, parent):
        self.progress_frame = ctk.CTkFrame(parent, fg_color="transparent");
        self.progress_frame.pack(pady=(10, 5), fill="both", expand=True)

        self.lbl_progress_status = ctk.CTkLabel(self.progress_frame, text="", font=("Segoe UI", 11, "bold"))
        self.lbl_percent = ctk.CTkLabel(self.progress_frame, text="", font=("Segoe UI", 11, "bold"))
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=10, corner_radius=8, mode='determinate');
        self.progress_bar.set(0)
        self.lbl_current_file = ctk.CTkLabel(self.progress_frame, text="", font=("Segoe UI", 9), anchor="w")
        self.btn_cancel = ctk.CTkButton(self.progress_frame, width=150, height=28)
        self.lbl_gif_animation = ctk.CTkLabel(self.progress_frame, text="")

    def _create_left_sidebar(self):
        self.side_left = ctk.CTkFrame(self, width=40, height=350, corner_radius=15);
        self.side_left.place(x=15, y=43)
        self.canvas_left = Canvas(self.side_left, width=25, height=310, highlightthickness=0);
        self.canvas_left.place(relx=0.5, rely=0.5, anchor="center")
        self.canvas_left.bind("<Configure>", self._paint_left_sidebar_text)

    def _create_right_sidebar(self):
        self.side_right = ctk.CTkFrame(self, width=60, height=350, fg_color="transparent");
        self.side_right.place(x=525, y=40)
        btn_color = COLORS['light' if self.current_theme == "Light" else 'dark']['left_bar']
        self.sidebar_buttons = {}
        icon_keys = ["ver", "nover", "theme_icon", "traducir", "restaurar", "github", "info"]

        for key in icon_keys:
            is_light = self.current_theme == "Light"
            initial_icon = self.icons.get('moon') if key == "theme_icon" and is_light else self.icons.get(
                'sun') if key == "theme_icon" else self.icons.get(key)

            btn = ctk.CTkButton(self.side_right, image=initial_icon, text="", width=BTN_W_ICON, height=BTN_H_ICON,
                                corner_radius=8, fg_color=btn_color, hover_color=btn_color)
            btn.pack(pady=4, padx=5)
            self.sidebar_buttons[key] = btn

    def _create_footer(self):
        self.footer_frame = ctk.CTkFrame(self, height=30, corner_radius=0);
        self.footer_frame.grid(row=4, column=0, columnspan=2, sticky="sew")
        ctk.CTkLabel(self.footer_frame, text=f"Copyright © {YEAR} - {AUTHOR} - All Rights Reserved.",
                     font=("Segoe UI", 9)).place(
            relx=0.5, rely=0.5, anchor="center")

    def update_ui_texts(self):
        self.lbl_title.configure(text=self._tr("title"))
        hour = datetime.datetime.now().hour
        greet_key = "greet_m" if 5 <= hour < 12 else "greet_a" if 12 <= hour < 19 else "greet_n"
        try:
            user = os.getlogin().lower().capitalize()
        except OSError:
            user = "User"
        greeting = self._tr(greet_key)
        self.lbl_greet.configure(text=f"{greeting} {user}{self._tr('welcome')}")
        key_map = {"selpath": "btn_sel_lecturas", "choose": "btn_choose_folder", "create_tree": "btn_create_tree",
                   "openlect": "btn_open_lecturas", "openlast": "btn_open_last", "delete": "btn_del"}
        for key, btn in self.main_buttons.items():
            if key in key_map: btn.configure(text=self._tr(key_map[key]))
        self.btn_cancel.configure(text=self._tr("btn_cancel"))
        self.lbl_progress_status.configure(text=self._tr("progress_processing_text"))

    def apply_theme(self):
        is_light = self.current_theme == "Light"
        ctk.set_appearance_mode(self.current_theme)
        theme = COLORS['light' if is_light else 'dark']
        self.configure(fg_color=theme['bg'])
        self.side_left.configure(fg_color=theme['left_bar'])
        self.canvas_left.configure(bg=theme['left_bar'])
        self._paint_left_sidebar_text()
        self.progress_bar.configure(fg_color=theme['progress_bar'])
        btn_color = theme['left_bar']
        for btn in self.sidebar_buttons.values(): btn.configure(fg_color=btn_color, hover_color=btn_color)
        self.sidebar_buttons['theme_icon'].configure(
            image=self.icons.get('moon') if is_light else self.icons.get('sun'))
        self.set_progress(self.target_progress, None, True)

    def _paint_left_sidebar_text(self, event=None):
        self.canvas_left.delete("all")
        w, h = self.canvas_left.winfo_width(), self.canvas_left.winfo_height()
        color = COLORS['dark']['text'] if self.current_theme == "Light" else COLORS['light']['text']
        self.canvas_left.create_text(w / 2, h / 2, text=f"Lectorcito Pro v{VERSION}", angle=90,
                                     font=("Segoe UI", 10, "bold"), fill=color)

    def _animate_progress(self):
        if self.animation_after_id: self.after_cancel(self.animation_after_id); self.animation_after_id = None
        diff = self.target_progress - self.current_progress
        if abs(diff) < 0.1:
            self.current_progress = self.target_progress
        else:
            self.current_progress += diff * 0.1;
            self.animation_after_id = self.after(20, self._animate_progress)
        self.progress_bar.set(self.current_progress / 100)

    def _animate_gif(self):
        if self.gif_animation_after_id: self.after_cancel(self.gif_animation_after_id)
        if self.gif_pil_frames:
            pil_frame = self.gif_pil_frames[self.gif_frame_index]
            ctk_image = ctk.CTkImage(light_image=pil_frame, dark_image=pil_frame, size=pil_frame.size)
            self.lbl_gif_animation.configure(image=ctk_image)
            self.gif_frame_index = (self.gif_frame_index + 1) % len(self.gif_pil_frames)
            self.gif_animation_after_id = self.after(self.gif_delay, self._animate_gif)

    def set_progress(self, percentage, file_context=None, force_color=False):
        new_target = int(percentage)
        if new_target != self.target_progress or force_color:
            self.target_progress = new_target
            color = COLORS['progress_colors']['done'] if self.target_progress >= 90 else COLORS['progress_colors'][
                'mid'] if self.target_progress >= 50 else COLORS['progress_colors']['start']
            self.progress_bar.configure(progress_color=color)
        self.lbl_percent.configure(text=f"{self.target_progress}%")
        if file_context: self.lbl_current_file.configure(text=file_context)
        if self.animation_after_id is None: self._animate_progress()

    def _change_and_reschedule_gif(self):
        """Carga un nuevo GIF y programa el siguiente cambio."""
        # Solo cambia el GIF si no hay un proceso activo
        if not self.controller.is_processing:
            self._load_and_prepare_gif()
            self._animate_gif()

        # Vuelve a programar la próxima ejecución
        self.gif_change_timer_id = self.after(GIF_CHANGE_INTERVAL_MS, self._change_and_reschedule_gif)

    def toggle_ui_for_processing(self, is_active: bool):
        state = "disabled" if is_active else "normal"
        for btn in self.main_buttons.values(): btn.configure(state=state)
        for btn in self.sidebar_buttons.values(): btn.configure(state=state)

        # Cancela el temporizador de cambio de GIF al iniciar o terminar un proceso
        if self.gif_change_timer_id:
            self.after_cancel(self.gif_change_timer_id)
            self.gif_change_timer_id = None

        if is_active:
            if self.gif_animation_after_id:
                self.after_cancel(self.gif_animation_after_id)
                self.gif_animation_after_id = None
            self.lbl_gif_animation.place_forget()

            self.set_progress(0)
            self.lbl_progress_status.place(relx=0.0, rely=0.1, anchor="w")
            self.lbl_percent.place(relx=1.0, rely=0.1, anchor="e")
            self.progress_bar.place(relx=0.5, rely=0.4, anchor="center", relwidth=0.95)
            self.lbl_current_file.place(relx=0.0, rely=0.6, anchor="w")
            self.btn_cancel.place(relx=0.5, rely=0.9, anchor="center")

        else:
            for widget in (self.lbl_progress_status, self.lbl_percent, self.progress_bar, self.lbl_current_file,
                           self.btn_cancel):
                widget.place_forget()

            self.after(50, self._load_and_prepare_gif)

            def show_gif():
                if self.gif_pil_frames:
                    self.lbl_gif_animation.place(relx=0.5, rely=0.5, anchor="center")
                    self._animate_gif()
                    # Inicia el ciclo de cambios automáticos
                    self.gif_change_timer_id = self.after(GIF_CHANGE_INTERVAL_MS, self._change_and_reschedule_gif)

            self.after(60, show_gif)

            self.after(1000, lambda: self.set_progress(0))

    def show_message(self, title_key: str, message_key: str, *args):
        MessageDialog(self, self._tr(title_key), self._tr(message_key, *args))

    def show_app_info(self):
        image_path = resource_path("Infografía_LectorcitoPro.png")
        if os.path.exists(image_path):
            InfographicDialog(self, title=self._tr("manual_title"), image_path=image_path)
        else:
            self.show_message("error_title", "msg_infographic_error")
