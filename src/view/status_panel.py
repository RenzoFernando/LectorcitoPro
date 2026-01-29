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
    - Ruta del archivo (durante lectura) dentro del mismo panel
    - Botón cancelar (icono ✕ compacto)
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
        self.status_panel = ctk.CTkFrame(self, corner_radius=16, border_width=1)
        self.status_panel.grid(row=0, column=0, padx=10, pady=(4, 6), sticky="ew")
        self.status_panel.grid_columnconfigure(0, weight=1)

        top_row = ctk.CTkFrame(self.status_panel, fg_color="transparent")
        top_row.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="ew")
        top_row.grid_columnconfigure(0, weight=1)  # status text
        top_row.grid_columnconfigure(1, weight=0)  # percent
        top_row.grid_columnconfigure(2, weight=0)  # cancel

        self.lbl_status = ctk.CTkLabel(
            top_row, text="", font=("Segoe UI", 11, "normal"), anchor="w"
        )
        self.lbl_status.grid(row=0, column=0, sticky="w")

        self.lbl_percent = ctk.CTkLabel(
            top_row, text="0%", font=("Segoe UI", 11, "bold"), anchor="e"
        )
        self.lbl_percent.grid(row=0, column=1, sticky="e", padx=(0, 8))

        # Cancel (icono compacto dentro del panel)
        self.btn_cancel = ctk.CTkButton(
            top_row,
            text="✕",
            width=28,
            height=28,
            corner_radius=14,
            fg_color="#D03B3D",
            hover_color="#A03031",
            text_color="white",
            font=("Segoe UI", 13, "bold"),
        )
        self.btn_cancel.grid(row=0, column=2, sticky="e")
        self.btn_cancel.grid_remove()  # oculto por defecto

        self.progress_bar = GradientProgressBar(self.status_panel, height=12, corner_radius=8)
        self.progress_bar.grid(row=1, column=0, padx=12, pady=(0, 6), sticky="ew")
        self.progress_bar.set(0.0)

        # Ruta (ruta actual / carpeta) — dentro del mismo rectángulo
        self.file_row = ctk.CTkFrame(self.status_panel, fg_color="transparent")
        self.file_row.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")
        self.file_row.grid_columnconfigure(1, weight=1)

        self.lbl_processing_prefix = ctk.CTkLabel(
            self.file_row, text="", font=("Segoe UI", 9, "bold"), anchor="w"
        )
        self.lbl_processing_prefix.grid(row=0, column=0, sticky="w", padx=(0, 6))

        self.lbl_current_file = ctk.CTkLabel(
            self.file_row,
            text="",
            font=("Segoe UI", 9, "normal"),
            anchor="w",
            justify="left",
            wraplength=460,
        )
        self.lbl_current_file.grid(row=0, column=1, sticky="ew")

        # Ajusta wraplength cuando cambie el ancho del panel
        self.status_panel.bind("<Configure>", self._on_panel_resize)

        # cache de traducción (para mostrar/ocultar el prefijo sin romper i18n)
        self._processing_label_text = ""
        self._btn_cancel_full_text = ""

        # Traducciones (se setean desde ui.py)
        self._tr = None  # callable(key)->str
        self._key_status_waiting = "status_waiting"
        self._key_status_reading = "status_reading"
        self._key_status_done = "status_done_panel"
        self._key_processing_label = "processing_label"
        self._key_btn_cancel = "btn_cancel"

        # Default idle
        self.lbl_processing_prefix.configure(text="")
        self.lbl_current_file.configure(text="")
        self._mode = "idle"
        self._set_status("Esperando lectura", with_dots=True)

    # ----------------------------
    # Conexión con i18n
    # ----------------------------
    def set_translator(self, tr_callable):
        self._tr = tr_callable
        self.refresh_texts()

    def refresh_texts(self):
        if not self._tr:
            return

        self._processing_label_text = self._tr(self._key_processing_label)
        if (self.lbl_processing_prefix.cget("text") or "").strip():
            self.lbl_processing_prefix.configure(text=self._processing_label_text)

        cancel_txt = self._tr(self._key_btn_cancel)
        self._btn_cancel_full_text = cancel_txt
        self.btn_cancel.configure(text=(cancel_txt if len(cancel_txt) <= 2 else "✕"))

        if self._mode == "processing":
            self._status_base = self._tr(self._key_status_reading)
        elif self._mode == "idle":
            self._status_base = self._tr(self._key_status_waiting)
        elif self._mode == "done":
            self._status_base = self._tr(self._key_status_done)

        if self._dots_after_id is None:
            self.lbl_status.configure(text=self._status_base)

    # ----------------------------
    # Tema
    # ----------------------------
    def apply_theme(self, theme_name: str):
        is_light = theme_name == "Light"
        if is_light:
            panel_bg = "#E3E6EA"
            panel_border = "#D0D7DE"
            text = "#24292F"
            muted = "#6E7781"
            track = "#C9CDD1"
            border = "#B6BAC0"
        else:
            panel_bg = "#20252B"
            panel_border = "#2B3137"
            text = "#E6EDF3"
            muted = "#8B949E"
            track = "#30363D"
            border = "#2B3137"

        try:
            self.status_panel.configure(fg_color=panel_bg, border_color=panel_border, border_width=1)
        except Exception:
            self.status_panel.configure(fg_color=panel_bg)

        self.lbl_status.configure(text_color=text)
        self.lbl_percent.configure(text_color=text)
        self.lbl_processing_prefix.configure(text_color=text)
        self.lbl_current_file.configure(text_color=muted)

        self.progress_bar.set_colors(track=track, border=border)
        self.progress_bar.set(self.current_progress / 100.0)

    def _on_panel_resize(self, event=None):
        try:
            panel_w = int(self.status_panel.winfo_width())
        except Exception:
            return

        usable = max(180, panel_w - 24)  # 12 + 12 padding aprox
        try:
            prefix_w = int(self.lbl_processing_prefix.winfo_reqwidth()) + 6
        except Exception:
            prefix_w = 0

        wrap = max(160, usable - prefix_w)
        try:
            self.lbl_current_file.configure(wraplength=wrap)
        except Exception:
            pass

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
        self._dots_after_id = self.after(450, self._tick_dots)

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
        dots = "." * self._dots_phase
        self._dots_phase += 1
        if self._dots_phase > 3:
            self._dots_phase = 1

        self.lbl_status.configure(text=f"{self._status_base}{dots}")
        self._dots_after_id = self.after(450, self._tick_dots)

    # ----------------------------
    # Regla UX: mínimo visible (MÉTODO QUE TE FALTABA)
    # ----------------------------
    def get_min_visible_completion_delay_ms(self) -> int:
        """
        Tiempo restante (ms) para cumplir el mínimo visible desde que empezó processing.
        El controller lo usa para retrasar el cierre/mensaje final y evitar parpadeo.
        """
        if self._processing_started_at is None:
            return 0
        now = time.monotonic()
        min_end = self._processing_started_at + self._min_visible_s
        remaining = max(0.0, min_end - now)
        return int(remaining * 1000)

    # ----------------------------
    # Animación de progreso suave
    # ----------------------------
    def _start_progress_animation(self):
        if self._progress_after_id is None:
            self._last_tick = time.monotonic()
            self._progress_after_id = self.after(16, self._tick_progress)

    def _stop_progress_animation(self):
        if self._progress_after_id is not None:
            try:
                self.after_cancel(self._progress_after_id)
            except Exception:
                pass
        self._progress_after_id = None

    def _tick_progress(self):
        if not self.winfo_exists():
            return

        now = time.monotonic()
        dt = (now - (self._last_tick or now))
        self._last_tick = now

        # Si estamos forzando fin por mínimo visible:
        if self._forced_end_time is not None and now < self._forced_end_time:
            self.target_progress = max(self.target_progress, 98.0)
        elif self._forced_end_time is not None and now >= self._forced_end_time:
            self._forced_end_time = None
            self.target_progress = 100.0

        diff = self.target_progress - self.current_progress
        step = diff * min(1.0, dt * 10.0)
        if abs(diff) < 0.05:
            self.current_progress = self.target_progress
        else:
            self.current_progress += step

        self.progress_bar.set(self.current_progress / 100.0)
        if self._mode != "indeterminate":
            self.lbl_percent.configure(text=f"{int(self.current_progress)}%")

        if abs(self.target_progress - self.current_progress) < 0.05:
            self.current_progress = self.target_progress
            self.progress_bar.set(self.current_progress / 100.0)
            if self._mode != "indeterminate":
                self.lbl_percent.configure(text=f"{int(self.current_progress)}%")
            self._stop_progress_animation()
            return

        self._progress_after_id = self.after(16, self._tick_progress)

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
    # API pública (ui.py / controller)
    # ----------------------------
    def set_progress(self, percentage: float, file_context: str | None = None):
        new_target = float(max(0, min(100, int(percentage))))

        # Si pidieron 100 y aún no cumplimos mínimo visible: forzamos end_time
        if new_target >= 100 and self._min_end_time is not None:
            now = time.monotonic()
            self._forced_end_time = self._min_end_time if now < self._min_end_time else None

        self.target_progress = new_target
        self._start_progress_animation()

        if file_context and self._mode == "processing":
            path_txt = self._ellipsize_middle(str(file_context), max_len=140)
            self.lbl_current_file.configure(text=path_txt)

            prefix = self._processing_label_text or (self._tr(self._key_processing_label) if self._tr else "Procesando:")
            self.lbl_processing_prefix.configure(text=prefix)

    def set_active(
        self,
        is_active: bool,
        *,
        mode: str = "determinate",
        text: str | None = None,
        final_status: str | None = None
    ):
        if is_active:
            self._processing_started_at = time.monotonic()
            self._min_end_time = self._processing_started_at + self._min_visible_s
            self._forced_end_time = None

            self.lbl_processing_prefix.configure(text="")
            self.lbl_current_file.configure(text="")

            if mode == "indeterminate":
                self._mode = "indeterminate"
                self.lbl_percent.configure(text="")
                self.progress_bar.start_indeterminate()

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

        # ---- is_active=False ----
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
            self.lbl_processing_prefix.configure(text="")
            self.lbl_current_file.configure(text="")

            self.after(900, self.back_to_idle)
        else:
            self.back_to_idle()

    def back_to_idle(self):
        if not self.winfo_exists():
            return
        self._mode = "idle"
        self.lbl_processing_prefix.configure(text="")
        self.lbl_current_file.configure(text="")

        self.current_progress = 0.0
        self.target_progress = 0.0
        self.progress_bar.set(0.0)
        self.lbl_percent.configure(text="0%")

        base = self._tr(self._key_status_waiting) if self._tr else "Esperando lectura"
        self._set_status(base, with_dots=True)

        try:
            self.btn_cancel.grid_remove()
        except Exception:
            pass

    def cleanup(self):
        self._stop_dots()
        self._stop_progress_animation()
        try:
            self.progress_bar.stop_indeterminate()
        except Exception:
            pass
