from __future__ import annotations

import customtkinter as ctk
import datetime
import os
import random
import webbrowser

from view.translations import TRANSLATIONS
from view.dialogs import MessageDialog
from view.tooltip import CustomTooltip

from view.ui_constants import (
    VERSION, YEAR, AUTHOR, REPO_URL,
    COLORS, BTN_W_MAIN, BTN_H_MAIN
)
from view.ui_assets import load_sidebar_icons, load_logo, safe_set_window_icon
from view.sidebars import LeftSidebar, RightSidebar, PillTextButton
from view.status_panel import StatusPanel


# =============================================================================
# INTERFAZ PRINCIPAL (MAIN WINDOW)
# =============================================================================

class LectorcitoApp(ctk.CTk):

    def __init__(self, cfg: dict, controller):
        super().__init__()

        # Ocultamos ventana inicialmente para evitar parpadeos durante la carga
        self.withdraw()
        self.attributes("-alpha", 0.0)

        self.TRANSLATIONS = TRANSLATIONS
        self.config = cfg
        self.controller = controller
        self.lang = self.config.get("language", "es")
        self.current_theme = self.config.get("theme", "Light")

        self.REPO_URL = REPO_URL
        self.tooltips: dict[str, CustomTooltip] = {}
        self._is_modal_open = False

        # --- Configuracion de Ventana ---
        self.title("Lectorcito Pro")
        self._app_w = 600
        self._app_h = 500
        self.geometry(f"{self._app_w}x{self._app_h}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)

        safe_set_window_icon(self)

        # --- Carga de Recursos ---
        self.icons = load_sidebar_icons()
        self.logo_image = load_logo(target_width=150)

        # --- Construccion UI ---
        self._build_ui()
        self.update_ui_texts()
        self.apply_theme()
        self.toggle_ui_for_processing(is_active=False)

        # Retraso intencional para asegurar carga completa de recursos antes de mostrar
        self.after(1000, self._precise_center_and_show)

    def _precise_center_and_show(self):
        try:
            # Necesario para obtener las dimensiones reales tras el renderizado
            self.update_idletasks()

            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()

            x = int((screen_width - self._app_w) / 2)
            y = int((screen_height - self._app_h) / 2)

            self.geometry(f"{self._app_w}x{self._app_h}+{x}+{y}")

            self.attributes("-alpha", 0.0)
            self.deiconify()
            self._fade_in()

        except Exception:
            self.deiconify()
            self.attributes("-alpha", 1.0)

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1:
            self.attributes("-alpha", min(alpha + 0.08, 1.0))
            self.after(15, self._fade_in)

    def _close_with_fade_out(self):
        # Limpieza explicita para evitar referencias colgadas
        try:
            for tp in self.tooltips.values():
                tp.cleanup()
        except Exception:
            pass
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

    def _tr(self, key: str, *args):
        entry = self.TRANSLATIONS.get(self.lang, self.TRANSLATIONS["es"]).get(key, f"<{key}>")
        if isinstance(entry, list):
            return random.choice(entry).format(*args)
        return entry.format(*args)

    # =========================================================================
    # CONSTRUCCION DE UI
    # =========================================================================

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Contenedores principales
        left_container = ctk.CTkFrame(self, fg_color="transparent")
        left_container.grid(row=0, column=0, sticky="ns", padx=15, pady=(0, 14))

        right_container = ctk.CTkFrame(self, fg_color="transparent")
        right_container.grid(row=0, column=2, sticky="ns", padx=15, pady=(0, 15))

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=0, column=1, sticky="nsew", pady=(5, 5))
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(2, weight=1)

        self._create_header(center)
        self._create_main_buttons(center)
        self._create_status_area(center)

        self.left_sidebar = LeftSidebar(left_container, text=f"Lectorcito Pro v{VERSION}")
        self.right_sidebar = RightSidebar(right_container, icons=self.icons, current_theme=self.current_theme)
        self.sidebar_buttons = self.right_sidebar.buttons

        self._create_footer()

    def _create_header(self, parent):
        self.header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(15, 20))

        self.lbl_title = ctk.CTkLabel(self.header_frame, text="", image=self.logo_image)
        self.lbl_title.pack()

        self.lbl_greet = ctk.CTkLabel(self.header_frame, font=("Segoe UI", 13))
        self.lbl_greet.pack()

    def _create_main_buttons(self, parent):
        is_light = self.current_theme == "Light"
        theme_keys = COLORS["light"] if is_light else COLORS["dark"]

        self.main_menu_frame = ctk.CTkFrame(
            parent,
            fg_color=theme_keys["surface"],
            corner_radius=16,
            border_width=1,
            border_color=theme_keys["border"]
        )
        self.main_menu_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        self.main_buttons_frame = ctk.CTkFrame(self.main_menu_frame, fg_color="transparent")
        self.main_buttons_frame.pack(pady=8, padx=10)

        outside_bg = theme_keys["surface"]
        btn_blue = COLORS["button"]["blue"]
        btn_green = COLORS["button"]["green"]
        btn_red = COLORS["button"]["red"]

        common = {
            "width": BTN_W_MAIN,
            "height": BTN_H_MAIN,
            "outside_bg": outside_bg,
            "border_width": 2,
            "font": ("Segoe UI", 11, "bold"),
            "text_color": "#FFFFFF",
        }

        self.main_buttons = {
            "selpath": PillTextButton(
                self.main_buttons_frame,
                fg_color=btn_blue["bg"], hover_color=btn_blue["hover"], border_color=btn_blue["border"],
                **common
            ),
            "choose": PillTextButton(
                self.main_buttons_frame,
                fg_color=btn_blue["bg"], hover_color=btn_blue["hover"], border_color=btn_blue["border"],
                **common
            ),
            "create_tree": PillTextButton(
                self.main_buttons_frame,
                fg_color=btn_blue["bg"], hover_color=btn_blue["hover"], border_color=btn_blue["border"],
                **common
            ),
            "openlect": PillTextButton(
                self.main_buttons_frame,
                fg_color=btn_blue["bg"], hover_color=btn_blue["hover"], border_color=btn_blue["border"],
                **common
            ),
            "openlast": PillTextButton(
                self.main_buttons_frame,
                fg_color=btn_green["bg"], hover_color=btn_green["hover"], border_color=btn_green["border"],
                **common
            ),
            "delete": PillTextButton(
                self.main_buttons_frame,
                fg_color=btn_red["bg"], hover_color=btn_red["hover"], border_color=btn_red["border"],
                **common
            ),
        }

        BTN_SPACING = 1.0
        for btn in self.main_buttons.values():
            btn.pack(pady=BTN_SPACING, anchor="center")

    def _create_status_area(self, parent):
        self.progress_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.progress_frame.grid(row=2, column=0, sticky="nsew", pady=(5, 5))
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.status_panel = StatusPanel(self.progress_frame, min_visible_seconds=1)
        self.status_panel.grid(row=0, column=0, sticky="ew")

        self.btn_cancel = self.status_panel.btn_cancel

    def _create_footer(self):
        self.footer_frame = ctk.CTkFrame(self, height=35, corner_radius=0)
        self.footer_frame.pack_propagate(False)

        self.footer_frame.place(relx=0.0, rely=1.0, anchor="sw", relwidth=1.0)
        self.footer_frame.lift()

        self.footer_line = ctk.CTkFrame(self.footer_frame, height=1, corner_radius=0)
        self.footer_line.pack(side="top", fill="x")

        self.lbl_copyright = ctk.CTkLabel(
            self.footer_frame,
            text="",
            font=("Segoe UI", 9)
        )
        self.lbl_copyright.place(relx=0.5, rely=0.5, anchor="center")

    # =========================================================================
    # LOGICA DE ACTUALIZACION VISUAL
    # =========================================================================

    def update_ui_texts(self):
        # Saludo dinamico segun la hora
        hour = datetime.datetime.now().hour
        greet_key = "greet_m" if 5 <= hour < 12 else "greet_a" if 12 <= hour < 19 else "greet_n"
        try:
            user = os.getlogin().lower().capitalize()
        except OSError:
            user = "User"
        self.lbl_greet.configure(text=f"{self._tr(greet_key)} {user}{self._tr('welcome')}")

        # Mapeo de botones principales
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

        self.status_panel.set_translator(lambda k: self._tr(k))
        self.lbl_copyright.configure(text=self._tr("footer_copyright", YEAR, AUTHOR))

        # Tooltips de barra lateral
        tooltip_map = {
            "ver": "tooltip_ver",
            "nover": "tooltip_nover",
            "etiqueta": "tooltip_etiqueta",
            "theme_icon": "tooltip_tema",
            "traducir": "tooltip_idioma",
            "restaurar": "tooltip_restaurar",
            "perfil": "tooltip_perfil",
            "github": "tooltip_github",
            "info": "tooltip_info",
            "ajustes": "tooltip_ajustes",
        }

        for key, btn in self.sidebar_buttons.items():
            if key in tooltip_map:
                txt = self._tr(tooltip_map[key])
                if key in self.tooltips:
                    self.tooltips[key].text = txt
                else:
                    self.tooltips[key] = CustomTooltip(btn, text=txt)

    def apply_theme(self):
        is_light = self.current_theme == "Light"
        ctk.set_appearance_mode(self.current_theme)

        theme_keys = COLORS["light"] if is_light else COLORS["dark"]

        self.configure(fg_color=theme_keys["bg"])

        self.left_sidebar.apply_theme(self.current_theme)
        self.right_sidebar.apply_theme(self.current_theme)
        self.status_panel.apply_theme(self.current_theme)

        try:
            self.main_menu_frame.configure(fg_color=theme_keys["surface"], border_color=theme_keys["border"])
        except Exception:
            pass

        for btn in self.main_buttons.values():
            try:
                btn.configure(outside_bg=theme_keys["surface"])
            except Exception:
                pass

        try:
            self.footer_frame.configure(fg_color=theme_keys["footer_bg"])
            self.footer_line.configure(fg_color=theme_keys["separator_line"])
            self.lbl_greet.configure(text_color=theme_keys["text"])

            for widget in self.footer_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text_color=theme_keys["text_secondary"])
        except Exception:
            pass

    def switch_theme_animated(self, new_theme: str):
        self._pending_new_theme = new_theme
        self._fade_out_for_switch()

    def _fade_out_for_switch(self):
        try:
            alpha = self.attributes("-alpha")
            if alpha > 0.0:
                self.attributes("-alpha", max(alpha - 0.12, 0.0))
                self.after(12, self._fade_out_for_switch)
            else:
                self.current_theme = self._pending_new_theme
                self.apply_theme()
                self._fade_in()
        except Exception:
            # Fallback seguro en caso de error UI
            self.current_theme = self._pending_new_theme
            self.apply_theme()
            self.attributes("-alpha", 1.0)


    # =========================================================================
    # ESTADO Y CONTROL
    # =========================================================================

    def get_min_visible_completion_delay_ms(self) -> int:
        return self.status_panel.get_min_visible_completion_delay_ms()

    def set_progress(self, percentage, file_context=None):
        self.status_panel.set_progress(percentage, file_context)

    def toggle_ui_for_processing(self, is_active: bool, mode: str = "determinate", text: str = None,
                                 final_status: str = None):
        if self._is_modal_open:
            return

        state = "disabled" if is_active else "normal"
        for btn in self.main_buttons.values():
            btn.configure(state=state)
        for btn in self.sidebar_buttons.values():
            btn.configure(state=state)

        self.left_sidebar.configure(state=state)
        self.status_panel.set_active(is_active, mode=mode, text=text, final_status=final_status)

    def dim_ui_for_modal(self):
        self._is_modal_open = True
        for btn in self.main_buttons.values():
            btn.configure(state="disabled")
        for btn in self.sidebar_buttons.values():
            btn.configure(state="disabled")
        self.left_sidebar.configure(state="disabled")

    def restore_ui_from_modal(self):
        self._is_modal_open = False
        if not self.controller.is_processing:
            for btn in self.main_buttons.values():
                btn.configure(state="normal")
            for btn in self.sidebar_buttons.values():
                btn.configure(state="normal")
            self.left_sidebar.configure(state="normal")
        else:
            pass

    def show_message(self, title_key: str, message_key: str, *args):
        MessageDialog(self, self._tr(title_key), self._tr(message_key, *args))

    def show_app_info(self):
        webbrowser.open("https://renzofernando.github.io/LectorcitoPro/")