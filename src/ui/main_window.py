import datetime
import os
import random
import webbrowser
from tkinter import Canvas

import customtkinter as ctk

from core.constants import (
    AUTHOR,
    BTN_H_ICON,
    BTN_H_MAIN,
    BTN_W_ICON,
    BTN_W_MAIN,
    COLORS,
    GIF_CHANGE_INTERVAL_MS,
    PROGRESS_W,
    REPO_URL,
    SIDEBAR_WIDTH,
    VERSION,
    YEAR,
)
from core.i18n import I18n
from core.logger import get_logger
from services.resource_loader import load_dual_icon, load_gif_frames, load_icon_set, load_single_icon
from ui.components.buttons import create_main_buttons
from ui.components.header import create_header
from ui.components.progress import create_progress_area
from ui.components.sidebar import create_left_sidebar, create_right_sidebar
from ui.components.tooltip import CustomTooltip
from ui.dialogs.info_view import InfographicDialog
from utils.path_utils import resource_path

logger = get_logger(__name__)


class MainWindow(ctk.CTk):
    def __init__(self, cfg, controller):
        super().__init__()
        self.attributes("-alpha", 0.0)
        self.config = cfg
        self.controller = controller
        self.lang = self.config.get("language", "es")
        self.current_theme = self.config.get("theme", "Light")
        self.current_progress = 0
        self.target_progress = 0
        self.animation_after_id = None
        self.tooltips = {}
        self.translator = I18n(self.lang)
        self.REPO_URL = REPO_URL

        self.gif_names = [
            "Cat_Working.gif",
            "Hacker_Coding.gif",
            "Computer_Coding.gif",
            "Mad_Artificial_Intelligence.gif",
            "Thinking_Working.gif",
            "Ctrl_C_V.gif",
            "Coding_Coffee.gif",
        ]
        self.gif_pil_frames = []
        self.gif_frame_index = 0
        self.gif_animation_after_id = None
        self.gif_delay = 100
        self.gif_change_timer_id = None

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
            self.geometry(f"+{x}+{y}")
        except Exception as e:
            logger.error("Error centering main window: %s", e)

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1:
            alpha = min(alpha + 0.08, 1.0)
            self.attributes("-alpha", alpha)
            self.after(15, self._fade_in)

    def _close_with_fade_out(self):
        if self.gif_animation_after_id:
            self.after_cancel(self.gif_animation_after_id)
        if self.gif_change_timer_id:
            self.after_cancel(self.gif_change_timer_id)
        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha = max(alpha - 0.08, 0.0)
            self.attributes("-alpha", alpha)
            self.after(15, self._close_with_fade_out)
        else:
            self.destroy()

    def _tr(self, key, *args):
        return self.translator.tr(key, *args, lang=self.lang)

    def _load_image_assets(self):
        self.icons = load_icon_set(("ver", "nover", "traducir", "restaurar", "github", "info"))
        self.icons["sun"] = load_single_icon("sol.png", size=(24, 24))
        self.icons["moon"] = load_single_icon("luna.png", size=(24, 24))

        try:
            logo_light_theme = resource_path("logo_oscuro.png")
            logo_dark_theme = resource_path("logo_claro.png")
            if os.path.exists(logo_light_theme):
                from PIL import Image

                light_im = Image.open(logo_light_theme)
                original_width, original_height = light_im.size
                target_width = 150
                aspect_ratio = original_height / original_width
                target_height = int(target_width * aspect_ratio)
                self.logo_image = load_dual_icon("logo_oscuro.png", "logo_claro.png", (target_width, target_height))
            else:
                self.logo_image = None
        except Exception as e:
            logger.error("Error al cargar las imágenes del logo: %s", e)
            self.logo_image = None

    def _load_and_prepare_gif(self):
        self.gif_pil_frames = []
        self.gif_frame_index = 0
        if not self.gif_names:
            return
        try:
            self.progress_frame.update_idletasks()
            container_width, container_height = self.progress_frame.winfo_width(), self.progress_frame.winfo_height()
            padding = 25
            max_w, max_h = container_width - padding, container_height - padding
            if max_w <= 50 or max_h <= 50:
                return
            chosen_gif = random.choice(self.gif_names)
            frames, delay = load_gif_frames(chosen_gif, max_w, max_h)
            self.gif_pil_frames = frames
            self.gif_delay = delay
        except Exception as e:
            logger.error("Error al cargar o redimensionar el GIF: %s", e)
            self.gif_pil_frames = []

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left_sidebar_container = ctk.CTkFrame(self, fg_color="transparent")
        left_sidebar_container.grid(row=0, column=0, sticky="ns", padx=15, pady=15)

        right_sidebar_container = ctk.CTkFrame(self, fg_color="transparent")
        right_sidebar_container.grid(row=0, column=2, sticky="ns", padx=15, pady=15)

        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=1, sticky="nsew", pady=10)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(2, weight=1)

        self.header_frame, self.lbl_title, self.lbl_greet = create_header(center_frame, self.logo_image)

        self.main_buttons_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        self.main_buttons_frame.grid(row=1, column=0, sticky="ew", pady=5)
        self.main_buttons = create_main_buttons(self.main_buttons_frame)

        progress_widgets = create_progress_area(center_frame)
        self.progress_frame = progress_widgets["frame"]
        self.progress_content_wrapper = progress_widgets["content_wrapper"]
        self.lbl_gif_animation = progress_widgets["gif"]
        self.lbl_progress_status = progress_widgets["status"]
        self.lbl_percent = progress_widgets["percent"]
        self.progress_bar = progress_widgets["bar"]
        self.lbl_current_file = progress_widgets["current_file"]
        self.btn_cancel = progress_widgets["cancel"]

        self.side_left, self.canvas_left = create_left_sidebar(left_sidebar_container)
        _, self.sidebar_buttons = create_right_sidebar(right_sidebar_container, self.icons, self.current_theme)
        self._create_footer()

    def _create_footer(self):
        self.footer_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.footer_frame.grid(row=1, column=0, columnspan=3, sticky="sew")
        ctk.CTkLabel(
            self.footer_frame,
            text=f"Copyright © {YEAR} - {AUTHOR} - All Rights Reserved.",
            font=("Segoe UI", 9),
        ).place(relx=0.5, rely=0.5, anchor="center")

    def update_ui_texts(self):
        hour = datetime.datetime.now().hour
        greet_key = "greet_m" if 5 <= hour < 12 else "greet_a" if 12 <= hour < 19 else "greet_n"
        try:
            user = os.getlogin().lower().capitalize()
        except OSError:
            user = "User"
        greeting = self._tr(greet_key)
        self.lbl_greet.configure(text=f"{greeting} {user}{self._tr('welcome')}")
        key_map = {
            "selpath": "btn_sel_lecturas",
            "choose": "btn_choose_folder",
            "create_tree": "btn_create_tree",
            "openlect": "btn_open_lecturas",
            "openlast": "btn_open_last",
            "delete": "btn_del",
        }
        for key, btn in self.main_buttons.items():
            if key in key_map:
                btn.configure(text=self._tr(key_map[key]))
        self.btn_cancel.configure(text=self._tr("btn_cancel"))
        self.lbl_progress_status.configure(text=self._tr("progress_processing_text"))

        tooltip_map = {
            "ver": "tooltip_ver",
            "nover": "tooltip_nover",
            "theme_icon": "tooltip_tema",
            "traducir": "tooltip_idioma",
            "restaurar": "tooltip_restaurar",
            "github": "tooltip_github",
            "info": "tooltip_info",
        }
        for key, btn in self.sidebar_buttons.items():
            if key in tooltip_map:
                if key in self.tooltips:
                    self.tooltips[key].text = self._tr(tooltip_map[key])
                else:
                    self.tooltips[key] = CustomTooltip(btn, text=self._tr(tooltip_map[key]))

    def apply_theme(self):
        is_light = self.current_theme == "Light"
        ctk.set_appearance_mode(self.current_theme)
        theme = COLORS["light" if is_light else "dark"]
        self.configure(fg_color=theme["bg"])
        self.side_left.configure(fg_color=theme["left_bar"])
        self.canvas_left.configure(bg=theme["left_bar"])
        self._paint_left_sidebar_text()
        self.progress_bar.configure(fg_color=theme["progress_bar"])

        btn_fg_color = COLORS["dark"]["bg"] if is_light else COLORS["light"]["bg"]
        btn_hover_color = COLORS["sidebar_hover"]["light"] if is_light else COLORS["sidebar_hover"]["dark"]
        for key, btn in self.sidebar_buttons.items():
            if key != "theme_icon":
                btn.configure(fg_color=btn_fg_color, hover_color=btn_hover_color)

        self.sidebar_buttons["theme_icon"].configure(
            image=self.icons.get("moon") if is_light else self.icons.get("sun"),
            fg_color=btn_fg_color,
            hover_color=btn_hover_color,
        )

        self.set_progress(self.target_progress, None, True)

    def _paint_left_sidebar_text(self, event=None):
        self.canvas_left.delete("all")
        w, h = self.canvas_left.winfo_width(), self.canvas_left.winfo_height()
        if w > 1 and h > 1:
            color = COLORS["dark"]["text"] if self.current_theme == "Light" else COLORS["light"]["text"]
            self.canvas_left.create_text(
                w / 2, h / 2, text=f"Lectorcito Pro v{VERSION}", angle=90, font=("Segoe UI", 10, "bold"), fill=color
            )

    def _animate_progress(self):
        if self.animation_after_id:
            self.after_cancel(self.animation_after_id)
            self.animation_after_id = None
        diff = self.target_progress - self.current_progress
        if abs(diff) < 0.1:
            self.current_progress = self.target_progress
        else:
            self.current_progress += diff * 0.1
            self.animation_after_id = self.after(20, self._animate_progress)
        self.progress_bar.set(self.current_progress / 100)

    def _animate_gif(self):
        if self.gif_animation_after_id:
            self.after_cancel(self.gif_animation_after_id)
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
            color = (
                COLORS["progress_colors"]["done"]
                if self.target_progress >= 99
                else COLORS["progress_colors"]["mid"]
                if self.target_progress >= 50
                else COLORS["progress_colors"]["start"]
            )
            self.progress_bar.configure(progress_color=color)

        if self.progress_bar.cget("mode") == "determinate":
            self.lbl_percent.configure(text=f"{self.target_progress}%")
        else:
            self.lbl_percent.configure(text="")

        if file_context:
            self.lbl_current_file.configure(text=file_context)
        if self.animation_after_id is None:
            self._animate_progress()

    def _change_and_reschedule_gif(self):
        if not self.controller.is_processing:
            self._load_and_prepare_gif()
            self._animate_gif()
        self.gif_change_timer_id = self.after(GIF_CHANGE_INTERVAL_MS, self._change_and_reschedule_gif)

    def toggle_ui_for_processing(self, is_active: bool, mode: str = "determinate", text: str | None = None):
        state = "disabled" if is_active else "normal"
        for btn in self.main_buttons.values():
            btn.configure(state=state)
        for btn in self.sidebar_buttons.values():
            btn.configure(state=state)

        if self.gif_change_timer_id:
            self.after_cancel(self.gif_change_timer_id)
            self.gif_change_timer_id = None

        if is_active:
            if self.gif_animation_after_id:
                self.after_cancel(self.gif_animation_after_id)
                self.gif_animation_after_id = None
            self.progress_content_wrapper.grid_remove()

            self.progress_bar.configure(mode=mode)
            self.progress_bar.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="ew")

            if mode == "indeterminate":
                self.progress_bar.start()
                self.lbl_progress_status.configure(text=text if text else "")
                self.lbl_progress_status.grid(row=0, column=0, padx=10, pady=(15, 0), sticky="s")
                self.lbl_percent.grid_forget()
                self.lbl_current_file.grid_forget()
            else:
                self.progress_bar.stop()
                self.set_progress(0)
                self.lbl_progress_status.configure(text=self._tr("progress_processing_text"))
                self.lbl_progress_status.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
                self.lbl_percent.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="e")
                self.lbl_current_file.grid(row=2, column=0, padx=10, sticky="w")

            self.btn_cancel.grid(row=3, column=0, pady=(10, 10), sticky="s")
        else:
            self.progress_bar.stop()
            for widget in (
                self.lbl_progress_status,
                self.lbl_percent,
                self.progress_bar,
                self.lbl_current_file,
                self.btn_cancel,
            ):
                widget.grid_forget()

            self.progress_content_wrapper.grid(row=0, column=0, sticky="nsew", rowspan=4)
            self.after(50, self._load_and_prepare_gif)

            def show_gif():
                if self.gif_pil_frames:
                    self._animate_gif()
                    self.gif_change_timer_id = self.after(GIF_CHANGE_INTERVAL_MS, self._change_and_reschedule_gif)

            self.after(60, show_gif)
            self.after(100, lambda: self.set_progress(0))

    def show_message(self, title_key: str, message_key: str, *args):
        from ui.dialogs.base_dialog import MessageDialog

        MessageDialog(self, self._tr(title_key), self._tr(message_key, *args))

    def show_app_info(self):
        image_path = resource_path("Infografía_LectorcitoPro.png")
        if os.path.exists(image_path):
            InfographicDialog(self, title=self._tr("manual_title"), image_path=image_path)
        else:
            self.show_message("error_title", "msg_infographic_error")
