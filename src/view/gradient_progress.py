from __future__ import annotations

import customtkinter as ctk

from view.ui_constants import (
    PROGRESS_DEFAULT_BORDER,
    PROGRESS_DEFAULT_STOPS,
    PROGRESS_DEFAULT_TRACK,
)

# =============================================================================
# BARRA DE PROGRESO
# =============================================================================


def gradient_color_at(t: float, stops=None) -> str:
    """Compatibilidad: devuelve un color solido de la paleta indicada."""
    palette = list(stops or PROGRESS_DEFAULT_STOPS)
    if not palette:
        return "#2563EB"
    t = max(0.0, min(1.0, float(t)))
    return min(palette, key=lambda item: abs(float(item[0]) - t))[1]


class GradientProgressBar(ctk.CTkFrame):
    """API historica de progreso con relleno oculto cuando el valor es cero."""

    def __init__(self, parent, *, height: int = 8, corner_radius: int = 4, **kwargs):
        self._track_color = PROGRESS_DEFAULT_TRACK
        self._border_color = PROGRESS_DEFAULT_BORDER
        self._progress_color = gradient_color_at(0.0)
        self._value = 0.0
        self._indeterminate = False
        self._indeterminate_after_id = None
        self._indeterminate_phase = 0.0
        self._indeterminate_direction = 1.0
        self._corner_radius = max(0, int(corner_radius))

        super().__init__(
            parent,
            height=height,
            corner_radius=self._corner_radius,
            fg_color=self._track_color,
            border_width=1,
            border_color=self._border_color,
            **kwargs,
        )
        # El frame interno no debe alterar la altura compacta de la barra.
        self.pack_propagate(False)

        inner_radius = max(0, self._corner_radius - 1)
        inner_height = max(1, int(height) - 2)
        self._track = ctk.CTkFrame(
            self,
            height=inner_height,
            fg_color=self._track_color,
            corner_radius=inner_radius,
            border_width=0,
        )
        self._track.pack(fill="both", expand=True, padx=1, pady=1)

        self._fill = ctk.CTkFrame(
            self._track,
            fg_color=self._progress_color,
            corner_radius=inner_radius,
            border_width=0,
        )
        self._render_determinate()

    def set_colors(self, *, track=None, border=None, stops=None):
        if track is not None:
            self._track_color = track
        if border is not None:
            self._border_color = border
        if stops:
            self._progress_color = gradient_color_at(0.0, stops)

        self.configure(
            fg_color=self._track_color,
            border_color=self._border_color,
        )
        self._track.configure(fg_color=self._track_color)
        self._fill.configure(fg_color=self._progress_color)

        if not self._indeterminate:
            self._render_determinate()

    def _render_determinate(self):
        if self._value <= 0.0:
            self._fill.place_forget()
            return

        self._fill.place(
            relx=0.0,
            rely=0.0,
            relwidth=self._value,
            relheight=1.0,
        )

    def set(self, value, from_variable_callback=False):
        try:
            self._value = max(0.0, min(1.0, float(value)))
        except Exception:
            self._value = 0.0

        if not self._indeterminate:
            self._render_determinate()
        return None

    def _tick_indeterminate(self):
        if not self.winfo_exists() or not self._indeterminate:
            self._indeterminate_after_id = None
            return

        self._indeterminate_phase += 0.045 * self._indeterminate_direction
        if self._indeterminate_phase >= 1.0:
            self._indeterminate_phase = 1.0
            self._indeterminate_direction = -1.0
        elif self._indeterminate_phase <= 0.0:
            self._indeterminate_phase = 0.0
            self._indeterminate_direction = 1.0

        segment_width = 0.24
        relx = self._indeterminate_phase * (1.0 - segment_width)
        self._fill.place(
            relx=relx,
            rely=0.0,
            relwidth=segment_width,
            relheight=1.0,
        )
        self._indeterminate_after_id = self.after(24, self._tick_indeterminate)

    def start_indeterminate(self):
        self.stop_indeterminate()
        self._indeterminate = True
        self._indeterminate_phase = 0.0
        self._indeterminate_direction = 1.0
        self._fill.configure(fg_color=self._progress_color)
        self._tick_indeterminate()

    def stop_indeterminate(self):
        if self._indeterminate_after_id is not None:
            try:
                self.after_cancel(self._indeterminate_after_id)
            except Exception:
                pass
        self._indeterminate_after_id = None
        self._indeterminate = False
        self._render_determinate()