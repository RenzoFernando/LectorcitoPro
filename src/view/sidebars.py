import customtkinter as ctk
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageDraw, ImageTk
from view.ui_constants import FONT_FAMILY_PRIMARY, COLORS, get_theme_tokens, get_button_tokens, SIDEBAR_WIDTH, BTN_H_ICON, NEUTRAL_WHITE, NEUTRAL_BLACK, LEFT_SIDEBAR_HEIGHT, SIDEBAR_REPAINT_DELAY_MS, LEFT_SIDEBAR_FONT_SIZE, SIDEBAR_CLICK_LOCK_DELAY_MS, PILL_TEXT_BUTTON_FONT_SIZE, PILL_TEXT_HORIZONTAL_INSET, RIGHT_SIDEBAR_BUTTON_SPACING, RIGHT_SIDEBAR_BUTTON_BORDER_WIDTH
from view.tooltip import CustomTooltip

# =============================================================================
# UTILIDADES DE COLOR
# =============================================================================

def _hex_to_rgb(h: str):
    h = (h or "").strip().lstrip("#")
    if len(h) != 6:
        return (0, 0, 0)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _luma(h: str) -> float:
    # Calculo de brillo perceptual para determinar contraste
    r, g, b = _hex_to_rgb(h)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _mix(a: str, b: str, t: float) -> str:
    ar, ag, ab = _hex_to_rgb(a)
    br, bg, bb = _hex_to_rgb(b)
    r = int(ar + (br - ar) * t)
    g = int(ag + (bg - ag) * t)
    b2 = int(ab + (bb - ab) * t)
    return f"#{r:02X}{g:02X}{b2:02X}"


def _auto_border(fill: str) -> str:
    # Genera un borde automatico basado en la luminosidad del relleno
    if _luma(fill) < 140:
        return _mix(fill, NEUTRAL_WHITE, 0.2)
    return _mix(fill, NEUTRAL_BLACK, 0.15)


def _gradient_color(stops: list[tuple[float, str]], t: float) -> str:
    t = max(0.0, min(1.0, float(t)))
    if not stops:
        return NEUTRAL_BLACK
    if len(stops) == 1:
        return stops[0][1]
    for i in range(len(stops) - 1):
        p1, c1 = stops[i]
        p2, c2 = stops[i + 1]
        if p1 <= t <= p2:
            local = (t - p1) / max(1e-9, (p2 - p1))
            return _mix(c1, c2, local)
    return stops[-1][1]


def _build_stops(start: str | None, end: str | None, mid: str | None = None) -> list[tuple[float, str]] | None:
    if not start or not end:
        return None
    if mid:
        return [(0.0, start), (0.54, mid), (1.0, end)]
    return [(0.0, start), (1.0, end)]


def _mix_stops(stops: list[tuple[float, str]] | None, base_color: str, ratio: float) -> list[tuple[float, str]] | None:
    if not stops:
        return None
    return [(point, _mix(color, base_color, ratio)) for point, color in stops]


def _draw_gradient_capsule(img, x1: int, y1: int, x2: int, y2: int, radius: int, stops: list[tuple[float, str]], border_rgb=None, border_width: int = 1):
    grad_w = max(1, int(x2 - x1))
    grad_h = max(1, int(y2 - y1))
    gradient = Image.new("RGBA", (grad_w, grad_h), (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient)
    for x in range(grad_w):
        color = _gradient_color(stops, x / max(1, grad_w - 1))
        gradient_draw.line((x, 0, x, grad_h), fill=_hex_to_rgb(color))
    mask = Image.new("L", (grad_w, grad_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, grad_w - 1, grad_h - 1), radius=radius, fill=255)
    img.paste(gradient, (x1, y1), mask)
    if border_rgb is not None and border_width > 0:
        ImageDraw.Draw(img).rounded_rectangle((x1, y1, x2, y2), radius=radius, outline=border_rgb, width=border_width)


def _trim_render_cache(cache: dict, limit: int = 12):
    while len(cache) > limit:
        try:
            cache.pop(next(iter(cache)))
        except Exception:
            break


def _build_surface_image(widget, backdrop_provider, width: int, height: int, outside_bg: str, scale: int = 4):
    target_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    signature = None

    if callable(backdrop_provider):
        try:
            patch, signature = backdrop_provider(widget, width, height)
        except Exception:
            patch, signature = None, None
        if isinstance(patch, Image.Image):
            patch = patch.convert("RGBA")
            if patch.size != target_size:
                resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)
                patch = patch.resize(target_size, resample)
            return patch.copy(), signature

    return Image.new("RGBA", target_size, (*_hex_to_rgb(outside_bg), 255)), signature


class BlendedRoundedFrame(tk.Frame):
    def __init__(
            self,
            parent,
            *,
            outside_bg: str = COLORS["light"]["bg_base"],
            fill_color: str = COLORS["light"]["bg_card"],
            border_color: str | None = None,
            border_width: int = 1,
            corner_radius: int = 18,
            content_inset: int | None = None,
            backdrop_provider=None
    ):
        super().__init__(parent, bg=outside_bg, bd=0, highlightthickness=0)

        self._outside_bg = outside_bg
        self._fill_color = fill_color
        self._border_color = border_color
        self._border_w = int(border_width)
        self._corner_radius = int(corner_radius)
        self._content_inset = int(content_inset if content_inset is not None else max(6, self._corner_radius // 2))
        self._backdrop_provider = backdrop_provider

        self._canvas = Canvas(self, width=1, height=1, highlightthickness=0, bd=0, relief="flat", bg=self._outside_bg)
        self._canvas.pack(fill="both", expand=True)

        self.content_frame = tk.Frame(self._canvas, bg=self._fill_color, bd=0, highlightthickness=0)
        self._content_window_id = self._canvas.create_window(0, 0, window=self.content_frame, anchor="nw")

        self._surface_photo = None
        self._paint_job = None
        self._paint_signature = None
        self._last_size = None
        self._render_cache = {}

        self.bind("<Configure>", self._on_configure, add="+")
        self._canvas.bind("<Configure>", self._on_configure, add="+")
        self.content_frame.bind("<Configure>", self._on_content_configure, add="+")
        self._sync_requested_size()
        self._schedule_paint()

    def configure(self, cnf=None, **kwargs):
        if cnf and isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}

        if "outside_bg" in kwargs:
            self._outside_bg = kwargs.pop("outside_bg")
            try:
                super().configure(bg=self._outside_bg)
                self._canvas.configure(bg=self._outside_bg)
            except Exception:
                pass

        if "fill_color" in kwargs:
            self._fill_color = kwargs.pop("fill_color")
            try:
                self.content_frame.configure(bg=self._fill_color)
            except Exception:
                pass

        if "fg_color" in kwargs:
            self._fill_color = kwargs.pop("fg_color")
            try:
                self.content_frame.configure(bg=self._fill_color)
            except Exception:
                pass

        if "border_color" in kwargs:
            self._border_color = kwargs.pop("border_color")

        if "border_width" in kwargs:
            self._border_w = int(kwargs.pop("border_width"))

        if "corner_radius" in kwargs:
            self._corner_radius = int(kwargs.pop("corner_radius"))

        if "content_inset" in kwargs:
            self._content_inset = int(kwargs.pop("content_inset"))

        if "backdrop_provider" in kwargs:
            self._backdrop_provider = kwargs.pop("backdrop_provider")

        self._paint_signature = None
        self._schedule_paint()

        if kwargs:
            super().configure(**kwargs)

    config = configure

    def refresh_backdrop(self):
        self._paint_signature = None
        self._render_cache.clear()
        self._schedule_paint(delay=SIDEBAR_REPAINT_DELAY_MS)

    def _sync_requested_size(self):
        inset = max(0, int(self._content_inset))
        try:
            req_w = max(1, int(self.content_frame.winfo_reqwidth()) + (inset * 2))
        except Exception:
            req_w = max(1, inset * 2)
        try:
            req_h = max(1, int(self.content_frame.winfo_reqheight()) + (inset * 2))
        except Exception:
            req_h = max(1, inset * 2)
        try:
            self._canvas.configure(width=req_w, height=req_h)
        except Exception:
            pass

    def _on_content_configure(self, event=None):
        self._sync_requested_size()
        self._schedule_paint(delay=SIDEBAR_REPAINT_DELAY_MS)

    def _sync_content_window(self, width: int, height: int):
        inset = max(0, int(self._content_inset))
        inner_w = max(1, int(width - (inset * 2)))
        inner_h = max(1, int(height - (inset * 2)))
        try:
            self._canvas.coords(self._content_window_id, inset, inset)
            self._canvas.itemconfigure(self._content_window_id, width=inner_w, height=inner_h)
        except Exception:
            pass

    def _on_configure(self, event=None):
        if event is not None and getattr(event, "widget", None) not in (self, self._canvas):
            return
        try:
            size = (
                max(1, int(getattr(event, "width", self._canvas.winfo_width()))),
                max(1, int(getattr(event, "height", self._canvas.winfo_height())))
            )
        except Exception:
            size = (max(1, int(self._canvas.winfo_width())), max(1, int(self._canvas.winfo_height())))
        self._sync_content_window(*size)
        if size == self._last_size:
            return
        self._last_size = size
        self._schedule_paint(delay=SIDEBAR_REPAINT_DELAY_MS)

    def _schedule_paint(self, delay=0):
        if self._paint_job is not None:
            try:
                self.after_cancel(self._paint_job)
            except Exception:
                pass
            self._paint_job = None
        try:
            self._paint_job = self.after(max(1, int(delay)), self._paint)
        except Exception:
            self._paint_job = None

    def _paint(self, event=None):
        self._paint_job = None
        w = max(1, int(self._canvas.winfo_width()))
        h = max(1, int(self._canvas.winfo_height()))
        if w <= 2 or h <= 2:
            return

        self._last_size = (w, h)
        self._sync_content_window(w, h)

        scale = 4
        W, H = w * scale, h * scale
        img, backdrop_signature = _build_surface_image(self._canvas, self._backdrop_provider, w, h, self._outside_bg, scale)

        paint_signature = (w, h, self._outside_bg, self._fill_color, self._border_color, self._border_w, self._corner_radius, self._content_inset, backdrop_signature)
        if paint_signature == self._paint_signature and self._canvas.find_all():
            return

        cached = self._render_cache.get(paint_signature)
        if cached is not None:
            self._surface_photo = cached
            self._canvas.delete("all")
            self._canvas.create_image(0, 0, image=self._surface_photo, anchor="nw")
            self._content_window_id = self._canvas.create_window(0, 0, window=self.content_frame, anchor="nw")
            self._sync_content_window(w, h)
            self._paint_signature = paint_signature
            return

        border_rgb = _hex_to_rgb(self._border_color) if self._border_color else None
        fill_rgba = (*_hex_to_rgb(self._fill_color), 255)

        pad = max(1, int(scale))
        x1, y1 = pad, pad
        x2, y2 = W - pad - 1, H - pad - 1
        radius = max(1, min((x2 - x1) // 2, (y2 - y1) // 2, int(self._corner_radius * scale)))
        bw = max(1, int(self._border_w * scale))

        ImageDraw.Draw(img).rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill_rgba, outline=border_rgb, width=bw)

        img_small = img.resize((w, h), Image.LANCZOS)
        self._surface_photo = ImageTk.PhotoImage(img_small)
        self._render_cache[paint_signature] = self._surface_photo
        _trim_render_cache(self._render_cache)
        self._canvas.delete("all")
        self._canvas.create_image(0, 0, image=self._surface_photo, anchor="nw")
        self._content_window_id = self._canvas.create_window(0, 0, window=self.content_frame, anchor="nw")
        self._sync_content_window(w, h)
        self._paint_signature = paint_signature


# =============================================================================
# BARRA LATERAL IZQUIERDA (VERTICAL)
# =============================================================================

class LeftSidebar(ctk.CTkFrame):
    def __init__(self, parent, text: str, height: int = 415, backdrop_provider=None):
        super().__init__(parent, width=SIDEBAR_WIDTH, height=height, fg_color="transparent")
        self.pack_propagate(False)

        self._text = text
        light_theme = get_theme_tokens("Light")
        self._outside_bg = light_theme["bg_base"]
        self._pill_bg = light_theme["bg_sidebar"]
        self._pill_bg_end = light_theme["sidebar_pill_end"]
        self._pill_bg_mid = light_theme.get("sidebar_pill_mid", _mix(self._pill_bg, self._pill_bg_end, 0.42))
        self._text_color = light_theme["sidebar_text"]
        self._state = "normal"

        self._border_w = 2
        self._border_color = None
        self._backdrop_provider = backdrop_provider

        self._canvas = Canvas(self, highlightthickness=0, bd=0, relief="flat", bg=self._outside_bg)
        self._canvas.pack(fill="both", expand=True)

        self._pill_photo = None
        self._paint_job = None
        self._last_size = None
        self._paint_signature = None
        self._render_cache = {}
        self.pack(expand=True, anchor="center")
        self.bind("<Configure>", self._on_configure, add="+")
        self._canvas.bind("<Configure>", self._on_configure, add="+")

    def configure(self, cnf=None, **kwargs):
        if cnf:
            kwargs.update(cnf)

        if "backdrop_provider" in kwargs:
            self._backdrop_provider = kwargs.pop("backdrop_provider")
            self._render_cache.clear()

        if "state" in kwargs:
            self._state = kwargs.pop("state")
        self._paint_signature = None
        self._schedule_paint()

        super().configure(**kwargs)

    def set_text(self, text: str):
        self._text = text
        self._paint_signature = None
        self._schedule_paint()

    def refresh_backdrop(self):
        self._paint_signature = None
        self._render_cache.clear()
        self._schedule_paint(delay=SIDEBAR_REPAINT_DELAY_MS)

    def apply_theme(self, theme_name: str):
        theme = get_theme_tokens(theme_name)

        self._outside_bg = theme["bg_base"]
        self._pill_bg = theme["bg_sidebar"]
        self._pill_bg_end = theme["sidebar_pill_end"]
        self._pill_bg_mid = theme.get("sidebar_pill_mid", _mix(self._pill_bg, self._pill_bg_end, 0.42))
        self._text_color = theme["sidebar_text"]

        if _luma(self._pill_bg) < 140:
            self._border_color = _mix(self._pill_bg_end, NEUTRAL_WHITE, 0.18)
        else:
            self._border_color = _mix(self._pill_bg_end, NEUTRAL_BLACK, 0.18)

        self._canvas.configure(bg=self._outside_bg)
        self._paint_signature = None
        self._render_cache.clear()
        self._schedule_paint()

    def _on_configure(self, event=None):
        if event is not None and getattr(event, "widget", None) not in (self, self._canvas):
            return
        try:
            size = (
                max(1, int(getattr(event, "width", self._canvas.winfo_width()))),
                max(1, int(getattr(event, "height", self._canvas.winfo_height())))
            )
        except Exception:
            size = (max(1, int(self._canvas.winfo_width())), max(1, int(self._canvas.winfo_height())))
        if size == self._last_size:
            return
        self._last_size = size
        self._schedule_paint(delay=SIDEBAR_REPAINT_DELAY_MS)

    def _schedule_paint(self, delay=0):
        if self._paint_job is not None:
            try:
                self.after_cancel(self._paint_job)
            except Exception:
                pass
            self._paint_job = None
        try:
            self._paint_job = self.after(max(1, int(delay)), self._paint)
        except Exception:
            self._paint_job = None

    def _paint(self, event=None):
        self._paint_job = None
        w = max(1, int(self._canvas.winfo_width()))
        h = max(1, int(self._canvas.winfo_height()))
        if w <= 2 or h <= 2:
            return

        self._last_size = (w, h)

        scale = 4
        W, H = w * scale, h * scale

        outside_fill = self._outside_bg
        pill_fill = self._pill_bg
        pill_mid_fill = self._pill_bg_mid
        pill_end_fill = self._pill_bg_end
        text_fill = self._text_color
        border_fill = self._border_color

        if self._state == "disabled":
            outside_fill = _mix(self._outside_bg, self._pill_bg, 0.16)
            pill_fill = _mix(pill_fill, outside_fill, 0.35)
            pill_mid_fill = _mix(pill_mid_fill, outside_fill, 0.35)
            pill_end_fill = _mix(pill_end_fill, outside_fill, 0.35)
            text_fill = _mix(text_fill, outside_fill, 0.55)
            if border_fill:
                border_fill = _mix(border_fill, outside_fill, 0.35)

        img, backdrop_signature = _build_surface_image(self._canvas, self._backdrop_provider, w, h, outside_fill, scale)

        paint_signature = (w, h, outside_fill, pill_fill, pill_mid_fill, pill_end_fill, text_fill, border_fill, self._state, self._text, backdrop_signature)
        if paint_signature == self._paint_signature and self._canvas.find_all():
            return

        cached_photo = self._render_cache.get(paint_signature)
        if cached_photo is not None:
            self._pill_photo = cached_photo
            self._canvas.delete("all")
            self._canvas.create_image(0, 0, image=self._pill_photo, anchor="nw")
            self._canvas.create_text(
                w / 2, h / 2,
                text=self._text,
                angle=90,
                font=(FONT_FAMILY_PRIMARY, LEFT_SIDEBAR_FONT_SIZE, "bold"),
                fill=text_fill
            )
            self._paint_signature = paint_signature
            return

        border_rgb = _hex_to_rgb(border_fill) if border_fill else None

        pad = 2 * scale
        x1, y1 = pad, pad
        x2, y2 = W - pad, H - pad

        usable_w = max(10 * scale, (x2 - x1))
        radius = usable_w // 2
        bw = max(1, int(self._border_w * scale))
        stops = _build_stops(pill_fill, pill_end_fill, pill_mid_fill)

        _draw_gradient_capsule(img, x1, y1, x2, y2, radius, stops, border_rgb=border_rgb, border_width=bw)

        img_small = img.resize((w, h), Image.LANCZOS)
        self._pill_photo = ImageTk.PhotoImage(img_small)
        self._render_cache[paint_signature] = self._pill_photo
        _trim_render_cache(self._render_cache)
        self._canvas.delete("all")
        self._canvas.create_image(0, 0, image=self._pill_photo, anchor="nw")

        self._canvas.create_text(
            w / 2, h / 2,
            text=self._text,
            angle=90,
            font=(FONT_FAMILY_PRIMARY, LEFT_SIDEBAR_FONT_SIZE, "bold"),
            fill=text_fill
        )
        self._paint_signature = paint_signature


# =============================================================================
# COMPONENTES DE BOTONES (PILL SHAPE)
# =============================================================================

class PillIconButton(ctk.CTkFrame):
    def __init__(
            self,
            parent,
            *,
            image=None,
            width: int = SIDEBAR_WIDTH,
            height: int = BTN_H_ICON,
            outside_bg: str = COLORS["light"]["bg_base"],
            fg_color: str = COLORS["light"]["sidebar_pill_start"],
            hover_color: str = COLORS["light"]["sidebar_pill_hover_start"],
            border_color: str = None,
            border_width: int = 2,
            gradient_start: str | None = None,
            gradient_mid: str | None = None,
            gradient_end: str | None = None,
            hover_gradient_start: str | None = None,
            hover_gradient_mid: str | None = None,
            hover_gradient_end: str | None = None,
            command=None,
            backdrop_provider=None
    ):
        super().__init__(parent, width=width, height=height, fg_color="transparent")
        self.pack_propagate(False)

        self._outside_bg = outside_bg
        self._fg_color = fg_color
        self._hover_color = hover_color
        self._border_w = int(border_width)
        self._gradient_start = gradient_start
        self._gradient_mid = gradient_mid
        self._gradient_end = gradient_end
        self._hover_gradient_start = hover_gradient_start
        self._hover_gradient_mid = hover_gradient_mid
        self._hover_gradient_end = hover_gradient_end

        self._hovered = False
        self._state = "normal"
        self._backdrop_provider = backdrop_provider
        self._explicit_border = border_color
        self._border_color = border_color if border_color else _auto_border(self._fg_color)
        self._hover_border_color = _auto_border(self._hover_color)

        self._canvas = Canvas(self, highlightthickness=0, bd=0, relief="flat", bg=self._outside_bg)
        self._canvas.pack(fill="both", expand=True)

        self._pill_photo = None
        self._icon_photo = None
        self._paint_job = None
        self._paint_signature = None
        self._last_size = None
        self._render_cache = {}
        self._command = command
        self._image = image

        try:
            self._canvas.configure(cursor="hand2")
        except Exception:
            pass

        super().bind("<Enter>", self._on_enter, add="+")
        super().bind("<Leave>", self._on_leave, add="+")
        super().bind("<Button-1>", self._on_click, add="+")

        self._canvas.bind("<Enter>", self._on_enter, add="+")
        self._canvas.bind("<Leave>", self._on_leave, add="+")
        self._canvas.bind("<Button-1>", self._on_click, add="+")

        self.bind("<Configure>", self._on_configure, add="+")
        self._canvas.bind("<Configure>", self._on_configure, add="+")
        self._schedule_paint()

    def configure(self, cnf=None, **kwargs):
        if cnf and isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}

        if "outside_bg" in kwargs:
            self._outside_bg = kwargs.pop("outside_bg")
            try:
                self._canvas.configure(bg=self._outside_bg)
            except Exception:
                pass

        if "backdrop_provider" in kwargs:
            self._backdrop_provider = kwargs.pop("backdrop_provider")
            self._render_cache.clear()

        if "fg_color" in kwargs:
            self._fg_color = kwargs.pop("fg_color")
            if not self._explicit_border:
                self._border_color = _auto_border(self._fg_color)

        if "border_color" in kwargs:
            self._explicit_border = kwargs.pop("border_color")
            self._border_color = self._explicit_border

        if "hover_color" in kwargs:
            self._hover_color = kwargs.pop("hover_color")
            self._hover_border_color = _auto_border(self._hover_color)

        if "gradient_start" in kwargs:
            self._gradient_start = kwargs.pop("gradient_start")
        if "gradient_mid" in kwargs:
            self._gradient_mid = kwargs.pop("gradient_mid")
        if "gradient_end" in kwargs:
            self._gradient_end = kwargs.pop("gradient_end")
        if "hover_gradient_start" in kwargs:
            self._hover_gradient_start = kwargs.pop("hover_gradient_start")
        if "hover_gradient_mid" in kwargs:
            self._hover_gradient_mid = kwargs.pop("hover_gradient_mid")
        if "hover_gradient_end" in kwargs:
            self._hover_gradient_end = kwargs.pop("hover_gradient_end")

        if "state" in kwargs:
            self._state = kwargs.pop("state")

        if "command" in kwargs:
            self._command = kwargs.pop("command")

        if "image" in kwargs:
            self._image = kwargs.pop("image")

        self._paint_signature = None
        self._schedule_paint()

    config = configure

    def cget(self, key):
        if key in ("outside_bg", "fg_color", "hover_color"):
            return {"outside_bg": self._outside_bg, "fg_color": self._fg_color, "hover_color": self._hover_color}[key]
        if key == "state":
            return self._state
        if key == "command":
            return self._command
        if key == "image":
            return self._image
        return super().cget(key)

    def bind(self, sequence=None, func=None, add=None):
        if add is None:
            add = "+"
        r = super().bind(sequence, func, add)
        try:
            self._canvas.bind(sequence, func, add)
        except Exception:
            pass
        return r

    def invoke(self):
        if self._state == "disabled":
            return None
        if callable(self._command):
            return self._command()
        return None

    def refresh_backdrop(self):
        self._paint_signature = None
        self._render_cache.clear()
        self._schedule_paint(delay=SIDEBAR_REPAINT_DELAY_MS)

    def _on_enter(self, event=None):
        if self._state == "disabled":
            return
        if not self._hovered:
            self._hovered = True
            self._schedule_paint()

    def _on_leave(self, event=None):
        if self._hovered:
            self._hovered = False
            self._schedule_paint()

    def _on_click(self, event=None):
        if self._state == "disabled":
            return "break"
        if getattr(self, "_click_lock", False):
            return "break"
        CustomTooltip.hide_global()
        self._click_lock = True
        try:
            self.after(SIDEBAR_CLICK_LOCK_DELAY_MS, lambda: setattr(self, "_click_lock", False))
        except Exception:
            self._click_lock = False
        if callable(self._command):
            self._command()
        return "break"

    def _pick_icon_pil(self):
        img = self._image
        if img is None:
            return None
        try:
            if isinstance(img, Image.Image):
                return img
        except Exception:
            pass
        try:
            mode = ctk.get_appearance_mode()
        except Exception:
            mode = "Light"

        pil = None
        if mode == "Dark":
            for a in ("_dark_image", "dark_image"):
                if hasattr(img, a):
                    pil = getattr(img, a)
                    break
        if pil is None:
            for a in ("_light_image", "light_image"):
                if hasattr(img, a):
                    pil = getattr(img, a)
                    break
        if pil is None:
            for a in ("_pil_image", "_image", "image"):
                if hasattr(img, a):
                    pil = getattr(img, a)
                    break
        if pil is None:
            return None
        size = None
        for a in ("_size", "size"):
            if hasattr(img, a):
                size = getattr(img, a)
                break
        if isinstance(size, (tuple, list)) and len(size) == 2:
            try:
                target = (int(size[0]), int(size[1]))
                if pil.size != target:
                    resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)
                    pil = pil.resize(target, resample)
            except Exception:
                pass
        return pil

    def _on_configure(self, event=None):
        if event is not None and getattr(event, "widget", None) not in (self, self._canvas):
            return
        try:
            size = (
                max(1, int(getattr(event, "width", self._canvas.winfo_width()))),
                max(1, int(getattr(event, "height", self._canvas.winfo_height())))
            )
        except Exception:
            size = (max(1, int(self._canvas.winfo_width())), max(1, int(self._canvas.winfo_height())))
        if size == self._last_size:
            return
        self._last_size = size
        self._schedule_paint(delay=SIDEBAR_REPAINT_DELAY_MS)

    def _schedule_paint(self, delay=0):
        if self._paint_job is not None:
            try:
                self.after_cancel(self._paint_job)
            except Exception:
                pass
            self._paint_job = None
        try:
            self._paint_job = self.after(max(1, int(delay)), self._paint)
        except Exception:
            self._paint_job = None

    def _paint(self, event=None):
        self._paint_job = None
        w = max(1, int(self._canvas.winfo_width()))
        h = max(1, int(self._canvas.winfo_height()))
        if w <= 2 or h <= 2:
            return

        self._last_size = (w, h)

        scale = 4
        W, H = w * scale, h * scale

        fill = self._hover_color if (self._hovered and self._state != "disabled") else self._fg_color
        border = self._hover_border_color if (self._hovered and self._state != "disabled") else self._border_color
        gradient_stops = _build_stops(self._gradient_start, self._gradient_end, self._gradient_mid)
        hover_gradient_stops = _build_stops(self._hover_gradient_start, self._hover_gradient_end, self._hover_gradient_mid)
        active_stops = hover_gradient_stops if (self._hovered and self._state != "disabled" and hover_gradient_stops) else gradient_stops

        if self._state == "disabled":
            fill = _mix(fill, self._outside_bg, 0.35)
            border = _mix(border, self._outside_bg, 0.35)
            active_stops = _mix_stops(active_stops, self._outside_bg, 0.35)

        img, backdrop_signature = _build_surface_image(self._canvas, self._backdrop_provider, w, h, self._outside_bg, scale)

        paint_signature = (w, h, self._outside_bg, fill, border, tuple(active_stops or []), self._state, self._hovered, self._border_w, bool(self._image), backdrop_signature)
        if paint_signature == self._paint_signature and self._canvas.find_all():
            return

        cached_photo = self._render_cache.get(paint_signature)
        if cached_photo is not None:
            self._pill_photo = cached_photo
            self._canvas.delete("all")
            self._canvas.create_image(0, 0, image=self._pill_photo, anchor="nw")
            self._paint_signature = paint_signature
            return

        border_rgb = _hex_to_rgb(border) if border else None

        pad = 2 * scale
        x1, y1 = pad, pad
        x2, y2 = W - pad, H - pad

        usable_w = max(10 * scale, (x2 - x1))
        usable_h = max(10 * scale, (y2 - y1))
        radius = min(usable_w, usable_h) // 2
        bw = max(1, int(self._border_w * scale))

        if active_stops:
            _draw_gradient_capsule(img, x1, y1, x2, y2, radius, active_stops, border_rgb=border_rgb, border_width=bw)
        else:
            ImageDraw.Draw(img).rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=_hex_to_rgb(fill), outline=border_rgb, width=bw)

        icon = self._pick_icon_pil()
        if icon is not None:
            try:
                icon = icon.convert("RGBA")
                iw, ih = icon.size
                max_w = max(1, int((x2 - x1) * 0.56))
                max_h = max(1, int((y2 - y1) * 0.56))
                ratio = min(max_w / max(1, iw), max_h / max(1, ih))
                if ratio < 1.0 or ratio > 1.02:
                    new_w = max(1, int(iw * ratio))
                    new_h = max(1, int(ih * ratio))
                    resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)
                    icon = icon.resize((new_w, new_h), resample)
                else:
                    new_w, new_h = iw, ih

                if self._state == "disabled":
                    alpha = icon.split()[-1].point(lambda a: int(a * 0.45))
                    icon.putalpha(alpha)

                ix = (W - new_w) // 2
                iy = (H - new_h) // 2
                img.alpha_composite(icon, (ix, iy))
            except Exception:
                pass

        img_small = img.resize((w, h), Image.LANCZOS)
        self._pill_photo = ImageTk.PhotoImage(img_small)
        self._render_cache[paint_signature] = self._pill_photo
        _trim_render_cache(self._render_cache)
        self._canvas.delete("all")
        self._canvas.create_image(0, 0, image=self._pill_photo, anchor="nw")
        self._paint_signature = paint_signature


class PillTextButton(ctk.CTkFrame):
    def __init__(
            self,
            parent,
            *,
            text: str = "",
            width: int = 300,
            height: int = 32,
            outside_bg: str = COLORS["light"]["bg_base"],
            fg_color: str = COLORS["button"]["blue"]["bg"],
            hover_color: str = COLORS["button"]["blue"]["hover"],
            border_color: str = None,
            border_width: int = 2,
            gradient_start: str | None = None,
            gradient_mid: str | None = None,
            gradient_end: str | None = None,
            hover_gradient_start: str | None = None,
            hover_gradient_mid: str | None = None,
            hover_gradient_end: str | None = None,
            text_color: str = COLORS["light"]["text_on_accent"],
            font=(FONT_FAMILY_PRIMARY, PILL_TEXT_BUTTON_FONT_SIZE, "bold"),
            command=None
    ):
        super().__init__(parent, width=width, height=height, fg_color="transparent")
        self.pack_propagate(False)

        self._outside_bg = outside_bg
        self._fg_color = fg_color
        self._hover_color = hover_color
        self._border_w = int(border_width)
        self._gradient_start = gradient_start
        self._gradient_mid = gradient_mid
        self._gradient_end = gradient_end
        self._hover_gradient_start = hover_gradient_start
        self._hover_gradient_mid = hover_gradient_mid
        self._hover_gradient_end = hover_gradient_end

        self._text = text or ""
        self._text_color = text_color
        self._font = font
        self._hovered = False
        self._state = "normal"
        self._command = command

        self._explicit_border = border_color
        self._border_color = border_color if border_color else _auto_border(self._fg_color)
        self._hover_border_color = _auto_border(self._hover_color)

        self._canvas = Canvas(self, highlightthickness=0, bd=0, relief="flat", bg=self._outside_bg)
        self._canvas.pack(fill="both", expand=True)

        self._pill_photo = None
        self._paint_job = None
        self._paint_signature = None
        self._last_size = None
        self._render_cache = {}

        try:
            self._canvas.configure(cursor="hand2")
        except Exception:
            pass

        self._click_lock = False

        super().bind("<Enter>", self._on_enter, add="+")
        super().bind("<Leave>", self._on_leave, add="+")
        super().bind("<Button-1>", self._on_click, add="+")

        self._canvas.bind("<Enter>", self._on_enter, add="+")
        self._canvas.bind("<Leave>", self._on_leave, add="+")
        self._canvas.bind("<Button-1>", self._on_click, add="+")

        self.bind("<Configure>", self._on_configure, add="+")
        self._canvas.bind("<Configure>", self._on_configure, add="+")
        self._schedule_paint()

    def configure(self, cnf=None, **kwargs):
        if cnf and isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}

        if "outside_bg" in kwargs:
            self._outside_bg = kwargs.pop("outside_bg")
            try:
                self._canvas.configure(bg=self._outside_bg)
            except Exception:
                pass

        if "fg_color" in kwargs:
            self._fg_color = kwargs.pop("fg_color")
            if not self._explicit_border:
                self._border_color = _auto_border(self._fg_color)

        if "border_color" in kwargs:
            self._explicit_border = kwargs.pop("border_color")
            self._border_color = self._explicit_border

        if "hover_color" in kwargs:
            self._hover_color = kwargs.pop("hover_color")
            self._hover_border_color = _auto_border(self._hover_color)

        if "gradient_start" in kwargs:
            self._gradient_start = kwargs.pop("gradient_start")
        if "gradient_mid" in kwargs:
            self._gradient_mid = kwargs.pop("gradient_mid")
        if "gradient_end" in kwargs:
            self._gradient_end = kwargs.pop("gradient_end")
        if "hover_gradient_start" in kwargs:
            self._hover_gradient_start = kwargs.pop("hover_gradient_start")
        if "hover_gradient_mid" in kwargs:
            self._hover_gradient_mid = kwargs.pop("hover_gradient_mid")
        if "hover_gradient_end" in kwargs:
            self._hover_gradient_end = kwargs.pop("hover_gradient_end")

        if "border_width" in kwargs:
            self._border_w = int(kwargs.pop("border_width"))

        if "text" in kwargs:
            self._text = str(kwargs.pop("text"))

        if "text_color" in kwargs:
            self._text_color = kwargs.pop("text_color")

        if "font" in kwargs:
            self._font = kwargs.pop("font")

        if "state" in kwargs:
            self._state = kwargs.pop("state")

        if "command" in kwargs:
            self._command = kwargs.pop("command")

        self._paint_signature = None
        self._schedule_paint()

    config = configure

    def cget(self, key):
        if key in ("outside_bg", "fg_color", "hover_color", "text", "text_color", "font", "state", "command"):
            return {
                "outside_bg": self._outside_bg,
                "fg_color": self._fg_color,
                "hover_color": self._hover_color,
                "text": self._text,
                "text_color": self._text_color,
                "font": self._font,
                "state": self._state,
                "command": self._command,
            }[key]
        return super().cget(key)

    def bind(self, sequence=None, func=None, add=None):
        if add is None:
            add = "+"
        r = super().bind(sequence, func, add)
        try:
            self._canvas.bind(sequence, func, add)
        except Exception:
            pass
        return r

    def invoke(self):
        if self._state == "disabled":
            return None
        if callable(self._command):
            return self._command()
        return None

    def _on_enter(self, event=None):
        if self._state == "disabled":
            return
        if not self._hovered:
            self._hovered = True
            self._schedule_paint()

    def _on_leave(self, event=None):
        if self._hovered:
            self._hovered = False
            self._schedule_paint()

    def _on_click(self, event=None):
        if self._state == "disabled":
            return "break"
        if getattr(self, "_click_lock", False):
            return "break"
        CustomTooltip.hide_global()
        self._click_lock = True
        try:
            self.after(SIDEBAR_CLICK_LOCK_DELAY_MS, lambda: setattr(self, "_click_lock", False))
        except Exception:
            self._click_lock = False
        if callable(self._command):
            self._command()
        return "break"

    def _on_configure(self, event=None):
        if event is not None and getattr(event, "widget", None) not in (self, self._canvas):
            return
        try:
            size = (
                max(1, int(getattr(event, "width", self._canvas.winfo_width()))),
                max(1, int(getattr(event, "height", self._canvas.winfo_height())))
            )
        except Exception:
            size = (max(1, int(self._canvas.winfo_width())), max(1, int(self._canvas.winfo_height())))
        if size == self._last_size:
            return
        self._last_size = size
        self._schedule_paint(delay=SIDEBAR_REPAINT_DELAY_MS)

    def _schedule_paint(self, delay=0):
        if self._paint_job is not None:
            try:
                self.after_cancel(self._paint_job)
            except Exception:
                pass
            self._paint_job = None
        try:
            self._paint_job = self.after(max(1, int(delay)), self._paint)
        except Exception:
            self._paint_job = None

    def _paint(self, event=None):
        self._paint_job = None
        w = max(1, int(self._canvas.winfo_width()))
        h = max(1, int(self._canvas.winfo_height()))
        if w <= 2 or h <= 2:
            return

        self._last_size = (w, h)

        scale = 4
        W, H = w * scale, h * scale

        fill = self._hover_color if (self._hovered and self._state != "disabled") else self._fg_color
        border = self._hover_border_color if (self._hovered and self._state != "disabled") else self._border_color
        text_color = self._text_color
        gradient_stops = _build_stops(self._gradient_start, self._gradient_end, self._gradient_mid)
        hover_gradient_stops = _build_stops(self._hover_gradient_start, self._hover_gradient_end, self._hover_gradient_mid)
        active_stops = hover_gradient_stops if (self._hovered and self._state != "disabled" and hover_gradient_stops) else gradient_stops

        if self._state == "disabled":
            fill = _mix(fill, self._outside_bg, 0.35)
            border = _mix(border, self._outside_bg, 0.35)
            try:
                text_color = _mix(text_color, self._outside_bg, 0.55)
            except Exception:
                pass
            active_stops = _mix_stops(active_stops, self._outside_bg, 0.35)

        paint_signature = (w, h, self._outside_bg, fill, border, text_color, self._text, str(self._font), self._state, self._hovered, self._border_w, tuple(active_stops or []))
        if paint_signature == self._paint_signature and self._canvas.find_all():
            return

        cached_photo = self._render_cache.get(paint_signature)
        if cached_photo is not None:
            self._pill_photo = cached_photo
            self._canvas.delete("all")
            self._canvas.create_image(0, 0, image=self._pill_photo, anchor="nw")
            wrap_w = max(10, w - PILL_TEXT_HORIZONTAL_INSET)
            self._canvas.create_text(
                w / 2, h / 2,
                text=self._text,
                font=self._font,
                fill=text_color,
                width=wrap_w,
                justify="center"
            )
            self._paint_signature = paint_signature
            return

        outside_rgb = _hex_to_rgb(self._outside_bg)
        border_rgb = _hex_to_rgb(border) if border else None

        img = Image.new("RGBA", (W, H), outside_rgb)

        pad = 2 * scale
        x1, y1 = pad, pad
        x2, y2 = W - pad, H - pad

        usable_w = max(10 * scale, (x2 - x1))
        usable_h = max(10 * scale, (y2 - y1))
        radius = min(usable_w, usable_h) // 2
        bw = max(1, int(self._border_w * scale))

        if active_stops:
            _draw_gradient_capsule(img, x1, y1, x2, y2, radius, active_stops, border_rgb=border_rgb, border_width=bw)
        else:
            ImageDraw.Draw(img).rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=_hex_to_rgb(fill), outline=border_rgb, width=bw)

        img_small = img.resize((w, h), Image.LANCZOS)
        self._pill_photo = ImageTk.PhotoImage(img_small)
        self._render_cache[paint_signature] = self._pill_photo
        _trim_render_cache(self._render_cache)
        self._canvas.delete("all")
        self._canvas.create_image(0, 0, image=self._pill_photo, anchor="nw")

        wrap_w = max(10, w - PILL_TEXT_HORIZONTAL_INSET)
        self._canvas.create_text(
            w / 2, h / 2,
            text=self._text,
            font=self._font,
            fill=text_color,
            width=wrap_w,
            justify="center"
        )
        self._paint_signature = paint_signature


# =============================================================================
# BARRA LATERAL DERECHA (ICONOS)
# =============================================================================

class RightSidebar(tk.Frame):
    def __init__(self, parent, icons: dict, current_theme: str, backdrop_provider=None):
        bg = get_theme_tokens(current_theme)["bg_base"]
        super().__init__(parent, bg=bg, bd=0, highlightthickness=0)
        self.pack(expand=True, anchor="center")

        self.icons = icons
        self.buttons: dict[str, PillIconButton] = {}
        self._backdrop_provider = backdrop_provider

        self._button_container = tk.Frame(self, bg=bg, bd=0, highlightthickness=0)
        self._button_container.pack(expand=True, anchor="center")

        keys = ["ver", "nover", "etiqueta", "theme_icon", "traducir", "restaurar", "perfil", "github", "info",
                "ajustes"]

        for key in keys:
            btn = self._create_button(key, current_theme)
            btn.pack(pady=RIGHT_SIDEBAR_BUTTON_SPACING)
            self.buttons[key] = btn

    def _create_button(self, key: str, theme_name: str) -> PillIconButton:
        is_light = theme_name == "Light"
        if key == "theme_icon":
            img = self.icons.get("moon") if is_light else self.icons.get("sun")
        else:
            img = self.icons.get(key)

        theme_keys = get_theme_tokens(theme_name)
        outside_bg = theme_keys["bg_base"]

        return PillIconButton(
            self._button_container,
            image=img,
            width=SIDEBAR_WIDTH,
            height=BTN_H_ICON,
            outside_bg=outside_bg,
            fg_color=theme_keys["bg_sidebar"],
            hover_color=theme_keys["sidebar_pill_hover_start"],
            gradient_start=theme_keys["bg_sidebar"],
            gradient_mid=theme_keys.get("sidebar_pill_mid", _mix(theme_keys["bg_sidebar"], theme_keys["sidebar_pill_end"], 0.42)),
            gradient_end=theme_keys["sidebar_pill_end"],
            hover_gradient_start=theme_keys["sidebar_pill_hover_start"],
            hover_gradient_mid=theme_keys.get("sidebar_pill_hover_mid", _mix(theme_keys["sidebar_pill_hover_start"], theme_keys["sidebar_pill_hover_end"], 0.48)),
            hover_gradient_end=theme_keys["sidebar_pill_hover_end"],
            border_color=theme_keys["border_strong"],
            border_width=RIGHT_SIDEBAR_BUTTON_BORDER_WIDTH,
            backdrop_provider=self._backdrop_provider
        )

    def refresh_backdrop(self):
        for btn in self.buttons.values():
            try:
                btn.refresh_backdrop()
            except Exception:
                pass

    def apply_theme(self, theme_name: str):
        is_light = theme_name == "Light"
        theme_keys = get_theme_tokens(theme_name)

        bg = theme_keys["bg_base"]
        try:
            self.configure(bg=bg)
            self._button_container.configure(bg=bg)
        except Exception:
            pass

        for key, btn in self.buttons.items():
            kwargs = {
                "fg_color": theme_keys["bg_sidebar"],
                "hover_color": theme_keys["sidebar_pill_hover_start"],
                "outside_bg": bg,
                "gradient_start": theme_keys["bg_sidebar"],
                "gradient_mid": theme_keys.get("sidebar_pill_mid", _mix(theme_keys["bg_sidebar"], theme_keys["sidebar_pill_end"], 0.42)),
                "gradient_end": theme_keys["sidebar_pill_end"],
                "hover_gradient_start": theme_keys["sidebar_pill_hover_start"],
                "hover_gradient_mid": theme_keys.get("sidebar_pill_hover_mid", _mix(theme_keys["sidebar_pill_hover_start"], theme_keys["sidebar_pill_hover_end"], 0.48)),
                "hover_gradient_end": theme_keys["sidebar_pill_hover_end"],
                "border_color": theme_keys["border_strong"],
                "border_width": 1,
            }
            if key == "theme_icon":
                kwargs["image"] = self.icons.get("moon") if is_light else self.icons.get("sun")
            btn.configure(**kwargs)