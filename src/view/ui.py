from __future__ import annotations

import customtkinter as ctk
import tkinter as tk
import datetime
import os
import random
import webbrowser

from PIL import Image, ImageDraw, ImageFilter, ImageTk

from app_meta import APP_DISPLAY_NAME, APP_WEBSITE_URL
from view.translations import TRANSLATIONS
from view.dialogs import MessageDialog, _get_widget_window_rect, _get_widget_workarea, _get_centered_position
from view.tooltip import CustomTooltip

from view.ui_constants import (
    VERSION, YEAR, AUTHOR, REPO_URL,
    COLORS, BTN_W_MAIN, BTN_H_MAIN,
    get_theme_tokens, get_button_tokens, hex_to_rgb, with_alpha,
    MAIN_WINDOW_SHOW_DELAY_MS, MAIN_WINDOW_CENTER_RETRY_DELAY_MS, MAIN_WINDOW_CENTER_MAX_ATTEMPTS,
    MAIN_WINDOW_INITIAL_ALPHA, MAIN_WINDOW_REVEAL_OFFSET_Y, MAIN_WINDOW_REVEAL_STEP_PX,
    MAIN_WINDOW_FADE_IN_STEP, MAIN_WINDOW_FADE_IN_INTERVAL_MS, MAIN_WINDOW_FADE_OUT_STEP, MAIN_WINDOW_FADE_OUT_INTERVAL_MS,
    MAIN_WINDOW_SOFT_REFRESH_ALPHA, MAIN_WINDOW_SWITCH_FADE_OUT_STEP, MAIN_WINDOW_SWITCH_FADE_OUT_INTERVAL_MS,
    MAIN_WINDOW_SWITCH_HOLD_MS, MAIN_WINDOW_SWITCH_FADE_IN_STEP, MAIN_WINDOW_SWITCH_FADE_IN_INTERVAL_MS
)
from view.ui_assets import load_sidebar_icons, load_logo, safe_set_window_icon
from view.sidebars import LeftSidebar, RightSidebar, PillTextButton
from view.status_panel import StatusPanel
from view.profiles_dialog import ProfilesDialog
from view.settings_dialog import SettingsDialog
from view.tags_dialog import TagsConfigDialog


# =============================================================================
# INTERFAZ PRINCIPAL (MAIN WINDOW)
# =============================================================================

class LectorcitoApp(ctk.CTk):

    def __init__(self, cfg: dict, controller):
        super().__init__()

        self.withdraw()
        self.attributes("-alpha", 0.0)

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
        self._modal_fail_safe_after_id = None
        self._dialog_cache = {}
        self._reveal_target_y = None
        self._is_theme_switching = False
        self._background_after_id = None
        self._background_photo = None

        self.title(APP_DISPLAY_NAME)
        self._app_w = 600
        self._app_h = 500
        self.geometry(f"{self._app_w}x{self._app_h}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)

        safe_set_window_icon(self)

        self.icons = load_sidebar_icons()
        self.logo_image = load_logo(target_width=150)

        self._build_ui()
        self.update_ui_texts()
        self.apply_theme()
        self.toggle_ui_for_processing(is_active=False)

        self.after(MAIN_WINDOW_SHOW_DELAY_MS, self._precise_center_and_show)
        self.after(MAIN_WINDOW_SHOW_DELAY_MS + 260, self._preload_persistent_dialogs)

    def get_real_window_rect(self):
        return _get_widget_window_rect(self)

    def _precise_center_and_show(self):
        try:
            self.update_idletasks()
            self._startup_target_rect = _get_widget_workarea(self)
            x, y = _get_centered_position(self._startup_target_rect, self._app_w, self._app_h)
            self.geometry(f"{self._app_w}x{self._app_h}+{x}+{y}")

            self.attributes("-alpha", 0.0)
            self.deiconify()
            self.after(MAIN_WINDOW_CENTER_RETRY_DELAY_MS, lambda: self._stabilize_initial_position(1))

        except Exception:
            self.deiconify()
            self.attributes("-alpha", 1.0)

    def _stabilize_initial_position(self, attempt=1):
        try:
            target_rect = getattr(self, "_startup_target_rect", _get_widget_workarea(self))
            target_cx = int((target_rect[0] + target_rect[2]) / 2)
            target_cy = int((target_rect[1] + target_rect[3]) / 2)
            actual_rect = self.get_real_window_rect()
            actual_cx = int((actual_rect[0] + actual_rect[2]) / 2)
            actual_cy = int((actual_rect[1] + actual_rect[3]) / 2)
            dx = target_cx - actual_cx
            dy = target_cy - actual_cy

            if (abs(dx) > 1 or abs(dy) > 1) and attempt < MAIN_WINDOW_CENTER_MAX_ATTEMPTS:
                self.geometry(f"{self._app_w}x{self._app_h}+{int(self.winfo_x()) + dx}+{int(self.winfo_y()) + dy}")
                self.after(MAIN_WINDOW_CENTER_RETRY_DELAY_MS, lambda: self._stabilize_initial_position(attempt + 1))
                return

            self._reveal_target_y = int(self.winfo_y())
            if MAIN_WINDOW_REVEAL_OFFSET_Y > 0:
                self.geometry(f"{self._app_w}x{self._app_h}+{int(self.winfo_x())}+{self._reveal_target_y + MAIN_WINDOW_REVEAL_OFFSET_Y}")
        except Exception:
            self._reveal_target_y = None
        self.attributes("-alpha", MAIN_WINDOW_INITIAL_ALPHA)
        self._fade_in()

    def _fade_in(self):
        try:
            alpha = float(self.attributes("-alpha"))
        except Exception:
            alpha = 1.0

        target_y = self._reveal_target_y
        if target_y is not None:
            try:
                current_y = int(self.winfo_y())
                if current_y > target_y:
                    step = min(MAIN_WINDOW_REVEAL_STEP_PX, current_y - target_y)
                    self.geometry(f"{self._app_w}x{self._app_h}+{int(self.winfo_x())}+{current_y - step}")
                else:
                    self._reveal_target_y = current_y
            except Exception:
                self._reveal_target_y = None

        if alpha < 1.0:
            self.attributes("-alpha", min(alpha + MAIN_WINDOW_FADE_IN_STEP, 1.0))
            self.after(MAIN_WINDOW_FADE_IN_INTERVAL_MS, self._fade_in)

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

    # =========================================================================
    # CONSTRUCCION DE UI
    # =========================================================================

    def _create_atmosphere_background(self):
        self._background_canvas = tk.Canvas(self, highlightthickness=0, bd=0, relief="flat")
        self._background_canvas.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.tk.call("lower", self._background_canvas._w)
        self.bind("<Configure>", self._schedule_background_refresh, add="+")

    def _schedule_background_refresh(self, event=None):
        if event is not None and event.widget is not self:
            return
        if self._background_after_id is not None:
            try:
                self.after_cancel(self._background_after_id)
            except Exception:
                pass
        try:
            self._background_after_id = self.after(16, self._refresh_background_canvas)
        except Exception:
            self._background_after_id = None

    def _refresh_background_canvas(self):
        self._background_after_id = None
        try:
            width = max(1, int(self.winfo_width()))
            height = max(1, int(self.winfo_height()))
        except Exception:
            return

        theme = get_theme_tokens(self.current_theme)
        self._background_photo = None
        self._background_canvas.configure(bg=theme["bg_base"])
        self._background_canvas.delete("all")
        self._background_canvas.create_rectangle(0, 0, width + 1, height + 1, outline="", fill=theme["bg_base"])
        self.tk.call("lower", self._background_canvas._w)

    def _build_ui(self):
        self._create_atmosphere_background()
        theme_keys = get_theme_tokens(self.current_theme)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.grid(row=0, column=0, sticky="ns", padx=15, pady=(0, 14))

        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=2, sticky="ns", padx=15, pady=(0, 15))

        self.center_container = ctk.CTkFrame(self, fg_color="transparent")
        self.center_container.grid(row=0, column=1, sticky="nsew", pady=(5, 5))
        self.center_container.grid_columnconfigure(0, weight=1)
        self.center_container.grid_rowconfigure(2, weight=1)

        self._create_header(self.center_container)
        self._create_main_buttons(self.center_container)
        self._create_status_area(self.center_container)

        self.left_sidebar = LeftSidebar(self.left_container, text=f"{APP_DISPLAY_NAME} v{VERSION}")
        self.right_sidebar = RightSidebar(self.right_container, icons=self.icons, current_theme=self.current_theme)
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
        theme_keys = get_theme_tokens(self.current_theme)

        self.main_menu_frame = ctk.CTkFrame(
            parent,
            fg_color=theme_keys["bg_panel"],
            corner_radius=18,
            border_width=1,
            border_color=theme_keys["border_subtle"]
        )
        self.main_menu_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        self.main_buttons_frame = ctk.CTkFrame(self.main_menu_frame, fg_color="transparent")
        self.main_buttons_frame.pack(pady=10, padx=10)

        outside_bg = theme_keys["bg_panel"]
        btn_blue = get_button_tokens("blue")
        btn_green = get_button_tokens("green")
        btn_red = get_button_tokens("red")

        common = {
            "width": BTN_W_MAIN,
            "height": BTN_H_MAIN,
            "outside_bg": outside_bg,
            "border_width": 2,
            "font": ("Segoe UI", 11, "bold"),
            "text_color": btn_blue["text"],
        }

        def build_palette(palette):
            return {
                "fg_color": palette["bg"],
                "hover_color": palette["hover"],
                "border_color": palette["border"],
                "gradient_start": palette.get("gradient_start"),
                "gradient_mid": palette.get("gradient_mid"),
                "gradient_end": palette.get("gradient_end"),
                "hover_gradient_start": palette.get("hover_gradient_start"),
                "hover_gradient_mid": palette.get("hover_gradient_mid"),
                "hover_gradient_end": palette.get("hover_gradient_end"),
            }

        self.main_buttons = {
            "selpath": PillTextButton(self.main_buttons_frame, **build_palette(btn_blue), **common),
            "choose": PillTextButton(self.main_buttons_frame, **build_palette(btn_blue), **common),
            "create_tree": PillTextButton(self.main_buttons_frame, **build_palette(btn_blue), **common),
            "openlect": PillTextButton(self.main_buttons_frame, **build_palette(btn_blue), **common),
            "openlast": PillTextButton(self.main_buttons_frame, **build_palette(btn_green), **common),
            "delete": PillTextButton(self.main_buttons_frame, **build_palette(btn_red), **common),
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
        hour = datetime.datetime.now().hour
        greet_key = "greet_m" if 5 <= hour < 12 else "greet_a" if 12 <= hour < 19 else "greet_n"
        try:
            user = os.getlogin().lower().capitalize()
        except OSError:
            user = "User"
        self.lbl_greet.configure(text=f"{self._tr(greet_key)} {user}{self._tr('welcome')}")

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

        try:
            for dialog in self._dialog_cache.values():
                try:
                    if dialog.winfo_exists() and hasattr(dialog, "refresh_texts"):
                        dialog.refresh_texts()
                except Exception:
                    pass
        except Exception:
            pass

    def apply_theme(self):
        ctk.set_appearance_mode(self.current_theme)

        theme_keys = get_theme_tokens(self.current_theme)

        self.configure(fg_color=theme_keys["bg_base"])
        self._refresh_background_canvas()

        self.left_sidebar.apply_theme(self.current_theme)
        self.right_sidebar.apply_theme(self.current_theme)
        self.status_panel.apply_theme(self.current_theme)

        try:
            self.left_container.configure(fg_color="transparent")
            self.right_container.configure(fg_color="transparent")
            self.center_container.configure(fg_color="transparent")
            self.header_frame.configure(fg_color="transparent")
            self.progress_frame.configure(fg_color="transparent")
            self.main_menu_frame.configure(fg_color=theme_keys["bg_panel"], border_color=theme_keys["border_subtle"])
        except Exception:
            pass

        for btn in self.main_buttons.values():
            try:
                btn.configure(outside_bg=theme_keys["bg_panel"])
            except Exception:
                pass

        try:
            self.footer_frame.configure(fg_color=theme_keys["bg_footer"])
            self.footer_line.configure(fg_color=theme_keys["separator_line"])
            self.lbl_greet.configure(text_color=theme_keys["text_primary"])
            self.lbl_title.configure(fg_color="transparent")
            self.lbl_copyright.configure(text_color=theme_keys["text_secondary"])
        except Exception:
            pass

    def switch_theme_animated(self, new_theme: str):
        if new_theme == self.current_theme or self._is_theme_switching:
            return
        self._is_theme_switching = True
        self._pending_new_theme = new_theme
        self._reveal_target_y = None
        CustomTooltip.hide_global()
        self._fade_out_for_switch()

    def _fade_out_for_switch(self):
        try:
            alpha = float(self.attributes("-alpha"))
            if alpha > 0.0:
                self.attributes("-alpha", max(alpha - MAIN_WINDOW_SWITCH_FADE_OUT_STEP, 0.0))
                self.after(MAIN_WINDOW_SWITCH_FADE_OUT_INTERVAL_MS, self._fade_out_for_switch)
            else:
                self.after(MAIN_WINDOW_SWITCH_HOLD_MS, self._apply_theme_after_switch)
        except Exception:
            self._is_theme_switching = False
            self.current_theme = self._pending_new_theme
            self.apply_theme()
            self.attributes("-alpha", 1.0)

    def _apply_theme_after_switch(self):
        try:
            self.current_theme = self._pending_new_theme
            self.apply_theme()
            self.update_idletasks()
            self._restore_window_stack_after_theme_switch()
            self.attributes("-alpha", 0.0)
            self._fade_in_after_switch()
        except Exception:
            self._is_theme_switching = False
            self.attributes("-alpha", 1.0)

    def _restore_window_stack_after_theme_switch(self):
        try:
            self.deiconify()
        except Exception:
            pass
        try:
            self.lift()
        except Exception:
            pass
        try:
            self.focus_force()
        except Exception:
            pass
        try:
            self.attributes("-topmost", True)
            self.after(90, lambda: self.attributes("-topmost", False))
        except Exception:
            pass

    def _fade_in_after_switch(self):
        try:
            alpha = float(self.attributes("-alpha"))
        except Exception:
            alpha = 1.0

        if alpha < 1.0:
            self.attributes("-alpha", min(alpha + MAIN_WINDOW_SWITCH_FADE_IN_STEP, 1.0))
            self.after(MAIN_WINDOW_SWITCH_FADE_IN_INTERVAL_MS, self._fade_in_after_switch)
        else:
            self._is_theme_switching = False

    def prepare_soft_refresh(self):
        CustomTooltip.hide_global()
        try:
            current_alpha = float(self.attributes("-alpha"))
        except Exception:
            current_alpha = 1.0
        try:
            self.attributes("-alpha", min(current_alpha, MAIN_WINDOW_SOFT_REFRESH_ALPHA))
        except Exception:
            pass
        self._reveal_target_y = None

    def complete_soft_refresh(self):
        self._fade_in()

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
            defer_show=True
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
            defer_show=True
        )

    def _create_media_dialog(self):
        tags_stored = self.controller.config.get("etiquetas_multimedia_config", [])
        if not tags_stored:
            raw_exts = self.controller.config.get("media_extensions", [])
            current_files = [{"nombre": x, "estado": "activo"} for x in raw_exts]
        else:
            current_files = tags_stored
        view_exts = {t["nombre"] for t in self.controller.config.get("etiquetas_extensiones_incluidas", [])}
        no_view_items = {t["nombre"] for t in self.controller.config.get("etiquetas_archivos_excluidos", [])}
        return TagsConfigDialog(
            parent=self,
            title=self._tr("dlg_etiqueta_title"),
            folders_prompt=None,
            initial_folders=None,
            files_prompt=self._tr("dlg_etiqueta_file_prompt"),
            initial_files=current_files,
            forbidden_items=view_exts.union(no_view_items),
            persistent=True,
            defer_show=True
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
            defer_show=True
        )

    def _create_settings_dialog(self):
        return SettingsDialog(
            parent=self,
            current_extension=self.controller.config.get("report_extension", ".txt"),
            current_exe_path=self.controller.config.get("custom_exe_path", ""),
            persistent=True,
            defer_show=True
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

    def _preload_persistent_dialogs(self):
        try:
            self.get_view_dialog()
            self.get_no_view_dialog()
            self.get_media_dialog()
            self.get_profiles_dialog()
            self.get_settings_dialog()
        except Exception:
            pass

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
            self._modal_fail_safe_after_id = self.after(900, self._modal_fail_safe_check)
        except Exception:
            self._modal_fail_safe_after_id = None

    def _has_live_modal_dialog(self) -> bool:
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
        self.restore_ui_from_modal()

    def get_min_visible_completion_delay_ms(self) -> int:
        return self.status_panel.get_min_visible_completion_delay_ms()

    def set_progress(self, percentage, file_context=None):
        self.status_panel.set_progress(percentage, file_context)

    def toggle_ui_for_processing(self, is_active: bool, mode: str = "determinate", text: str = None,
                                 final_status: str = None):
        CustomTooltip.hide_global()
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
        CustomTooltip.hide_global()
        self._is_modal_open = True
        for btn in self.main_buttons.values():
            btn.configure(state="disabled")
        for btn in self.sidebar_buttons.values():
            btn.configure(state="disabled")
        self.left_sidebar.configure(state="disabled")
        self._schedule_modal_fail_safe()

    def restore_ui_from_modal(self):
        CustomTooltip.hide_global()
        self._cancel_modal_fail_safe()
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
        CustomTooltip.hide_global()
        try:
            MessageDialog(self, self._tr(title_key), self._tr(message_key, *args))
        except Exception:
            self.restore_ui_from_modal()

    def show_app_info(self):
        if self.controller and hasattr(self.controller, "open_manual_link"):
            self.controller.open_manual_link()
        else:
            webbrowser.open(APP_WEBSITE_URL)