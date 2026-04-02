import sys
import customtkinter as ctk
from tkinter import TclError

TOOLTIP_AUTOHIDE_SECONDS = 2.5

# =============================================================================
# DETECCION DE PANTALLA
# =============================================================================

def _is_windows() -> bool:
    return sys.platform.startswith("win")


def _get_monitor_workarea_for_point(x: int, y: int, widget):
    # Intento obtener el area de trabajo real en Windows (excluyendo barra de tareas)
    if _is_windows():
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32

            class POINT(ctypes.Structure):
                _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", wintypes.LONG),
                    ("top", wintypes.LONG),
                    ("right", wintypes.LONG),
                    ("bottom", wintypes.LONG),
                ]

            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", RECT),
                    ("rcWork", RECT),
                    ("dwFlags", wintypes.DWORD),
                ]

            MONITOR_DEFAULTTONEAREST = 2

            pt = POINT(int(x), int(y))
            hmon = user32.MonitorFromPoint(pt, MONITOR_DEFAULTTONEAREST)
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)

            ok = user32.GetMonitorInfoW(hmon, ctypes.byref(mi))
            if ok:
                r = mi.rcWork
                return int(r.left), int(r.top), int(r.right), int(r.bottom)
        except Exception:
            pass

    # Fallback: Virtual root
    try:
        vx = int(widget.winfo_vrootx())
        vy = int(widget.winfo_vrooty())
        vw = int(widget.winfo_vrootwidth())
        vh = int(widget.winfo_vrootheight())
        return vx, vy, vx + vw, vy + vh
    except Exception:
        pass

    # Fallback final: Screen size basico
    try:
        sw = int(widget.winfo_screenwidth())
        sh = int(widget.winfo_screenheight())
        return 0, 0, sw, sh
    except Exception:
        return 0, 0, 1920, 1080


# =============================================================================
# VENTANA COMPARTIDA DEL TOOLTIP
# =============================================================================

class _SharedTooltipWindow:
    _instance = None

    @classmethod
    def get(cls, root_window):
        if cls._instance is None:
            cls._instance = cls(root_window)
        else:
            try:
                if not cls._instance._window.winfo_exists():
                    cls._instance = cls(root_window)
            except Exception:
                cls._instance = cls(root_window)
        return cls._instance

    def __init__(self, root_window):
        self._root = root_window
        self._owner_widget = None

        self._window = ctk.CTkToplevel(root_window)
        self._window.wm_overrideredirect(True)
        self._window.withdraw()
        self._window.attributes("-topmost", True)

        self._target_alpha = 0.96
        self._fade_after_id = None
        self._visible = False

        self._transparent_color = "#E532F1"
        try:
            self._window.configure(fg_color=self._transparent_color)
            self._window.wm_attributes("-transparentcolor", self._transparent_color)
        except Exception:
            self._transparent_color = None

        self._frame = ctk.CTkFrame(
            self._window,
            corner_radius=12,
            border_width=1,
        )
        self._frame.pack()

        self._label = ctk.CTkLabel(
            self._frame,
            text="",
            font=("Segoe UI", 10, "normal"),
            wraplength=260,
            justify="left",
        )
        self._label.pack(padx=12, pady=8)

        try:
            self._root.bind("<FocusOut>", self._on_root_invalidate, add="+")
            self._root.bind("<Unmap>", self._on_root_invalidate, add="+")
            self._root.bind("<Destroy>", self._on_root_destroy, add="+")
            self._root.bind("<ButtonPress>", self._on_root_invalidate, add="+")
        except Exception:
            pass

    def _safe_exists(self, widget) -> bool:
        try:
            return bool(widget) and widget.winfo_exists()
        except Exception:
            return False

    def _cancel_fade(self):
        if self._fade_after_id and self._safe_exists(self._window):
            try:
                self._window.after_cancel(self._fade_after_id)
            except Exception:
                pass
        self._fade_after_id = None

    def _apply_theme(self):
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            bg = "#1F2328"
            border = "#2B3137"
            text = "#E6EDF3"
        else:
            bg = "#FFFFFF"
            border = "#D0D7DE"
            text = "#24292F"

        try:
            self._frame.configure(fg_color=bg, border_color=border)
            self._label.configure(text_color=text)
        except Exception:
            pass

    def show(self, widget, text: str, placement: str = "auto", gap: int = 10):
        if not widget or not self._safe_exists(widget):
            return

        self._owner_widget = widget
        self._apply_theme()

        try:
            self._label.configure(text=text)
        except Exception:
            return

        try:
            self._window.update_idletasks()
        except Exception:
            pass

        self._reposition(widget, placement=placement, gap=gap)

        try:
            self._window.deiconify()
            self._window.lift()
        except Exception:
            return

        # Animacion Fade In
        self._cancel_fade()
        try:
            self._window.attributes("-alpha", 0.0)
        except Exception:
            pass

        self._visible = True
        self._fade_in_step()

    def hide(self):
        self._owner_widget = None
        if not self._safe_exists(self._window):
            self._visible = False
            return

        self._cancel_fade()
        if not self._visible:
            try:
                self._window.withdraw()
            except Exception:
                pass
            return

        self._fade_out_step()

    def hide_immediate(self):
        self._cancel_fade()
        self._visible = False
        self._owner_widget = None
        if self._safe_exists(self._window):
            try:
                self._window.withdraw()
                self._window.attributes("-alpha", 0.0)
            except Exception:
                pass

    def is_visible(self) -> bool:
        return self._visible and self._safe_exists(self._window)

    def destroy(self):
        self._cancel_fade()
        self._visible = False
        self._owner_widget = None
        if self._safe_exists(self._window):
            try:
                self._window.destroy()
            except Exception:
                pass

    def _on_root_invalidate(self, event=None):
        self.hide_immediate()

    def _on_root_destroy(self, event=None):
        self.destroy()
        if _SharedTooltipWindow._instance is self:
            _SharedTooltipWindow._instance = None

    def _fade_in_step(self):
        if not self._safe_exists(self._window) or not self._visible:
            return
        try:
            a = float(self._window.attributes("-alpha"))
        except Exception:
            return

        if a < self._target_alpha:
            a = min(a + 0.12, self._target_alpha)
            try:
                self._window.attributes("-alpha", a)
            except Exception:
                return
            self._fade_after_id = self._window.after(12, self._fade_in_step)
        else:
            self._fade_after_id = None

    def _fade_out_step(self):
        if not self._safe_exists(self._window):
            self._visible = False
            return

        try:
            a = float(self._window.attributes("-alpha"))
        except Exception:
            try:
                self._window.withdraw()
            except Exception:
                pass
            self._visible = False
            return

        if a > 0.0:
            a = max(a - 0.14, 0.0)
            try:
                self._window.attributes("-alpha", a)
            except Exception:
                pass
            self._fade_after_id = self._window.after(12, self._fade_out_step)
        else:
            try:
                self._window.withdraw()
            except Exception:
                pass
            self._fade_after_id = None
            self._visible = False

    def _reposition(self, widget, placement: str = "auto", gap: int = 10):
        try:
            wx = int(widget.winfo_rootx())
            wy = int(widget.winfo_rooty())
            ww = int(widget.winfo_width())
            wh = int(widget.winfo_height())
        except Exception:
            return

        try:
            tw = max(1, int(self._window.winfo_reqwidth()))
            th = max(1, int(self._window.winfo_reqheight()))
        except Exception:
            tw, th = 240, 40

        cx = wx + ww // 2
        cy = wy + wh // 2

        left, top, right, bottom = _get_monitor_workarea_for_point(cx, cy, widget)
        pad = 8
        gap = int(gap)

        space_right = (right - (wx + ww))
        space_left = (wx - left)
        space_bottom = (bottom - (wy + wh))
        space_top = (wy - top)

        pl = placement.lower().strip() if placement else "auto"
        if pl == "auto":
            if space_right >= tw + gap:
                pl = "right"
            elif space_left >= tw + gap:
                pl = "left"
            elif space_bottom >= th + gap:
                pl = "bottom"
            else:
                pl = "top"

        if pl == "right":
            x = wx + ww + gap
            y = cy - th // 2
        elif pl == "left":
            x = wx - tw - gap
            y = cy - th // 2
        elif pl == "bottom":
            x = cx - tw // 2
            y = wy + wh + gap
        else:
            x = cx - tw // 2
            y = wy - th - gap

        x = max(left + pad, min(x, right - tw - pad))
        y = max(top + pad, min(y, bottom - th - pad))

        try:
            self._window.wm_geometry(f"+{int(x)}+{int(y)}")
        except Exception:
            pass


# =============================================================================
# CLASE WRAPPER (USO PUBLICO)
# =============================================================================

class CustomTooltip:
    _active_tooltip = None

    def __init__(self, widget, text: str, delay: int = 500, placement: str = "auto", gap: int = 10):
        self.widget = widget
        self._text = text or ""
        self.delay = int(delay) if delay is not None else 500

        self.placement = placement
        self.gap = int(gap)

        self._after_id = None
        self._auto_hide_id = None
        self._auto_hide_master = None
        self._destroyed = False

        try:
            self.widget.bind("<Enter>", self._on_enter, add="+")
            self.widget.bind("<Leave>", self._on_leave, add="+")
            self.widget.bind("<ButtonPress>", self._on_leave, add="+")
            self.widget.bind("<Destroy>", self._on_destroy, add="+")
        except Exception:
            pass

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value if value is not None else ""
        if CustomTooltip._active_tooltip is self:
            win = self._get_shared_window()
            if win and win.is_visible():
                win.show(self.widget, self._text, placement=self.placement, gap=self.gap)
                self._schedule_auto_hide()

    def _on_enter(self, event=None):
        if self._destroyed:
            return
        self._cancel_scheduled_show()
        self._schedule_show()

    def _on_leave(self, event=None):
        self.hide_tooltip()

    def _on_destroy(self, event=None):
        self.cleanup()

    def _schedule_show(self):
        if not self._safe_widget():
            return
        try:
            self._after_id = self.widget.after(self.delay, self.show_tooltip)
        except Exception:
            self._after_id = None

    def show_tooltip(self):
        if self._destroyed or not self._safe_widget():
            return
        if not self._pointer_inside_widget():
            return

        prev = CustomTooltip._active_tooltip
        if prev is not None and prev is not self:
            prev.hide_tooltip()

        CustomTooltip._active_tooltip = self

        win = self._get_shared_window()
        if not win:
            return
        win.show(self.widget, self._text, placement=self.placement, gap=self.gap)
        self._schedule_auto_hide()

    def hide_tooltip(self):
        self._cancel_scheduled_show()
        self._cancel_scheduled_auto_hide()

        if CustomTooltip._active_tooltip is self:
            win = self._get_shared_window()
            if win:
                win.hide()
            CustomTooltip._active_tooltip = None

    def cleanup(self):
        if self._destroyed:
            return
        self._destroyed = True
        self.hide_tooltip()
        self._cancel_scheduled_show()

    @classmethod
    def hide_global(cls):
        active = cls._active_tooltip
        if active:
            active._cancel_scheduled_show()
            active._cancel_scheduled_auto_hide()
            win = active._get_shared_window()
            if win:
                win.hide_immediate()
            cls._active_tooltip = None
            return

        shared = _SharedTooltipWindow._instance
        if shared:
            try:
                shared.hide_immediate()
            except Exception:
                pass

    def _cancel_scheduled_show(self):
        if self._after_id and self._safe_widget():
            try:
                self.widget.after_cancel(self._after_id)
            except (TclError, Exception):
                pass
        self._after_id = None

    def _schedule_auto_hide(self):
        try:
            seconds = float(TOOLTIP_AUTOHIDE_SECONDS)
        except Exception:
            seconds = 5.0

        if seconds <= 0:
            return

        self._cancel_scheduled_auto_hide()

        if self._destroyed:
            return

        try:
            ms = max(1, int(seconds * 1000))
            master = None
            try:
                if self._safe_widget():
                    master = self.widget.winfo_toplevel()
            except Exception:
                master = None

            if master is None:
                master = self.widget

            self._auto_hide_master = master
            self._auto_hide_id = master.after(ms, self._on_auto_hide)

        except Exception:
            self._auto_hide_id = None
            self._auto_hide_master = None

    def _cancel_scheduled_auto_hide(self):
        if not self._auto_hide_id:
            self._auto_hide_id = None
            self._auto_hide_master = None
            return

        master = getattr(self, "_auto_hide_master", None) or self.widget
        try:
            master.after_cancel(self._auto_hide_id)
        except (TclError, Exception):
            pass

        self._auto_hide_id = None
        self._auto_hide_master = None

    def _get_shared_window(self):
        root_window = None
        if self._safe_widget():
            try:
                root_window = self.widget.winfo_toplevel()
            except Exception:
                root_window = None

        if root_window is None:
            root_window = getattr(self, "_auto_hide_master", None)

        if not root_window:
            return None

        try:
            return _SharedTooltipWindow.get(root_window)
        except Exception:
            return None

    def _on_auto_hide(self):
        self._auto_hide_id = None
        if CustomTooltip._active_tooltip is self:
            self.hide_tooltip()

    def _safe_widget(self) -> bool:
        try:
            return bool(self.widget) and self.widget.winfo_exists()
        except Exception:
            return False

    def _pointer_inside_widget(self) -> bool:
        try:
            px = self.widget.winfo_pointerx()
            py = self.widget.winfo_pointery()
            x0 = self.widget.winfo_rootx()
            y0 = self.widget.winfo_rooty()
            x1 = x0 + self.widget.winfo_width()
            y1 = y0 + self.widget.winfo_height()
            return x0 <= px <= x1 and y0 <= py <= y1
        except Exception:
            return False

