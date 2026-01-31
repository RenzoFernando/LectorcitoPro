# src/view/dialogs.py
import customtkinter as ctk
import os
from tkinter import filedialog
from PIL import Image
from view.tooltip import CustomTooltip
from view.ui_constants import COLORS

MESSAGE_AUTO_CLOSE_SECONDS = 5


# --- Helpers de estilo ---
def _get_color_tuple(key: str) -> tuple[str, str]:
    """Obtiene una tupla (color_claro, color_oscuro) desde COLORS."""
    # Mapeo de compatibilidad por si usamos claves viejas
    key_map = {
        "bg": "bg",
        "card": "surface",
        "card_border": "border",
        "inner_area": "surface_alt",
        "text": "text"
    }

    # Si la key está en el mapa, usamos la nueva clave semántica
    actual_key = key_map.get(key, key)

    return (COLORS["light"][actual_key], COLORS["dark"][actual_key])


def _style_button(btn: ctk.CTkButton, color_type="blue"):
    # Usamos la estructura nueva de botones en COLORS["button"]
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


# Clase base para todos los diálogos con animaciones de entrada y salida.
class BaseDialog(ctk.CTkToplevel):

    def __init__(self, parent, title: str):
        CustomTooltip.hide_global()

        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.resizable(False, False)
        self.attributes("-alpha", 0.0)

        # Usamos la key 'bg' del tema
        self.configure(fg_color=_get_color_tuple("bg"))

        self._closing_grab_released = False

        self._escape_bindtag = f"__esc_close_{id(self)}"
        try:
            self.bind_class(self._escape_bindtag, "<Escape>", self._on_escape_key, add="+")
        except Exception:
            self.bind("<Escape>", self._on_escape_key, add="+")

        self.bind("<Map>", self._install_escape_bindtags, add="+")
        self.after(120, self._install_escape_bindtags)
        self.after(350, self._install_escape_bindtags)

        def _set_icon():
            try:
                if hasattr(parent, '_icon_path') and parent._icon_path and os.path.exists(parent._icon_path):
                    self.iconbitmap(parent._icon_path)
            except Exception as e:
                print(f"Error al establecer el icono de la sub-ventana: {e}")

        self.after(200, _set_icon)

        self.result = None
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)
        self.after(100, self._center_and_fade_in)

    def _create_card_frame(self) -> ctk.CTkFrame:
        # Usa 'card' que _get_color_tuple mapea a 'surface'
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

    def _center_and_fade_in(self):
        try:
            self.grab_set()
            self._center_window()

            def _activate():
                try:
                    if not self.winfo_exists(): return
                    try:
                        self.deiconify()
                    except Exception:
                        pass
                    try:
                        self.lift()
                    except Exception:
                        pass
                    try:
                        self.focus_force();
                        self.focus_set()
                    except Exception:
                        pass
                    try:
                        self.attributes("-topmost", True)
                        self.after(10, lambda: self.winfo_exists() and self.attributes("-topmost", False))
                    except Exception:
                        pass
                except Exception:
                    pass

            _activate()
            self.after(40, _activate)
            self.after(140, _activate)
            self._fade_in()
        except Exception:
            pass

    def _center_window(self):
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        dx, dy = self.winfo_width(), self.winfo_height()
        x = parent_x + (parent_width - dx) // 2
        y = parent_y + (parent_height - dy) // 2
        self.geometry(f"+{x}+{y}")

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1:
            alpha = min(alpha + 0.1, 1.0)
            self.attributes("-alpha", alpha)
            self.after(15, self._fade_in)

    def _close_with_fade_out(self, event=None):
        if not self._closing_grab_released:
            try:
                self.grab_release()
            except Exception:
                pass
            self._closing_grab_released = True

        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha = max(alpha - 0.1, 0.0)
            self.attributes("-alpha", alpha)
            self.after(15, self._close_with_fade_out)
        else:
            self.destroy()

    def _on_ok(self, event=None):
        self._close_with_fade_out()

    def _on_cancel(self, event=None):
        self.result = None;
        self._close_with_fade_out()


# Diálogo simple para mostrar un mensaje con un botón de "OK".
class MessageDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)

        self._auto_close_after_id = None
        self._schedule_auto_close()

        # Ajuste para que se vea compacto
        card = self._create_card_frame()

        ctk.CTkLabel(
            card,
            text=message,
            wraplength=350,
            justify="center",
            font=("Segoe UI", 13),
            text_color=_get_color_tuple("text")
        ).pack(fill="x", padx=20, pady=(20, 20))  # Menos padding

        ok_button = ctk.CTkButton(
            card,
            text="OK",
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


# Diálogo de confirmación con opciones "Sí" y "No".
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

        btn_yes = ctk.CTkButton(button_frame, text="Sí", width=100, command=self._on_yes)
        _style_button(btn_yes, "green")
        btn_yes.pack(side="left", padx=10)

        btn_no = ctk.CTkButton(button_frame, text="No", width=100, command=self._on_no)
        _style_button(btn_no, "red")
        btn_no.pack(side="left", padx=10)

    def _on_yes(self, event=None): self.result = True; self._close_with_fade_out()

    def _on_no(self, event=None): self.result = False; self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, title, message):
        dialog = cls(parent, title, message)
        parent.wait_window(dialog)
        return dialog.result


# Diálogo que presenta dos opciones personalizables.
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
        ).pack(fill="x", padx=20, pady=(25, 15))  # Menos padding inferior

        # Botones
        btn1 = ctk.CTkButton(card, text=option1_text, width=220, command=self._on_option1)
        _style_button(btn1, "blue")
        btn1.pack(pady=(5, 8))  # Menos separación

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


# Diálogo para seleccionar, ordenar y eliminar múltiples rutas de carpetas.
class SelectFoldersDialog(BaseDialog):
    def __init__(self, parent, title):
        super().__init__(parent, title)
        # Ajuste de altura para que se vea más lleno
        self.geometry("550x420")
        self.selected_paths = []
        self._parent = parent
        self.list_item_widgets = []
        self.currently_selected_index = -1

        card = self._create_card_frame()
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        # -- Top --
        top_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))

        btn_add = ctk.CTkButton(top_frame, text=self._parent._tr("dlg_multi_add"), command=self._add_folder)
        _style_button(btn_add, "blue")
        btn_add.configure(width=130)
        btn_add.pack(side="left")

        # -- Middle --
        list_area_frame = ctk.CTkFrame(card, fg_color="transparent")
        list_area_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        list_area_frame.grid_columnconfigure(0, weight=1)
        list_area_frame.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(
            list_area_frame,
            label_text=self._parent._tr("dlg_multi_list_title"),
            fg_color=_get_color_tuple("inner_area"),
            label_text_color=_get_color_tuple("text"),
            border_width=1,
            border_color=_get_color_tuple("card_border")
        )
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")

        # Botones laterales
        reorder_button_frame = ctk.CTkFrame(list_area_frame, fg_color="transparent")
        reorder_button_frame.grid(row=0, column=1, sticky="ns", padx=(10, 0))

        def _style_icon_btn(btn, color):
            btn.configure(width=32, height=32, corner_radius=16, font=("Segoe UI", 12), text_color="#FFFFFF")
            _style_button(btn, color)
            btn.configure(width=32, height=32)

        btn_up = ctk.CTkButton(reorder_button_frame, text="▲", command=self._move_up)
        _style_icon_btn(btn_up, "blue")
        btn_up.pack(pady=2)

        btn_down = ctk.CTkButton(reorder_button_frame, text="▼", command=self._move_down)
        _style_icon_btn(btn_down, "blue")
        btn_down.pack(pady=2)

        btn_del = ctk.CTkButton(reorder_button_frame, text="✕", command=self._remove_selected_folder)
        _style_icon_btn(btn_del, "red")
        btn_del.pack(pady=(15, 2))

        # -- Bottom --
        bottom_button_frame = ctk.CTkFrame(card, fg_color="transparent")
        bottom_button_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(15, 20))

        btn_process = ctk.CTkButton(bottom_button_frame, text=self._parent._tr("dlg_multi_process"),
                                    command=self._on_process)
        _style_button(btn_process, "green")
        btn_process.configure(width=130)
        btn_process.pack(side="right")

        btn_cancel = ctk.CTkButton(bottom_button_frame, text=self._parent._tr("btn_cancel"), command=self._on_cancel)
        _style_button(btn_cancel, "red")
        btn_cancel.configure(width=100)
        btn_cancel.pack(side="right", padx=10)

        self._update_folder_list()

    def _update_folder_list(self):
        for widget in self.list_item_widgets: widget.destroy()
        self.list_item_widgets.clear()

        if not self.selected_paths:
            label = ctk.CTkLabel(self.scrollable_frame, text=self._parent._tr("dlg_multi_empty"), text_color="gray")
            label.pack(pady=10)
            self.list_item_widgets.append(label)
        else:
            for i, path in enumerate(self.selected_paths):
                is_selected = (i == self.currently_selected_index)
                fg_color = COLORS['list_item']['selected_bg'] if is_selected else COLORS['list_item']['normal_bg']

                item_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=fg_color, corner_radius=6)
                item_frame.pack(fill="x", padx=5, pady=3)

                label = ctk.CTkLabel(item_frame, text=f"{i + 1}. {path}", anchor="w", compound="left", padx=10,
                                     font=("Segoe UI", 11),
                                     text_color="#FFFFFF" if is_selected else _get_color_tuple("text"))
                label.pack(fill="x", pady=2)

                item_frame.bind("<Button-1>", lambda e, index=i: self._on_item_select(index))
                label.bind("<Button-1>", lambda e, index=i: self._on_item_select(index))
                self.list_item_widgets.append(item_frame)

    def _on_item_select(self, index):
        self.currently_selected_index = index
        self._update_folder_list()

    def _add_folder(self):
        path = filedialog.askdirectory(title=self._parent._tr("dlg_multi_add_title"))
        if path and path not in self.selected_paths:
            self.selected_paths.append(path)
            self.currently_selected_index = len(self.selected_paths) - 1
            self._update_folder_list()

    def _remove_selected_folder(self):
        if 0 <= self.currently_selected_index < len(self.selected_paths):
            self.selected_paths.pop(self.currently_selected_index)
            self.currently_selected_index = -1
            self._update_folder_list()

    def _move_up(self):
        if 0 < self.currently_selected_index < len(self.selected_paths):
            idx = self.currently_selected_index
            self.selected_paths[idx], self.selected_paths[idx - 1] = self.selected_paths[idx - 1], self.selected_paths[
                idx]
            self.currently_selected_index -= 1
            self._update_folder_list()

    def _move_down(self):
        if -1 <= self.currently_selected_index < len(self.selected_paths) - 1:
            idx = self.currently_selected_index
            self.selected_paths[idx], self.selected_paths[idx + 1] = self.selected_paths[idx + 1], self.selected_paths[
                idx]
            self.currently_selected_index += 1
            self._update_folder_list()

    def _on_process(self):
        if self.selected_paths:
            self.result = self.selected_paths
        else:
            self.result = None
        self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, title):
        dialog = cls(parent, title)
        parent.wait_window(dialog)
        return dialog.result


# Diálogo para mostrar una imagen infográfica con scroll.
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