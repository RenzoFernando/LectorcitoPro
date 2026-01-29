# src/view/status_panel.py
from __future__ import annotations

import time
import customtkinter as ctk

from view.gradient_progress import GradientProgressBar


class StatusPanel(ctk.CTkFrame):
    """
    Panel de Estado:
    - Texto de estado con puntos animados (., .., ...)
    - Porcentaje alineado a la derecha
    - Barra de progreso gradiente (track visible + sin puntico)
    - Ruta del archivo (solo durante lectura)
    - Botón cancelar
    - Regla UX: mínimo visible del progreso (evita parpadeo 0→100)
    """

    def __init__(self, parent, *, min_visible_seconds: float = 2.0):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        # --- Config / Estado ---
        self._min_visible_s = float(min_visible_seconds)
        self._processing_started_at: float | None = None
        self._min_end_time: float | None = None
        self._forced_end_time: float | None = None

        self._mode = "idle"  # idle | processing | indeterminate | done
        self._status_base = ""
        self._dots_after_id = None
        self._dots_phase = 1

        self.current_progress = 0.0
        self.target_progress = 0.0
        self._progress_after_id = None
        self._last_tick = None

        # --- UI ---
        # Panel gris moderno
        self.status_panel = ctk.CTkFrame(self, corner_radius=16, border_width=1)
        self.status_panel.grid(row=0, column=0, padx=10, pady=(4, 6), sticky="ew")
        self.status_panel.grid_columnconfigure(0, weight=1)

        top_row = ctk.CTkFrame(self.status_panel, fg_color="transparent")
        top_row.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="ew")
        top_row.grid_columnconfigure(0, weight=1)

        self.lbl_status = ctk.CTkLabel(
            top_row, text="", font=("Segoe UI", 11, "normal"), anchor="w"
        )
        self.lbl_status.grid(row=0, column=0, sticky="w")

        self.lbl_percent = ctk.CTkLabel(
            top_row, text="0%", font=("Segoe UI", 11, "bold"), anchor="e"
        )
        self.lbl_percent.grid(row=0, column=1, sticky="e")

        self.progress_bar = GradientProgressBar(self.status_panel, height=12, corner_radius=8)
        self.progress_bar.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")
        self.progress_bar.set(0.0)

        # Ruta (solo durante lectura)
        self.file_row = ctk.CTkFrame(self, fg_color="transparent")
        self.file_row.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")
        self.file_row.grid_columnconfigure(1, weight=1)

        self.lbl_processing_prefix = ctk.CTkLabel(
            self.file_row, text="", font=("Segoe UI", 9, "bold"), anchor="w"
        )
        self.lbl_processing_prefix.grid(row=0, column=0, sticky="w", padx=(0, 6))

        self.lbl_current_file = ctk.CTkLabel(
            self.file_row, text="", font=("Segoe UI", 9, "normal"), anchor="w"
        )
        self.lbl_current_file.grid(row=0, column=1, sticky="ew")

        # Cancel
        self.btn_cancel = ctk.CTkButton(self, width=150, height=28)
        self.btn_cancel.grid(row=2, column=0, pady=(4, 0))

        # Por defecto: idle
        self.file_row.grid_remove()

        # Traducciones (se setean desde ui.py)
        self._tr = None  # callable(key)->str
        self._key_status_waiting = "status_waiting"
        self._key_status_reading = "status_reading"
        self._key_status_done = "status_done_panel"
        self._key_processing_label = "processing_label"
        self._key_btn_cancel = "btn_cancel"

    # ----------------------------
    # Conexión con i18n
    # ----------------------------
    def set_translator(self, tr_callable):
        """
        tr_callable: función que recibe key y devuelve texto traducido.
        Ej: self._tr = lambda k: self._tr(k)
        """
        self._tr = tr_callable
        self.refresh_texts()

    def refresh_texts(self):
        if not self._tr:
            return

        self.lbl_processing_prefix.configure(text=self._tr(self._key_processing_label))
        self.btn_cancel.configure(text=self._tr(self._key_btn_cancel))

        # Reaplica status base actual, manteniendo fase de puntos si está activa
        if self._mode == "processing":
            self._status_base = self._tr(self._key_status_reading)
        elif self._mode == "idle":
            self._status_base = self._tr(self._key_status_waiting)
        elif self._mode == "done":
            self._status_base = self._tr(self._key_status_done)

        if self._dots_after_id is not None:
            self.lbl_status.configure(text=f"{self._status_base}{'.' * self._dots_phase}")
        else:
            self.lbl_status.configure(text=self._status_base)

    # ----------------------------
    # Tema / colores
    # ----------------------------
    def apply_theme(self, theme_name: str):
        """
        Ajusta colores del panel + textos + track de la barra.
        """
        is_light = theme_name == "Light"
        if is_light:
            panel_bg = "#E3E6EA"
            panel_border = "#D0D7DE"
            text = "#24292F"
            track = "#C9CDD1"
            border = "#B6BAC0"
        else:
            panel_bg = "#20252B"
            panel_border = "#2B3137"
            text = "#E6EDF3"
            track = "#30363D"
            border = "#2B3137"

        try:
            self.status_panel.configure(fg_color=panel_bg, border_color=panel_border, border_width=1)
        except Exception:
            self.status_panel.configure(fg_color=panel_bg)

        self.lbl_status.configure(text_color=text)
        self.lbl_percent.configure(text_color=text)
        self.lbl_processing_prefix.configure(text_color=text)
        self.lbl_current_file.configure(text_color=text)

        self.progress_bar.set_colors(track=track, border=border)
        # Redibuja a valor actual
        self.progress_bar.set(self.current_progress / 100.0)

    # ----------------------------
    # Animación de puntos
    # ----------------------------
    def _set_status(self, base_text: str, with_dots: bool):
        self._status_base = base_text or ""
        if with_dots:
            self._dots_phase = 1
            self._start_dots()
        else:
            self._stop_dots()
            self.lbl_status.configure(text=self._status_base)

    def _start_dots(self):
        self._stop_dots()
        self._tick_dots()

    def _stop_dots(self):
        if self._dots_after_id is not None:
            try:
                self.after_cancel(self._dots_after_id)
            except Exception:
                pass
        self._dots_after_id = None

    def _tick_dots(self):
        if not self.winfo_exists():
            return
        self.lbl_status.configure(text=f"{self._status_base}{'.' * self._dots_phase}")
        self._dots_phase = 1 if self._dots_phase >= 3 else (self._dots_phase + 1)
        self._dots_after_id = self.after(450, self._tick_dots)

    # ----------------------------
    # Progreso: animación + mínimo visible
    # ----------------------------
    def get_min_visible_completion_delay_ms(self) -> int:
        """
        Si terminó muy rápido, devuelve cuánto falta para cumplir el mínimo visible.
        """
        if self._min_end_time is None:
            return 0
        now = time.monotonic()
        remaining = self._min_end_time - now
        return int(max(0.0, remaining) * 1000)

    def _start_progress_animation(self):
        if self._progress_after_id is not None:
            return
        self._last_tick = time.monotonic()
        self._progress_after_id = self.after(16, self._animate_progress)

    def _stop_progress_animation(self):
        if self._progress_after_id is not None:
            try:
                self.after_cancel(self._progress_after_id)
            except Exception:
                pass
        self._progress_after_id = None
        self._last_tick = None

    def _animate_progress(self):
        if not self.winfo_exists():
            self._progress_after_id = None
            return

        now = time.monotonic()
        dt = max(0.001, now - (self._last_tick or now))
        self._last_tick = now

        diff = self.target_progress - self.current_progress
        if abs(diff) < 0.08:
            self.current_progress = self.target_progress
        else:
            # Si terminó rápido y forzamos un end_time, avanzamos para llegar justo a tiempo.
            if self._forced_end_time is not None and now < self._forced_end_time:
                remaining = max(0.001, self._forced_end_time - now)
                step_ratio = min(1.0, dt / remaining)
                self.current_progress += diff * step_ratio
            else:
                # easing normal
                self.current_progress += diff * 0.18

        self.current_progress = max(0.0, min(100.0, self.current_progress))
        self.progress_bar.set(self.current_progress / 100.0)

        # % visible solo si no estamos en indeterminate
        if self._mode in ("processing", "idle", "done"):
            self.lbl_percent.configure(text=f"{int(round(self.current_progress))}%")

        if abs(self.target_progress - self.current_progress) >= 0.08:
            self._progress_after_id = self.after(16, self._animate_progress)
        else:
            self._stop_progress_animation()

    # ----------------------------
    # Utilidad: ruta bonita
    # ----------------------------
    @staticmethod
    def _ellipsize_middle(s: str, max_len: int = 72) -> str:
        s = (s or "").strip()
        if len(s) <= max_len:
            return s
        keep = max_len - 1
        left = keep // 2
        right = keep - left
        return f"{s[:left]}…{s[-right:]}"

    # ----------------------------
    # API pública (la que usará ui.py / controller)
    # ----------------------------
    def set_progress(self, percentage: float, file_context: str | None = None):
        new_target = float(max(0, min(100, int(percentage))))

        # Si pidieron 100 y aún no cumplimos mínimo visible: forzamos end_time
        if new_target >= 100 and self._min_end_time is not None:
            now = time.monotonic()
            self._forced_end_time = self._min_end_time if now < self._min_end_time else None

        self.target_progress = new_target
        self._start_progress_animation()

        # Ruta solo durante lectura real
        if file_context and self._mode == "processing":
            path_txt = self._ellipsize_middle(str(file_context), max_len=72)
            self.lbl_current_file.configure(text=path_txt)
            self.file_row.grid()

    def set_active(self, is_active: bool, *, mode: str = "determinate", text: str | None = None, final_status: str | None = None):
        """
        Equivalente al toggle_ui_for_processing() que tenías en ui.py.
        - is_active=True: entra en processing o indeterminate
        - is_active=False: finaliza según final_status
        """
        if is_active:
            self._processing_started_at = time.monotonic()
            self._min_end_time = self._processing_started_at + self._min_visible_s
            self._forced_end_time = None

            self.file_row.grid_remove()
            self.lbl_current_file.configure(text="")

            if mode == "indeterminate":
                self._mode = "indeterminate"
                self.lbl_percent.configure(text="")
                self.progress_bar.start_indeterminate()

                # base status: texto que te pasan (ej. "Generando árbol...")
                base = text or (self._tr("progress_processing_text") if self._tr else "Procesando")
                self._set_status(base, with_dots=True)
            else:
                self._mode = "processing"
                self.progress_bar.stop_indeterminate()

                self.current_progress = 0.0
                self.target_progress = 0.0
                self.progress_bar.set(0.0)
                self.lbl_percent.configure(text="0%")

                base = self._tr(self._key_status_reading) if self._tr else "Haciendo lectura"
                self._set_status(base, with_dots=True)

            self.btn_cancel.grid()
            return

        # ---- is_active=False (finalización) ----
        self.btn_cancel.grid_remove()
        self.progress_bar.stop_indeterminate()

        if final_status == "success":
            self._mode = "done"
            base = self._tr(self._key_status_done) if self._tr else "¡Completado!"
            self._set_status(base, with_dots=False)

            self.current_progress = 100.0
            self.target_progress = 100.0
            self.progress_bar.set(1.0)
            self.lbl_percent.configure(text="100%")
            self.file_row.grid_remove()

            # vuelve a idle luego de un momentico
            self.after(900, self.back_to_idle)
        else:
            # cancel/error/no_files -> vuelve a idle directo
            self.back_to_idle()

    def back_to_idle(self):
        if not self.winfo_exists():
            return
        self._mode = "idle"
        self.file_row.grid_remove()
        self.lbl_current_file.configure(text="")

        self.current_progress = 0.0
        self.target_progress = 0.0
        self.progress_bar.set(0.0)
        self.lbl_percent.configure(text="0%")

        base = self._tr(self._key_status_waiting) if self._tr else "Esperando lectura"
        self._set_status(base, with_dots=True)

    def cleanup(self):
        """
        Llamar al cerrar la app para evitar after() colgando.
        """
        self._stop_dots()
        self._stop_progress_animation()
        try:
            self.progress_bar.cleanup()
        except Exception:
            pass
