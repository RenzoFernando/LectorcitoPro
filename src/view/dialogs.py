import customtkinter as ctk
import os
from tkinter import filedialog
from PIL import Image
from view.tooltip import CustomTooltip
from view.ui_constants import COLORS
from view.ui_assets import get_app_icon_path

MESSAGE_AUTO_CLOSE_SECONDS = 10


def _get_color_tuple(key: str) -> tuple[str, str]:
    key_map = {
        "bg": "bg",
        "card": "surface",
        "card_border": "border",
        "inner_area": "surface_alt",
        "text": "text"
    }
    actual_key = key_map.get(key, key)
    return (COLORS["light"][actual_key], COLORS["dark"][actual_key])


def _style_button(btn: ctk.CTkButton, color_type="blue"):
    base = COLORS["button"].get(color_type, COLORS["button"]["blue"])["bg"]
    hover = COLORS["button"].get(color_type, COLORS["button"]["blue"])["hover"]

    btn.configure(
        corner_radius=16,
        height=32,
        font=("Segoe UI", 12),
        text_color="#FFFFFF",
        fg_color=base,
        hover_color=hover
    )


class BaseDialog(ctk.CTkToplevel):

    def __init__(self, parent, title: str):
        CustomTooltip.hide_global()

        super().__init__(parent)
        self.parent = parent

        self.withdraw()
        self.attributes("-alpha", 0.0)

        if hasattr(parent, "dim_ui_for_modal"):
            parent.dim_ui_for_modal()

        self.title(title)
        self.resizable(False, False)

        self.configure(fg_color=_get_color_tuple("bg"))

        self._closing_grab_released = False
        self._escape_bindtag = f"__esc_close_{id(self)}"

        try:
            self.bind_class(self._escape_bindtag, "<Escape>", self._on_escape_key, add="+")
        except Exception:
            self.bind("<Escape>", self._on_escape_key, add="+")

        self.bind("<Map>", self._install_escape_bindtags, add="+")

        self.after(185, self._set_icon_safe)
        self.after(300, self._prepare_geometry)

        self.result = None
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)

    def _set_icon_safe(self):
        try:
            if not self.winfo_exists(): return

            icon_path = get_app_icon_path()

            if icon_path and os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                self.after(100, lambda: self.iconbitmap(icon_path))
        except Exception:
            pass

    def _create_card_frame(self) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            self,
            fg_color=_get_color_tuple("card"),
            border_color=_get_color_tuple("card_border"),
            border_width=1,
            corner_radius=15
        )
        card.pack(expand=True, fill="both", padx=15, pady=15)
        return card

    def _on_escape_key(self, event=None):
        self._close_with_fade_out()
        return "break"

    def _install_escape_bindtags(self, event=None):
        try:
            if not self.winfo_exists(): return
        except Exception:
            return

        def apply_tag(widget):
            try:
                tags = list(widget.bindtags())
            except Exception:
                return
            if self._escape_bindtag not in tags:
                tags.insert(0, self._escape_bindtag)
                try:
                    widget.bindtags(tuple(tags))
                except Exception:
                    pass
            try:
                for child in widget.winfo_children(): apply_tag(child)
            except Exception:
                pass

        apply_tag(self)

    def _prepare_geometry(self):
        if not self.winfo_exists(): return

        self.deiconify()
        self.attributes("-alpha", 0.0)
        self.update_idletasks()
        self.after(200, self._try_center_window)

    def _try_center_window(self):
        if not self.winfo_exists(): return

        try:
            # CAMBIO: Forzamos la actualización de la UI para calcular el tamaño real del contenido
            self.update_idletasks()

            w = self.winfo_width()
            h = self.winfo_height()

            if w < 50 or h < 50:
                self.after(100, self._try_center_window)
                return

            if self.master and self.master.winfo_exists():
                parent_x = self.master.winfo_x()
                parent_y = self.master.winfo_y()
                parent_w = self.master.winfo_width()
                parent_h = self.master.winfo_height()

                x = parent_x + (parent_w - w) // 2
                y = parent_y + (parent_h - h) // 2

                self.geometry(f"+{x}+{y}")

            self.lift()
            self.focus_force()
            self.grab_set()
            self._fade_in()

        except Exception:
            self.attributes("-alpha", 1.0)

    def _fade_in(self):
        if not self.winfo_exists(): return

        try:
            alpha = self.attributes("-alpha")
        except Exception:
            alpha = 0.0

        if alpha < 1.0:
            new_alpha = min(alpha + 0.50, 1.0)
            self.attributes("-alpha", new_alpha)
            self.after(15, self._fade_in)
        else:
            self.focus_set()

    def _close_with_fade_out(self, event=None):
        if not self._closing_grab_released:
            try:
                self.grab_release()
            except Exception:
                pass
            self._closing_grab_released = True

        try:
            alpha = self.attributes("-alpha")
        except:
            alpha = 1.0

        if alpha > 0:
            alpha = max(alpha - 0.20, 0.0)
            self.attributes("-alpha", alpha)
            self.after(5, self._close_with_fade_out)
        else:
            self.destroy()
            if hasattr(self.parent, "restore_ui_from_modal"):
                self.parent.restore_ui_from_modal()

    def _on_ok(self, event=None):
        self._close_with_fade_out()

    def _on_cancel(self, event=None):
        self.result = None
        self._close_with_fade_out()


class MessageDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)

        self._auto_close_after_id = None
        self._schedule_auto_close()

        card = self._create_card_frame()

        ctk.CTkLabel(
            card,
            text=message,
            wraplength=350,
            justify="center",
            font=("Segoe UI", 13),
            text_color=_get_color_tuple("text")
        ).pack(fill="x", padx=20, pady=(20, 20))

        btn_text = parent._tr("btn_ok") if hasattr(parent, "_tr") else "OK"

        ok_button = ctk.CTkButton(
            card,
            text=btn_text,
            width=110,
            command=self._on_ok
        )
        _style_button(ok_button, "blue")
        ok_button.pack(pady=(0, 20))
        ok_button.focus_set()

        self.bind("<Return>", self._on_ok)

    def _schedule_auto_close(self):
        self._cancel_auto_close()
        try:
            seconds = float(MESSAGE_AUTO_CLOSE_SECONDS)
        except Exception:
            seconds = 0.0
        if seconds <= 0: return
        ms = max(1, int(seconds * 1000))

        self._auto_close_after_id = self.after(ms, self._auto_close)

    def _cancel_auto_close(self):
        if self._auto_close_after_id:
            try:
                self.after_cancel(self._auto_close_after_id)
            except Exception:
                pass
            self._auto_close_after_id = None

    def _auto_close(self):
        self._auto_close_after_id = None
        try:
            if not self.winfo_exists(): return
        except Exception:
            return
        self.result = None
        self._close_with_fade_out()

    def _close_with_fade_out(self, event=None):
        self._cancel_auto_close()
        return super()._close_with_fade_out(event)

    def _on_ok(self, event=None):
        self._cancel_auto_close()
        self.result = True
        super()._on_ok(event)


class ConfirmDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        self.result = False

        card = self._create_card_frame()

        ctk.CTkLabel(
            card,
            text=message,
            wraplength=350,
            justify="center",
            font=("Segoe UI", 13),
            text_color=_get_color_tuple("text")
        ).pack(fill="x", padx=20, pady=(25, 25))

        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(pady=(0, 20))

        txt_yes = parent._tr("btn_yes") if hasattr(parent, "_tr") else "Sí"
        txt_no = parent._tr("btn_no") if hasattr(parent, "_tr") else "No"

        btn_yes = ctk.CTkButton(button_frame, text=txt_yes, width=100, command=self._on_yes)
        _style_button(btn_yes, "green")
        btn_yes.pack(side="left", padx=10)

        btn_no = ctk.CTkButton(button_frame, text=txt_no, width=100, command=self._on_no)
        _style_button(btn_no, "red")
        btn_no.pack(side="left", padx=10)

    def _on_yes(self, event=None): self.result = True; self._close_with_fade_out()

    def _on_no(self, event=None): self.result = False; self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, title, message):
        dialog = cls(parent, title, message)
        parent.wait_window(dialog)
        return dialog.result


class ChoiceDialog(BaseDialog):
    def __init__(self, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        super().__init__(parent, title)
        self.option1_value, self.option2_value = option1_value, option2_value

        self.geometry("400x200")

        card = self._create_card_frame()

        ctk.CTkLabel(
            card,
            text=message,
            wraplength=340,
            font=("Segoe UI", 13),
            text_color=_get_color_tuple("text")
        ).pack(fill="x", padx=20, pady=(25, 15))

        btn1 = ctk.CTkButton(card, text=option1_text, width=220, command=self._on_option1)
        _style_button(btn1, "blue")
        btn1.pack(pady=(5, 8))

        btn2 = ctk.CTkButton(card, text=option2_text, width=220, command=self._on_option2)
        _style_button(btn2, "blue")
        btn2.pack(pady=(0, 20))

    def _on_option1(self): self.result = self.option1_value; super()._on_ok()

    def _on_option2(self): self.result = self.option2_value; super()._on_ok()

    @classmethod
    def ask(cls, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        dialog = cls(parent, title, message, option1_text, option2_text, option1_value, option2_value)
        parent.wait_window(dialog)
        return dialog.result


class InfographicDialog(BaseDialog):
    def __init__(self, parent, title: str, image_path: str):
        super().__init__(parent, title)

        try:
            self.geometry("620x500")

            card = self._create_card_frame()

            scroll_frame = ctk.CTkScrollableFrame(card, label_text="", fg_color="transparent")
            scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)

            pil_image_original = Image.open(image_path)
            original_width, original_height = pil_image_original.size
            target_width = 525
            ratio = target_width / original_width
            target_height = int(original_height * ratio)

            pil_image_resized = pil_image_original.resize((target_width, target_height), Image.Resampling.LANCZOS)

            self.infographic_image = ctk.CTkImage(
                light_image=pil_image_resized,
                dark_image=pil_image_resized,
                size=(target_width, target_height)
            )

            image_label = ctk.CTkLabel(scroll_frame, image=self.infographic_image, text="")
            image_label.pack(expand=True)

        except Exception as e:
            parent.show_message("error_title", f"{parent._tr('msg_error_generic')}\n\n{e}")
            self.after(50, self.destroy)