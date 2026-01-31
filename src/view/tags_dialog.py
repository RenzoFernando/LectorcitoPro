import customtkinter as ctk
import copy
from view.dialogs import BaseDialog, _get_color_tuple, _style_button
from view.ui_constants import COLORS


# Diálogo para gestionar listas de etiquetas (carpetas, extensiones, etc.).
class TagsConfigDialog(BaseDialog):

    def __init__(self, parent, title: str,
                 folders_prompt: str, initial_folders: list,
                 files_prompt: str, initial_files: list):
        super().__init__(parent, title)

        self.folders_list = copy.deepcopy(initial_folders)
        self.files_list = copy.deepcopy(initial_files)

        self.tag_colors = {
            "activo": {"fg": COLORS['button']['blue'], "hover": COLORS['button_hover']['blue_h'], "text": "#FFFFFF"},
            "inactivo": {"fg": "#6c757d", "hover": "#5a6268", "text": "#FFFFFF"}
        }

        self.tag_font = ctk.CTkFont(family="Segoe UI", size=11)

        # AJUSTE DE GEOMETRÍA: Más ancho, menos alto para evitar espacio vacío.
        self.geometry("500x600")

        # Tarjeta principal
        self.main_frame = self._create_card_frame()
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Creación de las secciones
        text_color = _get_color_tuple("text")

        # Reducimos padding interno de las secciones
        self._create_tag_section(0, folders_prompt, "folders", text_color)
        self._create_tag_section(1, files_prompt, "files", text_color)

        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)

        # Botones de acción
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.grid(row=6, column=0, pady=(15, 10), sticky="ew")  # Menos padding abajo
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ok_button = ctk.CTkButton(button_frame, text="Guardar Cambios", command=self._on_ok)
        _style_button(ok_button, "green")
        ok_button.configure(width=140)
        ok_button.grid(row=0, column=0, padx=10, sticky="e")

        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self._on_cancel)
        _style_button(cancel_button, "red")
        cancel_button.configure(width=100)
        cancel_button.grid(row=0, column=1, padx=10, sticky="w")

        self.update_idletasks()
        self.after(500, self.redraw_all_tags)

    def _create_tag_section(self, section_index, prompt, section_id, text_color):
        base_row = section_index * 3
        # Título más pegado al contenido (pady reducido)
        ctk.CTkLabel(self.main_frame, text=prompt, font=("Segoe UI", 12, "bold"), text_color=text_color).grid(
            row=base_row, column=0,
            sticky="w", pady=(10, 2), padx=20)

        scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            label_text="",
            fg_color=_get_color_tuple("inner_area"),  # Contraste
            border_width=1,
            border_color=_get_color_tuple("card_border")
        )
        scroll_frame.grid(row=base_row + 1, column=0, sticky="nsew", padx=20)

        entry = ctk.CTkEntry(self.main_frame, placeholder_text="Escribir y presionar Enter para añadir...")
        entry.grid(row=base_row + 2, column=0, sticky="ew", pady=(5, 0), padx=20)

        if section_id == "folders":
            self.folders_scroll_frame = scroll_frame
            entry.bind("<Return>", lambda event: self._add_tag(entry, self.folders_list))
        else:
            self.files_scroll_frame = scroll_frame
            entry.bind("<Return>", lambda event: self._add_tag(entry, self.files_list))

    def redraw_all_tags(self):
        if not self.winfo_exists(): return
        self._redraw_tags_in_frame(self.folders_scroll_frame, self.folders_list)
        self._redraw_tags_in_frame(self.files_scroll_frame, self.files_list)

    def _redraw_tags_in_frame(self, frame, tag_list):
        for widget in frame.winfo_children(): widget.destroy()
        if not frame.winfo_exists(): return
        frame.update_idletasks()

        container_width = frame.winfo_width() - 30

        row_container = ctk.CTkFrame(frame, fg_color="transparent")
        row_container.pack(fill="x", anchor="nw")
        current_row = ctk.CTkFrame(row_container, fg_color="transparent")
        current_row.pack(fill="x", anchor="w", pady=(0, 5))
        current_row_width = 0

        PILL_FIXED_WIDTH = 75
        SPACE_BETWEEN_PILLS = 5

        for index, tag_data in enumerate(tag_list):
            text_width = self.tag_font.measure(tag_data["nombre"])
            pill_width = text_width + PILL_FIXED_WIDTH

            if current_row_width > 0 and (current_row_width + pill_width) > container_width:
                current_row = ctk.CTkFrame(row_container, fg_color="transparent")
                current_row.pack(fill="x", anchor="w", pady=(0, 5))
                current_row_width = 0

            pill_frame = self._create_pill_frame(current_row, tag_data, index, tag_list)
            pill_frame.pack(side="left", padx=(0, SPACE_BETWEEN_PILLS))
            current_row_width += pill_width + SPACE_BETWEEN_PILLS

    def _create_pill_frame(self, parent, tag_data, index, tag_list):
        tag_name, tag_state = tag_data["nombre"], tag_data["estado"]
        colors = self.tag_colors[tag_state]

        pill_frame = ctk.CTkFrame(parent, fg_color=colors["fg"], border_width=0, corner_radius=14)

        label = ctk.CTkLabel(pill_frame, text=tag_name, text_color=colors["text"], font=self.tag_font)
        label.pack(side="left", padx=(10, 4), pady=2)

        close_button = ctk.CTkButton(pill_frame, text="✕", width=20, height=20, corner_radius=10,
                                     text_color=colors["text"], fg_color="transparent", hover_color=colors["hover"],
                                     command=lambda i=index, l=tag_list: self._delete_tag(i, l))

        close_button.pack(side="right", padx=(0, 6), pady=2)
        pill_frame.bind("<Button-1>", lambda e, i=index, l=tag_list: self._toggle_tag_state(e, i, l))
        label.bind("<Button-1>", lambda e, i=index, l=tag_list: self._toggle_tag_state(e, i, l))
        return pill_frame

    def _add_tag(self, entry, tag_list):
        tag_name = entry.get().strip()
        if tag_name and not any(t["nombre"] == tag_name for t in tag_list):
            tag_list.append({"nombre": tag_name, "estado": "activo"})
            entry.delete(0, "end")
            self.redraw_all_tags()

    def _delete_tag(self, index, tag_list):
        if index < len(tag_list):
            tag_list.pop(index)
            self.redraw_all_tags()

    def _toggle_tag_state(self, event, index, tag_list):
        if index < len(tag_list):
            current_state = tag_list[index]["estado"]
            tag_list[index]["estado"] = "inactivo" if current_state == "activo" else "activo"
            self.redraw_all_tags()

    def _on_ok(self, event=None):
        self.result = (self.folders_list, self.files_list)
        super()._on_ok(event)

    @classmethod
    def get_input(cls, parent, title, folders_prompt, initial_folders, files_prompt, initial_files):
        dialog = cls(parent, title, folders_prompt, initial_folders, files_prompt, initial_files)
        parent.wait_window(dialog);
        return dialog.result