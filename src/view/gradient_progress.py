from __future__ import annotations
import customtkinter as ctk
from tkinter import Canvas
import math
from view.ui_constants import PROGRESS_DEFAULT_STOPS, PROGRESS_DEFAULT_TRACK, PROGRESS_DEFAULT_BORDER, NEUTRAL_WHITE, PROGRESS_CANVAS_TICK_MS, PROGRESS_CAPSULE_SEGMENTS, PROGRESS_MIN_BODY_SEGMENTS, PROGRESS_POINT_SEGMENTS

# =============================================================================
# UTILIDADES DE COLOR
# =============================================================================

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


DEFAULT_STOPS = list(PROGRESS_DEFAULT_STOPS)

def gradient_color_at(t: float, stops: list[tuple[float, str]] | None = None) -> str:
    stops = list(stops or DEFAULT_STOPS)
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


# =============================================================================
# FUNCIONES DE DIBUJO AVANZADO
# =============================================================================

def _capsule_points(x1: float, y1: float, x2: float, y2: float, r: float, segments: int = PROGRESS_POINT_SEGMENTS) -> list[float]:
    """Genera los puntos de un polígono con forma de cápsula perfectamente ovalada."""
    # Asegurar que el radio no sea mayor que la mitad de la dimensión más pequeña
    if x2 - x1 < 2 * r:
        r = (x2 - x1) / 2.0
    if y2 - y1 < 2 * r:
        r = (y2 - y1) / 2.0

    # Puntos del arco izquierdo
    cx_left = x1 + r
    cy = (y1 + y2) / 2.0
    points_left = []
    # Ángulo de 90 a 270 grados (pi/2 a 3pi/2)
    for seg in range(segments + 1):
        angle = math.pi / 2.0 + (math.pi * seg / segments)
        px = cx_left + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        points_left.extend([px, py])

    # Puntos del arco derecho
    cx_right = x2 - r
    points_right = []
    # Ángulo de -90 a 90 grados (-pi/2 a pi/2)
    for seg in range(segments + 1):
        angle = -math.pi / 2.0 + (math.pi * seg / segments)
        px = cx_right + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        points_right.extend([px, py])

    # Unir puntos en orden: arco izquierdo, luego arco derecho
    return points_left + points_right


# =============================================================================
# WIDGET BARRA DE PROGRESO
# =============================================================================

class GradientProgressBar(ctk.CTkFrame):
    def __init__(self, parent, height: int = 12, corner_radius: int = 8):
        super().__init__(parent, fg_color="transparent")
        self._h = height
        self._r = corner_radius

        self._value = 0.0
        self._mode = "determinate"
        self._ind_phase = 0.0
        self._ind_after_id = None

        self._track_color = PROGRESS_DEFAULT_TRACK
        self._border_color = PROGRESS_DEFAULT_BORDER
        self._gradient_stops = list(DEFAULT_STOPS)

        self._canvas = Canvas(self, height=self._h, highlightthickness=0, bd=0, relief="flat")
        self._canvas.pack(fill="both", expand=True)

        self.bind("<Configure>", lambda e: self._redraw())
        self._canvas.bind("<Configure>", lambda e: self._redraw())

    def set_colors(self, *, track: str, border: str, stops: list[tuple[float, str]] | None = None):
        self._track_color = track
        self._border_color = border
        if stops:
            self._gradient_stops = list(stops)
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
        self._ind_after_id = self.after(PROGRESS_CANVAS_TICK_MS, self._tick_indeterminate)

    def _get_canvas_bg(self) -> str:
        for widget in (self.master, self, getattr(self.master, "master", None)):
            if widget is None:
                continue
            for key in ("fg_color", "bg_color", "bg"):
                try:
                    color = widget.cget(key)
                except Exception:
                    continue
                if isinstance(color, (tuple, list)) and color:
                    color = color[0]
                if isinstance(color, str) and color and color != "transparent":
                    return color
        if isinstance(self._track_color, str) and self._track_color:
            return self._track_color
        color = self.cget("fg_color")
        if isinstance(color, (tuple, list)) and color:
            color = color[0]
        if isinstance(color, str) and color and color != "transparent":
            return color
        return NEUTRAL_WHITE

    def _draw_capsule_polygon(self, x1, y1, x2, y2, fill, outline=""):
        if x2 <= x1 or y2 <= y1:
            return

        h_ = y2 - y1
        r_ = h_ / 2.0  # Usar división flotante para precisión

        # Usar más segmentos para un óvalo extremadamente suave
        points = _capsule_points(x1, y1, x2, y2, r_, segments=PROGRESS_CAPSULE_SEGMENTS)
        self._canvas.create_polygon(points, outline=outline, fill=fill, smooth=True)

    def _draw_gradient_capsule(self, x1: float, y1: float, x2: float, y2: float, t_start: float, t_end: float):
        if x2 <= x1 or y2 <= y1:
            return

        h_ = y2 - y1
        r = h_ / 2.0
        cy = (y1 + y2) / 2.0
        width = max(1.0, x2 - x1)

        start_x = int(math.floor(x1))
        end_x = int(math.ceil(x2))

        for ix in range(start_x, end_x):
            px = ix + 0.5
            top = y1
            bottom = y2

            if px < x1 + r:
                dx = px - (x1 + r)
                dy = math.sqrt(max(0.0, (r * r) - (dx * dx)))
                top = cy - dy
                bottom = cy + dy
            elif px > x2 - r:
                dx = px - (x2 - r)
                dy = math.sqrt(max(0.0, (r * r) - (dx * dx)))
                top = cy - dy
                bottom = cy + dy

            rel = ((px - x1) / width) if width > 0 else 0.0
            t = t_start + ((t_end - t_start) * rel)
            color = gradient_color_at(t, self._gradient_stops)
            self._canvas.create_rectangle(ix, int(math.floor(top)), ix + 2, int(math.ceil(bottom)), outline='', fill=color)

    def _draw_track(self, w: int, h: int):
        self._canvas.delete("all")
        self._canvas.configure(bg=self._get_canvas_bg())

        x1, y1 = 1, 1
        x2, y2 = w - 1, h - 1

        # Usar polígonos para una forma perfecta y continua de la pista y el borde
        self._draw_capsule_polygon(x1, y1, x2, y2, self._border_color)
        self._draw_capsule_polygon(x1 + 1, y1 + 1, x2 - 1, y2 - 1, self._track_color)

    def _draw_fill_determinate(self, w: int, h: int):
        if self._value <= 0.0:
            return

        x1, y1 = 2, 2
        y2 = h - 2
        usable_w = w - 4
        fill_w = usable_w * self._value
        x2 = int(math.ceil(x1 + fill_w))

        if x2 <= x1:
            return

        inner_h = y2 - y1
        if inner_h <= 0 or fill_w <= 0:
            return

        if fill_w > inner_h:
            self._draw_gradient_capsule(x1, y1, x1 + fill_w, y2, 0.0, self._value)
            return

        r = inner_h / 2.0

        if fill_w <= inner_h:
            color = gradient_color_at(fill_w / max(1.0, float(usable_w)), self._gradient_stops)
            # Para anchos muy pequeños, dibujamos un óvalo centrado con create_polygon
            cx = (x1 + x2) // 2
            # Un óvalo es una cápsula con ancho y alto iguales a 2r
            self._draw_capsule_polygon(cx - r, y1, cx + r, y2, color)
            return

        # Para degradar el relleno en Tkinter, la subdivisión es necesaria.
        # Dibujaremos los extremos con óvalos y el centro con rectángulos subdivididos.
        # Esto es complejo, pero al tener la PISTA de fondo perfecta (gracias a create_polygon),
        # los artefactos visuales en el borde deberían desaparecer.

        # Dibujar casquetes ovalados en los extremos para forma perfecta
        left_color = gradient_color_at(0.0, self._gradient_stops)
        right_color = gradient_color_at(self._value, self._gradient_stops)

        # Usar create_oval para los extremos del RELLENO DEGRADADO.
        # Al alinear las geometrías de relleno perfectamente, la pista de fondo polygon
        # será el único borde visible en las esquinas, solucionando el problema del usuario.

        # Casquete izquierdo del relleno degradado
        self._canvas.create_oval(x1, y1, x1 + 2 * r + 1, y2, outline="", fill=left_color)
        # Casquete derecho del relleno degradado
        self._canvas.create_oval(x2 - 2 * r - 1, y1, x2, y2, outline="", fill=right_color)

        # Dibujar degradado en el cuerpo rectangular
        # Aseguramos que el cuerpo se alinee perfectamente entre los casquetes.
        rect_x1 = x1 + r - 1
        rect_x2 = x2 - r + 1
        mid_w = rect_x2 - rect_x1

        if mid_w > 0:
            # Solución de parches eliminada para volver a "estaba mejor el anterior".
            # La pista de fondo es ahora perfecta, solucionando el artefacto visual principal.

            segments = max(PROGRESS_MIN_BODY_SEGMENTS, int(mid_w))
            seg_w = mid_w / segments
            x = rect_x1

            for _ in range(segments):
                nx = x + seg_w
                mid = (x + nx) / 2.0
                t = (mid - 2.0) / max(1.0, float(usable_w))
                color = gradient_color_at(t, self._gradient_stops)

                # int(nx + 1) para solapamiento de 1px, necesario para degradado central
                self._canvas.create_rectangle(int(x), y1, int(math.ceil(nx + 1)), y2, outline="", fill=color)
                x = nx

            self._canvas.create_rectangle(int(rect_x2 - 1), y1, x2, y2, outline="", fill=right_color)

    def _draw_fill_indeterminate(self, w: int, h: int):
        usable_w = w - 4
        seg = usable_w * 0.30
        start = self._ind_phase * (usable_w + seg) - seg
        end = start + seg

        x1, y1 = 2, 2
        y2 = h - 2

        sx = max(0.0, start)
        ex = min(float(usable_w), end)
        if ex <= sx:
            return

        fill_w = ex - sx
        inner_h = y2 - y1
        if inner_h <= 0 or fill_w <= 0:
            return

        absolute_x1 = x1 + sx
        absolute_x2 = x1 + ex

        if fill_w > inner_h:
            t_start = sx / max(1.0, float(usable_w))
            t_end = ex / max(1.0, float(usable_w))
            self._draw_gradient_capsule(absolute_x1, y1, absolute_x2, y2, t_start, t_end)
            return

        r = inner_h / 2.0

        if fill_w <= inner_h:
            color = gradient_color_at(((sx + ex) / 2.0) / max(1.0, float(usable_w)), self._gradient_stops)
            # Óvalo centrado para anchos pequeños
            cx = (absolute_x1 + absolute_x2) // 2
            self._draw_capsule_polygon(cx - r, y1, cx + r, y2, color)
            return

        # Colores de los extremos del segmento flotante
        t_start = sx / max(1.0, float(usable_w))
        t_end = ex / max(1.0, float(usable_w))
        left_color = gradient_color_at(t_start, self._gradient_stops)
        right_color = gradient_color_at(t_end, self._gradient_stops)

        # Casquetes ovalados
        self._canvas.create_oval(absolute_x1, y1, absolute_x1 + 2 * r + 1, y2, outline="", fill=left_color)
        self._canvas.create_oval(absolute_x2 - 2 * r - 1, y1, absolute_x2, y2, outline="", fill=right_color)

        # Cuerpo degradado
        rect_x1 = absolute_x1 + r - 1
        rect_x2 = absolute_x2 - r + 1
        mid_w = rect_x2 - rect_x1

        if mid_w > 0:
            # Solución de parches eliminada para volver a "estaba mejor el anterior".
            # La pista de fondo es ahora perfecta, solucionando el artefacto visual principal.

            segments = max(16, int(mid_w))
            seg_w = mid_w / segments
            x = rect_x1
            for _ in range(segments):
                nx = x + seg_w
                mid = (x + nx) / 2.0
                t = (mid - 2.0) / max(1.0, float(usable_w))
                color = gradient_color_at(t, self._gradient_stops)
                # int(nx + 1) para solapamiento de 1px
                self._canvas.create_rectangle(int(x), y1, int(math.ceil(nx + 1)), y2, outline="", fill=color)
                x = nx

            self._canvas.create_rectangle(int(rect_x2 - 1), y1, absolute_x2, y2, outline="", fill=right_color)

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
