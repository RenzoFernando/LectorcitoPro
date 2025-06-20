import customtkinter as ctk
import os
from PIL import Image
from utils import resource_path


# --- DIÁLOGOS PERSONALIZADOS (CON ANIMACIONES) ---
class BaseDialog(ctk.CTkToplevel):
    """Clase base para todos los diálogos personalizados con efectos de aparición/desaparición."""

    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.resizable(False, False)
        self.attributes("-alpha", 0.0)

        # Centrar la ventana de diálogo con respecto al padre
        self.after(10, self._center_window)  # Retraso para asegurar que las dimensiones del padre estén listas

        # Intentar establecer el mismo icono que la ventana principal
        def _set_icon():
            try:
                if hasattr(parent, '_icon_path') and parent._icon_path and os.path.exists(parent._icon_path):
                    self.iconbitmap(parent._icon_path)
            except Exception as e:
                print(f"Error al establecer el icono de la sub-ventana: {e}")

        self.after(200, _set_icon)
        self.result = None
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)
        self.bind("<Escape>", self._close_with_fade_out)
        self.after(20, self._fade_in)
        self.grab_set()

    def _center_window(self):
        try:
            self.update_idletasks()
            parent_x, parent_y = self.master.winfo_x(), self.master.winfo_y()
            parent_width, parent_height = self.master.winfo_width(), self.master.winfo_height()
            dialog_width, dialog_height = self.winfo_width(), self.winfo_height()

            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
            self.geometry(f"+{x}+{y}")
        except Exception as e:
            print(f"Error al centrar el diálogo: {e}")

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1:
            alpha = min(alpha + 0.1, 1.0)
            self.attributes("-alpha", alpha)
            self.after(15, self._fade_in)

    def _close_with_fade_out(self, event=None):
        self.grab_release()
        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha = max(alpha - 0.1, 0.0)
            self.attributes("-alpha", alpha)
            self.after(15, self._close_with_fade_out)
        else:
            self.destroy()

    def _on_ok(self, event=None):
        # El resultado se establece en las subclases antes de llamar a esto
        self._close_with_fade_out()

    def _on_cancel(self, event=None):
        self.result = None
        self._close_with_fade_out()


class MessageDialog(BaseDialog):
    """Diálogo para mostrar un mensaje simple con un botón de OK."""

    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, justify="center").pack(fill="x", pady=(0, 20))
        ok_button = ctk.CTkButton(main_frame, text="OK", width=100, command=self._on_ok)
        ok_button.pack(pady=(0, 10))
        ok_button.focus_set()
        self.bind("<Return>", self._on_ok)

    def _on_ok(self, event=None):
        self.result = True  # Se establece un resultado para consistencia
        super()._on_ok(event)


class ConfirmDialog(BaseDialog):
    """Diálogo para pedir confirmación al usuario (Sí/No)."""

    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        self.result = False
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, justify="center").pack(fill="x", pady=(0, 20))
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()
        ctk.CTkButton(button_frame, text="Sí", width=100, command=self._on_yes).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="No", width=100, command=self._on_no).pack(side="left", padx=10)

    def _on_yes(self, event=None): self.result = True; self._close_with_fade_out()

    def _on_no(self, event=None): self.result = False; self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, title, message):
        dialog = cls(parent, title, message)
        parent.wait_window(dialog)
        return dialog.result


class ChoiceDialog(BaseDialog):
    """Diálogo para ofrecer al usuario dos opciones."""

    def __init__(self, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        super().__init__(parent, title)
        self.option1_value, self.option2_value = option1_value, option2_value
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350).pack(fill="x", pady=(0, 20))
        ctk.CTkButton(main_frame, text=option1_text, width=200, command=self._on_option1).pack(pady=5)
        ctk.CTkButton(main_frame, text=option2_text, width=200, command=self._on_option2).pack(pady=5)

    def _on_option1(self): self.result = self.option1_value; super()._on_ok()

    def _on_option2(self): self.result = self.option2_value; super()._on_ok()

    @classmethod
    def ask(cls, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        dialog = cls(parent, title, message, option1_text, option2_text, option1_value, option2_value)
        parent.wait_window(dialog)
        return dialog.result


class InfographicDialog(ctk.CTkToplevel):
    """Diálogo para mostrar una imagen grande, como una infografía."""

    def __init__(self, parent, title: str, image_path: str):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x400")
        self.resizable(False, False)
        self.transient(parent)
        self.attributes("-alpha", 0.0)

        def _set_icon():
            try:
                if hasattr(parent, '_icon_path') and parent._icon_path and os.path.exists(parent._icon_path):
                    self.iconbitmap(parent._icon_path)
            except Exception as e:
                print(f"Error al establecer el icono de la ventana de infografía: {e}")

        self.after(200, _set_icon)

        try:
            scroll_frame = ctk.CTkScrollableFrame(self, label_text="")
            scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)
            pil_image_original = Image.open(image_path)
            original_width, original_height = pil_image_original.size
            target_width = 450
            ratio = target_width / original_width
            target_height = int(original_height * ratio)
            pil_image_resized = pil_image_original.resize((target_width, target_height), Image.Resampling.LANCZOS)
            self.infographic_image = ctk.CTkImage(light_image=pil_image_resized, dark_image=pil_image_resized,
                                                  size=(target_width, target_height))
            image_label = ctk.CTkLabel(scroll_frame, image=self.infographic_image, text="")
            image_label.pack(expand=True)
        except Exception as e:
            self.destroy()
            parent.show_message("error_title", f"{parent._tr('msg_error_generic')}\n\n{e}")

        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)
        self.bind("<Escape>", self._close_with_fade_out)
        self.after(20, self._fade_in)
        self.grab_set()

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1:
            alpha = min(alpha + 0.1, 1.0);
            self.attributes("-alpha", alpha);
            self.after(15, self._fade_in)

    def _close_with_fade_out(self, event=None):
        self.grab_release()
        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha = max(alpha - 0.1, 0.0);
            self.attributes("-alpha", alpha);
            self.after(15, self._close_with_fade_out)
        else:
            self.destroy()
