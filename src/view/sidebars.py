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
        self.bind("<Configure>", self._paint)

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
# Right Sidebar (igual)
# -------------------------
class RightSidebar(ctk.CTkFrame):
    def __init__(self, parent, icons: dict, current_theme: str):
        super().__init__(parent, fg_color="transparent")
        self.pack(expand=True, anchor="center")

        self.icons = icons
        self.buttons: dict[str, ctk.CTkButton] = {}

        self._button_container = ctk.CTkFrame(self, fg_color="transparent")
        self._button_container.pack(expand=True, anchor="center")

        keys = ["ver", "nover", "theme_icon", "traducir", "restaurar", "github", "info"]
        for key in keys:
            btn = self._create_button(key, current_theme)
            btn.pack(pady=5)
            self.buttons[key] = btn

    def _create_button(self, key: str, theme_name: str) -> ctk.CTkButton:
        is_light = theme_name == "Light"
        if key == "theme_icon":
            img = self.icons.get("moon") if is_light else self.icons.get("sun")
        else:
            img = self.icons.get(key)

        fg_color = COLORS["dark"]["bg"] if is_light else COLORS["light"]["bg"]
        hover_color = COLORS["sidebar_hover"]["light"] if is_light else COLORS["sidebar_hover"]["dark"]

        return ctk.CTkButton(
            self._button_container,
            image=img,
            text="",
            width=SIDEBAR_WIDTH,
            height=BTN_H_ICON,
            corner_radius=8,
            fg_color=fg_color,
            hover_color=hover_color
        )

    def apply_theme(self, theme_name: str):
        is_light = theme_name == "Light"
        fg_color = COLORS["dark"]["bg"] if is_light else COLORS["light"]["bg"]
        hover_color = COLORS["sidebar_hover"]["light"] if is_light else COLORS["sidebar_hover"]["dark"]

        for key, btn in self.buttons.items():
            if key == "theme_icon":
                btn.configure(
                    image=self.icons.get("moon") if is_light else self.icons.get("sun"),
                    fg_color=fg_color,
                    hover_color=hover_color
                )
            else:
                btn.configure(fg_color=fg_color, hover_color=hover_color)
