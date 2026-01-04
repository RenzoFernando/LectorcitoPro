import os

import customtkinter as ctk

from core.constants import COLORS


class BaseDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.resizable(False, False)
        self.attributes("-alpha", 0.0)
        self._tr = getattr(parent, "_tr", lambda key, *args: key)

        def _set_icon():
            try:
                if hasattr(parent, "_icon_path") and parent._icon_path and os.path.exists(parent._icon_path):
                    self.iconbitmap(parent._icon_path)
            except Exception as e:
                print(f"Error al establecer el icono de la sub-ventana: {e}")

        self.after(200, _set_icon)
        self.result = None
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)
        self.bind("<Escape>", self._close_with_fade_out)
        self.after(100, self._center_and_fade_in)

    def _center_and_fade_in(self):
        try:
            self.grab_set()
            self._center_window()
            self._fade_in()
        except Exception:
            pass

    def _center_window(self):
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.geometry(f"+{x}+{y}")

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1:
            alpha = min(alpha + 0.1, 1.0)
            self.attributes("-alpha", alpha)
            self.after(15, self._fade_in)

    def _close_with_fade_out(self, event=None):
        self.grab_release()
        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha = max(alpha - 0.1, 0.0)
            self.attributes("-alpha", alpha)
            self.after(15, self._close_with_fade_out)
        else:
            self.destroy()

    def _on_ok(self, event=None):
        self._close_with_fade_out()

    def _on_cancel(self, event=None):
        self.result = None
        self._close_with_fade_out()


class MessageDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, justify="center", font=("Segoe UI", 13)).pack(
            fill="x", pady=(0, 20)
        )
        ok_button = ctk.CTkButton(
            main_frame,
            text=self._tr("btn_ok"),
            width=100,
            command=self._on_ok,
            fg_color=COLORS["button"]["blue"],
            hover_color=COLORS["button_hover"]["blue_h"],
        )
        ok_button.pack(pady=(0, 10))
        ok_button.focus_set()
        self.bind("<Return>", self._on_ok)

    def _on_ok(self, event=None):
        self.result = True
        super()._on_ok(event)


class ConfirmDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        self.result = False
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, justify="center", font=("Segoe UI", 13)).pack(
            fill="x", pady=(0, 20)
        )
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()

        ctk.CTkButton(
            button_frame,
            text=self._tr("btn_yes"),
            width=100,
            command=self._on_yes,
            fg_color=COLORS["button"]["green"],
            hover_color=COLORS["button_hover"]["green_h"],
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            button_frame,
            text=self._tr("btn_no"),
            width=100,
            command=self._on_no,
            fg_color=COLORS["button"]["red"],
            hover_color=COLORS["button_hover"]["red_h"],
        ).pack(side="left", padx=10)

    def _on_yes(self, event=None):
        self.result = True
        self._close_with_fade_out()

    def _on_no(self, event=None):
        self.result = False
        self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, title, message):
        dialog = cls(parent, title, message)
        parent.wait_window(dialog)
        return dialog.result


class ChoiceDialog(BaseDialog):
    def __init__(self, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        super().__init__(parent, title)
        self.option1_value, self.option2_value = option1_value, option2_value
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, font=("Segoe UI", 13)).pack(fill="x", pady=(0, 20))
        ctk.CTkButton(
            main_frame,
            text=option1_text,
            width=220,
            command=self._on_option1,
            fg_color=COLORS["button"]["blue"],
            hover_color=COLORS["button_hover"]["blue_h"],
        ).pack(pady=5)
        ctk.CTkButton(
            main_frame,
            text=option2_text,
            width=220,
            command=self._on_option2,
            fg_color=COLORS["button"]["blue"],
            hover_color=COLORS["button_hover"]["blue_h"],
        ).pack(pady=5)

    def _on_option1(self):
        self.result = self.option1_value
        super()._on_ok()

    def _on_option2(self):
        self.result = self.option2_value
        super()._on_ok()

    @classmethod
    def ask(cls, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        dialog = cls(parent, title, message, option1_text, option2_text, option1_value, option2_value)
        parent.wait_window(dialog)
        return dialog.result
