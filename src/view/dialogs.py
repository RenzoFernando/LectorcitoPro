import customtkinter as ctk
import os
from tkinter import filedialog
from PIL import Image
from utils import resource_path

# --- Paleta de Colores Estándar (para consistencia) ---
COLORS = {
    "light": {"bg": "#EBEBEB", "text": "#000000", "left_bar": "#1A1E22", "progress_bar": "#D9D9D9"},
    "dark": {"bg": "#1A1E22", "text": "#FFFFFF", "left_bar": "#EBEBEB", "progress_bar": "#333333"},
    "button": {"blue": "#3B8ED0", "green": "#3BD056", "red": "#D03B3D"},
    "button_hover": {"blue_h": "#3073A8", "green_h": "#2FA047", "red_h": "#A03031"},
    "sidebar_hover": {"light": "#3C3C3C", "dark": "#DCDCDC"},
    "progress_colors": {"start": "#3B8ED0", "mid": "#F9A825", "done": "#4CAF50"},
    "list_item": {"selected_bg": "#3B8ED0", "normal_bg": "transparent"}
}

# --- DIÁLOGOS PERSONALIZADOS (CON ANIMACIONES) ---
class BaseDialog(ctk.CTkToplevel):
    """Clase base para todos los diálogos personalizados con efectos de aparición/desaparición."""

    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.resizable(False, False)
        self.attributes("-alpha", 0.0)
        self.after(10, self._center_window)

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
        self._close_with_fade_out()

    def _on_cancel(self, event=None):
        self.result = None; self._close_with_fade_out()


class MessageDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, justify="center", font=("Segoe UI", 13)).pack(fill="x",
                                                                                                             pady=(0,
                                                                                                                   20))
        ok_button = ctk.CTkButton(main_frame, text="OK", width=100, command=self._on_ok,
                                  fg_color=COLORS['button']['blue'], hover_color=COLORS['button_hover']['blue_h'])
        ok_button.pack(pady=(0, 10));
        ok_button.focus_set();
        self.bind("<Return>", self._on_ok)

    def _on_ok(self, event=None): self.result = True; super()._on_ok(event)


class ConfirmDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        self.result = False
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, justify="center", font=("Segoe UI", 13)).pack(fill="x",
                                                                                                             pady=(0,
                                                                                                                   20))
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent");
        button_frame.pack()

        # --- ESTILO CORREGIDO ---
        ctk.CTkButton(button_frame, text="Sí", width=100, command=self._on_yes, fg_color=COLORS['button']['green'],
                      hover_color=COLORS['button_hover']['green_h']).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="No", width=100, command=self._on_no, fg_color=COLORS['button']['red'],
                      hover_color=COLORS['button_hover']['red_h']).pack(side="left", padx=10)

    def _on_yes(self, event=None): self.result = True; self._close_with_fade_out()

    def _on_no(self, event=None): self.result = False; self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, title, message):
        dialog = cls(parent, title, message);
        parent.wait_window(dialog);
        return dialog.result


class ChoiceDialog(BaseDialog):
    def __init__(self, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        super().__init__(parent, title)
        self.option1_value, self.option2_value = option1_value, option2_value
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, font=("Segoe UI", 13)).pack(fill="x", pady=(0, 20))
        ctk.CTkButton(main_frame, text=option1_text, width=220, command=self._on_option1,
                      fg_color=COLORS['button']['blue'], hover_color=COLORS['button_hover']['blue_h']).pack(pady=5)
        ctk.CTkButton(main_frame, text=option2_text, width=220, command=self._on_option2,
                      fg_color=COLORS['button']['blue'], hover_color=COLORS['button_hover']['blue_h']).pack(pady=5)

    def _on_option1(self): self.result = self.option1_value; super()._on_ok()

    def _on_option2(self): self.result = self.option2_value; super()._on_ok()

    @classmethod
    def ask(cls, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        dialog = cls(parent, title, message, option1_text, option2_text, option1_value, option2_value)
        parent.wait_window(dialog);
        return dialog.result


class SelectFoldersDialog(BaseDialog):
    def __init__(self, parent, title):
        super().__init__(parent, title)
        self.geometry("500x400")
        self.selected_paths = []
        self._parent = parent
        self.list_item_widgets = []
        self.currently_selected_index = -1

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkButton(top_frame, text=self._parent._tr("dlg_multi_add"), command=self._add_folder).pack(side="left")

        list_area_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        list_area_frame.grid(row=1, column=0, sticky="nsew")
        list_area_frame.grid_columnconfigure(0, weight=1)
        list_area_frame.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(list_area_frame,
                                                       label_text=self._parent._tr("dlg_multi_list_title"))
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")

        reorder_button_frame = ctk.CTkFrame(list_area_frame, fg_color="transparent")
        reorder_button_frame.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        ctk.CTkButton(reorder_button_frame, text="▲", width=30, command=self._move_up).pack(pady=2)
        ctk.CTkButton(reorder_button_frame, text="▼", width=30, command=self._move_down).pack(pady=2)
        ctk.CTkButton(reorder_button_frame, text="✕", width=30, command=self._remove_selected_folder,
                      fg_color=COLORS['button']['red'], hover_color=COLORS['button_hover']['red_h']).pack(pady=(10, 2))

        bottom_button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_button_frame.grid(row=2, column=0, sticky="e", pady=(15, 0))
        ctk.CTkButton(bottom_button_frame, text=self._parent._tr("btn_cancel"), command=self._on_cancel,
                      fg_color=COLORS['button']['red'], hover_color=COLORS['button_hover']['red_h']).pack(side="left",
                                                                                                          padx=10)
        ctk.CTkButton(bottom_button_frame, text=self._parent._tr("dlg_multi_process"), command=self._on_process,
                      fg_color=COLORS['button']['green'], hover_color=COLORS['button_hover']['green_h']).pack(
            side="left")

        self._update_folder_list()

    def _update_folder_list(self):
        for widget in self.list_item_widgets: widget.destroy()
        self.list_item_widgets.clear()

        if not self.selected_paths:
            label = ctk.CTkLabel(self.scrollable_frame, text=self._parent._tr("dlg_multi_empty"), text_color="gray")
            label.pack(pady=10);
            self.list_item_widgets.append(label)
        else:
            for i, path in enumerate(self.selected_paths):
                is_selected = (i == self.currently_selected_index)
                fg_color = COLORS['list_item']['selected_bg'] if is_selected else COLORS['list_item']['normal_bg']

                item_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=fg_color, corner_radius=6)
                item_frame.pack(fill="x", padx=5, pady=3)
                label = ctk.CTkLabel(item_frame, text=f"{i + 1}. {path}", anchor="w", compound="left", padx=10, font=("Segoe UI", 10))
                label.pack(fill="x")

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
        dialog = cls(parent, title);
        parent.wait_window(dialog);
        return dialog.result


class InfographicDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, image_path: str):
        super().__init__(parent)
        self.title(title);
        self.geometry("500x400");
        self.resizable(False, False)
        self.transient(parent);
        self.attributes("-alpha", 0.0)

        def _set_icon():
            try:
                if hasattr(parent, '_icon_path') and parent._icon_path and os.path.exists(
                    parent._icon_path): self.iconbitmap(parent._icon_path)
            except Exception as e:
                print(f"Error al establecer el icono de la ventana de infografía: {e}")

        self.after(200, _set_icon)
        try:
            scroll_frame = ctk.CTkScrollableFrame(self, label_text="");
            scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)
            pil_image_original = Image.open(image_path);
            original_width, original_height = pil_image_original.size
            target_width = 450;
            ratio = target_width / original_width;
            target_height = int(original_height * ratio)
            pil_image_resized = pil_image_original.resize((target_width, target_height), Image.Resampling.LANCZOS)
            self.infographic_image = ctk.CTkImage(light_image=pil_image_resized, dark_image=pil_image_resized,
                                                  size=(target_width, target_height))
            image_label = ctk.CTkLabel(scroll_frame, image=self.infographic_image, text="");
            image_label.pack(expand=True)
        except Exception as e:
            self.destroy();
            parent.show_message("error_title", f"{parent._tr('msg_error_generic')}\n\n{e}")
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out);
        self.bind("<Escape>", self._close_with_fade_out)
        self.after(20, self._fade_in);
        self.grab_set()

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1: alpha = min(alpha + 0.1, 1.0); self.attributes("-alpha", alpha); self.after(15, self._fade_in)

    def _close_with_fade_out(self, event=None):
        self.grab_release()
        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha = max(alpha - 0.1, 0.0); self.attributes("-alpha", alpha); self.after(15, self._close_with_fade_out)
        else:
            self.destroy()
