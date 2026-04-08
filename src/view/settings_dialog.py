import customtkinter as ctk
from app_meta import APP_EXECUTABLE_NAME
from view.dialogs import BaseDialog, _style_button, _get_color_tuple, _style_entry, _style_option_menu


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

        self.geometry("450x500")

        self.main_frame = self._create_card_frame()

        self.lbl_report_format = ctk.CTkLabel(
            self.main_frame,
            text=self.parent_view._tr("lbl_report_format"),
            font=("Segoe UI", 12, "bold"),
            text_color=_get_color_tuple("text")
        )
        self.lbl_report_format.pack(pady=(20, 5), padx=20, anchor="w")

        self.fmt_var = ctk.StringVar(value=self.selected_extension)
        self.opt_format = ctk.CTkOptionMenu(
            self.main_frame,
            values=[".txt", ".md"],
            command=self._on_format_change,
            variable=self.fmt_var,
            width=150,
            height=28,
            font=("Segoe UI", 12),
            fg_color=_get_color_tuple("card_border"),
            button_color=_get_color_tuple("card_border"),
            text_color=_get_color_tuple("text")
        )
        _style_option_menu(self.opt_format)
        self.opt_format.pack(padx=20, pady=(0, 10), anchor="w")

        self.lbl_exe_path = ctk.CTkLabel(
            self.main_frame,
            text=self.parent_view._tr("lbl_exe_path", APP_EXECUTABLE_NAME),
            font=("Segoe UI", 12, "bold"),
            text_color=_get_color_tuple("text")
        )
        self.lbl_exe_path.pack(pady=(10, 2), padx=20, anchor="w")

        self.lbl_exe_example = ctk.CTkLabel(
            self.main_frame,
            text=self.parent_view._tr("lbl_exe_example", APP_EXECUTABLE_NAME),
            font=("Segoe UI", 10, "normal"),
            text_color=_get_color_tuple("text_secondary")
        )
        self.lbl_exe_example.pack(pady=(0, 5), padx=20, anchor="w")

        self.entry_exe = ctk.CTkEntry(
            self.main_frame,
            placeholder_text=self.parent_view._tr("ph_exe_path")
        )
        _style_entry(self.entry_exe)
        self.entry_exe.pack(padx=20, pady=(0, 15), fill="x")
        self.entry_exe.insert(0, self.current_exe_path)

        ctk.CTkFrame(self.main_frame, height=1, fg_color=_get_color_tuple("separator_line")).pack(fill="x", padx=20,
                                                                                                  pady=5)

        self.lbl_system_shortcuts = ctk.CTkLabel(
            self.main_frame,
            text=self.parent_view._tr("lbl_system_shortcuts"),
            font=("Segoe UI", 12, "bold"),
            text_color=_get_color_tuple("text")
        )
        self.lbl_system_shortcuts.pack(pady=(15, 10), padx=20, anchor="w")

        self.btn_desktop = ctk.CTkButton(
            self.main_frame,
            text=self.parent_view._tr("btn_shortcut_desktop"),
            command=lambda: self._trigger_shortcut("desktop")
        )
        _style_button(self.btn_desktop, "blue")
        self.btn_desktop.pack(padx=20, pady=4, fill="x")

        self.btn_start = ctk.CTkButton(
            self.main_frame,
            text=self.parent_view._tr("btn_shortcut_start"),
            command=lambda: self._trigger_shortcut("start")
        )
        _style_button(self.btn_start, "blue")
        self.btn_start.pack(padx=20, pady=4, fill="x")

        self.btn_taskbar = ctk.CTkButton(
            self.main_frame,
            text=self.parent_view._tr("btn_shortcut_taskbar"),
            command=lambda: self._trigger_shortcut("taskbar")
        )
        _style_button(self.btn_taskbar, "blue")
        self.btn_taskbar.pack(padx=20, pady=4, fill="x")

        self.btn_pin_start = ctk.CTkButton(
            self.main_frame,
            text=self.parent_view._tr("btn_shortcut_pin_start"),
            command=lambda: self._trigger_shortcut("start_pin")
        )
        _style_button(self.btn_pin_start, "blue")
        self.btn_pin_start.pack(padx=20, pady=4, fill="x")

        # Espaciador flexible
        ctk.CTkFrame(self.main_frame, fg_color="transparent").pack(expand=True, fill="both")

        self.btn_close = ctk.CTkButton(
            self.main_frame,
            text=self.parent_view._tr("btn_ok"),
            command=self._on_ok
        )
        _style_button(self.btn_close, "green")
        self.btn_close.pack(pady=20)

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

    def load_state(self, current_extension: str, current_exe_path: str, on_save_callback=None, on_shortcut_callback=None):
        self.selected_extension = current_extension
        self.current_exe_path = current_exe_path or ""
        self.on_save_callback = on_save_callback
        self.on_shortcut_callback = on_shortcut_callback
        self.result = None
        self.fmt_var.set(self.selected_extension)
        self.entry_exe.delete(0, "end")
        self.entry_exe.insert(0, self.current_exe_path)
        self.refresh_texts()

    def present(self):
        super().present()
        try:
            self.entry_exe.focus_set()
        except Exception:
            pass

    def _on_format_change(self, value):
        self.selected_extension = value

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