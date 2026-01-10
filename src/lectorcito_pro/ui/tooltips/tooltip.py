from __future__ import annotations

import customtkinter as ctk
from tkinter import TclError


class CustomTooltip:
    """Tooltip simple con fade-in/fade-out.

    Fix v6:
    - Método `cleanup()` para cancelar callbacks `after` y cerrar el tooltip de forma segura.
    - Destroy del Toplevel vía `after_idle` para reducir riesgo de TclError en cierres rápidos.
    """

    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.show_id = None
        self.hide_id = None
        self._disposed = False
        self.widget.bind("<Destroy>", self.on_destroy, add="+")

        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)

    def on_enter(self, event=None):
        if self._disposed:
            return
        if self.hide_id:
            try:
                if self.tooltip_window and self.tooltip_window.winfo_exists():
                    self.tooltip_window.after_cancel(self.hide_id)
                else:
                    self.widget.after_cancel(self.hide_id)
            except Exception:
                pass
            self.hide_id = None

        if not self.tooltip_window:
            self.show_id = self.widget.after(300, self.show_tooltip)

    def on_leave(self, event=None):
        if self._disposed:
            return
        if self.show_id:
            try:
                self.widget.after_cancel(self.show_id)
            except Exception:
                pass
            self.show_id = None

        self.hide_tooltip()

    def show_tooltip(self):
        if self._disposed:
            return
        try:
            if not self.widget.winfo_exists():
                return
            root_window = self.widget.winfo_toplevel()
            if not root_window or not root_window.winfo_exists():
                return
            x = self.widget.winfo_rootx() + 25
            y = self.widget.winfo_rooty() + 25
        except Exception:
            return

        try:
            self.tooltip_window = ctk.CTkToplevel(root_window)
        except Exception:
            return
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.attributes("-topmost", True)
        self.tooltip_window.attributes("-alpha", 0.0)

        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.text,
            font=("Segoe UI", 10),
            corner_radius=6,
            fg_color="#333333",
            text_color="#ffffff",
            padx=10,
            pady=5,
        )
        label.pack()

        self.tooltip_window.geometry(f"+{x}+{y}")
        self.fade_in()

    def hide_tooltip(self):
        if self.tooltip_window:
            self.fade_out()

    def fade_in(self):
        if self._disposed:
            return
        if not self.tooltip_window or not self.tooltip_window.winfo_exists():
            return
        alpha = self.tooltip_window.attributes("-alpha")
        if alpha < 0.95:
            alpha = min(alpha + 0.1, 0.95)
            self.tooltip_window.attributes("-alpha", alpha)
            self.hide_id = self.tooltip_window.after(15, self.fade_in)

    def fade_out(self):
        if self._disposed:
            self.tooltip_window = None
            return
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
                    self._cancel_afters(self.tooltip_window)
                    self.tooltip_window.after_idle(self.tooltip_window.destroy)
                except Exception:
                    try:
                        self._cancel_afters(self.tooltip_window)
                        self.tooltip_window.destroy()
                    except (TclError, Exception):
                        pass
            self.tooltip_window = None

    def cleanup(self):
        """Cancela callbacks y cierra el tooltip inmediatamente."""
        if self._disposed and not self.tooltip_window:
            return
        if self.show_id:
            try:
                self.widget.after_cancel(self.show_id)
            except Exception:
                pass
            self.show_id = None

        if self.hide_id:
            try:
                self.widget.after_cancel(self.hide_id)
            except Exception:
                pass
            self.hide_id = None

        if self.tooltip_window and self.tooltip_window.winfo_exists():
            try:
                self._cancel_afters(self.tooltip_window)
                self.tooltip_window.after_idle(self.tooltip_window.destroy)
            except Exception:
                try:
                    self._cancel_afters(self.tooltip_window)
                    self.tooltip_window.destroy()
                except Exception:
                    pass
        self.tooltip_window = None

    def on_destroy(self, event=None):
        """Handler para destrucción del widget base."""
        self._disposed = True
        self.cleanup()

    def _cancel_afters(self, window):
        try:
            for after_id in list(window.after_info()):
                try:
                    window.after_cancel(after_id)
                except Exception:
                    pass
        except Exception:
            pass
