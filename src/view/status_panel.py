from __future__ import annotations

import math
import time
import tkinter.font as tkfont

import customtkinter as ctk

from i18n.translations import translate_default
from view.gradient_progress import GradientProgressBar
from view.sidebars import BlendedRoundedFrame
from view.ui_assets import load_cancel_reading_icon, load_status_dot_icon
from view.ui_constants import (
    FONT_BODY,
    FONT_FAMILY_PRIMARY,
    FONT_LABEL,
    STATUS_PANEL_BORDER_WIDTH,
    STATUS_PANEL_CANCEL_RADIUS,
    STATUS_PANEL_CANCEL_SIZE,
    STATUS_PANEL_CORNER_RADIUS,
    STATUS_PANEL_DEFAULT_MIN_VISIBLE_SECONDS,
    STATUS_PANEL_DOTS_INTERVAL_MS,
    STATUS_PANEL_FILE_TEXT_FONT_SIZE,
    STATUS_PANEL_PROGRESS_CRUISE_CENTER_BOOST,
    STATUS_PANEL_PROGRESS_CRUISE_EDGE_PER_SECOND,
    STATUS_PANEL_PROGRESS_HEIGHT,
    STATUS_PANEL_PROGRESS_LEAD_DAMPING_SPAN,
    STATUS_PANEL_PROGRESS_MAX_STALL_BOOST,
    STATUS_PANEL_PROGRESS_MIN_CRUISE_PER_SECOND,
    STATUS_PANEL_PROGRESS_RADIUS,
    STATUS_PANEL_PROGRESS_STALL_BOOST_AFTER_SECONDS,
    STATUS_PANEL_PROGRESS_TICK_MS,
    STATUS_PANEL_PROGRESS_VISUAL_LIMIT,
    get_theme_tokens,
)
from view.ui_scaling import canvas_font

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


class _CenteredIconButton(ctk.CTkButton):
    """Boton iconografico nativo con SVG centrado y sin estado visual recursivo."""

    def __init__(
        self,
        parent,
        *,
        width: int,
        height: int,
        corner_radius: int,
        border_width: int = 1,
        command=None,
    ):
        super().__init__(
            parent,
            text="",
            image=None,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color="#FCA5A5",
            fg_color="#FEF2F2",
            hover_color="#FEE2E2",
            text_color="#DC2626",
            border_spacing=0,
            anchor="center",
            command=command,
        )


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
        self._status_layout_after_id = None
        self._tr = None

        self.current_progress = 0.0
        self.target_progress = 0.0
        self._visual_progress_target = 0.0
        self._progress_after_id = None
        self._last_tick = None
        self._last_real_progress_at = None
        self._current_file = ""
        self._current_report = ""
        self._detail_wrap_width = 220

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

        self._state_icon_image = None
        self.state_dot = ctk.CTkLabel(
            self.state_row,
            text="",
            width=10,
            height=10,
            fg_color="transparent",
            bg_color="transparent",
            anchor="center",
        )
        self.state_dot.grid(row=0, column=0, sticky="w", padx=(10, 8), pady=6)

        self.lbl_status = ctk.CTkLabel(
            self.state_row,
            text="",
            font=(FONT_BODY[0], 11, "normal"),
            anchor="w",
            fg_color="transparent",
        )
        self.lbl_status.grid(row=0, column=1, sticky="ew", pady=5)
        self.state_row.bind("<Configure>", self._schedule_status_label_width_sync, add="+")

        self._cancel_icon_image = None
        self._cancel_bg = theme["danger_bg"]
        self._cancel_hover_bg = "#FEE2E2"
        self.btn_cancel = _CenteredIconButton(
            self.state_row,
            width=STATUS_PANEL_CANCEL_SIZE,
            height=STATUS_PANEL_CANCEL_SIZE,
            corner_radius=STATUS_PANEL_CANCEL_RADIUS,
            border_width=1,
        )
        self.btn_cancel.grid(row=0, column=2, sticky="e", padx=(8, 6), pady=4)
        self.btn_cancel.grid_remove()

        self.progress_meta = ctk.CTkFrame(content, fg_color="transparent")
        self.progress_meta.grid(row=2, column=0, sticky="ew", pady=(10, 4))
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

        # Los detalles se muestran solo cuando existe contexto de archivo o reporte.
        self.details_slot = ctk.CTkFrame(content, fg_color="transparent")
        self.details_slot.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        self.details_slot.grid_columnconfigure(0, weight=1)
        self.details_slot.grid_rowconfigure(1, weight=1)

        self.details_separator = ctk.CTkFrame(
            self.details_slot,
            height=1,
            corner_radius=0,
            fg_color=theme["separator_line"],
        )
        self.details_separator.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.details_separator.grid_remove()

        self.details_frame = ctk.CTkFrame(self.details_slot, fg_color="transparent")
        self.details_frame.grid(row=1, column=0, sticky="nsew")
        self.details_frame.grid_columnconfigure(0, weight=1)
        self.details_frame.grid_rowconfigure(0, weight=1)

        self.file_block, self.lbl_current_file = self._create_detail_value(
            self.details_frame,
            row=0,
            font_weight="normal",
            pady=(0, 8),
            sticky="new",
        )
        self.report_block, self.lbl_current_report = self._create_detail_value(
            self.details_frame,
            row=1,
            font_weight="bold",
            pady=(6, 0),
            sticky="sew",
        )

        self.details_frame.bind("<Configure>", self._on_panel_resize, add="+")
        self.apply_theme(self._current_theme)
        self.back_to_idle()

    def _create_detail_value(
        self,
        parent,
        *,
        row: int,
        font_weight: str,
        pady,
        sticky: str,
    ):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, sticky=sticky, pady=pady)
        frame.grid_columnconfigure(0, weight=1)

        detail_font = ctk.CTkFont(
            family=FONT_FAMILY_PRIMARY,
            size=STATUS_PANEL_FILE_TEXT_FONT_SIZE,
            weight=font_weight,
        )
        value = ctk.CTkLabel(
            frame,
            text="",
            font=detail_font,
            anchor="w",
            justify="left",
            wraplength=self._detail_wrap_width,
            fg_color="transparent",
        )
        value._detail_font = detail_font
        value._detail_font_weight = font_weight
        value.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        return frame, value

    def _schedule_status_label_width_sync(self, event=None):
        if self._status_layout_after_id is not None:
            return
        try:
            self._status_layout_after_id = self.after_idle(self._sync_status_label_width)
        except Exception:
            self._status_layout_after_id = None

    def _sync_status_label_width(self):
        self._status_layout_after_id = None
        try:
            if not self.winfo_exists():
                return
            _, _, cell_width, _ = self.state_row.grid_bbox(1, 0)
            if cell_width > 1:
                # CTkLabel puede conservar un ancho interno menor al asignado por grid
                # despues de cambios dinamicos de texto. Sincronizarlo evita recortes.
                self.lbl_status.configure(width=int(cell_width))
        except Exception:
            pass

    def set_translator(self, tr_callable):
        self._tr = tr_callable
        self.refresh_texts()

    def refresh_texts(self):
        self.lbl_title.configure(text=_translate_status(self._tr, "status_title"))
        self.lbl_progress.configure(text=_translate_status(self._tr, "progress_global"))

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
        self._schedule_status_label_width_sync()

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
        self.lbl_progress.configure(text_color=theme["text_muted"])
        self.lbl_current_file.configure(text_color=theme["text_secondary"])
        self.lbl_current_report.configure(text_color=theme["text_primary"])
        self.details_separator.configure(fg_color=theme["separator_line"])
        self.state_row.configure(
            fg_color=theme["surface_alt"],
            border_color=theme["border_subtle"],
        )

        self._cancel_icon_image = load_cancel_reading_icon(
            (14, 14),
            light_color=theme["danger_red_deep"],
            dark_color=theme["danger_red_deep"],
        )
        self._cancel_bg = theme["danger_bg"]
        self._cancel_hover_bg = "#FEE2E2" if str(theme_name).lower() != "dark" else "#5F2121"
        self.btn_cancel.configure(
            image=self._cancel_icon_image,
            fg_color=self._cancel_bg,
            hover_color=self._cancel_hover_bg,
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

        self._state_icon_image = load_status_dot_icon(
            (10, 10),
            light_color=color,
            dark_color=color,
        )
        self.state_dot.configure(image=self._state_icon_image)
        status_color = color if self._mode != "idle" else theme["text_secondary"]
        self.lbl_status.configure(text_color=status_color)
        percent_color = (
            theme["accent_blue_icon"]
            if self._mode in {"processing", "indeterminate", "done"}
            else theme["text_primary"]
        )
        self.lbl_percent.configure(text_color=percent_color)

    @staticmethod
    def _path_tokens(value: str) -> list[str]:
        tokens = []
        current = []
        for char in value:
            current.append(char)
            if char in {"\\", "/"}:
                tokens.append("".join(current))
                current = []
        if current:
            tokens.append("".join(current))
        return tokens

    @staticmethod
    def _split_token_to_width(token: str, max_width: int, measure) -> list[str]:
        if not token or measure(token) <= max_width:
            return [token] if token else []

        chunks = []
        current = ""
        for char in token:
            candidate = f"{current}{char}"
            if current and measure(candidate) > max_width:
                chunks.append(current)
                current = char
            else:
                current = candidate
        if current:
            chunks.append(current)
        return chunks

    def _wrap_context_path(self, value: str, label, max_width: int) -> str:
        value = (value or "").strip()
        if not value:
            return ""

        font_weight = getattr(label, "_detail_font_weight", "normal")
        try:
            font_spec = canvas_font(
                label,
                FONT_FAMILY_PRIMARY,
                STATUS_PANEL_FILE_TEXT_FONT_SIZE,
                font_weight,
            )
            measure_font = tkfont.Font(
                root=label,
                family=font_spec[0],
                size=font_spec[1],
                weight=font_spec[2],
            )
            measure = measure_font.measure
        except Exception:
            return value

        tokens = self._path_tokens(value)
        if len(tokens) <= 1:
            token_parts = self._split_token_to_width(value, max_width, measure)
            return "\n".join(token_parts) if token_parts else value

        lines = []
        current = ""
        for token in tokens:
            candidate = f"{current}{token}"
            if measure(candidate) <= max_width:
                current = candidate
                continue

            if current:
                lines.append(current)
                current = ""

            token_parts = self._split_token_to_width(token, max_width, measure)
            if not token_parts:
                continue
            lines.extend(token_parts[:-1])
            current = token_parts[-1]

        if current:
            lines.append(current)
        return "\n".join(lines)

    def _refresh_detail_texts(self):
        self.lbl_current_file.configure(
            text=self._wrap_context_path(
                self._current_file,
                self.lbl_current_file,
                self._detail_wrap_width,
            )
        )
        self.lbl_current_report.configure(
            text=self._wrap_context_path(
                self._current_report,
                self.lbl_current_report,
                self._detail_wrap_width,
            )
        )

    def _update_detail_visibility(self):
        has_file = bool(self._current_file)
        has_report = bool(self._current_report)

        if has_file:
            self.file_block.grid()
        else:
            self.file_block.grid_remove()

        if has_report:
            self.report_block.grid()
        else:
            self.report_block.grid_remove()

        self._refresh_detail_texts()

        if has_file or has_report:
            self.details_slot.grid()
            self.details_separator.grid()
            self.details_frame.grid()
        else:
            self.details_separator.grid_remove()
            self.details_frame.grid_remove()
            self.details_slot.grid_remove()

    def _on_panel_resize(self, event=None):
        try:
            frame_width = int(getattr(event, "width", 0) or self.details_frame.winfo_width())
            self._detail_wrap_width = max(140, frame_width - 16)
        except Exception:
            return
        for label in (self.lbl_current_file, self.lbl_current_report):
            try:
                label.configure(wraplength=self._detail_wrap_width)
            except Exception:
                pass
        self._refresh_detail_texts()

    @staticmethod
    def _truncate_context(value: str) -> str:
        # Se conserva el contexto completo; el ajuste visual se hace por separadores de ruta.
        return (value or "").strip()

    def _set_status(self, base_text: str, *, with_dots: bool):
        self._status_base = base_text or ""
        if with_dots:
            self._dots_phase = 1
            self._start_dots()
        else:
            self._stop_dots()
            self.lbl_status.configure(text=self._status_base)
        self._apply_state_colors()
        self._schedule_status_label_width_sync()

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

    @staticmethod
    def _progress_gaussian(progress: float) -> float:
        position = max(0.0, min(1.0, float(progress) / 100.0))
        return math.exp(-0.5 * ((position - 0.5) / 0.20) ** 2)

    def _advance_visual_progress_target(self, now: float, dt: float):
        if self._mode != "processing" or self.target_progress >= 100.0:
            return

        # La barra mantiene una inercia visual continua entre actualizaciones
        # reales. El progreso real sigue siendo la referencia y, cuanto mayor
        # sea la ventaja visual, mas se amortigua el avance sintetico.
        self._visual_progress_target = max(
            self._visual_progress_target,
            min(STATUS_PANEL_PROGRESS_VISUAL_LIMIT, self.target_progress + 1.0),
        )

        gaussian = self._progress_gaussian(self._visual_progress_target)
        drift_speed = STATUS_PANEL_PROGRESS_CRUISE_EDGE_PER_SECOND + (
            STATUS_PANEL_PROGRESS_CRUISE_CENTER_BOOST * gaussian
        )

        lead = max(0.0, self._visual_progress_target - self.target_progress)
        lead_damping = max(
            0.22,
            1.0 / (1.0 + (lead / STATUS_PANEL_PROGRESS_LEAD_DAMPING_SPAN)),
        )
        drift_speed *= lead_damping

        if self._last_real_progress_at is not None:
            stalled_for = max(0.0, now - self._last_real_progress_at)
            if stalled_for > STATUS_PANEL_PROGRESS_STALL_BOOST_AFTER_SECONDS:
                stall_boost = min(
                    STATUS_PANEL_PROGRESS_MAX_STALL_BOOST,
                    1.0 + (stalled_for - STATUS_PANEL_PROGRESS_STALL_BOOST_AFTER_SECONDS) * 0.055,
                )
                drift_speed *= stall_boost

        # Cerca del final la curva vuelve a desacelerar. Se conserva un minimo
        # de movimiento para que una operacion pesada no parezca congelada.
        if self._visual_progress_target > 88.0:
            remaining_factor = max(
                0.30,
                min(1.0, (100.0 - self._visual_progress_target) / 12.0),
            )
            drift_speed *= remaining_factor

        drift_speed = max(STATUS_PANEL_PROGRESS_MIN_CRUISE_PER_SECOND, drift_speed)
        self._visual_progress_target = min(
            STATUS_PANEL_PROGRESS_VISUAL_LIMIT,
            self._visual_progress_target + (drift_speed * dt),
        )

    def _tick_progress(self):
        if not self.winfo_exists():
            self._progress_after_id = None
            return

        now = time.monotonic()
        dt = max(0.0, min(0.25, now - (self._last_tick or now)))
        self._last_tick = now

        if self._forced_end_time is not None and now < self._forced_end_time:
            self.target_progress = max(self.target_progress, 98.0)
        elif self._forced_end_time is not None:
            self._forced_end_time = None
            self.target_progress = 100.0

        if self.target_progress >= 100.0:
            self._visual_progress_target = 100.0
        else:
            self._advance_visual_progress_target(now, dt)

        visual_target = max(self.target_progress, self._visual_progress_target)
        diff = visual_target - self.current_progress
        if diff > 0.05:
            # Los saltos del progreso real se absorben gradualmente con la misma
            # curva gaussiana, evitando avances bruscos entre archivos.
            gaussian = self._progress_gaussian(self.current_progress)
            catchup_rate = 3.2 + (5.8 * gaussian)
            self.current_progress += diff * min(1.0, dt * catchup_rate)
        elif abs(diff) <= 0.05:
            self.current_progress = max(self.current_progress, visual_target)

        self.current_progress = max(0.0, min(100.0, self.current_progress))
        self.progress_bar.set(self.current_progress / 100.0)
        self._set_percent_label()

        keep_cruising = self._mode == "processing" and self.target_progress < 100.0
        if not keep_cruising and abs(visual_target - self.current_progress) < 0.05:
            self.current_progress = max(self.current_progress, visual_target)
            self.progress_bar.set(self.current_progress / 100.0)
            self._set_percent_label()
            self._progress_after_id = None
            return

        self._progress_after_id = self.after(STATUS_PANEL_PROGRESS_TICK_MS, self._tick_progress)

    def _set_percent_label(self):
        if self._mode == "indeterminate":
            return
        display_value = int(round(self.current_progress))
        if self.target_progress < 100.0:
            display_value = min(99, display_value)
        self.lbl_percent.configure(text=f"{display_value}%")

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

        now = time.monotonic()
        self.target_progress = max(self.target_progress, new_target)
        self._last_real_progress_at = now
        if self.target_progress >= 100.0:
            self._visual_progress_target = 100.0
        # El boton permanece disponible hasta que el procesamiento finalice realmente.
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
                self._visual_progress_target = 0.0
                self._last_real_progress_at = time.monotonic()
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
            self._visual_progress_target = 100.0
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
        self._visual_progress_target = 0.0
        self._last_real_progress_at = None
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
        if self._status_layout_after_id is not None:
            try:
                self.after_cancel(self._status_layout_after_id)
            except Exception:
                pass
            self._status_layout_after_id = None
        try:
            self.progress_bar.stop_indeterminate()
        except Exception:
            pass
