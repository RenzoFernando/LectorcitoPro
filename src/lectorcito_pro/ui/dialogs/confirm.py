import customtkinter as ctk

from .base import BaseDialog, COLORS

class ConfirmDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        self.result = False
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, justify="center", font=("Segoe UI", 13)).pack(fill="x", pady=(0,20))
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()

        ctk.CTkButton(button_frame, text="Sí", width=100, command=self._on_yes, fg_color=COLORS['button']['green'],
                        hover_color=COLORS['button_hover']['green_h']).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="No", width=100, command=self._on_no, fg_color=COLORS['button']['red'],
                        hover_color=COLORS['button_hover']['red_h']).pack(side="left", padx=10)

    def _on_yes(self, event=None): self.result = True; self._close_with_fade_out()

    def _on_no(self, event=None): self.result = False; self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, title, message):
        dialog = cls(parent, title, message)
        parent.wait_window(dialog)
        return dialog.result
