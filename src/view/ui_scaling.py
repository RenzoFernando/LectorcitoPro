from __future__ import annotations

import sys
import tkinter.font as tkfont

import customtkinter as ctk

from view.ui_constants import MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT, SETTINGS_DIALOG_WIDTH, SETTINGS_DIALOG_HEIGHT, TAGS_DIALOG_WIDTH, TAGS_DIALOG_HEIGHT, PROFILES_DIALOG_WIDTH, PROFILES_DIALOG_HEIGHT


_STATE = {
    "user_scale": 1.0,
    "workarea": None,
    "auto_window_scale": 1.0,
    "auto_widget_scale": 1.0,
}


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def _read_method_scaling(widget, attribute: str) -> float | None:
    current = widget
    visited = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        getter = getattr(current, attribute, None)
        if callable(getter):
            try:
                value = float(getter())
                if value > 0:
                    return value
            except Exception:
                pass
        current = getattr(current, "master", None)
    return None


def _read_tk_scaling(widget, fallback: float = 1.0) -> float:
    try:
        tk_scale = float(widget.tk.call("tk", "scaling"))
        normalized = tk_scale / (96.0 / 72.0)
        if normalized > 0:
            return normalized
    except Exception:
        pass
    return float(fallback)


def get_widget_scaling(widget) -> float:
    widget_scale = _read_method_scaling(widget, "_get_widget_scaling")
    if widget_scale is not None:
        return widget_scale
    window_scale = _read_method_scaling(widget, "_get_window_scaling")
    if window_scale is not None:
        return window_scale
    return _read_tk_scaling(widget, 1.0)


def get_window_scaling(widget) -> float:
    window_scale = _read_method_scaling(widget, "_get_window_scaling")
    if window_scale is not None:
        return window_scale
    return get_widget_scaling(widget)


def scale_tk_value(widget, value):
    scale = get_widget_scaling(widget)
    if isinstance(value, tuple):
        return tuple(scale_tk_value(widget, item) for item in value)
    if isinstance(value, list):
        return [scale_tk_value(widget, item) for item in value]
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value == 0:
            return 0
        return max(1, int(round(value * scale))) if value > 0 else min(-1, int(round(value * scale)))
    if isinstance(value, float):
        return value * scale
    return value


def canvas_font(widget, family: str, logical_size: int, weight: str = "normal"):
    px = max(1, int(round(abs(logical_size) * get_widget_scaling(widget))))
    return family, -px, weight


def _font_object(widget, family: str, pixel_size: int, weight: str = "normal"):
    return tkfont.Font(root=widget, family=family, size=-max(1, int(pixel_size)), weight=weight)


def fit_canvas_font(widget, texts, family: str, base_size: int, min_size: int, max_width: int, max_height: int | None = None, weight: str = "normal"):
    if isinstance(texts, str):
        texts = [texts]
    clean_texts = [str(text or "") for text in texts]
    scale = get_widget_scaling(widget)
    start_px = max(1, int(round(abs(base_size) * scale)))
    min_px = max(1, int(round(abs(min_size) * scale)))
    if min_px > start_px:
        min_px = start_px
    available_width = max(1, int(max_width))
    available_height = None if max_height is None else max(1, int(max_height))

    selected_px = min_px
    for px in range(start_px, min_px - 1, -1):
        font = _font_object(widget, family, px, weight)
        width_ok = all(font.measure(text) <= available_width for text in clean_texts)
        height_ok = available_height is None or font.metrics("linespace") <= available_height
        if width_ok and height_ok:
            selected_px = px
            break

    return family, -selected_px, weight


def measure_canvas_text(widget, text: str, font_spec) -> tuple[int, int]:
    family = font_spec[0]
    raw_size = int(font_spec[1])
    weight = font_spec[2] if len(font_spec) > 2 else "normal"
    px = abs(raw_size)
    font = _font_object(widget, family, px, weight)
    return int(font.measure(str(text or ""))), int(font.metrics("linespace"))


def wrapped_line_count(widget, text: str, font_spec, max_width: int) -> int:
    family = font_spec[0]
    raw_size = int(font_spec[1])
    weight = font_spec[2] if len(font_spec) > 2 else "normal"
    font = _font_object(widget, family, abs(raw_size), weight)
    width = max(1, int(max_width))
    words = str(text or "").split()
    if not words:
        return 1

    lines = 1
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if font.measure(candidate) <= width:
            current = candidate
            continue
        if current:
            lines += 1
            current = ""
        if font.measure(word) <= width:
            current = word
            continue
        word_width = max(1, int(font.measure(word)))
        extra_lines = max(1, (word_width + width - 1) // width)
        lines += extra_lines - 1
        current = word
    return max(1, lines)


def _windows_monitor_workarea(widget, prefer_pointer: bool):
    if not sys.platform.startswith("win"):
        return None
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32

        class POINT(ctypes.Structure):
            _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", wintypes.LONG),
                ("top", wintypes.LONG),
                ("right", wintypes.LONG),
                ("bottom", wintypes.LONG),
            ]

        class MONITORINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("rcMonitor", RECT),
                ("rcWork", RECT),
                ("dwFlags", wintypes.DWORD),
            ]

        point = POINT()
        if prefer_pointer:
            if not user32.GetCursorPos(ctypes.byref(point)):
                raise RuntimeError
        else:
            hwnd = int(widget.winfo_id())
            rect = RECT()
            if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                point.x = int((rect.left + rect.right) / 2)
                point.y = int((rect.top + rect.bottom) / 2)
            elif not user32.GetCursorPos(ctypes.byref(point)):
                raise RuntimeError

        monitor = user32.MonitorFromPoint(point, 2)
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if not monitor or not user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
            raise RuntimeError
        work = info.rcWork
        return int(work.left), int(work.top), int(work.right), int(work.bottom), True
    except Exception:
        return None


def _generic_workarea(widget):
    try:
        x = int(widget.winfo_vrootx())
        y = int(widget.winfo_vrooty())
        w = int(widget.winfo_vrootwidth())
        h = int(widget.winfo_vrootheight())
        if w > 0 and h > 0:
            return x, y, x + w, y + h, False
    except Exception:
        pass
    try:
        w = int(widget.winfo_screenwidth())
        h = int(widget.winfo_screenheight())
        if w > 0 and h > 0:
            return 0, 0, w, h, False
    except Exception:
        pass
    return 0, 0, 1920, 1080, False


def _resolve_workarea(widget, prefer_pointer: bool):
    return _windows_monitor_workarea(widget, prefer_pointer) or _generic_workarea(widget)


def _compute_user_scale(logical_width: float, logical_height: float) -> float:
    critical_width = max(MAIN_WINDOW_WIDTH, SETTINGS_DIALOG_WIDTH, TAGS_DIALOG_WIDTH, PROFILES_DIALOG_WIDTH)
    critical_height = max(MAIN_WINDOW_HEIGHT, SETTINGS_DIALOG_HEIGHT, TAGS_DIALOG_HEIGHT, PROFILES_DIALOG_HEIGHT)
    fit_width = max(1.0, logical_width - 48.0) / max(1.0, float(critical_width))
    fit_height = max(1.0, logical_height - 96.0) / max(1.0, float(critical_height))
    fit_scale = min(fit_width, fit_height)
    screen_ratio = min(logical_width / 1920.0, logical_height / 1080.0)
    if screen_ratio >= 1.65:
        comfort_scale = 1.12
    elif screen_ratio >= 1.35:
        comfort_scale = 1.08
    elif screen_ratio >= 1.15:
        comfort_scale = 1.04
    else:
        comfort_scale = 1.0
    return _clamp(min(fit_scale, comfort_scale), 0.55, 1.12)


def configure_application_scaling(root, prefer_pointer: bool = True) -> bool:
    current_user_scale = float(_STATE.get("user_scale", 1.0) or 1.0)
    combined_window_scale = get_window_scaling(root)
    combined_widget_scale = _read_method_scaling(root, "_get_widget_scaling") or combined_window_scale
    auto_window_scale = combined_window_scale / current_user_scale if current_user_scale > 0 else combined_window_scale
    auto_widget_scale = combined_widget_scale / current_user_scale if current_user_scale > 0 else combined_widget_scale
    auto_window_scale = max(0.1, auto_window_scale)
    auto_widget_scale = max(0.1, auto_widget_scale)

    left, top, right, bottom, physical = _resolve_workarea(root, prefer_pointer)
    work_width = max(1.0, float(right - left))
    work_height = max(1.0, float(bottom - top))
    if physical:
        logical_width = work_width / auto_window_scale
        logical_height = work_height / auto_window_scale
    else:
        logical_width = work_width
        logical_height = work_height

    desired_user_scale = _compute_user_scale(logical_width, logical_height)
    changed = abs(desired_user_scale - current_user_scale) >= 0.01

    if changed:
        ctk.set_widget_scaling(desired_user_scale)
        ctk.set_window_scaling(desired_user_scale)

    _STATE["user_scale"] = desired_user_scale
    _STATE["workarea"] = (int(left), int(top), int(right), int(bottom))
    _STATE["auto_window_scale"] = auto_window_scale
    _STATE["auto_widget_scale"] = auto_widget_scale
    return changed


def refresh_application_scaling(root) -> bool:
    return configure_application_scaling(root, prefer_pointer=False)


def get_application_workarea(root):
    workarea = _STATE.get("workarea")
    if workarea is not None:
        return workarea
    left, top, right, bottom, _ = _resolve_workarea(root, True)
    return int(left), int(top), int(right), int(bottom)
