
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
        # Check if parent window exists before creating dialog
        try:
            if parent is None or not parent.winfo_exists():
                raise tk.TclError("Parent window does not exist")
        except tk.TclError:
            # Parent has been destroyed, cannot create dialog
            raise tk.TclError("Parent window does not exist")
        
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
        """Centra el diálogo sobre su ventana padre; si todavía no hay tamaño, centra en pantalla."""
        try:
            self.update_idletasks()
        except Exception:
            pass

        # Tamaño del diálogo (usa reqwidth/reqheight como fallback)
        try:
            w = self.winfo_width()
            h = self.winfo_height()
        except Exception:
            w, h = 400, 250

        try:
            req_w = self.winfo_reqwidth()
            req_h = self.winfo_reqheight()
            if w <= 1:
                w = req_w
            if h <= 1:
                h = req_h
        except Exception:
            pass

        # Intentar centrar sobre el parent, si está "realizado".
        x = y = None
        try:
            parent = self.master
            if parent is not None and parent.winfo_exists():
                parent.update_idletasks()
                pw = parent.winfo_width()
                ph = parent.winfo_height()
                px = parent.winfo_rootx()
                py = parent.winfo_rooty()

                if pw > 50 and ph > 50:
                    x = px + (pw // 2) - (w // 2)
                    y = py + (ph // 2) - (h // 2)
        except Exception:
            x = y = None

        # Fallback: centrar en pantalla
        if x is None or y is None:
            try:
                sw = self.winfo_screenwidth()
                sh = self.winfo_screenheight()
                x = (sw // 2) - (w // 2)
                y = (sh // 2) - (h // 2)
            except Exception:
                x, y = 100, 100

        # Mantener el diálogo dentro de los límites de la pantalla
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            margin = 10
            x = max(margin, min(x, sw - w - margin))
            y = max(margin, min(y, sh - h - margin))
        except Exception:
            pass

        self.geometry(f"+{x}+{y}")

        # Continuar con la animación de entrada (fade-in) si aplica
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
        self._cancel_all_afters()

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
        self._cancel_all_afters()
        if not self.winfo_exists():
            return
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

    def destroy(self):
        """Destruir de forma segura evitando TclError por callbacks pendientes."""
        self._cancel_all_afters()
        try:
            if self.winfo_exists():
                super().destroy()
        except tk.TclError:
            pass

    def _cancel_all_afters(self):
        """Cancela todos los callbacks `after` pendientes para evitar bad window path."""
        try:
            for after_id in list(self.after_info()):
                try:
                    self.after_cancel(after_id)
                except Exception:
                    pass
        except Exception:
            pass

    def _on_ok(self, event=None):
        self._close_with_fade_out()

    def _on_cancel(self, event=None):
        self.result = None
        self._close_with_fade_out()