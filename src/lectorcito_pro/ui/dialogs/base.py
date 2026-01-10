from __future__ import annotations

import customtkinter as ctk
import os
import tkinter as tk

from ..theme.palette import COLORS


class BaseDialog(ctk.CTkToplevel):
    """Base para diálogos con animación fade-in/fade-out.

    Fix v6:
    - Evita `TclError: can't delete Tcl command` al destruir dentro de callbacks `after`
      usando `after_idle` y un flag de cierre.
    """

    def __init__(self, parent, title: str):
        super().__init__(parent)

        self.transient(parent)
        self.title(title)
        self.resizable(False, False)
        self.attributes("-alpha", 0.0)

        self._closing = False
        self._fade_job: str | None = None

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
        try:
            self.grab_set()
            self.focus_set()
        except Exception:
            pass

        self.after(100, self._center_and_fade_in)

    def _center_and_fade_in(self):
        # Centrar diálogo sobre el parent
        try:
            self.update_idletasks()
            parent = self.master
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = px + (pw - w) // 2
            y = py + (ph - h) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        self._fade_in_step()

    def _fade_in_step(self):
        if not self.winfo_exists():
            return
        try:
            alpha = float(self.attributes("-alpha"))
        except Exception:
            alpha = 0.0

        if alpha < 1.0 and not self._closing:
            alpha = min(alpha + 0.1, 1.0)
            try:
                self.attributes("-alpha", alpha)
            except Exception:
                pass
            self.after(15, self._fade_in_step)

    def _close_with_fade_out(self, event=None):
        if self._closing:
            return
        self._closing = True

        try:
            self.grab_release()
        except Exception:
            pass

        self._fade_out_step()

    def _fade_out_step(self):
        if not self.winfo_exists():
            return

        try:
            alpha = float(self.attributes("-alpha"))
        except Exception:
            alpha = 0.0

        if alpha > 0.0:
            alpha = max(alpha - 0.1, 0.0)
            try:
                self.attributes("-alpha", alpha)
            except Exception:
                pass
            self._fade_job = self.after(15, self._fade_out_step)
        else:
            # Destruir fuera del callback activo
            try:
                self.after_idle(self._safe_destroy)
            except Exception:
                self._safe_destroy()

    def _safe_destroy(self):
        try:
            if self._fade_job:
                try:
                    self.after_cancel(self._fade_job)
                except Exception:
                    pass
                self._fade_job = None
        except Exception:
            pass

        try:
            super().destroy()
        except tk.TclError:
            # Evitar crash por doble-destroy / callbacks Tcl.
            pass

    def _on_ok(self, event=None):
        self._close_with_fade_out()

    def _on_cancel(self, event=None):
        self.result = None
        self._close_with_fade_out()
