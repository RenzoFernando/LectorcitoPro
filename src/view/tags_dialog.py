import customtkinter as ctk
import copy
from view.dialogs import BaseDialog

# Paleta de colores para mantener consistencia.
COLORS = {
    "light": {"bg": "#EBEBEB", "text": "#000000", "left_bar": "#1A1E22", "progress_bar": "#D9D9D9"},
    "dark": {"bg": "#1A1E22", "text": "#FFFFFF", "left_bar": "#EBEBEB", "progress_bar": "#333333"},
    "button": {"blue": "#3B8ED0", "green": "#3BD056", "red": "#D03B3D"},
    "button_hover": {"blue_h": "#3073A8", "green_h": "#2FA047", "red_h": "#A03031"},
    "sidebar_hover": {"light": "#3C3C3C", "dark": "#DCDCDC"},
    "progress_colors": {"start": "#3B8ED0", "mid": "#F9A825", "done": "#4CAF50"}
}


# Diálogo para gestionar listas de etiquetas (carpetas, extensiones, etc.).
class TagsConfigDialog(BaseDialog):

    # Inicializa el diálogo con las listas de etiquetas existentes.
    def __init__(self, parent, title: str,
                 folders_prompt: str, initial_folders: list,
                 files_prompt: str, initial_files: list):
        super().__init__(parent, title)

        self.folders_list = copy.deepcopy(initial_folders)
        self.files_list = copy.deepcopy(initial_files)

        # Colores para los estados de las etiquetas (activas/inactivas).
        self.tag_colors = {
            "activo": {"fg": COLORS['button']['blue'], "hover": COLORS['button_hover']['blue_h'], "text": "#FFFFFF"},
            "inactivo": {"fg": "#6c757d", "hover": "#5a6268", "text": "#FFFFFF"}
        }

        self.tag_font = ctk.CTkFont(family="Segoe UI", size=11)
        self.geometry("475x500")
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(expand=True, fill="both", padx=15, pady=15)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Creación de las secciones de carpetas y archivos.
        self._create_tag_section(0, folders_prompt, "folders")
        self._create_tag_section(1, files_prompt, "files")

        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)

        # Botones de acción (Guardar, Cancelar).
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.grid(row=6, column=0, pady=(20, 0), sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ok_button = ctk.CTkButton(button_frame, text="Guardar Cambios", command=self._on_ok,
                                  fg_color=COLORS['button']['green'], hover_color=COLORS['button_hover']['green_h'])
        ok_button.grid(row=0, column=0, padx=5, sticky="e")

        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self._on_cancel,
                                      fg_color=COLORS['button']['red'], hover_color=COLORS['button_hover']['red_h'])
        cancel_button.grid(row=0, column=1, padx=5, sticky="w")

        self.update_idletasks()
        self.after(500, self.redraw_all_tags)

    # Crea una sección completa para gestionar un tipo de etiqueta (título, lista y entrada).
    def _create_tag_section(self, section_index, prompt, section_id):
        base_row = section_index * 3
        ctk.CTkLabel(self.main_frame, text=prompt, font=("Segoe UI", 12, "bold")).grid(row=base_row, column=0,
                                                                                       sticky="w", pady=(15, 2))
        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="")
        scroll_frame.grid(row=base_row + 1, column=0, sticky="nsew")

        entry = ctk.CTkEntry(self.main_frame, placeholder_text="Escribir y presionar Enter para añadir...")
        entry.grid(row=base_row + 2, column=0, sticky="ew", pady=(5, 0))

        if section_id == "folders":
            self.folders_scroll_frame = scroll_frame
            entry.bind("<Return>", lambda event: self._add_tag(entry, self.folders_list))
        else:
            self.files_scroll_frame = scroll_frame
            entry.bind("<Return>", lambda event: self._add_tag(entry, self.files_list))

    # Redibuja todas las etiquetas en ambas secciones.
    def redraw_all_tags(self):
        if not self.winfo_exists(): return
        self._redraw_tags_in_frame(self.folders_scroll_frame, self.folders_list)
        self._redraw_tags_in_frame(self.files_scroll_frame, self.files_list)

    # Lógica para redibujar las etiquetas de forma fluida dentro de un frame.
    def _redraw_tags_in_frame(self, frame, tag_list):
        for widget in frame.winfo_children(): widget.destroy()
        if not frame.winfo_exists(): return
        frame.update_idletasks()
        container_width = frame.winfo_width() - 40

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

            # Si no hay espacio en la fila actual, crea una nueva.
            if current_row_width > 0 and (current_row_width + pill_width) > container_width:
                current_row = ctk.CTkFrame(row_container, fg_color="transparent")
                current_row.pack(fill="x", anchor="w", pady=(0, 5))
                current_row_width = 0

            pill_frame = self._create_pill_frame(current_row, tag_data, index, tag_list)
            pill_frame.pack(side="left", padx=(0, SPACE_BETWEEN_PILLS))
            current_row_width += pill_width + SPACE_BETWEEN_PILLS

    # Crea un widget individual para una etiqueta (píldora).
    def _create_pill_frame(self, parent, tag_data, index, tag_list):
        tag_name, tag_state = tag_data["nombre"], tag_data["estado"]
        colors = self.tag_colors[tag_state]
        pill_frame = ctk.CTkFrame(parent, fg_color=colors["fg"], border_width=0, corner_radius=12)
        label = ctk.CTkLabel(pill_frame, text=tag_name, text_color=colors["text"], font=self.tag_font)
        label.pack(side="left", padx=(10, 4), pady=4)
        close_button = ctk.CTkButton(pill_frame, text="✕", width=20, height=20, corner_radius=10,
                                     text_color=colors["text"], fg_color="transparent", hover_color=colors["hover"],
                                     command=lambda i=index, l=tag_list: self._delete_tag(i, l))
        close_button.pack(side="right", padx=(0, 6), pady=4)
        pill_frame.bind("<Button-1>", lambda e, i=index, l=tag_list: self._toggle_tag_state(e, i, l))
        label.bind("<Button-1>", lambda e, i=index, l=tag_list: self._toggle_tag_state(e, i, l))
        return pill_frame

    # Añade una nueva etiqueta a la lista correspondiente.
    def _add_tag(self, entry, tag_list):
        tag_name = entry.get().strip()
        if tag_name and not any(t["nombre"] == tag_name for t in tag_list):
            tag_list.append({"nombre": tag_name, "estado": "activo"})
            entry.delete(0, "end")
            self.redraw_all_tags()

    # Elimina una etiqueta de la lista.
    def _delete_tag(self, index, tag_list):
        if index < len(tag_list):
            tag_list.pop(index)
            self.redraw_all_tags()

    # Cambia el estado de una etiqueta (activo/inactivo).
    def _toggle_tag_state(self, event, index, tag_list):
        if index < len(tag_list):
            current_state = tag_list[index]["estado"]
            tag_list[index]["estado"] = "inactivo" if current_state == "activo" else "activo"
            self.redraw_all_tags()

    # Guarda los cambios y cierra el diálogo.
    def _on_ok(self, event=None):
        self.result = (self.folders_list, self.files_list)
        super()._on_ok(event)

    # Método de clase para mostrar el diálogo y devolver las listas de etiquetas.
    @classmethod
    def get_input(cls, parent, title, folders_prompt, initial_folders, files_prompt, initial_files):
        dialog = cls(parent, title, folders_prompt, initial_folders, files_prompt, initial_files)
        parent.wait_window(dialog);
        return dialog.result