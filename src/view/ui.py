# src/view/ui.py
from __future__ import annotations

import customtkinter as ctk
import datetime
import os
import random

from view.translations import TRANSLATIONS
from view.dialogs import MessageDialog, InfographicDialog
from view.tooltip import CustomTooltip

from view.ui_constants import (
    VERSION, YEAR, AUTHOR, REPO_URL,
    COLORS, BTN_W_MAIN, BTN_H_MAIN
)
from view.ui_assets import load_sidebar_icons, load_logo, safe_set_window_icon
from view.sidebars import LeftSidebar, RightSidebar
from view.status_panel import StatusPanel
from utils import resource_path


class LectorcitoApp(ctk.CTk):

    def __init__(self, cfg: dict, controller):
        super().__init__()
        self.attributes("-alpha", 0.0)

        self.TRANSLATIONS = TRANSLATIONS
        self.config = cfg
        self.controller = controller
        self.lang = self.config.get("language", "es")
        self.current_theme = self.config.get("theme", "Light")

        self.REPO_URL = REPO_URL
        self.tooltips: dict[str, CustomTooltip] = {}

        self.title("Lectorcito Pro")
        self.geometry("600x500")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)

        # Icono app (compatible con dialogs)
        safe_set_window_icon(self)

        # Assets
        self.icons = load_sidebar_icons()
        self.logo_image = load_logo(target_width=150)

        # UI
        self._is_centered = False
        self.bind("<Configure>", self._on_configure_center)
        self._build_ui()

        # Textos + tema + estado inicial
        self.update_ui_texts()
        self.apply_theme()
        self.toggle_ui_for_processing(is_active=False)

    # ---------------------------
    # Arranque / cierre
    # ---------------------------
    def _on_configure_center(self, event=None):
        if not self._is_centered:
            self._is_centered = True
            self._center_on_screen()
            self.after(10, self._fade_in)

    def _center_on_screen(self):
        try:
            self.update_idletasks()
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            ww, wh = self.winfo_width(), self.winfo_height()
            x = (sw // 2) - (ww // 2)
            y = (sh // 2) - (wh // 2)
            self.geometry(f"+{x}+{y}")
        except Exception as e:
            print(f"Error al centrar ventana: {e}")

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1:
            self.attributes("-alpha", min(alpha + 0.08, 1.0))
            self.after(15, self._fade_in)

    def _close_with_fade_out(self):
        # Limpieza tooltips (evita after colgando)
        try:
            for tp in self.tooltips.values():
                tp.cleanup()
        except Exception:
            pass

        # Limpieza panel de estado (evita after colgando)
        try:
            self.status_panel.cleanup()
        except Exception:
            pass

        alpha = self.attributes("-alpha")
        if alpha > 0:
            self.attributes("-alpha", max(alpha - 0.08, 0.0))
            self.after(15, self._close_with_fade_out)
        else:
            self.destroy()

    # ---------------------------
    # i18n
    # ---------------------------
    def _tr(self, key: str, *args):
        entry = self.TRANSLATIONS.get(self.lang, self.TRANSLATIONS["es"]).get(key, f"<{key}>")
        if isinstance(entry, list):
            return random.choice(entry).format(*args)
        return entry.format(*args)

    # ---------------------------
    # Layout principal
    # ---------------------------
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left_container = ctk.CTkFrame(self, fg_color="transparent")
        left_container.grid(row=0, column=0, sticky="ns", padx=15, pady=15)

        right_container = ctk.CTkFrame(self, fg_color="transparent")
        right_container.grid(row=0, column=2, sticky="ns", padx=15, pady=15)

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=0, column=1, sticky="nsew", pady=10)
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(2, weight=1)

        # Header
        self._create_header(center)

        # Main buttons
        self._create_main_buttons(center)

        # Status panel (reemplaza GIF)
        self._create_status_area(center)

        # Sidebars
        self.left_sidebar = LeftSidebar(left_container, text=f"Lectorcito Pro v{VERSION}")
        self.right_sidebar = RightSidebar(right_container, icons=self.icons, current_theme=self.current_theme)
        self.sidebar_buttons = self.right_sidebar.buttons  # compat con controller

        # Footer
        self._create_footer()

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

        opts = {
            "width": BTN_W_MAIN,
            "height": BTN_H_MAIN,
            "corner_radius": 8,
            "font": ("Segoe UI", 11, "bold"),
            "text_color": "#FFFFFF",
        }

        self.main_buttons = {
            "selpath": ctk.CTkButton(self.main_buttons_frame, **opts),
            "choose": ctk.CTkButton(self.main_buttons_frame, **opts),
            "create_tree": ctk.CTkButton(self.main_buttons_frame, **opts),
            "openlect": ctk.CTkButton(self.main_buttons_frame, **opts),
            "openlast": ctk.CTkButton(
                self.main_buttons_frame, **opts,
                fg_color=COLORS["button"]["green"], hover_color=COLORS["button_hover"]["green_h"]
            ),
            "delete": ctk.CTkButton(
                self.main_buttons_frame, **opts,
                fg_color=COLORS["button"]["red"], hover_color=COLORS["button_hover"]["red_h"]
            )
        }
        for btn in self.main_buttons.values():
            btn.pack(pady=3)

    def _create_status_area(self, parent):
        self.progress_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.progress_frame.grid(row=2, column=0, sticky="nsew", pady=(6, 6))
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.status_panel = StatusPanel(self.progress_frame, min_visible_seconds=2.0)
        self.status_panel.grid(row=0, column=0, sticky="ew")

        # compat: controller espera self.btn_cancel
        self.btn_cancel = self.status_panel.btn_cancel

    def _create_footer(self):
        self.footer_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.footer_frame.grid(row=1, column=0, columnspan=3, sticky="sew")
        ctk.CTkLabel(
            self.footer_frame,
            text=f"Copyright © {YEAR} - {AUTHOR} - All Rights Reserved.",
            font=("Segoe UI", 9)
        ).place(relx=0.5, rely=0.5, anchor="center")

    # ---------------------------
    # Textos UI (incluye tooltips)
    # ---------------------------
    def update_ui_texts(self):
        # Greeting
        hour = datetime.datetime.now().hour
        greet_key = "greet_m" if 5 <= hour < 12 else "greet_a" if 12 <= hour < 19 else "greet_n"
        try:
            user = os.getlogin().lower().capitalize()
        except OSError:
            user = "User"
        self.lbl_greet.configure(text=f"{self._tr(greet_key)} {user}{self._tr('welcome')}")

        # Botones main
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

        # Panel estado: traductor + refresco texts
        self.status_panel.set_translator(lambda k: self._tr(k))

        # Tooltips
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
                txt = self._tr(tooltip_map[key])
                if key in self.tooltips:
                    self.tooltips[key].text = txt
                else:
                    self.tooltips[key] = CustomTooltip(btn, text=txt)

    # ---------------------------
    # Tema
    # ---------------------------
    def apply_theme(self):
        is_light = self.current_theme == "Light"
        ctk.set_appearance_mode(self.current_theme)
        theme = COLORS["light" if is_light else "dark"]

        self.configure(fg_color=theme["bg"])

        # Sidebars
        self.left_sidebar.apply_theme(self.current_theme)
        self.right_sidebar.apply_theme(self.current_theme)

        # Status panel
        self.status_panel.apply_theme(self.current_theme)

    # ---------------------------
    # API usada por el controller
    # ---------------------------
    def get_min_visible_completion_delay_ms(self) -> int:
        return self.status_panel.get_min_visible_completion_delay_ms()

    def set_progress(self, percentage, file_context=None):
        self.status_panel.set_progress(percentage, file_context)

    def toggle_ui_for_processing(self, is_active: bool, mode: str = "determinate", text: str = None, final_status: str = None):
        # Bloqueo / desbloqueo botones
        state = "disabled" if is_active else "normal"
        for btn in self.main_buttons.values():
            btn.configure(state=state)
        for btn in self.sidebar_buttons.values():
            btn.configure(state=state)

        # Panel
        self.status_panel.set_active(is_active, mode=mode, text=text, final_status=final_status)

    # ---------------------------
    # Mensajes / info
    # ---------------------------
    def show_message(self, title_key: str, message_key: str, *args):
        MessageDialog(self, self._tr(title_key), self._tr(message_key, *args))

    def show_app_info(self):
        image_path = resource_path("Infografía_LectorcitoPro.png")
        if os.path.exists(image_path):
            InfographicDialog(self, title=self._tr("manual_title"), image_path=image_path)
        else:
            self.show_message("error_title", "msg_infographic_error")
