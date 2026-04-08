import customtkinter as ctk
from tkinter import Canvas
from PIL import Image, ImageDraw, ImageTk
from view.ui_constants import COLORS, SIDEBAR_WIDTH, BTN_H_ICON
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
        return _mix(fill, "#FFFFFF", 0.2)
    return _mix(fill, "#000000", 0.15)


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
        self._outside_bg = COLORS["light"]["bg"]
        self._pill_bg = COLORS["light"]["left_bar"]
        self._text_color = COLORS["light"]["sidebar_text"]
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
        is_light = (theme_name == "Light")
        theme = COLORS["light" if is_light else "dark"]

        self._outside_bg = theme["bg"]
        self._pill_bg = theme["left_bar"]
        self._text_color = theme["sidebar_text"]

        if _luma(self._pill_bg) < 140:
            self._border_color = _mix(self._pill_bg, "#FFFFFF", 0.18)
        else:
            self._border_color = _mix(self._pill_bg, "#000000", 0.18)

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

        paint_signature = (w, h, self._outside_bg, pill_fill, text_fill, border_fill, self._state, self._text)
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
                font=("Segoe UI", 10, "bold"),
                fill=text_fill
            )
            self._paint_signature = paint_signature
            return

        pill_rgb = _hex_to_rgb(pill_fill)
        border_rgb = _hex_to_rgb(border_fill) if border_fill else None

        img = Image.new("RGBA", (W, H), outside_rgb)
        draw = ImageDraw.Draw(img)

        pad = 2 * scale
        x1, y1 = pad, pad
        x2, y2 = W - pad, H - pad

        usable_w = max(10 * scale, (x2 - x1))
        radius = usable_w // 2
        bw = max(1, int(self._border_w * scale))

        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=radius,
            fill=pill_rgb,
            outline=border_rgb,
            width=bw
        )

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
            font=("Segoe UI", 10, "bold"),
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
            outside_bg: str = COLORS["light"]["bg"],
            fg_color: str = COLORS["light"]["left_bar"],
            hover_color: str = COLORS["sidebar_hover"]["light"],
            border_color: str = None,
            border_width: int = 2,
            command=None
    ):
        super().__init__(parent, width=width, height=height, fg_color="transparent")
        self.pack_propagate(False)

        self._outside_bg = outside_bg
        self._fg_color = fg_color
        self._hover_color = hover_color
        self._border_w = int(border_width)

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

        if self._state == "disabled":
            fill = _mix(fill, self._outside_bg, 0.35)
            border = _mix(border, self._outside_bg, 0.35)

        try:
            appearance_mode = ctk.get_appearance_mode()
        except Exception:
            appearance_mode = "Light"

        paint_signature = (w, h, self._outside_bg, fill, border, self._state, self._hovered, self._border_w, appearance_mode, id(self._image))
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
        fill_rgb = _hex_to_rgb(fill)
        border_rgb = _hex_to_rgb(border) if border else None

        img = Image.new("RGBA", (W, H), outside_rgb)
        draw = ImageDraw.Draw(img)

        pad = 2 * scale
        x1, y1 = pad, pad
        x2, y2 = W - pad, H - pad

        radius = 100
        bw = max(1, int(self._border_w * scale))

        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=radius,
            fill=fill_rgb,
            outline=border_rgb,
            width=bw
        )

        pil_icon = self._pick_icon_pil()
        if pil_icon is not None:
            try:
                icon = pil_icon.convert("RGBA")
                fill_lum = _luma(fill)
                need_light_icon = (fill_lum < 140)

                r, g, b, a = icon.split()

                # Ajustamos color del icono segun el fondo para asegurar contraste
                if need_light_icon:
                    icon = Image.merge("RGBA", (
                        a.point(lambda _: 255),
                        a.point(lambda _: 255),
                        a.point(lambda _: 255),
                        a
                    ))
                else:
                    icon = Image.merge("RGBA", (
                        a.point(lambda _: 30),
                        a.point(lambda _: 30),
                        a.point(lambda _: 30),
                        a
                    ))

                target_px = max(14, int(min(w, h) * 0.55))
                max_side = target_px * scale
                iw, ih = icon.size
                if iw > 0 and ih > 0:
                    ratio = min(max_side / iw, max_side / ih)
                    new_w = max(1, int(iw * ratio))
                    new_h = max(1, int(ih * ratio))
                    resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)
                    icon = icon.resize((new_w, new_h), resample)

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
            outside_bg: str = COLORS["light"]["bg"],
            fg_color: str = COLORS["button"]["blue"]["bg"],
            hover_color: str = COLORS["button"]["blue"]["hover"],
            border_color: str = None,
            border_width: int = 2,
            text_color: str = "#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            command=None
    ):
        super().__init__(parent, width=width, height=height, fg_color="transparent")
        self.pack_propagate(False)

        self._outside_bg = outside_bg
        self._fg_color = fg_color
        self._hover_color = hover_color
        self._border_w = int(border_width)

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

        if self._state == "disabled":
            fill = _mix(fill, self._outside_bg, 0.35)
            border = _mix(border, self._outside_bg, 0.35)
            try:
                text_color = _mix(text_color, self._outside_bg, 0.55)
            except Exception:
                pass

        paint_signature = (w, h, self._outside_bg, fill, border, text_color, self._text, str(self._font), self._state, self._hovered, self._border_w)
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
        fill_rgb = _hex_to_rgb(fill)
        border_rgb = _hex_to_rgb(border) if border else None

        img = Image.new("RGBA", (W, H), outside_rgb)
        draw = ImageDraw.Draw(img)

        pad = 2 * scale
        x1, y1 = pad, pad
        x2, y2 = W - pad, H - pad

        usable_w = max(10 * scale, (x2 - x1))
        usable_h = max(10 * scale, (y2 - y1))
        radius = min(usable_w, usable_h) // 2
        bw = max(1, int(self._border_w * scale))

        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=radius,
            fill=fill_rgb,
            outline=border_rgb,
            width=bw
        )

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
        bg = COLORS["light"]["bg"] if current_theme == "Light" else COLORS["dark"]["bg"]
        super().__init__(parent, fg_color=bg)
        self.pack(expand=True, anchor="center")

        self.icons = icons
        self.buttons: dict[str, PillIconButton] = {}

        self._button_container = ctk.CTkFrame(self, fg_color=bg)
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

        theme_keys = COLORS["light"] if is_light else COLORS["dark"]

        fg_color = theme_keys["left_bar"]
        hover_color = COLORS["sidebar_hover"]["light"] if is_light else COLORS["sidebar_hover"]["dark"]
        outside_bg = theme_keys["bg"]

        return PillIconButton(
            self._button_container,
            image=img,
            width=SIDEBAR_WIDTH,
            height=BTN_H_ICON,
            outside_bg=outside_bg,
            fg_color=fg_color,
            hover_color=hover_color,
            border_width=2
        )

    def apply_theme(self, theme_name: str):
        is_light = theme_name == "Light"
        theme_keys = COLORS["light"] if is_light else COLORS["dark"]

        bg = theme_keys["bg"]
        try:
            self.configure(fg_color=bg)
            self._button_container.configure(fg_color=bg)
        except Exception:
            pass

        fg_color = theme_keys["left_bar"]
        hover_color = COLORS["sidebar_hover"]["light"] if is_light else COLORS["sidebar_hover"]["dark"]
        outside_bg = bg

        for key, btn in self.buttons.items():
            if key == "theme_icon":
                btn.configure(
                    image=self.icons.get("moon") if is_light else self.icons.get("sun"),
                    fg_color=fg_color,
                    hover_color=hover_color,
                    outside_bg=outside_bg
                )
            else:
                btn.configure(fg_color=fg_color, hover_color=hover_color, outside_bg=outside_bg)
