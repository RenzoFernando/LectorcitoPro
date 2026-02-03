import customtkinter as ctk
from view.dialogs import BaseDialog, _style_button, _get_color_tuple


# =============================================================================
# DIALOGO DE CONFIGURACION GENERAL
# =============================================================================

class SettingsDialog(BaseDialog):
    def __init__(self, parent, current_extension: str, current_exe_path: str, on_save_callback=None,
                 on_shortcut_callback=None):
        title = parent._tr("dlg_settings_title") if hasattr(parent, "_tr") else "Ajustes"
        super().__init__(parent, title)

        self.withdraw()
        self.attributes("-alpha", 0.0)

        self.parent_view = parent
        self.selected_extension = current_extension
        self.current_exe_path = current_exe_path or ""
        self.on_save_callback = on_save_callback
        self.on_shortcut_callback = on_shortcut_callback
        self.result = None

        self.geometry("450x500")

        self.after(750, self._step_1_build_frame)

    def _step_1_build_frame(self):
        self.main_frame = self._create_card_frame()
        self.after(10, self._step_2_add_format_section)

    def _step_2_add_format_section(self):
        ctk.CTkLabel(
            self.main_frame,
            text=self.parent_view._tr("lbl_report_format"),
            font=("Segoe UI", 12, "bold"),
            text_color=_get_color_tuple("text")
        ).pack(pady=(20, 5), padx=20, anchor="w")

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
        self.opt_format.pack(padx=20, pady=(0, 10), anchor="w")

        self.after(20, self._step_2b_add_path_section)

    def _step_2b_add_path_section(self):
        ctk.CTkLabel(
            self.main_frame,
            text=self.parent_view._tr("lbl_exe_path"),
            font=("Segoe UI", 12, "bold"),
            text_color=_get_color_tuple("text")
        ).pack(pady=(10, 2), padx=20, anchor="w")

        ctk.CTkLabel(
            self.main_frame,
            text=self.parent_view._tr("lbl_exe_example"),
            font=("Segoe UI", 10, "normal"),
            text_color=_get_color_tuple("text_secondary")
        ).pack(pady=(0, 5), padx=20, anchor="w")

        self.entry_exe = ctk.CTkEntry(
            self.main_frame,
            placeholder_text=self.parent_view._tr("ph_exe_path")
        )
        self.entry_exe.pack(padx=20, pady=(0, 15), fill="x")
        self.entry_exe.insert(0, self.current_exe_path)

        ctk.CTkFrame(self.main_frame, height=1, fg_color=_get_color_tuple("separator_line")).pack(fill="x", padx=20,
                                                                                                  pady=5)
        self.after(20, self._step_3_add_shortcuts_header)

    def _step_3_add_shortcuts_header(self):
        ctk.CTkLabel(
            self.main_frame,
            text=self.parent_view._tr("lbl_system_shortcuts"),
            font=("Segoe UI", 12, "bold"),
            text_color=_get_color_tuple("text")
        ).pack(pady=(15, 10), padx=20, anchor="w")

        self.after(50, self._step_4_add_button_desktop)

    def _step_4_add_button_desktop(self):
        self.btn_desktop = ctk.CTkButton(
            self.main_frame,
            text=self.parent_view._tr("btn_shortcut_desktop"),
            command=lambda: self._trigger_shortcut("desktop")
        )
        _style_button(self.btn_desktop, "blue")
        self.btn_desktop.pack(padx=20, pady=4, fill="x")

        self.after(50, self._step_5_add_button_start)

    def _step_5_add_button_start(self):
        self.btn_start = ctk.CTkButton(
            self.main_frame,
            text=self.parent_view._tr("btn_shortcut_start"),
            command=lambda: self._trigger_shortcut("start")
        )
        _style_button(self.btn_start, "blue")
        self.btn_start.pack(padx=20, pady=4, fill="x")

        self.after(50, self._step_6_add_button_taskbar)

    def _step_6_add_button_taskbar(self):
        self.btn_taskbar = ctk.CTkButton(
            self.main_frame,
            text=self.parent_view._tr("btn_shortcut_taskbar"),
            command=lambda: self._trigger_shortcut("taskbar")
        )
        _style_button(self.btn_taskbar, "blue")
        self.btn_taskbar.pack(padx=20, pady=4, fill="x")

        self.after(50, self._step_7_add_button_pin_start)

    def _step_7_add_button_pin_start(self):
        self.btn_pin_start = ctk.CTkButton(
            self.main_frame,
            text=self.parent_view._tr("btn_shortcut_pin_start"),
            command=lambda: self._trigger_shortcut("start_pin")
        )
        _style_button(self.btn_pin_start, "blue")
        self.btn_pin_start.pack(padx=20, pady=4, fill="x")

        self.after(50, self._step_8_finalize)

    def _step_8_finalize(self):
        # Espaciador flexible
        ctk.CTkFrame(self.main_frame, fg_color="transparent").pack(expand=True, fill="both")

        self.btn_close = ctk.CTkButton(
            self.main_frame,
            text=self.parent_view._tr("btn_ok"),
            command=self._on_ok
        )
        _style_button(self.btn_close, "green")
        self.btn_close.pack(pady=20)

        self.deiconify()
        self._animate_fade_in()

        # Aseguramos el foco y el bloqueo modal
        self.lift()
        self.focus_force()
        try:
            self.grab_set()
        except Exception:
            pass

    def _animate_fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.1
            self.attributes("-alpha", alpha)
            self.after(45, self._animate_fade_in)
        else:
            self.attributes("-alpha", 1.0)
            try:
                self.grab_set()
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
        dialog = cls(parent, current_extension, current_exe_path, on_save_callback, on_shortcut_callback)
        parent.wait_window(dialog)
        return dialog.result