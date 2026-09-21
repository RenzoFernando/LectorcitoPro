import customtkinter as ctk

from app_meta import APP_EXECUTABLE_NAME
from i18n.translations import translate_default
from view.dialogs import BaseDialog, _get_color_tuple, _style_button, _style_entry
from view.ui_constants import (
    FONT_FAMILY_PRIMARY,
    SETTINGS_DIALOG_CONTENT_PADX,
    SETTINGS_DIALOG_CONTENT_PADY,
    SETTINGS_DIALOG_ENTRY_PADY,
    SETTINGS_DIALOG_EXAMPLE_FONT_SIZE,
    SETTINGS_DIALOG_EXAMPLE_PADY,
    SETTINGS_DIALOG_EXE_LABEL_PADY,
    SETTINGS_DIALOG_FORMAT_BUTTON_HEIGHT,
    SETTINGS_DIALOG_FORMAT_BUTTON_PAD,
    SETTINGS_DIALOG_FORMAT_BUTTON_WIDTH,
    SETTINGS_DIALOG_FORMAT_SHELL_BORDER_WIDTH,
    SETTINGS_DIALOG_FORMAT_SHELL_PADY,
    SETTINGS_DIALOG_FORMAT_SHELL_RADIUS,
    SETTINGS_DIALOG_HEIGHT,
    SETTINGS_DIALOG_MAIN_PADX,
    SETTINGS_DIALOG_MAIN_PADY,
    SETTINGS_DIALOG_SECTION_FONT_SIZE,
    SETTINGS_DIALOG_SECTION_PADY,
    SETTINGS_DIALOG_SEPARATOR_HEIGHT,
    SETTINGS_DIALOG_SEPARATOR_PADY,
    SETTINGS_DIALOG_SHORTCUT_BUTTON_PADY,
    SETTINGS_DIALOG_SHORTCUT_LAST_BUTTON_PADY,
    SETTINGS_DIALOG_SHORTCUTS_LABEL_PADY,
    SETTINGS_DIALOG_TOGGLE_BORDER_WIDTH,
    SETTINGS_DIALOG_TOGGLE_FONT_SIZE,
    SETTINGS_DIALOG_TOGGLE_RADIUS,
    SETTINGS_DIALOG_TRANSFER_BUTTON_PADY,
    SETTINGS_DIALOG_TRANSFER_LABEL_PADY,
    SETTINGS_DIALOG_TRANSFER_LAST_BUTTON_PADY,
    SETTINGS_DIALOG_WIDTH,
    get_button_tokens,
)

# =============================================================================
# DIALOGO DE CONFIGURACION GENERAL
# =============================================================================


def _tr_text(parent, key: str, *args):
    tr_callable = getattr(parent, "_tr", None)
    if callable(tr_callable):
        try:
            return tr_callable(key, *args)
        except Exception:
            pass
    return translate_default(key, *args)


class SettingsDialog(BaseDialog):
    def __init__(
        self,
        parent,
        current_extension: str = ".md",
        current_exe_path: str = "",
        on_save_callback=None,
        on_shortcut_callback=None,
        on_export_callback=None,
        on_import_callback=None,
        platform_capabilities=None,
        persistent: bool = False,
        defer_show: bool = False,
    ):
        title = _tr_text(parent, "dlg_settings_title")
        super().__init__(parent, title, persistent=persistent, defer_show=defer_show)

        self.parent_view = parent
        self.selected_extension = current_extension
        self.current_exe_path = current_exe_path or ""
        self.on_save_callback = on_save_callback
        self.on_shortcut_callback = on_shortcut_callback
        self.on_export_callback = on_export_callback
        self.on_import_callback = on_import_callback
        self.result = None
        self.platform_capabilities = self._normalize_platform_capabilities(platform_capabilities)
        self._save_after_id = None
        self._closing_settings_saved = False
        self._last_saved_extension = self.selected_extension
        self._last_saved_exe_path = self.current_exe_path

        self.geometry(f"{SETTINGS_DIALOG_WIDTH}x{SETTINGS_DIALOG_HEIGHT}")

        self.main_frame = self._create_card_frame()
        self.main_frame.pack_configure(
            padx=SETTINGS_DIALOG_MAIN_PADX, pady=SETTINGS_DIALOG_MAIN_PADY
        )

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(
            fill="both",
            expand=True,
            padx=SETTINGS_DIALOG_CONTENT_PADX,
            pady=SETTINGS_DIALOG_CONTENT_PADY,
        )

        self.lbl_report_format = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_report_format"),
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "bold"),
            text_color=_get_color_tuple("text"),
        )
        self.lbl_report_format.pack(pady=SETTINGS_DIALOG_SECTION_PADY, anchor="w")

        self.fmt_var = ctk.StringVar(value=self.selected_extension)
        self.format_shell = ctk.CTkFrame(
            self.content_frame,
            fg_color=_get_color_tuple("surface_alt"),
            border_width=SETTINGS_DIALOG_FORMAT_SHELL_BORDER_WIDTH,
            border_color=_get_color_tuple("border_subtle"),
            corner_radius=SETTINGS_DIALOG_FORMAT_SHELL_RADIUS,
        )
        self.format_shell.pack(pady=SETTINGS_DIALOG_FORMAT_SHELL_PADY, anchor="w")

        self.btn_fmt_md = ctk.CTkButton(
            self.format_shell,
            text=_tr_text(self.parent_view, "btn_format_md"),
            width=SETTINGS_DIALOG_FORMAT_BUTTON_WIDTH,
            height=SETTINGS_DIALOG_FORMAT_BUTTON_HEIGHT,
            command=lambda: self._on_format_change(".md"),
        )
        self.btn_fmt_md.pack(
            side="left",
            padx=SETTINGS_DIALOG_FORMAT_BUTTON_PAD,
            pady=SETTINGS_DIALOG_FORMAT_BUTTON_PAD,
        )

        self.btn_fmt_txt = ctk.CTkButton(
            self.format_shell,
            text=_tr_text(self.parent_view, "btn_format_txt"),
            width=SETTINGS_DIALOG_FORMAT_BUTTON_WIDTH,
            height=SETTINGS_DIALOG_FORMAT_BUTTON_HEIGHT,
            command=lambda: self._on_format_change(".txt"),
        )
        self.btn_fmt_txt.pack(
            side="left",
            padx=(0, SETTINGS_DIALOG_FORMAT_BUTTON_PAD),
            pady=SETTINGS_DIALOG_FORMAT_BUTTON_PAD,
        )

        self.lbl_exe_path = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_exe_path", APP_EXECUTABLE_NAME),
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "bold"),
            text_color=_get_color_tuple("text"),
        )
        self.lbl_exe_path.pack(pady=SETTINGS_DIALOG_EXE_LABEL_PADY, anchor="w")

        self.lbl_exe_example = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_exe_example", APP_EXECUTABLE_NAME),
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_EXAMPLE_FONT_SIZE, "normal"),
            text_color=_get_color_tuple("text_secondary"),
        )
        self.lbl_exe_example.pack(pady=SETTINGS_DIALOG_EXAMPLE_PADY, anchor="w")

        self.entry_exe = ctk.CTkEntry(
            self.content_frame, placeholder_text=self.parent_view._tr("ph_exe_path")
        )
        _style_entry(self.entry_exe)
        self.entry_exe.pack(pady=SETTINGS_DIALOG_ENTRY_PADY, fill="x")
        self.entry_exe.insert(0, self.current_exe_path)
        self.entry_exe.bind("<KeyRelease>", self._schedule_auto_save, add="+")
        self.entry_exe.bind("<FocusOut>", self._flush_pending_settings, add="+")
        self.entry_exe.bind("<Return>", self._on_exe_return, add="+")

        self.system_section_separator = ctk.CTkFrame(
            self.content_frame,
            height=SETTINGS_DIALOG_SEPARATOR_HEIGHT,
            fg_color=_get_color_tuple("separator_line"),
        )
        self.system_section_separator.pack(fill="x", pady=SETTINGS_DIALOG_SEPARATOR_PADY)

        self.lbl_system_shortcuts = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_system_shortcuts"),
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "bold"),
            text_color=_get_color_tuple("text"),
        )
        self.lbl_system_shortcuts.pack(pady=SETTINGS_DIALOG_SHORTCUTS_LABEL_PADY, anchor="w")

        self.shortcuts_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.shortcuts_frame.pack(fill="x")

        self.btn_desktop = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_desktop"),
            command=lambda: self._trigger_shortcut("desktop"),
        )
        _style_button(self.btn_desktop, "neutral")
        self.btn_desktop.configure(
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "normal")
        )
        self.btn_desktop.pack(pady=SETTINGS_DIALOG_SHORTCUT_BUTTON_PADY, fill="x")

        self.btn_start = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_start"),
            command=lambda: self._trigger_shortcut("start"),
        )
        _style_button(self.btn_start, "neutral")
        self.btn_start.configure(
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "normal")
        )
        self.btn_start.pack(pady=SETTINGS_DIALOG_SHORTCUT_BUTTON_PADY, fill="x")

        self.btn_taskbar = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_taskbar"),
            command=lambda: self._trigger_shortcut("taskbar"),
        )
        _style_button(self.btn_taskbar, "neutral")
        self.btn_taskbar.configure(
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "normal")
        )
        self.btn_taskbar.pack(pady=SETTINGS_DIALOG_SHORTCUT_BUTTON_PADY, fill="x")

        self.btn_pin_start = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_pin_start"),
            command=lambda: self._trigger_shortcut("start_pin"),
        )
        _style_button(self.btn_pin_start, "neutral")
        self.btn_pin_start.configure(
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "normal")
        )
        self.btn_pin_start.pack(pady=SETTINGS_DIALOG_SHORTCUT_LAST_BUTTON_PADY, fill="x")

        self.transfer_separator = ctk.CTkFrame(
            self.content_frame,
            height=SETTINGS_DIALOG_SEPARATOR_HEIGHT,
            fg_color=_get_color_tuple("separator_line"),
        )
        self.transfer_separator.pack(fill="x", pady=SETTINGS_DIALOG_SEPARATOR_PADY)

        self.lbl_config_transfer = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_config_transfer"),
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "bold"),
            text_color=_get_color_tuple("text"),
        )
        self.lbl_config_transfer.pack(pady=SETTINGS_DIALOG_TRANSFER_LABEL_PADY, anchor="w")

        self.transfer_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.transfer_frame.pack(fill="x")

        self.btn_export_config = ctk.CTkButton(
            self.transfer_frame,
            text=self.parent_view._tr("btn_export_config"),
            command=self._trigger_export,
        )
        _style_button(self.btn_export_config, "blue")
        self.btn_export_config.pack(pady=SETTINGS_DIALOG_TRANSFER_BUTTON_PADY, fill="x")
        action_button_height = int(self.btn_export_config.cget("height"))

        self.btn_import_config = ctk.CTkButton(
            self.transfer_frame,
            text=self.parent_view._tr("btn_import_config"),
            command=self._trigger_import,
            height=action_button_height,
        )
        _style_button(self.btn_import_config, "green")
        self.btn_import_config.configure(height=action_button_height)
        self.btn_import_config.pack(pady=SETTINGS_DIALOG_TRANSFER_LAST_BUTTON_PADY, fill="x")

        self._apply_format_button_styles()
        self._apply_platform_capabilities()

    def _normalize_platform_capabilities(self, capabilities):
        if capabilities is None:
            return {
                "platform": "windows",
                "supports_launcher_configuration": True,
                "shortcut_modes": ("desktop", "start", "taskbar", "start_pin"),
                "system_shortcuts_label_key": "lbl_system_shortcuts",
                "shortcut_label_keys": {},
            }
        source = capabilities if isinstance(capabilities, dict) else {}
        shortcut_modes = source.get("shortcut_modes", ())
        if isinstance(shortcut_modes, str):
            shortcut_modes = (shortcut_modes,)
        shortcut_label_keys = source.get("shortcut_label_keys", {})
        if not isinstance(shortcut_label_keys, dict):
            shortcut_label_keys = {}
        return {
            "platform": str(source.get("platform", "generic")),
            "supports_launcher_configuration": bool(
                source.get("supports_launcher_configuration", False)
            ),
            "shortcut_modes": tuple(shortcut_modes or ()),
            "system_shortcuts_label_key": str(
                source.get("system_shortcuts_label_key", "lbl_system_shortcuts")
            ),
            "shortcut_label_keys": dict(shortcut_label_keys),
        }

    def _apply_platform_capabilities(self):
        supports_launcher = bool(
            self.platform_capabilities.get("supports_launcher_configuration", False)
        )
        shortcut_modes = set(self.platform_capabilities.get("shortcut_modes", ()))
        has_system_integration = supports_launcher or bool(shortcut_modes)

        if not supports_launcher:
            self.lbl_exe_path.pack_forget()
            self.lbl_exe_example.pack_forget()
            self.entry_exe.pack_forget()

        button_modes = {
            "desktop": self.btn_desktop,
            "start": self.btn_start,
            "taskbar": self.btn_taskbar,
            "start_pin": self.btn_pin_start,
        }
        for mode, button in button_modes.items():
            if mode not in shortcut_modes:
                button.pack_forget()

        if not shortcut_modes:
            self.lbl_system_shortcuts.pack_forget()
            self.shortcuts_frame.pack_forget()

        if not has_system_integration:
            self.system_section_separator.pack_forget()
            self.transfer_separator.pack_forget()

    def _apply_format_button_styles(self):
        blue = get_button_tokens("blue")
        neutral = get_button_tokens("neutral")
        selected = self.fmt_var.get()
        shells = {
            ".txt": self.btn_fmt_txt,
            ".md": self.btn_fmt_md,
        }
        for value, button in shells.items():
            is_selected = value == selected
            button.configure(
                corner_radius=SETTINGS_DIALOG_TOGGLE_RADIUS,
                border_width=SETTINGS_DIALOG_TOGGLE_BORDER_WIDTH,
                font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_TOGGLE_FONT_SIZE, "bold"),
                fg_color=blue["bg"] if is_selected else _get_color_tuple("bg_elevated"),
                hover_color=blue["hover"] if is_selected else neutral["hover"],
                border_color=blue["border"] if is_selected else _get_color_tuple("border_subtle"),
                text_color=blue["text"] if is_selected else _get_color_tuple("text"),
            )

    def refresh_texts(self):
        try:
            self.title(_tr_text(self.parent_view, "dlg_settings_title"))
        except Exception:
            pass
        self.lbl_report_format.configure(text=self.parent_view._tr("lbl_report_format"))
        self.lbl_exe_path.configure(text=self.parent_view._tr("lbl_exe_path", APP_EXECUTABLE_NAME))
        self.lbl_exe_example.configure(
            text=self.parent_view._tr("lbl_exe_example", APP_EXECUTABLE_NAME)
        )
        self.entry_exe.configure(placeholder_text=self.parent_view._tr("ph_exe_path"))
        system_label_key = self.platform_capabilities.get(
            "system_shortcuts_label_key", "lbl_system_shortcuts"
        )
        shortcut_label_keys = self.platform_capabilities.get("shortcut_label_keys", {})
        self.lbl_system_shortcuts.configure(text=self.parent_view._tr(system_label_key))
        self.btn_desktop.configure(
            text=self.parent_view._tr(shortcut_label_keys.get("desktop", "btn_shortcut_desktop"))
        )
        self.btn_start.configure(
            text=self.parent_view._tr(shortcut_label_keys.get("start", "btn_shortcut_start"))
        )
        self.btn_taskbar.configure(
            text=self.parent_view._tr(shortcut_label_keys.get("taskbar", "btn_shortcut_taskbar"))
        )
        self.btn_pin_start.configure(
            text=self.parent_view._tr(
                shortcut_label_keys.get("start_pin", "btn_shortcut_pin_start")
            )
        )
        self.lbl_config_transfer.configure(text=self.parent_view._tr("lbl_config_transfer"))
        self.btn_export_config.configure(text=self.parent_view._tr("btn_export_config"))
        self.btn_import_config.configure(text=self.parent_view._tr("btn_import_config"))
        self.btn_fmt_txt.configure(text=_tr_text(self.parent_view, "btn_format_txt"))
        self.btn_fmt_md.configure(text=_tr_text(self.parent_view, "btn_format_md"))
        self._apply_format_button_styles()

    def load_state(
        self,
        current_extension: str,
        current_exe_path: str,
        on_save_callback=None,
        on_shortcut_callback=None,
        on_export_callback=None,
        on_import_callback=None,
        platform_capabilities=None,
    ):
        self._cancel_scheduled_save()
        self.selected_extension = current_extension
        self.current_exe_path = current_exe_path or ""
        self._last_saved_extension = self.selected_extension
        self._last_saved_exe_path = self.current_exe_path
        self._closing_settings_saved = False
        self.on_save_callback = on_save_callback
        self.on_shortcut_callback = on_shortcut_callback
        self.on_export_callback = on_export_callback
        self.on_import_callback = on_import_callback
        if platform_capabilities is not None:
            self.platform_capabilities = self._normalize_platform_capabilities(
                platform_capabilities
            )
        self.result = None
        self.fmt_var.set(self.selected_extension)
        self.entry_exe.delete(0, "end")
        self.entry_exe.insert(0, self.current_exe_path)
        self._apply_format_button_styles()
        self._apply_platform_capabilities()
        self.refresh_texts()

    def present(self):
        self._closing_settings_saved = False
        super().present()
        try:
            if self.platform_capabilities.get("supports_launcher_configuration", False):
                self.entry_exe.focus_set()
            else:
                self.btn_fmt_md.focus_set()
        except Exception:
            pass

    def _cancel_scheduled_save(self):
        if self._save_after_id is None:
            return
        try:
            self.after_cancel(self._save_after_id)
        except Exception:
            pass
        self._save_after_id = None

    def _current_settings(self):
        current_path = (
            self.entry_exe.get().strip().replace('"', "")
            if self.platform_capabilities.get("supports_launcher_configuration", False)
            else self.current_exe_path
        )
        return self.fmt_var.get(), current_path

    def _persist_current_settings(self):
        self._cancel_scheduled_save()
        current_ext, current_path = self._current_settings()
        if current_ext == self._last_saved_extension and current_path == self._last_saved_exe_path:
            return

        if self.on_save_callback:
            self.on_save_callback(current_ext, current_path)

        self.selected_extension = current_ext
        self.current_exe_path = current_path
        self._last_saved_extension = current_ext
        self._last_saved_exe_path = current_path

    def _schedule_auto_save(self, event=None):
        self._cancel_scheduled_save()
        try:
            self._save_after_id = self.after(300, self._persist_current_settings)
        except Exception:
            self._save_after_id = None

    def _flush_pending_settings(self, event=None):
        self._persist_current_settings()

    def _on_exe_return(self, event=None):
        self._flush_pending_settings()
        return "break"

    def _on_format_change(self, value):
        self.selected_extension = value
        self.fmt_var.set(value)
        self._apply_format_button_styles()
        self._persist_current_settings()

    def _trigger_shortcut(self, shortcut_type):
        self._flush_pending_settings()
        if shortcut_type not in self.platform_capabilities.get("shortcut_modes", ()):
            return
        current_path_input = (
            self.entry_exe.get().strip().replace('"', "")
            if self.platform_capabilities.get("supports_launcher_configuration", False)
            else ""
        )
        if self.on_shortcut_callback:
            self.on_shortcut_callback(shortcut_type, current_path_input, parent_window=self)

    def _trigger_export(self):
        self._flush_pending_settings()
        if self.on_export_callback:
            self.on_export_callback(parent_window=self)

    def _trigger_import(self):
        self._flush_pending_settings()
        if self.on_import_callback:
            self.on_import_callback(parent_window=self)

    def _close_with_fade_out(self, event=None):
        if not self._closing_settings_saved:
            self._closing_settings_saved = True
            self._flush_pending_settings()
        return super()._close_with_fade_out(event)
