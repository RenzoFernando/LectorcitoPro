
import customtkinter as ctk

from .base import BaseDialog, COLORS

class MessageDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, justify="center", font=("Segoe UI", 13)).pack(fill="x", pady=(0,20))
        ok_button = ctk.CTkButton(main_frame, text="OK", width=100, command=self._on_ok,
                                    fg_color=COLORS['button']['blue'], hover_color=COLORS['button_hover']['blue_h'])
        ok_button.pack(pady=(0, 10))
        ok_button.focus_set()
        self.bind("<Return>", self._on_ok)

    def _on_ok(self, event=None): self.result = True; super()._on_ok(event)
