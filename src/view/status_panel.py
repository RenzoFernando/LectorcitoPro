from __future__ import annotations
import time
import customtkinter as ctk

from view.gradient_progress import GradientProgressBar
from view.ui_constants import FONT_FAMILY_PRIMARY, COLORS, get_theme_tokens, get_button_tokens, STATUS_PANEL_DEFAULT_MIN_VISIBLE_SECONDS, STATUS_PANEL_CORNER_RADIUS, STATUS_PANEL_BORDER_WIDTH, STATUS_PANEL_PADX, STATUS_PANEL_PADY, STATUS_PANEL_ROW_PADX, STATUS_PANEL_TOP_ROW_PADY, STATUS_PANEL_STATUS_FONT_SIZE, STATUS_PANEL_PERCENT_FONT_SIZE, STATUS_PANEL_PERCENT_PADX, STATUS_PANEL_CANCEL_SIZE, STATUS_PANEL_CANCEL_RADIUS, STATUS_PANEL_CANCEL_FONT_SIZE, STATUS_PANEL_PROGRESS_HEIGHT, STATUS_PANEL_PROGRESS_RADIUS, STATUS_PANEL_PROGRESS_PADY, STATUS_PANEL_FILE_ROW_PADY, STATUS_PANEL_FILE_PREFIX_FONT_SIZE, STATUS_PANEL_FILE_TEXT_FONT_SIZE, STATUS_PANEL_FILE_WRAP_DEFAULT, STATUS_PANEL_MIN_USABLE_WIDTH, STATUS_PANEL_PREFIX_GAP, STATUS_PANEL_MIN_WRAP, STATUS_PANEL_DOTS_INTERVAL_MS, STATUS_PANEL_PROGRESS_TICK_MS, STATUS_PANEL_SUCCESS_RESET_DELAY_MS, STATUS_PANEL_ELLIPSIS_MAX_LEN, STATUS_PANEL_CONTEXT_MAX_LEN
from view.translations import translate_default


# =============================================================================
# PANEL DE ESTADO Y PROGRESO
# =============================================================================

def _translate_status(tr_callable, key: str):
    if callable(tr_callable):
        try:
            return tr_callable(key)
        except Exception:
            pass
    return translate_default(key)

class StatusPanel(ctk.CTkFrame):
    def __init__(self, parent, *, min_visible_seconds: float = STATUS_PANEL_DEFAULT_MIN_VISIBLE_SECONDS):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        self._min_visible_s = float(min_visible_seconds)
        self._processing_started_at: float | None = None
        self._min_end_time: float | None = None
        self._forced_end_time: float | None = None

        self._mode = "idle"
        self._status_base = ""
        self._dots_after_id = None
        self._dots_phase = 1

        self.current_progress = 0.0
        self.target_progress = 0.0
        self._progress_after_id = None
        self._last_tick = None
        self._current_theme = "Light"

        # --- Construccion UI ---
        self.status_panel = ctk.CTkFrame(self, corner_radius=STATUS_PANEL_CORNER_RADIUS, border_width=STATUS_PANEL_BORDER_WIDTH)
        self.status_panel.grid(row=0, column=0, padx=STATUS_PANEL_PADX, pady=STATUS_PANEL_PADY, sticky="ew")
        self.status_panel.grid_columnconfigure(0, weight=1)

        top_row = ctk.CTkFrame(self.status_panel, fg_color="transparent")
        top_row.grid(row=0, column=0, padx=STATUS_PANEL_ROW_PADX, pady=STATUS_PANEL_TOP_ROW_PADY, sticky="ew")
        top_row.grid_columnconfigure(0, weight=1)
        top_row.grid_columnconfigure(1, weight=0)
        top_row.grid_columnconfigure(2, weight=0)

        self.lbl_status = ctk.CTkLabel(
            top_row, text="", font=(FONT_FAMILY_PRIMARY, STATUS_PANEL_STATUS_FONT_SIZE, "normal"), anchor="w"
        )
        self.lbl_status.grid(row=0, column=0, sticky="w")

        self.lbl_percent = ctk.CTkLabel(
            top_row, text="0%", font=(FONT_FAMILY_PRIMARY, STATUS_PANEL_PERCENT_FONT_SIZE, "bold"), anchor="e"
        )
        self.lbl_percent.grid(row=0, column=1, sticky="e", padx=STATUS_PANEL_PERCENT_PADX)

        red_btn = get_button_tokens("red")
        self.btn_cancel = ctk.CTkButton(
            top_row,
            text="✕",
            width=STATUS_PANEL_CANCEL_SIZE,
            height=STATUS_PANEL_CANCEL_SIZE,
            corner_radius=STATUS_PANEL_CANCEL_RADIUS,
            fg_color=red_btn["bg"],
            hover_color=red_btn["hover"],
            border_width=STATUS_PANEL_BORDER_WIDTH,
            border_color=red_btn["border"],
            text_color=red_btn["text"],
            font=(FONT_FAMILY_PRIMARY, STATUS_PANEL_CANCEL_FONT_SIZE, "bold"),
        )
        self.btn_cancel.grid(row=0, column=2, sticky="e")
        self.btn_cancel.grid_remove()

        self.progress_bar = GradientProgressBar(self.status_panel, height=STATUS_PANEL_PROGRESS_HEIGHT, corner_radius=STATUS_PANEL_PROGRESS_RADIUS)
        self.progress_bar.grid(row=1, column=0, padx=STATUS_PANEL_ROW_PADX, pady=STATUS_PANEL_PROGRESS_PADY, sticky="ew")
        self.progress_bar.set(0.0)

        self.file_row = ctk.CTkFrame(self.status_panel, fg_color="transparent")
        self.file_row.grid(row=2, column=0, padx=STATUS_PANEL_ROW_PADX, pady=STATUS_PANEL_FILE_ROW_PADY, sticky="ew")
        self.file_row.grid_columnconfigure(1, weight=1)

        self.lbl_processing_prefix = ctk.CTkLabel(
            self.file_row, text="", font=(FONT_FAMILY_PRIMARY, STATUS_PANEL_FILE_PREFIX_FONT_SIZE, "bold"), anchor="w"
        )
        self.lbl_processing_prefix.grid(row=0, column=0, sticky="w", padx=(0, STATUS_PANEL_PREFIX_GAP))

        self.lbl_current_file = ctk.CTkLabel(
            self.file_row,
            text="",
            font=(FONT_FAMILY_PRIMARY, STATUS_PANEL_FILE_TEXT_FONT_SIZE, "normal"),
            anchor="w",
            justify="left",
            wraplength=STATUS_PANEL_FILE_WRAP_DEFAULT,
        )
        self.lbl_current_file.grid(row=0, column=1, sticky="ew")

        self.status_panel.bind("<Configure>", self._on_panel_resize)

        # Estados de traduccion
        self._processing_label_text = ""
        self._btn_cancel_full_text = ""
        self._tr = None
        self._key_status_waiting = "status_waiting"
        self._key_status_reading = "status_reading"
        self._key_status_done = "status_done_panel"
        self._key_processing_label = "processing_label"
        self._key_btn_cancel = "btn_cancel"

        self.lbl_processing_prefix.configure(text="")
        self.lbl_current_file.configure(text="")
        self._mode = "idle"
        self._set_status("", with_dots=True)
        self.apply_theme(self._current_theme)

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

    def apply_theme(self, theme_name: str):
        self._current_theme = theme_name
        theme = get_theme_tokens(theme_name)
        red_btn = get_button_tokens("red")

        try:
            self.status_panel.configure(fg_color=theme["bg_card"], border_color=theme["border_subtle"], border_width=STATUS_PANEL_BORDER_WIDTH)
        except Exception:
            self.status_panel.configure(fg_color=theme["bg_card"])

        self.lbl_status.configure(text_color=theme["text_primary"])
        self.lbl_percent.configure(text_color=theme["text_primary"])
        self.lbl_processing_prefix.configure(text_color=theme["accent_blue"])
        self.lbl_current_file.configure(text_color=theme["text_secondary"])
        self.btn_cancel.configure(
            fg_color=red_btn["bg"],
            hover_color=red_btn["hover"],
            border_color=red_btn["border"],
            text_color=red_btn["text"]
        )

        self.progress_bar.set_colors(
            track=theme["progress_track"],
            border=theme["progress_border"],
            stops=[
                (0.00, theme["progress_gradient_start"]),
                (0.55, theme["progress_gradient_mid"]),
                (1.00, theme["progress_gradient_end"]),
            ]
        )
        self.progress_bar.set(self.current_progress / 100.0)

    def _on_panel_resize(self, event=None):
        try:
            panel_w = int(self.status_panel.winfo_width())
        except Exception:
            return

        usable = max(STATUS_PANEL_MIN_USABLE_WIDTH, panel_w - (STATUS_PANEL_ROW_PADX * 2))
        try:
            prefix_w = int(self.lbl_processing_prefix.winfo_reqwidth()) + 6
        except Exception:
            prefix_w = 0

        wrap = max(STATUS_PANEL_MIN_WRAP, usable - prefix_w)
        try:
            self.lbl_current_file.configure(wraplength=wrap)
        except Exception:
            pass

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
        self._dots_after_id = self.after(STATUS_PANEL_DOTS_INTERVAL_MS, self._tick_dots)

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
        self._dots_after_id = self.after(STATUS_PANEL_DOTS_INTERVAL_MS, self._tick_dots)

    def get_min_visible_completion_delay_ms(self) -> int:
        if self._processing_started_at is None:
            return 0
        now = time.monotonic()
        min_end = self._processing_started_at + self._min_visible_s
        remaining = max(0.0, min_end - now)
        return int(remaining * 1000)

    def _start_progress_animation(self):
        if self._progress_after_id is None:
            self._last_tick = time.monotonic()
            self._progress_after_id = self.after(STATUS_PANEL_PROGRESS_TICK_MS, self._tick_progress)

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

        # Suavizado de progreso al final
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

        self._progress_after_id = self.after(STATUS_PANEL_PROGRESS_TICK_MS, self._tick_progress)

    @staticmethod
    def _ellipsize_middle(s: str, max_len: int = STATUS_PANEL_ELLIPSIS_MAX_LEN) -> str:
        s = (s or "").strip()
        if len(s) <= max_len:
            return s
        keep = max_len - 1
        left = keep // 2
        right = keep - left
        return f"{s[:left]}…{s[-right:]}"

    def set_progress(self, percentage: float, file_context: str | None = None):
        new_target = float(max(0, min(100, int(percentage))))

        if new_target >= 100 and self._min_end_time is not None:
            now = time.monotonic()
            self._forced_end_time = self._min_end_time if now < self._min_end_time else None

        self.target_progress = new_target
        self._start_progress_animation()

        if file_context and self._mode == "processing":
            path_txt = self._ellipsize_middle(str(file_context), max_len=STATUS_PANEL_CONTEXT_MAX_LEN)
            self.lbl_current_file.configure(text=path_txt)

            prefix = self._processing_label_text or _translate_status(self._tr, self._key_processing_label)
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
            # Reseteo de tiempos para calculo UX
            self._processing_started_at = time.monotonic()
            self._min_end_time = self._processing_started_at + self._min_visible_s
            self._forced_end_time = None

            self.lbl_processing_prefix.configure(text="")
            self.lbl_current_file.configure(text="")

            if mode == "indeterminate":
                self._mode = "indeterminate"
                self.lbl_percent.configure(text="")
                self.progress_bar.start_indeterminate()

                base = text or _translate_status(self._tr, "progress_processing_text")
                self._set_status(base, with_dots=True)
            else:
                self._mode = "processing"
                self.progress_bar.stop_indeterminate()

                self.current_progress = 0.0
                self.target_progress = 0.0
                self.progress_bar.set(0.0)
                self.lbl_percent.configure(text="0%")

                base = _translate_status(self._tr, self._key_status_reading)
                self._set_status(base, with_dots=True)

            self.btn_cancel.grid()
            return

        self.btn_cancel.grid_remove()
        self.progress_bar.stop_indeterminate()

        if final_status == "success":
            self._mode = "done"
            base = _translate_status(self._tr, self._key_status_done)
            self._set_status(base, with_dots=False)

            self.current_progress = 100.0
            self.target_progress = 100.0
            self.progress_bar.set(1.0)
            self.lbl_percent.configure(text="100%")
            self.lbl_processing_prefix.configure(text="")
            self.lbl_current_file.configure(text="")

            self.after(STATUS_PANEL_SUCCESS_RESET_DELAY_MS, self.back_to_idle)
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

        base = _translate_status(self._tr, self._key_status_waiting)
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