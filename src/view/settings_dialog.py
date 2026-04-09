import customtkinter as ctk
from app_meta import APP_EXECUTABLE_NAME
from view.dialogs import BaseDialog, _style_button, _get_color_tuple, _style_entry
from view.ui_constants import get_button_tokens


# =============================================================================
# DIALOGO DE CONFIGURACION GENERAL
# =============================================================================

class SettingsDialog(BaseDialog):
    def __init__(self, parent, current_extension: str = ".txt", current_exe_path: str = "", on_save_callback=None,
                 on_shortcut_callback=None, persistent: bool = False, defer_show: bool = False):
        title = parent._tr("dlg_settings_title") if hasattr(parent, "_tr") else "Ajustes"
        super().__init__(parent, title, persistent=persistent, defer_show=defer_show)

        self.parent_view = parent
        self.selected_extension = current_extension
        self.current_exe_path = current_exe_path or ""
        self.on_save_callback = on_save_callback
        self.on_shortcut_callback = on_shortcut_callback
        self.result = None

        self.geometry("450x486")

        self.main_frame = self._create_card_frame()
        self.main_frame.pack_configure(padx=15, pady=(15, 8))

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=18, pady=(18, 8))

        self.lbl_report_format = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_report_format"),
            font=("Segoe UI", 12, "bold"),
            text_color=_get_color_tuple("text")
        )
        self.lbl_report_format.pack(pady=(0, 5), anchor="w")

        self.fmt_var = ctk.StringVar(value=self.selected_extension)
        self.format_shell = ctk.CTkFrame(
            self.content_frame,
            fg_color=_get_color_tuple("bg_panel"),
            border_width=1,
            border_color=_get_color_tuple("border_subtle"),
            corner_radius=15
        )
        self.format_shell.pack(pady=(0, 8), anchor="w")

        self.btn_fmt_txt = ctk.CTkButton(
            self.format_shell,
            text="TXT",
            width=84,
            height=34,
            command=lambda: self._on_format_change(".txt")
        )
        self.btn_fmt_txt.pack(side="left", padx=4, pady=4)

        self.btn_fmt_md = ctk.CTkButton(
            self.format_shell,
            text="MD",
            width=84,
            height=34,
            command=lambda: self._on_format_change(".md")
        )
        self.btn_fmt_md.pack(side="left", padx=(0, 4), pady=4)

        self.lbl_exe_path = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_exe_path", APP_EXECUTABLE_NAME),
            font=("Segoe UI", 12, "bold"),
            text_color=_get_color_tuple("text")
        )
        self.lbl_exe_path.pack(pady=(10, 2), anchor="w")

        self.lbl_exe_example = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_exe_example", APP_EXECUTABLE_NAME),
            font=("Segoe UI", 10, "normal"),
            text_color=_get_color_tuple("text_secondary")
        )
        self.lbl_exe_example.pack(pady=(0, 5), anchor="w")

        self.entry_exe = ctk.CTkEntry(
            self.content_frame,
            placeholder_text=self.parent_view._tr("ph_exe_path")
        )
        _style_entry(self.entry_exe)
        self.entry_exe.pack(pady=(0, 8), fill="x")
        self.entry_exe.insert(0, self.current_exe_path)

        ctk.CTkFrame(self.content_frame, height=1, fg_color=_get_color_tuple("separator_line")).pack(fill="x", pady=(2, 6))

        self.lbl_system_shortcuts = ctk.CTkLabel(
            self.content_frame,
            text=self.parent_view._tr("lbl_system_shortcuts"),
            font=("Segoe UI", 12, "bold"),
            text_color=_get_color_tuple("text")
        )
        self.lbl_system_shortcuts.pack(pady=(4, 8), anchor="w")

        self.shortcuts_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.shortcuts_frame.pack(fill="x")

        self.btn_desktop = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_desktop"),
            command=lambda: self._trigger_shortcut("desktop")
        )
        _style_button(self.btn_desktop, "blue")
        self.btn_desktop.pack(pady=3, fill="x")

        self.btn_start = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_start"),
            command=lambda: self._trigger_shortcut("start")
        )
        _style_button(self.btn_start, "blue")
        self.btn_start.pack(pady=3, fill="x")

        self.btn_taskbar = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_taskbar"),
            command=lambda: self._trigger_shortcut("taskbar")
        )
        _style_button(self.btn_taskbar, "blue")
        self.btn_taskbar.pack(pady=3, fill="x")

        self.btn_pin_start = ctk.CTkButton(
            self.shortcuts_frame,
            text=self.parent_view._tr("btn_shortcut_pin_start"),
            command=lambda: self._trigger_shortcut("start_pin")
        )
        _style_button(self.btn_pin_start, "blue")
        self.btn_pin_start.pack(pady=(3, 0), fill="x")

        self.footer_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=_get_color_tuple("bg_panel"),
            border_width=1,
            border_color=_get_color_tuple("border_subtle"),
            corner_radius=16,
            height=58
        )
        self.footer_frame.pack(fill="x", padx=18, pady=(0, 16), side="bottom")
        self.footer_frame.pack_propagate(False)

        self.btn_close = ctk.CTkButton(
            self.footer_frame,
            text=self.parent_view._tr("btn_ok"),
            command=self._on_ok,
            width=126,
            height=36
        )
        _style_button(self.btn_close, "green")
        self.btn_close.pack(pady=10)

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
                corner_radius=12,
                border_width=1,
                font=("Segoe UI", 11, "bold"),
                fg_color=blue["bg"] if is_selected else _get_color_tuple("bg_dialog"),
                hover_color=blue["hover"] if is_selected else neutral["hover"],
                border_color=blue["border"] if is_selected else _get_color_tuple("border_subtle"),
                text_color=blue["text"] if is_selected else _get_color_tuple("text")
            )

    def refresh_texts(self):
        try:
            self.title(self.parent_view._tr("dlg_settings_title"))
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
        self.btn_close.configure(text=self.parent_view._tr("btn_ok"))
        self._apply_format_button_styles()

    def load_state(self, current_extension: str, current_exe_path: str, on_save_callback=None, on_shortcut_callback=None):
        self.selected_extension = current_extension
        self.current_exe_path = current_exe_path or ""
        self.on_save_callback = on_save_callback
        self.on_shortcut_callback = on_shortcut_callback
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

    def _on_ok(self):
        final_ext = self.fmt_var.get()
        final_path = self.entry_exe.get().strip().replace('"', '')
        self.result = (final_ext, final_path)
        if self.on_save_callback:
            self.on_save_callback(final_ext, final_path)
        self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, current_extension, current_exe_path, on_save_callback, on_shortcut_callback):
        dialog = None
        try:
            dialog = cls(parent, current_extension, current_exe_path, on_save_callback, on_shortcut_callback)
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


