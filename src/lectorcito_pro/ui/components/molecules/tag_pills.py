"""UI Molecule: Tag Pills.

Widget reutilizable para editar listas de tags (carpetas/archivos):
- Agregar tags con Enter
- Eliminar tags con '✕'
- Activar/desactivar clickeando la píldora

Se usa en `ui/dialogs/tags_config.py`.
"""

from __future__ import annotations

import customtkinter as ctk

from ...theme.palette import COLORS


class TagPillsEditor(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        prompt: str,
        tag_list: list[dict],
        placeholder: str,
        *,
        on_change=None,
    ):
        super().__init__(parent, fg_color="transparent")

        self.tag_list = tag_list
        self.on_change = on_change

        self.tag_colors = {
            "activo": {"fg": COLORS["button"]["blue"], "hover": COLORS["button_hover"]["blue_h"], "text": "#FFFFFF"},
            "inactivo": {"fg": "#6c757d", "hover": "#5a6268", "text": "#FFFFFF"},
        }
        self.tag_font = ctk.CTkFont(family="Segoe UI", size=11)

        self.grid_columnconfigure(0, weight=1)

        self.lbl_prompt = ctk.CTkLabel(self, text=prompt, font=("Segoe UI", 11, "bold"))
        self.lbl_prompt.grid(row=0, column=0, sticky="w", padx=20, pady=(10, 5))

        self.scroll_frame = ctk.CTkScrollableFrame(self, height=120, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20)

        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder)
        self.entry.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 0))
        self.entry.bind("<Return>", self._on_enter_add)

        # Primera pintura (después de que Tk calcule el ancho)
        self.after(50, self.redraw)

    def _on_enter_add(self, event=None):
        tag_name = self.entry.get().strip()
        if tag_name and not any(t.get("nombre") == tag_name for t in self.tag_list):
            self.tag_list.append({"nombre": tag_name, "estado": "activo"})
            self.entry.delete(0, "end")
            self.redraw()
            if self.on_change:
                self.on_change()

    def _delete_tag(self, index: int):
        if index < len(self.tag_list):
            self.tag_list.pop(index)
            self.redraw()
            if self.on_change:
                self.on_change()

    def _toggle_tag_state(self, index: int):
        if index < len(self.tag_list):
            current_state = self.tag_list[index].get("estado", "activo")
            self.tag_list[index]["estado"] = "inactivo" if current_state == "activo" else "activo"
            self.redraw()
            if self.on_change:
                self.on_change()

    def redraw(self):
        if not self.winfo_exists():
            return

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.scroll_frame.winfo_exists():
            return

        self.scroll_frame.update_idletasks()
        container_width = max(1, self.scroll_frame.winfo_width() - 40)

        row_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row_container.pack(fill="x", anchor="nw")

        current_row = ctk.CTkFrame(row_container, fg_color="transparent")
        current_row.pack(fill="x", anchor="w", pady=(0, 5))
        current_row_width = 0

        PILL_FIXED_WIDTH = 75
        SPACE_BETWEEN_PILLS = 5

        for index, tag_data in enumerate(self.tag_list):
            tag_name = str(tag_data.get("nombre", ""))
            text_width = self.tag_font.measure(tag_name)
            pill_width = text_width + PILL_FIXED_WIDTH

            if current_row_width > 0 and (current_row_width + pill_width) > container_width:
                current_row = ctk.CTkFrame(row_container, fg_color="transparent")
                current_row.pack(fill="x", anchor="w", pady=(0, 5))
                current_row_width = 0

            pill = self._create_pill_frame(current_row, tag_data, index)
            pill.pack(side="left", padx=(0, SPACE_BETWEEN_PILLS))
            current_row_width += pill_width + SPACE_BETWEEN_PILLS

    def _create_pill_frame(self, parent, tag_data: dict, index: int):
        tag_name = str(tag_data.get("nombre", ""))
        tag_state = tag_data.get("estado", "activo")
        colors = self.tag_colors.get(tag_state, self.tag_colors["activo"])

        pill_frame = ctk.CTkFrame(parent, fg_color=colors["fg"], border_width=0, corner_radius=12)

        label = ctk.CTkLabel(pill_frame, text=tag_name, text_color=colors["text"], font=self.tag_font)
        label.pack(side="left", padx=(10, 4), pady=4)

        close_button = ctk.CTkButton(
            pill_frame,
            text="✕",
            width=20,
            height=20,
            corner_radius=10,
            text_color=colors["text"],
            fg_color="transparent",
            hover_color=colors["hover"],
            command=lambda i=index: self._delete_tag(i),
        )
        close_button.pack(side="right", padx=(0, 6), pady=4)

        pill_frame.bind("<Button-1>", lambda e, i=index: self._toggle_tag_state(i))
        label.bind("<Button-1>", lambda e, i=index: self._toggle_tag_state(i))
        return pill_frame
