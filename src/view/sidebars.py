import customtkinter as ctk
from tkinter import Canvas
from PIL import Image, ImageDraw, ImageTk
from view.ui_constants import FONT_FAMILY_PRIMARY, COLORS, get_theme_tokens, get_button_tokens, SIDEBAR_WIDTH, BTN_H_ICON, NEUTRAL_WHITE, NEUTRAL_BLACK
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


# =============================================================================
# BARRA LATERAL IZQUIERDA (VERTICAL)
# =============================================================================

class LeftSidebar(ctk.CTkFrame):
    def __init__(self, parent, text: str, height: int = 415):
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

        if "state" in kwargs:
            self._state = kwargs.pop("state")
        self._paint_signature = None
        self._schedule_paint()

        super().configure(**kwargs)

    def set_text(self, text: str):
        self._text = text
        self._paint_signature = None
        self._schedule_paint()

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
        self._schedule_paint(delay=16)

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

        outside_rgb = _hex_to_rgb(self._outside_bg)

        pill_fill = self._pill_bg
        text_fill = self._text_color
        border_fill = self._border_color

        if self._state == "disabled":
            pill_fill = _mix(pill_fill, self._outside_bg, 0.35)
            text_fill = _mix(text_fill, self._outside_bg, 0.55)
            if border_fill:
                border_fill = _mix(border_fill, self._outside_bg, 0.35)

        paint_signature = (w, h, self._outside_bg, pill_fill, self._pill_bg_mid, self._pill_bg_end, text_fill, border_fill, self._state, self._text)
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
                font=(FONT_FAMILY_PRIMARY, 10, "bold"),
                fill=text_fill
            )
            self._paint_signature = paint_signature
            return

        border_rgb = _hex_to_rgb(border_fill) if border_fill else None

        img = Image.new("RGBA", (W, H), outside_rgb)

        pad = 2 * scale
        x1, y1 = pad, pad
        x2, y2 = W - pad, H - pad

        usable_w = max(10 * scale, (x2 - x1))
        radius = usable_w // 2
        bw = max(1, int(self._border_w * scale))
        stops = _build_stops(pill_fill, self._pill_bg_end, self._pill_bg_mid)

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
            font=(FONT_FAMILY_PRIMARY, 10, "bold"),
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

        self._hovered = False
        self._state = "normal"
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
            self.after(220, lambda: setattr(self, "_click_lock", False))
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
        self._schedule_paint(delay=16)

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

        paint_signature = (w, h, self._outside_bg, fill, border, tuple(active_stops or []), self._state, self._hovered, self._border_w, bool(self._image))
        if paint_signature == self._paint_signature and self._canvas.find_all():
            return

        cached_photo = self._render_cache.get(paint_signature)
        if cached_photo is not None:
            self._pill_photo = cached_photo
            self._canvas.delete("all")
            self._canvas.create_image(0, 0, image=self._pill_photo, anchor="nw")
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
            font=(FONT_FAMILY_PRIMARY, 11, "bold"),
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
            self.after(220, lambda: setattr(self, "_click_lock", False))
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
        self._schedule_paint(delay=16)

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
            wrap_w = max(10, w - 16)
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

        wrap_w = max(10, w - 16)
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

class RightSidebar(ctk.CTkFrame):
    def __init__(self, parent, icons: dict, current_theme: str):
        bg = get_theme_tokens(current_theme)["bg_base"]
        super().__init__(parent, fg_color="transparent")
        self.pack(expand=True, anchor="center")

        self.icons = icons
        self.buttons: dict[str, PillIconButton] = {}

        self._button_container = ctk.CTkFrame(self, fg_color="transparent")
        self._button_container.pack(expand=True, anchor="center")

        keys = ["ver", "nover", "etiqueta", "theme_icon", "traducir", "restaurar", "perfil", "github", "info",
                "ajustes"]

        for key in keys:
            btn = self._create_button(key, current_theme)
            btn.pack(pady=1)
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
            border_width=1
        )

    def apply_theme(self, theme_name: str):
        is_light = theme_name == "Light"
        theme_keys = get_theme_tokens(theme_name)

        bg = theme_keys["bg_base"]
        try:
            self.configure(fg_color="transparent")
            self._button_container.configure(fg_color="transparent")
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