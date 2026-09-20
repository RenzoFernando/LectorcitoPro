from __future__ import annotations

import time

import customtkinter as ctk

from i18n.translations import translate_default
from view.gradient_progress import GradientProgressBar
from view.sidebars import BlendedRoundedFrame
from view.ui_constants import (
    FONT_BODY,
    FONT_FAMILY_PRIMARY,
    FONT_LABEL,
    STATUS_PANEL_BORDER_WIDTH,
    STATUS_PANEL_CANCEL_FONT_SIZE,
    STATUS_PANEL_CANCEL_RADIUS,
    STATUS_PANEL_CANCEL_SIZE,
    STATUS_PANEL_CONTEXT_MAX_LEN,
    STATUS_PANEL_CORNER_RADIUS,
    STATUS_PANEL_DEFAULT_MIN_VISIBLE_SECONDS,
    STATUS_PANEL_DETAILS_HEIGHT,
    STATUS_PANEL_DOTS_INTERVAL_MS,
    STATUS_PANEL_FILE_PREFIX_FONT_SIZE,
    STATUS_PANEL_FILE_TEXT_FONT_SIZE,
    STATUS_PANEL_PROGRESS_HEIGHT,
    STATUS_PANEL_PROGRESS_RADIUS,
    STATUS_PANEL_PROGRESS_TICK_MS,
    get_theme_tokens,
)

# =============================================================================
# PANEL DE ESTADO Y PROGRESO
# =============================================================================


def _translate_status(tr_callable, key: str) -> str:
    if callable(tr_callable):
        try:
            return tr_callable(key)
        except Exception:
            pass
    return translate_default(key)


class StatusPanel(ctk.CTkFrame):
    def __init__(
        self, parent, *, min_visible_seconds: float = STATUS_PANEL_DEFAULT_MIN_VISIBLE_SECONDS
    ):
        theme = get_theme_tokens("Light")
        super().__init__(parent, fg_color="transparent", bg_color=theme["bg_base"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._min_visible_s = float(min_visible_seconds)
        self._processing_started_at: float | None = None
        self._min_end_time: float | None = None
        self._forced_end_time: float | None = None
        self._current_theme = "Light"
        self._mode = "idle"
        self._status_base = ""
        self._dots_after_id = None
        self._dots_phase = 1
        self._tr = None

        self.current_progress = 0.0
        self.target_progress = 0.0
        self._progress_after_id = None
        self._last_tick = None
        self._current_file = ""
        self._current_report = ""

        self.status_panel = BlendedRoundedFrame(
            self,
            outside_bg=theme["bg_base"],
            fill_color=theme["bg_panel"],
            corner_radius=STATUS_PANEL_CORNER_RADIUS,
            border_width=STATUS_PANEL_BORDER_WIDTH,
            border_color=theme["card_border"],
            content_inset=12,
        )
        self.status_panel.grid(row=0, column=0, sticky="nsew")

        content = self.status_panel.content_frame
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(4, weight=1)

        self.lbl_title = ctk.CTkLabel(
            content,
            text="",
            font=FONT_LABEL,
            anchor="w",
            fg_color="transparent",
        )
        self.lbl_title.grid(row=0, column=0, sticky="ew", pady=(0, 7))

        self.state_row = ctk.CTkFrame(
            content,
            fg_color=theme["surface_alt"],
            border_width=1,
            border_color=theme["border_subtle"],
            corner_radius=8,
        )
        self.state_row.grid(row=1, column=0, sticky="ew")
        self.state_row.grid_columnconfigure(1, weight=1)

        self.state_dot = ctk.CTkFrame(
            self.state_row,
            width=8,
            height=8,
            corner_radius=4,
            fg_color=theme["text_muted"],
        )
        self.state_dot.grid(row=0, column=0, sticky="w", padx=(10, 8), pady=6)
        self.state_dot.grid_propagate(False)

        self.lbl_status = ctk.CTkLabel(
            self.state_row,
            text="",
            font=(FONT_BODY[0], 11, "normal"),
            anchor="w",
            fg_color="transparent",
        )
        self.lbl_status.grid(row=0, column=1, sticky="ew", pady=5)

        self.btn_cancel = ctk.CTkButton(
            self.state_row,
            text="×",
            width=STATUS_PANEL_CANCEL_SIZE,
            height=STATUS_PANEL_CANCEL_SIZE,
            corner_radius=STATUS_PANEL_CANCEL_RADIUS,
            border_width=1,
            font=(FONT_BODY[0], STATUS_PANEL_CANCEL_FONT_SIZE + 2, "bold"),
        )
        self.btn_cancel.grid(row=0, column=2, sticky="e", padx=(8, 6), pady=4)
        self.btn_cancel.grid_remove()

        self.progress_meta = ctk.CTkFrame(content, fg_color="transparent")
        self.progress_meta.grid(row=2, column=0, sticky="ew", pady=(15, 5))
        self.progress_meta.grid_columnconfigure(0, weight=1)

        self.lbl_progress = ctk.CTkLabel(
            self.progress_meta,
            text="",
            font=(FONT_FAMILY_PRIMARY, 12, "bold"),
            anchor="w",
            fg_color="transparent",
        )
        self.lbl_progress.grid(row=0, column=0, sticky="w")

        self.lbl_percent = ctk.CTkLabel(
            self.progress_meta,
            text="0%",
            font=(FONT_FAMILY_PRIMARY, 12, "bold"),
            anchor="e",
            fg_color="transparent",
        )
        self.lbl_percent.grid(row=0, column=1, sticky="e")

        self.progress_bar = GradientProgressBar(
            content,
            height=STATUS_PANEL_PROGRESS_HEIGHT,
            corner_radius=STATUS_PANEL_PROGRESS_RADIUS,
        )
        self.progress_bar.grid(row=3, column=0, sticky="ew")
        self.progress_bar.set(0.0)

        # El espacio de detalles es fijo para que el boton destructivo no cambie de posicion.
        self.details_slot = ctk.CTkFrame(
            content,
            height=STATUS_PANEL_DETAILS_HEIGHT,
            fg_color="transparent",
        )
        self.details_slot.grid(row=4, column=0, sticky="nsew", pady=(12, 0))
        self.details_slot.grid_propagate(False)
        self.details_slot.grid_columnconfigure(0, weight=1)

        self.details_separator = ctk.CTkFrame(
            self.details_slot,
            height=1,
            corner_radius=0,
            fg_color=theme["separator_line"],
        )
        self.details_separator.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.details_separator.grid_remove()

        self.details_frame = ctk.CTkFrame(self.details_slot, fg_color="transparent")
        self.details_frame.grid(row=1, column=0, sticky="new")
        self.details_frame.grid_columnconfigure(0, weight=1)

        self.file_block, self.lbl_file_caption, self.lbl_current_file = self._create_detail_block(
            self.details_frame, row=0
        )
        (
            self.report_block,
            self.lbl_report_caption,
            self.lbl_current_report,
        ) = self._create_detail_block(self.details_frame, row=1)

        self.status_panel.bind("<Configure>", self._on_panel_resize, add="+")
        self.apply_theme(self._current_theme)
        self.back_to_idle()

    def _create_detail_block(self, parent, *, row: int):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 7 if row == 0 else 0))
        frame.grid_columnconfigure(0, weight=1)

        caption = ctk.CTkLabel(
            frame,
            text="",
            font=(FONT_FAMILY_PRIMARY, STATUS_PANEL_FILE_PREFIX_FONT_SIZE, "bold"),
            anchor="w",
            fg_color="transparent",
        )
        caption.grid(row=0, column=0, sticky="ew")

        value = ctk.CTkLabel(
            frame,
            text="",
            font=(FONT_FAMILY_PRIMARY, STATUS_PANEL_FILE_TEXT_FONT_SIZE, "normal"),
            anchor="w",
            justify="left",
            wraplength=250,
            fg_color="transparent",
        )
        value.grid(row=1, column=0, sticky="ew", pady=(1, 0))
        return frame, caption, value

    def set_translator(self, tr_callable):
        self._tr = tr_callable
        self.refresh_texts()

    def refresh_texts(self):
        self.lbl_title.configure(text=_translate_status(self._tr, "status_title"))
        self.lbl_progress.configure(text=_translate_status(self._tr, "progress_global"))
        self.lbl_file_caption.configure(text=_translate_status(self._tr, "status_file_label"))
        self.lbl_report_caption.configure(text=_translate_status(self._tr, "status_report_label"))

        if self._mode == "processing":
            self._status_base = _translate_status(self._tr, "status_reading")
        elif self._mode == "cancelling":
            self._status_base = _translate_status(self._tr, "status_cancelling")
        elif self._mode == "done":
            self._status_base = _translate_status(self._tr, "status_done_panel")
        elif self._mode == "indeterminate":
            self._status_base = _translate_status(self._tr, "progress_processing_text")
        else:
            self._status_base = _translate_status(self._tr, "status_waiting")

        if self._dots_after_id is None:
            self.lbl_status.configure(text=self._status_base)
        self._apply_state_colors()

    def set_backdrop_color(self, color: str):
        self.configure(bg_color=color)
        self.status_panel.configure(outside_bg=color)

    def set_backdrop_provider(self, backdrop_provider):
        return None

    def refresh_backdrop(self):
        return None

    def apply_theme(self, theme_name: str):
        self._current_theme = theme_name
        theme = get_theme_tokens(theme_name)
        self.configure(bg_color=theme["bg_base"])
        self.status_panel.configure(
            outside_bg=theme["bg_base"],
            fill_color=theme["bg_panel"],
            border_color=theme["card_border"],
            border_width=STATUS_PANEL_BORDER_WIDTH,
        )

        self.lbl_title.configure(text_color=theme["text_primary"])
        self.lbl_progress.configure(text_color=theme["text_primary"])
        self.lbl_percent.configure(text_color=theme["accent_blue_icon"])
        self.lbl_file_caption.configure(text_color=theme["text_secondary"])
        self.lbl_report_caption.configure(text_color=theme["text_secondary"])
        self.lbl_current_file.configure(text_color=theme["text_secondary"])
        self.lbl_current_report.configure(text_color=theme["text_secondary"])
        self.details_separator.configure(fg_color=theme["separator_line"])
        self.state_row.configure(
            fg_color=theme["surface_alt"],
            border_color=theme["border_subtle"],
        )

        self.btn_cancel.configure(
            fg_color=theme["danger_bg"],
            hover_color="#FEE2E2" if str(theme_name).lower() != "dark" else "#5F2121",
            border_color=theme["danger_border"],
            text_color=theme["danger_red_deep"],
        )

        self.progress_bar.set_colors(
            track=theme["progress_track"],
            border=theme["progress_border"],
            stops=[(0.0, theme["progress_fill"]), (1.0, theme["progress_fill"])],
        )
        self.progress_bar.set(self.current_progress / 100.0)
        self._apply_state_colors()

    def _apply_state_colors(self):
        theme = get_theme_tokens(self._current_theme)
        if self._mode == "done":
            color = theme["success_green"]
        elif self._mode == "cancelling":
            color = theme["danger_red_deep"]
        elif self._mode in {"processing", "indeterminate"}:
            color = theme["accent_blue_icon"]
        else:
            color = theme["text_muted"]

        self.state_dot.configure(fg_color=color)
        status_color = color if self._mode != "idle" else theme["text_secondary"]
        self.lbl_status.configure(text_color=status_color)

    def _update_detail_visibility(self):
        has_file = bool(self._current_file)
        has_report = bool(self._current_report)

        if has_file:
            self.lbl_current_file.configure(text=self._current_file)
            self.file_block.grid()
        else:
            self.lbl_current_file.configure(text="")
            self.file_block.grid_remove()

        if has_report:
            self.lbl_current_report.configure(text=self._current_report)
            self.report_block.grid()
        else:
            self.lbl_current_report.configure(text="")
            self.report_block.grid_remove()

        if has_file or has_report:
            self.details_separator.grid()
            self.details_frame.grid()
        else:
            self.details_separator.grid_remove()
            self.details_frame.grid_remove()

    def _on_panel_resize(self, event=None):
        try:
            panel_w = max(160, int(self.status_panel.winfo_width()) - 28)
        except Exception:
            return
        for label in (self.lbl_current_file, self.lbl_current_report):
            try:
                label.configure(wraplength=panel_w)
            except Exception:
                pass

    @staticmethod
    def _truncate_context(value: str) -> str:
        value = (value or "").strip()
        if len(value) <= STATUS_PANEL_CONTEXT_MAX_LEN:
            return value
        keep = STATUS_PANEL_CONTEXT_MAX_LEN - 1
        left = keep // 2
        right = keep - left
        return f"{value[:left]}…{value[-right:]}"

    def _set_status(self, base_text: str, *, with_dots: bool):
        self._status_base = base_text or ""
        if with_dots:
            self._dots_phase = 1
            self._start_dots()
        else:
            self._stop_dots()
            self.lbl_status.configure(text=self._status_base)
        self._apply_state_colors()

    def _start_dots(self):
        self._stop_dots()
        self.lbl_status.configure(text=f"{self._status_base}.")
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
            self._dots_after_id = None
            return
        dots = "." * self._dots_phase
        self._dots_phase = 1 if self._dots_phase >= 3 else self._dots_phase + 1
        self.lbl_status.configure(text=f"{self._status_base}{dots}")
        self._dots_after_id = self.after(STATUS_PANEL_DOTS_INTERVAL_MS, self._tick_dots)

    def get_min_visible_completion_delay_ms(self) -> int:
        if self._processing_started_at is None:
            return 0
        remaining = max(0.0, (self._processing_started_at + self._min_visible_s) - time.monotonic())
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
            self._progress_after_id = None
            return

        now = time.monotonic()
        dt = now - (self._last_tick or now)
        self._last_tick = now

        if self._forced_end_time is not None and now < self._forced_end_time:
            self.target_progress = max(self.target_progress, 98.0)
        elif self._forced_end_time is not None:
            self._forced_end_time = None
            self.target_progress = 100.0

        diff = self.target_progress - self.current_progress
        if abs(diff) < 0.05:
            self.current_progress = self.target_progress
        else:
            self.current_progress += diff * min(1.0, dt * 10.0)

        self.progress_bar.set(self.current_progress / 100.0)
        if self._mode != "indeterminate":
            self.lbl_percent.configure(text=f"{int(self.current_progress)}%")

        if abs(self.target_progress - self.current_progress) < 0.05:
            self.current_progress = self.target_progress
            self.progress_bar.set(self.current_progress / 100.0)
            if self._mode != "indeterminate":
                self.lbl_percent.configure(text=f"{int(self.current_progress)}%")
            self._progress_after_id = None
            return

        self._progress_after_id = self.after(STATUS_PANEL_PROGRESS_TICK_MS, self._tick_progress)

    def set_progress(
        self,
        percentage: float,
        file_context: str | None = None,
        report_context: str | None = None,
    ):
        new_target = float(max(0.0, min(100.0, float(percentage))))
        if new_target >= 100 and self._min_end_time is not None:
            now = time.monotonic()
            self._forced_end_time = self._min_end_time if now < self._min_end_time else None

        self.target_progress = new_target
        if new_target >= 100:
            self.btn_cancel.grid_remove()
        self._start_progress_animation()

        if file_context is not None:
            self._current_file = self._truncate_context(str(file_context))
        if report_context is not None:
            self._current_report = self._truncate_context(str(report_context))
        self._update_detail_visibility()

    def set_active(
        self,
        is_active: bool,
        *,
        mode: str = "determinate",
        text: str | None = None,
        final_status: str | None = None,
    ):
        if is_active:
            self._processing_started_at = time.monotonic()
            self._min_end_time = self._processing_started_at + self._min_visible_s
            self._forced_end_time = None
            self._current_file = ""
            self._current_report = ""
            self._update_detail_visibility()
            self.btn_cancel.configure(state="normal")

            if mode == "indeterminate":
                self.btn_cancel.grid_remove()
                self._mode = "indeterminate"
                self.lbl_percent.configure(text="")
                self.progress_bar.start_indeterminate()
                self._set_status(
                    text or _translate_status(self._tr, "progress_processing_text"),
                    with_dots=True,
                )
            else:
                self.btn_cancel.grid()
                self._mode = "processing"
                self.progress_bar.stop_indeterminate()
                self.current_progress = 0.0
                self.target_progress = 0.0
                self.progress_bar.set(0.0)
                self.lbl_percent.configure(text="0%")
                self._set_status(_translate_status(self._tr, "status_reading"), with_dots=True)
            return

        self.btn_cancel.grid_remove()
        self.progress_bar.stop_indeterminate()
        if final_status == "success":
            self._mode = "done"
            self.current_progress = 100.0
            self.target_progress = 100.0
            self.progress_bar.set(1.0)
            self.lbl_percent.configure(text="100%")
            # El reporte deja de estar "en generacion" al completar la lectura.
            # Conservamos el archivo actual como contexto util y retiramos ese bloque.
            self._current_report = ""
            self._update_detail_visibility()
            self._set_status(_translate_status(self._tr, "status_done_panel"), with_dots=False)
        else:
            self.back_to_idle()

    def set_cancelling(self):
        if self._mode not in {"processing", "indeterminate", "cancelling"}:
            return
        self._mode = "cancelling"
        self.btn_cancel.configure(state="disabled")
        self._set_status(_translate_status(self._tr, "status_cancelling"), with_dots=True)

    def back_to_idle(self):
        if not self.winfo_exists():
            return

        self._mode = "idle"
        self._processing_started_at = None
        self._min_end_time = None
        self._forced_end_time = None
        self._stop_progress_animation()
        self.progress_bar.stop_indeterminate()
        self.current_progress = 0.0
        self.target_progress = 0.0
        self.progress_bar.set(0.0)
        self.lbl_percent.configure(text="0%")
        self._current_file = ""
        self._current_report = ""
        self._update_detail_visibility()
        self.btn_cancel.configure(state="normal")
        self.btn_cancel.grid_remove()
        self._set_status(_translate_status(self._tr, "status_waiting"), with_dots=True)

    def cleanup(self):
        self._stop_dots()
        self._stop_progress_animation()
        try:
            self.progress_bar.stop_indeterminate()
        except Exception:
            pass
