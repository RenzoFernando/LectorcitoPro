
import customtkinter as ctk
from PIL import Image

from .base import BaseDialog

class InfographicDialog(BaseDialog):
    def __init__(self, parent, title: str, image_path: str):
        super().__init__(parent, title)

        try:
            self.geometry("575x400")

            scroll_frame = ctk.CTkScrollableFrame(self, label_text="")
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
