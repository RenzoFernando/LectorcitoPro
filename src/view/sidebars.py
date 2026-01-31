# src/view/sidebars.py
import customtkinter as ctk
from tkinter import Canvas

from PIL import Image, ImageDraw, ImageTk  # <- antialias real

from view.ui_constants import COLORS, SIDEBAR_WIDTH, BTN_H_ICON


# -------------------------
# Helpers de color
# -------------------------
def _hex_to_rgb(h: str):
    h = (h or "").strip().lstrip("#")
    if len(h) != 6:
        return (0, 0, 0)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _luma(h: str) -> float:
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
    """Borde sutil automático: si el fill es oscuro -> borde hacia blanco; si es claro -> hacia negro."""
    if _luma(fill) < 140:
        return _mix(fill, "#FFFFFF", 0.18)
    return _mix(fill, "#000000", 0.18)


# -------------------------
# Left Sidebar (pill suave)
# -------------------------
class LeftSidebar(ctk.CTkFrame):
    def __init__(self, parent, text: str, height: int = 400):
        super().__init__(parent, width=SIDEBAR_WIDTH, height=height, fg_color="transparent")
        self.pack_propagate(False)

        self._text = text
        self._outside_bg = COLORS["light"]["bg"]
        self._pill_bg = COLORS["light"]["left_bar"]
        self._text_color = COLORS["dark"]["text"]

        self._border_w = 2
        self._border_color = None

        self._canvas = Canvas(self, highlightthickness=0, bd=0, relief="flat", bg=self._outside_bg)
        self._canvas.pack(fill="both", expand=True)

        # mantener referencia viva de la imagen
        self._pill_photo = None

        self.pack(expand=True, anchor="center")
        self.bind("<Configure>", self._paint, add="+")

    def set_text(self, text: str):
        self._text = text
        self._paint()

    def apply_theme(self, theme_name: str):
        is_light = (theme_name == "Light")
        theme = COLORS["light" if is_light else "dark"]

        self._outside_bg = theme["bg"]
        self._pill_bg = theme["left_bar"]
        self._text_color = COLORS["dark"]["text"] if is_light else COLORS["light"]["text"]

        # borde sutil automático (más claro si el pill es oscuro, más oscuro si es claro)
        if _luma(self._pill_bg) < 140:
            self._border_color = _mix(self._pill_bg, "#FFFFFF", 0.18)
        else:
            self._border_color = _mix(self._pill_bg, "#000000", 0.18)

        self._canvas.configure(bg=self._outside_bg)
        self._paint()

    def _paint(self, event=None):
        w = max(1, int(self._canvas.winfo_width()))
        h = max(1, int(self._canvas.winfo_height()))
        if w <= 2 or h <= 2:
            return

        self._canvas.delete("all")

        # --- Antialias: dibuja grande y baja ---
        scale = 4  # 3 o 4 es ideal
        W, H = w * scale, h * scale

        outside_rgb = _hex_to_rgb(self._outside_bg)
        pill_rgb = _hex_to_rgb(self._pill_bg)
        border_rgb = _hex_to_rgb(self._border_color) if self._border_color else None

        img = Image.new("RGBA", (W, H), outside_rgb)
        draw = ImageDraw.Draw(img)

        pad = 2 * scale
        x1, y1 = pad, pad
        x2, y2 = W - pad, H - pad

        # Radio perfectamente simétrico: mitad del ancho usable
        usable_w = max(10 * scale, (x2 - x1))
        radius = usable_w // 2

        # ancho de borde escalado (evita bordes “chuecos” al reducir)
        bw = max(1, int(self._border_w * scale))

        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=radius,
            fill=pill_rgb,
            outline=border_rgb,
            width=bw
        )

        # downsample con LANCZOS para suavidad
        img_small = img.resize((w, h), Image.LANCZOS)
        self._pill_photo = ImageTk.PhotoImage(img_small)

        self._canvas.create_image(0, 0, image=self._pill_photo, anchor="nw")

        # Texto centrado (sobre la imagen)
        self._canvas.create_text(
            w / 2, h / 2,
            text=self._text,
            angle=90,
            font=("Segoe UI", 10, "bold"),
            fill=self._text_color
        )


# -------------------------
# Pill Icon Button (píldora suave para íconos)
# -------------------------
class PillIconButton(ctk.CTkFrame):
    """
    Botón tipo “píldora” con bordes realmente suavizados (PIL + downsample),
    pensado para los íconos del sidebar derecho.
    """

    def __init__(
        self,
        parent,
        *,
        image=None,
        width: int = SIDEBAR_WIDTH,
        height: int = BTN_H_ICON,
        outside_bg: str = COLORS["light"]["bg"],
        fg_color: str = COLORS["dark"]["bg"],
        hover_color: str = COLORS["sidebar_hover"]["light"],
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

        self._border_color = _auto_border(self._fg_color)
        self._hover_border_color = _auto_border(self._hover_color)

        # Canvas con el pill (fondo)
        self._canvas = Canvas(self, highlightthickness=0, bd=0, relief="flat", bg=self._outside_bg)
        self._canvas.pack(fill="both", expand=True)

        self._pill_photo = None  # mantener referencia viva
        self._icon_photo = None  # mantener referencia viva del ícono (fallback)
        self._paint_job = None  # debounce para evitar loops

        # Estado, comando e ícono (compat con .configure(...) del controller)
        self._command = command
        self._image = image

        # cursor y bindings (hover/click)
        try:
            self._canvas.configure(cursor="hand2")
        except Exception:
            pass

        # Hover / click events (sin duplicar binds)
        super().bind("<Enter>", self._on_enter, add="+")
        super().bind("<Leave>", self._on_leave, add="+")
        super().bind("<Button-1>", self._on_click, add="+")  # click en el frame (bordes)

        self._canvas.bind("<Enter>", self._on_enter, add="+")
        self._canvas.bind("<Leave>", self._on_leave, add="+")
        self._canvas.bind("<Button-1>", self._on_click, add="+")  # click en el canvas (área principal)

        self.bind("<Configure>", self._on_configure, add="+")
        self._schedule_paint()

    # --- API “tipo CTkButton” ---
    def configure(self, cnf=None, **kwargs):  # compatible con tkinter
        # algunos usos estilo tkinter pasan un dict en `cnf`
        if cnf and isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}

        # colores propios del pill
        if "outside_bg" in kwargs:
            self._outside_bg = kwargs.pop("outside_bg")
            try:
                self._canvas.configure(bg=self._outside_bg)
            except Exception:
                pass

        if "fg_color" in kwargs:
            self._fg_color = kwargs.pop("fg_color")
            self._border_color = _auto_border(self._fg_color)

        if "hover_color" in kwargs:
            self._hover_color = kwargs.pop("hover_color")
            self._hover_border_color = _auto_border(self._hover_color)

        # state / command / image (compat con CTkButton)
        if "state" in kwargs:
            self._state = kwargs.pop("state")

        if "command" in kwargs:
            self._command = kwargs.pop("command")

        if "image" in kwargs:
            self._image = kwargs.pop("image")

        self._schedule_paint()

    config = configure  # alias común en tkinter

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
        # Bind al frame + canvas, para que tooltips funcionen bien.
        # CustomTkinter requiere add="+" (o True) para no pisar callbacks internos.
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

    # --- Hover + click ---
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

        self._click_lock = True
        try:
            self.after(220, lambda: setattr(self, "_click_lock", False))
        except Exception:
            self._click_lock = False

        if callable(self._command):
            self._command()

        return "break"

    def _pick_icon_pil(self):
        """Convierte un CTkImage (o PIL.Image) a PIL.Image correcto para el modo actual."""
        img = self._image
        if img is None:
            return None

        # Si ya es PIL Image
        try:
            if isinstance(img, Image.Image):
                return img
        except Exception:
            pass

        # CTkImage suele exponer _light_image/_dark_image y _size (depende de versión)
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
            # fallback: algunas versiones guardan una sola PIL
            for a in ("_pil_image", "_image", "image"):
                if hasattr(img, a):
                    pil = getattr(img, a)
                    break

        if pil is None:
            return None

        # Ajustar tamaño si CTkImage lo define
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
        self._schedule_paint()

    def _schedule_paint(self):
        # Evita loops / repintados infinitos: solo agenda 1 repintado a la vez
        if self._paint_job is not None:
            return
        try:
            self._paint_job = self.after_idle(self._paint)
        except Exception:
            self._paint_job = None

    def _paint(self, event=None):
        self._paint_job = None
        w = max(1, int(self._canvas.winfo_width()))
        h = max(1, int(self._canvas.winfo_height()))
        if w <= 2 or h <= 2:

            return

        self._canvas.delete("all")

        scale = 4
        W, H = w * scale, h * scale

        fill = self._hover_color if (self._hovered and self._state != "disabled") else self._fg_color
        border = self._hover_border_color if (self._hovered and self._state != "disabled") else self._border_color

        # si está disabled, “apaga” un poco el fill mezclándolo con el fondo
        if self._state == "disabled":
            fill = _mix(fill, self._outside_bg, 0.35)
            border = _mix(border, self._outside_bg, 0.35)

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
        radius = min(usable_w, usable_h) // 2  # “píldora” real
        bw = max(1, int(self._border_w * scale))

        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=radius,
            fill=fill_rgb,
            outline=border_rgb,
            width=bw
        )

        # Ícono centrado
        pil_icon = self._pick_icon_pil()
        if pil_icon is not None:
            try:
                icon = pil_icon.convert("RGBA")

                # tamaño objetivo: ~55% del alto
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
                        # baja un poco la opacidad
                        alpha = icon.split()[-1].point(lambda a: int(a * 0.45))
                        icon.putalpha(alpha)

                    ix = (W - new_w) // 2
                    iy = (H - new_h) // 2
                    img.alpha_composite(icon, (ix, iy))
            except Exception:
                pass

        # downsample con LANCZOS para suavidad
        img_small = img.resize((w, h), Image.LANCZOS)
        self._pill_photo = ImageTk.PhotoImage(img_small)
        self._canvas.create_image(0, 0, image=self._pill_photo, anchor="nw")


        if pil_icon is None and self._image is not None:
            try:
                img_obj = self._image
                tk_icon = None

                if hasattr(img_obj, "create_scaled_photo_image"):
                    try:
                        mode = ctk.get_appearance_mode()
                    except Exception:
                        mode = "Light"
                    try:
                        scaling = ctk.get_widget_scaling()
                    except Exception:
                        scaling = 1
                    try:
                        tk_icon = img_obj.create_scaled_photo_image(scaling, mode)
                    except TypeError:
                        # algunas versiones usan keywords diferentes
                        tk_icon = img_obj.create_scaled_photo_image(widget_scaling=scaling, appearance_mode=mode)

                # Si ya es un PhotoImage (o compatible) úsalo tal cual
                if tk_icon is None:
                    tk_icon = img_obj

                # Dibujar centrado (si Tk acepta la imagen)
                self._icon_photo = tk_icon
                self._canvas.create_image(w // 2, h // 2, image=self._icon_photo)
            except Exception:
                pass

# -------------------------
# Pill Text Button (píldora suave para texto)
# -------------------------
class PillTextButton(ctk.CTkFrame):
    """
    Botón tipo “píldora” con bordes realmente suavizados (PIL + downsample),
    pensado para los 6 botones principales (texto).
    API compatible con CTkButton: configure(text=..., command=..., state=..., fg_color=..., hover_color=..., outside_bg=...)
    """

    def __init__(
        self,
        parent,
        *,
        text: str = "",
        width: int = 300,
        height: int = 32,
        outside_bg: str = COLORS["light"]["bg"],
        fg_color: str = COLORS["button"]["blue"],
        hover_color: str = COLORS["button_hover"]["blue_h"],
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

        self._border_color = _auto_border(self._fg_color)
        self._hover_border_color = _auto_border(self._hover_color)

        self._canvas = Canvas(self, highlightthickness=0, bd=0, relief="flat", bg=self._outside_bg)
        self._canvas.pack(fill="both", expand=True)

        self._pill_photo = None  # mantener referencia viva
        self._paint_job = None   # debounce

        try:
            self._canvas.configure(cursor="hand2")
        except Exception:
            pass

        # (opcional pero recomendado)
        self._click_lock = False

        # Hover / click events (sin duplicar binds)
        super().bind("<Enter>", self._on_enter, add="+")
        super().bind("<Leave>", self._on_leave, add="+")
        super().bind("<Button-1>", self._on_click, add="+")  # click en bordes del frame

        self._canvas.bind("<Enter>", self._on_enter, add="+")
        self._canvas.bind("<Leave>", self._on_leave, add="+")
        self._canvas.bind("<Button-1>", self._on_click, add="+")  # click en el área principal

        self.bind("<Configure>", self._on_configure, add="+")
        self._schedule_paint()

    # --- API “tipo CTkButton” ---
    def configure(self, cnf=None, **kwargs):  # compatible con tkinter
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
            self._border_color = _auto_border(self._fg_color)

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

        self._schedule_paint()

    config = configure  # alias común en tkinter

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

    # --- Hover + click ---
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

        self._click_lock = True
        try:
            self.after(220, lambda: setattr(self, "_click_lock", False))
        except Exception:
            self._click_lock = False

        if callable(self._command):
            self._command()

        return "break"

    def _on_configure(self, event=None):
        self._schedule_paint()

    def _schedule_paint(self):
        if self._paint_job is not None:
            return
        try:
            self._paint_job = self.after_idle(self._paint)
        except Exception:
            self._paint_job = None

    def _paint(self, event=None):
        self._paint_job = None
        w = max(1, int(self._canvas.winfo_width()))
        h = max(1, int(self._canvas.winfo_height()))
        if w <= 2 or h <= 2:
            return

        self._canvas.delete("all")

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
        radius = min(usable_w, usable_h) // 2  # píldora real
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

# -------------------------
# Right Sidebar (píldoras suaves)
# -------------------------
class RightSidebar(ctk.CTkFrame):
    def __init__(self, parent, icons: dict, current_theme: str):
        bg = COLORS["light"]["bg"] if current_theme == "Light" else COLORS["dark"]["bg"]
        super().__init__(parent, fg_color=bg)
        self.pack(expand=True, anchor="center")

        self.icons = icons
        self.buttons: dict[str, PillIconButton] = {}

        self._button_container = ctk.CTkFrame(self, fg_color=bg)
        self._button_container.pack(expand=True, anchor="center")

        keys = ["ver", "nover", "theme_icon", "traducir", "restaurar", "github", "info"]
        for key in keys:
            btn = self._create_button(key, current_theme)
            btn.pack(pady=5)
            self.buttons[key] = btn

    def _create_button(self, key: str, theme_name: str) -> PillIconButton:
        is_light = theme_name == "Light"
        if key == "theme_icon":
            img = self.icons.get("moon") if is_light else self.icons.get("sun")
        else:
            img = self.icons.get(key)

        # - tema claro: botones oscuros
        # - tema oscuro: botones claros
        fg_color = COLORS["dark"]["bg"] if is_light else COLORS["light"]["bg"]
        hover_color = COLORS["sidebar_hover"]["light"] if is_light else COLORS["sidebar_hover"]["dark"]
        outside_bg = COLORS["light"]["bg"] if is_light else COLORS["dark"]["bg"]

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
        bg = COLORS["light"]["bg"] if is_light else COLORS["dark"]["bg"]
        try:
            self.configure(fg_color=bg)
            self._button_container.configure(fg_color=bg)
        except Exception:
            pass


        fg_color = COLORS["dark"]["bg"] if is_light else COLORS["light"]["bg"]
        hover_color = COLORS["sidebar_hover"]["light"] if is_light else COLORS["sidebar_hover"]["dark"]
        outside_bg = COLORS["light"]["bg"] if is_light else COLORS["dark"]["bg"]

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
