import customtkinter as ctk
from tkinter import TclError

class CustomTooltip:

    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.show_id = None
        self.hide_id = None

        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)

    def on_enter(self, event=None):
        if self.hide_id:
            self.widget.after_cancel(self.hide_id)
            self.hide_id = None
        self.show_id = self.widget.after(500, self.show_tooltip)

    def on_leave(self, event=None):
        if self.show_id:
            self.widget.after_cancel(self.show_id)
            self.show_id = None
        self.hide_tooltip()

    def show_tooltip(self, event=None):
        if self.tooltip_window is not None:
            return

        root_window = self.widget.winfo_toplevel()
        self.tooltip_window = ctk.CTkToplevel(root_window)
        self.tooltip_window.wm_overrideredirect(True)

        x = self.widget.winfo_pointerx() + 15
        y = self.widget.winfo_pointery() + 10
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes("-topmost", True)
        self.tooltip_window.attributes("-alpha", 0)

        transparent_color = '#E532F1'
        self.tooltip_window.configure(fg_color=transparent_color)
        self.tooltip_window.wm_attributes("-transparentcolor", transparent_color)

        current_theme = ctk.get_appearance_mode()
        if current_theme == "Dark":
            bg_color, text_color = "#323232", "#D3D3D3"
        else:
            bg_color, text_color = "#F5F5F5", "#2E2E2E"

        frame = ctk.CTkFrame(self.tooltip_window, fg_color=bg_color, border_width=0, corner_radius=14)
        frame.pack()

        label = ctk.CTkLabel(frame, text=self.text, font=("Segoe UI", 9, "normal"),
                             text_color=text_color, wraplength=220, justify="center")
        label.pack(padx=10, pady=5)

        self.fade_in()

    def hide_tooltip(self):
        if self.tooltip_window is not None:
            self.fade_out()

    def fade_in(self):
        if not self.tooltip_window or not self.tooltip_window.winfo_exists():
            return
        alpha = self.tooltip_window.attributes("-alpha")
        if alpha < 0.95:
            alpha = min(alpha + 0.1, 0.95)
            self.tooltip_window.attributes("-alpha", alpha)
            self.hide_id = self.tooltip_window.after(15, self.fade_in)

    def fade_out(self):
        if not self.tooltip_window or not self.tooltip_window.winfo_exists():
            self.tooltip_window = None
            return

        alpha = self.tooltip_window.attributes("-alpha")
        if alpha > 0:
            alpha = max(alpha - 0.15, 0.0)
            self.tooltip_window.attributes("-alpha", alpha)
            self.hide_id = self.tooltip_window.after(15, self.fade_out)
        else:
            if self.tooltip_window and self.tooltip_window.winfo_exists():
                try:
                    self.tooltip_window.destroy()
                except (TclError, Exception):
                    pass
            self.tooltip_window = None
