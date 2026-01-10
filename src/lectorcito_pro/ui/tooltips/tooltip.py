"""
Tooltips robustos para CustomTkinter.

Problemas que arregla (especialmente en Windows + Python 3.1x):
- Evita crear/destrozar CTkToplevel constantemente (eso dispara errores tipo:
  "bad window path name", "can't delete Tcl command", "application has been destroyed").
- Garantiza que solo haya UN tooltip visible a la vez.
- Cancela correctamente los callbacks de `after` cuando el mouse sale o cuando la app se cierra.
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional

import customtkinter as ctk

from ..theme.palette import COLORS


class _SharedTooltipWindow:
    """Una única ventana tooltip compartida para toda la app."""
    def __init__(self) -> None:
        self._root: Optional[tk.Misc] = None
        self._win: Optional[tk.Toplevel] = None
        self._frame: Optional[tk.Frame] = None
        self._label: Optional[tk.Label] = None

    def _theme_colors(self) -> tuple[str, str, str]:
        # En esta app el "left_bar" contrasta con el background del tema:
        # - Tema Light => left_bar oscuro => texto blanco
        # - Tema Dark  => left_bar claro  => texto negro
        mode = ctk.get_appearance_mode()  # "Light" / "Dark"
        if mode == "Dark":
            bg = COLORS["dark"]["left_bar"]      # claro
            fg = COLORS["light"]["text"]         # negro
            border = COLORS["dark"]["bg"]        # oscuro
        else:
            bg = COLORS["light"]["left_bar"]     # oscuro
            fg = COLORS["dark"]["text"]          # blanco
            border = COLORS["light"]["bg"]       # claro
        return bg, fg, border

    def _ensure(self, root: tk.Misc) -> None:
        # Si no existe o cambió el root, recreamos.
        try:
            if self._win is not None and self._win.winfo_exists():
                if self._root is root:
                    return
                self._win.destroy()
        except Exception:
            pass

        self._root = root
        self._win = tk.Toplevel(root)
        self._win.withdraw()
        self._win.overrideredirect(True)
        try:
            self._win.attributes("-topmost", True)
        except Exception:
            pass

        bg, fg, border = self._theme_colors()

        self._frame = tk.Frame(
            self._win,
            bg=bg,
            highlightthickness=1,
            highlightbackground=border,
            highlightcolor=border,
            bd=0,
        )
        self._frame.pack(fill="both", expand=True)

        self._label = tk.Label(
            self._frame,
            text="",
            bg=bg,
            fg=fg,
            justify="left",
            font=("Segoe UI", 9),
            wraplength=260,
        )
        self._label.pack(padx=8, pady=5)

    def show(self, widget: tk.Widget, text: str) -> None:
        # Si la app ya se destruyó, no hacemos nada.
        try:
            if not widget.winfo_exists():
                return
        except Exception:
            return

        try:
            root = widget.winfo_toplevel()
            if not root.winfo_exists():
                return
        except Exception:
            return

        self._ensure(root)

        if self._win is None or self._label is None or self._frame is None:
            return

        bg, fg, border = self._theme_colors()
        try:
            self._frame.configure(bg=bg, highlightbackground=border, highlightcolor=border)
            self._label.configure(text=text, bg=bg, fg=fg)
        except Exception:
            return

        # Posición: debajo del widget (con pequeño offset)
        try:
            x = widget.winfo_rootx() + 18
            y = widget.winfo_rooty() + widget.winfo_height() + 10
        except Exception:
            x, y = 100, 100

        # Ajustar a la pantalla
        try:
            self._win.update_idletasks()
            w = self._win.winfo_reqwidth()
            h = self._win.winfo_reqheight()
            sw = self._win.winfo_screenwidth()
            sh = self._win.winfo_screenheight()
            margin = 10
            x = max(margin, min(x, sw - w - margin))
            y = max(margin, min(y, sh - h - margin))
        except Exception:
            pass

        try:
            self._win.geometry(f"+{x}+{y}")
            self._win.deiconify()
            self._win.lift()
        except Exception:
            pass

    def hide(self) -> None:
        try:
            if self._win is not None and self._win.winfo_exists():
                self._win.withdraw()
        except Exception:
            pass

    def destroy(self) -> None:
        try:
            if self._win is not None and self._win.winfo_exists():
                self._win.destroy()
        except Exception:
            pass
        self._win = None
        self._root = None
        self._frame = None
        self._label = None


class CustomTooltip:
    """
    Tooltip para asociar a un widget.

    - Usa UNA sola ventana compartida (_SharedTooltipWindow).
    - Solo muestra 1 tooltip a la vez.
    """
    _shared = _SharedTooltipWindow()
    _active: Optional["CustomTooltip"] = None

    def __init__(self, widget: tk.Widget, text: str, delay: int = 500) -> None:
        self.widget = widget
        self.text = text
        self.delay = delay
        self._after_id: Optional[str] = None
        self._disposed = False

        # add="+" para no pisar otros binds
        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<ButtonPress>", self._on_leave, add="+")
        self.widget.bind("<Destroy>", self._on_destroy, add="+")

    def _cancel_scheduled(self) -> None:
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _on_enter(self, _event=None) -> None:
        if self._disposed:
            return
        self._cancel_scheduled()
        try:
            self._after_id = self.widget.after(self.delay, self.show_tooltip)
        except Exception:
            self._after_id = None

    def _on_leave(self, _event=None) -> None:
        self.hide_tooltip()

    def _on_destroy(self, _event=None) -> None:
        self.cleanup()

    def show_tooltip(self) -> None:
        if self._disposed:
            return

        try:
            if not self.widget.winfo_exists():
                return
        except Exception:
            return

        # Cerrar tooltip previo
        prev = CustomTooltip._active
        if prev is not None and prev is not self:
            prev.hide_tooltip()

        CustomTooltip._active = self
        CustomTooltip._shared.show(self.widget, self.text)

    def hide_tooltip(self) -> None:
        self._cancel_scheduled()
        if CustomTooltip._active is self:
            CustomTooltip._active = None
        CustomTooltip._shared.hide()

    def cleanup(self) -> None:
        if self._disposed:
            return
        self._disposed = True
        self.hide_tooltip()
