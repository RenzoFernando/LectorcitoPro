# src/view/gradient_progress.py
from __future__ import annotations

import customtkinter as ctk
from tkinter import Canvas


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lerp_color(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    r = int(_lerp(r1, r2, t))
    g = int(_lerp(g1, g2, t))
    b = int(_lerp(b1, b2, t))
    return _rgb_to_hex((r, g, b))


def gradient_color_at(t: float) -> str:
    """
    Gradiente continuo:
    rojo -> naranja -> ámbar -> lima -> verde
    (colores ajustados a la paleta de la app)
    """
    stops = [
        # Paleta de la app (mismo rojo/verde que botones) + tonos intermedios coherentes
        (0.00, "#D03B3D"),  # rojo (app)
        (0.30, "#D06A3B"),  # rojo-naranja
        (0.55, "#D0A33B"),  # ámbar
        (0.78, "#A8D03B"),  # lima
        (1.00, "#3BD056"),  # verde (app)
    ]
    t = max(0.0, min(1.0, float(t)))

    for i in range(len(stops) - 1):
        p1, c1 = stops[i]
        p2, c2 = stops[i + 1]
        if p1 <= t <= p2:
            local = (t - p1) / max(1e-9, (p2 - p1))
            return _lerp_color(c1, c2, local)

    return stops[-1][1]


def rounded_rect_points(x1: int, y1: int, x2: int, y2: int, r: int) -> list[int]:
    r = max(0, min(r, (x2 - x1) // 2, (y2 - y1) // 2))
    pts = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1
    ]
    return pts


class GradientProgressBar(ctk.CTkFrame):
    """
    Barra custom:
    - track visible
    - fill con degradado
    - sin “puntico”
    - modo indeterminate opcional
    """
    def __init__(self, parent, height: int = 12, corner_radius: int = 8):
        super().__init__(parent, fg_color="transparent")
        self._h = height
        self._r = corner_radius

        self._value = 0.0  # 0..1
        self._mode = "determinate"  # determinate | indeterminate
        self._ind_phase = 0.0
        self._ind_after_id = None

        self._track_color = "#C9CDD1"
        self._border_color = "#B6BAC0"

        self._canvas = Canvas(self, height=self._h, highlightthickness=0, bd=0, relief="flat")
        self._canvas.pack(fill="both", expand=True)

        self.bind("<Configure>", lambda e: self._redraw())

    def set_colors(self, *, track: str, border: str):
        self._track_color = track
        self._border_color = border
        self._redraw()

    def set(self, value: float):
        self._value = max(0.0, min(1.0, float(value)))
        self._redraw()

    def start_indeterminate(self):
        if self._mode == "indeterminate":
            return
        self._mode = "indeterminate"
        self._ind_phase = 0.0
        self._tick_indeterminate()

    def stop_indeterminate(self):
        if self._mode != "indeterminate":
            return
        self._mode = "determinate"
        if self._ind_after_id is not None:
            try:
                self.after_cancel(self._ind_after_id)
            except Exception:
                pass
        self._ind_after_id = None
        self._redraw()

    def _tick_indeterminate(self):
        if not self.winfo_exists():
            self._ind_after_id = None
            return
        self._ind_phase = (self._ind_phase + 0.018) % 1.0
        self._redraw()
        self._ind_after_id = self.after(16, self._tick_indeterminate)

    def _draw_track(self, w: int, h: int):
        self._canvas.delete("all")
        x1, y1 = 1, 1
        x2, y2 = w - 1, h - 1
        pts = rounded_rect_points(x1, y1, x2, y2, self._r)
        self._canvas.create_polygon(pts, smooth=True, fill=self._track_color, outline=self._border_color, width=1)

    def _draw_fill_determinate(self, w: int, h: int):
        if self._value <= 0.0:
            return

        x1, y1 = 2, 2
        y2 = h - 2
        usable_w = (w - 4)
        fill_w = int(usable_w * self._value)
        x2 = x1 + fill_w
        if x2 <= x1:
            return

        segments = 80
        seg_w = max(1, fill_w // segments)

        x = x1
        while x < x2:
            nx = min(x + seg_w, x2)
            t = (x - x1) / max(1, usable_w)
            color = gradient_color_at(t)
            self._canvas.create_rectangle(x, y1, nx, y2, outline="", fill=color)
            x = nx

        # Redondeado izquierdo
        cap_r = min(self._r, max(2, fill_w // 2))
        pts_left = rounded_rect_points(x1, y1, min(x1 + cap_r * 2, x2), y2, cap_r)
        self._canvas.create_polygon(pts_left, smooth=True, fill=gradient_color_at(0.0), outline="")

        # Si llegó al 100%, redondeado derecho
        if self._value >= 0.999:
            pts_right = rounded_rect_points(max(x1, x2 - cap_r * 2), y1, x2, y2, cap_r)
            self._canvas.create_polygon(pts_right, smooth=True, fill=gradient_color_at(1.0), outline="")

    def _draw_fill_indeterminate(self, w: int, h: int):
        usable_w = (w - 4)
        seg = int(usable_w * 0.30)
        start = int(self._ind_phase * (usable_w + seg)) - seg
        end = start + seg

        x1, y1 = 2, 2
        y2 = h - 2

        sx = max(0, start)
        ex = min(usable_w, end)
        if ex <= sx:
            return

        segments = 40
        seg_w = max(1, (ex - sx) // segments)

        x = x1 + sx
        x_end = x1 + ex
        while x < x_end:
            nx = min(x + seg_w, x_end)
            t = (x - x1) / max(1, usable_w)
            color = gradient_color_at(t)
            self._canvas.create_rectangle(x, y1, nx, y2, outline="", fill=color)
            x = nx

    def _redraw(self):
        try:
            w = max(10, int(self._canvas.winfo_width()))
            h = max(6, int(self._canvas.winfo_height()))
        except Exception:
            return

        self._draw_track(w, h)
        if self._mode == "indeterminate":
            self._draw_fill_indeterminate(w, h)
        else:
            self._draw_fill_determinate(w, h)
