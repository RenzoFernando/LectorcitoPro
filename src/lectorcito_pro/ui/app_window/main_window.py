

import customtkinter as ctk
from tkinter import Canvas
import tkinter as tk
from PIL import Image
import datetime
import os
import random
import logging

from ...core.paths import resource_path
from ...i18n.translations import TRANSLATIONS
from ..dialogs.message import MessageDialog
from ..dialogs.infographic import InfographicDialog
from ..tooltips.tooltip import CustomTooltip
from ..components.pages.home_page import HomePage
from ..components.molecules.sidebar import LeftSidebar, RightSidebar
from ..components.organisms.footer import Footer


from ..theme.palette import (
    COLORS,
    BTN_W_MAIN,
    BTN_H_MAIN,
    BTN_W_ICON,
    BTN_H_ICON,
    SIDEBAR_WIDTH,
    PROGRESS_W,
)
from ..theme.theme_manager import set_theme


VERSION = "6.0.0"
YEAR = datetime.datetime.now().year
AUTHOR = "Renzo Fernando Mosquera Daza"
REPO_URL = "https://github.com/RenzoFernando/LectorcitoPro.git"
GIF_CHANGE_INTERVAL_MS = 1 * 60 * 1000



class LectorcitoApp(ctk.CTk):

    def __init__(self, cfg: dict, controller):
        super().__init__()
        self.attributes("-alpha", 0.0)
        self.logger = logging.getLogger(__name__)
        self.TRANSLATIONS = TRANSLATIONS
        self.config = cfg
        self.controller = controller
        self.lang = self.config.get("language", "es")
        self.current_theme = self.config.get("theme", "Light")
        self.current_progress = 0
        self.target_progress = 0
        self.animation_after_id = None
        self.REPO_URL = REPO_URL
        self.tooltips = {}

        self.gif_names = []
        self.gif_pil_frames = []
        self.gif_frame_index = 0
        self.gif_animation_after_id = None
        self.gif_delay = 100
        self.gif_change_timer_id = None
        # Control de cierre (evita doble destroy desde callbacks `after`)
        self._closing = False
        self._close_after_id = None
        self._idle_status_after_id = None
        self._idle_waiting_index = 0
        self._idle_waiting_variants = ("Esperando lectura [.]","Esperando lectura [..]","Esperando lectura [...]")


        self.title("Lectorcito Pro")
        self.geometry("600x500")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)

        self._icon_path = resource_path("lector.ico")
        if os.path.exists(self._icon_path):
            self.iconbitmap(self._icon_path)

        self._is_centered = False
        self.bind("<Configure>", self._on_configure_center)

        self._load_image_assets()
        self._build_ui()
        self.update_ui_texts()
        self.apply_theme()
        self.toggle_ui_for_processing(is_active=False)

    def _on_configure_center(self, event=None):
        if not self._is_centered:
            self._is_centered = True
            self._center_on_screen()
            self.after(10, self._fade_in)

    def _center_on_screen(self):
        try:
            self.update_idletasks()
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            window_width = self.winfo_width()
            window_height = self.winfo_height()
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)
            self.geometry(f'+{x}+{y}')
        except Exception as e:
            print(f"Error al centrar la ventana principal: {e}")

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1:
            alpha = min(alpha + 0.08, 1.0)
            self.attributes("-alpha", alpha)
            self.after(15, self._fade_in)

    def _close_with_fade_out(self):
        """Cierra la app con animación, evitando errores Tcl por doble destroy."""
        if getattr(self, "_closing", False):
            return
        self._closing = True

        # Cancelar jobs programados (progress/gif/fade)
        for attr in ("animation_after_id", "gif_animation_after_id", "gif_change_timer_id", "_close_after_id", "_idle_status_after_id"):
            job_id = getattr(self, attr, None)
            if job_id:
                try:
                    self.after_cancel(job_id)
                except tk.TclError:
                    pass
                setattr(self, attr, None)

        # Limpiar tooltips (cancela callbacks y cierra toplevels de tooltips)
        try:
            for tp in getattr(self, "tooltips", {}).values():
                try:
                    tp.cleanup()
                except tk.TclError:
                    pass
        except tk.TclError:
            pass

        self._fade_out_step()

    def _fade_out_step(self):
        if not self.winfo_exists():
            return
        try:
            alpha = float(self.attributes("-alpha"))
        except tk.TclError:
            alpha = 0.0
        if alpha > 0.0:
            alpha = max(alpha - 0.08, 0.0)
            try:
                self.attributes("-alpha", alpha)
            except tk.TclError:
                pass
            self._close_after_id = self.after(15, self._fade_out_step)
        else:
            # Destruir fuera del callback actual para evitar `can't delete Tcl command`
            try:
                self.after_idle(self._safe_destroy)
            except tk.TclError:
                self._safe_destroy()

    def _safe_destroy(self):
        # Cancel any pending callbacks to avoid TclError on teardown.
        try:
            for after_id in list(self.after_info()):
                try:
                    self.after_cancel(after_id)
                except tk.TclError:
                    pass
        except tk.TclError:
            pass
        if not self.winfo_exists():
            return
        try:
            ctk.CTk.destroy(self)
        except tk.TclError:
            # Último recurso: evitar crash en cierre
            pass

    def _tr(self, key, *args):
        translation_entry = self.TRANSLATIONS.get(self.lang, self.TRANSLATIONS["es"]).get(key, f"{key}")
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
                print(f"Error cargando icono '{key}': {e}")
                self.icons[key] = None
        try:
            self.icons['sun'] = ctk.CTkImage(Image.open(resource_path("sol.png")), size=(24, 24))
            self.icons['moon'] = ctk.CTkImage(Image.open(resource_path("luna.png")), size=(24, 24))
        except Exception as e:
            print(f"Error cargando iconos de tema: {e}")

        try:
            logo_light_theme = Image.open(resource_path("logo_oscuro.png"))
            logo_dark_theme = Image.open(resource_path("logo_claro.png"))

            original_width, original_height = logo_light_theme.size
            target_width = 150
            aspect_ratio = original_height / original_width
            target_height = int(target_width * aspect_ratio)

            self.logo_image = ctk.CTkImage(
                light_image=logo_light_theme,
                dark_image=logo_dark_theme,
                size=(target_width, target_height)
            )
        except Exception as e:
            print(f"Error al cargar las imágenes del logo: {e}")
            self.logo_image = None

    def _load_and_prepare_gif(self):
        self.gif_pil_frames = []
        self.gif_frame_index = 0
        if not self.gif_names: return
        try:
            self.progress_frame.update_idletasks()
            container_width, container_height = self.progress_frame.winfo_width(), self.progress_frame.winfo_height()
            padding = 25
            max_w, max_h = container_width - padding, container_height - padding
            if max_w <= 50 or max_h <= 50: return
            chosen_gif = random.choice(self.gif_names)
            gif_path = resource_path(chosen_gif)
            with Image.open(gif_path) as im:
                self.gif_delay = im.info.get('duration', 100)
                original_width, original_height = im.size
                if original_height <= 0 or original_width <= 0: return
                ratio = min(max_w / original_width, max_h / original_height)
                target_width, target_height = int(original_width * ratio), int(original_height * ratio)
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
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left_sidebar_container = ctk.CTkFrame(self, fg_color="transparent")
        left_sidebar_container.grid(row=0, column=0, sticky="ns", padx=15, pady=15)

        right_sidebar_container = ctk.CTkFrame(self, fg_color="transparent")
        right_sidebar_container.grid(row=0, column=2, sticky="ns", padx=15, pady=15)

        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=1, sticky="nsew", pady=10)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(0, weight=1)

        self._create_home_page(center_frame)


        self._create_left_sidebar(left_sidebar_container)
        self._create_right_sidebar(right_sidebar_container)
        self._create_footer()

    def _create_home_page(self, parent):
        """Crea la página principal (Home) usando componentes reutilizables."""
        self.home_page = HomePage(parent, logo_image=self.logo_image)
        self.home_page.grid(row=0, column=0, sticky="nsew")

        # Mapeo de referencias para mantener compatibilidad con el controller actual
        self.header_frame = self.home_page.header
        self.lbl_title = self.home_page.header.lbl_title
        self.lbl_greet = self.home_page.header.lbl_greet

        self.main_buttons_frame = self.home_page.main_buttons_frame
        self.main_buttons = self.home_page.main_buttons

        self.progress_frame = self.home_page.progress_panel
        self.lbl_progress_status = self.home_page.progress_panel.lbl_progress_status
        self.lbl_percent = self.home_page.progress_panel.lbl_percent
        self.progress_bar = self.home_page.progress_panel.progress_bar
        self.lbl_current_file = self.home_page.progress_panel.lbl_current_file
        self.btn_cancel = self.home_page.progress_panel.btn_cancel
        self.btn_cancel.configure(width=BTN_W_MAIN, height=BTN_H_MAIN)

    def _create_header(self, parent):
        self.header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(20, 15))
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="", image=self.logo_image)
        self.lbl_title.pack()
        self.lbl_greet = ctk.CTkLabel(self.header_frame, font=("Segoe UI", 13))
        self.lbl_greet.pack()

    def _create_main_buttons(self, parent):
        self.main_buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_buttons_frame.grid(row=1, column=0, sticky="ew", pady=5)
        opts = {"width": BTN_W_MAIN, "height": BTN_H_MAIN, "corner_radius": 8, "font": ("Segoe UI", 11, "bold"),
                "text_color": "#FFFFFF"}
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
        for btn in self.main_buttons.values(): btn.pack(pady=3, fill="x", expand=True)

    def _create_progress_and_cancel(self, parent):
        self.progress_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.progress_frame.grid(row=2, column=0, sticky="nsew", pady=(1, 1))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_rowconfigure(1, weight=1)
        self.progress_frame.grid_rowconfigure(3, weight=1)

        self.progress_content_wrapper = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.progress_content_wrapper.grid(row=0, column=0, sticky="nsew", rowspan=4)
        self.lbl_gif_animation = ctk.CTkLabel(self.progress_content_wrapper, text="")
        self.lbl_gif_animation.pack(expand=True)

        self.lbl_progress_status = ctk.CTkLabel(self.progress_frame, text="", font=("Segoe UI", 11, "bold"))
        self.lbl_percent = ctk.CTkLabel(self.progress_frame, text="", font=("Segoe UI", 11, "bold"))
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=10, corner_radius=8, mode='determinate')
        self.progress_bar.set(0)
        self.lbl_current_file = ctk.CTkLabel(self.progress_frame, text="", font=("Segoe UI", 9), anchor="w")
        self.btn_cancel = ctk.CTkButton(self.progress_frame, width=150, height=28)

    def _create_left_sidebar(self, parent):
        """Sidebar izquierdo usando el componente LeftSidebar."""
        sidebar_height = max(200, self.winfo_height() - 40)
        self.side_left = LeftSidebar(parent, height=sidebar_height, corner_radius=15)
        self.side_left.pack(expand=True, anchor="center")
        self.canvas_left = self.side_left.canvas
        self.canvas_left.bind("<Configure>", self._paint_left_sidebar_text)

    def _create_right_sidebar(self, parent):
        """Sidebar derecho usando el componente RightSidebar."""
        self.right_sidebar = RightSidebar(parent, icons=self.icons, current_theme=self.current_theme)
        self.right_sidebar.pack(expand=True, anchor="center")
        self.sidebar_buttons = self.right_sidebar.buttons

    def _create_footer(self):
        """Footer usando el componente Footer."""
        footer_text = f"Copyright ©{YEAR} - {AUTHOR} {self._tr(' - All rights reserved')}"
        self.footer_frame = Footer(self, text=footer_text)
        self.footer_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=0, pady=0)

    def update_ui_texts(self):
        # Check if window is being destroyed or already destroyed
        if not self.winfo_exists() or getattr(self, "_closing", False):
            return
        
        hour = datetime.datetime.now().hour
        greet_key = "greet_m" if 5 <= hour < 12 else "greet_a" if 12 <= hour < 19 else "greet_n"
        try:
            user = os.getlogin().lower().capitalize()
        except OSError:
            user = "User"
        greeting = self._tr(greet_key)
        
        # Safely configure label if it exists
        try:
            if hasattr(self, 'lbl_greet') and self.lbl_greet.winfo_exists():
                self.lbl_greet.configure(text=f"{greeting} {user}{self._tr('welcome')}")
        except tk.TclError:
            pass
        
        key_map = {"selpath": "btn_sel_lecturas", "choose": "btn_choose_folder", "create_tree": "btn_create_tree",
                    "openlect": "btn_open_lecturas", "openlast": "btn_open_last", "delete": "btn_del"}
        for key, btn in self.main_buttons.items():
            try:
                if btn.winfo_exists():
                    if key in key_map: btn.configure(text=self._tr(key_map[key]))
                    btn.configure(width=BTN_W_MAIN, height=BTN_H_MAIN)
            except tk.TclError:
                pass
        
        try:
            if hasattr(self, 'btn_cancel') and self.btn_cancel.winfo_exists():
                self.btn_cancel.configure(text=self._tr("btn_cancel"))
        except tk.TclError:
            pass
        
        try:
            if hasattr(self, 'lbl_progress_status') and self.lbl_progress_status.winfo_exists():
                self.lbl_progress_status.configure(text=self._tr("progress_processing_text") if self.controller.is_processing else self._idle_waiting_variants[0])
        except tk.TclError:
            pass

        tooltip_map = {
            "ver": "tooltip_ver",
            "nover": "tooltip_nover",
            "theme_icon": "tooltip_tema",
            "traducir": "tooltip_idioma",
            "restaurar": "tooltip_restaurar",
            "github": "tooltip_github",
            "info": "tooltip_info"
        }
        for key, btn in self.sidebar_buttons.items():
            try:
                if key in tooltip_map and btn.winfo_exists():
                    if key in self.tooltips:
                        self.tooltips[key].text = self._tr(tooltip_map[key])
                    else:
                        self.tooltips[key] = CustomTooltip(btn, text=self._tr(tooltip_map[key]))
            except tk.TclError:
                pass

    def apply_theme(self):
        # Check if window is being destroyed or already destroyed
        if not self.winfo_exists() or getattr(self, "_closing", False):
            return
            
        is_light = self.current_theme == "Light"
        set_theme(self.current_theme)
        theme = COLORS['light' if is_light else 'dark']
        
        try:
            self.configure(fg_color=theme['bg'])
            self.side_left.configure(fg_color=theme['left_bar'])
            self.canvas_left.configure(bg=theme['left_bar'])
            self._paint_left_sidebar_text()
            self.progress_bar.configure(fg_color=theme['progress_bar'])
        except tk.TclError:
            pass

        btn_fg_color = COLORS['dark']['bg'] if is_light else COLORS['light']['bg']
        btn_hover_color = COLORS['sidebar_hover']['light'] if is_light else COLORS['sidebar_hover']['dark']
        for key, btn in self.sidebar_buttons.items():
            try:
                if btn.winfo_exists():
                    if key != "theme_icon":
                        btn.configure(fg_color=btn_fg_color, hover_color=btn_hover_color)
            except tk.TclError:
                pass

        try:
            if self.sidebar_buttons['theme_icon'].winfo_exists():
                self.sidebar_buttons['theme_icon'].configure(
                    image=self.icons.get('moon') if is_light else self.icons.get('sun'),
                    fg_color=btn_fg_color, hover_color=btn_hover_color)
        except tk.TclError:
            pass

        try:
            # Footer (barra inferior) - cubrir todo el ancho y mantener buen contraste
            footer_text_color = COLORS["dark"]["text"] if self.current_theme == "Light" else COLORS["light"]["text"]
            self.footer_frame.configure(fg_color=theme["left_bar"])
            self.footer_frame.lbl.configure(text_color=footer_text_color)
        except tk.TclError:
            pass

        self.set_progress(self.target_progress, None, True)

    def _paint_left_sidebar_text(self, event=None):
        self.canvas_left.delete("all")
        w, h = self.canvas_left.winfo_width(), self.canvas_left.winfo_height()
        if w > 1 and h > 1:
            color = COLORS['dark']['text'] if self.current_theme == "Light" else COLORS['light']['text']
            self.canvas_left.create_text(w / 2, h / 2, text=f"Lectorcito Pro v{VERSION}", angle=90, font=("Segoe UI", 10, "bold"), fill=color)

    def _animate_progress(self):
        # Check if window is being destroyed or already destroyed
        if not self.winfo_exists() or getattr(self, "_closing", False):
            return
            
        if self.animation_after_id:
            try:
                self.after_cancel(self.animation_after_id)
            except tk.TclError:
                pass
            self.animation_after_id = None
        diff = self.target_progress - self.current_progress
        if abs(diff) < 0.1:
            self.current_progress = self.target_progress
        else:
            self.current_progress += diff * 0.1
            self.animation_after_id = self.after(20, self._animate_progress)
        try:
            if self.progress_bar.winfo_exists():
                self.progress_bar.set(self.current_progress / 100)
        except tk.TclError:
            pass

    def _animate_gif(self):
        # Check if window is being destroyed or already destroyed
        if not self.winfo_exists() or getattr(self, "_closing", False):
            return
            
        if self.gif_animation_after_id:
            try:
                self.after_cancel(self.gif_animation_after_id)
            except tk.TclError:
                pass
        if self.gif_pil_frames:
            try:
                if self.lbl_gif_animation.winfo_exists():
                    pil_frame = self.gif_pil_frames[self.gif_frame_index]
                    ctk_image = ctk.CTkImage(light_image=pil_frame, dark_image=pil_frame, size=pil_frame.size)
                    self.lbl_gif_animation.configure(image=ctk_image)
                    self.gif_frame_index = (self.gif_frame_index + 1) % len(self.gif_pil_frames)
                    self.gif_animation_after_id = self.after(self.gif_delay, self._animate_gif)
            except tk.TclError:
                pass

    def _start_idle_status_animation(self):
        self._idle_waiting_index = 0
        def _tick():
            if not self.winfo_exists() or self.controller.is_processing:
                return
            self._idle_waiting_index = (self._idle_waiting_index + 1) % len(self._idle_waiting_variants)
            try:
                self.lbl_progress_status.configure(text=self._idle_waiting_variants[self._idle_waiting_index])
            except tk.TclError:
                return
            self._idle_status_after_id = self.after(600, _tick)
        self._idle_status_after_id = self.after(600, _tick)

    def _stop_idle_status_animation(self):
        if self._idle_status_after_id:
            try:
                self.after_cancel(self._idle_status_after_id)
            except tk.TclError:
                pass
            self._idle_status_after_id = None

    def set_progress(self, percentage, file_context=None, force_color=False):
        # Check if window is being destroyed or already destroyed
        if not self.winfo_exists() or getattr(self, "_closing", False):
            return
            
        new_target = int(percentage)
        if new_target != self.target_progress or force_color:
            self.target_progress = new_target
            color = COLORS['progress_colors']['done'] if self.target_progress >= 99 else COLORS['progress_colors'][
                'mid'] if self.target_progress >= 50 else COLORS['progress_colors']['start']
            try:
                if self.progress_bar.winfo_exists():
                    self.progress_bar.configure(progress_color=color)
            except tk.TclError:
                pass

        try:
            if self.progress_bar.winfo_exists() and self.progress_bar.cget("mode") == "determinate":
                if self.lbl_percent.winfo_exists():
                    self.lbl_percent.configure(text=f"{self.target_progress}%")
            else:
                if self.lbl_percent.winfo_exists():
                    self.lbl_percent.configure(text="")
        except tk.TclError:
            pass

        try:
            if file_context and self.lbl_current_file.winfo_exists():
                self.lbl_current_file.configure(text=file_context)
        except tk.TclError:
            pass
        if self.animation_after_id is None: self._animate_progress()

    def _change_and_reschedule_gif(self):
        self.gif_change_timer_id = None

    def toggle_ui_for_processing(self, is_active: bool, mode: str = 'determinate', text: str = None):
        # Check if window is being destroyed or already destroyed
        if not self.winfo_exists() or getattr(self, "_closing", False):
            return
            
        state = "disabled" if is_active else "normal"
        for btn in self.main_buttons.values():
            try:
                if btn.winfo_exists():
                    btn.configure(state=state)
            except tk.TclError:
                pass
        for btn in self.sidebar_buttons.values():
            try:
                if btn.winfo_exists():
                    btn.configure(state=state)
            except tk.TclError:
                pass

        self._stop_idle_status_animation()

        if is_active:
            if self.gif_animation_after_id:
                try:
                    self.after_cancel(self.gif_animation_after_id)
                except tk.TclError:
                    pass
                self.gif_animation_after_id = None

            try:
                if self.progress_bar.winfo_exists():
                    self.progress_bar.configure(mode=mode)
                    self.progress_bar.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="ew")
            except tk.TclError:
                pass

            if mode == 'indeterminate':
                try:
                    if self.progress_bar.winfo_exists():
                        self.progress_bar.start()
                    if self.lbl_progress_status.winfo_exists():
                        self.lbl_progress_status.configure(text=text if text else "")
                        self.lbl_progress_status.grid(row=0, column=0, padx=10, pady=(15, 0), sticky="s")
                    if self.lbl_percent.winfo_exists():
                        self.lbl_percent.grid_forget()
                    if self.lbl_current_file.winfo_exists():
                        self.lbl_current_file.grid_forget()
                except tk.TclError:
                    pass
            else:
                try:
                    if self.progress_bar.winfo_exists():
                        self.progress_bar.stop()
                    self.set_progress(0)
                    if self.lbl_progress_status.winfo_exists():
                        self.lbl_progress_status.configure(text=self._tr("progress_processing_text") if self.controller.is_processing else self._idle_waiting_variants[0])
                        self.lbl_progress_status.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
                    if self.lbl_percent.winfo_exists():
                        self.lbl_percent.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="e")
                    if self.lbl_current_file.winfo_exists():
                        self.lbl_current_file.grid(row=2, column=0, padx=10, sticky="w")
                except tk.TclError:
                    pass

            try:
                if self.btn_cancel.winfo_exists():
                    self.btn_cancel.grid(row=3, column=0, pady=(10, 10), sticky="s")
            except tk.TclError:
                pass
        else:
            try:
                if self.progress_bar.winfo_exists():
                    self.progress_bar.stop()
                for widget in (self.lbl_progress_status, self.lbl_percent, self.progress_bar, self.lbl_current_file, self.btn_cancel):
                    if widget.winfo_exists():
                        widget.grid_forget()
                if self.progress_bar.winfo_exists():
                    self.progress_bar.configure(mode='determinate')
                self.set_progress(0, None, True)
                if self.lbl_progress_status.winfo_exists():
                    self.lbl_progress_status.configure(text=self._idle_waiting_variants[0])
                if self.lbl_percent.winfo_exists():
                    self.lbl_percent.configure(text="0%")
                if self.lbl_current_file.winfo_exists():
                    self.lbl_current_file.configure(text="")

                if self.lbl_progress_status.winfo_exists():
                    self.lbl_progress_status.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
                if self.lbl_percent.winfo_exists():
                    self.lbl_percent.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="e")
                if self.progress_bar.winfo_exists():
                    self.progress_bar.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="ew")
                if self.lbl_current_file.winfo_exists():
                    self.lbl_current_file.grid(row=2, column=0, padx=10, sticky="w")
            except tk.TclError:
                pass

            self._start_idle_status_animation()

    def show_message(self, title_key: str, message_key: str, *args):
        # Check if the window still exists and is not being closed
        if not self.winfo_exists() or getattr(self, "_closing", False):
            return
        try:
            MessageDialog(self, self._tr(title_key), self._tr(message_key, *args))
        except tk.TclError:
            # Silently handle TclError when window is being destroyed
            pass
        except Exception as e:
            # Log unexpected errors for debugging
            self.logger.error(f"Unexpected error showing message dialog: {e}")

    def show_app_info(self):
        # Check if the window still exists and is not being closed
        if not self.winfo_exists() or getattr(self, "_closing", False):
            return
        try:
            from ...features.help.application.open_manual import get_infographic_path
            image_path = get_infographic_path()
            if os.path.exists(image_path):
                InfographicDialog(self, title=self._tr("manual_title"), image_path=image_path)
            else:
                self.show_message("error_title", "msg_infographic_error")
        except tk.TclError:
            # Silently handle TclError when window is being destroyed
            pass
        except Exception as e:
            # Log unexpected errors for debugging
            self.logger.error(f"Unexpected error showing app info: {e}")