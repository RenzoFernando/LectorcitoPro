from __future__ import annotations

import datetime
import getpass
import os
import random
import tkinter as tk
import tkinter.font as tkfont

import customtkinter as ctk

from app_logging import log_error, log_info, log_warning
from app_meta import APP_DISPLAY_NAME, APP_WEBSITE_URL, get_current_year
from i18n.translations import TRANSLATIONS, translate_default
from platform_services import get_platform_service
from view.dialogs import (
    MessageDialog,
    _get_widget_window_rect,
)
from view.profiles_dialog import ProfilesDialog
from view.settings_dialog import SettingsDialog
from view.sidebars import BlendedRoundedFrame, PillTextButton, RightSidebar
from view.status_panel import StatusPanel
from view.tags_dialog import TagsConfigDialog
from view.tooltip import CustomTooltip
from view.ui_assets import load_action_icons, load_logo, load_sidebar_icons, safe_set_window_icon
from view.ui_constants import *
from view.ui_constants import (
    AUTHOR,
    BTN_H_MAIN,
    BTN_W_MAIN,
    COLORS,
    FONT_FAMILY_PRIMARY,
    MAIN_WINDOW_FADE_OUT_INTERVAL_MS,
    MAIN_WINDOW_FADE_OUT_STEP,
    REPO_URL,
    VERSION,
    get_theme_tokens,
)
from view.ui_scaling import (
    configure_application_scaling,
    get_application_workarea,
    scale_tk_value,
)

# =============================================================================

# INTERFAZ PRINCIPAL (MAIN WINDOW)

# =============================================================================


class LectorcitoApp(ctk.CTk):
    def __init__(self, cfg: dict, controller):
        super().__init__()

        self.withdraw()
        try:
            self.attributes("-alpha", 0.0)
        except Exception:
            pass
        configure_application_scaling(self, prefer_pointer=True)

        self.TRANSLATIONS = TRANSLATIONS
        self.config = cfg
        self.controller = controller
        self.lang = self.config.get("language", "es")
        self.current_theme = self.config.get("theme", "Light")
        self.config["language"] = self.lang
        self.config["theme"] = self.current_theme

        self.REPO_URL = REPO_URL
        self.tooltips: dict[str, CustomTooltip] = {}
        self._is_modal_open = False
        self._modal_depth = 0
        self._native_modal_depth = 0
        self._modal_control_states = {}
        self._modal_overlay = None
        self._modal_overlay_sync_after_id = None
        self._modal_action_depth = 0
        self._modal_fail_safe_after_id = None
        self._dialog_cache = {}
        self._is_theme_switching = False
        self._is_profile_switching = False
        self._startup_visible = False
        self._header_greeting_title = ""
        self._header_greeting_subtitle = ""

        self.title(APP_DISPLAY_NAME)
        self._app_w = MAIN_WINDOW_WIDTH
        self._app_h = MAIN_WINDOW_HEIGHT
        self.geometry(f"{self._app_w}x{self._app_h}")
        self.minsize(self._app_w, self._app_h)
        self.maxsize(self._app_w, self._app_h)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)
        self.bind("<Configure>", self._schedule_modal_overlay_sync, add="+")

        safe_set_window_icon(self)

        self.icons = load_sidebar_icons()
        self.action_icons = load_action_icons()
        self.logo_image = load_logo()

        self._build_ui()
        self.update_ui_texts()
        self.apply_theme()
        self.toggle_ui_for_processing(is_active=False)

        # El root permanece oculto hasta que el controlador inicia el mainloop.
        # Esto evita mostrar una ventana a medio construir y elimina callbacks
        # de layout durante el arranque.
        self._apply_raw_tk_scaling()
        log_info("Interfaz principal construida.", operation="startup_ui")

    def _schedule_header_refresh(self, event=None):
        self._refresh_header_canvas()

    def _get_current_user_name(self) -> str:
        candidates = []
        try:
            candidates.append(getpass.getuser())
        except Exception:
            pass
        try:
            candidates.append(os.getlogin())
        except OSError:
            pass
        for key in ("USERNAME", "USER", "LOGNAME"):
            candidates.append(os.environ.get(key, ""))

        for candidate in candidates:
            clean = str(candidate or "").strip()
            if not clean:
                continue
            clean = clean.rsplit("\\", 1)[-1].split("@", 1)[0].strip()
            if clean:
                return clean.lower().capitalize()
        return self._tr("fallback_user")

    def _refresh_header_canvas(self):
        if not hasattr(self, "lbl_greeting_title"):
            return
        theme = get_theme_tokens(self.current_theme)
        title_text = self._header_greeting_title or ""
        subtitle_text = self._header_greeting_subtitle or ""
        try:
            actual_width = int(self.header_message_frame.winfo_width())
        except Exception:
            actual_width = 0
        available_width = max(
            180,
            actual_width - 4 if actual_width > 40 else MAIN_WINDOW_HEADER_TEXT_WIDTH,
        )

        def fit_font_size(text: str, preferred: int, minimum: int, weight: str) -> int:
            for size in range(preferred, minimum - 1, -1):
                try:
                    pixel_size = max(1, int(scale_tk_value(self, size)))
                    font = tkfont.Font(
                        root=self,
                        family=FONT_FAMILY_PRIMARY,
                        size=-pixel_size,
                        weight=weight,
                    )
                    if font.measure(text) <= available_width:
                        return size
                except Exception:
                    break
            return minimum

        title_size = fit_font_size(
            title_text,
            MAIN_WINDOW_GREETING_FONT_SIZE,
            MAIN_WINDOW_GREETING_MIN_FONT_SIZE,
            "bold",
        )
        subtitle_size = fit_font_size(
            subtitle_text,
            MAIN_WINDOW_SUBTITLE_FONT_SIZE,
            MAIN_WINDOW_SUBTITLE_MIN_FONT_SIZE,
            "normal",
        )
        try:
            self.lbl_greeting_title.configure(
                text=title_text,
                text_color=theme["text_primary"],
                font=(FONT_FAMILY_PRIMARY, title_size, "bold"),
                wraplength=0,
            )
            self.lbl_greeting_subtitle.configure(
                text=subtitle_text,
                text_color=theme["text_secondary"],
                font=(FONT_FAMILY_PRIMARY, subtitle_size, "normal"),
                wraplength=0,
            )
        except Exception:
            pass

    def _apply_raw_tk_scaling(self):
        footer_height = max(1, scale_tk_value(self, MAIN_WINDOW_FOOTER_HEIGHT))
        footer_clearance = footer_height + scale_tk_value(self, 8)
        center_pady = scale_tk_value(self, MAIN_WINDOW_CENTER_PADY)
        header_clearance = scale_tk_value(
            self, MAIN_WINDOW_HEADER_MIN_HEIGHT + MAIN_WINDOW_HEADER_CONTENT_GAP
        )

        try:
            self.center_container.grid_configure(
                padx=scale_tk_value(self, MAIN_WINDOW_SIDE_PADX),
                pady=(header_clearance, center_pady[1] + footer_clearance),
            )
            self.header_frame.configure(height=scale_tk_value(self, MAIN_WINDOW_HEADER_MIN_HEIGHT))
            self.footer_frame.configure(height=footer_height)
        except Exception:
            pass

    def get_real_window_rect(self):

        return _get_widget_window_rect(self)

    def _center_main_window_on_workarea(self, max_attempts: int = 6):
        try:
            left, top, right, bottom = get_application_workarea(self)
            target_cx = int((left + right) / 2)
            target_cy = int((top + bottom) / 2)
        except Exception:
            return

        for _ in range(max(1, int(max_attempts))):
            try:
                self.update_idletasks()
                rect = _get_widget_window_rect(self)
                if rect == (0, 0, 0, 0):
                    return
                actual_cx = int((rect[0] + rect[2]) / 2)
                actual_cy = int((rect[1] + rect[3]) / 2)
                dx = target_cx - actual_cx
                dy = target_cy - actual_cy
                if abs(dx) <= 1 and abs(dy) <= 1:
                    return

                new_x = int(self.winfo_x()) + dx
                new_y = int(self.winfo_y()) + dy
                self.geometry(f"{new_x:+d}{new_y:+d}")
            except Exception:
                return

    def show_main_window(self):
        """Muestra el root una sola vez, centrado y completamente dibujado."""
        if getattr(self, "_startup_visible", False):
            return

        try:
            self.attributes("-alpha", 0.0)
        except Exception:
            pass

        try:
            left, top, right, bottom = get_application_workarea(self)
            initial_x = int(left + ((right - left) - self._app_w) / 2)
            initial_y = int(top + ((bottom - top) - self._app_h) / 2)
            self.geometry(
                f"{self._app_w}x{self._app_h}{initial_x:+d}{initial_y:+d}"
            )
            self.update_idletasks()

            # La ventana se mapea aun transparente para medir el marco nativo real.
            # Después se corrige su centro contra el area util del monitor elegido.
            self.deiconify()
            self.update_idletasks()
            self._center_main_window_on_workarea()
            self.update_idletasks()
        except Exception as error:
            log_warning(str(error), operation="show_main_window")

        self._startup_visible = True
        try:
            self.lift()
            self.after(MAIN_WINDOW_FADE_OUT_INTERVAL_MS, self._fade_in_on_startup)
        except Exception as error:
            log_warning(str(error), operation="show_main_window")
            try:
                self.attributes("-alpha", 1.0)
            except Exception:
                pass
            log_info("Ventana principal visible.", operation="startup_ui")

    def _fade_in_on_startup(self):
        try:
            alpha = float(self.attributes("-alpha"))
            next_alpha = min(1.0, alpha + MAIN_WINDOW_FADE_OUT_STEP)
            self.attributes("-alpha", next_alpha)
        except Exception as error:
            log_warning(str(error), operation="startup_fade_in")
            next_alpha = 1.0

        if next_alpha < 1.0:
            self.after(MAIN_WINDOW_FADE_OUT_INTERVAL_MS, self._fade_in_on_startup)
            return

        log_info("Ventana principal visible.", operation="startup_ui")

    def _close_with_fade_out(self):

        try:
            for tp in self.tooltips.values():
                tp.cleanup()

        except Exception:
            pass

        try:
            self.status_panel.cleanup()

        except Exception:
            pass

        try:
            for dialog in self._dialog_cache.values():
                try:
                    if dialog.winfo_exists():
                        dialog.destroy()

                except Exception:
                    pass

        except Exception:
            pass

        alpha = self.attributes("-alpha")

        if alpha > 0:
            self.attributes("-alpha", max(alpha - MAIN_WINDOW_FADE_OUT_STEP, 0.0))

            self.after(MAIN_WINDOW_FADE_OUT_INTERVAL_MS, self._close_with_fade_out)

        else:
            self.destroy()

    def _tr(self, key: str, *args):

        entry = self.TRANSLATIONS.get(self.lang, self.TRANSLATIONS["es"]).get(key, f"<{key}>")

        if isinstance(entry, list):
            return random.choice(entry).format(*args)

        return entry.format(*args)

    def _refresh_local_surface_colors(self):
        theme = get_theme_tokens(self.current_theme)
        try:
            self.configure(fg_color=theme["bg_base"])
            self.center_container.configure(fg_color=theme["bg_base"])
        except Exception:
            pass

    def get_backdrop_patch(self, widget, width=None, height=None):
        # API conservada para componentes persistentes antiguos. El fondo actual es solido.
        return None, None

    # =========================================================================

    # CONSTRUCCION DE UI

    # =========================================================================

    def _build_ui(self):
        theme = get_theme_tokens(self.current_theme)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        footer_height = max(1, scale_tk_value(self, MAIN_WINDOW_FOOTER_HEIGHT))
        center_pady = scale_tk_value(self, MAIN_WINDOW_CENTER_PADY)
        header_clearance = scale_tk_value(
            self, MAIN_WINDOW_HEADER_MIN_HEIGHT + MAIN_WINDOW_HEADER_CONTENT_GAP
        )

        self._create_header(self)

        self.center_container = ctk.CTkFrame(
            self,
            fg_color=theme["bg_base"],
            corner_radius=0,
        )
        self.center_container.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=scale_tk_value(self, MAIN_WINDOW_SIDE_PADX),
            pady=(header_clearance, center_pady[1] + footer_height + scale_tk_value(self, 8)),
        )
        self.center_container.grid_columnconfigure(0, weight=1)
        self.center_container.grid_rowconfigure(2, weight=1)

        self._create_main_buttons(self.center_container)
        self._create_status_area(self.center_container)
        self._create_footer()

    def _create_header(self, parent):
        theme = get_theme_tokens(self.current_theme)

        # El encabezado replica la superficie y la linea del pie de pagina.
        self.header_frame = tk.Frame(
            parent,
            height=scale_tk_value(self, MAIN_WINDOW_HEADER_MIN_HEIGHT),
            bg=theme["bg_footer"],
            bd=0,
            highlightthickness=0,
        )
        self.header_frame.place(relx=0.0, rely=0.0, anchor="nw", relwidth=1.0)
        self.header_frame.grid_propagate(False)
        self.header_frame.pack_propagate(False)
        self.header_frame.grid_columnconfigure(0, weight=1, minsize=0)
        self.header_frame.grid_columnconfigure(1, weight=0)
        self.header_frame.grid_rowconfigure(0, weight=1, uniform="header_rows")
        self.header_frame.grid_rowconfigure(1, weight=1, uniform="header_rows")

        # El bloque de texto ocupa las dos filas. Un espaciador flexible arriba
        # acerca el saludo al mensaje sin mover la fila inferior de iconos.
        self.header_text_stack = ctk.CTkFrame(
            self.header_frame,
            fg_color="transparent",
            bg_color=theme["bg_footer"],
        )
        self.header_text_stack.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="nsew",
            padx=(MAIN_WINDOW_HEADER_TEXT_SIDE_PAD, 12),
            pady=(MAIN_WINDOW_HEADER_TOP_INSET, MAIN_WINDOW_HEADER_BOTTOM_INSET),
        )
        self.header_text_stack.grid_columnconfigure(0, weight=1)
        self.header_text_stack.grid_rowconfigure(0, weight=1)

        self.header_title_frame = ctk.CTkFrame(
            self.header_text_stack,
            fg_color="transparent",
            bg_color=theme["bg_footer"],
        )
        self.header_title_frame.grid(row=1, column=0, sticky="ew")
        self.header_title_frame.grid_columnconfigure(0, weight=1)

        self.lbl_greeting_title = ctk.CTkLabel(
            self.header_title_frame,
            text="",
            font=(FONT_FAMILY_PRIMARY, MAIN_WINDOW_GREETING_FONT_SIZE, "bold"),
            anchor="w",
            justify="left",
            wraplength=MAIN_WINDOW_HEADER_TEXT_WIDTH,
            fg_color="transparent",
            bg_color=theme["bg_footer"],
            text_color=theme["text_primary"],
        )
        self.lbl_greeting_title.grid(row=0, column=0, sticky="ew")

        self.header_message_frame = ctk.CTkFrame(
            self.header_text_stack,
            fg_color="transparent",
            bg_color=theme["bg_footer"],
        )
        self.header_message_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(MAIN_WINDOW_HEADER_TEXT_GAP, 0),
        )
        self.header_message_frame.grid_columnconfigure(0, weight=1)

        self.lbl_greeting_subtitle = ctk.CTkLabel(
            self.header_message_frame,
            text="",
            font=(FONT_FAMILY_PRIMARY, MAIN_WINDOW_SUBTITLE_FONT_SIZE, "normal"),
            anchor="w",
            justify="left",
            wraplength=MAIN_WINDOW_HEADER_TEXT_WIDTH,
            fg_color="transparent",
            bg_color=theme["bg_footer"],
            text_color=theme["text_secondary"],
        )
        self.lbl_greeting_subtitle.grid(row=0, column=0, sticky="ew")
        self.header_message_frame.bind("<Configure>", self._schedule_header_refresh, add="+")

        self.right_sidebar = RightSidebar(
            self.header_frame,
            icons=self.icons,
            current_theme=self.current_theme,
            orientation="horizontal",
            auto_pack=False,
        )
        self.right_sidebar.grid(
            row=1,
            column=1,
            sticky="se",
            padx=(0, MAIN_WINDOW_HEADER_TEXT_SIDE_PAD),
            pady=(MAIN_WINDOW_HEADER_TEXT_GAP, MAIN_WINDOW_HEADER_BOTTOM_INSET),
        )
        self.right_sidebar.configure(bg_color=theme["bg_footer"], fg_color="transparent")
        self.sidebar_buttons = self.right_sidebar.buttons

        self.header_separator = tk.Frame(
            self.header_frame,
            height=scale_tk_value(self, MAIN_WINDOW_HEADER_LINE_HEIGHT),
            bg=theme["separator_line"],
            bd=0,
            highlightthickness=0,
        )
        self.header_separator.place(relx=0.0, rely=1.0, anchor="sw", relwidth=1.0)
        self.header_frame.lift()

    def _create_main_buttons(self, parent):
        theme = get_theme_tokens(self.current_theme)
        self.main_content_frame = ctk.CTkFrame(parent, fg_color=theme["bg_base"], corner_radius=0)
        self.main_content_frame.grid(row=2, column=0, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=3, uniform="main")
        self.main_content_frame.grid_columnconfigure(1, weight=2, uniform="main")
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        self.left_actions_frame = ctk.CTkFrame(
            self.main_content_frame,
            fg_color=theme["bg_base"],
            corner_radius=0,
        )
        self.left_actions_frame.grid(
            row=0, column=0, sticky="nsew", padx=(0, scale_tk_value(self, 8))
        )
        self.left_actions_frame.grid_columnconfigure(0, weight=1)
        self.left_actions_frame.grid_rowconfigure(0, weight=2)
        self.left_actions_frame.grid_rowconfigure(1, weight=3)

        self.primary_actions_card = BlendedRoundedFrame(
            self.left_actions_frame,
            outside_bg=theme["bg_base"],
            fill_color=theme["bg_panel"],
            border_color=theme["card_border"],
            border_width=MAIN_WINDOW_CARD_BORDER_WIDTH,
            corner_radius=12,
            content_inset=10,
        )
        self.primary_actions_card.grid(row=0, column=0, sticky="nsew")

        self.secondary_actions_card = BlendedRoundedFrame(
            self.left_actions_frame,
            outside_bg=theme["bg_base"],
            fill_color=theme["bg_panel"],
            border_color=theme["card_border"],
            border_width=MAIN_WINDOW_CARD_BORDER_WIDTH,
            corner_radius=12,
            content_inset=10,
        )
        self.secondary_actions_card.grid(
            row=1, column=0, sticky="nsew", pady=(scale_tk_value(self, 12), 0)
        )

        self.primary_actions_stack = ctk.CTkFrame(
            self.primary_actions_card.content_frame, fg_color="transparent"
        )
        self.primary_actions_stack.pack(fill="x", expand=True)
        self.secondary_actions_stack = ctk.CTkFrame(
            self.secondary_actions_card.content_frame, fg_color="transparent"
        )
        self.secondary_actions_stack.pack(fill="x", expand=True)

        self.main_menu_frame = self.primary_actions_card
        self.main_buttons_frame = self.primary_actions_stack
        self._main_button_variants = {
            "choose": "primary",
            "openlect": "primary",
            "create_tree": "secondary",
            "openlast": "secondary",
            "selpath": "secondary",
            "delete": "destructive",
        }

        def create_action(parent_frame, key: str):
            variant = self._main_button_variants[key]
            palette = get_action_button_tokens(self.current_theme, variant)
            action_image = self.action_icons.get(key)

            button = PillTextButton(
                parent_frame,
                image=action_image,
                width=BTN_W_MAIN,
                height=BTN_H_MAIN,
                outside_bg=theme["bg_panel"],
                fg_color=palette["bg"],
                hover_color=palette["hover"],
                border_color=palette["border"],
                border_width=MAIN_WINDOW_ACTION_BORDER_WIDTH,
                text_color=palette["text"],
                font=FONT_ACTION,
                corner_radius=10,
                icon_placeholder=action_image is None,
                icon_color=palette["icon"],
                chevron=True,
                chevron_color=palette["chevron"],
                content_pad=14,
                text_anchor="w",
            )
            button.pack(fill="x", pady=scale_tk_value(self, 3))
            return button

        self.main_buttons = {
            "choose": create_action(self.primary_actions_stack, "choose"),
            "openlect": create_action(self.primary_actions_stack, "openlect"),
            "create_tree": create_action(self.secondary_actions_stack, "create_tree"),
            "openlast": create_action(self.secondary_actions_stack, "openlast"),
            "selpath": create_action(self.secondary_actions_stack, "selpath"),
        }

    def _create_status_area(self, parent):
        theme = get_theme_tokens(self.current_theme)
        self.progress_frame = ctk.CTkFrame(
            self.main_content_frame,
            fg_color=theme["bg_base"],
            corner_radius=0,
        )
        self.progress_frame.grid(row=0, column=1, sticky="nsew", padx=(scale_tk_value(self, 8), 0))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_rowconfigure(0, weight=1)
        self.progress_frame.grid_rowconfigure(1, weight=0)

        self.status_panel = StatusPanel(
            self.progress_frame,
            min_visible_seconds=MAIN_WINDOW_STATUS_MIN_VISIBLE_SECONDS,
        )
        self.status_panel.grid(row=0, column=0, sticky="nsew")
        self.btn_cancel = self.status_panel.btn_cancel

        palette = get_action_button_tokens(self.current_theme, "destructive")
        action_image = self.action_icons.get("delete")
        delete_button = PillTextButton(
            self.progress_frame,
            image=action_image,
            width=MAIN_WINDOW_RIGHT_ACTION_WIDTH,
            height=BTN_H_MAIN,
            outside_bg=theme["bg_base"],
            fg_color=palette["bg"],
            hover_color=palette["hover"],
            border_color=palette["border"],
            border_width=MAIN_WINDOW_ACTION_BORDER_WIDTH,
            text_color=palette["text"],
            font=FONT_ACTION,
            corner_radius=10,
            icon_placeholder=action_image is None,
            icon_color=palette["icon"],
            chevron=True,
            chevron_color=palette["chevron"],
            content_pad=14,
            text_anchor="w",
        )
        delete_button.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(scale_tk_value(self, 10), 0),
        )
        self.main_buttons["delete"] = delete_button

    def _create_footer(self):
        theme = get_theme_tokens(self.current_theme)
        self.footer_frame = tk.Frame(
            self,
            height=scale_tk_value(self, MAIN_WINDOW_FOOTER_HEIGHT),
            bg=theme["bg_footer"],
            bd=0,
            highlightthickness=0,
        )
        self.footer_frame.pack_propagate(False)
        self.footer_frame.place(relx=0.0, rely=1.0, anchor="sw", relwidth=1.0)
        self.footer_frame.lift()

        self.footer_line = tk.Frame(
            self.footer_frame,
            height=MAIN_WINDOW_FOOTER_LINE_HEIGHT,
            bg=theme["separator_line"],
            bd=0,
            highlightthickness=0,
        )
        self.footer_line.pack(side="top", fill="x")

        self.lbl_copyright = ctk.CTkLabel(
            self.footer_frame,
            text="",
            font=FONT_AUXILIARY,
            fg_color="transparent",
            bg_color=theme["bg_footer"],
            anchor="w",
        )
        self.lbl_copyright.place(
            x=scale_tk_value(self, MAIN_WINDOW_SIDE_PADX), rely=0.55, anchor="w"
        )

        self.footer_brand = ctk.CTkFrame(
            self.footer_frame, fg_color="transparent", bg_color=theme["bg_footer"]
        )
        self.footer_brand.place(
            relx=1.0,
            x=-scale_tk_value(self, MAIN_WINDOW_SIDE_PADX),
            rely=0.55,
            anchor="e",
        )

        self.lbl_footer_logo = ctk.CTkLabel(
            self.footer_brand,
            text="" if self.logo_image is not None else APP_DISPLAY_NAME,
            image=self.logo_image,
            compound="left",
            font=FONT_AUXILIARY,
            fg_color="transparent",
            bg_color=theme["bg_footer"],
        )
        self.lbl_footer_logo.pack(side="left")

        self.lbl_footer_version = ctk.CTkLabel(
            self.footer_brand,
            text=f"v{VERSION}",
            font=FONT_AUXILIARY_EMPHASIS,
            fg_color="transparent",
            bg_color=theme["bg_footer"],
        )
        self.lbl_footer_version.pack(side="left", padx=(scale_tk_value(self, 6), 0))

    def update_ui_texts(self):
        user = self._get_current_user_name()

        hour = datetime.datetime.now().hour
        greet_key = "greet_m" if 5 <= hour < 12 else "greet_a" if 12 <= hour < 19 else "greet_n"
        self._header_greeting_title = self._tr("greeting_user", user)
        self._header_greeting_subtitle = f"{self._tr(greet_key)} {self._tr('main_action_prompt')}"
        self._schedule_header_refresh()

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

        self.status_panel.set_translator(lambda key: self._tr(key))
        self.lbl_copyright.configure(
            text=self._tr("footer_copyright", get_current_year(), AUTHOR)
        )
        self.lbl_footer_version.configure(text=f"v{VERSION}")

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
            if key not in tooltip_map:
                continue
            text = self._tr(tooltip_map[key])
            if key in self.tooltips:
                self.tooltips[key].text = text
            else:
                self.tooltips[key] = CustomTooltip(btn, text=text)

        for dialog in self._dialog_cache.values():
            try:
                if dialog.winfo_exists() and hasattr(dialog, "refresh_texts"):
                    dialog.refresh_texts()
            except Exception:
                pass

        self._refresh_local_surface_colors()

    def apply_theme(self):
        ctk.set_appearance_mode(self.current_theme)
        theme = get_theme_tokens(self.current_theme)
        self.configure(fg_color=theme["bg_base"])

        self.right_sidebar.apply_theme(self.current_theme)
        self.status_panel.apply_theme(self.current_theme)

        for frame in (
            self.center_container,
            self.main_content_frame,
            self.left_actions_frame,
            self.progress_frame,
        ):
            try:
                frame.configure(fg_color=theme["bg_base"])
            except Exception:
                pass

        self.header_frame.configure(bg=theme["bg_footer"])
        self.header_text_stack.configure(bg_color=theme["bg_footer"], fg_color="transparent")
        self.header_title_frame.configure(bg_color=theme["bg_footer"], fg_color="transparent")
        self.header_message_frame.configure(bg_color=theme["bg_footer"], fg_color="transparent")
        self.right_sidebar.configure(bg_color=theme["bg_footer"], fg_color="transparent")
        self.lbl_greeting_title.configure(
            bg_color=theme["bg_footer"],
            text_color=theme["text_primary"],
        )
        self.lbl_greeting_subtitle.configure(
            bg_color=theme["bg_footer"],
            text_color=theme["text_secondary"],
        )
        self.header_separator.configure(bg=theme["separator_line"])

        for card in (self.primary_actions_card, self.secondary_actions_card):
            card.configure(
                outside_bg=theme["bg_base"],
                fill_color=theme["bg_panel"],
                border_color=theme["card_border"],
                border_width=MAIN_WINDOW_CARD_BORDER_WIDTH,
            )

        for key, btn in self.main_buttons.items():
            variant = self._main_button_variants.get(key, "secondary")
            palette = get_action_button_tokens(self.current_theme, variant)
            outside = theme["bg_base"] if key == "delete" else theme["bg_panel"]
            action_image = self.action_icons.get(key)
            btn.configure(
                image=action_image,
                icon_placeholder=action_image is None,
                outside_bg=outside,
                fg_color=palette["bg"],
                hover_color=palette["hover"],
                border_color=palette["border"],
                text_color=palette["text"],
                icon_color=palette["icon"],
                chevron_color=palette["chevron"],
            )

        self.footer_frame.configure(bg=theme["bg_footer"])
        self.footer_line.configure(bg=theme["separator_line"])
        self.footer_brand.configure(bg_color=theme["bg_footer"])
        self.lbl_copyright.configure(
            bg_color=theme["bg_footer"],
            fg_color="transparent",
            text_color=theme["text_secondary"],
        )
        self.lbl_footer_logo.configure(
            bg_color=theme["bg_footer"], text_color=theme["text_primary"]
        )
        self.lbl_footer_version.configure(
            bg_color=theme["bg_footer"], text_color=theme["text_secondary"]
        )

        self._schedule_header_refresh()

    def switch_theme_animated(self, new_theme: str):
        """Oculta suavemente la ventana, aplica el tema y vuelve a mostrarla."""
        if new_theme == self.current_theme or self._is_theme_switching:
            return
        self._is_theme_switching = True
        self._theme_switch_target = new_theme
        CustomTooltip.hide_global()
        self._fade_out_for_theme_switch()

    def _fade_out_for_theme_switch(self):
        try:
            alpha = float(self.attributes("-alpha"))
            next_alpha = max(0.0, alpha - MAIN_WINDOW_FADE_OUT_STEP)
            self.attributes("-alpha", next_alpha)
        except Exception:
            self._apply_theme_switch_midpoint()
            return

        if next_alpha > 0.0:
            self.after(MAIN_WINDOW_FADE_OUT_INTERVAL_MS, self._fade_out_for_theme_switch)
            return
        self.after(MAIN_WINDOW_FADE_OUT_INTERVAL_MS, self._apply_theme_switch_midpoint)

    def _apply_theme_switch_midpoint(self):
        try:
            target = getattr(self, "_theme_switch_target", self.current_theme)
            self.current_theme = target
            self.apply_theme()
            self.update_idletasks()
        except Exception as error:
            log_warning(str(error), operation="theme_switch")
        finally:
            self.after(THEME_SWITCH_SETTLE_MS, self._fade_in_after_theme_switch)

    def _fade_in_after_theme_switch(self):
        try:
            alpha = float(self.attributes("-alpha"))
            next_alpha = min(1.0, alpha + MAIN_WINDOW_FADE_OUT_STEP)
            self.attributes("-alpha", next_alpha)
        except Exception:
            next_alpha = 1.0

        if next_alpha < 1.0:
            self.after(MAIN_WINDOW_FADE_OUT_INTERVAL_MS, self._fade_in_after_theme_switch)
            return

        self._theme_switch_target = None
        self._is_theme_switching = False

    def switch_profile_animated(self, apply_callback, complete_callback=None):
        """Cambia de perfil en sitio para evitar parpadeos de la ventana principal."""
        if self._is_theme_switching or self._is_profile_switching:
            return
        self._is_profile_switching = True
        CustomTooltip.hide_global()
        try:
            if callable(apply_callback):
                apply_callback()
        finally:
            self._is_profile_switching = False
        if callable(complete_callback):
            self.after_idle(complete_callback)

    def prepare_soft_refresh(self):
        """Prepara una actualizacion de datos sin modificar alpha ni geometria."""
        CustomTooltip.hide_global()

    def complete_soft_refresh(self):
        return None

    def _create_view_dialog(self):

        return TagsConfigDialog(
            parent=self,
            title=self._tr("dlg_ver_title"),
            folders_prompt=self._tr("dlg_ver_folder_prompt"),
            initial_folders=self.controller.config.get("etiquetas_carpetas_importantes", []),
            files_prompt=self._tr("dlg_ver_file_prompt"),
            initial_files=self.controller.config.get("etiquetas_extensiones_incluidas", []),
            allow_autodetect=True,
            excluded_folders=self.controller.config.get("etiquetas_carpetas_excluidas", []),
            excluded_files=self.controller.config.get("etiquetas_archivos_excluidos", []),
            media_extensions=self.controller.config.get("media_extensions", []),
            persistent=True,
            defer_show=True,
        )

    def _create_no_view_dialog(self):

        return TagsConfigDialog(
            parent=self,
            title=self._tr("dlg_nover_title"),
            folders_prompt=self._tr("dlg_nover_folder_prompt"),
            initial_folders=self.controller.config.get("etiquetas_carpetas_excluidas", []),
            files_prompt=self._tr("dlg_nover_file_prompt"),
            initial_files=self.controller.config.get("etiquetas_archivos_excluidos", []),
            extra_checkbox_text=self._tr("chk_use_gitignore"),
            extra_checkbox_value=self.controller.config.get("use_gitignore_exclusions", False),
            persistent=True,
            defer_show=True,
        )

    def _create_media_dialog(self):

        tags_stored = self.controller.config.get("etiquetas_multimedia_config", [])

        if not tags_stored:
            raw_exts = self.controller.config.get("media_extensions", [])

            current_files = [{"nombre": x, "estado": "activo"} for x in raw_exts]

        else:
            current_files = tags_stored

        view_exts = {
            t["nombre"] for t in self.controller.config.get("etiquetas_extensiones_incluidas", [])
        }

        no_view_items = {
            t["nombre"] for t in self.controller.config.get("etiquetas_archivos_excluidos", [])
        }

        return TagsConfigDialog(
            parent=self,
            title=self._tr("dlg_etiqueta_title"),
            folders_prompt=None,
            initial_folders=None,
            files_prompt=self._tr("dlg_etiqueta_file_prompt"),
            initial_files=current_files,
            forbidden_items=view_exts.union(no_view_items),
            persistent=True,
            defer_show=True,
        )

    def _create_profiles_dialog(self):

        profiles = self.controller.config.get("_profiles_meta", {})

        active_id = self.controller.config.get("_active_profile_id", "default")

        if not profiles:
            profiles = {"default": self.controller.config.copy()}

        return ProfilesDialog(
            parent=self,
            profiles_meta=profiles,
            active_id=active_id,
            persistent=True,
            defer_show=True,
        )

    def _create_settings_dialog(self):

        return SettingsDialog(
            parent=self,
            current_extension=self.controller.config.get("report_extension", ".md"),
            current_exe_path=self.controller.config.get("custom_exe_path", ""),
            persistent=True,
            defer_show=True,
        )

    def _get_or_create_dialog(self, key, factory):

        dialog = self._dialog_cache.get(key)

        if dialog is None:
            dialog = factory()

            self._dialog_cache[key] = dialog

        else:
            try:
                if not dialog.winfo_exists():
                    dialog = factory()

                    self._dialog_cache[key] = dialog

            except Exception:
                dialog = factory()

                self._dialog_cache[key] = dialog

        return dialog

    def get_view_dialog(self):

        return self._get_or_create_dialog("view", self._create_view_dialog)

    def get_no_view_dialog(self):

        return self._get_or_create_dialog("no_view", self._create_no_view_dialog)

    def get_media_dialog(self):

        return self._get_or_create_dialog("media", self._create_media_dialog)

    def get_profiles_dialog(self):

        return self._get_or_create_dialog("profiles", self._create_profiles_dialog)

    def get_settings_dialog(self):

        return self._get_or_create_dialog("settings", self._create_settings_dialog)

    # =========================================================================

    # ESTADO Y CONTROL

    # =========================================================================

    def _cancel_modal_fail_safe(self):

        if self._modal_fail_safe_after_id:
            try:
                self.after_cancel(self._modal_fail_safe_after_id)

            except Exception:
                pass

        self._modal_fail_safe_after_id = None

    def _schedule_modal_fail_safe(self):

        self._cancel_modal_fail_safe()

        try:
            self._modal_fail_safe_after_id = self.after(
                MAIN_WINDOW_MODAL_FAIL_SAFE_DELAY_MS, self._modal_fail_safe_check
            )

        except Exception:
            self._modal_fail_safe_after_id = None

    def _iter_modal_controls(self):
        controls = []
        controls.extend(self.main_buttons.values())
        controls.extend(self.sidebar_buttons.values())
        return controls

    def _schedule_modal_overlay_sync(self, event=None):
        if self._modal_overlay is None:
            return
        if self._modal_overlay_sync_after_id is not None:
            return
        try:
            self._modal_overlay_sync_after_id = self.after_idle(
                self._sync_modal_overlay_geometry
            )
        except Exception:
            self._modal_overlay_sync_after_id = None

    def _sync_modal_overlay_geometry(self):
        self._modal_overlay_sync_after_id = None
        overlay = self._modal_overlay
        if overlay is None:
            return
        try:
            if not overlay.winfo_exists() or not self.winfo_ismapped():
                return
            self.update_idletasks()
            x = int(self.winfo_rootx())
            y = int(self.winfo_rooty())
            width = max(1, int(self.winfo_width()))
            height = max(1, int(self.winfo_height()))
            overlay.geometry(f"{width}x{height}{x:+d}{y:+d}")
        except Exception:
            pass

    def _create_modal_overlay(self):
        self._destroy_modal_overlay()
        theme = get_theme_tokens(self.current_theme)
        overlay = tk.Toplevel(self)
        self._modal_overlay = overlay
        try:
            overlay.withdraw()
            overlay.overrideredirect(True)
            overlay.transient(self)
            overlay.configure(
                bg=theme["modal_overlay"],
                takefocus=0,
                bd=0,
                highlightthickness=0,
            )
            try:
                overlay.attributes("-toolwindow", True)
            except Exception:
                pass
            try:
                overlay.attributes("-alpha", MAIN_WINDOW_MODAL_OVERLAY_ALPHA)
            except Exception:
                pass
            overlay.bind("<Button>", lambda event: "break", add="+")
            overlay.bind("<Key>", lambda event: "break", add="+")
            overlay.protocol("WM_DELETE_WINDOW", lambda: None)
            self._sync_modal_overlay_geometry()
            overlay.deiconify()
            overlay.lift(self)
            overlay.update_idletasks()
        except Exception:
            try:
                overlay.destroy()
            except Exception:
                pass
            self._modal_overlay = None

    def _destroy_modal_overlay(self):
        if self._modal_overlay_sync_after_id is not None:
            try:
                self.after_cancel(self._modal_overlay_sync_after_id)
            except Exception:
                pass
            self._modal_overlay_sync_after_id = None

        overlay = self._modal_overlay
        self._modal_overlay = None
        if overlay is None:
            return
        try:
            if overlay.winfo_exists():
                overlay.destroy()
        except Exception:
            pass

    def _enter_modal_visual_state(self):
        self._modal_control_states = {}
        for button in self._iter_modal_controls():
            try:
                self._modal_control_states[button] = button.cget("state")
            except Exception:
                self._modal_control_states[button] = "normal"
            try:
                button.configure(state="disabled")
            except Exception:
                pass

        theme = get_theme_tokens(self.current_theme)
        for button in self.main_buttons.values():
            try:
                button.configure(
                    fg_color=theme["surface_alt"],
                    hover_color=theme["surface_alt"],
                    border_color=theme["border_subtle"],
                    text_color=theme["text_muted"],
                    icon_color=theme["text_muted"],
                    chevron_color=theme["text_muted"],
                )
            except Exception:
                pass

        if self._startup_visible:
            try:
                self.update_idletasks()
            except Exception:
                pass
            self._create_modal_overlay()

    def _leave_modal_visual_state(self):
        states = self._modal_control_states
        self._modal_control_states = {}
        try:
            self.apply_theme()
        except Exception:
            pass
        for button, state in states.items():
            try:
                if button.winfo_exists():
                    button.configure(state=state)
            except Exception:
                pass

        self._destroy_modal_overlay()

    def _has_live_modal_dialog(self) -> bool:

        if self._modal_action_depth > 0 or self._native_modal_depth > 0:
            return True

        try:
            for child in self.winfo_children():
                try:
                    if not getattr(child, "_is_base_dialog", False):
                        continue

                    if not child.winfo_exists():
                        continue

                    if str(child.state()) == "withdrawn":
                        continue

                    return True

                except Exception:
                    pass

        except Exception:
            pass

        return False

    def _modal_fail_safe_check(self):

        self._modal_fail_safe_after_id = None

        if not self._is_modal_open:
            return

        if self._has_live_modal_dialog():
            self._schedule_modal_fail_safe()

            return

        self.restore_ui_from_modal(force=True)

    def get_min_visible_completion_delay_ms(self) -> int:

        return self.status_panel.get_min_visible_completion_delay_ms()

    def set_progress(self, percentage, file_context=None, report_context=None):
        self.status_panel.set_progress(percentage, file_context, report_context)

    def set_processing_cancelling(self):
        self.status_panel.set_cancelling()

    def toggle_ui_for_processing(
        self, is_active: bool, mode: str = "determinate", text: str = None, final_status: str = None
    ):
        CustomTooltip.hide_global()
        if self._is_modal_open:
            return

        state = "disabled" if is_active else "normal"
        for btn in self.main_buttons.values():
            btn.configure(state=state)
        for btn in self.sidebar_buttons.values():
            btn.configure(state=state)

        self.status_panel.set_active(is_active, mode=mode, text=text, final_status=final_status)

    def dim_ui_for_modal(self):
        CustomTooltip.hide_global()
        if self._modal_depth == 0:
            self._enter_modal_visual_state()
        self._modal_depth += 1
        self._is_modal_open = True
        self._schedule_modal_fail_safe()

    def restore_ui_from_modal(self, force: bool = False):
        CustomTooltip.hide_global()
        if force:
            self._modal_depth = 0
        elif self._modal_depth > 0:
            self._modal_depth -= 1

        if self._modal_depth > 0:
            self._is_modal_open = True
            self._schedule_modal_fail_safe()
            return

        self._cancel_modal_fail_safe()
        self._modal_depth = 0
        self._is_modal_open = False
        self._leave_modal_visual_state()

    def run_modal_action(self, callback):
        """Bloquea visualmente la ventana antes de ejecutar una accion modal."""
        self._modal_action_depth += 1
        self.dim_ui_for_modal()
        try:
            # Fuerza el dibujo del estado bloqueado antes de crear o cargar
            # cualquier dialogo potencialmente costoso.
            self.update_idletasks()
            return callback()
        finally:
            self._modal_action_depth = max(0, self._modal_action_depth - 1)
            self.restore_ui_from_modal()

    def run_native_modal(self, callback):
        self._native_modal_depth += 1
        self.dim_ui_for_modal()
        try:
            self.update_idletasks()
            return callback()
        finally:
            self._native_modal_depth = max(0, self._native_modal_depth - 1)
            self.restore_ui_from_modal()

    def show_message(self, title_key: str, message_key: str, *args):

        CustomTooltip.hide_global()

        try:

            def _on_message_closed():

                try:
                    if getattr(self.status_panel, "_mode", "") == "done":
                        self.status_panel.back_to_idle()

                except Exception:
                    pass

            MessageDialog(
                self, self._tr(title_key), self._tr(message_key, *args), on_close=_on_message_closed
            )

        except Exception as error:
            log_error("Error mostrando dialogo de mensaje.", error, operation="show_message")

            self.restore_ui_from_modal()

    def show_app_info(self):

        if self.controller and hasattr(self.controller, "open_manual_link"):
            self.controller.open_manual_link()

        else:
            if not get_platform_service().open_url(APP_WEBSITE_URL):
                log_warning(
                    "No se pudo abrir el sitio oficial de Lectorcito Pro.",
                    operation="show_app_info",
                    file_path=APP_WEBSITE_URL,
                )