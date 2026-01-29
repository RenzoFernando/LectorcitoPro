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
    rojo -> naranja -> amarillo -> amarillo limón -> verde
    """
    stops = [
        (0.00, "#D03B3D"),  # rojo
        (0.25, "#F08C00"),  # naranja
        (0.50, "#F9C74F"),  # amarillo
        (0.75, "#CDEB4A"),  # amarillo limón
        (1.00, "#2FA047"),  # verde
    ]
    t = max(0.0, min(1.0, float(t)))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if p0 <= t <= p1:
            local = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
            return _lerp_color(c0, c1, local)
    return stops[-1][1]


def rounded_rect_points(x1: int, y1: int, x2: int, y2: int, r: int):
    """
    Puntos para un rectángulo redondeado en Canvas (polygon smooth=True).
    """
    r = max(0, min(r, (x2 - x1) // 2, (y2 - y1) // 2))
    return [
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


class GradientProgressBar(ctk.CTkFrame):
    """
    Barra de progreso personalizada:
    - Track gris marcado
    - Fill con gradiente continuo rojo→verde
    - Sin “puntico azul”
    - Modo indeterminate opcional (segmento moviéndose)
    """
    def __init__(self, parent, height: int = 12, corner_radius: int = 8):
        super().__init__(parent, fg_color="transparent")
        self._h = int(height)
        self._r = int(corner_radius)

        self._value = 0.0  # 0..1
        self._mode = "determinate"  # determinate | indeterminate

        self._ind_after = None
        self._ind_phase = 0.0

        # Colores por defecto (se pueden sobreescribir con set_colors)
        self._track = "#C9CDD1"
        self._border = "#B6BAC0"

        self._canvas = Canvas(self, height=self._h, highlightthickness=0, bd=0)
        self._canvas.pack(fill="x", expand=True)
        self._canvas.bind("<Configure>", lambda e: self._redraw())

    def set_colors(self, track: str, border: str):
        self._track = track
        self._border = border
        self._redraw()

    def set(self, value_0_1: float):
        self._value = max(0.0, min(1.0, float(value_0_1)))
        if self._mode != "determinate":
            self.stop_indeterminate()
        self._redraw()

    def start_indeterminate(self):
        self._mode = "indeterminate"
        self._cancel_indeterminate()
        self._ind_phase = 0.0
        self._tick_indeterminate()

    def stop_indeterminate(self):
        self._mode = "determinate"
        self._cancel_indeterminate()
        self._redraw()

    def cleanup(self):
        self._cancel_indeterminate()

    def _cancel_indeterminate(self):
        if self._ind_after is not None:
            try:
                self.after_cancel(self._ind_after)
            except Exception:
                pass
        self._ind_after = None

    def _tick_indeterminate(self):
        if self._mode != "indeterminate":
            return
        # Avanza fase (60fps aprox)
        self._ind_phase = (self._ind_phase + 0.03) % 1.0
        self._redraw()
        self._ind_after = self.after(16, self._tick_indeterminate)

    def _draw_track(self, w: int, h: int):
        self._canvas.delete("all")
        pts = rounded_rect_points(2, 2, w - 2, h - 2, self._r)
        self._canvas.create_polygon(
            pts, smooth=True,
            fill=self._track, outline=self._border, width=1
        )

    def _draw_fill_determinate(self, w: int, h: int):
        fill_w = int((w - 4) * self._value)
        if fill_w <= 0:
            return

        x1, y1 = 2, 2
        x2 = x1 + fill_w
        y2 = h - 2

        # Segmentar para simular degradado continuo
        # (número relativamente alto para que no se vean cortes)
        segments = 70
        seg_w = max(1, fill_w // segments)

        x = x1
        while x < x2:
            nx = min(x + seg_w, x2)
            mid = (x + nx) / 2
            t = (mid - x1) / max(1, (w - 4))
            color = gradient_color_at(t)
            self._canvas.create_rectangle(x, y1, nx, y2, outline="", fill=color)
            x = nx

        # Cap redondeado izquierdo
        cap_r = min(self._r, max(2, fill_w // 2))
        pts_left = rounded_rect_points(x1, y1, min(x1 + cap_r * 2, x2), y2, cap_r)
        self._canvas.create_polygon(pts_left, smooth=True, fill=gradient_color_at(0.0), outline="")

        # Si llegó al 100%, redondeado derecho
        if self._value >= 0.999:
            pts_right = rounded_rect_points(max(x1, x2 - cap_r * 2), y1, x2, y2, cap_r)
            self._canvas.create_polygon(pts_right, smooth=True, fill=gradient_color_at(1.0), outline="")

    def _draw_fill_indeterminate(self, w: int, h: int):
        # Segmento móvil (30% del ancho total usable)
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

        # Degradado dentro del segmento
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
