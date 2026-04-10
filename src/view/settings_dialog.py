import customtkinter as ctk
from app_meta import APP_EXECUTABLE_NAME
from view.dialogs import BaseDialog, _style_button, _get_color_tuple, _style_entry
from view.ui_constants import FONT_FAMILY_PRIMARY, get_button_tokens, SETTINGS_DIALOG_WIDTH, SETTINGS_DIALOG_HEIGHT, SETTINGS_DIALOG_MAIN_PADX, SETTINGS_DIALOG_MAIN_PADY, SETTINGS_DIALOG_CONTENT_PADX, SETTINGS_DIALOG_CONTENT_PADY, SETTINGS_DIALOG_SECTION_FONT_SIZE, SETTINGS_DIALOG_SECTION_PADY, SETTINGS_DIALOG_FORMAT_SHELL_BORDER_WIDTH, SETTINGS_DIALOG_FORMAT_SHELL_RADIUS, SETTINGS_DIALOG_FORMAT_SHELL_PADY, SETTINGS_DIALOG_FORMAT_BUTTON_WIDTH, SETTINGS_DIALOG_FORMAT_BUTTON_HEIGHT, SETTINGS_DIALOG_FORMAT_BUTTON_PAD, SETTINGS_DIALOG_EXE_LABEL_PADY, SETTINGS_DIALOG_EXAMPLE_FONT_SIZE, SETTINGS_DIALOG_EXAMPLE_PADY, SETTINGS_DIALOG_ENTRY_PADY, SETTINGS_DIALOG_SEPARATOR_HEIGHT, SETTINGS_DIALOG_SEPARATOR_PADY, SETTINGS_DIALOG_SHORTCUTS_LABEL_PADY, SETTINGS_DIALOG_SHORTCUT_BUTTON_PADY, SETTINGS_DIALOG_SHORTCUT_LAST_BUTTON_PADY, SETTINGS_DIALOG_TRANSFER_LABEL_PADY, SETTINGS_DIALOG_TRANSFER_BUTTON_PADY, SETTINGS_DIALOG_TRANSFER_LAST_BUTTON_PADY, SETTINGS_DIALOG_TOGGLE_RADIUS, SETTINGS_DIALOG_TOGGLE_BORDER_WIDTH, SETTINGS_DIALOG_TOGGLE_FONT_SIZE
from view.translations import translate_default

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
    def __init__(self, parent, current_extension: str = ".txt", current_exe_path: str = "", on_save_callback=None,
                 on_shortcut_callback=None, on_export_callback=None, on_import_callback=None, persistent: bool = False, defer_show: bool = False):
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

        self.geometry(f"{SETTINGS_DIALOG_WIDTH}x{SETTINGS_DIALOG_HEIGHT}")

        self.main_frame = self._create_card_frame()
        self.main_frame.pack_configure(padx=SETTINGS_DIALOG_MAIN_PADX, pady=SETTINGS_DIALOG_MAIN_PADY)

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=SETTINGS_DIALOG_CONTENT_PADX, pady=SETTINGS_DIALOG_CONTENT_PADY)

        self.lbl_report_format = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_report_format"),
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "bold"),
            text_color=_get_color_tuple("text")
        )
        self.lbl_report_format.pack(pady=SETTINGS_DIALOG_SECTION_PADY, anchor="w")

        self.fmt_var = ctk.StringVar(value=self.selected_extension)
        self.format_shell = ctk.CTkFrame(
            self.content_frame,
            fg_color=_get_color_tuple("bg_panel"),
            border_width=SETTINGS_DIALOG_FORMAT_SHELL_BORDER_WIDTH,
            border_color=_get_color_tuple("border_subtle"),
            corner_radius=SETTINGS_DIALOG_FORMAT_SHELL_RADIUS
        )
        self.format_shell.pack(pady=SETTINGS_DIALOG_FORMAT_SHELL_PADY, anchor="w")

        self.btn_fmt_txt = ctk.CTkButton(
            self.format_shell,
            text=_tr_text(self.parent_view, "btn_format_txt"),
            width=SETTINGS_DIALOG_FORMAT_BUTTON_WIDTH,
            height=SETTINGS_DIALOG_FORMAT_BUTTON_HEIGHT,
            command=lambda: self._on_format_change(".txt")
        )
        self.btn_fmt_txt.pack(side="left", padx=SETTINGS_DIALOG_FORMAT_BUTTON_PAD, pady=SETTINGS_DIALOG_FORMAT_BUTTON_PAD)

        self.btn_fmt_md = ctk.CTkButton(
            self.format_shell,
            text=_tr_text(self.parent_view, "btn_format_md"),
            width=SETTINGS_DIALOG_FORMAT_BUTTON_WIDTH,
            height=SETTINGS_DIALOG_FORMAT_BUTTON_HEIGHT,
            command=lambda: self._on_format_change(".md")
        )
        self.btn_fmt_md.pack(side="left", padx=(0, SETTINGS_DIALOG_FORMAT_BUTTON_PAD), pady=SETTINGS_DIALOG_FORMAT_BUTTON_PAD)

        self.lbl_exe_path = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_exe_path", APP_EXECUTABLE_NAME),
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "bold"),
            text_color=_get_color_tuple("text")
        )
        self.lbl_exe_path.pack(pady=SETTINGS_DIALOG_EXE_LABEL_PADY, anchor="w")

        self.lbl_exe_example = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_exe_example", APP_EXECUTABLE_NAME),
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_EXAMPLE_FONT_SIZE, "normal"),
            text_color=_get_color_tuple("text_secondary")
        )
        self.lbl_exe_example.pack(pady=SETTINGS_DIALOG_EXAMPLE_PADY, anchor="w")

        self.entry_exe = ctk.CTkEntry(
            self.content_frame,
            placeholder_text=self.parent_view._tr("ph_exe_path")
        )
        _style_entry(self.entry_exe)
        self.entry_exe.pack(pady=SETTINGS_DIALOG_ENTRY_PADY, fill="x")
        self.entry_exe.insert(0, self.current_exe_path)

        ctk.CTkFrame(self.content_frame, height=SETTINGS_DIALOG_SEPARATOR_HEIGHT, fg_color=_get_color_tuple("separator_line")).pack(fill="x", pady=SETTINGS_DIALOG_SEPARATOR_PADY)

        self.lbl_system_shortcuts = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_system_shortcuts"),
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "bold"),
            text_color=_get_color_tuple("text")
        )
        self.lbl_system_shortcuts.pack(pady=SETTINGS_DIALOG_SHORTCUTS_LABEL_PADY, anchor="w")

        self.shortcuts_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.shortcuts_frame.pack(fill="x")

        self.btn_desktop = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_desktop"),
            command=lambda: self._trigger_shortcut("desktop")
        )
        _style_button(self.btn_desktop, "blue")
        self.btn_desktop.pack(pady=SETTINGS_DIALOG_SHORTCUT_BUTTON_PADY, fill="x")

        self.btn_start = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_start"),
            command=lambda: self._trigger_shortcut("start")
        )
        _style_button(self.btn_start, "blue")
        self.btn_start.pack(pady=SETTINGS_DIALOG_SHORTCUT_BUTTON_PADY, fill="x")

        self.btn_taskbar = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_taskbar"),
            command=lambda: self._trigger_shortcut("taskbar")
        )
        _style_button(self.btn_taskbar, "blue")
        self.btn_taskbar.pack(pady=SETTINGS_DIALOG_SHORTCUT_BUTTON_PADY, fill="x")

        self.btn_pin_start = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_pin_start"),
            command=lambda: self._trigger_shortcut("start_pin")
        )
        _style_button(self.btn_pin_start, "blue")
        self.btn_pin_start.pack(pady=SETTINGS_DIALOG_SHORTCUT_LAST_BUTTON_PADY, fill="x")

        ctk.CTkFrame(self.content_frame, height=SETTINGS_DIALOG_SEPARATOR_HEIGHT, fg_color=_get_color_tuple("separator_line")).pack(fill="x", pady=SETTINGS_DIALOG_SEPARATOR_PADY)

        self.lbl_config_transfer = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_config_transfer"),
            font=(FONT_FAMILY_PRIMARY, SETTINGS_DIALOG_SECTION_FONT_SIZE, "bold"),
            text_color=_get_color_tuple("text")
        )
        self.lbl_config_transfer.pack(pady=SETTINGS_DIALOG_TRANSFER_LABEL_PADY, anchor="w")

        self.transfer_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.transfer_frame.pack(fill="x")

        self.btn_export_config = ctk.CTkButton(
            self.transfer_frame,
            text=self.parent_view._tr("btn_export_config"),
            command=self._trigger_export
        )
        _style_button(self.btn_export_config, "blue")
        self.btn_export_config.pack(pady=SETTINGS_DIALOG_TRANSFER_BUTTON_PADY, fill="x")
        action_button_height = int(self.btn_export_config.cget("height"))

        self.btn_import_config = ctk.CTkButton(
            self.transfer_frame,
            text=self.parent_view._tr("btn_import_config"),
            command=self._trigger_import,
            height=action_button_height
        )
        _style_button(self.btn_import_config, "green")
        self.btn_import_config.configure(height=action_button_height)
        self.btn_import_config.pack(pady=SETTINGS_DIALOG_TRANSFER_LAST_BUTTON_PADY, fill="x")

        self._apply_format_button_styles()

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
                fg_color=blue["bg"] if is_selected else _get_color_tuple("bg_dialog"),
                hover_color=blue["hover"] if is_selected else neutral["hover"],
                border_color=blue["border"] if is_selected else _get_color_tuple("border_subtle"),
                text_color=blue["text"] if is_selected else _get_color_tuple("text")
            )

    def refresh_texts(self):
        try:
            self.title(_tr_text(self.parent_view, "dlg_settings_title"))
        except Exception:
            pass
        self.lbl_report_format.configure(text=self.parent_view._tr("lbl_report_format"))
        self.lbl_exe_path.configure(text=self.parent_view._tr("lbl_exe_path", APP_EXECUTABLE_NAME))
        self.lbl_exe_example.configure(text=self.parent_view._tr("lbl_exe_example", APP_EXECUTABLE_NAME))
        self.entry_exe.configure(placeholder_text=self.parent_view._tr("ph_exe_path"))
        self.lbl_system_shortcuts.configure(text=self.parent_view._tr("lbl_system_shortcuts"))
        self.btn_desktop.configure(text=self.parent_view._tr("btn_shortcut_desktop"))
        self.btn_start.configure(text=self.parent_view._tr("btn_shortcut_start"))
        self.btn_taskbar.configure(text=self.parent_view._tr("btn_shortcut_taskbar"))
        self.btn_pin_start.configure(text=self.parent_view._tr("btn_shortcut_pin_start"))
        self.lbl_config_transfer.configure(text=self.parent_view._tr("lbl_config_transfer"))
        self.btn_export_config.configure(text=self.parent_view._tr("btn_export_config"))
        self.btn_import_config.configure(text=self.parent_view._tr("btn_import_config"))
        self.btn_fmt_txt.configure(text=_tr_text(self.parent_view, "btn_format_txt"))
        self.btn_fmt_md.configure(text=_tr_text(self.parent_view, "btn_format_md"))
        self._apply_format_button_styles()

    def load_state(self, current_extension: str, current_exe_path: str, on_save_callback=None, on_shortcut_callback=None, on_export_callback=None, on_import_callback=None):
        self.selected_extension = current_extension
        self.current_exe_path = current_exe_path or ""
        self.on_save_callback = on_save_callback
        self.on_shortcut_callback = on_shortcut_callback
        self.on_export_callback = on_export_callback
        self.on_import_callback = on_import_callback
        self.result = None
        self.fmt_var.set(self.selected_extension)
        self.entry_exe.delete(0, "end")
        self.entry_exe.insert(0, self.current_exe_path)
        self._apply_format_button_styles()
        self.refresh_texts()

    def present(self):
        super().present()
        try:
            self.entry_exe.focus_set()
        except Exception:
            pass

    def _on_format_change(self, value):
        self.selected_extension = value
        self.fmt_var.set(value)
        self._apply_format_button_styles()

    def _trigger_shortcut(self, shortcut_type):
        current_path_input = self.entry_exe.get().strip().replace('"', '')
        if self.on_shortcut_callback:
            self.on_shortcut_callback(shortcut_type, current_path_input, parent_window=self)

    def _trigger_export(self):
        if self.on_export_callback:
            self.on_export_callback(parent_window=self)

    def _trigger_import(self):
        if self.on_import_callback:
            self.on_import_callback(parent_window=self)

    def _on_ok(self):
        final_ext = self.fmt_var.get()
        final_path = self.entry_exe.get().strip().replace('"', '')
        self.result = (final_ext, final_path)
        if self.on_save_callback:
            self.on_save_callback(final_ext, final_path)
        self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, current_extension, current_exe_path, on_save_callback, on_shortcut_callback, on_export_callback=None, on_import_callback=None):
        dialog = None
        try:
            dialog = cls(parent, current_extension, current_exe_path, on_save_callback, on_shortcut_callback, on_export_callback, on_import_callback)
            parent.wait_window(dialog)
            return dialog.result
        except Exception:
            try:
                if hasattr(parent, "restore_ui_from_modal"):
                    parent.restore_ui_from_modal()
            except Exception:
                pass
            return None
        finally:
            if dialog is not None:
                try:
                    if dialog.winfo_exists():
                        dialog.destroy()
                except Exception:
                    pass
