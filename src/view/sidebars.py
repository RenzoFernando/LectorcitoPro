from __future__ import annotations

import customtkinter as ctk

from view.ui_assets import load_chevron_icon
from view.ui_constants import (
    BTN_H_ICON,
    COLORS,
    FONT_FAMILY_PRIMARY,
    PILL_TEXT_BUTTON_FONT_SIZE,
    RIGHT_SIDEBAR_BUTTON_SPACING,
    SIDEBAR_WIDTH,
    get_theme_tokens,
)

# =============================================================================
# COMPONENTES COMPARTIDOS DE NAVEGACION Y ACCIONES
# =============================================================================


class BlendedRoundedFrame(ctk.CTkFrame):
    """Card redondeada nativa, sin renderizado por Canvas ni degradados."""

    def __init__(
        self,
        parent,
        *,
        outside_bg: str = COLORS["light"]["bg_base"],
        fill_color: str = COLORS["light"]["bg_card"],
        border_color: str | None = None,
        border_width: int = 1,
        corner_radius: int = 12,
        content_inset: int | None = None,
    ):
        self._content_inset = int(content_inset if content_inset is not None else 10)
        super().__init__(
            parent,
            fg_color=fill_color,
            bg_color=outside_bg,
            border_color=border_color or fill_color,
            border_width=max(0, int(border_width)),
            corner_radius=max(0, int(corner_radius)),
        )

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent", bg_color="transparent")
        self.content_frame.pack(
            fill="both",
            expand=True,
            padx=self._content_inset,
            pady=self._content_inset,
        )

    def configure(self, cnf=None, **kwargs):
        if cnf and isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}

        outside_bg = kwargs.pop("outside_bg", None)
        fill_color = kwargs.pop("fill_color", None)
        content_inset = kwargs.pop("content_inset", None)
        if outside_bg is not None:
            kwargs["bg_color"] = outside_bg
        if fill_color is not None:
            kwargs["fg_color"] = fill_color
        if content_inset is not None:
            self._content_inset = max(0, int(content_inset))
            try:
                self.content_frame.pack_configure(
                    padx=self._content_inset,
                    pady=self._content_inset,
                )
            except Exception:
                pass

        return super().configure(**kwargs)

    config = configure


class PillIconButton(ctk.CTkButton):
    """Boton compacto para la barra superior usando el renderizado nativo de CTk."""

    def __init__(
        self,
        parent,
        *,
        image=None,
        width: int = SIDEBAR_WIDTH,
        height: int = BTN_H_ICON,
        outside_bg: str = COLORS["light"]["bg_base"],
        fg_color: str = "transparent",
        hover_color: str = COLORS["light"]["sidebar_hover"],
        border_color: str | None = None,
        border_width: int = 0,
        command=None,
        **legacy_kwargs,
    ):
        # CTkButton permite transparencia en el fondo, pero no en border_color.
        # El color es irrelevante con border_width=0, por lo que usamos uno valido.
        safe_border_color = border_color
        if safe_border_color in (None, "transparent"):
            safe_border_color = hover_color

        # La barra superior no usa contorno de hover. El estado interactivo se
        # comunica solo mediante el color de fondo, igual que el resto de botones.
        legacy_kwargs.pop("hover_border_color", None)

        super().__init__(
            parent,
            text="",
            image=image,
            width=width,
            height=height,
            corner_radius=6,
            fg_color=fg_color,
            hover_color=hover_color,
            bg_color="transparent",
            border_color=safe_border_color,
            border_width=max(0, int(border_width)),
            border_spacing=0,
            anchor="center",
            command=command,
        )
        try:
            self.configure(cursor="hand2")
        except Exception:
            pass

    def configure(self, cnf=None, **kwargs):
        if cnf and isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}
        kwargs.pop("outside_bg", None)
        kwargs.pop("hover_border_color", None)
        if kwargs.get("border_color") == "transparent":
            kwargs.pop("border_color")
        kwargs["bg_color"] = "transparent"
        return super().configure(**kwargs)

    config = configure


class PillTextButton(ctk.CTkFrame):
    """Accion de texto con slot de icono estable y chevron centrado."""

    def __init__(
        self,
        parent,
        *,
        text: str = "",
        image=None,
        width: int = 380,
        height: int = 42,
        outside_bg: str = COLORS["light"]["bg_base"],
        fg_color: str = COLORS["light"]["bg_panel"],
        hover_color: str = COLORS["light"]["surface_alt"],
        border_color: str | None = None,
        border_width: int = 1,
        text_color: str = COLORS["light"]["text_primary"],
        font=None,
        corner_radius: int = 10,
        command=None,
        icon_placeholder: bool = False,
        icon_color: str | None = None,
        chevron: bool = False,
        chevron_color: str | None = None,
        content_pad: int = 14,
        text_anchor: str = "w",
        **legacy_kwargs,
    ):
        self._pill_ready = False
        self._text = text
        self._command = command
        self._state = "normal"
        self._hovered = False
        self._applied_bg_color = None
        self._applied_cursor = None
        self._normal_color = fg_color
        self._hover_color = hover_color
        self._text_color = text_color
        self._icon_color = icon_color or text_color
        self._chevron_color = chevron_color or text_color
        self._font = font or (FONT_FAMILY_PRIMARY, PILL_TEXT_BUTTON_FONT_SIZE, "bold")
        self._image = image
        self._icon_placeholder = bool(icon_placeholder)
        self._show_chevron = bool(chevron)

        super().__init__(
            parent,
            width=width,
            height=height,
            fg_color=fg_color,
            bg_color=outside_bg,
            border_color=border_color or fg_color,
            border_width=max(0, int(border_width)),
            corner_radius=max(0, int(corner_radius)),
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._icon_host = ctk.CTkFrame(
            self,
            width=20,
            height=20,
            fg_color="transparent",
            bg_color="transparent",
        )
        self._icon_host.grid(row=0, column=0, padx=(content_pad, 10), sticky="w")
        self._icon_host.grid_propagate(False)

        self._icon_label = ctk.CTkLabel(
            self._icon_host,
            text="",
            width=20,
            height=20,
            image=image,
            fg_color="transparent",
            bg_color="transparent",
        )

        self._placeholder = ctk.CTkFrame(
            self._icon_host,
            width=18,
            height=18,
            fg_color="transparent",
            bg_color="transparent",
            border_width=1,
            border_color=self._icon_color,
            corner_radius=0,
        )
        self._placeholder.pack_propagate(False)

        self._text_label = ctk.CTkLabel(
            self,
            text=text,
            font=self._font,
            text_color=self._text_color,
            fg_color="transparent",
            bg_color="transparent",
            anchor=text_anchor,
        )
        self._text_label.grid(row=0, column=1, sticky="ew")

        self._chevron_host = ctk.CTkFrame(
            self,
            width=20,
            height=20,
            fg_color=fg_color,
            bg_color=fg_color,
        )
        self._chevron_host.grid(row=0, column=2, padx=(8, content_pad))
        self._chevron_host.grid_propagate(False)
        self._chevron_host.grid_rowconfigure(0, weight=1)
        self._chevron_host.grid_columnconfigure(0, weight=1)

        self._chevron_image = None
        self._chevron_label = ctk.CTkLabel(
            self._chevron_host,
            text="",
            width=14,
            height=14,
            font=(FONT_FAMILY_PRIMARY, 18, "normal"),
            text_color=self._chevron_color,
            fg_color=fg_color,
            bg_color=fg_color,
            anchor="center",
            justify="center",
        )
        # Grid centra el glyph dentro de todo el slot y evita offsets dependientes
        # del redondeo de place()/DPI.
        self._chevron_label.grid(row=0, column=0)

        self._pill_ready = True
        self._sync_icon()
        self._sync_chevron()
        self._bind_interaction_tree()
        self._apply_visual_state()

    def _interactive_widgets(self):
        return (
            self,
            self._icon_host,
            self._icon_label,
            self._placeholder,
            self._text_label,
            self._chevron_host,
            self._chevron_label,
        )

    def _bind_interaction_tree(self):
        for widget in self._interactive_widgets():
            try:
                if widget is self:
                    ctk.CTkFrame.bind(self, "<Enter>", self._on_enter, add="+")
                    ctk.CTkFrame.bind(self, "<Leave>", self._on_leave, add="+")
                    ctk.CTkFrame.bind(self, "<Button-1>", self._on_click, add="+")
                    ctk.CTkFrame.configure(self, cursor="hand2")
                else:
                    widget.bind("<Enter>", self._on_enter, add="+")
                    widget.bind("<Leave>", self._on_leave, add="+")
                    widget.bind("<Button-1>", self._on_click, add="+")
                    widget.configure(cursor="hand2")
            except Exception:
                pass
        self._applied_cursor = "hand2"

    def _pointer_inside(self) -> bool:
        try:
            x, y = self.winfo_pointerxy()
            left = self.winfo_rootx()
            top = self.winfo_rooty()
            return left <= x < left + self.winfo_width() and top <= y < top + self.winfo_height()
        except Exception:
            return False

    def _on_enter(self, event=None):
        if self._state == "disabled":
            return
        self._hovered = True
        self._apply_visual_state()

    def _on_leave(self, event=None):
        if self._pointer_inside():
            return
        self._hovered = False
        self._apply_visual_state()

    def _on_click(self, event=None):
        if self._state == "disabled":
            return
        self.invoke()

    def _sync_icon(self):
        try:
            self._icon_label.pack_forget()
            self._placeholder.pack_forget()
        except Exception:
            pass

        if self._image is not None:
            self._icon_label.configure(image=self._image)
            self._icon_label.pack(fill="both", expand=True)
        elif self._icon_placeholder:
            self._placeholder.configure(border_color=self._icon_color)
            self._placeholder.pack(expand=True)

    def _sync_chevron(self):
        if not self._show_chevron:
            self._chevron_image = None
            self._chevron_label.configure(image=None, text="")
            return

        self._chevron_image = load_chevron_icon(
            (14, 14),
            light_color=self._chevron_color,
            dark_color=self._chevron_color,
        )
        if self._chevron_image is None:
            self._chevron_label.configure(image=None, text="")
            return
        self._chevron_label.configure(image=self._chevron_image, text="")

    def _apply_icon_surface(self, color):
        # Los hijos transparentes de CTk pueden heredar el fondo exterior del
        # contenedor. Igualamos su superficie al boton para evitar cuadrados
        # visibles detras de SVG con transparencia.
        for widget in (self._icon_host, self._icon_label, self._placeholder):
            try:
                widget.configure(fg_color=color, bg_color=color)
            except Exception:
                pass

    def _apply_chevron_surface(self, color):
        # El chevron no ocupa toda la altura: asi no tapa el borde redondeado
        # del boton y mantiene visible el stroke en el extremo derecho.
        for widget in (self._chevron_host, self._chevron_label):
            try:
                widget.configure(fg_color=color, bg_color=color)
            except Exception:
                pass

    def _apply_visual_state(self):
        disabled = self._state == "disabled"
        base = self._normal_color if disabled or not self._hovered else self._hover_color

        if base != self._applied_bg_color:
            ctk.CTkFrame.configure(self, fg_color=base)
            self._apply_icon_surface(base)
            self._apply_chevron_surface(base)
            self._applied_bg_color = base

        cursor = "arrow" if disabled else "hand2"
        if cursor != self._applied_cursor:
            try:
                ctk.CTkFrame.configure(self, cursor=cursor)
            except Exception:
                pass
            for widget in self._interactive_widgets()[1:]:
                try:
                    widget.configure(cursor=cursor)
                except Exception:
                    pass
            self._applied_cursor = cursor

    def configure(self, cnf=None, **kwargs):
        if cnf and isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}

        # CTkFrame puede invocar configure() durante su propio __init__.
        if not getattr(self, "_pill_ready", False):
            return ctk.CTkFrame.configure(self, **kwargs)

        visual_state_dirty = False
        frame_kwargs = {}

        if "text" in kwargs:
            self._text = kwargs.pop("text")
            self._text_label.configure(text=self._text)
        if "image" in kwargs:
            self._image = kwargs.pop("image")
            self._sync_icon()
        if "command" in kwargs:
            self._command = kwargs.pop("command")
        if "state" in kwargs:
            new_state = kwargs.pop("state")
            if new_state != self._state:
                self._state = new_state
                visual_state_dirty = True
        if "font" in kwargs:
            new_font = kwargs.pop("font")
            if new_font != self._font:
                self._font = new_font
                self._text_label.configure(font=self._font)
        if "text_color" in kwargs:
            new_color = kwargs.pop("text_color")
            if new_color != self._text_color:
                self._text_color = new_color
                self._text_label.configure(text_color=self._text_color)
        if "icon_color" in kwargs:
            new_color = kwargs.pop("icon_color")
            if new_color != self._icon_color:
                self._icon_color = new_color
                self._placeholder.configure(border_color=self._icon_color)
        if "chevron_color" in kwargs:
            new_color = kwargs.pop("chevron_color")
            if new_color != self._chevron_color:
                self._chevron_color = new_color
                self._sync_chevron()
        if "fg_color" in kwargs:
            new_color = kwargs.pop("fg_color")
            if new_color != self._normal_color:
                self._normal_color = new_color
                visual_state_dirty = True
        if "hover_color" in kwargs:
            new_color = kwargs.pop("hover_color")
            if new_color != self._hover_color:
                self._hover_color = new_color
                visual_state_dirty = True
        if "outside_bg" in kwargs:
            frame_kwargs["bg_color"] = kwargs.pop("outside_bg")
        if "icon_placeholder" in kwargs:
            new_placeholder = bool(kwargs.pop("icon_placeholder"))
            if new_placeholder != self._icon_placeholder:
                self._icon_placeholder = new_placeholder
                self._sync_icon()
        if "chevron" in kwargs:
            new_chevron = bool(kwargs.pop("chevron"))
            if new_chevron != self._show_chevron:
                self._show_chevron = new_chevron
                self._sync_chevron()
        kwargs.pop("content_pad", None)
        kwargs.pop("text_anchor", None)

        frame_kwargs.update(kwargs)
        result = None
        if frame_kwargs:
            result = ctk.CTkFrame.configure(self, **frame_kwargs)

        if visual_state_dirty:
            self._apply_visual_state()
        return result

    config = configure

    def cget(self, key):
        custom = {
            "state": self._state,
            "text": self._text,
            "image": self._image,
            "command": self._command,
            "fg_color": self._normal_color,
            "hover_color": self._hover_color,
            "text_color": self._text_color,
        }
        if key in custom:
            return custom[key]
        return super().cget(key)

    def bind(self, sequence=None, func=None, add=None):
        result = super().bind(sequence, func, add)
        if not getattr(self, "_pill_ready", False):
            return result

        for widget in self._interactive_widgets()[1:]:
            try:
                widget.bind(sequence, func, add)
            except Exception:
                pass
        return result

    def invoke(self):
        if self._state != "disabled" and callable(self._command):
            return self._command()
        return None


class RightSidebar(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        icons: dict,
        current_theme: str,
        *,
        orientation: str = "vertical",
        auto_pack: bool = True,
    ):
        self._orientation = "horizontal" if orientation == "horizontal" else "vertical"
        self.icons = icons
        self.buttons: dict[str, PillIconButton] = {}

        super().__init__(parent, fg_color="transparent", bg_color="transparent")
        if auto_pack:
            self.pack(expand=True, anchor="center")

        keys = [
            "ver",
            "nover",
            "etiqueta",
            "theme_icon",
            "traducir",
            "restaurar",
            "perfil",
            "github",
            "info",
            "ajustes",
        ]

        for index, key in enumerate(keys):
            button = self._create_button(key, current_theme)
            if self._orientation == "horizontal":
                self.grid_columnconfigure(index, minsize=SIDEBAR_WIDTH)
                button.grid(
                    row=0,
                    column=index,
                    padx=RIGHT_SIDEBAR_BUTTON_SPACING,
                )
            else:
                button.pack(pady=RIGHT_SIDEBAR_BUTTON_SPACING)
            self.buttons[key] = button

    def _create_button(self, key: str, theme_name: str) -> PillIconButton:
        is_light = str(theme_name).lower() != "dark"
        if key == "theme_icon":
            image = self.icons.get("moon") if is_light else self.icons.get("sun")
        else:
            image = self.icons.get(key)

        theme = get_theme_tokens(theme_name)
        return PillIconButton(
            self,
            image=image,
            width=SIDEBAR_WIDTH,
            height=BTN_H_ICON,
            outside_bg="transparent",
            fg_color="transparent",
            hover_color=theme["sidebar_hover"],
            border_color=theme["sidebar_border"],
            border_width=0,
        )

    def apply_theme(self, theme_name: str):
        is_light = str(theme_name).lower() != "dark"
        theme = get_theme_tokens(theme_name)
        self.configure(bg_color=theme["bg_base"])

        for key, button in self.buttons.items():
            payload = {
                "fg_color": "transparent",
                "hover_color": theme["sidebar_hover"],
                "outside_bg": "transparent",
                "border_color": theme["sidebar_border"],
                "border_width": 0,
            }
            if key == "theme_icon":
                payload["image"] = self.icons.get("moon") if is_light else self.icons.get("sun")
            button.configure(**payload)
