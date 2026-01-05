import customtkinter as ctk

from .base import BaseDialog, COLORS

class ChoiceDialog(BaseDialog):
    def __init__(self, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        super().__init__(parent, title)
        self.option1_value, self.option2_value = option1_value, option2_value
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, font=("Segoe UI", 13)).pack(fill="x", pady=(0, 20))
        ctk.CTkButton(main_frame, text=option1_text, width=220, command=self._on_option1,
                        fg_color=COLORS['button']['blue'], hover_color=COLORS['button_hover']['blue_h']).pack(pady=5)
        ctk.CTkButton(main_frame, text=option2_text, width=220, command=self._on_option2,
                        fg_color=COLORS['button']['blue'], hover_color=COLORS['button_hover']['blue_h']).pack(pady=5)

    def _on_option1(self): self.result = self.option1_value; super()._on_ok()

    def _on_option2(self): self.result = self.option2_value; super()._on_ok()

    @classmethod
    def ask(cls, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        dialog = cls(parent, title, message, option1_text, option2_text, option1_value, option2_value)
        parent.wait_window(dialog)
        return dialog.result
