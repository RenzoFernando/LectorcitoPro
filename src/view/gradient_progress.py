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


class GradientProgressBar(ctk.CTkProgressBar):
    """API historica sobre CTkProgressBar, ahora sin degradados ni Canvas."""

    def __init__(self, parent, *, height: int = 8, corner_radius: int = 4, **kwargs):
        self._track_color = PROGRESS_DEFAULT_TRACK
        self._progress_color = gradient_color_at(0.0)
        self._displayed_progress_color = None
        self._value = 0.0
        self._indeterminate = False

        super().__init__(
            parent,
            height=height,
            corner_radius=corner_radius,
            fg_color=self._track_color,
            progress_color=self._track_color,
            border_width=1,
            border_color=PROGRESS_DEFAULT_BORDER,
            mode="determinate",
            **kwargs,
        )
        self._displayed_progress_color = self._track_color
        super().set(0.0)

    def _sync_progress_color(self, *, force_active: bool = False):
        color = self._progress_color if force_active or self._value > 0.0 else self._track_color
        if color == self._displayed_progress_color:
            return
        super().configure(progress_color=color)
        self._displayed_progress_color = color

    def set_colors(self, *, track=None, border=None, stops=None):
        payload = {}
        if track is not None:
            self._track_color = track
            payload["fg_color"] = track
        if border is not None:
            payload["border_color"] = border
        if stops:
            self._progress_color = gradient_color_at(0.0, stops)
        if payload:
            super().configure(**payload)
        self._sync_progress_color(force_active=self._indeterminate)

    def set(self, value, from_variable_callback=False):
        try:
            self._value = max(0.0, min(1.0, float(value)))
        except Exception:
            self._value = 0.0
        self._sync_progress_color()
        return super().set(self._value, from_variable_callback=from_variable_callback)

    def start_indeterminate(self):
        self._indeterminate = True
        self._sync_progress_color(force_active=True)
        super().configure(mode="indeterminate")
        self.start()

    def stop_indeterminate(self):
        try:
            self.stop()
        finally:
            self._indeterminate = False
            super().configure(mode="determinate")
            self._sync_progress_color()
            super().set(self._value)
